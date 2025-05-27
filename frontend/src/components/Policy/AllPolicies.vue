<template>
  <div class="all-policies-container">
    <!-- Policy Details Modal -->
    <div v-if="selectedPolicy" class="policy-details-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ selectedPolicy.name }}</h2>
          <button class="close-btn" @click="selectedPolicy = null">
            <span class="close-icon">×</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="section">
            <h3>Introduction</h3>
            <p>{{ selectedPolicy.description }}</p>
          </div>
         
          <div class="section">
            <h3>Objectives</h3>
            <ul>
              <li v-for="(objective, index) in selectedPolicy.objectives" :key="index">
                {{ objective }}
              </li>
            </ul>
          </div>
 
          <div class="section">
            <h3>Scope</h3>
            <p>{{ selectedPolicy.scope }}</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="download-btn">
            <i class="fas fa-download"></i> Download
          </button>
        </div>
      </div>
    </div>
 
    <!-- Subpolicy Details Modal -->
    <div v-if="selectedSubpolicy" class="subpolicy-details-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ selectedSubpolicy.name }}</h2>
          <button class="close-btn" @click="selectedSubpolicy = null">
            <span class="close-icon">×</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="section">
            <h3>Description</h3>
            <p>{{ selectedSubpolicy.description }}</p>
          </div>
         
          <div class="section">
            <h3>Control</h3>
            <p>{{ selectedSubpolicy.control }}</p>
          </div>
        </div>
      </div>
    </div>
 
    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>Loading...</p>
    </div>
 
    <!-- Error Message -->
    <div v-if="error" class="error-message">
      {{ error }}
      <button class="close-btn" @click="error = null">✕</button>
    </div>
 
    <!-- Summary Cards Row -->
    <div class="summary-cards-row">
      <div class="summary-card"
           @click="handleSummaryCardClick('active')"
           :class="{ active: selectedActiveInactive === 'Active' }">
        <div class="summary-count">{{ summaryCounts.active }}</div>
        <div class="summary-label">Active</div>
      </div>
      <div class="summary-card"
           @click="handleSummaryCardClick('inactive')"
           :class="{ active: selectedActiveInactive === 'Inactive' }">
        <div class="summary-count">{{ summaryCounts.inactive }}</div>
        <div class="summary-label">Inactive</div>
      </div>
      <div class="summary-card"
           @click="handleSummaryCardClick('approved')"
           :class="{ active: selectedStatus === 'Approved' }">
        <div class="summary-count">{{ summaryCounts.approved }}</div>
        <div class="summary-label">Approved</div>
      </div>
      <div class="summary-card"
           @click="handleSummaryCardClick('rejected')"
           :class="{ active: selectedStatus === 'Rejected' }">
        <div class="summary-count">{{ summaryCounts.rejected }}</div>
        <div class="summary-label">Rejected</div>
      </div>
      <div class="summary-card"
           @click="handleSummaryCardClick('under-review')"
           :class="{ active: selectedStatus === 'Under Review' }">
        <div class="summary-count">{{ summaryCounts.under_review }}</div>
        <div class="summary-label">Under Review</div>
      </div>
    </div>
 
    <!-- Search and Filters Row -->
    <div class="filters-row">
      <select v-model="selectedFramework" class="filter-dropdown" :disabled="loading">
        <option value="">Sort by Framework</option>
        <option v-for="framework in frameworks" :key="framework.id" :value="framework.id">
          {{ framework.name }} (ID: {{ framework.id }})
        </option>
      </select>
      <select v-model="selectedActiveInactive" class="filter-dropdown" :disabled="loading">
        <option value="">Sort by Active/Inactive</option>
        <option value="Active">Active</option>
        <option value="Inactive">Inactive</option>
      </select>
      <select v-model="selectedStatus" class="filter-dropdown" :disabled="loading">
        <option value="">Sort by Status</option>
        <option value="Approved">Approved</option>
        <option value="Rejected">Rejected</option>
        <option value="Under Review">Under Review</option>
      </select>
      <button class="table-toggle-btn" @click="toggleViewMode" title="Toggle Table/Card View">
        <i class="fas fa-table"></i>
      </button>
    </div>
 
    <!-- Policy Cards Grid -->
    <div v-if="viewMode === 'card'" class="policy-cards-grid">
      <div v-for="policy in filteredPolicies" :key="policy.id" class="policy-card">
        <div class="policy-card-header">
          <div class="policy-icon">P</div>
          <div class="policy-title">{{ policy.name }}</div>
          <div class="policy-framework">{{ policy.framework }}</div>
        </div>
        <div class="policy-status-row">
          <div class="policy-active-status" :class="safeToLowerCase(policy.activeInactive)">
            {{ policy.activeInactive }}
          </div>
          <div class="policy-workflow-status" :class="safeToLowerCase(policy.status)">
          {{ policy.status }}
          </div>
        </div>
        <div class="subpolicies-list">
          <div v-for="sub in policy.subpolicies" :key="sub.id" class="subpolicy-row">
            <div class="subpolicy-info">
            <span class="subpolicy-name">{{ sub.name }}</span>
              <span class="subpolicy-identifier">({{ sub.identifier }})</span>
            </div>
            <span class="subpolicy-status" :class="safeToLowerCase(sub.status)">{{ sub.status }}</span>
          </div>
          <div v-if="policy.subpolicies.length === 0" class="no-subpolicies">
            No subpolicies found
          </div>
        </div>
      </div>
      <div v-if="filteredPolicies.length === 0" class="empty-state">
        <i class="fas fa-file-alt"></i>
        <p>No policies found for the selected filters</p>
      </div>
    </div>
 
    <!-- Policy Table View -->
    <div v-else class="policy-table-container">
      <table class="policy-table">
        <thead>
          <tr>
            <th><input type="checkbox" disabled /></th>
            <th>Name of the Policy</th>
            <th>Identifier</th>
            <th>Department</th>
            <th>Applicability</th>
            <th>Created By</th>
            <th>Reviewer</th>
            <th>Start Date</th>
            <th>End Date</th>
            <th>Active/Inactive</th>
            <th>Status</th>
            <th>Sub Policies</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="policy in filteredPolicies" :key="policy.id">
            <tr :class="{ 'has-subpolicies': policy.subpolicies && policy.subpolicies.length > 0 }">
              <td><input type="checkbox" /></td>
              <td :title="policy.name" @click="showPolicyDetails(policy)" style="cursor: pointer">{{ policy.name }}</td>
              <td :title="policy.identifier">{{ policy.identifier }}</td>
              <td :title="policy.department">{{ policy.department }}</td>
              <td :title="policy.applicability">{{ policy.applicability }}</td>
              <td :title="policy.createdBy">{{ policy.createdBy }}</td>
              <td :title="policy.reviewer">{{ policy.reviewer }}</td>
              <td :title="formatDate(policy.startDate)">{{ formatDate(policy.startDate) }}</td>
              <td :title="formatDate(policy.endDate)">{{ formatDate(policy.endDate) }}</td>
              <td>
                <span class="status-badge" :class="safeToLowerCase(policy.activeInactive)">
                  {{ policy.activeInactive }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="safeToLowerCase(policy.status)">
                  {{ policy.status }}
                </span>
              </td>
              <td>
                <button class="expand-btn" @click.stop="toggleExpanded(policy.id)" :title="expandedPolicies.includes(policy.id) ? 'Collapse' : 'Expand'">
                  {{ expandedPolicies.includes(policy.id) ? '-' : policy.subpolicies.length }}
                </button>
              </td>
            </tr>
            <tr v-if="expandedPolicies.includes(policy.id)" :key="policy.id + '-subs'" class="subpolicies-row">
              <td class="subpolicies-container" colspan="12">
                <div class="subpolicies-wrapper">
                  <div v-for="sub in policy.subpolicies"
                       :key="sub.id"
                       :class="['subpolicy-tag', safeToLowerCase(sub.status)]"
                       @click="showSubpolicyDetails(sub)">
                    {{ sub.name }}
                    <span class="status-dot" :class="safeToLowerCase(sub.status)"></span>
                  </div>
                  <div v-if="!policy.subpolicies || policy.subpolicies.length === 0" class="no-subpolicies">
                    No subpolicies found
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
      <div v-if="filteredPolicies.length === 0" class="empty-state">
        <i class="fas fa-file-alt"></i>
        <p>No policies found for the selected filters</p>
      </div>
    </div>
  </div>
</template>
 
<script>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import './AllPolicies.css'
 
const API_BASE_URL = 'http://localhost:8000/api'
 
export default {
  name: 'AllPolicies',
  setup() {
    const searchQuery = ref('')
    const selectedFramework = ref('')
    const selectedStatus = ref('')
    const selectedActiveInactive = ref('')
    const viewMode = ref('card')
    const expandedPolicies = ref([])
    const loading = ref(false)
    const error = ref(null)
 
    // Data refs
    const policies = ref([])
    const summaryCounts = ref({
      active: 0,
      inactive: 0,
      approved: 0,
      rejected: 0,
      under_review: 0
    })
 
    // Fetch frameworks for dropdown
    const frameworks = ref([])
    const fetchFrameworks = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/frameworks/`)
        frameworks.value = response.data.map(fw => ({
          id: fw.FrameworkId,
          name: fw.FrameworkName
        }))
      } catch (err) {
        console.error('Error fetching frameworks:', err)
        error.value = 'Failed to fetch frameworks'
      }
    }
 
    // Fetch policies and summary counts
    const fetchPolicies = async () => {
      try {
        loading.value = true
        error.value = null
 
        let url = `${API_BASE_URL}/policies/`
        const params = new URLSearchParams()
       
        if (selectedFramework.value) {
          console.log('Adding framework_id to params:', selectedFramework.value)
          params.append('framework_id', selectedFramework.value)
        }
        if (selectedStatus.value) {
          params.append('status', selectedStatus.value)
        }
        if (selectedActiveInactive.value) {
          params.append('active_inactive', selectedActiveInactive.value)
        }
 
        const finalUrl = params.toString() ? `${url}?${params.toString()}` : url
        console.log('Fetching policies with URL:', finalUrl)
 
        const response = await axios.get(finalUrl)
        console.log('Received policies:', response.data)
       
        // Transform API data to match component structure
        policies.value = response.data.policies.map(p => ({
          id: p.PolicyId,
          name: p.PolicyName,
          identifier: p.Identifier,
          department: p.Department,
          applicability: p.Applicability,
          createdBy: p.CreatedByName,
          reviewer: p.Reviewer,
          startDate: p.StartDate,
          endDate: p.EndDate,
          framework: p.FrameworkName,
          frameworkId: p.FrameworkId,
          status: p.Status,
          activeInactive: p.ActiveInactive,
          description: p.PolicyDescription,
          scope: p.Scope,
          objectives: p.Objective ? p.Objective.split('\n').filter(obj => obj.trim()) : [],
          subpolicies: p.subpolicies ? p.subpolicies.map(sp => ({
            id: sp.SubPolicyId,
            name: sp.SubPolicyName,
            identifier: sp.Identifier,
            description: sp.Description,
            control: sp.Control,
            status: sp.Status
          })) : []
        }))
 
        // Update summary counts
        summaryCounts.value = response.data.summary_counts
 
      } catch (err) {
        console.error('Error fetching policies:', err)
        error.value = 'Failed to fetch policies'
      } finally {
        loading.value = false
      }
    }
 
    // Watch for filter changes
    watch([selectedFramework, selectedStatus, selectedActiveInactive], () => {
      console.log('Framework selected:', selectedFramework.value)
      fetchPolicies()
    })
 
    // Filtering logic
    const filteredPolicies = computed(() => {
      return policies.value.filter(policy => {
        // Search filter
        const matchesSearch = !searchQuery.value ||
          policy.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          policy.framework.toLowerCase().includes(searchQuery.value.toLowerCase());
 
        // Active/Inactive filter
        const matchesActiveInactive = !selectedActiveInactive.value ||
          policy.activeInactive === selectedActiveInactive.value;
 
        // Framework filter - ensure both values are strings when comparing
        const matchesFramework = !selectedFramework.value ||
          policy.frameworkId?.toString() === selectedFramework.value?.toString();
 
        // Status filter
        const matchesStatus = !selectedStatus.value ||
          policy.status === selectedStatus.value;
 
        return matchesSearch && matchesActiveInactive && matchesFramework && matchesStatus;
      });
    })
 
    // Format date function
    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
 
    function toggleViewMode() {
      viewMode.value = viewMode.value === 'card' ? 'table' : 'card'
    }
 
    function toggleExpanded(policyId) {
      if (expandedPolicies.value.includes(policyId)) {
        expandedPolicies.value = expandedPolicies.value.filter(id => id !== policyId)
      } else {
        expandedPolicies.value.push(policyId)
      }
    }
 
    const selectedPolicy = ref(null)
   
    const showPolicyDetails = (policy) => {
      selectedPolicy.value = {
        ...policy,
        description: policy.description || 'This document outlines the policy for the organization. This policy aims to ensure that the organization\'s information security is maintained and to comply with the information security program regarding the protection of sensitive information.',
        objectives: policy.objectives && policy.objectives.length > 0 ? policy.objectives : [
          'To ensure compliance with the organization\'s information security and quality requirements.',
          'To establish a process for managing the security and quality of information.',
          'To minimize the risk of information security incidents and quality issues.'
        ],
        scope: policy.scope || 'This policy applies to all who handle or have access to the organization\'s sensitive information or provide materials or services that affect product quality, including but not limited to contractors, sub-contractors, and third-party service providers.'
      }
    }
 
    const selectedSubpolicy = ref(null)
 
    const showSubpolicyDetails = (subpolicy) => {
      selectedSubpolicy.value = {
        ...subpolicy,
        description: subpolicy.description || 'This subpolicy provides specific controls and requirements for the parent policy.',
        control: subpolicy.control || 'Standard control measures apply to this subpolicy.'
      }
    }
 
    const handleSummaryCardClick = (filterType) => {
      // Clear all filters first if clicking an inactive filter
      if (
        (filterType === 'active' && selectedActiveInactive.value !== 'Active') ||
        (filterType === 'inactive' && selectedActiveInactive.value !== 'Inactive') ||
        (filterType === 'approved' && selectedStatus.value !== 'Approved') ||
        (filterType === 'rejected' && selectedStatus.value !== 'Rejected') ||
        (filterType === 'under-review' && selectedStatus.value !== 'Under Review')
      ) {
        selectedActiveInactive.value = ''
        selectedStatus.value = ''
      }
 
      // Apply the selected filter
      switch (filterType) {
        case 'active':
          selectedActiveInactive.value = selectedActiveInactive.value === 'Active' ? '' : 'Active'
          break
        case 'inactive':
          selectedActiveInactive.value = selectedActiveInactive.value === 'Inactive' ? '' : 'Inactive'
          break
        case 'approved':
          selectedStatus.value = selectedStatus.value === 'Approved' ? '' : 'Approved'
          break
        case 'rejected':
          selectedStatus.value = selectedStatus.value === 'Rejected' ? '' : 'Rejected'
          break
        case 'under-review':
          selectedStatus.value = selectedStatus.value === 'Under Review' ? '' : 'Under Review'
          break
      }
    }
 
    // Fetch data on component mount
    onMounted(() => {
      fetchFrameworks()
      fetchPolicies()
    })
 
    // Add this method to handle safe string operations
    const safeToLowerCase = (value) => {
      return (value || '').toLowerCase();
    }
    
    const safeString = (value) => {
      return value || '';
    }
 
    return {
      searchQuery,
      selectedFramework,
      selectedStatus,
      selectedActiveInactive,
      frameworks,
      policies,
      filteredPolicies,
      summaryCounts,
      viewMode,
      toggleViewMode,
      expandedPolicies,
      toggleExpanded,
      formatDate,
      loading,
      error,
      selectedPolicy,
      showPolicyDetails,
      handleSummaryCardClick,
      selectedSubpolicy,
      showSubpolicyDetails,
      safeToLowerCase,
      safeString
    }
  }
}
</script>
 
<style scoped>
/* Add new styles for loading and error states */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
 
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
 
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
 
.error-message {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #ff4444;
  color: white;
  padding: 12px 20px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
}
 
.close-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
}
 
/* Existing styles remain unchanged */
 
.subpolicy-table-item {
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin: 8px 0;
  background: #f9f9f9;
}
 
.subpolicy-table-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}
 
.subpolicy-identifier {
  color: #666;
  font-size: 0.9em;
}
 
.subpolicy-table-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 0.9em;
  color: #333;
}
 
.subpolicy-control,
.subpolicy-description {
  line-height: 1.4;
}
 
.no-subpolicies {
  text-align: center;
  color: #666;
  padding: 12px;
  font-style: italic;
}
 
.subpolicy-info {
  display: flex;
  align-items: center;
  gap: 8px;
}
 
/* Status colors */
.active { color: #4caf50; }
.inactive { color: #f44336; }
.under-review { color: #ff9800; }
.approved { color: #2196f3; }
.rejected { color: #9c27b0; }
 
.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.9em;
  width: fit-content;
  min-width: 80px;
}
 
.status-badge.active { background: #e8f5e9; }
.status-badge.inactive { background: #ffebee; }
.status-badge.under-review { background: #fff3e0; }
.status-badge.approved { background: #e3f2fd; }
.status-badge.rejected { background: #f3e5f5; }
 
.policy-table-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
 
.policy-table-status-dot.active { background: #4caf50; }
.policy-table-status-dot.inactive { background: #f44336; }
.policy-table-status-dot.under-review { background: #ff9800; }
.policy-table-status-dot.approved { background: #2196f3; }
.policy-table-status-dot.rejected { background: #9c27b0; }
 
.policy-status-row {
  display: flex;
  gap: 12px;
  margin: 8px 0;
}
 
.policy-active-status,
.policy-workflow-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.9em;
}
 
.policy-active-status.active {
  background: #e8f5e9;
  color: #4caf50;
}
 
.policy-active-status.inactive {
  background: #ffebee;
  color: #f44336;
}
 
.policy-workflow-status.approved {
  background: #e3f2fd;
  color: #2196f3;
}
 
.policy-workflow-status.rejected {
  background: #f3e5f5;
  color: #9c27b0;
}
 
.policy-workflow-status.under-review {
  background: #fff3e0;
  color: #ff9800;
}
 
.subpolicies-row {
  background: #f8f9fa;
}
 
.subpolicies-row td {
  padding: 0 !important;
}
 
.subpolicies-table-list {
  width: 100%;
  padding: 8px 16px;
}
 
.subpolicy-table-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  margin: 8px 0;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  gap: 16px;
}
 
.subpolicy-table-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}
 
.subpolicy-name {
  font-weight: 500;
  color: #333;
}
 
.subpolicy-identifier {
  color: #666;
  font-size: 0.9em;
}
 
.subpolicy-table-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
  padding-left: 24px;
}
 
.subpolicy-control,
.subpolicy-description {
  display: flex;
  gap: 8px;
  align-items: baseline;
}
 
.subpolicy-control strong,
.subpolicy-description strong {
  min-width: 100px;
  color: #666;
}
 
/* Update the expand button style */
.expand-btn {
  padding: 4px 12px;
  min-width: 40px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  margin: 0 auto;
  display: block;
  font-weight: 500;
  color: #333;
}
 
.expand-btn:hover {
  background: #f5f5f5;
  border-color: #ccc;
}
 
/* Add hover effect to the table rows */
.policy-table tbody tr:hover {
  background-color: #f8f9fa;
}
 
.policy-table-container {
  width: 100%;
  overflow-x: auto;
  margin-top: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 0;
}
 
.policy-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1400px; /* Increased minimum width to accommodate all columns */
  table-layout: auto; /* Changed to auto for better column distribution */
}
 
.policy-table th,
.policy-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
 
/* Column-specific widths */
.policy-table th:nth-child(1),
.policy-table td:nth-child(1) { /* Checkbox column */
  width: 40px;
}
 
.policy-table th:nth-child(2),
.policy-table td:nth-child(2) { /* Name column */
  width: 200px;
}
 
.policy-table th:nth-child(3),
.policy-table td:nth-child(3) { /* Identifier */
  width: 120px;
}
 
.policy-table th:nth-child(4),
.policy-table td:nth-child(4) { /* Department */
  width: 120px;
}
 
.policy-table th:nth-child(5),
.policy-table td:nth-child(5) { /* Applicability */
  width: 120px;
}
 
.policy-table th:nth-child(6),
.policy-table td:nth-child(6) { /* Created By */
  width: 120px;
}
 
.policy-table th:nth-child(7),
.policy-table td:nth-child(7) { /* Reviewer */
  width: 120px;
}
 
.policy-table th:nth-child(8),
.policy-table td:nth-child(8) { /* Start Date */
  width: 120px;
}
 
.policy-table th:nth-child(9),
.policy-table td:nth-child(9) { /* End Date */
  width: 120px;
}
 
.policy-table th:nth-child(10),
.policy-table td:nth-child(10) { /* Active/Inactive */
  width: 120px;
}
 
.policy-table th:nth-child(11),
.policy-table td:nth-child(11) { /* Status */
  width: 120px;
}
 
.policy-table th:nth-child(12),
.policy-table td:nth-child(12) { /* Sub Policies */
  width: 100px;
  text-align: center;
}
 
.policy-table th {
  background: #f5f5f5;
  font-weight: 600;
  color: #333;
  position: sticky;
  top: 0;
  z-index: 1;
}
 
.policy-table tr:hover {
  background-color: #f8f9fa;
}
 
.policy-table td[title] {
  cursor: help;
}
 
/* Container responsiveness */
@media screen and (max-width: 1400px) {
  .policy-table-container {
    margin: 0 -16px;
    border-radius: 0;
  }
}
 
.policy-details-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
 
.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
 
.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
 
.modal-header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}
 
.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}
 
.close-btn:hover {
  background: #f5f5f5;
}
 
.modal-body {
  padding: 20px;
}
 
.section {
  margin-bottom: 24px;
}
 
.section h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 12px;
}
 
.section p {
  color: #666;
  line-height: 1.6;
  margin: 0;
}
 
.section ul {
  list-style-type: disc;
  padding-left: 20px;
  color: #666;
  line-height: 1.6;
}
 
.modal-footer {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
}
 
.download-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}
 
.download-btn:hover {
  background: #0056b3;
}
 
/* Make table rows clickable */
.policy-table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s;
}
 
.policy-table tbody tr:hover {
  background-color: #f8f9fa;
}
 
/* Add styles for clickable policy name */
.policy-name-cell {
  cursor: pointer;
  color: #2196f3;
  text-decoration: underline;
}
 
.policy-name-cell:hover {
  color: #1976d2;
}
 
/* Update table cell styles */
.policy-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
 
/* Remove pointer cursor from table rows */
.policy-table tbody tr {
  cursor: default;
}
 
.summary-cards-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
 
.summary-card {
  background: white;
  border-radius: 8px;
  padding: 16px 24px;
  min-width: 140px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}
 
.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
 
.summary-card.active {
  border-color: #2196f3;
  background-color: #e3f2fd;
}
 
.summary-count {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}
 
.summary-label {
  font-size: 14px;
  color: #666;
}
 
/* Add specific colors for different status cards */
.summary-card[data-filter="active"]:hover,
.summary-card[data-filter="active"].active {
  border-color: #4caf50;
  background-color: #e8f5e9;
}
 
.summary-card[data-filter="inactive"]:hover,
.summary-card[data-filter="inactive"].active {
  border-color: #f44336;
  background-color: #ffebee;
}
 
.summary-card[data-filter="approved"]:hover,
.summary-card[data-filter="approved"].active {
  border-color: #2196f3;
  background-color: #e3f2fd;
}
 
.summary-card[data-filter="rejected"]:hover,
.summary-card[data-filter="rejected"].active {
  border-color: #9c27b0;
  background-color: #f3e5f5;
}
 
.summary-card[data-filter="under-review"]:hover,
.summary-card[data-filter="under-review"].active {
  border-color: #ff9800;
  background-color: #fff3e0;
}
</style>