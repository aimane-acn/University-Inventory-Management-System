from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    View,
    CreateView, 
    UpdateView,
    ListView
) 
from django.urls import reverse_lazy
from django.http import JsonResponse
from collections import defaultdict
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import produit,commande,Exprimer_besion,DetailCommande
from stockapp.models import Professeur,Directeur,Magasinier,Admin
from .forms import BesionForm,ProduitForm,CommandeForm
from django_filters.views import FilterView
from .filters import StockFilterproduit,StockFilterbesion,StockFiltercommande,DetailCommandeFilter
from django.http import HttpResponse
from django.db.models import Count, Min

# Constants to isolate demo accounts from newly created visitor data/spam
DEMO_PROF_IDS = [11, 15, 16, 17, 18, 19, 20, 21]
DEMO_ADMIN_IDS = [3, 4, 5, 6, 7, 8, 9, 10]
DEMO_MAX_COMMANDE_ID = 10
DEMO_MAX_BESOIN_ID = 9
DEMO_MAX_PRODUIT_ID = 46


def view_more_besoin_archive(request, commande_id):
    besoin = Exprimer_besion.objects.filter(id=commande_id)
    return render(request, 'directeur/view_more_besoin_archive.html', {'details_commande': besoin})


def view_besoin(request, commande_id):
    besoin = Exprimer_besion.objects.filter(id=commande_id)
    return render(request, 'produit/view_besoin.html', {'details_commande': besoin})


def view_more_besoin(request, commande_id):
    besoin = Exprimer_besion.objects.filter(id=commande_id)
    return render(request, 'directeur/view_more_besoin.html', {'details_commande': besoin})


def viww_besoin(request, commande_id):
    besoin = Exprimer_besion.objects.filter(id=commande_id)
    return render(request, 'besion/viww_besoin.html', {'details_commande': besoin})


def DashboardView(request):
    details_qs = DetailCommande.objects.all()
    if request.session.get('is_demo', False):
        details_qs = details_qs.filter(commande_id__lte=DEMO_MAX_COMMANDE_ID)
    produits_plus_commandes = details_qs.values('produit__name_produit').annotate(total_commandes=Count('produit')).order_by('-total_commandes')[:5]
    
    context = {
        'produits_plus_commandes': produits_plus_commandes,
    }
    
    return render(request, 'directeur/dashbord_plus.html', context)



def view_more_archive(request, commande_id):
    details_commande = DetailCommande.objects.filter(commande_id=commande_id)
    return render(request, 'directeur/view_more_archive.html', {'details_commande': details_commande})


class BesiondirecteurarchiveListView(FilterView):
    filterset_class = StockFilterbesion
    template_name = 'directeur/list_archive_directeur.html'
    paginate_by = 10 

    def get_queryset(self):
        qs = Exprimer_besion.objects.filter(is_deleted=True)
        if self.request.session.get('is_demo', False):
            qs = qs.filter(id__lte=DEMO_MAX_BESOIN_ID)
        return qs.order_by('-Date')

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["detail_list"] = self.get_queryset()      
        return context



def view_more_magasinier(request, commande_id):
    details_commande = DetailCommande.objects.filter(commande_id=commande_id)
    return render(request, 'produit/view_more_magasinier.html', {'details_commande': details_commande})



def view_more_directeur(request, commande_id):
    details_commande = DetailCommande.objects.filter(commande_id=commande_id)
    return render(request, 'directeur/view_more_directeur.html', {'details_commande': details_commande})

class SupprimerAdmin(View):
    template_name = "directeur/supprimer_admin.html"
    success_message = "L'administrateur a été supprimé avec succès"

    def get(self, request, pk):
        admin = get_object_or_404(Admin, pk=pk)
        return render(request, self.template_name, {'object' : admin})

    def post(self, request, pk):  
        admin = get_object_or_404(Admin, pk=pk)
        admin.delete()                                             
        messages.success(request, self.success_message)
        return redirect('list_admin')




