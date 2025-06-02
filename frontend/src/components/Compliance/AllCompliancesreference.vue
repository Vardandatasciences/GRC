<template>
  <div class="all-compliances-container">
    <h1>All Compliances</h1>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <span>{{ error }}</span>
    </div>

    <div class="content-wrapper">
      <!-- Frameworks Section -->
      <div class="section frameworks-section">
        <h2>Frameworks</h2>
        <div v-if="loadingFrameworks" class="loading-spinner">
          <i class="fas fa-circle-notch fa-spin"></i>
          <span>Loading frameworks...</span>
        </div>
        <div v-else class="frameworks-list">
          <div v-for="framework in frameworks" 
               :key="framework.id" 
               class="framework-item"
               :class="{ active: selectedFramework?.id === framework.id }"
               @click="selectFramework(framework)">
            <i class="fas fa-sitemap"></i>
            <div class="item-content">
              <div class="item-header">
                <span class="item-name">{{ framework.name || 'Information Security Framework' }}</span>
                <span class="status-badge" :class="framework.status?.toLowerCase()">
                  {{ framework.status || 'Active' }}
                </span>
              </div>
              <span class="item-category" v-if="framework.category">{{ framework.category }}</span>
              <span class="item-description" v-if="framework.description">{{ framework.description }}</span>
              <span class="version-info">Version {{ framework.version || '1.0' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Policies Section -->
      <div v-if="selectedFramework" class="section policies-section">
        <h2>Policies</h2>
        <div v-if="loadingPolicies" class="loading-spinner">
          <i class="fas fa-circle-notch fa-spin"></i>
          <span>Loading policies...</span>
        </div>
        <div v-else-if="policies.length === 0" class="empty-state">
          <i class="fas fa-info-circle"></i>
          <span>No policies found</span>
        </div>
        <div v-else class="policies-list">
          <div v-for="policy in policies" 
               :key="policy.id" 
               class="policy-item"
               :class="{ active: selectedPolicy?.id === policy.id }"
               @click="selectPolicy(policy)">
            <i class="fas fa-file-alt"></i>
            <div class="item-content">
              <div class="item-header">
                <span class="item-name">{{ policy.name }}</span>
                <span class="status-badge" :class="policy.status?.toLowerCase()">
                  {{ policy.status }}
                </span>
              </div>
              <span class="item-category" v-if="policy.category">{{ policy.category }}</span>
              <span class="version-info">Version {{ policy.version || '1.0' }}</span>
              <span class="item-description" v-if="policy.description">{{ policy.description }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Subpolicies Section -->
      <div v-if="selectedPolicy" class="section subpolicies-section">
        <h2>Subpolicies</h2>
        <div v-if="loadingSubpolicies" class="loading-spinner">
          <i class="fas fa-circle-notch fa-spin"></i>
          <span>Loading subpolicies...</span>
        </div>
        <div v-else-if="subpolicies.length === 0" class="empty-state">
          <i class="fas fa-info-circle"></i>
          <span>No subpolicies found</span>
        </div>
        <div v-else class="subpolicies-list">
          <div v-for="subpolicy in subpolicies" 
               :key="subpolicy.id" 
               class="subpolicy-item"
               :class="{ active: selectedSubpolicy?.id === subpolicy.id }"
               @click="selectSubpolicy(subpolicy)">
            <i class="fas fa-tasks"></i>
            <div class="item-content">
              <div class="item-header">
                <span class="item-name">{{ subpolicy.name }}</span>
                <span class="status-badge" :class="subpolicy.status?.toLowerCase()">
                  {{ subpolicy.status }}
                </span>
              </div>
              <span class="item-description" v-if="subpolicy.description">{{ subpolicy.description }}</span>
              <span class="control-info" v-if="subpolicy.control">{{ subpolicy.control }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Compliances Section -->
      <div v-if="selectedSubpolicy" class="section compliances-section">
        <h2>Compliances</h2>
        <div v-if="loadingCompliances" class="loading-spinner">
          <i class="fas fa-circle-notch fa-spin"></i>
          <span>Loading compliances...</span>
        </div>
        <div v-else-if="compliances.length === 0" class="empty-state">
          <i class="fas fa-info-circle"></i>
          <span>No compliances found</span>
        </div>
        <div v-else class="compliances-list">
          <div v-for="compliance in compliances" 
               :key="compliance.ComplianceId" 
               class="compliance-item"
               :class="{ active: selectedCompliance?.ComplianceId === compliance.ComplianceId }"
               @click="selectCompliance(compliance)">
            <div class="compliance-header">
              <i class="fas fa-check-circle"></i>
              <div class="compliance-title">
                <span class="item-name">{{ compliance.ComplianceItemDescription }}</span>
                <div class="version-status">
                  <span class="version-info">v{{ compliance.ComplianceVersion }}</span>
                  <span class="status-badge" :class="compliance.ActiveInactive?.toLowerCase()">
                    {{ compliance.ActiveInactive }}
                  </span>
                </div>
              </div>
            </div>
            <div class="compliance-details">
              <span class="badge" :class="compliance.Status.toLowerCase()">{{ compliance.Status }}</span>
              <span class="badge" :class="compliance.Criticality.toLowerCase()">{{ compliance.Criticality }}</span>
              <span class="badge maturity-level">{{ compliance.MaturityLevel }}</span>
              <span class="badge">{{ compliance.ManualAutomatic }}</span>
              <span class="badge">{{ compliance.MandatoryOptional }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Compliance Versions Modal -->
    <div v-if="showVersionsModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Compliance Versions</h3>
          <button @click="closeVersionsModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div v-if="loading" class="loading-spinner">
            <i class="fas fa-circle-notch fa-spin"></i>
            <span>Loading versions...</span>
          </div>
          <div v-else-if="complianceVersions.length === 0" class="empty-state">
            <i class="fas fa-info-circle"></i>
            <span>No versions found</span>
          </div>
          <div v-else v-for="version in complianceVersions" 
               :key="version.ComplianceId" 
               class="version-item">
            <div class="version-header">
              <div class="version-title">
                <span class="version-number">Version {{ version.ComplianceVersion }}</span>
                <span class="status-badge" :class="version.ActiveInactive?.toLowerCase()">
                  {{ version.ActiveInactive }}
                </span>
              </div>
              <span class="badge" :class="version.Status.toLowerCase()">{{ version.Status }}</span>
            </div>
            <div class="version-details">
              <p>{{ version.ComplianceItemDescription }}</p>
              <div class="version-metadata">
                <span>Created by: {{ version.CreatedByName }}</span>
                <span>Date: {{ formatDate(version.CreatedByDate) }}</span>
                <span>Maturity Level: {{ version.MaturityLevel }}</span>
                <span>Criticality: {{ version.Criticality }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AllCompliances',
  data() {
    return {
      frameworks: [],
      policies: [],
      subpolicies: [],
      compliances: [],
      complianceVersions: [],
      selectedFramework: null,
      selectedPolicy: null,
      selectedSubpolicy: null,
      selectedCompliance: null,
      showVersionsModal: false,
      loading: false,
      error: null,
      loadingFrameworks: false,
      loadingPolicies: false,
      loadingSubpolicies: false,
      loadingCompliances: false
    }
  },
  methods: {
    async fetchFrameworks() {
      this.loadingFrameworks = true;
      this.error = null;
      try {
        const response = await axios.get('/api/all-policies/frameworks/');
        this.frameworks = response.data.map(framework => ({
          id: framework.FrameworkId,
          name: framework.FrameworkName,
          description: framework.FrameworkDescription,
          category: framework.Category,
          status: framework.ActiveInactive,
          version: framework.Version
        }));
      } catch (error) {
        console.error('Error fetching frameworks:', error);
        this.error = 'Failed to load frameworks. Please try again.';
      } finally {
        this.loadingFrameworks = false;
      }
    },

    async selectFramework(framework) {
      this.loadingPolicies = true;
      this.error = null;
      this.selectedFramework = framework;
      this.selectedPolicy = null;
      this.selectedSubpolicy = null;
      this.selectedCompliance = null;
      this.policies = [];
      this.subpolicies = [];
      this.compliances = [];
      
      try {
        const response = await axios.get(`/api/all-policies/policies/`, {
          params: { framework_id: framework.id }
        });
        this.policies = response.data.map(policy => ({
          id: policy.id,
          name: policy.name,
          description: policy.description,
          category: policy.category,
          status: policy.status,
          version: policy.Version
        }));
      } catch (error) {
        console.error('Error fetching policies:', error);
        this.error = 'Failed to load policies. Please try again.';
      } finally {
        this.loadingPolicies = false;
      }
    },

    async selectPolicy(policy) {
      this.loadingSubpolicies = true;
      this.error = null;
      this.selectedPolicy = policy;
      this.selectedSubpolicy = null;
      this.selectedCompliance = null;
      this.subpolicies = [];
      this.compliances = [];
      
      try {
        const response = await axios.get(`/api/all-policies/subpolicies/`, {
          params: { policy_id: policy.id }
        });
        this.subpolicies = response.data.map(subpolicy => ({
          id: subpolicy.id,
          name: subpolicy.name,
          description: subpolicy.description,
          status: subpolicy.status,
          control: subpolicy.control,
          version: subpolicy.Version
        }));
      } catch (error) {
        console.error('Error fetching subpolicies:', error);
        this.error = 'Failed to load subpolicies. Please try again.';
      } finally {
        this.loadingSubpolicies = false;
      }
    },

    async selectSubpolicy(subpolicy) {
      this.loadingCompliances = true;
      this.error = null;
      this.selectedSubpolicy = subpolicy;
      this.selectedCompliance = null;
      this.compliances = [];
      
      try {
        const response = await axios.get(`/api/all-policies/subpolicies/${subpolicy.id}/compliances/`);
        this.compliances = response.data.map(compliance => ({
          ComplianceId: compliance.ComplianceId,
          ComplianceItemDescription: compliance.ComplianceItemDescription,
          Status: compliance.Status,
          Criticality: compliance.Criticality,
          MaturityLevel: compliance.MaturityLevel,
          ActiveInactive: compliance.ActiveInactive,
          ManualAutomatic: compliance.ManualAutomatic,
          MandatoryOptional: compliance.MandatoryOptional,
          ComplianceVersion: compliance.ComplianceVersion
        }));
      } catch (error) {
        console.error('Error fetching compliances:', error);
        this.error = 'Failed to load compliances. Please try again.';
      } finally {
        this.loadingCompliances = false;
      }
    },

    async selectCompliance(compliance) {
      this.loading = true;
      this.error = null;
      this.selectedCompliance = compliance;
      
      try {
        const response = await axios.get(`/api/all-policies/compliances/${compliance.ComplianceId}/versions/`);
        this.complianceVersions = response.data;
        this.showVersionsModal = true;
      } catch (error) {
        console.error('Error fetching compliance versions:', error);
        this.error = 'Failed to load compliance versions. Please try again.';
      } finally {
        this.loading = false;
      }
    },

    closeVersionsModal() {
      this.showVersionsModal = false;
      this.complianceVersions = [];
    },

    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleDateString();
    },

    handleError(error) {
      console.error('API Error:', error);
      this.error = error.response?.data?.message || 'An error occurred. Please try again.';
    }
  },
  mounted() {
    this.fetchFrameworks();
  }
}
</script>

<style scoped>
@import './AllCompliances.css';

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.status-badge {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.status-badge.active {
  background-color: #e8f7ee;
  color: #22a722;
}

.status-badge.inactive {
  background-color: #fbeaea;
  color: #dc2626;
}

.version-info {
  font-size: 0.8rem;
  color: #6b46c1;
  font-weight: 500;
}

.item-description {
  font-size: 0.9rem;
  color: #666;
  margin-top: 4px;
}

.control-info {
  font-size: 0.85rem;
  color: #4b5563;
  margin-top: 4px;
  font-style: italic;
}

.compliance-title {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.version-status {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.version-title {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style> 