from django.contrib import admin

from .models import Professeur, Directeur, Magasinier, Admin

# Register your models here.

admin.site.register(Professeur)

admin.site.register(Directeur)

admin.site.register(Magasinier)

admin.site.register(Admin)