class ModifierAdmin(SuccessMessageMixin, UpdateView):
    model = Admin
    #form_class = ProfEditForm
    success_url = 'directeur/list_admin'
    success_message = "les détails d'administrateur ont été mis à jour avec succès"
    template_name = "directeur/modifier_admin.html"
    fields = ['nom', 'prenom', 'email', 'telephone']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Modifier l'administrateur"
        context["savebtn"] = 'Sauvgarder'
        context["delbtn"] = 'Delete Supplier'
        context["admin"] = Admin.objects.get(id=self.kwargs.get("pk"))
        return context
    
    def get_object(self, queryset=None):
        # Récupérer l'ID de la commande à partir de l'URL
        admin_id = self.kwargs.get("pk")
        # Récupérer l'objet DetailCommande correspondant à l'ID de la commande
        return get_object_or_404(Admin, id=admin_id)

    def post(self, request, *args, **kwargs):
        # Utiliser self.object pour accéder à l'objet DetailCommande actuel
        admin = self.get_object()

        email = request.POST.get("email")
        telephone = request.POST.get("telephone")
        # Mettre à jour les champs de l'objet DetailCommande
        admin.email = email
        admin.telephone = telephone
        admin.save()

        return redirect('list_admin')


class AdminList(ListView):
    model = Admin
    template_name = "directeur/list_admin.html"
    paginate_by = 10

    def get_queryset(self):
        qs = Admin.objects.filter(is_deleted=False).order_by('id')
        if self.request.session.get('is_demo', False):
            qs = qs.filter(id__in=DEMO_ADMIN_IDS)
        return qs



class Adminadd(SuccessMessageMixin, CreateView):
    model = Admin
    fields = ['nom', 'prenom', 'email', 'telephone', 'nomUtilisateur', 'motDePasse']
    success_url = reverse_lazy('list_admin')
    success_message = "L'admin a été créé avec succès"
    template_name = "directeur/ajouter_admin.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Ajouter un administrateur'
        context["savebtn"] = 'Ajouter'
        return context    
    def post(self, request, *args, **kwargs):
        # Utiliser self.object pour accéder à l'objet DetailCommande actuel
        if request.method == 'POST':
            nom = request.POST.get("nom")
            prenom = request.POST.get("prenom")
            email = request.POST.get("email")
            telephone = request.POST.get("telephone")
            nomUtilisateur = request.POST.get("nomUtilisateur")
            motDePasse = request.POST.get("motDePasse")

            # Mettre à jour les champs de l'objet DetailCommande
            admin=Admin.objects.create(nom=nom,prenom=prenom,email=email,telephone=telephone,nomUtilisateur=nomUtilisateur,motDePasse=motDePasse)
            admin.save()

        return redirect('list_admin')


class SupprimerProfesseur(View):
    template_name = "directeur/supprimer_prof.html"
    success_message = "Le professeur a été supprimé avec succès"

    def get(self, request, pk):
        prof = get_object_or_404(Professeur, pk=pk)
        return render(request, self.template_name, {'object' : prof})

    def post(self, request, pk):  
        prof = get_object_or_404(Professeur, pk=pk)
        prof.delete()                                              
        messages.success(request, self.success_message)
        return redirect('list_fonctionnaire')



class ModifierProfesseur(SuccessMessageMixin, UpdateView):
    model = Professeur
    #form_class = ProfEditForm
    success_url = 'directeur/list_fonctionnaire'
    success_message = "les détails du professeur ont été mis à jour avec succès"
    template_name = "directeur/modifier_prof.html"
    fields = ['nom', 'prenom', 'email', 'telephone', 'departement']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Modifier le professeur'
        context["savebtn"] = 'Sauvgarder'
        context["delbtn"] = 'Delete Supplier'
        context["prof"] = Professeur.objects.get(id=self.kwargs.get("pk"))
        return context
    
    def get_object(self, queryset=None):
        # Récupérer l'ID de la commande à partir de l'URL
        prof_id = self.kwargs.get("pk")
        # Récupérer l'objet DetailCommande correspondant à l'ID de la commande
        return get_object_or_404(Professeur, id=prof_id)

    def post(self, request, *args, **kwargs):
        # Utiliser self.object pour accéder à l'objet DetailCommande actuel
        prof = self.get_object()

        email = request.POST.get("email")
        telephone = request.POST.get("telephone")
        departement = request.POST.get("departement")
        # Mettre à jour les champs de l'objet DetailCommande
        prof.email = email
        prof.telephone = telephone
        prof.departement = departement
        prof.save()

        return redirect('list_fonctionnaire')


