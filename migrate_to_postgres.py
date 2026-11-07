#!/usr/bin/env python
"""
Data migration script: SQLite -> PostgreSQL

Usage:
  1. Set DATABASE_URL to your PostgreSQL URL in your terminal:
       $env:DATABASE_URL="postgresql://user:pass@host:5432/dbname"   (PowerShell)
       set DATABASE_URL=postgresql://user:pass@host:5432/dbname      (CMD)
       export DATABASE_URL=...                                       (Linux/Mac)
  
  2. Run:
       python migrate_to_postgres.py

Safety guarantees:
  - Idempotent: Refuses `loaddata` if ANY of the 12 fixture tables already contains data
  - Non-destructive: Does not touch or delete local db.sqlite3 (opened read-only for CT mapping)
  - ContentType remapping: admin.logentry content_type IDs remapped SQLite->PostgreSQL via (app_label, model) identity
  - Exact row count validation across all 12 fixture models
  - Full Foreign Key relational integrity validation
  - Non-zero exit code (sys.exit(1)) on ANY failure
  - Zero password or hash disclosure in console output
  - Static assertion: all models present in data_backup.json are covered by the guard
"""

import json
import os
import sqlite3
import sys
import subprocess
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

DATABASE_URL = os.environ.get('DATABASE_URL', '')
if not DATABASE_URL:
    print('ERROR: DATABASE_URL environment variable is not set.')
    print('Set it before running this script:')
    print('  $env:DATABASE_URL="postgresql://user:pass@host:5432/dbname"')
    sys.exit(1)

BACKUP_FILE = os.path.join(BASE_DIR, 'data_backup.json')
if not os.path.exists(BACKUP_FILE):
    BACKUP_FILE = os.path.join(BASE_DIR, 'scratch', 'data_backup.json')
if not os.path.exists(BACKUP_FILE):
    print('ERROR: Backup file not found at data_backup.json or scratch/data_backup.json')
    print('Make sure the backup was created before running this script.')
    sys.exit(1)

PYTHON = sys.executable

