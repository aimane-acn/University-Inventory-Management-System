import django_filters
from .models import produit,commande,Exprimer_besion,DetailCommande


class StockFilterproduit(django_filters.FilterSet):                            
    name_produit = django_filters.CharFilter(lookup_expr='icontains')         
    class Meta:
        model = produit
        fields = ['name_produit']
  


class StockFiltercommande(django_filters.FilterSet):                            # Stockfilter used to filter based on name
    date = django_filters.DateFilter(field_name='date', label='Date (YYYY-MM-DD)', lookup_expr='date')          # allows filtering without entering the full name
    class Meta:
        model = commande
        fields = ['date']

class StockFilterbesion(django_filters.FilterSet):                            # Stockfilter used to filter based on name
    name_besion = django_filters.CharFilter(lookup_expr='icontains')           # allows filtering without entering the full name
    class Meta:
        model = Exprimer_besion
        fields = ['name_besion']

class DetailCommandeFilter(django_filters.FilterSet):
    commande_date = django_filters.DateFilter(field_name='commande_date', label='Command Date (YYYY-MM-DD)', lookup_expr='exact')
    produit_name = django_filters.CharFilter(field_name='produit_name', label='Product Name', lookup_expr='icontains')

    class Meta:
        model = DetailCommande
        fields = {
            'is_deleted': ['exact'],
            'quantite': ['exact', 'gte', 'lte'],
        }