class ProfesseurList(ListView):
    model = Professeur
    template_name = "directeur/list_fonctionnaire.html"
    paginate_by = 10

    def get_queryset(self):
        qs = Professeur.objects.filter(is_deleted=False).order_by('id')
        if self.request.session.get('is_demo', False):
            qs = qs.filter(id__in=DEMO_PROF_IDS)
        return qs



class Professeuradd(SuccessMessageMixin, CreateView):
    model = Professeur
    fields = ['nom', 'prenom', 'email', 'telephone', 'departement', 'nomUtilisateur', 'motDePasse']
    success_url = reverse_lazy('list_fonctionnaire')
    success_message = "Le fonctionnaire a été créé avec succès"
    template_name = "directeur/ajouter_prof.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Ajouter un professeur'
        context["savebtn"] = 'Ajouter'
        return context    
    def post(self, request, *args, **kwargs):
        # Utiliser self.object pour accéder à l'objet DetailCommande actuel
        if request.method == 'POST':
            nom = request.POST.get("nom")
            prenom = request.POST.get("prenom")
            email = request.POST.get("email")
            telephone = request.POST.get("telephone")
            departement = request.POST.get("departement")
            nomUtilisateur = request.POST.get("nomUtilisateur")
            motDePasse = request.POST.get("motDePasse")
            # Mettre à jour les champs de l'objet DetailCommande
            Prof=Professeur.objects.create(nom=nom,prenom=prenom,email=email,telephone=telephone,departement=departement,nomUtilisateur=nomUtilisateur,motDePasse=motDePasse)
            Prof.save()

        return redirect('list_fonctionnaire')





class dashboard(View):
    template_name = 'produit/dashboard_magasinier.html'
    def get(self, request):
        labels = []
        data = []
        produits = produit.objects.filter(is_deleted=False)
        if request.session.get('is_demo', False):
            produits = produits.filter(id__lte=DEMO_MAX_PRODUIT_ID)
        produits = produits.order_by('-quantity_produit')
        for item in produits:
            labels.append(item.name_produit)
            data.append(item.quantity_produit)
        
        context = {
            'labels'    : labels,
            'data'      : data,
        }
        return render(request, self.template_name, context)
    


class dashboardDirecteur(View):
    template_name = 'produit/dashboard_directeur.html'

    def get(self, request):
        labels = []
        data = []
        produits = produit.objects.filter(is_deleted=False)
        if request.session.get('is_demo', False):
            produits = produits.filter(id__lte=DEMO_MAX_PRODUIT_ID)
        produits = produits.order_by('-quantity_produit')
        for item in produits:
            labels.append(item.name_produit)
            data.append(item.quantity_produit)

        # Trouver la valeur minimale de Min parmi les produits
        min_value = produits.aggregate(min_value=Min('Min'))['min_value']

        context = {
            'labels': labels,
            'data': data,
            'min_value': min_value,
        }
        return render(request, self.template_name, context)







# class StockListView(FilterView):
#     filterset_class = StockFilter
#     queryset = produit.objects.filter(is_deleted=False)
#     template_name = 'inventory.html'
#     paginate_by = 10
from django.db.models import Prefetch

def view_more(request, commande_id):
        details_commande = DetailCommande.objects.filter(commande_id=commande_id)
        commandee = commande.objects.filter(id=commande_id)
        if request.method == 'POST':
           commandee.delete()  
           return redirect('/inventory')
        return render(request, 'commander/view_more.html', {'details_commande': details_commande})



class StockListView(FilterView):
    model = commande
    template_name = 'commander/list_commande_fonctionnaire.html'
    paginate_by = 15

    def get_queryset(self):
        qs = commande.objects.all()
        if self.request.session.get('is_demo', False):
            qs = qs.filter(id__lte=DEMO_MAX_COMMANDE_ID)
        return qs.order_by('-Date').prefetch_related(Prefetch('detailcommande_set', queryset=DetailCommande.objects.all().select_related('produit')))
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commande_list"] = context.get("object_list", self.get_queryset())
        return context
    def post(self, request):
            commande_id = request.POST.get('commande_id')
            validation_status = request.POST.get('validation')

            # Assume you have a 'Commande' model with a 'validation' field
            com= commande.objects.get(id=commande_id)
            details= DetailCommande.objects.filter(commande=com)
            # prod= produit.objects.get(id=idd)
            if validation_status == 'recus':
                com.is_deleted = True
                com.validation  = 'recus'
                for detail in details:    
                    prod = detail.produit
                    prod.quantity_produit -= detail.quantite
                    prod.save()
                
            com.save()
            detail.save()
            # Redirect to the same page after processing the form
            return redirect('/inventory')
    

    

