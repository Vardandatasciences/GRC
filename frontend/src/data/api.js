import axios from 'axios';

// API base URL - Use environment variable or default to localhost:8000/api
const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api';
console.log(`Using API URL: ${API_URL}`);

// Create an axios instance with the base URL
const axiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 second timeout (increased for debugging)
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  // Enable withCredentials to make sure cookies are sent with requests
  withCredentials: true
});

// Add request interceptor for logging
axiosInstance.interceptors.request.use(
  config => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.baseURL}${config.url}`, 
      config.data ? JSON.stringify(config.data) : '{}'
    );
    return config;
  },
  error => {
    console.error("Request error:", error);
    return Promise.reject(error);
  }
);

// Add response interceptor for logging
axiosInstance.interceptors.response.use(
  response => {
    // Log full response data for debugging
    console.log(`API Response from ${response.config.url}:`);
    if (typeof response.data === 'object') {
      console.log('Full Response Data:', response.data);
      // Also log the stringified version for easy copying
      console.log('JSON String:', JSON.stringify(response.data));
    } else {
      console.log(response.data);
    }
    return response;
  },
  error => {
    console.error(`API Error from ${error.config?.url || 'unknown endpoint'}:`, 
      error.response?.data ? JSON.stringify(error.response.data) : error.message
    );
    console.error(`Status: ${error.response?.status}, Status Text: ${error.response?.statusText}`);
    if (error.response?.data?.details) {
      console.error('Validation errors:', error.response.data.details);
    }
    return Promise.reject(error);
  }
);

// API functions
export const api = {
  // Framework endpoints
  getFrameworks: () => axiosInstance.get('/frameworks/'),
  
  // Policy endpoints
  getPoliciesByFramework: (frameworkId) => axiosInstance.get(`/frameworks/${frameworkId}/policies/`),
  
  // User endpoints
  getUsers: () => axiosInstance.get('/users/'),
  
  // Assignment endpoints
  getAssignData: () => axiosInstance.get('/assign-data/'),
  allocatePolicy: (data) => axiosInstance.post('/allocate-policy/', data),
  
  // Audit endpoints
  getAllAudits: () => axiosInstance.get('/audits/'),
  getMyAudits: () => axiosInstance.get('/my-audits/'),
  getMyReviews: () => axiosInstance.get('/my-reviews/'),
  getAuditDetails: (auditId) => axiosInstance.get(`/audits/${auditId}/`),
  updateAuditStatus: (auditId, statusData) => axiosInstance.post(`/audits/${auditId}/status/`, statusData),
  updateAuditReviewStatus: (auditId, data) => axiosInstance.post(`/audits/${auditId}/review-status/`, data),
  saveReviewProgress: (auditId, data) => axiosInstance.post(`/audits/${auditId}/save-review/`, data),
  getAuditStatus: (auditId) => axiosInstance.get(`/audits/${auditId}/get-status/`),
  getAuditCompliances: (auditId) => axiosInstance.get(`/audits/${auditId}/compliances/`),
  addComplianceToAudit: (auditId, data) => axiosInstance.post(`/audits/${auditId}/add-compliance/`, data),
  updateComplianceStatus: (complianceId, data) => axiosInstance.post(`/audit-findings/${complianceId}/`, data),
  submitAuditFindings: (auditId) => axiosInstance.post(`/audits/${auditId}/submit/`),
  loadLatestReviewVersion: (auditId) => axiosInstance.get(`/audits/${auditId}/load-latest-review-version/`),
  loadAuditContinuingData: (auditId) => axiosInstance.get(`/audits/${auditId}/load-continuing-data/`),
  saveAuditVersion: (auditId, auditData) => axiosInstance.post(`/audits/${auditId}/save-audit-version/`, { audit_data: auditData }),
  
  // Audit Report endpoints
  checkAuditReports: (params) => axiosInstance.get('/audit-reports/check/', { params }),
  getReportDetails: (reportIds) => axiosInstance.get('/audit-reports/details/', { params: { report_ids: reportIds } }),
  
  // Audit Version endpoints
  getAuditVersions: (auditId) => axiosInstance.get(`/audits/${auditId}/versions/`),
  getAuditVersionDetails: (auditId, version) => {
    return axiosInstance.get(`/audits/${auditId}/versions/${version}/`)
      .then(response => {
        // Print detailed information about the version data
        console.log(`Version ${version} loaded successfully for audit ${auditId}`);
        
        // Log the structure of findings
        if (response.data.findings) {
          console.log(`Found ${response.data.findings.length} findings in version ${version}`);
          
          // Print sample finding structure (first finding)
          if (response.data.findings.length > 0) {
            const sampleFinding = response.data.findings[0];
            console.log('Sample finding structure:', sampleFinding);
            
            // Print all review_status and review_comments values for debugging
            const reviewStatuses = {};
            response.data.findings.forEach(finding => {
              if (finding.review_status || finding.review_comments) {
                reviewStatuses[finding.compliance_id] = {
                  review_status: finding.review_status,
                  review_comments: finding.review_comments ? 
                    (finding.review_comments.length > 50 ? 
                      finding.review_comments.substring(0, 50) + '...' : 
                      finding.review_comments) : null
                };
              }
            });
            console.log('Review statuses in findings:', reviewStatuses);
          }
        }
        
        // Log the version metadata
        if (response.data.version_info) {
          console.log('Version info:', response.data.version_info);
          
          if (response.data.version_info.metadata) {
            console.log('Version metadata:', response.data.version_info.metadata);
          }
        }
        
        return response;
      })
      .catch(error => {
        console.error(`Error retrieving version details for audit ${auditId}, version ${version}:`, error);
        // Throw a more informative error that includes version info
        const errorMsg = error.response?.data?.error || `Failed to load version ${version}`;
        throw new Error(`Version error (${version}): ${errorMsg}`);
      });
  },
  checkAuditVersion: (auditId) => {
    return axiosInstance.get(`/audits/${auditId}/check-version/`)
      .then(response => {
        // Enhanced logging for version check results
        console.log(`===== VERSION CHECK DETAILS for Audit ${auditId} =====`);
        
        if (response.data.auditor_versions_found > 0) {
          console.log(`Found ${response.data.auditor_versions_found} auditor versions:`);
          response.data.auditor_versions.forEach((v, i) => {
            console.log(`  ${i+1}. ${v.Version} created on ${v.Date}`);
          });
        } else {
          console.log('No auditor versions found.');
        }
        
        if (response.data.reviewer_versions_found > 0) {
          console.log(`Found ${response.data.reviewer_versions_found} reviewer versions:`);
          response.data.reviewer_versions.forEach((v, i) => {
            console.log(`  ${i+1}. ${v.Version} created on ${v.Date} - Status: ${v.ApprovedRejected || 'None'}`);
          });
        } else {
          console.log('No reviewer versions found.');
        }
        
        if (response.data.recommended_version) {
          console.log(`Recommended version: ${response.data.recommended_version}`);
        }
        
        console.log('===== END VERSION CHECK DETAILS =====');
        return response;
      });
  },
  
  // Upload evidence - requires special content-type handling
  uploadEvidence: (complianceId, formData) => {
    const customConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    };
    return axiosInstance.post(`/audit-findings/${complianceId}/evidence/`, formData, customConfig);
  },
  
  // Debug helpers
  debugPrintAuditData: (auditId) => {
    console.log(`===== DEBUG PRINT AUDIT DATA FOR AUDIT ID: ${auditId} =====`);
    return Promise.all([
      axiosInstance.get(`/audits/${auditId}/`),
      axiosInstance.get(`/audits/${auditId}/check-version/`),
      axiosInstance.get(`/audits/${auditId}/compliances/`)
    ]).then(([auditDetails, versionCheck, compliances]) => {
      console.log('1. AUDIT DETAILS:', auditDetails.data);
      console.log('2. VERSION INFO:', versionCheck.data);
      console.log('3. COMPLIANCES STRUCTURE:');
      
      // Print policies and subpolicies structure
      if (compliances.data && compliances.data.policies) {
        console.log(`Found ${compliances.data.policies.length} policies`);
        
        compliances.data.policies.forEach(policy => {
          console.log(`- Policy: ${policy.policy_name} (ID: ${policy.policy_id})`);
          
          policy.subpolicies.forEach(subpolicy => {
            console.log(`  - Subpolicy: ${subpolicy.subpolicy_name} (ID: ${subpolicy.subpolicy_id})`);
            console.log(`    - Compliances: ${subpolicy.compliances.length} items`);
            
            // Print first compliance as sample
            if (subpolicy.compliances.length > 0) {
              const sample = subpolicy.compliances[0];
              console.log('    - Sample compliance:', {
                id: sample.compliance_id,
                description: sample.description,
                status: sample.compliance_status,
                criticality: sample.criticality,
                review_status: sample.review_status || 'None',
                review_comments: sample.review_comments || 'None'
              });
            }
          });
        });
      }
      
      // If version data is available, try to load the latest version
      if (versionCheck.data.auditor_versions_found > 0) {
        const latestVersion = versionCheck.data.auditor_versions[0].Version;
        console.log(`Loading latest auditor version: ${latestVersion}`);
        
        return axiosInstance.get(`/audits/${auditId}/versions/${latestVersion}/`)
          .then(versionData => {
            console.log('4. LATEST VERSION DATA:', versionData.data);
            return {
              auditDetails: auditDetails.data,
              versionCheck: versionCheck.data,
              compliances: compliances.data,
              versionData: versionData.data
            };
          })
          .catch(error => {
            console.error('Error loading version data:', error);
            return {
              auditDetails: auditDetails.data,
              versionCheck: versionCheck.data,
              compliances: compliances.data,
              versionData: null,
              versionError: error.message
            };
          });
      }
      
      console.log('===== END DEBUG PRINT =====');
      return {
        auditDetails: auditDetails.data,
        versionCheck: versionCheck.data,
        compliances: compliances.data
      };
    });
  },
  
  // Download audit report
  downloadAuditReport: (auditId) => axiosInstance.get(`/generate-audit-report/${auditId}/`, {
    responseType: 'blob',
    headers: {
      'Accept': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
  }),
};

export default api; 