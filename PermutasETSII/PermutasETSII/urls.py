"""
URL configuration for PermutasETSII project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


from Permutas.views import custom_login, home,todasPermutas,nuevaPermutas,registro,profile,logout,generate_pdf_from_existing, mis_permutas,aceptar_permuta,asignaturas_estudiante, grupos_estudiante,permutas_all,aceptar_solicitud_permuta

    
urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('permutas/', permutas_all, name='todasPermutas'),
    path('solicitar-permuta/', nuevaPermutas, name='nuevaPermuta'),
    path('', home, name='home'),
    path('register/', registro, name='register'),
    path('login/', custom_login, name='login'),
    path('logout/', logout, name='logout'),
    path('accounts/profile/', profile, name='profile'),
    path('generate-pdf/', generate_pdf_from_existing, name='generate_pdf'),
    path('mis-permutas/', mis_permutas, name='mis_permutas'),
    path('aceptar-permuta/<int:permuta_id>/', aceptar_permuta, name='aceptar_permuta'),
    path('aceptar-solicutud-permuta/<int:solicitud_permuta_id>/', aceptar_solicitud_permuta, name='aceptar_solicitud_permuta'),
    path('mis_asignaturas/', asignaturas_estudiante, name='asignaturas_estudiante'),
    path('mis_grupos/', grupos_estudiante, name='grupos_estudiante'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)