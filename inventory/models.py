from django.db import models
from stockapp.models import Magasinier,Professeur,Directeur
from django.utils import timezone
    
# class produit(models.Model):
#     id = models.AutoField(primary_key=True)
#     name_produit = models.CharField(max_length=30, unique=True)
#     quantity_produit = models.IntegerField(default=1)
#     is_deleted = models.BooleanField(default=False)
#     Magasinier = models.ForeignKey(Magasinier, on_delete=models.CASCADE,null=True, blank=True)

#     def __str__(self):
# 	    return self.name_produit

# class commande(models.Model):
#     id = models.AutoField(primary_key=True)
#     name_commande = models.CharField(max_length=30,blank=True, null=True)
#     quantity_commande = models.IntegerField(default=1)
#     is_deleted = models.BooleanField(default=False)
#     description = models.CharField(max_length=400, default='dfghj')
#     validation = models.CharField(max_length=254, default='en attente')
#     Professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE,null=True, blank=True)
#     Directeur = models.ForeignKey(Directeur, on_delete=models.CASCADE,null=True, blank=True)
    

#     def __str__(self):
# 	    return self.id
class produit(models.Model):
    id = models.AutoField(primary_key=True)
    name_produit = models.CharField(max_length=30, unique=True)
    quantity_produit = models.IntegerField(default=1)
    description = models.CharField(max_length=200, null=True, blank=True)
    Max = models.IntegerField(default=3)
    Min = models.IntegerField(default=3)
    is_deleted = models.BooleanField(default=False)
    def _str_(self):
	    return self.name_produit
    

class commande(models.Model):
    id = models.AutoField(primary_key=True)
    is_deleted = models.BooleanField(default=False)
    validation = models.CharField(max_length=254,default="en attente")
    Date = models.DateTimeField(default=timezone.now)
    Professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE,null=True, blank=True,default=11)
    Directeur = models.ForeignKey(Directeur, on_delete=models.CASCADE,null=True, blank=True,default=4)
    def _str_(self):
	    return str(self.id)

class DetailCommande(models.Model):
    id = models.AutoField(primary_key=True)
    is_deleted = models.BooleanField(default=False)
    commande = models.ForeignKey(commande, on_delete=models.CASCADE)
    produit = models.ForeignKey(produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=1)
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE,default=11)


   
class Exprimer_besion(models.Model):
    id = models.AutoField(primary_key=True)
    name_besion = models.CharField(max_length=30, unique=True)
    description_produit = models.CharField(max_length=200, unique=True)
    quantite = models.IntegerField(default=1)
    besion = models.CharField(max_length=200, unique=True)
    validation = models.CharField(max_length=254,default='en attente')
    Date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    Professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE,null=True, blank=True, default=11)

    def __str__(self):
        return self.name_besion
