<template>
  <div class="assign-audit-container">
    <div class="assign-audit-header">
      <h1><i class="fas fa-clipboard-check header-icon"></i> Assign Audit</h1>
    </div>
    
    <!-- Messages -->
    <div v-if="error" class="error-message">
      <i class="fas fa-exclamation-circle message-icon"></i>
      {{ error }}
      <button @click="retryLoading" class="retry-btn">Retry</button>
    </div>
    <div v-if="success" class="success-message">
      <i class="fas fa-check-circle message-icon"></i>
      {{ success }}
    </div>

    <!-- Loading indicator -->
    <div v-if="loading" class="loading-indicator">
      <i class="fas fa-spinner fa-spin"></i> Loading form data, please wait...
    </div>

    <!-- Form section -->
    <div v-else class="assign-audit-form-container">
        <form @submit.prevent="handleSubmit" class="assign-audit-form">
        <div class="form-fields-layout">
          <div class="form-field framework-field">
            <label for="framework">
              <i class="fas fa-project-diagram field-icon"></i> Framework
            </label>
            <select id="framework" v-model="form.framework" required @change="resetPolicySubpolicy">
              <option value="">Select Framework</option>
              <option v-for="f in dropdowns.frameworks || []" :key="f.FrameworkId" :value="f.FrameworkId">{{ f.FrameworkName }}</option>
            </select>
          </div>

          <div class="form-field policy-field">
            <label for="policy">
              <i class="fas fa-file-alt field-icon"></i> Policy
          </label>
            <select id="policy" v-model="form.policy" @change="form.subpolicy = ''">
              <option value="">Select Policy</option>
              <option v-for="p in filteredPolicies" :key="p.PolicyId" :value="p.PolicyId">{{ p.PolicyName }}</option>
            </select>
          </div>

          <div class="form-field subpolicy-field">
            <label for="subpolicy">
              <i class="fas fa-file-contract field-icon"></i> Subpolicy
          </label>
            <select id="subpolicy" v-model="form.subpolicy">
              <option value="">Select Subpolicy</option>
              <option v-for="sp in filteredSubpolicies" :key="sp.SubPolicyId" :value="sp.SubPolicyId">{{ sp.SubPolicyName }}</option>
            </select>
          </div>

          <div class="form-field auditor-field">
            <label for="auditor">
              <i class="fas fa-user-tie field-icon"></i> Auditor
          </label>
            <select id="auditor" v-model="form.auditor" required>
              <option value="">Select Auditor</option>
              <option v-for="u in dropdowns.users || []" :key="u.UserId" :value="u.UserId">{{ u.UserName }}</option>
            </select>
          </div>

          <div class="form-field date-field">
            <label for="duedate">
              <i class="fas fa-calendar-alt field-icon"></i> Due Date
          </label>
            <input 
              id="duedate" 
              type="date" 
              v-model="form.duedate" 
              required 
              min="2023-01-01"
              :max="maxDate"
            />
          </div>

          <div class="form-field frequency-field">
            <label for="frequency">
              <i class="fas fa-sync-alt field-icon"></i> Frequency
          </label>
            <select id="frequency" v-model="form.frequency" required>
              <option value="">Select Frequency</option>
              <option v-for="opt in frequencyOptions" :key="opt.value + opt.label" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>

          <div class="form-field audit-type-field">
            <label for="audit_type">
              <i class="fas fa-tag field-icon"></i> Audit Type
          </label>
            <select id="audit_type" v-model="form.audit_type" required>
              <option value="">Select Type</option>
              <option value="I">Internal</option>
              <option value="E">External</option>
            </select>
          </div>

          <div class="form-field reviewer-field">
            <label for="reviewer">
              <i class="fas fa-user-check field-icon"></i> Reviewer
          </label>
            <select id="reviewer" v-model="form.reviewer">
              <option value="">Select Reviewer</option>
              <option v-for="u in dropdowns.users || []" :key="u.UserId" :value="u.UserId">{{ u.UserName }}</option>
            </select>
          </div>
          </div>

        <div class="form-actions">
          <button type="button" @click="resetForm" class="cancel-btn">
            <i class="fas fa-undo-alt"></i> Reset
          </button>
          <button type="submit" :disabled="submitting" class="submit-btn">
            <i class="fas fa-save"></i> {{ submitting ? 'Submitting...' : 'Submit' }}
            </button>
          </div>
        </form>
    </div>
    
    <!-- Audit Details Modal -->
    <div v-if="showAuditDetails && currentAudit" class="assign-audit-modal">
      <div class="assign-audit-modal-content audit-details-modal">
        <div class="modal-header">
          <h2><i class="fas fa-info-circle"></i> Audit Details</h2>
          <button type="button" class="close-btn" @click="closeAuditDetails">&times;</button>
        </div>
        
        <div v-if="loadingAuditDetails" class="loading-indicator">
          <i class="fas fa-spinner fa-spin"></i> Loading audit details...
        </div>
        
        <div v-else-if="currentAudit" class="audit-details-content">
          <div class="audit-info">
            <div class="info-item">
              <strong><i class="fas fa-project-diagram"></i> Framework:</strong> {{ currentAudit.framework || 'N/A' }}
            </div>
            <div class="info-item">
              <strong><i class="fas fa-file-alt"></i> Policy:</strong> {{ currentAudit.policy || 'N/A' }}
            </div>
            <div class="info-item">
              <strong><i class="fas fa-file-contract"></i> Subpolicy:</strong> {{ currentAudit.subpolicy || 'N/A' }}
            </div>
            <div class="info-item">
              <strong><i class="fas fa-user-tie"></i> Auditor:</strong> {{ currentAudit.auditor || 'N/A' }}
            </div>
            <div class="info-item">
              <strong><i class="fas fa-user"></i> Assignee:</strong> {{ currentAudit.assignee || 'N/A' }}
            </div>
            <div class="info-item">
              <strong><i class="fas fa-user-check"></i> Reviewer:</strong> {{ currentAudit.reviewer || 'N/A' }}
            </div>
            <div class="info-item">
              <strong><i class="fas fa-calendar-alt"></i> Due Date:</strong> {{ currentAudit.duedate || 'N/A' }}
            </div>
            <div class="info-item">
              <strong><i class="fas fa-info-circle"></i> Status:</strong> {{ currentAudit.status || 'N/A' }}
            </div>
            <div class="info-item">
              <strong><i class="fas fa-tasks"></i> Completion:</strong> {{ currentAudit.completed_compliances || 0 }}/{{ currentAudit.total_compliances || 0 }}
            </div>
          </div>
          
          <div v-if="currentAudit.compliance_items && currentAudit.compliance_items.length > 0" class="compliance-items">
            <h3><i class="fas fa-clipboard-list"></i> Compliance Items</h3>
            <table class="compliance-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Description</th>
                  <th>Criticality</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in currentAudit.compliance_items" :key="item.ComplianceId">
                  <td>{{ item.ComplianceId }}</td>
                  <td>{{ item.ComplianceItemDescription }}</td>
                  <td>{{ formatCriticality(item.Criticality) }}</td>
                  <td>{{ item.status_text }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="no-compliance-items">
            <p><i class="fas fa-exclamation-circle"></i> No compliance items found for this audit.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../../data/api.js';

export default {
  components: {},
  data() {
    // Get current date in YYYY-MM-DD format for default due date
    const today = new Date();
    const defaultDueDate = new Date(today);
    defaultDueDate.setDate(today.getDate() + 30); // Default to 30 days from now
    const formattedDueDate = defaultDueDate.toISOString().split('T')[0];
    
    return {
      searchQuery: '',
      form: {
        framework: '',
        policy: '',
        subpolicy: '',
        auditor: '',
        duedate: formattedDueDate,
        frequency: 182, // Default to Half Yearly
        audit_type: 'I', // Default to Internal
        reviewer: ''
      },
      dropdowns: {
        frameworks: [],
        policies: [],
        subpolicies: [],
        users: []
      },
      auditData: [],
      filteredAuditData: [],
      error: '',
      success: '',
      loading: false,
      submitting: false,
      frequencyOptions: [
        { label: 'Only Once', value: 0 },
        { label: 'Daily', value: 1 },
        { label: 'Every 2 Months', value: 60 },
        { label: 'Every 4 Months', value: 120 },
        { label: 'Half Yearly', value: 182 },
        { label: 'Yearly', value: 365 },
        { label: 'Annually', value: 365 },
      ],
      showAuditDetails: false,
      currentAudit: null,
      loadingAuditDetails: false,
      autoSaveStatus: null,
      autoSaveTimeout: null,
      lastAutoSave: null,
      draftAuditId: null,  // To store the ID of a draft audit being edited
    };
  },
  computed: {
    filteredPolicies() {
      if (!this.dropdowns.policies || !Array.isArray(this.dropdowns.policies)) {
        return [];
      }
      return this.dropdowns.policies.filter(p => p && String(p.FrameworkId) === String(this.form.framework));
    },
    filteredSubpolicies() {
      if (!this.dropdowns.subpolicies || !Array.isArray(this.dropdowns.subpolicies)) {
        return [];
      }
      return this.dropdowns.subpolicies.filter(sp => sp && String(sp.PolicyId) === String(this.form.policy));
    },
    maxDate() {
      // Allow selecting dates up to 5 years in the future
      const fiveYearsLater = new Date();
      fiveYearsLater.setFullYear(fiveYearsLater.getFullYear() + 5);
      return fiveYearsLater.toISOString().split('T')[0];
    }
  },
  mounted() {
    console.log("Component mounted, fetching data...");
    this.loadData();
  },
  methods: {
    loadData() {
      this.loading = true;
      this.error = '';
      
      // Only fetch dropdown data, not audit data since we don't need it anymore
      this.fetchDropdownData()
        .then(() => {
          this.loading = false;
        })
        .catch(err => {
          this.loading = false;
          this.error = `Failed to load data: ${err.message || err}`;
          console.error("Error loading data:", err);
        });
    },
    retryLoading() {
      this.loadData();
    },
    fetchDropdownData() {
      console.log("Fetching dropdown data...");
      return api.getAssignData()  // Use the API method instead of direct axios
        .then(res => {
          console.log("Dropdown data received:", res.data);
          // Ensure all properties exist and are arrays
          this.dropdowns = {
            frameworks: Array.isArray(res.data.frameworks) ? res.data.frameworks : [],
            policies: Array.isArray(res.data.policies) ? res.data.policies : [],
            subpolicies: Array.isArray(res.data.subpolicies) ? res.data.subpolicies : [],
            users: Array.isArray(res.data.users) ? res.data.users : []
          };
          return res;
        })
        .catch(err => {
          console.error("Error fetching dropdown data:", err);
          throw err;
        });
    },
    resetPolicySubpolicy() {
      this.form.policy = '';
      this.form.subpolicy = '';
    },
    handleSubmit() {
      this.error = '';
      this.success = '';
      
      console.log("Submitting form with data:", this.form);
      
      // Client-side validation
      if (!this.form.framework) {
        this.error = "Framework is required";
        return;
      }
      
      if (!this.form.auditor) {
        this.error = "Auditor is required";
        return;
      }
      
      if (!this.form.duedate) {
        this.error = "Due date is required";
        return;
      }
      
      if (!this.form.frequency) {
        this.error = "Frequency is required";
        return;
      }
      
      if (!this.form.audit_type) {
        this.error = "Audit type is required";
        return;
      }
      
      this.submitting = true;
      
      // Get current user ID if available from session/localStorage
      const currentUserId = localStorage.getItem('user_id') || 1020;  // Default to 1020 if not set
      
      // Convert any empty strings to null for optional fields
      const payload = {
        framework: parseInt(this.form.framework),
        policy: this.form.policy ? parseInt(this.form.policy) : null,
        subpolicy: this.form.subpolicy ? parseInt(this.form.subpolicy) : null,
        assignee: parseInt(currentUserId),
        auditor: parseInt(this.form.auditor),
        reviewer: this.form.reviewer ? parseInt(this.form.reviewer) : null,
        duedate: this.form.duedate,
        frequency: parseInt(this.form.frequency),
        audit_type: this.form.audit_type,
        is_draft: false  // Mark as a final submission, not a draft
      };

      console.log("Sending payload:", payload);

      this.error = this.success = '';
      api.allocatePolicy(payload)
        .then(response => {
          console.log("Policy allocation successful:", response.data);
          this.success = `Audit assigned successfully! ${response.data.findings_created} compliance items created for audit.`;
          
          // Reset form with defaults
          this.resetForm();
          
          this.submitting = false;
        })
        .catch(err => {
          console.error("Error allocating policy:", err);
          
          // Handle detailed validation errors if available
          if (err.response?.data?.details) {
            const errorDetails = err.response.data.details;
            const errorMessages = [];
            
            // Format each field's errors
            for (const field in errorDetails) {
              if (errorDetails[field] && errorDetails[field].length > 0) {
                errorMessages.push(`${field}: ${errorDetails[field].join(', ')}`);
              }
            }
            
            if (errorMessages.length > 0) {
              this.error = errorMessages.join(' | ');
            } else {
              this.error = err.response?.data?.error || `Failed to assign audit: ${err.message || err}`;
            }
          } else {
            this.error = err.response?.data?.error || `Failed to assign audit: ${err.message || err}`;
          }
          
          this.submitting = false;
        });
    },
    viewAuditDetails(auditId) {
      if (!auditId) {
        this.error = 'Invalid audit ID';
        return;
      }
      
      this.loadingAuditDetails = true;
      this.currentAudit = null;
      this.showAuditDetails = true;
      
      console.log("Fetching audit details for ID:", auditId);
      api.getAuditDetails(auditId)
        .then(response => {
          console.log("Audit details received:", response.data);
          this.currentAudit = response.data;
          this.loadingAuditDetails = false;
        })
        .catch(err => {
          console.error("Error fetching audit details:", err);
          this.error = err.response?.data?.error || `Failed to load audit details: ${err.message || err}`;
          this.loadingAuditDetails = false;
          this.showAuditDetails = false;
        });
    },
    closeAuditDetails() {
      this.showAuditDetails = false;
      this.currentAudit = null;
    },
    resetForm() {
      // Get current date in YYYY-MM-DD format for default due date
      const today = new Date();
      const defaultDueDate = new Date(today);
      defaultDueDate.setDate(today.getDate() + 30); // Default to 30 days from now
      const formattedDueDate = defaultDueDate.toISOString().split('T')[0];
      
      // Reset form with defaults
      this.form = {
        framework: '',
        policy: '',
        subpolicy: '',
        auditor: '',
        duedate: formattedDueDate,
        frequency: 182, // Default to Half Yearly
        audit_type: 'I', // Default to Internal
        reviewer: ''
      };
      
      // Clear draft ID
      this.draftAuditId = null;
      this.success = '';
      this.error = '';
    },
    formatCriticality(value) {
      // Handle numeric criticality values
      if (value === 0 || value === '0') return 'Minor';
      if (value === 1 || value === '1') return 'Major'; 
      if (value === 2 || value === '2') return 'Not Applicable';
      
      // If it's already a string value, return as is
      if (typeof value === 'string' && isNaN(parseInt(value))) return value;
      
      // Default fallback
      return 'Not Specified';
    },
  }
};
</script>

<style scoped>
@import './AssignAudit.css';

/* Additional inline styles for icons and field-specific colors */
.header-icon {
  margin-right: 10px;
  color: #4f7cff;
}

.field-icon {
  margin-right: 8px;
  width: 16px;
}

.message-icon {
  margin-right: 8px;
}

/* Field-specific colors */
.framework-field label {
  color: #4f7cff;
}

.policy-field label {
  color: #4f7cff;
}

.subpolicy-field label {
  color: #4f7cff;
}

.auditor-field label {
  color: #4f7cff;
}

.date-field label {
  color: #4f7cff;
}

.frequency-field label {
  color: #4f7cff;
}

.audit-type-field label {
  color: #4f7cff;
}

.reviewer-field label {
  color: #4f7cff;
}
</style>
