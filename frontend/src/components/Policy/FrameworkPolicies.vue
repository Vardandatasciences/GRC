<template>
  <div class="framework-policies-container">
    <div class="breadcrumb-tab">
      <span class="breadcrumb-chip">
        {{ frameworkName }}
        <span class="breadcrumb-close" @click="goBack">×</span>
      </span>
    </div>
    <h2>Policies for {{ frameworkName }}</h2>
    <div class="policy-card-grid">
      <div v-for="policy in policies" :key="policy.id" class="policy-card">
        <div class="policy-card-header">
          <div class="policy-title-section">
            <span class="policy-icon">
              <i class="fas fa-file-alt"></i>
            </span>
            <span class="policy-card-title">{{ policy.name }}</span>
          </div>
          <span class="policy-card-status" :class="policy.status.toLowerCase()">{{ policy.status }}</span>
        </div>
        <div class="policy-card-category">Category: {{ policy.category }}</div>
        <div class="policy-card-desc">{{ policy.description }}</div>
        <div class="policy-card-actions">
          <div class="action-buttons">
            <button @click="toggleStatus(policy)">
              {{ policy.status === 'Active' ? 'Inactive' : 'Active' }}
            </button>
            <button v-if="policy.status === 'Active'" 
                    @click="acknowledgePolicy(policy)" 
                    class="acknowledge-btn"
                    :class="{ 'acknowledged': policy.isAcknowledged }">
              {{ policy.isAcknowledged ? 'Acknowledged' : 'Acknowledge' }}
            </button>
          </div>
          <span class="document-icon" @click="showPolicyDetails(policy.id)">
            <i class="fas fa-file-lines"></i>
          </span>
        </div>
      </div>
    </div>

    <!-- Policy Details Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Policy Details</h3>
          <span class="close-btn" @click="closeModal">&times;</span>
        </div>
        <div v-if="isLoadingDetails" class="modal-loading">
          <i class="fas fa-spinner fa-spin"></i> Loading details...
        </div>
        <div v-else-if="policyDetails" class="modal-body">
          <div class="detail-row">
            <span class="detail-label">Policy Name:</span>
            <span class="detail-value">{{ policyDetails.PolicyName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Description:</span>
            <span class="detail-value">{{ policyDetails.PolicyDescription }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Department:</span>
            <span class="detail-value">{{ policyDetails.Department }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Version:</span>
            <span class="detail-value">{{ policyDetails.CurrentVersion }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span class="detail-value">{{ policyDetails.Status }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Active/Inactive:</span>
            <span class="detail-value">{{ policyDetails.ActiveInactive }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Identifier:</span>
            <span class="detail-value">{{ policyDetails.Identifier }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Start Date:</span>
            <span class="detail-value">{{ formatDate(policyDetails.StartDate) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">End Date:</span>
            <span class="detail-value">{{ formatDate(policyDetails.EndDate) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Created By:</span>
            <span class="detail-value">{{ policyDetails.CreatedByName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Created Date:</span>
            <span class="detail-value">{{ formatDate(policyDetails.CreatedByDate) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Applicability:</span>
            <span class="detail-value">{{ policyDetails.Applicability }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Scope:</span>
            <span class="detail-value">{{ policyDetails.Scope }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Objective:</span>
            <span class="detail-value">{{ policyDetails.Objective }}</span>
          </div>
          <div class="detail-row" v-if="policyDetails.DocURL">
            <span class="detail-label">Documentation:</span>
            <a :href="policyDetails.DocURL" target="_blank" class="doc-link">View Documentation</a>
          </div>
          
          <!-- Subpolicies section -->
          <div v-if="policyDetails.subpolicies && policyDetails.subpolicies.length > 0" class="subpolicies-section">
            <h4>Subpolicies</h4>
            <div v-for="(subpolicy, index) in policyDetails.subpolicies" :key="index" class="subpolicy-item">
              <div class="subpolicy-header">
                <span class="subpolicy-name">{{ subpolicy.SubPolicyName }}</span>
                <span class="subpolicy-status" :class="subpolicy.Status.toLowerCase()">{{ subpolicy.Status }}</span>
              </div>
              <div class="subpolicy-detail">
                <span class="subpolicy-label">Identifier:</span>
                <span>{{ subpolicy.Identifier }}</span>
              </div>
              <div class="subpolicy-detail">
                <span class="subpolicy-label">Description:</span>
                <span>{{ subpolicy.Description }}</span>
              </div>
              <div class="subpolicy-detail">
                <span class="subpolicy-label">Control:</span>
                <span>{{ subpolicy.Control }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-subpolicies">
            No subpolicies found for this policy.
          </div>
        </div>
        <div v-else class="modal-error">
          Failed to load policy details.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const frameworkId = route.params.frameworkId
const frameworkName = ref('')
const policies = ref([])
const isLoading = ref(false)

// Modal and details states
const showModal = ref(false)
const isLoadingDetails = ref(false)
const policyDetails = ref(null)

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString()
  } catch (e) {
    return dateString
  }
}

// Fetch policies for the selected framework
const fetchPolicies = async () => {
  isLoading.value = true
  try {
    const response = await axios.get(`/api/frameworks/${frameworkId}/policies-list/`)
    policies.value = response.data.policies
    frameworkName.value = response.data.framework.name
  } catch (error) {
    console.error('Error fetching policies:', error)
  } finally {
    isLoading.value = false
  }
}

// Show policy details
const showPolicyDetails = async (policyId) => {
  policyDetails.value = null
  showModal.value = true
  isLoadingDetails.value = true
  
  try {
    const response = await axios.get(`/api/policies/${policyId}/details/`)
    policyDetails.value = response.data
  } catch (error) {
    console.error('Error fetching policy details:', error)
  } finally {
    isLoadingDetails.value = false
  }
}

// Close the modal
const closeModal = () => {
  showModal.value = false
}

// Toggle policy status
const toggleStatus = async (policy) => {
  try {
    const response = await axios.post(`/api/policies/${policy.id}/toggle-status/`, {
      cascadeSubpolicies: true // Ensure subpolicies are also updated
    })
    
    // Update local state
    policy.status = response.data.status
    
    // Show feedback to user
    let message = `Policy status changed to ${response.data.status}.`;
    
    if (response.data.other_versions_deactivated > 0) {
      message += ` ${response.data.other_versions_deactivated} other version(s) of this policy were automatically deactivated.`;
    }
    
    if (response.data.subpolicies_affected > 0) {
      message += ` ${response.data.subpolicies_affected} subpolicies belong to this policy (subpolicy status remains unchanged).`;
    }
    
    alert(message);
    
    // Refresh the policy list to ensure UI is in sync with backend
    await fetchPolicies();
  } catch (error) {
    console.error('Error toggling policy status:', error)
    alert('Failed to update policy status. Please try again.')
  }
}

// Add acknowledge policy function
const acknowledgePolicy = async (policy) => {
  try {
    const response = await axios.post(`/api/acknowledge-policy/${policy.id}/`)
    policy.isAcknowledged = true
    alert(response.data.message)
  } catch (error) {
    console.error('Error acknowledging policy:', error)
    alert('Failed to acknowledge policy. Please try again.')
  }
}

function goBack() {
  router.push({ name: 'FrameworkExplorer' })
}

// Fetch policies on component mount
onMounted(() => {
  fetchPolicies()
})
</script>

<style scoped>
.framework-policies-container {
  padding: 32px 40px;
  margin-left: 200px;
  max-width: calc(100vw - 240px);
  min-height: calc(100vh - 64px);
}

.breadcrumb-tab {
  margin-bottom: 24px;
}

.breadcrumb-chip {
  background: #e8edfa;
  color: #4f6cff;
  border-radius: 24px;
  padding: 12px 24px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  font-size: 0.95rem;
  box-shadow: 0 2px 8px rgba(79,108,255,0.12);
  letter-spacing: 0.01em;
  transition: all 0.2s ease;
}

.breadcrumb-chip:hover {
  box-shadow: 0 4px 12px rgba(79,108,255,0.18);
  transform: translateY(-1px);
}

.breadcrumb-close {
  margin-left: 12px;
  color: #888;
  font-size: 1rem;
  cursor: pointer;
  font-weight: bold;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

.breadcrumb-close:hover {
  color: #e53935;
  background-color: rgba(229, 57, 53, 0.1);
}

.policy-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  width: 100%;
  margin-top: 24px;
  box-sizing: border-box;
  padding: 0 16px;
}

.policy-card {
  background: #f7f7fa;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  font-size: 0.9rem;
  cursor: pointer;
  min-height: 180px;
  box-shadow: 0 4px 14px rgba(79,108,255,0.08);
  border-left: 4px solid transparent;
  transition: all 0.2s ease;
  width: 100%;
  box-sizing: border-box;
  margin: 0;
}

.policy-card:hover {
  transform: translateY(-2px) scale(1.025);
  box-shadow: 0 8px 24px rgba(79,108,255,0.13);
}

.policy-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.1rem;
  font-weight: 700;
  width: 100%;
  margin-bottom: 4px;
}

.policy-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #e8edfa;
  border-radius: 8px;
  color: #4f6cff;
  font-size: 1rem;
}

.policy-card-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  background: #f5f5f7;
}

.policy-card-status.active {
  color: #22a722;
  background: #e8f7ee;
}

.policy-card-status.inactive {
  color: #e53935;
  background: #fbeaea;
}

.policy-card-category {
  font-size: 0.85rem;
  color: #4f6cff;
  font-weight: 600;
  background: #e8edfa;
  border-radius: 8px;
  padding: 2px 8px;
  width: fit-content;
  margin-bottom: 8px;
}

.policy-card-desc {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #444;
  font-weight: 400;
  flex-grow: 1;
}

.policy-card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

button {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  background: #4f6cff;
  color: #fff;
  transition: all 0.2s;
  width: fit-content;
}

button:hover {
  background: #3a57e8;
  transform: translateY(-1px);
}

.document-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #f0f4ff;
  border-radius: 50%;
  color: #4f6cff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.document-icon:hover {
  background: #e0e7ff;
  transform: translateY(-2px);
}

h2 {
  font-size: 1.6rem;
  margin-bottom: 24px;
  color: #2c3e50;
  font-weight: 700;
}

.policy-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.policy-card-title {
  margin-left: 0;
  word-break: break-word;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 5px 30px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  background: white;
  z-index: 2;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.4rem;
}

.close-btn {
  font-size: 1.8rem;
  font-weight: bold;
  color: #666;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #e53935;
}

.modal-body {
  padding: 24px;
}

.modal-loading, .modal-error {
  padding: 24px;
  text-align: center;
  color: #666;
}

.detail-row {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
}

.detail-label {
  font-weight: 600;
  width: 140px;
  color: #555;
}

.detail-value {
  flex: 1;
  min-width: 200px;
}

.doc-link {
  color: #4f6cff;
  text-decoration: none;
  font-weight: 600;
}

.doc-link:hover {
  text-decoration: underline;
}

/* Subpolicies section */
.subpolicies-section {
  margin-top: 24px;
  border-top: 1px solid #eee;
  padding-top: 16px;
}

.subpolicies-section h4 {
  font-size: 1.2rem;
  margin-bottom: 16px;
  color: #2c3e50;
}

.subpolicy-item {
  background: #f8f9fd;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  border-left: 3px solid #4f6cff;
}

.subpolicy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.subpolicy-name {
  font-weight: 600;
  font-size: 1rem;
  color: #2c3e50;
}

.subpolicy-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.subpolicy-status.approved {
  color: #22a722;
  background: #e8f7ee;
}

.subpolicy-status.inactive, .subpolicy-status.rejected {
  color: #e53935;
  background: #fbeaea;
}

.subpolicy-status.under.review {
  color: #f5a623;
  background: #fff5e6;
}

.subpolicy-detail {
  margin-bottom: 6px;
  font-size: 0.9rem;
}

.subpolicy-label {
  font-weight: 600;
  color: #555;
  margin-right: 6px;
}

.no-subpolicies {
  margin-top: 16px;
  color: #666;
  font-style: italic;
  text-align: center;
}

@media (max-width: 1200px) {
  .policy-card-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    padding: 0 12px;
  }
}

@media (max-width: 800px) {
  .policy-card-grid {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 0 8px;
  }
  
  .framework-policies-container {
    padding: 20px;
  }
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.acknowledge-btn {
  background: #22a722 !important;
}

.acknowledge-btn.acknowledged {
  background: #4CAF50 !important;
  opacity: 0.8;
  cursor: default;
}

.acknowledge-btn:hover:not(.acknowledged) {
  background: #1b8c1b !important;
}
</style> 