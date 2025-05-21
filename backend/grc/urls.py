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
    path('api/risk/metrics', views.risk_metrics, name='risk_metrics'),
]
