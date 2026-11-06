from django.urls import path,reverse
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.StockListView.as_view(), name='inventory'),
    path('new', views.StockCreateView.as_view(), name='new-stock'),
    path('edit-stock/<int:pk>/', views.StockUpdateView.as_view(), name='edit-stock'),
    path('delete-stock/<int:pk>/', views.StockDeleteView.as_view(), name='delete-stock'),
       

    path('list_besion', views.BesionListView.as_view(), name='list_besion'),
    path('new_besion', views.BesionCreateView.as_view(), name='new-besion'),
    path('besion/<pk>/edit', views.BesionUpdateView.as_view(), name='edit-besion'),
    path('besion/<pk>/delete', views.BesionDeleteView.as_view(), name='delete-besion'),
    path('view_more/<int:commande_id>/', views.view_more, name='view_more'),
    
    path('list_produit', views.ProduitListView.as_view(), name='list_produit'),
    path('produit', views.ProduitCreateView.as_view(), name='new-produit'),
    path('produit/<pk>/edit', views.ProduitUpdateView.as_view(), name='edit-produit'),
    path('produit/<pk>/delete', views.ProduitDeleteView.as_view(), name='delete-produit'),
    
    


    path('list_commande', views.CommandeListView.as_view(), name='list_commande'),
    path('list_produit', views.ProduitListView.as_view(), name='list_produit'),
    path('list_besions', views.BeesionListView.as_view(), name='list_besions'),

    path('viww_besoin/<int:commande_id>/', views.viww_besoin, name='viww_besoin'),
    path('view_besoin/<int:commande_id>/', views.view_besoin, name='view_besoin'),

    path('view_more_magasinier/<int:commande_id>/', views.view_more_magasinier, name='view_more_magasinier'),


    path('list_commande_directeur', views.CommandedirecteurListView.as_view(), name='list_commande_directeur'),
    path('list_produit_directeur', views.ProduitdirecteurListView.as_view(), name='list_produit_directeur'),
    path('list_archive', views.CommandedirecteurarchiveListView.as_view(), name='list_archive'),
    path('list_archive_directeur', views.BesiondirecteurarchiveListView.as_view(), name='list_archive_directeur'),
    path('list_besion_directeur', views.BesiondirecteurListView.as_view(), name='list_besion_directeur'),

    path('view_more_besoin_archive/<int:commande_id>/', views.view_more_besoin_archive, name='view_more_besoin_archive'),


    path('view_more_besoin/<int:commande_id>/', views.view_more_besoin, name='view_more_besoin'),

    path('view_more_archive/<int:commande_id>/',views.view_more_archive, name='view_more_archive'),

    path('view_more_directeur/<int:commande_id>/', views.view_more_directeur, name='view_more_directeur'),


    path('dashboard/', views.dashboard.as_view(), name='dashboard'),
    path('dashboard_directeur', views.dashboardDirecteur.as_view(), name='dashboard_directeur'),
    path('dashboard_plus', views.DashboardView, name='dashboard_plus'),


    path('ajouter_prof', views.Professeuradd.as_view(), name='ajouter_prof'),
    path('list_fonctionnaire', views.ProfesseurList.as_view(), name='list_fonctionnaire'),
    path('modifier/<pk>/prof', views.ModifierProfesseur.as_view(), name='modifier_prof'),
    path('supprimer/<pk>/prof', views.SupprimerProfesseur.as_view(), name='supprimer_prof'),

    path('ajouter_admin', views.Adminadd.as_view(), name='ajouter_admin'),
    path('list_admin', views.AdminList.as_view(), name='list_admin'),
    path('modifier/<pk>/admin', views.ModifierAdmin.as_view(), name='modifier_admin'),
    path('supprimer/<pk>/admin', views.SupprimerAdmin.as_view(), name='supprimer_admin'),


]
