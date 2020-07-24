from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'elements', views.ElementViewSet)
router.register(r'calculation', views.CalculationViewSet)
router.register(r'entry', views.EntryViewSet)
router.register(r'composition', views.CompositionViewSet)
router.register(r'structure', views.StructureViewSet)
router.register(r'atom', views.AtomViewSet)
router.register(r'site', views.SiteViewSet)
router.register(r'species', views.SpeciesViewSet)
router.register(r'dos', views.DosViewSet)
router.register(r'spacegroup', views.SpacegroupViewSet)
router.register(r'wyckoffSite', views.WyckoffSiteViewSet)





# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('rest', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]