class BesionListView(FilterView):
    filterset_class = StockFilterbesion
    template_name = 'besion/list_besion.html'
    paginate_by = 15

    def get_queryset(self):
        qs = Exprimer_besion.objects.all()
        if self.request.session.get('is_demo', False):
            qs = qs.filter(id__lte=DEMO_MAX_BESOIN_ID)
        return qs.order_by('-Date')

class BeesionListView(FilterView):
    filterset_class = StockFilterbesion
    template_name = 'produit/list_des_besoin.html'
    paginate_by = 10

    def get_queryset(self):
        qs = Exprimer_besion.objects.filter(is_deleted=True)
        if self.request.session.get('is_demo', False):
            qs = qs.filter(id__lte=DEMO_MAX_BESOIN_ID)
        return qs.order_by('-Date')

    def get_context_data(self, **kwargs):                                               # used to send additional context
            context = super().get_context_data(**kwargs)
            context["detail_list"] = self.get_queryset()      
            return context


class ProduitListView(FilterView):
    filterset_class = StockFilterproduit
    template_name = 'produit/list_produit.html'
    paginate_by = 10  

    def get_queryset(self):
        qs = produit.objects.all().order_by('id')
        if self.request.session.get('is_demo', False):
            qs = qs.filter(id__lte=DEMO_MAX_PRODUIT_ID)
        self.filterset = self.filterset_class(self.request.GET, queryset=qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):                                              
        context = super().get_context_data(**kwargs)
        context["stocks"] = self.filterset.qs
        context["error"] = 'Le produit va presque finis'
        return context


        

class CommandedirecteurarchiveListView(FilterView):
        filterset_class = DetailCommandeFilter  
        template_name = 'directeur/list_archive.html'
        detail_list = DetailCommande.objects.all()
        paginate_by = 10  

        def get_queryset(self):
            qs = commande.objects.filter(is_deleted=True)
            if self.request.session.get('is_demo', False):
                qs = qs.filter(id__lte=DEMO_MAX_COMMANDE_ID)
            return qs.order_by('-Date')

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            commandess = self.get_queryset().order_by('-Date').prefetch_related(Prefetch('detailcommande_set', queryset=DetailCommande.objects.all().select_related('produit')))
            context["commande_list"] = commandess
            proff_qs = Professeur.objects.all()
            if self.request.session.get('is_demo', False):
                proff_qs = proff_qs.filter(id__in=DEMO_PROF_IDS)
            context["proff"] = proff_qs  
            return context

class CommandeListView(FilterView):
        filterset_class = StockFiltercommande
        template_name = 'produit/list_commande.html'
        detail_list = DetailCommande.objects.all()
        paginate_by = 10

        def get_queryset(self):
            qs = commande.objects.filter(is_deleted=True).order_by('-Date', 'id')
            if self.request.session.get('is_demo', False):
                qs = qs.filter(id__lte=DEMO_MAX_COMMANDE_ID)
            return qs

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            commandes = self.get_queryset().order_by('-Date').prefetch_related(Prefetch('detailcommande_set', queryset=DetailCommande.objects.all().select_related('produit')))
            context["commande_list"] = commandes
            proff_qs = Professeur.objects.all()
            if self.request.session.get('is_demo', False):
                proff_qs = proff_qs.filter(id__in=DEMO_PROF_IDS)
            context["proff"] = proff_qs  
            return context     


        

            



    
class ProduitdirecteurListView(FilterView):
    filterset_class = StockFilterproduit
    template_name = 'directeur/list_produit_directeur.html'
    paginate_by = 10
    
    def get_queryset(self):
        qs = produit.objects.filter(is_deleted=False)
        if self.request.session.get('is_demo', False):
            qs = qs.filter(id__lte=DEMO_MAX_PRODUIT_ID)
        return qs.order_by('name_produit')

    def get_context_data(self, **kwargs):                                               # used to send additional context
            context = super().get_context_data(**kwargs)
            context["stocks"] = self.get_queryset()
            context["error"] = 'Le produit va presque finis'
            return context   
  
