<template>
  <div class="assign-audit-page">
    <h1 class="assign-audit-title left-align">
      <span class="assign-audit-title-icon blue-icon"><i class="fa fa-tasks"></i></span>
      Assign
    </h1>
    <div class="assign-audit-form-card">
      <form @submit.prevent="handleSubmit" class="assign-audit-form-grid">
        <!-- Framework -->
        <div class="form-group">
          <label><span class="form-icon blue-icon"><i class="fa fa-project-diagram"></i></span> Framework</label>
          <select v-model="form.framework" required @change="resetPolicySubpolicy">
            <option value="">Select Framework</option>
            <option v-for="f in dropdowns.frameworks || []" :key="f.FrameworkId" :value="f.FrameworkId">{{ f.FrameworkName }}</option>
          </select>
        </div>
        <!-- Policy -->
        <div class="form-group">
          <label><span class="form-icon blue-icon"><i class="fa fa-file-alt"></i></span> Policy</label>
          <select v-model="form.policy" @change="form.subpolicy = ''">
            <option value="">Select Policy</option>
            <option v-for="p in filteredPolicies" :key="p.PolicyId" :value="p.PolicyId">{{ p.PolicyName }}</option>
          </select>
        </div>
        <!-- Subpolicy -->
        <div class="form-group">
          <label><span class="form-icon blue-icon"><i class="fa fa-copy"></i></span> Subpolicy</label>
          <select v-model="form.subpolicy">
            <option value="">Select Subpolicy</option>
            <option v-for="sp in filteredSubpolicies" :key="sp.SubPolicyId" :value="sp.SubPolicyId">{{ sp.SubPolicyName }}</option>
          </select>
        </div>
        <!-- Auditor -->
        <div class="form-group">
          <label><span class="form-icon blue-icon"><i class="fa fa-user"></i></span> Auditor</label>
          <select v-model="form.auditor" required>
            <option value="">Select Auditor</option>
            <option v-for="u in dropdowns.users || []" :key="u.UserId" :value="u.UserId">{{ u.UserName }}</option>
          </select>
        </div>
        <!-- Due Date -->
        <div class="form-group">
          <label><span class="form-icon blue-icon"><i class="fa fa-calendar-alt"></i></span> Due Date</label>
          <input type="date" v-model="form.duedate" required />
        </div>
        <!-- Frequency -->
        <div class="form-group">
          <label><span class="form-icon blue-icon"><i class="fa fa-sync-alt"></i></span> Frequency</label>
          <select v-model="form.frequency" required>
            <option value="">Select Frequency</option>
            <option v-for="opt in frequencyOptions" :key="opt.value + opt.label" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <!-- Audit Type -->
        <div class="form-group">
          <label><span class="form-icon blue-icon"><i class="fa fa-tags"></i></span> Audit Type</label>
          <select v-model="form.audit_type" required>
            <option value="">Select Type</option>
            <option value="I">Internal</option>
            <option value="E">External</option>
          </select>
        </div>
        <!-- Reviewer -->
        <div class="form-group">
          <label><span class="form-icon blue-icon"><i class="fa fa-users"></i></span> Reviewer</label>
          <select v-model="form.reviewer">
            <option value="">Select Reviewer</option>
            <option v-for="u in dropdowns.users || []" :key="u.UserId" :value="u.UserId">{{ u.UserName }}</option>
          </select>
        </div>
        <!-- Buttons -->
        <div class="form-actions">
          <button type="button" class="reset-btn" @click="resetForm">Reset</button>
          <button type="submit" class="submit-btn" :disabled="submitting">
            {{ submitting ? 'Submitting...' : 'Submit' }}
          </button>
        </div>
      </form>
      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="success" class="success-message">{{ success }}</div>
    </div>

    <!-- Reports Modal -->
    <div v-if="showReportsModal" class="modal">
      <div class="modal-content">
        <h2>Previous Reports</h2>
        <div class="reports-table">
          <table>
            <thead>
              <tr>
                <th>Report ID</th>
                <th>Report Date</th>
                <th>Auditor</th>
                <th>Reviewer</th>
                <th>Select</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="report in previousReports" :key="report.ReportId">
                <td>{{ report.ReportId }}</td>
                <td>{{ formatDate(report.CompletionDate) }}</td>
                <td>{{ report.AuditorName }}</td>
                <td>{{ report.ReviewerName }}</td>
                <td>
                  <input 
                    type="checkbox" 
                    :value="report.ReportId" 
                    v-model="selectedReports"
                  >
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="modal-actions">
          <button @click="confirmReportSelection" class="submit-btn">Confirm</button>
          <button @click="closeReportsModal" class="reset-btn">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../../data/api';

