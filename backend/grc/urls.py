from django.urls import path
from django.http import HttpResponse
from . import views
from .views import create_workflow, create_incident_from_audit_finding

urlpatterns = [
    # path('login/', views.login, name='login'),
    # path('register/', views.register, name='register'),
     path('', lambda request: HttpResponse("API is working ✅")),
    path('incidents/', views.list_incidents, name='list-incidents'),
    path('api/incidents/', views.list_incidents, name='api-list-incidents'),
    path('incidents/create/', views.create_incident, name='create-incident'),
    path('api/login/', views.login, name='api_login'),
    path('audit-findings/unchecked/', views.unchecked_audit_findings, name='unchecked-audit-findings'),
    path('users/', views.list_users, name='list-users'),
    path('workflow/create/', create_workflow, name='workflow-create'),
    path('workflow/assigned/', views.list_assigned_findings, name='list-assigned-findings'),
    path('dashboard/incidents/', views.combined_incidents_and_audit_findings, name='dashboard-incidents'),
    path('incident/from-audit-finding/', create_incident_from_audit_finding, name='incident_from_audit_finding'),
    path('incident/schedule-manual/', views.schedule_manual_incident, name='schedule_manual_incident'),
    path('incident/reject/', views.reject_incident, name='reject_incident'),
    path('api/frameworks/<int:framework_id>/policies/', views.add_policy_to_framework, name='add-policy-to-framework'),
    path('api/policy-approvals/reviewer/', views.list_policy_approvals_for_reviewer, name='policy-approvals-for-reviewer'),
    path('api/policy-approvals/<int:approval_id>/', views.update_policy_approval, name='update_policy_approval'),
    path('api/policy-approvals/<int:approval_id>/review/', views.submit_policy_review, name='submit_policy_review'),
    path('api/policy-approvals/rejected/<int:user_id>/', views.list_rejected_policy_approvals_for_user),
    path('api/policy-approvals/resubmit/<int:approval_id>/', views.resubmit_policy_approval),
    path('frameworks/', views.get_frameworks, name='get-frameworks'),
    path('api/policies/<int:policy_id>/subpolicies/', views.get_subpolicies, name='get-subpolicies'),
    path('compliance/create/', views.create_compliance, name='create-compliance'),
    path('compliance/<int:compliance_id>/edit/', views.edit_compliance, name='edit-compliance'),
    path('compliance/<int:compliance_id>/clone/', views.clone_compliance, name='clone-compliance'),
    path('compliance/dashboard/', views.get_compliance_dashboard, name='compliance-dashboard'),
    path('api/compliance-approvals/<int:approval_id>/review/', views.submit_compliance_review, name='submit_compliance_review'),
    path('api/compliance-approvals/resubmit/<int:approval_id>/', views.resubmit_compliance_approval, name='resubmit_compliance_approval'),
]


 
 