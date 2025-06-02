<template>
  <div class="auditor-dashboard-container">
    <div class="auditor-status-row">
      <div v-for="(s, i) in statusSummary" :key="i" class="auditor-status-box" :class="{
        'status-yet': s.label === 'Yet to start',
        'status-progress': s.label === 'Work In Progress',
        'status-review': s.label === 'Under review',
        'status-completed': s.label === 'Completed'
      }" :style="{ borderColor: s.color }">
        <span class="auditor-status-icon">
          <i v-if="s.label === 'Yet to start'" class="fas fa-hourglass-start"></i>
          <i v-else-if="s.label === 'Work In Progress'" class="fas fa-spinner"></i>
          <i v-else-if="s.label === 'Under review'" class="fas fa-search"></i>
          <i v-else-if="s.label === 'Completed'" class="fas fa-check-circle"></i>
        </span>
        <span class="auditor-status-count" :style="{ color: s.color }">{{ s.count }}</span>
        <span class="auditor-status-label">{{ s.label }}</span>
      </div>
    </div>
    <div v-if="loading" class="loading-indicator">Loading audits...</div>
    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="retryLoading" class="retry-btn">Retry</button>
    </div>
    <div class="auditor-filters-row" v-if="!loading">
      <select class="auditor-filter">
        <option value="">All Framework</option>
        <option v-for="fw in frameworks" :key="fw" :value="fw">{{ fw }}</option>
      </select>
      <select class="auditor-filter">
        <option value="">All Status</option>
        <option value="Yet to Start">Yet to Start</option>
        <option value="Work In Progress">Work In Progress</option>
        <option value="Under review">Under review</option>
        <option value="Completed">Completed</option>
      </select>
      <div class="auditor-view-toggle">
        <button :class="{ active: view === 'list' }" @click="view = 'list'">
          <i class="fas fa-list"></i> List
        </button>
        <button :class="{ active: view === 'grid' }" @click="view = 'grid'">
          <i class="fas fa-th-large"></i> Card
        </button>
      </div>
    </div>

    <!-- TABLE VIEW -->
    <div v-if="!loading && audits.length > 0 && view === 'list'" class="audits-table-wrapper">
      <table class="audits-table">
        <thead>
          <tr>
            <th>Frame work</th>
            <th>Policy</th>
            <th>Subpolicy</th>
            <th>Auditor</th>
            <th>Duedate</th>
            <th>Frequency</th>
            <th>Review</th>
            <th>Audit Type</th>
            <th>Status</th>
            <th>Report</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(audit, idx) in audits" :key="audit.audit_id">
            <td>{{ audit.framework }}</td>
            <td>{{ audit.policy }}</td>
            <td>{{ audit.subpolicy || '-' }}</td>
            <td>{{ audit.user }}</td>
            <td>{{ audit.date }}</td>
            <td>{{ audit.frequency }}</td>
            <td>{{ audit.reviewer }}</td>
            <td>{{ audit.auditType }}</td>
            <td>
              <select
                v-model="auditStatuses[idx]"
                class="auditor-card-status-select"
                :class="{
                  'status-yet': auditStatuses[idx] === 'Yet to Start',
                  'status-progress': auditStatuses[idx] === 'Work In Progress',
                  'status-review': auditStatuses[idx] === 'Under review',
                  'status-completed': auditStatuses[idx] === 'Completed'
                }"
                @change="handleStatusChange(idx, $event.target.value)"
                :disabled="audit.status === 'Completed'"
              >
                <option value="Yet to Start">Yet to Start</option>
                <option value="Work In Progress">Work In Progress</option>
                <option value="Under review">Under review</option>
                <option value="Completed">Completed</option>
              </select>
            </td>
            <td>
              <button 
                class="report-btn" 
                @click="showReports(audit)"
              >
                <i class="fas fa-file-download"></i> View Reports
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- CARD VIEW -->
    <div v-if="!loading && audits.length > 0 && view === 'grid'" class="audits-card-grid">
      <div v-for="(audit, idx) in audits" :key="audit.audit_id" class="audit-card">
        <div class="card-header">
          <span class="status-badge"
            :class="[
              audit.status === 'Completed' ? 'status-completed' :
              audit.status === 'Work In Progress' ? 'status-progress' :
              audit.status === 'Yet to Start' ? 'status-yet' :
              audit.status === 'Under review' ? 'status-review' : '',
            ]">
            {{ audit.status }}
          </span>
          <span class="card-framework">{{ audit.framework }}</span>
        </div>
        <div class="card-body">
          <div class="card-info-row">
            <span class="card-info-icon"><i class="fas fa-file-alt"></i></span>
            <span class="card-info-label">Policy:</span>
            <span class="card-info-value">{{ audit.policy }}</span>
          </div>
          <div class="card-info-row">
            <span class="card-info-icon"><i class="fas fa-list"></i></span>
            <span class="card-info-label">Subpolicy:</span>
            <span class="card-info-value">{{ audit.subpolicy || '-' }}</span>
          </div>
          <div class="card-info-row">
            <span class="card-info-icon"><i class="fas fa-user"></i></span>
            <span class="card-info-label">Auditor:</span>
            <span class="card-info-value">{{ audit.user }}</span>
          </div>
          <div class="card-info-row">
            <span class="card-info-icon"><i class="fas fa-calendar-alt"></i></span>
            <span class="card-info-label">Due Date:</span>
            <span class="card-info-value">{{ audit.date }}</span>
          </div>
          <div class="card-info-row">
            <span class="card-info-icon"><i class="fas fa-sync-alt"></i></span>
            <span class="card-info-label">Frequency:</span>
            <span class="card-info-value">{{ audit.frequency }}</span>
          </div>
          <div class="card-info-row">
            <span class="card-info-icon"><i class="fas fa-user-check"></i></span>
            <span class="card-info-label">Reviewer:</span>
            <span class="card-info-value">{{ audit.reviewer }}</span>
          </div>
          <!-- Status Dropdown and Task/Start Button Functionality -->
          <div class="card-info-row" style="margin-top: 10px; gap: 10px;">
            <select
              v-model="auditStatuses[idx]"
              class="auditor-card-status-select"
              :class="{
                'status-yet': auditStatuses[idx] === 'Yet to Start',
                'status-progress': auditStatuses[idx] === 'Work In Progress',
                'status-review': auditStatuses[idx] === 'Under review',
                'status-completed': auditStatuses[idx] === 'Completed'
              }"
              @change="handleStatusChange(idx, $event.target.value)"
              :disabled="audit.status === 'Completed'"
            >
              <option value="Yet to Start">Yet to Start</option>
              <option value="Work In Progress">Work In Progress</option>
              <option value="Under review">Under review</option>
              <option value="Completed">Completed</option>
            </select>
            <template v-if="audit.status === 'Yet to Start'">
              <button class="auditor-card-status start" @click="openPopup(idx)">Start</button>
            </template>
            <template v-else-if="audit.status === 'Work In Progress'">
              <button class="auditor-card-status progress" @click="openPopup(idx)">Task</button>
            </template>
          </div>
        </div>
        <div class="card-footer">
          <div class="card-audit-type">
            <i class="fas fa-clipboard-check"></i> {{ audit.auditType }}
          </div>
          <div class="card-report">
            <button 
              class="report-btn" 
              @click="showReports(audit)"
            >
              <i class="fas fa-file-download"></i> View Reports
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!loading && audits.length === 0" class="no-data-message">
      No audits found. You don't have any audits assigned to you.
    </div>

    <!-- Reports Modal -->
    <div v-if="showReportsModal" class="reports-modal-overlay">
      <div class="reports-modal">
        <div class="reports-modal-header">
          <h2>Previous Reports</h2>
          <button class="close-btn" @click="closeReportsModal">&times;</button>
        </div>
        
        <div v-if="loadingReports" class="loading-message">
          Loading reports...
        </div>
        
        <div v-else-if="reportsError" class="error-message">
          {{ reportsError }}
        </div>
        
        <div v-else-if="!reports || reports.length === 0" class="no-reports-message">
          No reports available for this audit
        </div>
        
        <div v-else class="reports-table-container">
          <table class="reports-table">
            <thead>
              <tr>
                <th>Report ID</th>
                <th>Report Date</th>
                <th>Auditor</th>
                <th>Reviewer</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="report in reports" :key="report.report_id">
                <td>{{ report.report_id }}</td>
                <td>{{ formatDate(report.report_date) }}</td>
                <td>{{ report.auditor }}</td>
                <td>{{ report.reviewer }}</td>
                <td>
                  <button class="action-btn view" @click="viewReport(report)">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="action-btn download" @click="downloadReport(report)">
                    <i class="fas fa-download"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Popup Modal -->
    <div v-if="showPopup" class="audit-popup-overlay">
      <div class="audit-popup-modal">
        <button class="popup-close" @click="closePopup">&times;</button>
        <div class="popup-header">
          <h2 class="popup-title">{{ popupData.framework }}</h2>
        </div>
        <div class="popup-content">
          <div class="popup-policy">
            <h3 class="popup-policy-name">{{ popupData.policy }}</h3>
            
        <div v-for="(sub, sIdx) in popupData.subpolicies" :key="sIdx" class="popup-subpolicy-block">
          <div class="popup-subpolicy-header">
                <span class="popup-subpolicy-name">{{ sub.name || 'N/A' }}</span>
          </div>
          <div class="popup-compliance-list">
            <div v-for="(compliance, cIdx) in sub.compliances" :key="cIdx" class="popup-compliance-row">
                  <input type="checkbox" v-model="compliance.checked" class="popup-compliance-checkbox" />
              <span class="popup-compliance-label">Compliance {{ cIdx + 1 }}</span>
              <input class="popup-comment-input" v-model="compliance.comment" placeholder="Comment" />
                </div>
                <button class="popup-add-btn" @click="addCompliance(sIdx)">Add</button>
              </div>
            </div>
          </div>
        </div>
        <button class="popup-submit-btn" @click="submitPopup">Submit</button>
      </div>
    </div>
  </div>
