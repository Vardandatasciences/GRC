<template>
  <div class="reviewer-page">
    <h2 class="page-title">
      <span class="page-title-icon"><i class="fas fa-clipboard-check"></i></span>
      Review Dashboard
    </h2>
    
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Loading review tasks...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchReviewTasks" class="btn-retry">Retry</button>
    </div>
    
    <div v-else-if="audits.length === 0" class="no-data">
      <p>No review tasks found</p>
    </div>
    
    <div v-else class="reviews-container">
      <div class="filters">
        <div class="status-filter">
          <label>Filter by Status:</label>
          <select v-model="statusFilter" class="status-select">
            <option value="">All Statuses</option>
            <option value="Yet to Start">Yet to Start</option>
            <option value="In Review">In Review</option>
            <option value="Accept">Accepted</option>
            <option value="Reject">Rejected</option>
          </select>
        </div>
        <div class="auditor-view-toggle">
          <button :class="{ active: view === 'list' }" @click="view = 'list'">
            <i class="fas fa-list"></i> List
          </button>
          <button :class="{ active: view === 'grid' }" @click="view = 'grid'">
            <i class="fas fa-th-large"></i> Card
          </button>
        </div>
      </div>
      
      <div v-if="view === 'list'">
        <table class="reviews-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Framework</th>
              <th>Policy</th>
              <th>Subpolicy</th>
              <th>Auditor</th>
              <th>Due Date</th>
              <th>Progress</th>
              <th>Audit Status</th>
              <th>Review Status</th>
              <th>Actions</th>
              <th>Download</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="audit in filteredAudits" :key="audit.audit_id" :class="getRowClass(audit)">
              <td>{{ audit.audit_id }}</td>
              <td>{{ audit.framework }}</td>
              <td>{{ audit.policy || 'All Policies' }}</td>
              <td>{{ audit.subpolicy || 'All Subpolicies' }}</td>
              <td>{{ audit.auditor }}</td>
              <td>{{ audit.duedate }}</td>
              <td>
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: `${audit.completion_percentage}%` }"
                    :class="getProgressClass(audit.completion_percentage)"
                  ></div>
                </div>
                <span class="progress-text">{{ audit.completion_percentage }}%</span>
              </td>
              <td>{{ audit.status }}</td>
              <td>
                <select 
                  v-model="audit.review_status" 
                  @change="updateReviewStatus(audit)" 
                  class="review-status-select"
                >
                  <option value="Yet to Start">Yet to Start</option>
                  <option value="In Review">In Review</option>
                  <option value="Accept">Accept</option>
                  <option value="Reject">Reject</option>
                </select>
                <span v-if="audit.approved_rejected" class="approved-rejected-badge" :class="getApprovedRejectedClass(audit.approved_rejected)">
                  {{ audit.approved_rejected }}
                </span>
              </td>
              <td>
                <button 
                  v-if="canReview(audit)" 
                  @click="openReviewDialog(audit)" 
                  class="btn-review"
                  :class="{ 'btn-in-progress': audit.review_status === 'In Review' }"
                  title="Review this audit"
                >
                  {{ getReviewButtonText(audit) }}
                </button>
              </td>
              <td class="text-center">
                <button 
                  class="btn-download" 
                  :disabled="!canDownload(audit)"
                  @click="downloadAuditReport(audit.audit_id)" 
                  title="Download Audit Report"
                >
                  <i class="fas fa-download"></i> Download
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="review-cards-grid">
        <div v-for="audit in filteredAudits" :key="audit.audit_id" class="review-card">
          <span class="review-card-status-top"
            :class="{
              'review-card-status-accept': audit.review_status === 'Accept',
              'review-card-status-inreview': audit.review_status === 'In Review',
              'review-card-status-reject': audit.review_status === 'Reject',
              'review-card-status-yet': audit.review_status === 'Yet to Start'
            }"
          ></span>
          <div class="review-card-header">
            <span class="review-card-title">#{{ audit.audit_id }} {{ audit.framework }}</span>
            <span class="review-card-info-label" style="font-weight:400; color:#888; font-size:13px;">{{ audit.policy || 'All Policies' }}<span v-if="audit.subpolicy"> / {{ audit.subpolicy }}</span></span>
          </div>
          <div class="review-card-body">
            <div class="review-card-info-row">
              <span class="review-card-info-icon"><i class="fas fa-user"></i></span>
              <span class="review-card-info-label">Auditor:</span>
              <span class="review-card-info-value">{{ audit.auditor }}</span>
            </div>
            <div class="review-card-info-row">
              <span class="review-card-info-icon"><i class="fas fa-calendar-alt"></i></span>
              <span class="review-card-info-label">Due Date:</span>
              <span class="review-card-info-value">{{ audit.duedate }}</span>
            </div>
            <div class="review-card-info-row">
              <span class="review-card-info-icon"><i class="fas fa-tasks"></i></span>
              <span class="review-card-info-label">Status:</span>
              <span class="review-card-info-value">{{ audit.status }}</span>
            </div>
            <div class="review-card-info-row">
              <span class="review-card-info-icon"><i class="fas fa-chart-bar"></i></span>
              <span class="review-card-info-label">Progress:</span>
              <span class="review-card-info-value">
                <div class="progress-bar" style="display:inline-block;width:70px;margin-right:6px;vertical-align:middle;">
                  <div 
                    class="progress-fill" 
                    :style="{ width: `${audit.completion_percentage}%` }"
                    :class="getProgressClass(audit.completion_percentage)"
                  ></div>
                </div>
                <span class="progress-text">{{ audit.completion_percentage }}%</span>
              </span>
            </div>
            <div class="review-card-info-row">
              <span class="review-card-info-icon"><i class="fas fa-clipboard-check"></i></span>
              <span class="review-card-info-label">Review Status:</span>
              <span class="review-card-info-value">
                <select 
                  v-model="audit.review_status" 
                  @change="updateReviewStatus(audit)" 
                  class="review-status-select"
                >
                  <option value="Yet to Start">Yet to Start</option>
                  <option value="In Review">In Review</option>
                  <option value="Accept">Accept</option>
                  <option value="Reject">Reject</option>
                </select>
                <span v-if="audit.approved_rejected" class="approved-rejected-badge" :class="getApprovedRejectedClass(audit.approved_rejected)">
                  {{ audit.approved_rejected }}
                </span>
              </span>
            </div>
          </div>
          <div class="review-card-footer">
            <div>
              <button 
                v-if="canReview(audit)" 
                @click="openReviewDialog(audit)" 
                class="btn-review"
                :class="{ 'btn-in-progress': audit.review_status === 'In Review' }"
                title="Review this audit"
              >
                {{ getReviewButtonText(audit) }}
              </button>
            </div>
            <div>
              <button 
                class="btn-download" 
                :disabled="!canDownload(audit)"
                @click="downloadAuditReport(audit.audit_id)" 
                title="Download Audit Report"
              >
                <i class="fas fa-download"></i> Download
              </button>
            </div>
          </div>
        </div>
        <!-- Placeholder cards to fill the row -->
        <div
          v-for="n in cardPlaceholders"
          :key="'placeholder-' + n"
          class="review-card review-card-placeholder"
          aria-hidden="true"
        ></div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../../data/api';

