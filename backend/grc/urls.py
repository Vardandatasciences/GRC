from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import RiskViewSet, IncidentViewSet, ComplianceViewSet, RiskInstanceViewSet
from django.http import HttpResponse
router = DefaultRouter()
router.register(r'risks', views.RiskViewSet)
router.register(r'incidents', views.IncidentViewSet)
router.register(r'compliance', views.ComplianceViewSet)
router.register(r'risk-instances', views.RiskInstanceViewSet)

urlpatterns = [
    path('', lambda request: HttpResponse("API is working ✅")),

    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('test-connection/', views.test_connection, name='test-connection'),
    path('api/', include(router.urls)),
    path('api/last-incident/', views.last_incident, name='last-incident'),
    path('api/compliance-by-incident/<int:incident_id>/', views.get_compliance_by_incident, name='compliance-by-incident'),
    path('api/risks-by-incident/<int:incident_id>/', views.get_risks_by_incident, name='risks-by-incident'),
    path('api/analyze-incident/', views.analyze_incident, name='analyze-incident'),
    path('api/risk/metrics/', views.risk_metrics, name='risk_metrics'),
    path('api/risk/metrics-by-category/', views.risk_metrics_by_category, name='risk_metrics_by_category'),
    path('api/risk/kpi-data/', views.risk_kpi_data, name='risk_kpi_data'),
    path('api/risk/active-risks-kpi/', views.active_risks_kpi, name='active_risks_kpi'),
    path('api/risk/exposure-trend/', views.risk_exposure_trend, name='risk_exposure_trend'),
    path('api/risk/reduction-trend/', views.risk_reduction_trend, name='risk_reduction_trend'),
    path('api/risk/high-criticality/', views.high_criticality_risks, name='high_criticality_risks'),
    path('api/risk/mitigation-completion-rate/', views.mitigation_completion_rate, name='mitigation_completion_rate'),
    path('api/risk/avg-remediation-time/', views.avg_remediation_time, name='avg_remediation_time'),
    path('api/risk/recurrence-rate/', views.recurrence_rate, name='recurrence_rate'),
    path('api/risk/avg-incident-response-time/', views.avg_incident_response_time, name='avg_incident_response_time'),
    path('api/risk/mitigation-cost/', views.mitigation_cost, name='mitigation_cost'),
    path('api/risk/identification-rate/', views.risk_identification_rate, name='risk_identification_rate'),
    path('api/risk/due-mitigation/', views.due_mitigation, name='due_mitigation'),
    path('api/risk/classification-accuracy/', views.classification_accuracy, name='classification_accuracy'),
    path('api/risk/improvement-initiatives/', views.improvement_initiatives, name='improvement_initiatives'),
    path('api/risk/impact/', views.risk_impact, name='risk_impact'),
    path('api/risk/severity/', views.risk_severity, name='risk_severity'),
    path('api/risk/exposure-score/', views.risk_exposure_score, name='risk_exposure_score'),
    path('api/risk/resilience/', views.risk_resilience, name='risk_resilience'),
    path('api/risk/assessment-frequency/', views.risk_assessment_frequency, name='risk_assessment_frequency'),
    path('api/risk/assessment-consensus/', views.risk_assessment_consensus, name='risk_assessment_consensus'),
    path('api/risk/approval-rate-cycle/', views.risk_approval_rate_cycle, name='risk_approval_rate_cycle'),
    path('api/risk/register-update-frequency/', views.risk_register_update_frequency, name='risk_register_update_frequency'),
    path('api/risk/recurrence-probability/', views.risk_recurrence_probability, name='risk_recurrence_probability'),
    path('api/risk/tolerance-thresholds/', views.risk_tolerance_thresholds, name='risk_tolerance_thresholds'),
    path('api/risk/appetite/', views.risk_appetite, name='risk_appetite'),
]
