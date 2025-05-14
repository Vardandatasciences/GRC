from django.urls import path
from . import views
from .views import create_workflow

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('incidents/', views.list_incidents, name='list-incidents'),
    path('incidents/create/', views.create_incident, name='create-incident'),
    path('api/login/', views.login, name='api_login'),
    path('audit-findings/unchecked/', views.unchecked_audit_findings, name='unchecked-audit-findings'),
    path('users/', views.list_users, name='list-users'),
    path('workflow/create/', create_workflow, name='workflow-create'),
    path('workflow/assigned/', views.list_assigned_findings, name='list-assigned-findings'),
]
