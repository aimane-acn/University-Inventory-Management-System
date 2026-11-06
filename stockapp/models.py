from django.db import models
from django.contrib.auth.hashers import check_password, make_password

# Helper function to hash raw passwords safely
def safe_make_password(password):
    if password and not (
        password.startswith('pbkdf2_') or
        password.startswith('bcrypt') or
        password.startswith('argon2')
    ):
        return make_password(password)
    return password

class Professeur(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=254)
    prenom = models.CharField(max_length=254)
    email = models.EmailField(max_length=254)
    telephone = models.CharField(max_length=20)
    is_deleted = models.BooleanField(default=False)
    departement = models.CharField(max_length=254)
    nomUtilisateur = models.CharField(max_length=254)
    motDePasse = models.CharField(max_length=254)
    last_login = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.motDePasse = safe_make_password(self.motDePasse)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)
    
    def check_password(self, raw_motDePasse):
        return check_password(raw_motDePasse, self.motDePasse)


class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=254)
    prenom = models.CharField(max_length=254)
    email = models.EmailField(max_length=254)
    telephone = models.CharField(max_length=20)
    is_deleted = models.BooleanField(default=False)
    nomUtilisateur = models.CharField(max_length=254)
    motDePasse = models.CharField(max_length=254)
    last_login = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.motDePasse = safe_make_password(self.motDePasse)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom
    
    def check_password(self, raw_motDePasse):
        return check_password(raw_motDePasse, self.motDePasse)


class Directeur(models.Model):
    nom = models.CharField(max_length=254)
    prenom = models.CharField(max_length=254)
    email = models.CharField(max_length=254)
    telephone = models.CharField(max_length=254)
    nomUtilisateur = models.CharField(max_length=254)
    motDePasse = models.CharField(max_length=254)
    last_login = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        self.motDePasse = safe_make_password(self.motDePasse)
        super().save(*args, **kwargs)

    def check_password(self, raw_motDePasse):
        return check_password(raw_motDePasse, self.motDePasse)


class Magasinier(models.Model):
    nom = models.CharField(max_length=254)
    prenom = models.CharField(max_length=254)
    email = models.CharField(max_length=254)
    telephone = models.CharField(max_length=254)
    nomUtilisateur = models.CharField(max_length=254)
    motDePasse = models.CharField(max_length=254)
    last_login = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        self.motDePasse = safe_make_password(self.motDePasse)
        super().save(*args, **kwargs)

    def check_password(self, raw_motDePasse):
        return check_password(raw_motDePasse, self.motDePasse)
