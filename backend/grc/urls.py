from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import RiskViewSet, IncidentViewSet, ComplianceViewSet, RiskInstanceViewSet

router = DefaultRouter()
router.register(r'incidents', views.IncidentViewSet)
router.register(r'risk-instances', views.RiskInstanceViewSet)
router.register(r'risks', views.RiskViewSet)
router.register(r'compliances', views.ComplianceViewSet)

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('test-connection/', views.test_connection, name='test-connection'),
    # Include router URLs directly in the main urlpatterns
    path('', include(router.urls)),
    path('last-incident/', views.last_incident, name='last-incident'),
    path('compliance-by-incident/<int:incident_id>/', views.get_compliance_by_incident, name='compliance-by-incident'),
    path('risks-by-incident/<int:incident_id>/', views.get_risks_by_incident, name='risks-by-incident'),
    path('analyze-incident/', views.analyze_incident, name='analyze-incident'),
    path('risk/metrics', views.risk_metrics, name='risk_metrics'),
    path('users/', views.get_users, name='get-users'),
    path('risk-workflow/', views.risk_workflow, name='risk-workflow'),
    path('risk-assign/', views.assign_risk_instance, name='risk-assign'),
    path('custom-users/', views.get_custom_users, name='custom-users'),
    path('user-risks/<int:user_id>/', views.get_user_risks, name='user-risks'),
    path('risk-update-status/', views.update_risk_status, name='risk-update-status'),
    path('risk-mitigations/<int:risk_id>/', views.get_risk_mitigations, name='risk-mitigations'),
    path('update-mitigation-status/', views.update_mitigation_status, name='update-mitigation-status'),
    path('assign-reviewer/', views.assign_reviewer, name='assign-reviewer'),
    path('reviewer-tasks/<int:user_id>/', views.get_reviewer_tasks, name='reviewer-tasks'),
    # path('update-mitigation-approval/', views.update_mitigation_approval, name='update-mitigation-approval'),
    path('complete-review/', views.complete_review, name='complete-review'),
    # path('user-notifications/<int:user_id>/', views.get_user_notifications, name='user-notifications'),
    path('reviewer-comments/<int:risk_id>/', views.get_reviewer_comments, name='reviewer-comments'),
    path('latest-review/<int:risk_id>/', views.get_latest_review, name='latest-review'),
    path('get-assigned-reviewer/<int:risk_id>/', views.get_assigned_reviewer, name='get-assigned-reviewer'),
    path('risk-update-mitigation/<int:risk_id>/', views.update_risk_mitigation, name='risk-update-mitigation'),
    path('risk-form-details/<int:risk_id>/', views.get_risk_form_details, name='risk-form-details'),
    path('logs/', views.GRCLogList.as_view(), name='log-list'),
    path('logs/<int:pk>/', views.GRCLogDetail.as_view(), name='log-detail'),
]
