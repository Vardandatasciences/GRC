from django.urls import path
from . import views

urlpatterns = [
    # Export endpoints - moved to top level without grc prefix
    path('api/export/', views.export_data, name='export-data'),
    path('api/export/compliance/', views.export_compliance_data, name='export-compliance-data'),
    
    # Auth endpoints
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('test-connection/', views.test_connection, name='test-connection'),
    
    # Framework and Policy endpoints
    path('frameworks/', views.get_frameworks, name='get-frameworks'),
    path('frameworks/<int:framework_id>/policies/', views.get_policies, name='get-policies'),
    path('policies/<int:policy_id>/subpolicies/', views.get_subpolicies, name='get-subpolicies'),
    
    # Compliance endpoints
    path('compliance/create/', views.create_compliance, name='create-compliance'),
    path('compliance/<int:compliance_id>/edit/', views.edit_compliance, name='edit-compliance'),
    path('compliance/<int:compliance_id>/clone/', views.clone_compliance, name='clone-compliance'),
    path('compliance/user-dashboard/', views.get_compliance_dashboard, name='compliance-dashboard'),
    path('compliance/kpi-dashboard/analytics/', views.get_compliance_analytics, name='compliance-analytics'),
    path('subpolicies/<int:subpolicy_id>/compliances/', views.get_compliances_by_subpolicy, name='get-compliances-by-subpolicy'),
    
    # All Policies endpoints
    path('all-policies/frameworks/', views.all_policies_get_frameworks, name='all-policies-get-frameworks'),
    path('all-policies/policies/', views.all_policies_get_policies, name='all-policies-get-policies'),
    path('all-policies/subpolicies/', views.all_policies_get_subpolicies, name='all-policies-get-subpolicies'),
    path('all-policies/subpolicy/<int:subpolicy_id>/compliances/', views.all_policies_get_subpolicy_compliances, name='all-policies-get-subpolicy-compliances'),
    path('all-policies/compliance/<int:compliance_id>/versions/', views.all_policies_get_compliance_versions, name='all-policies-get-compliance-versions'),
    
    # Compliance approval endpoints
    path('compliance-approvals/<int:approval_id>/review/', views.submit_compliance_review, name='submit_compliance_review'),
    path('compliance-approvals/resubmit/<int:approval_id>/', views.resubmit_compliance_approval, name='resubmit_compliance_approval'),
    path('compliance/versioning/', views.get_compliance_versioning, name='get-compliance-versioning'),
    path('policy-approvals/reviewer/', views.get_policy_approvals_by_reviewer, name='get-policy-approvals-by-reviewer'),
    path('policy-approvals/rejected/<int:reviewer_id>/', views.get_rejected_approvals, name='get-rejected-approvals'),
    
    # User endpoints
    path('users/', views.get_all_users, name='get-all-users'),

    path('api/all-policies/frameworks/', views.all_policies_get_frameworks, name='all-policies-frameworks'),
    path('api/all-policies/frameworks/<int:framework_id>/versions/', views.all_policies_get_framework_versions, name='all-policies-framework-versions'),
    path('api/all-policies/framework-versions/<int:version_id>/policies/', views.all_policies_get_framework_version_policies, name='all-policies-framework-version-policies'),
    path('api/all-policies/policies/', views.all_policies_get_policies, name='all-policies-policies'),
    path('api/all-policies/policies/<int:policy_id>/versions/', views.all_policies_get_policy_versions, name='all-policies-policy-versions'),
    path('api/all-policies/subpolicies/', views.all_policies_get_subpolicies, name='all-policies-subpolicies'),
    path('api/all-policies/policy-versions/<int:version_id>/subpolicies/', views.all_policies_get_policy_version_subpolicies, name='all-policies-policy-version-subpolicies'),
    path('api/all-policies/subpolicies/<int:subpolicy_id>/', views.all_policies_get_subpolicy_details, name='all-policies-subpolicy-details'),
    path('api/all-policies/subpolicies/<int:subpolicy_id>/compliances/', views.all_policies_get_subpolicy_compliances, name='all-policies-subpolicy-compliances'),
    path('api/all-policies/compliances/<int:compliance_id>/versions/', views.all_policies_get_compliance_versions, name='all-policies-compliance-versions'),
        
    # Version control endpoints
    path('compliance/<int:compliance_id>/toggle-version/', views.toggle_compliance_version, name='toggle-compliance-version'),

    # Performance Analysis endpoints
    path('compliance/kpi-dashboard/', views.get_compliance_kpi, name='get-compliance-kpi-dashboard'),
    path('compliance/user-dashboard/', views.get_compliance_dashboard, name='get-compliance-user-dashboard'),
    path('compliance/kpi-dashboard/analytics/', views.get_compliance_analytics, name='get-compliance-kpi-analytics'),
    path('compliance/kpi-dashboard/analytics/maturity-level/', views.get_maturity_level_kpi, name='get-maturity-level-kpi'),
    path('compliance/kpi-dashboard/analytics/non-compliance-count/', views.get_non_compliance_count, name='get-non-compliance-count'),
    path('compliance/kpi-dashboard/analytics/mitigated-risks-count/', views.get_mitigated_risks_count, name='get-mitigated-risks-count'),
    path('compliance/kpi-dashboard/analytics/automated-controls-count/', views.get_automated_controls_count, name='get-automated-controls-count'),
    path('compliance/kpi-dashboard/analytics/non-compliance-repetitions/', views.get_non_compliance_repetitions, name='get-non-compliance-repetitions'),

    # Export endpoints
    path('grc/api/export/', views.export_data, name='export-data'),
    path('grc/api/export/compliance/', views.export_compliance_data, name='export-compliance-data'),
    path('export/download/', views.download_export, name='download-export'),  # New endpoint for downloads
]
