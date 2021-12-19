from django.urls import path
from . import views

urlpatterns = [
    path('search', views.search, name='search_elastic'),
    path('insert', views.insert, name='insert_elastic'),
    path('inserts/range', views.range_inserts, name='range_inserts_elastic'),
    path('inserts/multipage', views.multipage_inserts, name='multipage_insert_elastic'),
]