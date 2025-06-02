<template>
  <div class="version-list-container">
    <div class="version-list-header">
      <h2 class="version-list-heading">Compliance Version List</h2>
    </div>

    <!-- Filter Section -->
    <div class="filter-section">
      <div class="filter-group">
        <label>Framework:</label>
        <select v-model="selectedFramework" @change="loadPolicies" class="select">
          <option value="">Select Framework</option>
          <option v-for="framework in frameworks" 
                  :key="framework.FrameworkId" 
                  :value="framework.FrameworkId">
            {{ framework.FrameworkName }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>Policy:</label>
        <select v-model="selectedPolicy" @change="loadSubPolicies" :disabled="!selectedFramework" class="select">
          <option value="">Select Policy</option>
          <option v-for="policy in policies" 
                  :key="policy.PolicyId" 
                  :value="policy.PolicyId">
            {{ policy.PolicyName }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>Sub Policy:</label>
        <select v-model="selectedSubPolicy" @change="loadCompliances" :disabled="!selectedPolicy" class="select">
          <option value="">Select Sub Policy</option>
          <option v-for="subPolicy in subPolicies" 
                  :key="subPolicy.SubPolicyId" 
                  :value="subPolicy.SubPolicyId">
            {{ subPolicy.SubPolicyName }}
          </option>
        </select>
      </div>

      <!-- Search Bar -->
      <div class="search-bar-container">
        <input
          v-model="searchQuery"
          @keyup.enter="handleSearch"
          type="text"
          class="search-input"
          placeholder="Search..."
        />
        <button class="search-btn" @click="handleSearch">
          <svg height="20" width="20" viewBox="0 0 20 20" fill="none">
            <circle cx="9" cy="9" r="7" stroke="white" stroke-width="2"/>
            <line x1="14.2" y1="14.2" x2="18" y2="18" stroke="white" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Grouped Compliance Table -->
    <div class="table-container" v-if="groupedCompliances.length > 0">
      <div v-for="(group, groupIndex) in groupedCompliances" :key="groupIndex" class="compliance-group">
        <div class="group-header">
          <h3>Compliance ID: {{ group[0].Identifier }}</h3>
          <div class="group-description">{{ group[0].ComplianceItemDescription }}</div>
        </div>
        
        <div class="table-wrapper">
          <table class="compliance-table">
            <thead>
              <tr>
                <th>Version</th>
                <th>Status</th>
                <th>Active/Inactive</th>
                <th>Created By</th>
                <th>Created Date</th>
                <th>Previous Version</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="compliance in group" 
                  :key="compliance.ComplianceId"
                  :class="{ 'active-version': compliance.ActiveInactive === 'Active' }">
                <td>{{ compliance.ComplianceVersion }}</td>
                <td>{{ compliance.Status }}</td>
                <td>
                  <div class="toggle-switch">
                    <input 
                      type="checkbox" 
                      :id="'toggle-' + compliance.ComplianceId"
                      :checked="compliance.ActiveInactive === 'Active'"
                      @change="toggleActiveStatus(compliance)"
                      :disabled="compliance.Status !== 'Approved'"
                    >
                    <label :for="'toggle-' + compliance.ComplianceId"></label>
                  </div>
                </td>
                <td>{{ compliance.CreatedByName || 'N/A' }}</td>
                <td>{{ formatDate(compliance.CreatedByDate) }}</td>
                <td>{{ compliance.PreviousComplianceVersionId || 'None' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <div v-else-if="selectedSubPolicy" class="no-data">
      No compliances found for the selected criteria
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ComplianceVersionList',
  data() {
    return {
      frameworks: [],
      policies: [],
      subPolicies: [],
      compliances: [],
      selectedFramework: '',
      selectedPolicy: '',
      selectedSubPolicy: '',
      loading: false,
      searchQuery: ''
    }
  },
  computed: {
    groupedCompliances() {
      let filtered = this.compliances;
      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        filtered = filtered.filter(c =>
          (c.Identifier && c.Identifier.toLowerCase().includes(q)) ||
          (c.ComplianceItemDescription && c.ComplianceItemDescription.toLowerCase().includes(q))
        );
      }
      const groups = {};
      filtered.forEach(compliance => {
        if (!groups[compliance.Identifier]) {
          groups[compliance.Identifier] = [];
        }
        groups[compliance.Identifier].push(compliance);
      });
      // Sort each group by version number (descending)
      return Object.values(groups).map(group => {
        return group.sort((a, b) => {
          const versionA = parseFloat(a.ComplianceVersion);
          const versionB = parseFloat(b.ComplianceVersion);
          return versionB - versionA;
        });
      });
    }
  },
  mounted() {
    this.loadFrameworks();
  },
  methods: {
    async loadFrameworks() {
      try {
        const response = await axios.get('/frameworks/');
        if (response.data.success) {
          this.frameworks = response.data.data;
        } else {
          console.error('Error in response:', response.data);
        }
      } catch (error) {
        console.error('Error loading frameworks:', error);
      }
    },
    async loadPolicies() {
      if (!this.selectedFramework) {
        this.policies = [];
        this.selectedPolicy = '';
        return;
      }
      try {
        const response = await axios.get(`/frameworks/${this.selectedFramework}/policies/`);
        if (response.data.success) {
          this.policies = response.data.data;
        } else {
          console.error('Error in response:', response.data);
        }
        this.selectedPolicy = '';
        this.selectedSubPolicy = '';
      } catch (error) {
        console.error('Error loading policies:', error);
      }
    },
    async loadSubPolicies() {
      if (!this.selectedPolicy) {
        this.subPolicies = [];
        this.selectedSubPolicy = '';
        return;
      }
      try {
        const response = await axios.get(`/policies/${this.selectedPolicy}/subpolicies/`);
        if (response.data.success) {
          this.subPolicies = response.data.data;
        } else {
          console.error('Error in response:', response.data);
        }
        this.selectedSubPolicy = '';
      } catch (error) {
        console.error('Error loading subpolicies:', error);
      }
    },
    async loadCompliances() {
      if (!this.selectedSubPolicy) {
        this.compliances = [];
        return;
      }
      try {
        const response = await axios.get(`/subpolicies/${this.selectedSubPolicy}/compliances/`);
        if (response.data.success) {
          this.compliances = response.data.data;
        } else {
          console.error('Error in response:', response.data);
        }
      } catch (error) {
        console.error('Error loading compliances:', error);
      }
    },
    async toggleActiveStatus(compliance) {
      if (compliance.Status !== 'Approved') {
        alert('Only approved compliances can be toggled');
        return;
      }
      
      try {
        const response = await axios.post(`/compliance/${compliance.ComplianceId}/toggle-version/`);
        
        if (response.data.success) {
          await this.loadCompliances();
        } else {
          alert(response.data.message || 'Error toggling compliance status');
        }
      } catch (error) {
        console.error('Error toggling compliance status:', error);
        alert('Error toggling compliance status');
      }
    },
    formatDate(date) {
      if (!date) return 'N/A';
      return new Date(date).toLocaleDateString();
    },
    handleSearch() {
      // Filtering is handled reactively in computed property
    }
  }
}
</script>

<style scoped>
@import './ComplianceVersioning.css';
</style> 