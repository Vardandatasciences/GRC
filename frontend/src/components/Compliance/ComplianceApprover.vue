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
        <li v-for="approval in complianceApprovals" 
            :key="approval.ApprovalId"
            :class="{'new-approval': isNewApproval(approval), 'approved-item': isApproved(approval)}">
          <strong 
            :class="[
              'compliance-id-tag', 
              {'clickable': !isApproved(approval), 'approved-tag': isApproved(approval)}
            ]" 
            @click="isApproved(approval) ? showApprovedMessage(approval) : openApprovalDetails(approval)"
          >
            {{ getComplianceId(approval) }}
          </strong>
          <span class="item-type-badge compliance-badge">COMPLIANCE</span>
          <span class="date-info">
            {{ formatDate(approval.ExtractedData?.CreatedByDate || approval.created_at) }}
          </span>
          <span v-if="isNewApproval(approval)" class="new-badge">NEW</span>
          - {{ approval.ExtractedData.ComplianceItemDescription || 'No Description' }} 
          <span class="assigned-by">
            <img class="assigned-avatar" :src="approval.ExtractedData.CreatedByAvatar || 'https://randomuser.me/api/portraits/men/32.jpg'" alt="avatar" />
            {{ approval.ExtractedData.CreatedByName || 'System' }}
          </span>
          <span v-if="isApproved(approval)" class="approval-status approved">(Approved)</span>
          <span v-else-if="approval.ApprovedNot === false || approval.ExtractedData?.Status === 'Rejected'" class="approval-status rejected">(Rejected)</span>
          <span v-else class="approval-status pending">(Under Review)</span>
        </li>
      </ul>
    </div>

    <!-- Compliance Details Modal -->
    <div v-if="showDetails && selectedApproval" class="policy-details-modal">
      <div class="policy-details-content">
        <h3>
          <span class="detail-type-indicator">Compliance</span> 
          Details: <span class="compliance-id-heading">{{ getComplianceId(selectedApproval) }}</span>
        </h3>
        <button class="close-btn" @click="closeApprovalDetails">Close</button>
        
        <!-- Compliance Approval Section -->
        <div class="policy-approval-section">
          <h4>Compliance Approval</h4>
          
          <!-- Add policy status indicator -->
          <div class="policy-status-indicator">
            <span class="status-label">Status:</span>
            <span class="status-value" :class="{
              'status-approved': selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved',
              'status-rejected': selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected',
              'status-pending': selectedApproval.ApprovedNot === null || selectedApproval.ExtractedData?.Status === 'Under Review'
            }">
              {{ selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved' ? 'Approved' : 
                 selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected' ? 'Rejected' : 
                 'Under Review' }}
            </span>
          </div>
          
          <div class="policy-actions">
            <button class="submit-btn" @click="submitReview()" v-if="!isApproved(selectedApproval)">
              <i class="fas fa-paper-plane"></i> Submit Review
            </button>
          </div>
          
          <!-- Add this section to show approval status -->
          <div v-if="approvalStatus && 
                    !(selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved') && 
                    !(selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected')" 
               class="policy-approval-status">
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
          <!-- Add prominent ComplianceID display at the top -->
          <div class="compliance-id-display">
            <strong>Compliance ID:</strong> 
            <span class="compliance-id-value">{{ getComplianceId(selectedApproval) }}</span>
          </div>
          
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
          
          <!-- Show action buttons only if not already approved -->
          <div class="policy-actions" v-if="!isApproved(selectedApproval)">
            <button class="approve-btn" @click="approveCompliance()">Approve</button>
            <button class="reject-btn" @click="rejectCompliance()">Reject</button>
          </div>
          
          <!-- Show approved message if already approved -->
          <div class="approved-message" v-else>
            <div class="approved-badge">
              <i class="fas fa-check-circle"></i> This compliance has been approved
            </div>
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
            <strong class="clickable compliance-id-tag" @click="openRejectedItem(compliance)">
              {{ getComplianceId(compliance) }}
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
        <h3>Edit & Resubmit Compliance: <span class="compliance-id-heading">{{ getComplianceId(editingCompliance) }}</span></h3>
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
        // Process approvals to ensure UI reflects backend statuses
        const processedApprovals = response.data.map(approval => {
          // Check status from backend and sync with frontend
          if (approval.ExtractedData?.Status === 'Approved' && approval.ApprovedNot !== true) {
            approval.ApprovedNot = true;
            approval.isAlreadyApproved = true;
          } else if (approval.ExtractedData?.Status === 'Rejected' && approval.ApprovedNot !== false) {
            approval.ApprovedNot = false;
          }
          return approval;
        });
        
        this.approvals = processedApprovals;
      })
      .catch(error => {
        console.error('Error fetching approvals:', error);
      });
    this.fetchRejectedCompliances();
  },
  methods: {
    openApprovalDetails(approval) {
      this.selectedApproval = approval;
      
      // Check if already approved directly or via status field
      const isApproved = approval.ApprovedNot === true || 
                        approval.ExtractedData?.Status === 'Approved' || 
                        approval.ExtractedData?.status === 'approved';
                        
      // If already approved, show alert and update UI to reflect approved status
      if (isApproved) {
        // Update the local status to ensure UI consistency
        approval.ApprovedNot = true;
        approval.ExtractedData.Status = 'Approved';
        
        // Set this flag to control action buttons display
        approval.isAlreadyApproved = true;
      }
      
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
      
      // Set status explicitly in ExtractedData in multiple formats for the backend
      this.selectedApproval.ExtractedData.Status = 'Rejected';
      this.selectedApproval.ExtractedData.status = 'Rejected';
      
      // Make sure ComplianceId is included in the ExtractedData in multiple formats
      const complianceId = this.getComplianceId(this.selectedApproval);
      if (complianceId && complianceId !== 'N/A' && !complianceId.startsWith('Approval-')) {
        // Set the ID in multiple formats to improve chances of successful backend processing
        this.selectedApproval.ExtractedData.ComplianceId = complianceId;
        this.selectedApproval.ExtractedData.compliance_id = complianceId;
        this.selectedApproval.ExtractedData.Identifier = complianceId;
      }
      
      // Update the overall approval status
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
          // Process the data to ensure UI reflects backend statuses correctly
          data.forEach(approval => {
            // Check if the backend has a status set but local doesn't reflect it
            if (approval.ExtractedData?.Status === 'Approved' && approval.ApprovedNot !== true) {
              approval.ApprovedNot = true;
              approval.isAlreadyApproved = true;
            } else if (approval.ExtractedData?.Status === 'Rejected' && approval.ApprovedNot !== false) {
              approval.ApprovedNot = false;
            }
          });
          
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
      
      // Make sure ComplianceId is included in the ExtractedData in multiple formats to ensure the backend can find it
      const complianceId = this.getComplianceId(this.selectedApproval);
      if (complianceId && complianceId !== 'N/A' && !complianceId.startsWith('Approval-')) {
        // Set the ID in multiple formats to improve chances of successful backend processing
        reviewData.ExtractedData.ComplianceId = complianceId;
        reviewData.ExtractedData.compliance_id = complianceId;
        reviewData.ExtractedData.Identifier = complianceId;
        
        // For debug purposes
        console.log(`Setting ComplianceId in multiple formats: ${complianceId}`);
      }
      
      // Make sure Status is explicitly set
      if (this.selectedApproval.ApprovedNot === true) {
        reviewData.ExtractedData.Status = 'Approved';
      } else if (this.selectedApproval.ApprovedNot === false) {
        reviewData.ExtractedData.Status = 'Rejected';
      }
      
      // Store a local copy of the approval ID before the request
      const approvalId = this.selectedApproval.ApprovalId;
      
      console.log('Sending review data:', reviewData);
      
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
      
      // Make sure ComplianceId is included in the ExtractedData in multiple formats
      const complianceId = this.getComplianceId(this.selectedApproval);
      if (complianceId && complianceId !== 'N/A' && !complianceId.startsWith('Approval-')) {
        // Set the ID in multiple formats to improve chances of successful backend processing
        this.selectedApproval.ExtractedData.ComplianceId = complianceId;
        this.selectedApproval.ExtractedData.compliance_id = complianceId;
        this.selectedApproval.ExtractedData.Identifier = complianceId;
        
        console.log(`Setting ComplianceId in multiple formats: ${complianceId}`);
      }
      
      // Include the compliance data explicitly in the ExtractedData
      this.selectedApproval.ExtractedData.Status = 'Approved';
      
      // Update the overall approval status
      this.selectedApproval.ApprovedNot = true;
      
      // Submit the review immediately
      this.submitReview();
    },
    rejectCompliance() {
      // Make sure ComplianceId is included in the ExtractedData in multiple formats
      const complianceId = this.getComplianceId(this.selectedApproval);
      if (complianceId && complianceId !== 'N/A' && !complianceId.startsWith('Approval-')) {
        // Set the ID in multiple formats to improve chances of successful backend processing
        this.selectedApproval.ExtractedData.ComplianceId = complianceId;
        this.selectedApproval.ExtractedData.compliance_id = complianceId;
        this.selectedApproval.ExtractedData.Identifier = complianceId;
        
        console.log(`Setting ComplianceId in multiple formats: ${complianceId}`);
      }
      
      // Open rejection modal
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
    },
    getComplianceId(compliance) {
      // If we don't have a compliance object, return N/A
      if (!compliance) return 'N/A';
      
      // Try to get it from the compliance record directly
      if (compliance.ComplianceId) {
        return typeof compliance.ComplianceId === 'object' ? compliance.ComplianceId.ComplianceId : compliance.ComplianceId;
      }
      
      // Check in ExtractedData with high priority fields first
      if (compliance.ExtractedData) {
        // Look for explicit ComplianceId field first
        if (compliance.ExtractedData.ComplianceId) {
          return compliance.ExtractedData.ComplianceId;
        }
        
        // Look for compliance_id field
        if (compliance.ExtractedData.compliance_id) {
          return compliance.ExtractedData.compliance_id;
        }
        
        // Check if there's a compliance object with an ID
        if (compliance.ExtractedData.compliance && compliance.ExtractedData.compliance.ComplianceId) {
          return compliance.ExtractedData.compliance.ComplianceId;
        }
        
        // Also check if it's in the identifier field
        if (compliance.ExtractedData.Identifier) {
          return compliance.ExtractedData.Identifier;
        }
      }
      
      // Check in identifiers outside ExtractedData
      if (compliance.Identifier) {
        return compliance.Identifier;
      }
      
      // Check common property names for ID
      if (typeof compliance === 'object') {
        const possibleKeys = ['identifier', 'ID', 'id', 'complianceId', 'compliance_id', 'complianceid', 'compliance_ID'];
        for (const key of possibleKeys) {
          if (compliance[key]) {
            return compliance[key];
          }
        }
      }
      
      // Finally, if we can't find it, use the approval ID
      return compliance.ApprovalId ? `Approval-${compliance.ApprovalId}` : 'N/A';
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
    isNewApproval(approval) {
      const createdDate = approval.ExtractedData?.CreatedByDate || approval.created_at;
      if (!createdDate) return false;
      
      const date = new Date(createdDate);
      if (isNaN(date.getTime())) return false; // Invalid date
      
      const threeDaysAgo = new Date();
      threeDaysAgo.setDate(threeDaysAgo.getDate() - 3); // Show new badge for 3 days
      
      return date > threeDaysAgo;
    },
    isApproved(approval) {
      if (!approval) return false;
      
      return approval.ApprovedNot === true || 
             approval.ExtractedData?.Status === 'Approved' || 
             approval.ExtractedData?.status === 'approved' ||
             approval.isAlreadyApproved === true;
    },
    showApprovedMessage(approval) {
      const complianceId = this.getComplianceId(approval);
      alert(`Compliance ${complianceId} has already been approved and cannot be modified.`);
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

/* Additional styles */
.new-badge {
  background-color: #f97316;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
  font-weight: bold;
}

.date-info {
  color: #6b7280;
  font-size: 12px;
  margin-left: 8px;
  margin-right: 8px;
}

.item-type-badge.compliance-badge {
  background-color: #10b981;
}

.compliance-detail-row {
  margin-bottom: 10px;
  display: flex;
}

.compliance-detail-row strong {
  min-width: 120px;
  font-weight: 600;
  color: #4b5563;
}

.compliance-detail-row span {
  flex: 1;
}

.new-approval {
  border-left: 4px solid #f97316;
  animation: pulse-border 2s infinite;
}

@keyframes pulse-border {
  0% { border-left-color: #f97316; }
  50% { border-left-color: #fdba74; }
  100% { border-left-color: #f97316; }
}

.policy-status-indicator {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.status-value.status-approved {
  background-color: #10b981;
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
}

.status-value.status-rejected {
  background-color: #ef4444;
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
}

.status-value.status-pending {
  background-color: #f59e0b;
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
}

.policy-detail-row {
  margin: 15px 0;
  padding: 10px;
  background-color: #f9fafb;
  border-radius: 8px;
  display: flex;
}

.policy-detail-row strong {
  min-width: 120px;
  font-weight: 600;
  color: #4b5563;
}

.approval-status.pending {
  background-color: #f59e0b;
  color: white;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 600;
}

.approval-status.approved {
  background-color: #10b981;
  color: white;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 600;
}

.approval-status.rejected {
  background-color: #ef4444;
  color: white;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 600;
}

/* New styles for ComplianceID display */
.compliance-id-display {
  background-color: #f0f9ff;
  border: 2px solid #0ea5e9;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.compliance-id-display strong {
  font-size: 16px;
  color: #0369a1;
  margin-right: 12px;
}

.compliance-id-value {
  font-size: 18px;
  font-weight: 700;
  color: #0c4a6e;
  background-color: #e0f2fe;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid #7dd3fc;
}

/* Style for ComplianceID in list view */
.compliance-id-tag {
  color: #0c4a6e;
  background-color: #e0f2fe;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #7dd3fc;
  display: inline-block;
  font-size: 14px;
  margin-right: 8px;
}

.compliance-id-heading {
  color: #0c4a6e;
  background-color: #e0f2fe;
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid #7dd3fc;
  font-weight: 700;
}

/* Approved message styling */
.approved-message {
  margin: 15px 0;
  padding: 15px;
  text-align: center;
}

.approved-badge {
  display: inline-block;
  background-color: #10b981;
  color: white;
  padding: 10px 15px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.approved-badge i {
  margin-right: 8px;
}

/* Approved item styling */
.approved-item {
  background-color: rgba(16, 185, 129, 0.05);
  border-left: 4px solid #10b981 !important;
}

.approved-tag {
  cursor: default;
  position: relative;
  color: #047857;
}

.approved-tag::after {
  content: "✓";
  margin-left: 4px;
  font-weight: bold;
  color: #10b981;
}
</style>
