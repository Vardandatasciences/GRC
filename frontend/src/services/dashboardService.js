import axios from 'axios';

const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:3000/api';

const dashboardService = {
  // Dashboard summary data
  getDashboardSummary() {
    return axios.get(`${API_URL}/policy/dashboard/summary`);
  },

  // Policy status distribution
  getPolicyStatusDistribution() {
    return axios.get(`${API_URL}/policy/dashboard/status-distribution`);
  },

  // Recent policy activity
  getRecentPolicyActivity() {
    return axios.get(`${API_URL}/policy/dashboard/recent-activity`);
  },

  // Average approval time
  getAvgApprovalTime() {
    return axios.get(`${API_URL}/policy/dashboard/avg-approval-time`);
  },

  // Reviewer workload
  getReviewerWorkload() {
    return axios.get(`${API_URL}/policy/dashboard/reviewer-workload`);
  },

  // Policy analytics with dynamic parameters
  getPolicyAnalytics(xAxis, yAxis) {
    return axios.get(`${API_URL}/policy/dashboard/analytics`, {
      params: { xAxis, yAxis }
    });
  }
};

export default dashboardService; 