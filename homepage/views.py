from django.shortcuts import render
from django.views.generic import View, TemplateView
from inventory.models import produit
from transactions.models import SaleBill, PurchaseBill


class HomeView(View):
    template_name = "home.html"
    def get(self, request):        
        labels = []
        data = []        
        stockqueryset = produit.objects.filter(is_deleted=False).order_by('-quantity_produit')
        for item in stockqueryset:
            labels.append(item.name_produit)
            data.append(item.quantity_produit)
        sales = SaleBill.objects.order_by('-time')[:3]
        purchases = PurchaseBill.objects.order_by('-time')[:3]
        context = {
            'labels'    : labels,
            'data'      : data,
            'sales'     : sales,
            'purchases' : purchases
        }
        return render(request, self.template_name, context)

# class AboutView(TemplateView):
#     template_name = "about.html"
