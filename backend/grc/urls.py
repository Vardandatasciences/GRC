from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import RiskViewSet, IncidentViewSet, ComplianceViewSet, RiskInstanceViewSet

router = DefaultRouter()
router.register(r'risks', views.RiskViewSet)
router.register(r'incidents', views.IncidentViewSet)
router.register(r'compliances', views.ComplianceViewSet)
router.register(r'risk-instances', views.RiskInstanceViewSet)

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('test-connection/', views.test_connection, name='test-connection'),
    path('api/', include(router.urls)),
    path('api/last-incident/', views.last_incident, name='last-incident'),
    path('api/compliance-by-incident/<int:incident_id>/', views.get_compliance_by_incident, name='compliance-by-incident'),
    path('api/risks-by-incident/<int:incident_id>/', views.get_risks_by_incident, name='risks-by-incident'),
    path('api/analyze-incident/', views.analyze_incident, name='analyze-incident'),
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
