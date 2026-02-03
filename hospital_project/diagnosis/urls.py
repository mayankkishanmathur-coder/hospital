from django.urls import path
from . import views

urlpatterns = [
    path('', views.diagnosis_index, name='diagnosis_index'),
    path('results/<int:record_id>/', views.diagnosis_results, name='diagnosis_results'),
    path('book/<int:record_id>/<int:doctor_id>/', views.book_from_diagnosis, name='book_from_diagnosis'),
    path('history/', views.diagnosis_history, name='diagnosis_history'),
    path('delete/<int:record_id>/', views.delete_diagnosis, name='delete_diagnosis'),
]