class BesiondirecteurListView(FilterView):
    filterset_class = StockFilterbesion
    template_name = 'directeur/list_besion_directeur.html'
    paginate_by = 10 

    def get_queryset(self):
        qs = Exprimer_besion.objects.filter(is_deleted=False)
        if self.request.session.get('is_demo', False):
            qs = qs.filter(id__lte=DEMO_MAX_BESOIN_ID)
        return qs.order_by('-Date')

    def get_context_data(self, **kwargs):                                               # used to send additional context
            context = super().get_context_data(**kwargs)
            context["detail_list"] = self.get_queryset()      
            return context 
    def post(self, request):
            besoin_id = request.POST.get('besoin_id')
            validation_status = request.POST.get('validation')

            # Assume you have a 'Commande' model with a 'validation' field
            besoin = Exprimer_besion.objects.get(id=besoin_id)
            if validation_status == 'Accepter':
                besoin.validation = 'Accepter' 
                besoin.is_deleted = True  
            else :
                besoin.is_deleted = True 
                besoin.validation = 'Refuse'   
            besoin.save()
            # Redirect to the same page after processing the form
            return redirect('list_besion_directeur')


# class StockCreateView(SuccessMessageMixin, CreateView):                                 # createview class to add new stock, mixin used to display message
#     model = produit                                                                      # setting 'Stock' model as model
#     form_class = ProduitForm                                                            # setting 'StockForm' form as form
#     template_name = "edit_stock.html"                                                   # 'edit_stock.html' used as the template
#     success_url = '/inventory'                                                          # redirects to 'inventory' page in the url after submitting the form
#     success_message = "Stock has been created successfully"                             # displays message when form is submitted

#     def get_context_data(self, **kwargs):                                               # used to send additional context
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'New Stock'
#         context["savebtn"] = 'Add to Inventory'
#         context["stocks"] = produit.objects.all
#         return context       

class StockCreateView(CreateView):
    model = commande
    template_name = "commander/ajouter_commande.html"
    success_url = "/inventory"
    form_class = CommandeForm   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Nouvelle commande'
        context["savebtn"] = 'Envoyer'
        stocks = produit.objects.all()
        if self.request.session.get('is_demo', False):
            stocks = stocks.filter(id__lte=DEMO_MAX_PRODUIT_ID)
        context["stocks"] = stocks
        return context    

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            
            produits = request.POST.getlist('produit_id[]')
            quantites = request.POST.getlist('quantite[]')
            prof_id = request.session.get('user_id') if request.session.get('role') == 'fonctionnaire' else 11
            commandee = commande.objects.create(Professeur_id=prof_id)
            for produit_id, quantite in zip(produits, quantites):
                pro = produit.objects.get(id=produit_id)
                quantite = int(quantite)
                if quantite > pro.Max:
                        commandee.delete()
                        return render(request,'commander/ajouter_commande.html',{'error': 'La quantité dépasse la limite donnée',
                                                                            'title': 'Nouvel commande',
                                                                            'savebtn': 'Ajouter',
                                                                            'besion': 'Ajouter le besion',
                                                                            'stocks': produit.objects.all(),
                                                                            'produit': pro})
                   
                
                DetailCommande.objects.create(commande=commandee, produit_id=produit_id, quantite=quantite, professeur_id=prof_id)

            
        return redirect('/inventory')

        # for produit_id, quantite in zip(produits, quantites):
        #         pro = Produit.objects.get(id=produit_id)
        #         quantite = int(quantite)
        #         if quantite > pro.Max:
        #             # Supprimer la commande créée
        #             commandee.delete()
        #             return render(request, 'commander/ajouter_commande.html', {
        #                 'error': 'La quantité dépasse la limite donnée',
        #                 'title': 'Nouvelle commande',
        #                 'savebtn': 'Ajouter',
        #                 'besion': 'Ajouter le besion',
        #                 'stocks': Produit.objects.all(),
        #                 'produit': pro
        #             })
        #         DetailCommande.objects.create(commande=commandee, produit_id=produit_id, quantite=quantite)

        #     return HttpResponseRedirect(self.get_success_url())

        # return super().post(request, *args, **kwargs)

            


