from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from .models import Professeur, Directeur, Magasinier, Admin

DEMO_USERNAMES = {'fonctionnaire', 'stock_manager', 'directeur', 'ali', 'ilham', 'hosam', 'admin', 'alii'}

def home(request):
    return render(request, 'commander/list_commande_fonctionnaire.html')


def signup(request):
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        role = request.POST.get('role', 'fonctionnaire').strip()
        departement = request.POST.get('option_type', 'Informatique').strip()
        nomUtilisateur = request.POST.get('nomUtilisateur', '').strip()
        motDePasse = request.POST.get('motDePasse', '')
        confirme_motdepasse = request.POST.get('confirme_motdepasse', '')

        context = {
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'telephone': telephone,
            'role': role,
            'departement': departement,
            'nomUtilisateur': nomUtilisateur,
        }

        if not nomUtilisateur or not motDePasse:
            context['error'] = 'Veuillez remplir tous les champs obligatoires.'
            return render(request, 'signup.html', context)

        if motDePasse != confirme_motdepasse:
            context['error'] = 'Les mots de passe ne sont pas identiques.'
            return render(request, 'signup.html', context)

        # Check if username already exists in any user table
        username_taken = (
            Professeur.objects.filter(nomUtilisateur__iexact=nomUtilisateur).exists() or
            Magasinier.objects.filter(nomUtilisateur__iexact=nomUtilisateur).exists() or
            Directeur.objects.filter(nomUtilisateur__iexact=nomUtilisateur).exists() or
            Admin.objects.filter(nomUtilisateur__iexact=nomUtilisateur).exists()
        )

        if username_taken:
            context['error'] = "Ce nom d'utilisateur est déjà utilisé. Veuillez en choisir un autre."
            return render(request, 'signup.html', context)

        # Create account depending on selected role
        if role == 'gestionnaire':
            user = Magasinier(
                nom=nom,
                prenom=prenom,
                email=email,
                telephone=telephone,
                nomUtilisateur=nomUtilisateur,
                motDePasse=motDePasse
            )
            user.save()
        else:
            # Default to fonctionnaire (Professeur)
            user = Professeur(
                nom=nom,
                prenom=prenom,
                email=email,
                telephone=telephone,
                departement=departement if departement else 'Informatique',
                nomUtilisateur=nomUtilisateur,
                motDePasse=motDePasse
            )
            user.save()

        messages.success(request, f"Votre compte '{nomUtilisateur}' a été créé avec succès ! Connectez-vous dès maintenant.")
        return redirect('my_login')

    return render(request, 'signup.html')


def my_login(request):
    def authen_magasinier(username, password):
        try:
            user = Magasinier.objects.get(nomUtilisateur=username)
            if user.check_password(password):
                return user
        except (Magasinier.DoesNotExist, Magasinier.MultipleObjectsReturned):
            pass
        return None

    def authen_directeur(username, password):
        try:
            user = Directeur.objects.get(nomUtilisateur=username)
            if user.check_password(password):
                return user
        except (Directeur.DoesNotExist, Directeur.MultipleObjectsReturned):
            pass
        return None

    def authen_professeur(username, password):
        try:
            user = Professeur.objects.get(nomUtilisateur=username)
            if user.check_password(password):
                return user
        except (Professeur.DoesNotExist, Professeur.MultipleObjectsReturned):
            pass
        return None

    def authen_admin(username, password):
        try:
            user = Admin.objects.get(nomUtilisateur=username)
            if user.check_password(password):
                return user
        except (Admin.DoesNotExist, Admin.MultipleObjectsReturned):
            pass
        return None

    if request.method == 'POST':
        nomUtilisateur = request.POST.get('nomUtilisateur', '').strip()
        motDePasse = request.POST.get('motDePasse', '')

        professeur = authen_professeur(nomUtilisateur, motDePasse)
        magasinier = authen_magasinier(nomUtilisateur, motDePasse)
        directeur = authen_directeur(nomUtilisateur, motDePasse)
        admin = authen_admin(nomUtilisateur, motDePasse)

        is_demo = nomUtilisateur.lower() in DEMO_USERNAMES

        if professeur is not None:
            request.session['role'] = 'fonctionnaire'
            request.session['user_id'] = professeur.id
            request.session['username'] = professeur.nomUtilisateur
            request.session['full_name'] = f"{professeur.prenom} {professeur.nom}"
            request.session['is_demo'] = is_demo
            return redirect('inventory')

        if magasinier is not None:
            request.session['role'] = 'magasinier'
            request.session['user_id'] = magasinier.id
            request.session['username'] = magasinier.nomUtilisateur
            request.session['full_name'] = f"{magasinier.prenom} {magasinier.nom}"
            request.session['is_demo'] = is_demo
            return redirect('list_produit')

        if directeur is not None:
            request.session['role'] = 'directeur'
            request.session['user_id'] = directeur.id
            request.session['username'] = directeur.nomUtilisateur
            request.session['full_name'] = f"{directeur.prenom} {directeur.nom}"
            request.session['is_demo'] = is_demo
            return redirect('list_produit_directeur')

        if admin is not None:
            request.session['role'] = 'admin'
            request.session['user_id'] = admin.id
            request.session['username'] = admin.nomUtilisateur
            request.session['full_name'] = f"{admin.prenom} {admin.nom}"
            request.session['is_demo'] = is_demo
            return redirect('inventory')

        return render(request, 'my_login.html', {'error': 'Nom d\'utilisateur ou mot de passe incorrect !'})

    return render(request, 'my_login.html')


def Logout(request):
    logout(request)
    request.session.flush()
    return redirect('my_login')
