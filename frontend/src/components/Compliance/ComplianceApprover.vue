<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Compliance Approver</h2>
      <div class="dashboard-actions">
        <button class="action-btn" @click="refreshData" :disabled="isLoading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
        </button>
        <button class="action-btn"><i class="fas fa-download"></i></button>
      </div>
    </div>

    <!-- Error message -->
    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="refreshData" class="retry-btn">Retry</button>
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

    <!-- Loading state -->
    <div v-if="isLoading && !approvals.length" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i> Loading approvals...
    </div>

    <!-- No data state -->
    <div v-else-if="!isLoading && complianceApprovals.length === 0" class="no-data-state">
      <i class="fas fa-inbox"></i>
      <p>No pending approvals found.</p>
      <small>Any compliance items with "Under Review" status will appear here.</small>
    </div>

    <!-- Compliance Approvals List -->
    <div v-else class="approvals-list">
      <h3>My Approval Tasks</h3>
      <ul>
        <li v-for="approval in complianceApprovals" :key="approval.ApprovalId">
          <strong class="clickable" @click="openApprovalDetails(approval)">
            {{ approval.Identifier }}
          </strong>
          <span class="item-type-badge compliance-badge">Compliance</span>
          <div class="approval-details">
            <p class="description">{{ approval.ExtractedData.ComplianceItemDescription || 'No Description' }}</p>
            <div class="meta-info">
              <span class="criticality" :class="approval.ExtractedData.Criticality?.toLowerCase()">
                {{ approval.ExtractedData.Criticality || 'N/A' }}
              </span>
              <span class="created-by">
                <i class="fas fa-user"></i>
                {{ approval.ExtractedData.CreatedByName || 'System' }}
              </span>
              <span class="version">v{{ approval.ExtractedData.ComplianceVersion || '1.0' }}</span>
            </div>
          </div>
          <span class="approval-status pending">(Pending Review)</span>
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
            
            <!-- Add approval date display -->
            <div v-if="selectedApproval.ApprovedDate" class="approval-date">
              <div class="date-label">Approved on:</div>
              <div class="date-value">{{ formatDate(selectedApproval.ApprovedDate) }}</div>
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
import { complianceService } from '@/services/api';

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
      isLoading: false,
      error: null,
      counts: {
        pending: 0,
        approved: 0,
        rejected: 0
      },
      refreshInterval: null
    }
  },
  async mounted() {
    console.log('ComplianceApprover mounted');
    await this.refreshData();
    // Set up auto-refresh every 30 seconds
    this.refreshInterval = setInterval(() => {
      this.refreshData();
    }, 30000);
  },
  beforeUnmount() {
    // Clear the refresh interval when component is destroyed
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  methods: {
    async refreshData() {
      if (this.isLoading) return; // Prevent multiple simultaneous refreshes
      
      this.isLoading = true;
      this.error = null;
      console.log('Refreshing data...');
      
      try {
        // Fetch approvals with reviewer_id
        const approvalsResponse = await complianceService.getPolicyApprovals({ 
          reviewer_id: this.userId 
        });
        console.log('Approvals response:', approvalsResponse);

        if (approvalsResponse.data.success) {
          // Ensure ExtractedData is properly formatted
          this.approvals = (approvalsResponse.data.data || []).map(approval => ({
            ...approval,
            ExtractedData: {
              ...approval.ExtractedData,
              type: approval.ExtractedData?.type || 'compliance',
              compliance_approval: approval.ExtractedData?.compliance_approval || {
                approved: null,
                remarks: ''
              }
            }
          }));
          
          this.counts = approvalsResponse.data.counts || {
            pending: 0,
            approved: 0,
            rejected: 0
          };
          console.log('Updated approvals:', this.approvals);
          console.log('Updated counts:', this.counts);
        } else {
          throw new Error(approvalsResponse.data.message || 'Failed to fetch approvals');
        }

        // Fetch rejected compliances
        const rejectedResponse = await complianceService.getRejectedApprovals(this.userId);
        console.log('Rejected compliances response:', rejectedResponse);

        if (rejectedResponse.data) {
          const complianceItems = rejectedResponse.data.filter(item => 
            item.ExtractedData?.type === 'compliance'
          );
          
          // Get unique latest versions
          const uniqueCompliances = [];
          const identifiers = new Set();
          
          complianceItems
            .sort((a, b) => b.ApprovalId - a.ApprovalId)
            .forEach(compliance => {
              if (!identifiers.has(compliance.Identifier)) {
                identifiers.add(compliance.Identifier);
                uniqueCompliances.push(compliance);
              }
            });
          
          this.rejectedCompliances = uniqueCompliances;
          console.log('Updated rejected compliances:', this.rejectedCompliances);
        }
        
      } catch (error) {
        console.error('Error refreshing data:', error);
        this.error = error.response?.data?.message || error.message || 'Failed to load approvals';
      } finally {
        this.isLoading = false;
      }
    },
    
    openApprovalDetails(approval) {
      console.log('Opening approval details:', approval);
      this.selectedApproval = approval;
      this.showDetails = true;
    },
    
    closeApprovalDetails() {
      this.selectedApproval = null;
      this.showDetails = false;
    },
    
    async submitReview() {
      if (!this.selectedApproval) return;
      
      try {
        const reviewData = {
          ExtractedData: JSON.parse(JSON.stringify(this.selectedApproval.ExtractedData)),
          ApprovedNot: this.selectedApproval.ApprovedNot
        };
        
        const response = await complianceService.submitComplianceReview(
          this.selectedApproval.ApprovalId, 
          reviewData
        );
        
        console.log('Review submitted:', response.data);
        alert('Compliance review submitted successfully!');
        
        this.closeApprovalDetails();
        await this.refreshData();
        
      } catch (error) {
        console.error('Error submitting review:', error);
        alert('Error submitting review: ' + (error.response?.data?.message || error.message));
      }
    },
    
    async approveCompliance() {
      if (!this.selectedApproval) return;
      
      try {
        // Initialize compliance approval if doesn't exist
        if (!this.selectedApproval.ExtractedData.compliance_approval) {
          this.selectedApproval.ExtractedData.compliance_approval = {};
        }
        this.selectedApproval.ExtractedData.compliance_approval.approved = true;
        this.selectedApproval.ExtractedData.compliance_approval.remarks = '';
        
        // Update the overall approval status
        this.selectedApproval.ApprovedNot = true;
        
        await this.submitReview();
      } catch (error) {
        console.error('Error approving compliance:', error);
        alert('Error approving compliance: ' + error.message);
      }
    },
    
    rejectCompliance() {
      this.showRejectModal = true;
    },
    
    async confirmRejection() {
      if (!this.rejectionComment.trim()) {
        alert('Please provide a reason for rejection');
        return;
      }
      
      try {
        if (!this.selectedApproval.ExtractedData.compliance_approval) {
          this.selectedApproval.ExtractedData.compliance_approval = {};
        }
        this.selectedApproval.ExtractedData.compliance_approval.approved = false;
        this.selectedApproval.ExtractedData.compliance_approval.remarks = this.rejectionComment;
        this.selectedApproval.ApprovedNot = false;
        
        await this.submitReview();
        
        this.showRejectModal = false;
        this.rejectionComment = '';
      } catch (error) {
        console.error('Error rejecting compliance:', error);
        alert('Error rejecting compliance: ' + error.message);
      }
    },
    
    cancelRejection() {
      this.showRejectModal = false;
      this.rejectionComment = '';
    },
    
    openRejectedItem(item) {
      console.log('Opening rejected item:', item);
      this.editingCompliance = JSON.parse(JSON.stringify(item));
      this.showEditComplianceModal = true;
    },
    
    closeEditComplianceModal() {
      this.showEditComplianceModal = false;
      this.editingCompliance = null;
    },
    
    async resubmitCompliance(compliance) {
      try {
        // Reset approval status
        if (compliance.ExtractedData.compliance_approval) {
          compliance.ExtractedData.compliance_approval.approved = null;
          compliance.ExtractedData.compliance_approval.remarks = '';
        }
        
        await complianceService.resubmitComplianceApproval(
          compliance.ApprovalId, 
          { ExtractedData: compliance.ExtractedData }
        );
        
        alert('Compliance resubmitted for review!');
        this.showEditComplianceModal = false;
        await this.refreshData();
      } catch (error) {
        console.error('Error resubmitting compliance:', error);
        alert('Error resubmitting compliance: ' + error.message);
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString();
    }
  },
  computed: {
    pendingApprovalsCount() {
      return this.counts.pending || 0;
    },
    approvedApprovalsCount() {
      return this.counts.approved || 0;
    },
    rejectedApprovalsCount() {
      return this.counts.rejected || 0;
    },
    complianceApprovals() {
      return this.approvals.filter(approval => 
        approval.ExtractedData?.type === 'compliance' && 
        approval.ApprovedNot === null
      );
    },
    approvalStatus() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData) return null;
      return this.selectedApproval.ExtractedData.compliance_approval || { approved: null, remarks: '' };
    }
  }
}
</script>

<style scoped>
.error-message {
  background-color: #fee;
  color: #c00;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 4px;
  border: 1px solid #fcc;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.retry-btn {
  background: #c00;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.no-data-state {
  text-align: center;
  padding: 2rem;
  color: #666;
  background: #f9f9f9;
  border-radius: 4px;
  margin: 1rem 0;
}

.no-data-state i {
  font-size: 2rem;
  color: #999;
  margin-bottom: 1rem;
}

.approval-details {
  margin: 0.5rem 0;
}

.description {
  margin: 0.5rem 0;
  color: #666;
}

.meta-info {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.criticality {
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
  font-weight: 500;
}

.criticality.high {
  background: #fee;
  color: #c00;
}

.criticality.medium {
  background: #ffd;
  color: #960;
}

.criticality.low {
  background: #efe;
  color: #060;
}

.created-by {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.version {
  color: #999;
}

@import './ComplianceApprover.css';
</style>