class BesionCreateView(SuccessMessageMixin, CreateView):                                 # createview class to add new stock, mixin used to display message
    model = Exprimer_besion                                                                      # setting 'Stock' model as model
    form_class = BesionForm                                                          # setting 'StockForm' form as form
    template_name = "besion/exprimer_besion.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/inventory/list_besion'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Le besoin a été créé avec succès"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Exprimer un besoin'
        context["savebtn"] = 'Envoyer '
        # context["stocks"] = produit.objects.all
        return context

    def form_valid(self, form):
        prof_id = self.request.session.get('user_id')
        if prof_id and self.request.session.get('role') == 'fonctionnaire':
            form.instance.Professeur_id = prof_id
        return super().form_valid(form)  


class ProduitCreateView(SuccessMessageMixin, CreateView):                                 # createview class to add new stock, mixin used to display message
    model = produit                                                                      # setting 'Stock' model as model
    form_class = ProduitForm                                                            # setting 'StockForm' form as form
    template_name = "produit/ajouter_produit.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/inventory/list_produit'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Le produit a été créé avec succès"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Ajouter des nouveaux produits'
        context["savebtn"] = 'Envoyer'
        
        return context 
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            noms = request.POST.getlist('nom[]')
            descriptions = request.POST.getlist('description[]')
            quantites = request.POST.getlist('quantite[]')

            for nom, description, quantite in zip(noms, descriptions, quantites):
                produit.objects.create(name_produit=nom, description=description, quantity_produit=quantite)

        return redirect('list_produit')
 
    # def select_article(request):
    #     if request.method == 'POST':
    #         form = CommandeForm(request.POST)
    #         if form.is_valid():
    #             article_id = form.cleaned_data['id']
    #             selected_article = commande.objects.get(pk=article_id)
    #             # Faites ce que vous voulez avec l'article sélectionné
    #             return render(request, 'inventory.html', {'name_commande': selected_article})
    #     else:
    #         form = CommandeForm()
    #     return render(request, 'edit_stock.html', {'form': form})
    
# class StockUpdateView(SuccessMessageMixin, UpdateView):                                 # updateview class to edit stock, mixin used to display message
#     model = produit                                                                      # setting 'Stock' model as model
#     form_class = ProduitForm                                                              # setting 'StockForm' form as form
#     template_name = "edit_stock.html"                                                   # 'edit_stock.html' used as the template
#     success_url = '/inventory'                                                          # redirects to 'inventory' page in the url after submitting the form
#     success_message = "Stock has been updated successfully"                             # displays message when form is submitted

#     def get_context_data(self, **kwargs):                                               # used to send additional context
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'Edit Stock'
#         context["savebtn"] = 'Update Stock'
#         context["delbtn"] = 'Delete Stock'
#         return context

                                 # updateview class to edit stock, mixin used to display message
    # model = commande                                                                      # setting 'Stock' model as model
    # # form_class = CommandeForm                                                              # setting 'StockForm' form as form
    # template_name = "commander/modifier_commande.html"                                                   # 'edit_stock.html' used as the template
    # success_url = 'inventory'                                                          # redirects to 'inventory' page in the url after submitting the form
    # success_message = "La commande a été mis à jour avec succès"                             # displays message when form is submitted

    #                             # displays message when form is submitted

    # def get_context_data(self, **kwargs):                                               # used to send additional context
    #     context = super().get_context_data(**kwargs)
    #     context["title"]    = 'Nouvel commande'
    #     context["savebtn"]  = 'Ajouter'
    #     context["besion"]   = 'Ajouter le besion'
    #     produit_id = self.kwargs.get('pk')
    #     context["stock"] = self.model.objects.get(id=produit_id)

    #     return context
      
    # def form_valid(self, form):
    #     response = super().form_valid(form)
    #     return response
    
# class StockUpdateView(SuccessMessageMixin, UpdateView):
#     model = DetailCommande
#     template_name = "commander/modifier_commande.html"
#     success_url = "/inventory"
#     success_message = "La commande a été modifiée avec succès"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'modifier commande'
#         context["savebtn"] = 'modifier'
#         context["stocks"] = produit.objects.all()

#         return context