export default {
  name: 'ReviewerPage',
  data() {
    return {
      audits: [],
      loading: true,
      error: null,
      searchQuery: '',
      statusFilter: '',
      view: 'list',
    };
  },
  computed: {
    filteredAudits() {
      return this.audits.filter(audit => {
        // Status filter
        if (this.statusFilter && audit.review_status !== this.statusFilter) {
          return false;
        }
        
        // Search filter - search in framework, policy, auditor
        if (this.searchQuery) {
          const query = this.searchQuery.toLowerCase();
          const searchFields = [
            audit.framework,
            audit.policy,
            audit.subpolicy,
            audit.auditor,
            audit.status,
            audit.review_status
          ].filter(Boolean).map(field => field.toLowerCase());
          
          if (!searchFields.some(field => field.includes(query))) {
            return false;
          }
        }
        
        return true;
      });
    },
    cardPlaceholders() {
      const count = this.filteredAudits.length;
      const remainder = count % 3;
      return remainder === 0 ? 0 : 3 - remainder;
    }
  },
  created() {
    this.fetchReviewTasks();
  },
  methods: {
    async fetchReviewTasks() {
      this.loading = true;
      this.error = null;
      
      try {
        console.log('Fetching review tasks...');
        const response = await api.getMyReviews();
        this.audits = response.data.audits;
        console.log(`Fetched ${this.audits.length} review tasks`);
      } catch (error) {
        console.error('Error fetching review tasks:', error);
        this.error = error.response?.data?.error || 'Failed to load review tasks. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    getRowClass(audit) {
      // Get class based on review status
      if (audit.review_status === 'Yet to Start') {
        return 'status-not-started';
      } else if (audit.review_status === 'In Review') {
        return 'status-in-review';
      } else if (audit.review_status === 'Accept') {
        return 'status-accepted';
      } else if (audit.review_status === 'Reject') {
        return 'status-rejected';
      }
      return '';
    },
    
    getProgressClass(percentage) {
      if (percentage < 30) return 'progress-low';
      if (percentage < 70) return 'progress-medium';
      return 'progress-high';
    },
    
    getReviewStatusClass(status) {
      if (status === 'Yet to Start') return 'status-badge not-started';
      if (status === 'In Review') return 'status-badge in-review';
      if (status === 'Accept') return 'status-badge accepted';
      if (status === 'Reject') return 'status-badge rejected';
      return 'status-badge';
    },
    
    getApprovedRejectedClass(status) {
      if (status === 'Approved') return 'approved';
      if (status === 'Rejected') return 'rejected';
      return '';
    },
    
    canReview(audit) {
      // Can review if status is "Under review" and the can_update_review flag is true
      return audit.status === 'Under review' && audit.can_update_review === true;
    },
    
    getReviewButtonText(audit) {
      if (audit.review_status === 'In Review') {
        return 'Continue Review';
      }
      return 'Review Latest Submission';
    },
    
    openReviewDialog(audit) {
      // Navigate to the ReviewTaskView component with the audit ID
      console.log(`Opening review for audit ${audit.audit_id}`);
      this.$router.push(`/reviewer/task/${audit.audit_id}`);
    },
    
    async updateReviewStatus(audit) {
      try {
        console.log(`Updating review status for audit ${audit.audit_id} to ${audit.review_status}`);
        
        // Prompt for review comments if status is being set to Reject
        let review_comments = '';
        if (audit.review_status === 'Reject') {
          review_comments = prompt('Please provide rejection comments:', audit.review_comments || '');
          if (review_comments === null) {
            // User cancelled the prompt, revert the status change
            this.fetchReviewTasks();
            return;
          }
        } else if (audit.review_status === 'Accept') {
          // Optionally prompt for approval comments
          review_comments = prompt('Please provide any approval comments (optional):', audit.review_comments || '');
          if (review_comments === null) {
            // User cancelled the prompt, revert the status change
            this.fetchReviewTasks();
            return;
          }
        }
        
        const response = await api.updateAuditReviewStatus(audit.audit_id, {
          review_status: audit.review_status,
          review_comments: review_comments
        });
        
        console.log('Review status updated successfully:', response.data);
        
        // Update the local audit object with the comments
        audit.review_comments = review_comments;
        
        // If accepted, update audit status to Completed
        if (audit.review_status === 'Accept' && response.data.audit_status) {
          audit.status = response.data.audit_status;
        }
        
        // Show success message
        alert('Review status updated successfully!');
        
      } catch (error) {
        console.error('Error updating review status:', error);
        // Revert the status change on error
        this.fetchReviewTasks(); // Reload data from server
        alert(error.response?.data?.error || 'Failed to update review status. Please try again.');
      }
    },
    
    canDownload(audit) {
      // Can download if the review status is Accept
      return audit.review_status === 'Accept' || audit.status === 'ACCEPTED' || audit.status === 'APPROVED';
    },
    
    async downloadAuditReport(auditId) {
      try {
        console.log(`Downloading audit report for audit ${auditId}`);
        this.$toast?.info?.('Generating audit report...') || alert('Generating audit report...');
        
        // Create a direct URL for the download
        const reportUrl = `${api.baseURL || 'http://localhost:8000/api'}/generate-audit-report/${auditId}/`;
        console.log(`Downloading report from URL: ${reportUrl}`);
        
        // Use window.open for direct download
        window.open(reportUrl, '_blank');
        
        // Show success message
        this.$toast?.success?.('Report download initiated') || alert('Report download initiated');
      } catch (error) {
        console.error('Error initiating report download:', error);
        const errorMessage = error.message || 'Failed to download report. Please try again.';
        this.$toast?.error?.(errorMessage) || alert(errorMessage);
      }
    }
  }
};
</script>

<style scoped>
@import './Reviewer.css';
</style>