</template>

<script>
import './AuditorDashboard.css'
import { api } from '../../data/api'

export default {
  name: 'AuditorDashboard',
  data() {
    return {
      view: 'grid',
      auditStatuses: [],
      loading: true,
      error: '',
      statusSummary: [
        { label: 'Yet to start', count: 0, color: '#1aaf5d' },
        { label: 'Work In Progress', count: 0, color: '#2d7be5' },
        { label: 'Under review', count: 0, color: '#e5a12d' },
        { label: 'Completed', count: 0, color: '#1aaf5d' }
      ],
      audits: [],
      showPopup: false,
      popupData: {
        framework: '',
        policy: '',
        subpolicy: '',
        audit_id: null,
        subpolicies: [
          {
            name: '',
            compliances: [
              { checked: false, comment: '', commentChecked: false }
            ]
          }
        ]
      },
      frameworks: [],
      policies: [],
      statusUpdating: false,
      showReportsModal: false,
      loadingReports: false,
      reportsError: null,
      reports: [],
      currentAudit: null
    }
  },
  created() {
    this.fetchAudits()
  },
  methods: {
    retryLoading() {
      this.fetchAudits()
    },
    fetchAudits() {
      this.loading = true;
      this.error = '';
      
      api.getMyAudits()
        .then(response => {
          console.log('Audit data received:', response.data);
          
          // Transform the data for our component
          if (response.data && response.data.audits) {
            this.audits = response.data.audits.map(audit => {
              // Get reports field (try both cases and log for debugging)
              const reportsField = audit.Reports || audit.reports;
              console.log(`Audit ${audit.audit_id} raw reports field:`, audit.Reports);
              console.log(`Audit ${audit.audit_id} processed reports field:`, reportsField);
              
              // Check if reports are available
              const hasReports = Boolean(reportsField && reportsField !== 'null' && reportsField !== '[]' && reportsField !== '{}');
              console.log(`Audit ${audit.audit_id} has reports:`, hasReports);
              
              return {
                audit_id: audit.audit_id,
                framework: audit.framework || 'N/A',
                policy: audit.policy || 'N/A',
                subpolicy: audit.subpolicy && audit.subpolicy !== 'null' ? audit.subpolicy : null,
                user: audit.assignee || 'N/A',
                reviewer: audit.reviewer || 'N/A',
                status: audit.status || 'Yet to Start',
                date: audit.duedate || 'N/A',
                progress: audit.completion_percentage || 0,
                auditType: audit.audit_type_text || audit.audit_type || 'N/A',
                frequency: audit.frequency_text || 'N/A',
                Reports: reportsField, // Store reports field
                report_available: hasReports // Set report availability
              };
            });

            // Initialize auditStatuses with the initial statuses from audits
            this.auditStatuses = this.audits.map(a => a.status);
            
            // Update status summary counts
            this.updateStatusSummary();
            
            // Extract unique frameworks and policies for dropdown
            this.frameworks = [...new Set(this.audits.map(a => a.framework).filter(Boolean))];
            this.policies = [...new Set(this.audits.map(a => a.policy).filter(Boolean))];
          } else {
            this.audits = [];
            this.auditStatuses = [];
          }
          
          this.loading = false;
        })
        .catch(error => {
          console.error('Error fetching audits:', error);
          this.error = 'Failed to load audit data. Please try again.';
          this.loading = false;
        });
    },
    
    updateStatusSummary() {
      // Reset counts
      this.statusSummary.forEach(s => s.count = 0)
      
      // Count statuses
      this.audits.forEach(audit => {
        if (audit.status === 'Yet to Start') {
          this.statusSummary[0].count++
        } else if (audit.status === 'Work In progress' || audit.status === 'Work In Progress') {
          this.statusSummary[1].count++
        } else if (audit.status === 'Under review') {
          this.statusSummary[2].count++
        } else if (audit.status === 'Completed') {
          this.statusSummary[3].count++
        }
      })
    },
    
    handleStatusChange(idx, newStatus) {
      if (this.statusUpdating) return;
      this.statusUpdating = true;
      
      const auditId = this.audits[idx].audit_id;
      const oldStatus = this.audits[idx].status;
      
      // Optimistically update UI
      this.auditStatuses[idx] = newStatus;
      this.audits[idx].status = newStatus;
      this.updateStatusSummary();
      
      // Set progress to 100% if status is Completed
      if (newStatus === 'Completed') {
        this.audits[idx].progress = 100;
      }
      
      // Update the server - fix by passing status in correct format
      api.updateAuditStatus(auditId, { status: newStatus })
        .then(response => {
          console.log('Status update successful:', response.data);
          this.statusUpdating = false;
        })
        .catch(error => {
          console.error('Error updating status:', error);
          
          // Revert to old status on error
          this.auditStatuses[idx] = oldStatus;
          this.audits[idx].status = oldStatus;
          this.updateStatusSummary();
          
          this.error = 'Failed to update status. Please try again.';
          this.statusUpdating = false;
        });
    },
    
    openPopup(idx) {
      // If status is "Yet to Start", update it to "Work In Progress" when opening popup
      if (this.audits[idx].status === 'Yet to Start') {
        this.handleStatusChange(idx, 'Work In Progress');
      }
      
      const audit = this.audits[idx];
      
      // Navigate to the TaskView component with the audit ID
      this.$router.push(`/audit/${audit.audit_id}/tasks`);
    },
    
    closePopup() {
      this.showPopup = false
    },
    
    addCompliance(subIdx) {
      this.popupData.subpolicies[subIdx].compliances.push({ checked: false, comment: '', commentChecked: false })
    },
    
    submitPopup() {
      // Here you would send the compliance updates to the backend
      // For example:
      // api.updateComplianceItems(this.popupData.audit_id, transformedComplianceData)
      //   .then(() => {
      //     // Refresh data after update
      //     this.fetchAudits();
      //   })
      
      console.log('Submitting compliance updates:', this.popupData)
      this.closePopup()
      
      // For now, let's just update the local progress to show something changed
      const auditIndex = this.audits.findIndex(a => a.audit_id === this.popupData.audit_id)
      if (auditIndex >= 0) {
        // Simulate progress increase
        this.audits[auditIndex].progress = Math.min(100, this.audits[auditIndex].progress + 20)
        
        // If progress is 100%, change status to Completed
        if (this.audits[auditIndex].progress === 100) {
          this.handleStatusChange(auditIndex, 'Completed');
        }
      }
    },
    async showReports(audit) {
      console.log('Opening reports for audit:', audit);
      this.currentAudit = audit;
      this.showReportsModal = true;
      this.loadingReports = true;
      this.reportsError = null;
      
      try {
        // Check if Reports field exists
        const reportsField = audit.Reports;
        console.log('Raw reports field:', reportsField);
        console.log('Reports field type:', typeof reportsField);
        
        if (!reportsField) {
          console.log('No reports field found');
          this.reportsError = 'No reports available for this audit';
          this.loadingReports = false;
          return;
        }

        let reportIds = [];
        try {
          // Parse the Reports field
          let reportsData = reportsField;
          
          // If it's a string, try to parse it as JSON
          if (typeof reportsData === 'string') {
            console.log('Parsing string reports data:', reportsData);
            reportsData = JSON.parse(reportsData);
          }
          
          console.log('Parsed reports data:', reportsData);
          
          // Handle object format {"id_1": 11, "id_2": 12, "id_3": 22}
          if (typeof reportsData === 'object' && !Array.isArray(reportsData)) {
            reportIds = Object.values(reportsData).filter(id => id && !isNaN(id));
          } else if (Array.isArray(reportsData)) {
            // Handle array format
            reportIds = reportsData.filter(id => id && !isNaN(id));
          }
          
          console.log('Extracted report IDs:', reportIds);
          
          if (reportIds.length === 0) {
            throw new Error('No valid report IDs found');
          }

          // Convert reportIds to string for API call
          const reportIdsString = reportIds.join(',');
          console.log('Fetching details for reports:', reportIdsString);
          
          // Fetch details for each report ID
          const response = await api.getReportDetails(reportIdsString);
          console.log('Report details response:', response);
          
          if (response.data && response.data.reports && response.data.reports.length > 0) {
            this.reports = response.data.reports;
          } else {
            this.reportsError = 'No reports found for this audit';
            this.reports = [];
          }
        } catch (e) {
          console.error('Error parsing Reports data:', e);
          this.reportsError = 'Invalid report data format';
          this.loadingReports = false;
          return;
        }
      } catch (error) {
        console.error('Error loading reports:', error);
        this.reportsError = error.response?.data?.error || 'Failed to load reports. Please try again.';
      } finally {
        this.loadingReports = false;
      }
    },
    
    closeReportsModal() {
      this.showReportsModal = false;
      this.reports = [];
      this.currentAudit = null;
      this.reportsError = null;
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    
    viewReport(report) {
      // Implement view report functionality
      window.open(`/api/reports/${report.report_id}/view`, '_blank');
    },
    
    downloadReport(report) {
      // Implement download report functionality
      window.open(`/api/reports/${report.report_id}/download`, '_blank');
    }
  }
}
</script>

<style scoped>
@import './AuditorDashboard.css';

/* Add new styles for reports modal */
.reports-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.reports-modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 80%;
  max-width: 1000px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.reports-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.reports-modal-header h2 {
  margin: 0;
  color: #2d3748;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #4a5568;
}

.reports-table-container {
  overflow-x: auto;
}

.reports-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
}

.reports-table th,
.reports-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.reports-table th {
  background: #f7fafc;
  font-weight: 600;
  color: #4a5568;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  margin: 0 4px;
  border-radius: 4px;
  transition: background 0.2s;
}

.action-btn.view {
  color: #4299e1;
}

.action-btn.download {
  color: #48bb78;
}

.action-btn:hover {
  background: #edf2f7;
}

.no-reports-message {
  text-align: center;
  padding: 24px;
  color: #718096;
  font-size: 1.1rem;
}

.report-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #4f7cff;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s;
}

.report-btn:hover {
  background: #2563eb;
}
</style> 