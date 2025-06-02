from django.urls import path
from . import views



from .routes.policy import (
    framework_list, framework_detail, policy_detail, policy_list,
    add_policy_to_framework, add_subpolicy_to_policy, 
    subpolicy_detail, copy_framework, copy_policy,
    create_framework_version, create_policy_version,
    export_policies_to_excel,
    update_policy_approval,
    submit_policy_review,
    # list_rejected_policy_approvals_for_user,
    resubmit_policy_approval,
    list_users,
    get_framework_explorer_data,
    get_framework_policies,
    toggle_framework_status,
    toggle_policy_status,
    get_framework_details,
    get_policy_details,
    all_policies_get_frameworks,
    all_policies_get_framework_versions,
    all_policies_get_framework_version_policies,
    all_policies_get_policies,
    all_policies_get_policy_versions,
    all_policies_get_subpolicies,
    all_policies_get_policy_version_subpolicies,
    all_policies_get_subpolicy_details,
    get_policy_dashboard_summary,
    get_policy_status_distribution,
    get_reviewer_workload,
    get_recent_policy_activity,
    get_avg_policy_approval_time,
    get_policy_analytics,
    get_policy_kpis,
    acknowledge_policy,
    get_policies_by_framework,
    get_subpolicies_by_policy,  
    get_latest_policy_approval,
    get_latest_policy_approval_by_role,
    get_latest_reviewer_version,
    submit_subpolicy_review,
    resubmit_subpolicy,
    get_policy_version,
    get_subpolicy_version,
    submit_policy_approval_review,
    get_policy_version_history,
    list_policy_approvals_for_reviewer,
    list_rejected_policy_approvals_for_user
)
from .routes.frameworks import (
    create_framework_approval,
    get_framework_approvals,
    update_framework_approval,
    submit_framework_review,
    get_latest_framework_approval,
    resubmit_framework
)


