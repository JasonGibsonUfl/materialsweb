from . import views
from django.urls import path, include
from django.conf.urls import url

urlpatterns = [
    path('app', views.lattice_matching_view, name='app'),
    ]