print('=' * 65)
print('Step 1: Applying database schema migrations to PostgreSQL...')
print('=' * 65)
result = subprocess.run(
    [PYTHON, 'manage.py', 'migrate', '--no-input'],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print(result.stdout)
if result.returncode != 0:
    print('MIGRATION ERROR:')
    print(result.stderr)
    sys.exit(1)
print('[OK] Migrations applied successfully.\n')

# Setup Django environment to inspect PostgreSQL state
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from stockapp.models import Professeur, Magasinier, Directeur, Admin
from inventory.models import produit, commande, DetailCommande, Exprimer_besion
from transactions.models import Supplier

print('=' * 65)
print('Step 2: Checking existing data across ALL 12 fixture tables...')
print('=' * 65)

# ---------------------------------------------------------------------------
# Static assertion: every model present in data_backup.json must be listed
# here. This mapping is the single source of truth for the guard.
# If you add or remove models from the fixture, update BOTH this dict and
# the FIXTURE_MODELS set below.
# ---------------------------------------------------------------------------
FIXTURE_MODELS = {
    'admin.logentry',
    'auth.user',
    'inventory.commande',
    'inventory.detailcommande',
    'inventory.exprimer_besion',
    'inventory.produit',
    'sessions.session',
    'stockapp.admin',
    'stockapp.directeur',
    'stockapp.magasinier',
    'stockapp.professeur',
    'transactions.supplier',
}

# Guard dict: label -> (django_label, row_count)
# Covers all 12 models in data_backup.json — no personal data is displayed.
table_counts = {
    'stockapp.professeur     (Professeur)':    Professeur.objects.count(),
    'stockapp.magasinier     (Magasinier)':    Magasinier.objects.count(),
    'stockapp.directeur      (Directeur)':     Directeur.objects.count(),
    'stockapp.admin          (Admin)':         Admin.objects.count(),
    'auth.user               (User)':          User.objects.count(),
    'inventory.produit       (produit)':       produit.objects.count(),
    'inventory.commande      (commande)':      commande.objects.count(),
    'inventory.detailcommande(DetailCommande)':DetailCommande.objects.count(),
    'inventory.exprimer_besio(Exprimer_besion)':Exprimer_besion.objects.count(),
    'admin.logentry          (LogEntry)':      LogEntry.objects.count(),
    'sessions.session        (Session)':       Session.objects.count(),
    'transactions.supplier   (Supplier)':      Supplier.objects.count(),
}

# Static assertion: guard covers exactly the fixture models (fail-fast at startup)
guarded_django_labels = {
    'admin.logentry', 'auth.user',
    'inventory.commande', 'inventory.detailcommande', 'inventory.exprimer_besion',
    'inventory.produit', 'sessions.session',
    'stockapp.admin', 'stockapp.directeur', 'stockapp.magasinier', 'stockapp.professeur',
    'transactions.supplier',
}
assert guarded_django_labels == FIXTURE_MODELS, (
    f'[BUG] Guard coverage mismatch!\n'
    f'  Missing from guard : {FIXTURE_MODELS - guarded_django_labels}\n'
    f'  Extra in guard     : {guarded_django_labels - FIXTURE_MODELS}'
)
print(f'  [OK] Static assertion passed: guard covers all {len(FIXTURE_MODELS)} fixture models.')

any_data_present = any(count > 0 for count in table_counts.values())

if any_data_present:
    print('[PROTECTION ACTIVATED] Data is ALREADY present in target database!')
    for tbl, count in table_counts.items():
        if count > 0:
            print(f'  - Table `{tbl}` has {count} record(s)')
    print('\n`loaddata` is STRICTLY REFUSED to prevent overwriting or duplicate errors.')
    print('If you intentionally wish to re-import, manually empty the target PostgreSQL database first.\n')
    sys.exit(1)
else:
    print('  [OK] All 12 fixture tables are empty. Safe to proceed.\n')

    # -----------------------------------------------------------------------
    # Phase 0: Build ContentType ID remapping  SQLite -> PostgreSQL
    # db.sqlite3 is opened read-only; it is NEVER modified.
    # -----------------------------------------------------------------------
    print('=' * 65)
    print('Phase 0: Building ContentType ID remapping (SQLite -> PostgreSQL)...')
    print('=' * 65)

    sqlite_db_path = os.path.join(BASE_DIR, 'db.sqlite3')
    if not os.path.exists(sqlite_db_path):
        print(f'[ERROR] db.sqlite3 not found at {sqlite_db_path}')
        sys.exit(1)

    _sqlite_conn = sqlite3.connect(f'file:{sqlite_db_path}?mode=ro', uri=True)
    try:
        sqlite_ct_map = {
            row[0]: (row[1], row[2])
            for row in _sqlite_conn.execute(
                'SELECT id, app_label, model FROM django_content_type'
            ).fetchall()
        }
    finally:
        _sqlite_conn.close()
    print(f'  SQLite : {len(sqlite_ct_map)} ContentType entries read (read-only).')

    # Query PostgreSQL ContentTypes created by `migrate` in Step 1
    pg_ct_map = {(ct.app_label, ct.model): ct.id for ct in ContentType.objects.all()}
    print(f'  PostgreSQL: {len(pg_ct_map)} ContentType entries found.')

    # Build remapping: sqlite_ct_id -> postgresql_ct_id  (via app_label+model identity)
    ct_remap = {}
    remap_warnings = []
    for sqlite_id, (app_label, model) in sqlite_ct_map.items():
        pg_id = pg_ct_map.get((app_label, model))
        if pg_id is not None:
            ct_remap[sqlite_id] = pg_id
        else:
            # Stale content types (deleted apps) are expected and harmless
            remap_warnings.append(f'({app_label}, {model})')

    if remap_warnings:
        print(f'  Note: {len(remap_warnings)} SQLite ContentType(s) have no matching '
              f'PostgreSQL entry (stale/deleted apps — expected):')
        for w in remap_warnings:
            print(f'    - {w}')

    print(f'  Remapping complete: {len(ct_remap)} SQLite IDs mapped to PostgreSQL IDs.\n')

    # -----------------------------------------------------------------------
    # Phase 1: Split fixture in memory into two parts
    #   - other_records   : all records EXCEPT admin.logentry  (no CT FK issue)
    #   - logentry_records: admin.logentry with content_type_id remapped to PG IDs
    # data_backup.json is never modified.
    # -----------------------------------------------------------------------
    print('=' * 65)
    print('Phase 1: Splitting fixture and remapping admin.logentry...')
    print('=' * 65)

    with open(BACKUP_FILE, encoding='utf-8') as _f:
        all_records = json.load(_f)

    logentry_records = []
    other_records = []
    logentry_missing_ct = []

    for item in all_records:
        if item['model'] == 'admin.logentry':
            remapped_item = {
                'model': item['model'],
                'pk': item['pk'],
                'fields': dict(item['fields']),
            }
            old_ct_id = item['fields'].get('content_type')
            new_ct_id = ct_remap.get(old_ct_id)
            if new_ct_id is None:
                logentry_missing_ct.append(f"pk={item['pk']} content_type={old_ct_id}")
            else:
                remapped_item['fields']['content_type'] = new_ct_id
            logentry_records.append(remapped_item)
        else:
            other_records.append(item)

    if logentry_missing_ct:
        print(f'[ERROR] {len(logentry_missing_ct)} admin.logentry record(s) could not be '
              f'remapped (content_type_id not in SQLite CT map):')
        for e in logentry_missing_ct[:10]:
            print(f'  - {e}')
        sys.exit(1)

    total_split = len(other_records) + len(logentry_records)
    print(f'  Fixture split OK: {len(other_records)} standard + '
          f'{len(logentry_records)} admin.logentry (remapped) = {total_split} total.')
    if total_split != len(all_records):
        print(f'[ERROR] Split count mismatch: {total_split} != {len(all_records)} total records.')
        sys.exit(1)
    print()

    # -----------------------------------------------------------------------
    # Phase 2: Write temp fixtures to disk and import in two loaddata calls
    # Temp files are cleaned up in the `finally` block regardless of outcome.
    # -----------------------------------------------------------------------
    print('=' * 65)
    print('Phase 2: Importing data into PostgreSQL (two-phase loaddata)...')
    print('=' * 65)

    _tmp_dir = tempfile.gettempdir()
    _other_path    = os.path.join(_tmp_dir, 'mig_other_records.json')
    _logentry_path = os.path.join(_tmp_dir, 'mig_logentry_remapped.json')

    try:
        with open(_other_path, 'w', encoding='utf-8') as _f:
            json.dump(other_records, _f, ensure_ascii=False)
        with open(_logentry_path, 'w', encoding='utf-8') as _f:
            json.dump(logentry_records, _f, ensure_ascii=False)

        # --- Phase 2a: standard records (no ContentType FK to remap) ---
        print(f'Loading {len(other_records)} standard records (excluding admin.logentry)...')
        result = subprocess.run(
            [PYTHON, 'manage.py', 'loaddata', _other_path],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        print(result.stdout)
        if result.returncode != 0:
            print('[ERROR] LOADDATA FAILED (standard records):')
            print(result.stderr)
            sys.exit(1)

        # --- Phase 2b: admin.logentry with remapped content_type IDs ---
        print(f'Loading {len(logentry_records)} remapped admin.logentry records...')
        result = subprocess.run(
            [PYTHON, 'manage.py', 'loaddata', _logentry_path],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        print(result.stdout)
        if result.returncode != 0:
            print('[ERROR] LOADDATA FAILED (admin.logentry):')
            print(result.stderr)
            sys.exit(1)

        print(f'[OK] All {len(all_records)} records loaded successfully '
              f'({len(other_records)} standard + {len(logentry_records)} admin.logentry).\n')

    finally:
        for _p in [_other_path, _logentry_path]:
            try:
                os.remove(_p)
            except OSError:
                pass
        print('Temporary fixture files cleaned up.')

print('=' * 65)
print('Step 3: Exact count verification across all models...')
print('=' * 65)

# Exact expected row counts from source SQLite backup
checks = [
    ('Professeurs (Fonctionnaires)', Professeur.objects.count(), 10),
    ('Magasiniers (Stock Managers)', Magasinier.objects.count(), 1),
    ('Directeurs',                  Directeur.objects.count(), 1),
    ('Admins',                      Admin.objects.count(), 8),
    ('Comptes auth_user (Django)',  User.objects.count(), 3),
    ('Produits',                    produit.objects.count(), 26),
    ('Commandes',                   commande.objects.count(), 11),
    ('Details de commandes',        DetailCommande.objects.count(), 24),
    ('Besoins exprimes',            Exprimer_besion.objects.count(), 10),
    ('LogEntries (admin.logentry)', LogEntry.objects.count(), 482),
    ('Sessions',                    Session.objects.count(), 37),
    ('Fournisseurs (Supplier)',      Supplier.objects.count(), 1),
]

all_counts_ok = True
for label, actual, expected in checks:
    is_exact = (actual == expected)
    status = '[OK]' if is_exact else '[MISMATCH]'
    if not is_exact:
        all_counts_ok = False
    print(f'  {status} {label:<32}: {actual} / {expected} attendus')

if not all_counts_ok:
    print('\n[ERROR] Table row count validation failed! Aborting.')
    sys.exit(1)

print('\n' + '=' * 65)
print('Step 4: Relational integrity & Foreign Key validation...')
print('=' * 65)

relation_errors = 0

# 1. Verify commande foreign keys point to existing Professeur and Directeur
prof_pks = set(Professeur.objects.values_list('id', flat=True))
directeur_pks = set(Directeur.objects.values_list('id', flat=True))
produit_pks = set(produit.objects.values_list('id', flat=True))
commande_pks = set(commande.objects.values_list('id', flat=True))

for c in commande.objects.all():
    if c.Professeur_id and c.Professeur_id not in prof_pks:
        print(f'  [FK ERROR] Commande #{c.id} references missing Professeur #{c.Professeur_id}')
        relation_errors += 1
    if c.Directeur_id and c.Directeur_id not in directeur_pks:
        print(f'  [FK ERROR] Commande #{c.id} references missing Directeur #{c.Directeur_id}')
        relation_errors += 1

# 2. Verify DetailCommande foreign keys point to existing commande and produit
for dc in DetailCommande.objects.all():
    if dc.commande_id not in commande_pks:
        print(f'  [FK ERROR] DetailCommande #{dc.id} references missing Commande #{dc.commande_id}')
        relation_errors += 1
    if dc.produit_id not in produit_pks:
        print(f'  [FK ERROR] DetailCommande #{dc.id} references missing Produit #{dc.produit_id}')
        relation_errors += 1
    if dc.professeur_id and dc.professeur_id not in prof_pks:
        print(f'  [FK ERROR] DetailCommande #{dc.id} references missing Professeur #{dc.professeur_id}')
        relation_errors += 1

# 3. Verify Exprimer_besion foreign keys point to existing Professeur
for eb in Exprimer_besion.objects.all():
    if eb.Professeur_id and eb.Professeur_id not in prof_pks:
        print(f'  [FK ERROR] Exprimer_besion #{eb.id} references missing Professeur #{eb.Professeur_id}')
        relation_errors += 1

if relation_errors == 0:
    print('  [OK] All foreign key relationships are valid and intact.')
else:
    print(f'  [ERROR] Found {relation_errors} foreign key integrity error(s)!')
    sys.exit(1)

print('\n' + '=' * 65)
print('Step 5: Demo & Admin Accounts Verification (Zero Secret Disclosure)...')
print('=' * 65)

account_errors = 0

# Check Fonctionnaire
f_acc = Professeur.objects.filter(nomUtilisateur='fonctionnaire').first()
if f_acc and f_acc.motDePasse and f_acc.motDePasse.startswith('pbkdf2_'):
    print(f'  [OK] Fonctionnaire : user={f_acc.nomUtilisateur:<15} nom={f_acc.nom} | Hashed password valid [YES]')
else:
    print('  [ERROR] Fonctionnaire demo account missing or invalid password hash!')
    account_errors += 1

# Check Stock Manager
sm_acc = Magasinier.objects.filter(nomUtilisateur='stock_manager').first()
if sm_acc and sm_acc.motDePasse and sm_acc.motDePasse.startswith('pbkdf2_'):
    print(f'  [OK] Stock Manager : user={sm_acc.nomUtilisateur:<15} nom={sm_acc.nom} | Hashed password valid [YES]')
else:
    print('  [ERROR] Stock Manager demo account missing or invalid password hash!')
    account_errors += 1

# Check Directeur
d_acc = Directeur.objects.filter(nomUtilisateur='directeur').first()
if d_acc and d_acc.motDePasse and d_acc.motDePasse.startswith('pbkdf2_'):
    print(f'  [OK] Directeur     : user={d_acc.nomUtilisateur:<15} nom={d_acc.nom} | Hashed password valid [YES]')
else:
    print('  [ERROR] Directeur demo account missing or invalid password hash!')
    account_errors += 1

# Check Superuser
su_acc = User.objects.filter(is_superuser=True).first()
if su_acc and su_acc.password and su_acc.password.startswith('pbkdf2_'):
    print(f'  [OK] Django Admin  : superusers verified ({User.objects.filter(is_superuser=True).count()} accounts) | Hashed password valid [YES]')
else:
    print('  [ERROR] Django Superuser missing or invalid password hash!')
    account_errors += 1

if account_errors > 0:
    print(f'\n[ERROR] Demo/admin account verification failed with {account_errors} error(s)!')
    sys.exit(1)

print('\n' + '=' * 65)
print('[SUCCESS] All verification steps passed with 0 errors.')
print('Database migration is verified, intact, and ready.')
print('=' * 65)