urlpatterns = [
    # Export endpoints - moved to top level without grc prefix
    path('api/export/', views.export_data, name='export-data'),
    path('api/export/compliance/', views.export_compliance_data, name='export-compliance-data'),
    
    # Auth endpoints
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('test-connection/', views.test_connection, name='test-connection'),
    
    # Framework and Policy endpoints
    # path('api/frameworks/', views.get_frameworks, name='get-frameworks'),
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

    path('api/frameworks/', framework_list, name='framework-list'),
    path('api/frameworks/<int:pk>/', framework_detail, name='framework-detail'),
    path('api/frameworks/<int:pk>/copy/', copy_framework, name='copy-framework'),
    path('api/frameworks/<int:pk>/create-version/', create_framework_version, name='create-framework-version'),
    path('api/frameworks/<int:framework_id>/export/', export_policies_to_excel, name='export-framework-policies'),
    path('api/policies/', policy_list, name='policy-list'),
    path('api/policies/<int:pk>/', policy_detail, name='policy-detail'),
    path('api/policies/<int:pk>/copy/', copy_policy, name='copy-policy'),
    path('api/policies/<int:pk>/create-version/', create_policy_version, name='create-policy-version'),
    path('api/subpolicies/<int:pk>/', subpolicy_detail, name='subpolicy-detail'),
    path('api/frameworks/<int:framework_id>/policies/', add_policy_to_framework, name='add-policy-to-framework'),
    path('policies/<int:policy_id>/subpolicies/', add_subpolicy_to_policy, name='add-subpolicy-to-policy'),
    path('api/subpolicies/<int:pk>/review/', submit_subpolicy_review, name='submit-subpolicy-review'),
    path('api/subpolicies/<int:pk>/resubmit/', resubmit_subpolicy, name='resubmit-subpolicy'),
    path('api/policy-approvals/reviewer/', list_policy_approvals_for_reviewer, name='policy-approvals-for-reviewer'),
    path('api/policy-approvals/<int:approval_id>/', update_policy_approval, name='update_policy_approval'),
    path('api/policy-approvals/<int:approval_id>/review/', submit_policy_review, name='submit_policy_review'),
    path('api/policy-approvals/rejected/<int:user_id>/', list_rejected_policy_approvals_for_user),
    path('api/policy-approvals/resubmit/<int:approval_id>/', resubmit_policy_approval),
    path('api/users/', list_users, name='list-users'),
    path('api/framework-explorer/', get_framework_explorer_data, name='framework-explorer'),
    path('api/frameworks/<int:framework_id>/policies-list/', get_framework_policies, name='framework-policies'),
    path('api/frameworks/<int:framework_id>/toggle-status/', toggle_framework_status, name='toggle-framework-status'),
    path('api/policies/<int:policy_id>/toggle-status/', toggle_policy_status, name='toggle-policy-status'),
    path('api/frameworks/<int:framework_id>/details/', get_framework_details, name='framework-details'),
    path('api/policies/<int:policy_id>/details/', get_policy_details, name='policy-details'),
    path('api/all-policies/frameworks/', all_policies_get_frameworks, name='all-policies-frameworks'),
    path('api/all-policies/frameworks/<int:framework_id>/versions/', all_policies_get_framework_versions, name='all-policies-framework-versions'),
    path('api/all-policies/framework-versions/<int:version_id>/policies/', all_policies_get_framework_version_policies, name='all-policies-framework-version-policies'),
    path('api/all-policies/policies/', all_policies_get_policies, name='all-policies-policies'),
    path('api/all-policies/policies/<int:policy_id>/versions/', all_policies_get_policy_versions, name='all-policies-policy-versions'),
    path('api/all-policies/subpolicies/', all_policies_get_subpolicies, name='all-policies-subpolicies'),
    path('api/all-policies/policy-versions/<int:version_id>/subpolicies/', all_policies_get_policy_version_subpolicies, name='all-policies-policy-version-subpolicies'),
    path('api/all-policies/subpolicies/<int:subpolicy_id>/', all_policies_get_subpolicy_details, name='all-policies-subpolicy-details'),
    path('api/policy-dashboard/', get_policy_dashboard_summary),
    path('api/policy-status-distribution/', get_policy_status_distribution),
    path('api/reviewer-workload/', get_reviewer_workload),
    path('api/recent-policy-activity/', get_recent_policy_activity),
    path('api/avg-policy-approval-time/', get_avg_policy_approval_time),
    path('api/policy-analytics/', get_policy_analytics, name='policy-analytics'),
    path('policy-analytics/', get_policy_analytics),
    path('api/policy-kpis/', get_policy_kpis),    
    path('api/acknowledge-policy/<int:policy_id>/', acknowledge_policy, name='acknowledge-policy'),      
    path('api/frameworks/<int:framework_id>/get-policies/', get_policies_by_framework, name='get-policies-by-framework'),
    path('api/policies/<int:policy_id>/get-subpolicies/', get_subpolicies_by_policy, name='get-subpolicies-by-policy'),
    path('api/policies/<int:policy_id>/version/', get_policy_version, name='get-policy-version'),
    path('api/subpolicies/<int:subpolicy_id>/version/', get_subpolicy_version, name='get-subpolicy-version'),
    path('api/policy-approvals/latest/<int:policy_id>/', get_latest_policy_approval, name='get-latest-policy-approval'),
    path('api/policy-approvals/latest-by-role/<int:policy_id>/<str:role>/', get_latest_policy_approval_by_role, name='get-latest-policy-approval-by-role'),
    path('api/policies/<int:policy_id>/reviewer-version/', get_latest_reviewer_version, name='get-policy-reviewer-version'),
    path('api/policies/<int:policy_id>/submit-review/', submit_policy_approval_review, name='submit-policy-approval-review'),
    path('api/policies/<int:policy_id>/version-history/', get_policy_version_history, name='get-policy-version-history'),
    path('api/frameworks/<int:framework_id>/create-approval/', create_framework_approval, name='create-framework-approval'),
    path('api/framework-approvals/', get_framework_approvals, name='get-framework-approvals'),
    path('api/framework-approvals/<int:framework_id>/', get_framework_approvals, name='get-framework-approvals-by-id'),
    path('api/framework-approvals/<int:approval_id>/update/', update_framework_approval, name='update-framework-approval'),
    path('api/frameworks/<int:framework_id>/submit-review/', submit_framework_review, name='submit-framework-review'),
    path('api/framework-approvals/latest/<int:framework_id>/', get_latest_framework_approval, name='get-latest-framework-approval'),
    path('api/frameworks/<int:framework_id>/resubmit/', resubmit_framework, name='resubmit-framework')
]
