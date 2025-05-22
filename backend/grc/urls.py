
from django.urls import path, include
from django.http import HttpResponse
from . import views
from rest_framework.routers import DefaultRouter
from .views import create_workflow, create_incident_from_audit_finding,RiskViewSet, IncidentViewSet, ComplianceViewSet, RiskInstanceViewSet



router = DefaultRouter()
router.register(r'risks', views.RiskViewSet)
router.register(r'incidents', views.IncidentViewSet)
router.register(r'compliances', views.ComplianceViewSet)
router.register(r'risk-instances', views.RiskInstanceViewSet)


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



    path('test-connection/', views.test_connection, name='test-connection'),
    path('api/', include(router.urls)),
    path('api/last-incident/', views.last_incident, name='last-incident'),
    path('api/compliance-by-incident/<int:incident_id>/', views.get_compliance_by_incident, name='compliance-by-incident'),
    path('api/risks-by-incident/<int:incident_id>/', views.get_risks_by_incident, name='risks-by-incident'),
    path('api/analyze-incident/', views.analyze_incident, name='analyze-incident'),
    path('api/risk/metrics', views.risk_metrics, name='risk_metrics'),
    path('users/', views.get_users, name='get-users'),
    path('api/risk-workflow/', views.risk_workflow, name='risk-workflow'),
    path('api/risk-assign/', views.assign_risk_instance, name='risk-assign'),
    path('api/custom-users/', views.get_custom_users, name='custom-users'),
    path('api/user-risks/<int:user_id>/', views.get_user_risks, name='user-risks'),
    path('api/risk-update-status/', views.update_risk_status, name='risk-update-status'),
    path('api/risk-mitigations/<int:risk_id>/', views.get_risk_mitigations, name='risk-mitigations'),
    path('api/update-mitigation-status/', views.update_mitigation_approval, name='update-mitigation-status'),
    path('api/assign-reviewer/', views.assign_reviewer, name='assign-reviewer'),
    path('api/reviewer-tasks/<int:user_id>/', views.get_reviewer_tasks, name='reviewer-tasks'),
    # path('api/update-mitigation-approval/', views.update_mitigation_approval, name='update-mitigation-approval'),
    path('api/complete-review/', views.complete_review, name='complete-review'),
    # path('api/user-notifications/<int:user_id>/', views.get_user_notifications, name='user-notifications'),
    path('api/reviewer-comments/<int:risk_id>/', views.get_reviewer_comments, name='reviewer-comments'),
    path('api/latest-review/<int:risk_id>/', views.get_latest_review, name='latest-review'),
    path('api/get-assigned-reviewer/<int:risk_id>/', views.get_assigned_reviewer, name='get-assigned-reviewer'),
    path('api/risk-update-mitigation/<int:risk_id>/', views.update_risk_mitigation, name='risk-update-mitigation'),

]


 
 