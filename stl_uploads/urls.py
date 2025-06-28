from django.urls import path
from . import views

app_name = 'stl_uploads'

urlpatterns = [
    path('', views.stl_list, name='list'),
    path('upload/', views.stl_upload, name='upload'),
    path('<int:pk>/', views.stl_detail, name='detail'),
    path('<int:pk>/delete/', views.delete_stl, name='delete'),
    path('<int:pk>/download/', views.download_stl, name='download'),
    path('<int:pk>/preview/', views.preview_image, name='preview'),
    path('<int:pk>/reprocess/', views.reprocess_stl, name='reprocess'),
    path('<int:pk>/status/', views.check_processing_status, name='status'),
    path('<int:stl_pk>/order/', views.create_print_order, name='create_order'),
]