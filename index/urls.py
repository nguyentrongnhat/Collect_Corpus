from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search_data', views.search_page, name='search_page'),
]