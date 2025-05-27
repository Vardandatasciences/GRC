<template>
  <div class="reviewer-page">
    <h2 class="page-title">Review Audit</h2>
    
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
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search audits..." 
            class="search-input"
          />
          <i class="search-icon">🔍</i>
        </div>
        
        <div class="filter-actions">
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
          
          <!-- Add view toggle control -->
          <div class="view-toggle">
            <span class="view-toggle-label">View:</span>
            <div class="toggle-buttons">
              <button 
                @click="viewMode = 'list'" 
                class="toggle-btn" 
                :class="{ active: viewMode === 'list' }"
              >
                <span>≡</span> List
              </button>
              <button 
                @click="viewMode = 'card'" 
                class="toggle-btn" 
                :class="{ active: viewMode === 'card' }"
              >
                <span>⊞</span> Card
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Table/List View -->
      <table v-if="viewMode === 'list'" class="reviews-table">
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
              <div class="status-dropdown-container">
                <span 
                  :class="getReviewStatusClass(audit.display_review_status || audit.review_status)"
                  class="status-badge status-clickable"
                  @click.stop="openStatusDropdown($event, audit.audit_id)"
                >
                  {{ audit.display_review_status || audit.review_status }}
                  <i class="fas fa-chevron-down status-dropdown-icon"></i>
                </span>
                <div v-if="openStatusIdx === audit.audit_id" class="status-options">
                  <div class="status-option" @click.stop="changeStatus(audit, 'Yet to Start')">
                    <span class="status-dot not-started"></span> Yet to Start
                  </div>
                  <div class="status-option" @click.stop="changeStatus(audit, 'In Review')">
                    <span class="status-dot in-review"></span> In Review
                  </div>
                  <div class="status-option" @click.stop="changeStatus(audit, 'Accept')">
                    <span class="status-dot accepted"></span> Accept
                  </div>
                  <div class="status-option" @click.stop="changeStatus(audit, 'Reject')">
                    <span class="status-dot rejected"></span> Reject
                  </div>
                </div>
              </div>
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
          </tr>
        </tbody>
      </table>
      
      <!-- Card View -->
      <div v-else class="cards-container">
        <div v-for="audit in filteredAudits" :key="audit.audit_id" class="audit-card" :class="getRowClass(audit)">
          <div class="card-header">
            <div class="card-id">#{{ audit.audit_id }}</div>
            <div class="card-framework">{{ audit.framework }}</div>
            <div class="card-policy">{{ audit.policy || 'All Policies' }} / {{ audit.subpolicy || 'All Subpolicies' }}</div>
          </div>
          
          <div class="card-body">
            <div class="card-info-row">
              <div class="card-info-icon">👤</div>
              <div class="card-info-label">Auditor:</div>
              <div class="card-info-value">{{ audit.auditor }}</div>
            </div>
            
            <div class="card-info-row">
              <div class="card-info-icon">📅</div>
              <div class="card-info-label">Due Date:</div>
              <div class="card-info-value">{{ audit.duedate }}</div>
            </div>
            
            <div class="card-info-row">
              <div class="card-info-icon">📊</div>
              <div class="card-info-label">Status:</div>
              <div class="card-info-value">{{ audit.status }}</div>
            </div>
            
            <div class="card-progress">
              <div class="card-progress-label">
                <span class="card-progress-text">Progress</span>
                <span class="card-progress-text">{{ audit.completion_percentage }}%</span>
              </div>
              <div class="card-progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: `${audit.completion_percentage}%` }"
                  :class="getProgressClass(audit.completion_percentage)"
                ></div>
              </div>
            </div>
          </div>
          
          <div class="card-footer">
            <div class="card-status">
              <div class="status-dropdown-container">
                <span 
                  :class="getReviewStatusClass(audit.display_review_status || audit.review_status)"
                  class="status-badge status-clickable"
                  @click.stop="openStatusDropdown($event, 'card-'+audit.audit_id)"
                >
                  {{ audit.display_review_status || audit.review_status }}
                  <i class="fas fa-chevron-down status-dropdown-icon"></i>
                </span>
                <div v-if="openStatusIdx === 'card-'+audit.audit_id" class="status-options">
                  <div class="status-option" @click.stop="changeStatus(audit, 'Yet to Start')">
                    <span class="status-dot not-started"></span> Yet to Start
                  </div>
                  <div class="status-option" @click.stop="changeStatus(audit, 'In Review')">
                    <span class="status-dot in-review"></span> In Review
                  </div>
                  <div class="status-option" @click.stop="changeStatus(audit, 'Accept')">
                    <span class="status-dot accepted"></span> Accept
                  </div>
                  <div class="status-option" @click.stop="changeStatus(audit, 'Reject')">
                    <span class="status-dot rejected"></span> Reject
                  </div>
                </div>
              </div>
            </div>
            
            <div class="card-actions">
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../../data/api.js';

export default {
  name: 'ReviewerPage',
  data() {
    return {
      audits: [],
      loading: true,
      error: null,
      searchQuery: '',
      statusFilter: '',
      viewMode: 'list',
      openStatusIdx: null
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
    
    canReview(audit) {
      // Can review if status is "Under review" and the can_update_review flag is true
      return audit.status === 'Under review' && audit.can_update_review === true;
    },
    
    getReviewButtonText(audit) {
      if (audit.review_status === 'In Review') {
        return 'Continue Review (Latest)';
      }
      return 'Review';
    },
    
    openReviewDialog(audit) {
      // Navigate to the ReviewTaskView component with the audit ID
      this.$router.push(`/reviewer/task/${audit.audit_id}`);
    },
    
    // Add this new method to handle direct status updates from the dropdown
    async updateReviewStatus(audit) {
      try {
        console.log(`Updating review status for audit ${audit.audit_id} to ${audit.review_status}`);
        
        const response = await api.updateAuditReviewStatus(audit.audit_id, {
          review_status: audit.review_status
        });
        
        console.log('Review status updated successfully:', response.data);
        
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
    
    openStatusDropdown(event, idx) {
      event.stopPropagation(); // Prevent row click event
      this.openStatusIdx = this.openStatusIdx === idx ? null : idx;
    },
    
    changeStatus(audit, newStatus) {
      audit.review_status = newStatus;
      this.updateReviewStatus(audit);
      this.openStatusIdx = null; // Close dropdown
    },
    
    closeDropdownOnClickOutside(event) {
      if (!event.target.closest('.status-dropdown-container')) {
        this.openStatusIdx = null;
      }
    }
  },
  mounted() {
    this.fetchReviewTasks();
    
    document.addEventListener('click', this.closeDropdownOnClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.closeDropdownOnClickOutside);
  }
};
</script>

<style scoped>
@import './Reviewer.css';
</style> 