import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const complianceService = {
  // Framework endpoints
  getFrameworks: () => api.get('/frameworks/'),
  
  // Policy endpoints
  getPolicies: (frameworkId) => api.get(`/frameworks/${frameworkId}/policies/`),
  
  // SubPolicy endpoints
  getSubPolicies: (policyId) => api.get(`/policies/${policyId}/subpolicies/`),
  
  // Compliance endpoints
  createCompliance: (data) => api.post('/compliance/create/', data),
  editCompliance: (complianceId, data) => api.put(`/compliance/${complianceId}/edit/`, data),
  cloneCompliance: (complianceId, data) => api.post(`/compliance/${complianceId}/clone/`, data),
  getComplianceDashboard: (filters) => api.get('/compliance/user-dashboard/', { params: filters }),
  getComplianceAnalytics: (data) => api.post('/compliance/kpi-dashboard/analytics/', data),
  getCompliancesBySubPolicy: (subPolicyId) => api.get(`/subpolicies/${subPolicyId}/compliances/`),
  
  // KPI endpoints
  getMaturityLevelKPI: () => api.get('/compliance/kpi-dashboard/analytics/maturity-level/'),
  getNonComplianceCount: () => api.get('/compliance/kpi-dashboard/analytics/non-compliance-count/'),
  getMitigatedRisksCount: () => api.get('/compliance/kpi-dashboard/analytics/mitigated-risks-count/'),
  getAutomatedControlsCount: () => api.get('/compliance/kpi-dashboard/analytics/automated-controls-count/'),
  getNonComplianceRepetitions: () => api.get('/compliance/kpi-dashboard/analytics/non-compliance-repetitions/'),
  getComplianceKPI: () => api.get('/compliance/kpi-dashboard/'),
  
  // Compliance approval endpoints
  getPolicyApprovals: (params) => api.get('/policy-approvals/reviewer/', { params }),
  getRejectedApprovals: (reviewerId) => api.get(`/policy-approvals/rejected/${reviewerId}/`),
  submitComplianceReview: (approvalId, data) => api.put(`/compliance-approvals/${approvalId}/review/`, data),
  resubmitComplianceApproval: (approvalId, data) => api.put(`/compliance-approvals/resubmit/${approvalId}/`, data),
  
  // New endpoint
  getUsers: () => api.get('/users/'),
};

export default api; 