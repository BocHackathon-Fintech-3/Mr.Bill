from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/setup/start/', views.setup_start, name='setup_start'),
    path('dashboard/setup/step-1/', views.setup_step1, name='setup_step1'),
    path('dashboard/setup/step-2/', views.setup_step2, name='setup_step2'),
    path('dashboard/setup/complete/', views.setup_complete, name='setup_complete'),

]
