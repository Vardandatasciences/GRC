from django.urls import path
from . import views
from . import report_views
from . import audit_report_views
from . import kpi_functions
from . import audit_report_handlers
from .views import (
    add_compliance_to_audit, get_assign_data, load_review_data, save_review_progress, load_latest_review_version,
    load_continuing_data, load_audit_continuing_data, save_audit_json_version
)

urlpatterns = [
    # Framework endpoints
    path('frameworks/', views.get_frameworks, name='get_frameworks'),
    path('frameworks/<int:framework_id>/policies/', views.get_policies_by_framework, name='get_policies_by_framework'),
    
    # User endpoints
    path('users/', views.get_users, name='get_users'),

    # Data endpoints for assignment
    path('assign-data/', get_assign_data, name='get_assign_data'),
    
    # Policy allocation endpoint
    path('allocate-policy/', views.allocate_policy, name='allocate_policy'),

    # Audit endpoints
    path('audits/', views.get_all_audits, name='get_all_audits'),
    path('my-audits/', views.get_my_audits, name='get_my_audits'),
    path('my-reviews/', views.get_my_reviews, name='get_my_reviews'),
    path('audits/<int:audit_id>/', views.get_audit_details, name='get_audit_details'),
    path('audits/<int:audit_id>/status/', views.update_audit_status, name='update_audit_status'),
    path('audits/<int:audit_id>/review-status/', views.update_review_status, name='update_review_status'),
    path('audits/<int:audit_id>/get-status/', views.get_audit_status, name='get_audit_status'),
    path('audits/<int:audit_id>/compliances/', views.get_audit_compliances, name='get_audit_compliances'),
    path('audits/<int:audit_id>/submit/', views.submit_audit_findings, name='submit_audit_findings'),
    
    # Audit Version endpoints
    path('audits/<int:audit_id>/versions/', views.get_audit_versions, name='get_audit_versions'),
    path('audits/<int:audit_id>/versions/<str:version>/', views.get_audit_version_details, name='get_audit_version_details'),
    path('audits/<int:audit_id>/check-version/', views.check_audit_version, name='check_audit_version'),
    
    # New endpoint for saving audit JSON to version table
    path('audits/<int:audit_id>/save-audit-version/', save_audit_json_version, name='save_audit_json_version'),
    
    # Audit Finding endpoints
    path('audit-findings/<int:compliance_id>/', views.update_audit_finding, name='update_audit_finding'),
    path('audit-findings/<int:compliance_id>/upload-evidence/', views.upload_evidence, name='upload_evidence'),
    
    # Compliance endpoints
    path('compliance/', views.get_all_compliance, name='get_all_compliance'),
    path('subpolicies/<int:subpolicy_id>/compliance/', views.get_compliance_by_subpolicy, name='get_compliance_by_subpolicy'),
    
    # New endpoint for adding compliance items in audit context
    path('audits/<int:audit_id>/add-compliance/', add_compliance_to_audit, name='add_compliance_to_audit'),
    
    # Migration helper endpoints
    path('add-majorminor-column/', views.add_majorminor_column, name='add_majorminor_column'),
    
    # Fixed subpolicy version field
    path('fix-subpolicy-version/', views.fix_subpolicy_version_field, name='fix_subpolicy_version_field'),
    path('fix-audit-table/', views.fix_audit_table, name='fix_audit_table'),

    # Endpoint for saving review progress
    path('audits/<int:audit_id>/save-review/', save_review_progress, name='save_review_progress'),

    # New endpoint for loading review data
    path('audits/<int:audit_id>/load-review/', load_review_data, name='load_review_data'),
    
    # Endpoint for loading latest review version data regardless of prefix (A or R)
    path('audits/<int:audit_id>/load-latest-review-version/', load_latest_review_version, name='load_latest_review_version'),
    
    # Endpoint for loading continuing data for auditors after reviewer feedback
    path('audits/<int:audit_id>/load-continuing-data/', load_continuing_data, name='load_continuing_data'),
    
    # Alias for load-continuing-data for consistency with frontend API call
    path('audits/<int:audit_id>/load-audit-continuing-data/', load_audit_continuing_data, name='load_audit_continuing_data'),

    # Add this to urlpatterns
    path('audits/<int:audit_id>/debug-status-transition/', views.debug_audit_status_transition, name='debug_audit_status_transition'),

    # New debug endpoint
    path('debug/audit-version-schema/', views.debug_audit_version_schema, name='debug_audit_version_schema'),

    # New debug endpoint for checking audit versions
    path('debug/audit-versions/<int:audit_id>/', views.debug_audit_versions, name='debug_audit_versions'),

    # New endpoint for generating and downloading audit report - using the simplified version
    path('generate-audit-report/<int:audit_id>/', report_views.generate_audit_report, name='generate-audit-report'),
    
    # Audit Reports endpoints
    path('audit-reports/', audit_report_views.get_audit_reports, name='get_audit_reports'),
    path('audit-reports/<int:audit_id>/versions/', audit_report_views.get_audit_report_versions, name='get_audit_report_versions'),
    path('audit-reports/<int:audit_id>/versions/<str:version>/delete/', audit_report_views.delete_audit_report_version, name='delete_audit_report_version'),
    path('audit-reports/<int:audit_id>/versions/<str:version>/s3-link/', audit_report_views.get_audit_report_s3_link, name='get_audit_report_s3_link'),
    path('audit-reports/check/', audit_report_handlers.check_audit_reports, name='check_audit_reports'),
    path('audit-reports/details/', audit_report_handlers.get_report_details, name='get_report_details'),
    
    # KPI endpoints
    path('kpi/audit-completion/', kpi_functions.get_audit_completion_kpi, name='get_audit_completion_kpi'),
    path('kpi/audit-completion-trend/', kpi_functions.get_audit_completion_trend, name='get_audit_completion_trend'),
]