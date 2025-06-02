<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Framework Approver</h2>
      <div class="dashboard-actions">
        <button class="action-btn" @click="refreshData"><i class="fas fa-sync-alt"></i></button>
        <button class="action-btn"><i class="fas fa-download"></i></button>
      </div>
    </div>

    <!-- Performance Summary Cards for Framework Approver -->
    <div class="performance-summary">
      <div class="summary-card growth">
        <div class="summary-icon"><i class="fas fa-user-check"></i></div>
        <div class="summary-content">
          <div class="summary-label">Pending Approvals</div>
          <div class="summary-value">{{ pendingApprovalsCount }}</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-check-circle"></i></div>
        <div class="summary-content">
          <div class="summary-label">Approved</div>
          <div class="summary-value">{{ approvedApprovalsCount }}</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-times-circle"></i></div>
        <div class="summary-content">
          <div class="summary-label">Rejected</div>
          <div class="summary-value">{{ rejectedApprovalsCount }}</div>
        </div>
      </div>
    </div>

    <!-- Framework Approvals List -->
    <div class="approvals-list">
      <h3>My Framework Approval Tasks</h3>
      <ul>
        <li v-for="framework in sortedFrameworks" 
            :key="framework.ApprovalId" 
            :class="{'new-framework': isNewFramework(framework)}">
          <div class="framework-item-header" @click="openApprovalDetails(framework)">
            <strong class="clickable">
              {{ getFrameworkId(framework) }}
            </strong>
            <span class="item-type-badge framework-badge">Framework</span>
            <span class="date-info">
              {{ formatDate(framework.ExtractedData?.CreatedByDate || framework.created_at) }}
            </span>
            <span v-if="isNewFramework(framework)" class="new-badge">NEW</span>
            <span class="framework-category">{{ framework.ExtractedData.Category || 'No Category' }}</span>
            <span class="assigned-by">
              <img class="assigned-avatar" :src="framework.ExtractedData.CreatedByAvatar || 'https://randomuser.me/api/portraits/men/32.jpg'" alt="avatar" />
              {{ framework.ExtractedData.CreatedByName || 'System' }}
            </span>
            <span v-if="framework.ApprovedNot === null" class="approval-status pending">(Pending)</span>
            <span v-else-if="framework.ApprovedNot === true" class="approval-status approved">
              <i class="fas fa-check"></i> Approved
            </span>
            <span v-else class="approval-status rejected">(Rejected)</span>
          </div>

          <!-- Inline Framework Details -->
          <div v-if="showDetails && selectedApproval && selectedApproval.FrameworkId === framework.FrameworkId" 
               class="framework-details-inline">
            <div class="framework-details-content">
              <h3>
                <span class="detail-type-indicator">Framework</span> 
                Details: {{ getFrameworkId(framework) }}
                <span class="version-pill">Version: {{ framework.version || 'u1' }}</span>
              </h3>
              
              <!-- Framework Approval Section -->
              <div class="framework-approval-section">
                <h4>Framework Approval</h4>
                
                <!-- Framework status indicator -->
                <div class="framework-status-indicator">
                  <span class="status-label">Status:</span>
                  <span class="status-value" :class="{
                    'status-approved': framework.ApprovedNot === true || framework.ExtractedData?.Status === 'Approved',
                    'status-rejected': framework.ApprovedNot === false || framework.ExtractedData?.Status === 'Rejected',
                    'status-pending': framework.ApprovedNot === null && framework.ExtractedData?.Status !== 'Approved' && framework.ExtractedData?.Status !== 'Rejected'
                  }">
                    {{ framework.ApprovedNot === true || framework.ExtractedData?.Status === 'Approved' ? 'Approved' : 
                       framework.ApprovedNot === false || framework.ExtractedData?.Status === 'Rejected' ? 'Rejected' : 
                       'Under Review' }}
                  </span>
                </div>
                
                <div class="framework-actions">
                  <button class="approve-btn" @click="approveFramework()" v-if="isReviewer && framework.ApprovedNot === null">
                    <i class="fas fa-check"></i> Approve
                  </button>
                  <button class="reject-btn" @click="rejectFramework()" v-if="isReviewer && framework.ApprovedNot === null">
                    <i class="fas fa-times"></i> Reject
                  </button>
                  <button class="submit-btn" @click="submitReview()" v-if="isReviewer && framework.ApprovedNot !== null">
                    <i class="fas fa-paper-plane"></i> Submit Review
                  </button>
                </div>
              </div>
              
              <!-- Display framework details -->
              <div v-if="framework.ExtractedData">
                <div v-for="(value, key) in framework.ExtractedData" :key="key" class="framework-detail-row">
                  <template v-if="key !== 'policies' && key !== 'framework_approval' && key !== 'type'">
                    <strong>{{ formatFieldName(key) }}:</strong> <span>{{ value }}</span>
                  </template>
                </div>
              </div>

              <!-- Policies Section -->
              <div v-if="framework.ApprovedNot === true && framework.policies && framework.policies.length > 0" class="policies-section">
                <h4>Framework Policies</h4>
                <ul class="policies-list">
                  <li v-for="policy in framework.policies" :key="policy.PolicyId" class="policy-item">
                    <span class="policy-name">{{ policy.PolicyName }}</span>
                    <span class="policy-status" :class="{
                      'status-approved': policy.Status === 'Approved',
                      'status-rejected': policy.Status === 'Rejected',
                      'status-pending': policy.Status === 'Under Review'
                    }">{{ policy.Status }}</span>
                  </li>
                </ul>
              </div>

              <!-- Rejected Framework Message -->
              <div v-if="framework.ApprovedNot === false" class="rejected-framework-message">
                <div class="rejection-note">
                  <i class="fas fa-exclamation-triangle"></i>
                  This framework has been rejected. All policies and subpolicies within this framework have been automatically rejected.
                </div>
              </div>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <!-- Rejected Frameworks List -->
    <div class="rejected-approvals-list" v-if="rejectedFrameworks.length">
      <h3>Rejected Frameworks (Edit & Resubmit)</h3>
      <ul>
        <li v-for="framework in rejectedFrameworks" :key="framework.ApprovalId">
          <div>
            <strong class="clickable" @click="openRejectedItem(framework)">
              {{ getFrameworkId(framework) }}
            </strong>
            <span class="item-type-badge framework-badge">Framework</span>
            <span class="badge rejected">Rejected</span>
            
            <!-- Show item description -->
            <div>
              - {{ framework.ExtractedData.Category || 'No Category' }}
            </div>
            
            <!-- Show rejection reason -->
            <div v-if="framework.ExtractedData?.framework_approval?.remarks" class="framework-rejection-reason">
              <strong>Rejection Reason:</strong> {{ framework.ExtractedData.framework_approval.remarks }}
            </div>
            <div v-else-if="framework.rejection_reason" class="framework-rejection-reason">
              <strong>Rejection Reason:</strong> {{ framework.rejection_reason }}
            </div>
          </div>
        </li>
      </ul>
    </div>

    <!-- Edit Modal for Rejected Framework -->
    <div v-if="showEditModal && editingFramework" class="edit-framework-modal">
      <div class="edit-framework-content">
        <h3>Edit & Resubmit Framework: {{ getFrameworkId(editingFramework) }}</h3>
        <button class="close-btn" @click="closeEditModal">Close</button>
        
        <!-- Framework fields -->
        <div>
          <label>Framework Name:</label>
          <input v-model="editingFramework.ExtractedData.FrameworkName" />
        </div>
        <div>
          <label>Framework Description:</label>
          <textarea v-model="editingFramework.ExtractedData.FrameworkDescription"></textarea>
        </div>
        <div>
          <label>Category:</label>
          <input v-model="editingFramework.ExtractedData.Category" />
        </div>
        <div>
          <label>Effective Date:</label>
          <input type="date" v-model="editingFramework.ExtractedData.EffectiveDate" />
        </div>
        <div>
          <label>Start Date:</label>
          <input type="date" v-model="editingFramework.ExtractedData.StartDate" />
        </div>
        <div>
          <label>End Date:</label>
          <input type="date" v-model="editingFramework.ExtractedData.EndDate" />
        </div>
        
        <!-- Show rejection reason -->
        <div v-if="editingFramework.ExtractedData?.framework_approval?.remarks">
          <label>Rejection Reason:</label>
          <div class="rejection-reason">{{ editingFramework.ExtractedData.framework_approval.remarks }}</div>
        </div>
        
        <button class="resubmit-btn" @click="resubmitFramework(editingFramework)">Resubmit for Review</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'FrameworkApprover',
  data() {
    return {
      approvals: [],
      selectedApproval: null,
      showDetails: false,
      showRejectModal: false,
      rejectionComment: '',
      rejectedFrameworks: [],
      showEditModal: false,
      editingFramework: null,
      userId: 2, // Default user id
      isReviewer: true, // Set based on user role, for testing
    }
  },
  mounted() {
    this.fetchFrameworks();
    this.fetchRejectedFrameworks();
  },
  methods: {
    fetchFrameworks() {
      console.log('Fetching frameworks...');
      axios.get('http://localhost:8000/api/frameworks/')
        .then(response => {
          console.log('Frameworks response:', response.data);
          this.approvals = response.data.map(framework => {
            // Get latest version for framework
            let frameworkVersion = framework.CurrentVersion?.toString() || 'u1';
            
            return {
              FrameworkId: framework.FrameworkId,
              ExtractedData: {
                type: 'framework',
                FrameworkName: framework.FrameworkName,
                CreatedByName: framework.CreatedByName,
                CreatedByDate: framework.CreatedByDate,
                Category: framework.Category,
                Status: framework.Status,
                FrameworkDescription: framework.FrameworkDescription,
                EffectiveDate: framework.EffectiveDate,
                StartDate: framework.StartDate,
                EndDate: framework.EndDate,
                Identifier: framework.Identifier,
              },
              ApprovedNot: framework.Status === 'Approved' ? true : 
                          framework.Status === 'Rejected' ? false : null,
              version: frameworkVersion
            };
          });
          console.log('Processed frameworks:', this.approvals);
        })
        .catch(error => {
          console.error('Error fetching frameworks:', error);
        });
    },
    
    openApprovalDetails(framework) {
      // If clicking the same framework, toggle the details
      if (this.selectedApproval && this.selectedApproval.FrameworkId === framework.FrameworkId) {
        this.showDetails = !this.showDetails;
        if (!this.showDetails) {
          this.selectedApproval = null;
        }
        return;
      }

      // Get the framework ID
      const frameworkId = this.getFrameworkId(framework);

      // Fetch the latest framework approval
      axios.get(`http://localhost:8000/api/framework-approvals/latest/${frameworkId}/`)
        .then(approvalResponse => {
          console.log('Latest framework approval:', approvalResponse.data);
          
          // If we got data and it has ExtractedData, use it
          if (approvalResponse.data && approvalResponse.data.ExtractedData) {
            const latestApproval = approvalResponse.data;
            
            // Create a complete approval object with the latest data
            const updatedApproval = {
              ...framework,
              ...latestApproval,
              version: latestApproval.Version || 'u1',
              ExtractedData: latestApproval.ExtractedData
            };
            
            // If framework is approved, fetch its policies
            if (updatedApproval.ApprovedNot === true) {
              axios.get(`http://localhost:8000/api/frameworks/${frameworkId}/get-policies/`)
                .then(policiesResponse => {
                  updatedApproval.policies = policiesResponse.data;
                  this.selectedApproval = updatedApproval;
                  this.showDetails = true;
                })
                .catch(policiesError => {
                  console.error('Error fetching policies:', policiesError);
                  this.selectedApproval = updatedApproval;
                  this.showDetails = true;
                });
            } else {
              this.selectedApproval = updatedApproval;
              this.showDetails = true;
            }
          } else {
            // If no approval data found, just use the framework data
            this.selectedApproval = framework;
            this.showDetails = true;
          }
        })
        .catch(error => {
          console.error('Error fetching framework approval:', error);
          // Fall back to using the framework as-is
          this.selectedApproval = framework;
          this.showDetails = true;
        });
    },
    
    refreshData() {
      this.fetchFrameworks();
      
      if (this.selectedApproval && this.selectedApproval.FrameworkId) {
        this.openApprovalDetails(this.selectedApproval);
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return ''; // Invalid date
      
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    isNewFramework(framework) {
      const createdDate = framework.ExtractedData?.CreatedByDate || framework.created_at;
      if (!createdDate) return false;
      
      const date = new Date(createdDate);
      if (isNaN(date.getTime())) return false; // Invalid date
      
      const threeDaysAgo = new Date();
      threeDaysAgo.setDate(threeDaysAgo.getDate() - 3); // Show new badge for 3 days
      
      return date > threeDaysAgo;
    },
    
    getFrameworkId(framework) {
      if (framework.FrameworkId) {
        return typeof framework.FrameworkId === 'object' ? framework.FrameworkId.FrameworkId : framework.FrameworkId;
      }
      return framework.ApprovalId;
    },
    
    approveFramework() {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for approval');
        return;
      }
      
      // Initialize framework approval if doesn't exist
      if (!this.selectedApproval.ExtractedData.framework_approval) {
        this.selectedApproval.ExtractedData.framework_approval = {};
      }
      this.selectedApproval.ExtractedData.framework_approval.approved = true;
      this.selectedApproval.ExtractedData.framework_approval.remarks = '';
      
      // Update the overall approval status
      this.selectedApproval.ApprovedNot = true;
      this.selectedApproval.ExtractedData.Status = 'Approved';
    },
    
    rejectFramework() {
      this.showRejectModal = true;
    },
    
    cancelRejection() {
      this.showRejectModal = false;
      this.rejectionComment = '';
    },
    
    confirmRejection() {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for rejection');
        this.showRejectModal = false;
        return;
      }
      
      // Initialize framework approval if doesn't exist
      if (!this.selectedApproval.ExtractedData.framework_approval) {
        this.selectedApproval.ExtractedData.framework_approval = {};
      }
      this.selectedApproval.ExtractedData.framework_approval.approved = false;
      this.selectedApproval.ExtractedData.framework_approval.remarks = this.rejectionComment;
      
      // Update the overall approval status
      this.selectedApproval.ApprovedNot = false;
      this.selectedApproval.ExtractedData.Status = 'Rejected';
      
      // Close the rejection modal
      this.showRejectModal = false;
      this.rejectionComment = '';
    },
    
    submitReview() {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for review submission');
        return;
      }
      
      const frameworkId = this.getFrameworkId(this.selectedApproval);
      
      // Create the framework review data
      const reviewData = {
        ExtractedData: JSON.parse(JSON.stringify(this.selectedApproval.ExtractedData)),
        ApprovedNot: this.selectedApproval.ApprovedNot,
        UserId: this.userId,
        ReviewerId: this.userId,
        currentVersion: this.selectedApproval.version || 'u1'
      };
      
      // Submit framework review
      axios.post(`http://localhost:8000/api/frameworks/${frameworkId}/submit-review/`, reviewData)
        .then(response => {
          console.log('Framework review submitted successfully:', response.data);
          
          // Update the local approval with the returned data
          this.selectedApproval.Version = response.data.Version;
          
          if (response.data.ApprovedDate) {
            this.selectedApproval.ApprovedDate = response.data.ApprovedDate;
          }
          
          alert(`Framework review submitted successfully! New version: ${response.data.Version}`);
          
          // Refresh the frameworks list
          this.fetchFrameworks();
        })
        .catch(error => {
          console.error('Error submitting review:', error);
          alert('Error submitting review: ' + (error.response?.data?.error || error.message));
        });
    },
    
    fetchRejectedFrameworks() {
      console.log('Fetching rejected frameworks...');
      axios.get('http://localhost:8000/api/frameworks/?status=Rejected')
        .then(response => {
          console.log('Rejected frameworks response:', response.data);
          this.rejectedFrameworks = response.data.map(framework => ({
            FrameworkId: framework.FrameworkId,
            ExtractedData: {
              type: 'framework',
              FrameworkName: framework.FrameworkName,
              CreatedByName: framework.CreatedByName,
              CreatedByDate: framework.CreatedByDate,
              Category: framework.Category,
              Status: framework.Status,
              FrameworkDescription: framework.FrameworkDescription
            },
            ApprovedNot: false
          }));
        })
        .catch(error => {
          console.error('Error fetching rejected frameworks:', error);
        });
    },
    
    openRejectedItem(framework) {
      this.editingFramework = JSON.parse(JSON.stringify(framework)); // Deep copy
      this.showEditModal = true;
    },
    
    closeEditModal() {
      this.showEditModal = false;
      this.editingFramework = null;
    },
    
    resubmitFramework(framework) {
      const frameworkId = this.getFrameworkId(framework);
      
      // Reset approval status
      if (framework.ExtractedData.framework_approval) {
        framework.ExtractedData.framework_approval.approved = null;
        framework.ExtractedData.framework_approval.remarks = '';
      }
      
      // Prepare data for resubmission
      const resubmitData = {
        FrameworkName: framework.ExtractedData.FrameworkName,
        FrameworkDescription: framework.ExtractedData.FrameworkDescription,
        Category: framework.ExtractedData.Category,
        EffectiveDate: framework.ExtractedData.EffectiveDate,
        StartDate: framework.ExtractedData.StartDate,
        EndDate: framework.ExtractedData.EndDate
      };
      
      // Submit resubmission request
      axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/resubmit/`, resubmitData)
        .then(response => {
          console.log('Framework resubmitted successfully:', response.data);
          
          // Show version information in the alert
          alert(`Framework resubmitted for review! New version: ${response.data.Version}`);
          
          this.closeEditModal();
          this.fetchRejectedFrameworks();
          this.fetchFrameworks();
        })
        .catch(error => {
          console.error('Error resubmitting framework:', error);
          alert('Error resubmitting framework: ' + (error.response?.data?.error || error.message));
        });
    },
    
    formatFieldName(field) {
      // Convert camelCase or PascalCase to display format
      return field
        // Insert space before all uppercase letters
        .replace(/([A-Z])/g, ' $1')
        // Replace first char with uppercase
        .replace(/^./, str => str.toUpperCase())
        .trim();
    }
  },
  computed: {
    pendingApprovalsCount() {
      return this.approvals.filter(a => a.ApprovedNot === null).length;
    },
    approvedApprovalsCount() {
      return this.approvals.filter(a => a.ApprovedNot === true).length;
    },
    rejectedApprovalsCount() {
      return this.approvals.filter(a => a.ApprovedNot === false).length;
    },
    sortedFrameworks() {
      return [...this.approvals].sort((a, b) => {
        const dateA = new Date(a.ExtractedData?.CreatedByDate || 0);
        const dateB = new Date(b.ExtractedData?.CreatedByDate || 0);
        return dateB - dateA; // Most recent first
      });
    }
  }
}
</script>

<style scoped>
@import './FrameworkApprover.css';
</style> 