<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Compliance Approver</h2>
      <div class="dashboard-actions">
        <button class="action-btn" @click="refreshData"><i class="fas fa-sync-alt"></i></button>
        <button class="action-btn"><i class="fas fa-download"></i></button>
      </div>
    </div>

    <!-- Performance Summary Cards -->
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

    <!-- Compliance Approvals List -->
    <div class="approvals-list">
      <h3>My Approval Tasks</h3>
      <ul>
        <li v-for="approval in complianceApprovals" :key="approval.ApprovalId">
          <strong class="clickable" @click="openApprovalDetails(approval)">
            {{ approval.Identifier }}
          </strong>
          <span class="item-type-badge compliance-badge">Compliance</span>
          - {{ approval.ExtractedData.ComplianceItemDescription || 'No Scope' }} 
          <span class="assigned-by">
            <img class="assigned-avatar" src="https://randomuser.me/api/portraits/men/32.jpg" alt="avatar" />
            {{ approval.ExtractedData.CreatedByName || 'System' }}
          </span>
          <span v-if="approval.ApprovedNot === null" class="approval-status pending">(Pending)</span>
          <span v-else-if="approval.ApprovedNot === true" class="approval-status approved">(Approved)</span>
          <span v-else class="approval-status rejected">(Rejected)</span>
        </li>
      </ul>
    </div>

    <!-- Compliance Details Modal -->
    <div v-if="showDetails && selectedApproval" class="policy-details-modal">
      <div class="policy-details-content">
        <h3>
          <span class="detail-type-indicator">Compliance</span> 
          Details: {{ selectedApproval.Identifier }}
        </h3>
        <button class="close-btn" @click="closeApprovalDetails">Close</button>
        
        <!-- Compliance Approval Section -->
        <div class="policy-approval-section">
          <h4>Compliance Approval</h4>
          <div class="policy-actions">
            <button class="submit-btn" @click="submitReview()">
              <i class="fas fa-paper-plane"></i> Submit Review
            </button>
          </div>
          
          <!-- Add this section to show approval status -->
          <div v-if="approvalStatus" class="policy-approval-status">
            <div class="status-container">
              <div class="status-label">Status:</div>
              <div class="status-value" :class="{
                'approved': approvalStatus.approved === true,
                'rejected': approvalStatus.approved === false,
                'pending': approvalStatus.approved === null
              }">
                {{ approvalStatus.approved === true ? 'Approved' : 
                   approvalStatus.approved === false ? 'Rejected' : 'Pending' }}
              </div>
            </div>
            
            <!-- Show remarks if rejected -->
            <div v-if="approvalStatus.approved === false && 
                      approvalStatus.remarks" class="policy-rejection-remarks">
              <div class="remarks-label">Rejection Reason:</div>
              <div class="remarks-value">{{ approvalStatus.remarks }}</div>
            </div>
          </div>
        </div>
        
        <!-- Display compliance details -->
        <div v-if="selectedApproval.ExtractedData" class="compliance-details">
          <div class="compliance-detail-row">
            <strong>Description:</strong> <span>{{ selectedApproval.ExtractedData.ComplianceItemDescription }}</span>
          </div>
          <div class="compliance-detail-row">
            <strong>Criticality:</strong> <span>{{ selectedApproval.ExtractedData.Criticality }}</span>
          </div>
          <div class="compliance-detail-row">
            <strong>Impact:</strong> <span>{{ selectedApproval.ExtractedData.Impact }}</span>
          </div>
          <div class="compliance-detail-row">
            <strong>Probability:</strong> <span>{{ selectedApproval.ExtractedData.Probability }}</span>
          </div>
          <div class="compliance-detail-row">
            <strong>Mitigation:</strong> <span>{{ selectedApproval.ExtractedData.mitigation }}</span>
          </div>
          <div class="policy-actions">
            <button class="approve-btn" @click="approveCompliance()">Approve</button>
            <button class="reject-btn" @click="rejectCompliance()">Reject</button>
          </div>
        </div>
      </div>
      
      <!-- Rejection Modal -->
      <div v-if="showRejectModal" class="reject-modal">
        <div class="reject-modal-content">
          <h4>Rejection Reason</h4>
          <p>Please provide a reason for rejecting the compliance item</p>
          <textarea 
            v-model="rejectionComment" 
            class="rejection-comment" 
            placeholder="Enter your comments here..."></textarea>
          <div class="reject-modal-actions">
            <button class="cancel-btn" @click="cancelRejection">Cancel</button>
            <button class="confirm-btn" @click="confirmRejection">Confirm Rejection</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Rejected Compliances List -->
    <div class="rejected-approvals-list" v-if="rejectedCompliances.length">
      <h3>Rejected Compliances (Edit & Resubmit)</h3>
      <ul>
        <li v-for="compliance in rejectedCompliances" :key="compliance.ApprovalId">
          <div>
            <strong class="clickable" @click="openRejectedItem(compliance)">
              {{ compliance.Identifier }}
            </strong>
            <span class="item-type-badge compliance-badge">Compliance</span>
            <span class="badge rejected">Rejected</span>
            
            <!-- Show item description -->
            <div>
              - {{ compliance.ExtractedData.ComplianceItemDescription || 'No Description' }}
              <div v-if="compliance.rejection_reason">
                <strong>Reason:</strong> {{ compliance.rejection_reason }}
              </div>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <!-- Edit Modal for Rejected Compliance -->
    <div v-if="showEditComplianceModal && editingCompliance" class="edit-policy-modal">
      <div class="edit-policy-content">
        <h3>Edit & Resubmit Compliance: {{ editingCompliance.Identifier }}</h3>
        <button class="close-btn" @click="closeEditComplianceModal">Close</button>
        
        <!-- Compliance fields -->
        <div>
          <label>Description:</label>
          <input v-model="editingCompliance.ExtractedData.ComplianceItemDescription" />
        </div>
        <div>
          <label>Criticality:</label>
          <select v-model="editingCompliance.ExtractedData.Criticality">
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </div>
        <div>
          <label>Impact:</label>
          <input v-model="editingCompliance.ExtractedData.Impact" />
        </div>
        <div>
          <label>Probability:</label>
          <input v-model="editingCompliance.ExtractedData.Probability" />
        </div>
        <div>
          <label>Mitigation:</label>
          <textarea v-model="editingCompliance.ExtractedData.mitigation"></textarea>
        </div>
        <!-- Show rejection reason -->
        <div>
          <label>Rejection Reason:</label>
          <div class="rejection-reason">{{ editingCompliance.ExtractedData.compliance_approval?.remarks }}</div>
        </div>
        
        <button class="resubmit-btn" @click="resubmitCompliance(editingCompliance)">Resubmit for Review</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ComplianceApprover',
  data() {
    return {
      approvals: [],
      selectedApproval: null,
      showDetails: false,
      showRejectModal: false,
      rejectionComment: '',
      rejectedCompliances: [],
      showEditComplianceModal: false,
      editingCompliance: null,
      userId: 2, // Default user id
    }
  },
  mounted() {
    // Fetch approvals for reviewer (hardcoded as 2)
    axios.get('http://localhost:8000/api/policy-approvals/reviewer/')
      .then(response => {
        this.approvals = response.data;
      })
      .catch(error => {
        console.error('Error fetching approvals:', error);
      });
    this.fetchRejectedCompliances();
  },
  methods: {
    openApprovalDetails(approval) {
      this.selectedApproval = approval;
      this.showDetails = true;
    },
    closeApprovalDetails() {
      this.selectedApproval = null;
      this.showDetails = false;
    },
    cancelRejection() {
      this.showRejectModal = false;
      this.rejectionComment = '';
    },
    confirmRejection() {
      if (!this.rejectionComment.trim()) {
        alert('Please provide a reason for rejection');
        return;
      }
      
      // Handle compliance rejection
      if (!this.selectedApproval.ExtractedData.compliance_approval) {
        this.selectedApproval.ExtractedData.compliance_approval = {};
      }
      this.selectedApproval.ExtractedData.compliance_approval.approved = false;
      this.selectedApproval.ExtractedData.compliance_approval.remarks = this.rejectionComment;
      this.selectedApproval.ApprovedNot = false;
      
      // Close the rejection modal
      this.showRejectModal = false;
      this.rejectionComment = '';
      
      // Important: Submit the review immediately to save changes
      this.submitReview();
    },
    refreshData() {
      // Show loading indicator or feedback if desired
      this.refreshApprovals();
      this.fetchRejectedCompliances();
    },
    refreshApprovals() {
      axios.get('http://localhost:8000/api/policy-approvals/reviewer/')
        .then(({ data }) => {
          this.approvals = data;
        })
        .catch(error => {
          console.error('Error fetching approvals:', error);
        });
    },
    fetchRejectedCompliances() {
      // Use the hardcoded user ID 2 for reviewer
      const reviewerId = 2;
      
      axios.get(`http://localhost:8000/api/policy-approvals/rejected/${reviewerId}/`)
        .then(response => {
          // Filter for compliance items only
          const complianceItems = response.data.filter(item => item.ExtractedData?.type === 'compliance');
          
          // Get unique compliance items by Identifier
          const uniqueCompliances = [];
          const identifiers = new Set();
          
          // Sort by ApprovalId (descending) to get the most recent first
          const sortedCompliances = complianceItems.sort((a, b) => b.ApprovalId - a.ApprovalId);
          
          // Take only the most recent version of each compliance
          sortedCompliances.forEach(compliance => {
            if (!identifiers.has(compliance.Identifier)) {
              identifiers.add(compliance.Identifier);
              uniqueCompliances.push(compliance);
            }
          });
          
          this.rejectedCompliances = uniqueCompliances;
        })
        .catch(error => {
          console.error('Error fetching rejected compliances:', error);
        });
    },
    submitReview() {
      // For compliance reviews
      const reviewData = {
        ExtractedData: JSON.parse(JSON.stringify(this.selectedApproval.ExtractedData)),
        ApprovedNot: this.selectedApproval.ApprovedNot
      };
      
      // Store a local copy of the approval ID before the request
      const approvalId = this.selectedApproval.ApprovalId;
      
      axios.put(
        `http://localhost:8000/api/compliance-approvals/${approvalId}/review/`,
        reviewData
      )
      .then(response => {
        console.log('Response:', response.data);
        alert('Compliance review submitted successfully!');
        
        // First close the details view
        this.closeApprovalDetails();
        
        // Then refresh the approvals list to update the UI
        this.refreshApprovals();
        
        // Force reload the page to ensure everything is updated
        setTimeout(() => {
          window.location.reload();
        }, 500);
      })
      .catch(error => {
        console.error('Error submitting review:', error);
        alert('Error submitting review: ' + (error.response?.data?.error || error.message));
      });
    },
    approveCompliance() {
      // Initialize compliance approval if doesn't exist
      if (!this.selectedApproval.ExtractedData.compliance_approval) {
        this.selectedApproval.ExtractedData.compliance_approval = {};
      }
      this.selectedApproval.ExtractedData.compliance_approval.approved = true;
      this.selectedApproval.ExtractedData.compliance_approval.remarks = '';
      
      // Update the overall approval status
      this.selectedApproval.ApprovedNot = true;
    },
    rejectCompliance() {
      this.showRejectModal = true;
    },
    openRejectedItem(item) {
      this.editingCompliance = JSON.parse(JSON.stringify(item)); // Deep copy
      this.showEditComplianceModal = true;
    },
    closeEditComplianceModal() {
      this.showEditComplianceModal = false;
      this.editingCompliance = null;
    },
    resubmitCompliance(compliance) {
      // Reset approval status
      if (compliance.ExtractedData.compliance_approval) {
        compliance.ExtractedData.compliance_approval.approved = null;
        compliance.ExtractedData.compliance_approval.remarks = '';
      }
      
      axios.put(`http://localhost:8000/api/compliance-approvals/resubmit/${compliance.ApprovalId}/`, {
        ExtractedData: compliance.ExtractedData
      })
      .then(() => {
        alert('Compliance resubmitted for review!');
        this.showEditComplianceModal = false;
        this.fetchRejectedCompliances();
        // Force reload to update UI
        setTimeout(() => {
          window.location.reload();
        }, 500);
      })
      .catch(error => {
        alert('Error resubmitting compliance');
        console.error(error);
      });
    }
  },
  computed: {
    complianceApprovals() {
      // Only show compliance items
      return this.approvals.filter(approval => approval.ExtractedData?.type === 'compliance');
    },
    pendingApprovalsCount() {
      return this.complianceApprovals.filter(a => a.ApprovedNot === null).length;
    },
    approvedApprovalsCount() {
      return this.complianceApprovals.filter(a => a.ApprovedNot === true).length;
    },
    rejectedApprovalsCount() {
      return this.complianceApprovals.filter(a => a.ApprovedNot === false).length;
    },
    approvalStatus() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData) return null;
      return this.selectedApproval.ExtractedData.compliance_approval || { approved: null, remarks: '' };
    }
  }
}
</script>

<style scoped>
@import '../Policy/PolicyApprover.css';
</style>
