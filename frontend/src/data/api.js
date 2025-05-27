import axios from 'axios';

// Fix the API base URL to match your backend
const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000';
console.log(`Using API URL: ${API_URL}`);

// Create an axios instance with the base URL
const axiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 second timeout (increased for debugging)
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  // Remove withCredentials if you don't need authentication cookies
  // withCredentials: true
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

// Add response interceptor for better error handling
axiosInstance.interceptors.response.use(
  response => {
    console.log(`API Response from ${response.config.url}:`, 
      typeof response.data === 'object' ? JSON.stringify(response.data).substring(0, 500) : response.data
    );
    return response;
  },
  error => {
    console.error(`API Error from ${error.config?.url || 'unknown endpoint'}:`, 
      error.response?.data ? JSON.stringify(error.response.data) : error.message
    );
    console.error(`Status: ${error.response?.status}, Status Text: ${error.response?.statusText}`);
    if (error.response?.data?.details) {
      console.error('Error details:', error.response.data.details);
    }
    
    // Log the full error for debugging
    if (error.response?.status === 500) {
      console.error('Internal Server Error - Check Django server logs');
    }
    
    return Promise.reject(error);
  }
);

// Compliance Service
export const complianceService = {
  // Framework endpoints
  getFrameworks: () => axiosInstance.get('/api/frameworks/'),
  
  // Policy endpoints
  getPolicies: (frameworkId) => axiosInstance.get(`/api/frameworks/${frameworkId}/get-policies/`),
  
  // SubPolicy endpoints
  getSubPolicies: (policyId) => axiosInstance.get(`/api/policies/${policyId}/get-subpolicies/`),
  
  // User endpoints
  getUsers: () => axiosInstance.get('/api/users/'),
  
  // Compliance endpoints
  createCompliance: (data) => axiosInstance.post('/compliance/create/', data),
  editCompliance: (complianceId, data) => axiosInstance.put(`/compliance/${complianceId}/edit/`, data),
  cloneCompliance: (complianceId) => axiosInstance.post(`/compliance/${complianceId}/clone/`),
  getComplianceDashboard: () => axiosInstance.get('/compliance/dashboard/')
};

// API functions
export const api = {
  // Framework endpoints - updated to use the correct backend paths
  getFrameworks: () => axiosInstance.get('/api/frameworks/'),
  getFrameworkDetails: (frameworkId) => axiosInstance.get(`/api/frameworks/${frameworkId}/`),
  getFrameworkDetailsForTree: (frameworkId) => axiosInstance.get(`/api/frameworks/${frameworkId}/tree/`),
  
  // Policy endpoints - updated to use the correct backend paths  
  getPolicies: () => axiosInstance.get('/api/policies/'),
  getPoliciesByFramework: (frameworkId) => axiosInstance.get(`/api/frameworks/${frameworkId}/policies/`),
  
  // User endpoints
  getUsers: () => axiosInstance.get('/api/users/'),
  
  // Incident endpoints
  getIncidents: () => axiosInstance.get('/api/incidents/'),
  
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
  getAuditStatus: (auditId) => axiosInstance.get(`/audits/${auditId}/status/`),
  getAuditCompliances: (auditId) => axiosInstance.get(`/audits/${auditId}/compliances/`),
  addComplianceToAudit: (auditId, data) => axiosInstance.post(`/audits/${auditId}/add-compliance/`, data),
  updateComplianceStatus: (complianceId, data) => axiosInstance.post(`/audit-findings/${complianceId}/`, data),
  submitAuditFindings: (auditId) => axiosInstance.post(`/audits/${auditId}/submit/`),
  loadLatestReviewVersion: (auditId) => axiosInstance.get(`/audits/${auditId}/load-latest-review-version/`),
  loadAuditContinuingData: (auditId) => axiosInstance.get(`/audits/${auditId}/load-continuing-data/`),
  
  // Audit Version endpoints
  getAuditVersions: (auditId) => axiosInstance.get(`/audits/${auditId}/versions/`),
  getAuditVersionDetails: (auditId, version) => axiosInstance.get(`/audits/${auditId}/versions/${version}/`),
  checkAuditVersion: (auditId) => axiosInstance.get(`/audits/${auditId}/check-version/`),
  
  // Upload evidence - requires special content-type handling
  uploadEvidence: (complianceId, formData) => {
    const customConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    };
    return axiosInstance.post(`/audit-findings/${complianceId}/evidence/`, formData, customConfig);
  }
};

export default api; 