export default {
  components: {},
  data() {
    // Get current date in YYYY-MM-DD format for default due date
    const today = new Date();
    const defaultDueDate = new Date(today);
    defaultDueDate.setDate(today.getDate() + 30); // Default to 30 days from now
    const formattedDueDate = defaultDueDate.toISOString().split('T')[0];
    
    return {
      showForm: false,
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
      loading: true,
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
      showReportsModal: false,
      previousReports: [],
      selectedReports: [],
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
      
      // Use Promise.all to load both datasets concurrently
      Promise.all([
        this.fetchDropdownData(),
        this.fetchAuditData()
      ])
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
      return api.getAssignData()
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
    fetchAuditData() {
      console.log("Fetching audit data...");
      return api.getAllAudits()
        .then(res => {
          console.log("Audit data received:", res.data);
          if (Array.isArray(res.data)) {
          this.auditData = res.data;
          this.filteredAuditData = res.data;
          } else {
            console.warn("Received non-array audit data:", res.data);
            this.auditData = [];
            this.filteredAuditData = [];
          }
          return res;
        })
        .catch(err => {
          console.error("Error fetching audit data:", err);
          this.auditData = [];
          this.filteredAuditData = [];
          throw err;
        });
    },
    handleSearch() {
      if (!Array.isArray(this.auditData)) {
        this.filteredAuditData = [];
        return;
      }
      
      const query = this.searchQuery.toLowerCase();
      if (!query) {
        this.filteredAuditData = this.auditData;
        return;
      }
      this.filteredAuditData = this.auditData.filter(audit =>
        (audit.framework && audit.framework.toLowerCase().includes(query)) ||
        (audit.policy && audit.policy.toLowerCase().includes(query)) ||
        (audit.subpolicy && audit.subpolicy.toLowerCase().includes(query)) ||
        (audit.auditor && audit.auditor.toLowerCase().includes(query)) ||
        (audit.status && audit.status.toLowerCase().includes(query))
      );
    },
    resetPolicySubpolicy() {
      this.form.policy = '';
      this.form.subpolicy = '';
    },
    async checkPreviousReports() {
      try {
        console.log('Checking previous reports with params:', {
          framework_id: this.form.framework,
          policy_id: this.form.policy || null,
          subpolicy_id: this.form.subpolicy || null
        });
        
        const response = await api.checkAuditReports({
          framework_id: this.form.framework,
          policy_id: this.form.policy || null,
          subpolicy_id: this.form.subpolicy || null
        });
        
        console.log('Previous reports response:', response.data);
        
        if (response.data.reports && response.data.reports.length > 0) {
          this.previousReports = response.data.reports;
          this.showReportsModal = true;
          console.log('Found previous reports:', this.previousReports);
          return true;
        }
        console.log('No previous reports found');
        return false;
      } catch (error) {
        console.error('Error checking previous reports:', error);
        return false;
      }
    },
    closeReportsModal() {
      console.log('Closing reports modal');
      this.showReportsModal = false;
      this.selectedReports = [];
    },
    async confirmReportSelection() {
      console.log('Confirming report selection:', this.selectedReports);
      this.showReportsModal = false;
      await this.submitForm(this.selectedReports);
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    async handleSubmit() {
      this.error = '';
      this.success = '';
      
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

      // Check for previous reports before submitting
      const hasReports = await this.checkPreviousReports();
      if (!hasReports) {
        await this.submitForm([]);
      }
    },
    async submitForm(selectedReports = []) {
      console.log('Submitting form with selected reports:', selectedReports);
      this.submitting = true;
      
      // Get current user ID if available from session/localStorage
      const currentUserId = localStorage.getItem('user_id') || 1020;
      
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
        is_draft: false,
        selected_reports: selectedReports
      };

      console.log("Sending payload:", payload);

      try {
        const response = await api.allocatePolicy(payload);
        console.log("Policy allocation successful:", response.data);
        this.success = `Audit assigned successfully! ${response.data.findings_created} compliance items created for audit.`;
        this.showForm = false;
        
        // Reset form
        this.resetForm();
        this.fetchAuditData();
      } catch (err) {
        console.error("Error allocating policy:", err);
        
        if (err.response?.data?.details) {
          const errorDetails = err.response.data.details;
          const errorMessages = [];
          
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
      } finally {
        this.submitting = false;
      }
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
    autoSaveForm() {
      // Don't auto-save if we don't have enough data yet
      if (!this.form.framework || !this.form.auditor || !this.form.duedate) {
        return;
      }
      
      // Set status to saving
      this.autoSaveStatus = 'Saving...';
      
      // Clear any existing timeout
      if (this.autoSaveTimeout) {
        clearTimeout(this.autoSaveTimeout);
      }
      
      // Set a timeout for debouncing
      this.autoSaveTimeout = setTimeout(async () => {
        try {
          // Get current user ID if available from session/localStorage
          const currentUserId = localStorage.getItem('user_id') || 1020;
          
          // Prepare payload for auto-save - mark it as a draft
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
            is_draft: true,
            auto_save: true
          };
          
          // If we already have a draft ID, update it instead of creating a new one
          let response;
          if (this.draftAuditId) {
            response = await api.updateDraftAudit(this.draftAuditId, payload);
          } else {
            response = await api.createDraftAudit(payload);
            // Store the draft ID for future updates
            if (response.data && response.data.audit_id) {
              this.draftAuditId = response.data.audit_id;
            }
          }
          
          console.log('Auto-saved audit form', response.data);
          this.autoSaveStatus = 'Saved';
          this.lastAutoSave = new Date();
          
          // Reset status after 3 seconds
          setTimeout(() => {
            this.autoSaveStatus = null;
          }, 3000);
          
        } catch (error) {
          console.error('Error auto-saving audit form:', error);
          this.autoSaveStatus = 'Save failed';
          
          // Reset status after 3 seconds
          setTimeout(() => {
            this.autoSaveStatus = null;
          }, 3000);
        }
      }, 2000); // 2 second debounce time
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
  },
  watch: {
    // Watch form fields for changes to trigger auto-save
    'form.framework': function() {
      if (this.form.framework) this.autoSaveForm();
    },
    'form.policy': function() {
      if (this.form.policy) this.autoSaveForm();
    },
    'form.subpolicy': function() {
      this.autoSaveForm();
    },
    'form.auditor': function() {
      if (this.form.auditor) this.autoSaveForm();
    },
    'form.duedate': function() {
      if (this.form.duedate) this.autoSaveForm();
    },
    'form.frequency': function() {
      if (this.form.frequency) this.autoSaveForm();
    },
    'form.audit_type': function() {
      if (this.form.audit_type) this.autoSaveForm();
    },
    'form.reviewer': function() {
      this.autoSaveForm();
    }
  }
};
</script>

<style scoped>
@import './AssignAudit.css';

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  width: 80%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.reports-table {
  margin: 1rem 0;
  overflow-x: auto;
}

.reports-table table {
  width: 100%;
  border-collapse: collapse;
}

.reports-table th,
.reports-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.reports-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.modal-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.modal-actions button {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s ease;
}

.modal-actions .submit-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
}

.modal-actions .reset-btn {
  background-color: #f44336;
  color: white;
  border: none;
}
</style>