#     def post(self, request, *args, **kwargs):
#         commande_id = self.kwargs.get('pk')
#         produit_id = request.POST.get('produit')
#         quantite = request.POST.get('quantite')

#         detail_commande = DetailCommande.objects.get(commande=commande_id)
#         detail_commande.produit= produit_id
#         detail_commande.quantite = quantite
#         detail_commande.save()

#         return redirect('/inventory')




class StockUpdateView(SuccessMessageMixin, UpdateView):
    model = DetailCommande
    template_name = "commander/modifier_commande.html"
    success_url = "/inventory"
    success_message = "La commande a été modifiée avec succès"
    fields = ['produit', 'quantite']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Modifier la commande'
        context["savebtn"] = 'Modifier'
        context["stocks"] = produit.objects.all()
        return context

    def get_object(self, queryset=None):
        # Récupérer l'ID de la commande à partir de l'URL
        commande_id = self.kwargs.get("pk")
        # Récupérer l'objet DetailCommande correspondant à l'ID de la commande
        return get_object_or_404(DetailCommande, id=commande_id)
    
    def post(self, request, *args, **kwargs):
        # Utiliser self.object pour accéder à l'objet DetailCommande actuel
        detail_commande = self.get_object()
        produit_id = request.POST.get("produit_id")
        quantite = request.POST.get("quantite")
        produit_instance = get_object_or_404(produit, pk=produit_id)
        quantite = int( quantite)
        if quantite > produit_instance.Max:
                 return render(request,'commander/modifier_commande.html',{'error': 'La quantité dépasse la limite donnée',
                                                                            'title': 'Modifier la commande',
                                                                            'savebtn': 'Modifier',
                                                                            
                                                                            'stocks': produit.objects.all(),
                                                                            })
        # Mettre à jour les champs de l'objet DetailCommande
        detail_commande.produit = produit_instance
        detail_commande.quantite = quantite
        detail_commande.save()
        return redirect('/inventory')







# class StockUpdateView(SuccessMessageMixin, UpdateView):
#         model = commande                                                                      # setting 'Stock' model as model
#         form_class = CommandeForm                                                            # setting 'StockForm' form as form
#         template_name = "commander/modifier_commande.html"                                                   # 'edit_stock.html' used as the template
#         success_url = "/inventory"                                                          # redirects to 'inventory' page in the url after submitting the form
#         success_message = "La commande a été créé avec succès"                             # displays message when form is submitted

#         def get_context_data(self, **kwargs):                                               # used to send additional context
#             context = super().get_context_data(**kwargs)
#             context["title"]    = 'modifier commande'
#             context["savebtn"]  = 'modifier'
#             context["stocks"]   = produit.objects.all
#             commande_id = self.kwargs.get('pk')
#             context["stock"] = commande.objects.get(id=commande_id)
               
#         def post(self, request):
#             if request.method == 'POST':
                
#                 comandeid=request.POST.get('id')
#                 produit_id = request.POST.get('produit_id')
#                 quantite = request.POST.get('quantite')
#                 # Assume you have a 'Commande' model with a 'validation' field
#                 DetailCommandee=DetailCommande.objects.update(commande=comandeid,produit_id=produit_id, quantite=quantite)
#                 DetailCommandee.save()
               

#                 # Redirect to the same page after processing the form
#                 return redirect('/inventory')

        
class BesionUpdateView(SuccessMessageMixin, UpdateView):                                 # updateview class to edit stock, mixin used to display message
    model = Exprimer_besion                                                                      # setting 'Stock' model as model
    form_class = BesionForm                                                              # setting 'StockForm' form as form
    template_name = "besion/exprimer_besion.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/inventory/list_besion'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Le besoin a été mis à jour avec succès"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Modifier le besoin'
        context["savebtn"] = 'modifier'
        context["delbtn"] = 'Supprimer'
        return context
    
class ProduitUpdateView(SuccessMessageMixin, UpdateView):                                 # updateview class to edit stock, mixin used to display message
    model = produit                                                                      # setting 'Stock' model as model
    form_class = ProduitForm                                                              # setting 'StockForm' form as form
    template_name = "produit/modifier_produit.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/inventory/list_produit'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Le produit a été mis à jour avec succès"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Modifier le produit'
        context["savebtn"] = 'Modifier'
        context["delbtn"] = 'Supprimer'
        return context


