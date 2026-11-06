from django import forms
from .models import produit,commande,Exprimer_besion,DetailCommande


class ProduitForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):                                                        # used to set css classes to the various fields
        super().__init__(*args, **kwargs)
        self.fields['name_produit'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['quantity_produit'].widget.attrs.update({'class': 'textinput form-control', 'min': '0' })
        self.fields['description'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = produit
        fields = ['name_produit' ,  'quantity_produit' , 'description']





class CommandeForm(forms.ModelForm):
    class Meta:
        model = commande
        fields = ['validation', 'Professeur', 'Directeur']
    




    


class BesionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):                                                        # used to set css classes to the various fields
        super().__init__(*args, **kwargs)
        self.fields['name_besion'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['quantite'].widget.attrs.update({'class': 'textinput form-control', 'min': '0' })
        self.fields['besion'].widget.attrs.update({'class': 'textinput form-control'})
    
    class Meta:
        model = Exprimer_besion
        fields = ['name_besion','quantite' ,'description_produit','besion']
        widgets = {
            'description_produit' : forms.Textarea(
                attrs = {
                    'class' : 'textinput form-control',
                    'rows'  : '4'
                }
            )

        }

