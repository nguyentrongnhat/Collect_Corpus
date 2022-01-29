from django.urls import path
from . import views

urlpatterns = [
    path('search', views.search, name='search_elastic'),
    path('delete/doc', views.delete_doc, name='delete_doc'),
    path('insert', views.insert, name='insert_elastic'),
    path('inserts/range', views.range_inserts, name='range_inserts_elastic'),
    path('inserts/multipage', views.multipage_inserts, name='multipage_insert_elastic'),
    path('source/doc/all', views.all_doc_from_source, name='all_doc_from_source'),
    path('source/delete', views.source_delete, name='source_delete'),
    path('progress/download', views.update_progress_download, name='update_progress_download'),
    path('progress/save', views.update_progress_save, name='update_progress_save'),
    path('result/list_document', views.result_list_document, name='resutl_list_document'),
    path('thread/pause', views.pause_thread, name='pause_thread'),
    path('thread/resume', views.resume_thread, name='resume_thread'),
    path('thread/stop', views.stop_thread, name='stop_thread'),
]