# class StockDeleteView(View):                                                            # view class to delete stock
#     template_name = "delete_stock.html"                                                 # 'delete_stock.html' used as the template
#     success_message = "Stock has been deleted successfully"                             # displays message when form is submitted
    
#     def get(self, request, pk):
#         stock = get_object_or_404(produit, pk=pk)
#         return render(request, self.template_name, {'object' : stock})

#     def post(self, request, pk):  
#         stock = get_object_or_404(produit, pk=pk)
#         stock.is_deleted = True
#         stock.save()                                               
#         messages.success(request, self.success_message)
#         return redirect('inventory')
    

class StockDeleteView(SuccessMessageMixin, UpdateView):                                                            # view class to delete stock
    model = DetailCommande
    template_name = "commander/supprimer_commande.html"
    success_url = "/inventory"
    success_message = "La commande a été supprimer avec succès"
    fields = ['produit', 'quantite']
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Supprimer commande'
        context["savebtn"] = 'Oui, supprimer'
        context["stocks"] = produit.objects.all()
        return context
    
    
    def get_object(self, queryset=None):
        # Récupérer l'ID de la commande à partir de l'URL
        commande_id = self.kwargs.get("pk")
        # Récupérer l'objet DetailCommande correspondant à l'ID de la commande
        return get_object_or_404(DetailCommande, id=commande_id)
    
    def post(self, request, *args, **kwargs):
        # Utiliser self.object pour accéder à l'objet DetailCommande actuel
        detail_commande = self.get_object()
        detail_commande.delete()

        return redirect('/inventory')



class BesionDeleteView(View):                                                            # view class to delete stock
    template_name = "besion/supprimer_besion.html"                                                 # 'delete_stock.html' used as the template
    success_message = "Le besoin a été supprimé avec succès"                             # displays message when form is submitted
    
    def get(self, request, pk):
        besion = get_object_or_404(Exprimer_besion, pk=pk)
        return render(request, self.template_name, {'object' : besion})

    def post(self, request, pk):  
        besion = get_object_or_404(Exprimer_besion, pk=pk)
        besion.delete()                                            
        messages.success(request, self.success_message)
        return redirect('list_besion')

class ProduitDeleteView(View):                                                            # view class to delete stock
    template_name = "produit/supprimer_produit.html"                                                   # 'edit_stock.html' used as the template
                                                                              # 'delete_stock.html' used as the template
    success_message = "Le produit a été supprimé avec succès"                             # displays message when form is submitted
    
    def get(self, request, pk):
        stock = get_object_or_404(produit, pk=pk)
        return render(request, self.template_name, {'object' : stock})

    def post(self, request, pk):  
        stock = get_object_or_404(produit, pk=pk)
        stock.delete()                                             
        messages.success(request, self.success_message)
        return redirect('list_produit')
    




class CommandedirecteurListView(FilterView):
        filterset_class = DetailCommandeFilter  
        template_name = 'directeur/list_commande_directeur.html'
        detail_list = DetailCommande.objects.all()
        paginate_by = 10

        def get_queryset(self):
            qs = commande.objects.filter(is_deleted=False)
            if self.request.session.get('is_demo', False):
                qs = qs.filter(id__lte=DEMO_MAX_COMMANDE_ID)
            return qs

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            commandes = self.get_queryset().order_by('-Date').prefetch_related(Prefetch('detailcommande_set', queryset=DetailCommande.objects.all().select_related('produit')))
            context["commande_list"] = commandes
            proff_qs = Professeur.objects.all()
            if self.request.session.get('is_demo', False):
                proff_qs = proff_qs.filter(id__in=DEMO_PROF_IDS)
            context["proff"] = proff_qs  
            return context
                   
        def post(self, request):
            commande_id = request.POST.get('commande_id')
            validation_status = request.POST.get('validation')

            # Assume you have a 'Commande' model with a 'validation' field
            com= commande.objects.get(id=commande_id)
            
            if validation_status == 'Accepter':
                com.is_deleted = True
                com.validation  = 'Accepter'
                
            elif validation_status == 'Refuser':
                com.is_deleted = True
                com.validation = 'Refuser'

            com.save()
            
            # Redirect to the same page after processing the form
            return redirect('list_commande_directeur')