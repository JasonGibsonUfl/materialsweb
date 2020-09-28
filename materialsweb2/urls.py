"""materialsweb2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from pages import views
from electronic_visualization import simpleexample
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('about', views.about_view, name='about'),
    path('api', views.api_view, name='api'),
    path('docs', views.docs_view, name='docs'),
    path('contact', views.contact_view, name='contact'),
    path('logout', views.home_view, name='Sign Out'),
    path('accounts/', include(('accounts.urls', 'accounts'),namespace='accounts')),
    path('', include('django.contrib.auth.urls')),
    path('database', views.database_view, name='database'),
    path('database/<int:pk>', views.result_view, name='result'),
    path('', include('api.urls')),
    path('gasp', views.gasp_view, name='gasp'),
    path('electronic_visualization', views.electronic_visualization_view, name='electronic_visualization'),
    path('substrate', views.substrate_view, name='substrate'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('lattice_matching/', include(('lattice_matching.urls', 'lattice_matching'), namespace='lattice_matching')),
    path('models', views.models_view, name='models'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)