from . import views
from django.urls import path, include

urlpatterns = [
    path('app', views.lattice_matching_view, name='app'),
    ]