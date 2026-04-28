from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('privacy/', views.privacy_view, name='privacy'),
    path('terms/', views.terms_view, name='terms'),
    path('contact/', views.contact_view, name='contact'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manager-dashboard/', views.manager_dashboard_view, name='manager_dashboard'),
    
    path('workflows/', views.workflow_list, name='workflow_list'),
    path('workflows/create/', views.workflow_create, name='workflow_create'),
    path('workflows/<int:pk>/', views.workflow_detail, name='workflow_detail'),
    
    path('entities/create/', views.entity_create, name='entity_create'),
    path('entities/<int:pk>/', views.entity_detail, name='entity_detail'),
    path('entities/<int:pk>/delete/', views.entity_delete, name='entity_delete'),
    
    path('entities/<int:entity_id>/transition/<int:transition_id>/', views.execute_transition, name='execute_transition'),
]