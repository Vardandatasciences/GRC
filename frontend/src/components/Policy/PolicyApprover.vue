<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Policy Approver</h2>
      <div class="dashboard-actions">
        <button class="action-btn" @click="refreshData"><i class="fas fa-sync-alt"></i></button>
        <button class="action-btn"><i class="fas fa-download"></i></button>
        
      </div>
    </div>

    <!-- Performance Summary Cards for Policy Approver -->
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

    <!-- Add this after the performance-summary div -->
    <div class="approvals-list">
      <h3>My Approval Tasks</h3>
      <ul>
        <li v-for="approval in policyApprovals" :key="approval.ApprovalId">
          <strong class="clickable" @click="openApprovalDetails(approval)">
            {{ approval.Identifier }}
          </strong>
          <span class="item-type-badge" :class="{
            'policy-badge': !approval.ExtractedData.type || approval.ExtractedData.type === 'policy',
            'subpolicy-badge': approval.ExtractedData.type === 'subpolicy'
          }">
            {{ approval.ExtractedData.type === 'subpolicy' ? 'Subpolicy' : 'Policy' }}
          </span>
          - {{ approval.ExtractedData.Scope || 'No Scope' }} 
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

    <!-- Policy/Compliance Details Modal/Section -->
    <div v-if="showDetails && selectedApproval" class="policy-details-modal">
      <div class="policy-details-content">
        <h3>
          <span class="detail-type-indicator">
            {{ isComplianceApproval ? 'Compliance' : 'Policy' }}
          </span> 
          Details: {{ selectedApproval.Identifier }}
        </h3>
        <button class="close-btn" @click="closeApprovalDetails">Close</button>
        
        <!-- Policy/Compliance Approval Section -->
        <div class="policy-approval-section">
          <h4>{{ isComplianceApproval ? 'Compliance' : 'Policy' }} Approval</h4>
          <div class="policy-actions">
            <button class="submit-btn" @click="submitReview()" :disabled="isComplianceApproval ? false : hasUnreviewedSubpolicies">
              <i class="fas fa-paper-plane"></i> Submit Review
            </button>
          </div>
          
          <!-- Add this section to show policy approval status -->
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
        
        <!-- Display details based on type -->
        <div v-if="selectedApproval.ExtractedData">
          <!-- For compliance approvals -->
          <div v-if="isComplianceApproval" class="compliance-details">
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
          
          <!-- For policy approvals (existing code) -->
          <div v-else v-for="(value, key) in selectedApproval.ExtractedData" :key="key" class="policy-detail-row">
            <template v-if="key !== 'subpolicies' && key !== 'policy_approval'">
              <strong>{{ key }}:</strong> <span>{{ value }}</span>
            </template>
            
            <!-- Subpolicies Section -->
            <template v-if="key === 'subpolicies' && Array.isArray(value)">
              <h4>Subpolicies</h4>
              <ul v-if="value && value.length">
                <li v-for="sub in value" :key="sub.Identifier" class="subpolicy-status">
                  <div>
                    <span class="subpolicy-id">{{ sub.Identifier }}</span> :
                    <span class="subpolicy-name">{{ sub.SubPolicyName }}</span>
                    <span class="item-type-badge subpolicy-badge">Subpolicy</span>
                    <span
                      class="badge"
                      :class="{
                        approved: sub.approval?.approved === true,
                        rejected: sub.approval?.approved === false,
                        pending: sub.approval?.approved === null && !sub.resubmitted,
                        resubmitted: sub.approval?.approved === null && sub.resubmitted
                      }"
                    >
                      {{
                        sub.approval?.approved === true
                          ? 'Approved'
                          : sub.approval?.approved === false
                          ? 'Rejected'
                          : sub.resubmitted
                          ? 'Resubmitted'
                          : 'Pending'
                      }}
                    </span>
                  </div>
                  <div><strong>Description:</strong> {{ sub.Description }}</div>
                  <div><strong>Control:</strong> {{ sub.Control }}</div>
                  <div v-if="sub.approval?.approved === false">
                    <strong>Reason:</strong> {{ sub.approval?.remarks }}
                  </div>
                  <!-- Approve/Reject buttons for pending subpolicies -->
                  <div v-if="(sub.approval?.approved === null || sub.approval?.approved === undefined) && (isReviewer || !sub.resubmitted)" class="subpolicy-actions">
                    <button class="approve-btn" @click="approveSubpolicy(sub)">Approve</button>
                    <button class="reject-btn" @click="rejectSubpolicy(sub)">Reject</button>
                  </div>
                </li>
              </ul>
            </template>
          </div>
        </div>
      </div>
      
      <!-- Rejection Modal -->
      <div v-if="showRejectModal" class="reject-modal">
        <div class="reject-modal-content">
          <h4>Rejection Reason</h4>
          <p>Please provide a reason for rejecting {{ rejectingType === 'policy' ? 'the policy' : 'subpolicy ' + rejectingSubpolicy?.Identifier }}</p>
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

    <!-- GRC Tasks Card -->
    <div class="dashboard-main-row">
      <div class="dashboard-main-col grc-tasks-col">
        <div class="my-grc-tasks-header">
         
        </div>
      </div>
    </div>

    <!-- Rejected Policies & Compliances List -->
    <div class="rejected-approvals-list" v-if="rejectedPolicies.length">
      <h3>Rejected Policies & Compliances (Edit & Resubmit)</h3>
      <ul>
        <li v-for="policy in rejectedPolicies" :key="policy.ApprovalId">
          <div>
            <strong class="clickable" @click="openRejectedItem(policy)">
              {{ policy.Identifier }}
            </strong>
            <span class="item-type-badge" :class="{
              'compliance-badge': policy.is_compliance,
              'policy-badge': !policy.is_compliance && policy.main_policy_rejected,
              'subpolicy-badge': !policy.is_compliance && !policy.main_policy_rejected
            }">
              {{ policy.is_compliance ? 'Compliance' : 
                 (policy.main_policy_rejected ? 'Policy' : 'Subpolicy') }}
            </span>
            <span v-if="policy.is_compliance" class="badge rejected">Rejected</span>
            <span v-else-if="policy.main_policy_rejected" class="badge rejected">Rejected</span>
            <span v-else class="badge rejected">Rejected</span>
            
            <!-- Show item description -->
            <div v-if="policy.is_compliance">
              - {{ policy.ExtractedData.ComplianceItemDescription || 'No Description' }}
              <div v-if="policy.rejection_reason">
                <strong>Reason:</strong> {{ policy.rejection_reason }}
              </div>
            </div>
            <div v-else>
              - {{ policy.ExtractedData.Scope || 'No Scope' }}
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

    <!-- Edit Modal for Rejected Policy -->
    <div v-if="showEditModal && editingPolicy" class="edit-policy-modal">
      <div class="edit-policy-content">
        <h3>Edit & Resubmit Policy: {{ editingPolicy.Identifier }}</h3>
        <button class="close-btn" @click="closeEditModal">Close</button>
        
        <!-- Main policy fields -->
        <div>
          <label>Scope:</label>
          <input v-model="editingPolicy.ExtractedData.Scope" />
        </div>
        <div>
          <label>Objective:</label>
          <input v-model="editingPolicy.ExtractedData.Objective" />
        </div>
        
        <!-- Rejected Subpolicies Section -->
        <div class="edit-subpolicy-section" v-if="hasRejectedSubpolicies">
          <h4>Rejected Subpolicies</h4>
          
          <div v-for="sub in rejectedSubpolicies" :key="sub.Identifier" class="subpolicy-edit-item">
            <div class="subpolicy-edit-header">
              <span>{{ sub.Identifier }}: {{ sub.SubPolicyName }}</span>
              <span class="subpolicy-badge">Rejected</span>
            </div>
            
            <div class="subpolicy-edit-field">
              <label>Name:</label>
              <input v-model="sub.SubPolicyName" />
            </div>
            
            <div class="subpolicy-edit-field">
              <label>Description:</label>
              <textarea v-model="sub.Description"></textarea>
            </div>
            
            <div class="subpolicy-edit-field">
              <label>Control:</label>
              <textarea v-model="sub.Control"></textarea>
            </div>
            
            <div class="subpolicy-edit-field">
              <label>Rejection Reason:</label>
              <div class="rejection-reason">{{ sub.approval?.remarks }}</div>
            </div>
          </div>
        </div>
        
        <button class="resubmit-btn" @click="resubmitPolicy(editingPolicy)">Resubmit for Review</button>
      </div>
    </div>

    <!-- Edit Modal for Rejected Subpolicy -->
    <div v-if="showEditSubpolicyModal && editingSubpolicy" class="edit-subpolicy-modal">
      <div class="edit-policy-content">
        <h3>Edit & Resubmit Subpolicy: {{ editingSubpolicy.Identifier }}</h3>
        <button class="close-btn" @click="closeEditSubpolicyModal">Close</button>
        <div>
          <label>Name:</label>
          <input v-model="editingSubpolicy.SubPolicyName" />
        </div>
        <div>
          <label>Description:</label>
          <textarea v-model="editingSubpolicy.Description"></textarea>
        </div>
        <div>
          <label>Control:</label>
          <textarea v-model="editingSubpolicy.Control"></textarea>
        </div>
        <div>
          <label>Remarks:</label>
          <textarea v-model="editingSubpolicy.remarks"></textarea>
        </div>
        <button class="resubmit-btn" @click="resubmitSubpolicy(editingSubpolicy)">Resubmit Subpolicy</button>
      </div>
    </div>

    <!-- Subpolicies Modal -->
    <div v-if="showSubpoliciesModal && selectedPolicyForSubpolicies" class="subpolicies-modal">
      <div class="subpolicies-modal-content">
        <h3>Subpolicies for {{ selectedPolicyForSubpolicies.Identifier }}</h3>
        <button class="close-btn" @click="closeSubpoliciesModal">Close</button>
        <div v-for="sub in selectedPolicyForSubpolicies.ExtractedData.subpolicies" :key="sub.Identifier" class="subpolicy-status">
          <div>
            <span class="subpolicy-id">{{ sub.Identifier }}</span> :
            <span class="subpolicy-name">{{ sub.SubPolicyName }}</span>
            <span
              class="badge"
              :class="{
                approved: sub.approval?.approved === true,
                rejected: sub.approval?.approved === false,
                pending: sub.approval?.approved === null && !sub.resubmitted,
                resubmitted: sub.approval?.approved === null && sub.resubmitted
              }"
            >
              {{
                sub.approval?.approved === true
                  ? 'Approved'
                  : sub.approval?.approved === false
                  ? 'Rejected'
                  : sub.resubmitted
                  ? 'Resubmitted'
                  : 'Pending'
              }}
            </span>
          </div>
          <div><strong>Description:</strong> {{ sub.Description }}</div>
          <div><strong>Control:</strong> {{ sub.Control }}</div>
          <div v-if="sub.approval?.approved === false">
            <strong>Reason:</strong> {{ sub.approval?.remarks }}
          </div>
          <!-- Show Approve/Reject buttons if pending -->
          <div v-if="(sub.approval?.approved === null || sub.approval?.approved === undefined) && (isReviewer || !sub.resubmitted)" class="subpolicy-actions">
            <button class="approve-btn" @click="approveSubpolicyFromModal(sub)">Approve</button>
            <button class="reject-btn" @click="rejectSubpolicyFromModal(sub)">Reject</button>
          </div>
          <!-- Replace the Edit & Resubmit button with this: -->
          <div v-if="sub.approval?.approved === false">
            <div v-if="sub.showEditForm">
              <!-- Inline edit form -->
              <div class="subpolicy-inline-edit">
                <h4>Edit Subpolicy</h4>
                <div>
                  <label>Name:</label>
                  <input v-model="sub.SubPolicyName" />
                </div>
                <div>
                  <label>Description:</label>
                  <textarea v-model="sub.Description"></textarea>
                </div>
                <div>
                  <label>Control:</label>
                  <textarea v-model="sub.Control"></textarea>
                </div>
                <div>
                  <label>Remarks:</label>
                  <textarea v-model="sub.remarks"></textarea>
                </div>
                <div class="subpolicy-edit-actions">
                  <button class="resubmit-btn" @click="resubmitSubpolicyDirect(sub)">Resubmit</button>
                  <button class="cancel-btn" @click="hideEditFormInline(sub)">Cancel</button>
                </div>
              </div>
            </div>
            <button v-else class="edit-btn" @click="showEditFormInline(sub)">Edit & Resubmit</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'PolicyApprover',
  data() {
    return {
      approvals: [],
      selectedApproval: null,
      showDetails: false,
      showRejectModal: false,
      rejectingSubpolicy: null,
      rejectingType: '', // 'policy' or 'subpolicy'
      rejectionComment: '',
      rejectedPolicies: [],
      showEditModal: false,
      editingPolicy: null,
      showEditSubpolicyModal: false,
      editingSubpolicy: null,
      editingSubpolicyParent: null,
      userId: 2, // Default user id
      showSubpoliciesModal: false,
      selectedPolicyForSubpolicies: null,
      showEditComplianceModal: false,
      editingCompliance: null,
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
    this.fetchRejectedPolicies();
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
    approveSubpolicy(subpolicy) {
      subpolicy.approval = subpolicy.approval || {};
      subpolicy.approval.approved = true;
      subpolicy.approval.remarks = '';
      // No API call here, just update local model
    },
    rejectSubpolicy(subpolicy) {
      this.rejectingType = 'subpolicy';
      this.rejectingSubpolicy = subpolicy;
      this.showRejectModal = true;
    },
    cancelRejection() {
      this.showRejectModal = false;
      this.rejectingSubpolicy = null;
      this.rejectingType = '';
      this.rejectionComment = '';
    },
    confirmRejection() {
      if (!this.rejectionComment.trim()) {
        alert('Please provide a reason for rejection');
        return;
      }
      
      if (this.rejectingType === 'compliance') {
        // Handle compliance rejection
        if (!this.selectedApproval.ExtractedData.compliance_approval) {
          this.selectedApproval.ExtractedData.compliance_approval = {};
        }
        this.selectedApproval.ExtractedData.compliance_approval.approved = false;
        this.selectedApproval.ExtractedData.compliance_approval.remarks = this.rejectionComment;
        this.selectedApproval.ApprovedNot = false;
        
        // Close the rejection modal
        this.showRejectModal = false;
        this.rejectingType = '';
        this.rejectionComment = '';
        
        // Important: Submit the review immediately to save changes
        this.submitReview();
        return;
      } 
      else if (this.rejectingType === 'subpolicy' && this.rejectingSubpolicy) {
        // Existing subpolicy rejection logic
        this.rejectingSubpolicy.approval = this.rejectingSubpolicy.approval || {};
        this.rejectingSubpolicy.approval.approved = false;
        this.rejectingSubpolicy.approval.remarks = this.rejectionComment;
      }
      else if (this.rejectingType === 'policy') {
        // Handle policy rejection
        if (!this.selectedApproval.ExtractedData.policy_approval) {
          this.selectedApproval.ExtractedData.policy_approval = {};
        }
        this.selectedApproval.ExtractedData.policy_approval.approved = false;
        this.selectedApproval.ExtractedData.policy_approval.remarks = this.rejectionComment;
        this.selectedApproval.ApprovedNot = false;
      }
      
      this.showRejectModal = false;
      this.rejectingSubpolicy = null;
      this.rejectingType = '';
      this.rejectionComment = '';
    },
    updateApproval() {
      console.log('Updating approval:', this.selectedApproval);
      
      axios.put(`http://localhost:8000/api/policy-approvals/${this.selectedApproval.ApprovalId}/`, {
        ExtractedData: this.selectedApproval.ExtractedData,
        ApprovedNot: this.selectedApproval.ApprovedNot
      })
      .then(response => {
        console.log('Approval updated successfully');
        // Update the approval ID to point to the newly created record
        this.selectedApproval.ApprovalId = response.data.ApprovalId;
        this.selectedApproval.Version = response.data.Version;
        // Refresh the approval list to show updated status
        this.refreshApprovals();
      })
      .catch(error => {
        console.error('Error updating approval:', error);
      });
    },
    // Add a method to refresh approvals
    refreshData() {
      // Show loading indicator or feedback if desired
      this.refreshApprovals();
      this.fetchRejectedPolicies();
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
    fetchRejectedPolicies() {
      // Use the hardcoded user ID 2 for reviewer
      const reviewerId = 2;
      
      axios.get(`http://localhost:8000/api/policy-approvals/rejected/${reviewerId}/`)
        .then(response => {
          // Filter out compliance items
          const policyItems = response.data.filter(item => item.ExtractedData?.type !== 'compliance');
          
          // Get unique policies by Identifier
          const uniquePolicies = [];
          const identifiers = new Set();
          
          // Sort by ApprovalId (descending) to get the most recent first
          const sortedPolicies = policyItems.sort((a, b) => b.ApprovalId - a.ApprovalId);
          
          // Take only the most recent version of each policy
          sortedPolicies.forEach(policy => {
            if (!identifiers.has(policy.Identifier)) {
              identifiers.add(policy.Identifier);
              uniquePolicies.push(policy);
            }
          });
          
          this.rejectedPolicies = uniquePolicies;
        })
        .catch(error => {
          console.error('Error fetching rejected policies:', error);
        });
    },
    editRejectedPolicy(policy) {
      this.editingPolicy = JSON.parse(JSON.stringify(policy)); // Deep copy
      this.showEditModal = true;
    },
    closeEditModal() {
      this.showEditModal = false;
      this.editingPolicy = null;
    },
    resubmitPolicy(policy) {
      axios.put(`http://localhost:8000/api/policy-approvals/resubmit/${policy.ApprovalId}/`, {
        ExtractedData: policy.ExtractedData
      })
      .then(response => {
        alert('Policy resubmitted for review!');
        this.showEditModal = false;
        // Update the approval ID to point to the newly created record
        policy.ApprovalId = response.data.ApprovalId;
        policy.Version = response.data.Version;
        this.fetchRejectedPolicies();
      })
      .catch(error => {
        alert('Error resubmitting policy');
        console.error(error);
      });
    },
    editRejectedSubpolicy(policy, subpolicy) {
      // No longer close the subpolicies modal
      // this.showSubpoliciesModal = false;
      
      // Find the actual subpolicy object in the parent policy's ExtractedData
      const parent = policy;
      const sub = parent.ExtractedData.subpolicies.find(s => s.Identifier === subpolicy.Identifier);
      this.editingSubpolicy = sub;
      this.editingSubpolicyParent = parent;
      this.showEditSubpolicyModal = true;
    },
    closeEditSubpolicyModal() {
      this.showEditSubpolicyModal = false;
      this.editingSubpolicy = null;
      this.editingSubpolicyParent = null;
    },
    resubmitSubpolicy(subpolicy) {
      // Mark as pending (null) and clear remarks
      if (!subpolicy.approval) subpolicy.approval = {};
      subpolicy.approval.approved = null;
      subpolicy.approval.remarks = subpolicy.remarks || '';
      
      // Update via API
      axios.put(`http://localhost:8000/api/policy-approvals/resubmit/${this.editingSubpolicyParent.ApprovalId}/`, {
        ExtractedData: this.editingSubpolicyParent.ExtractedData
      })
      .then(response => {
        alert('Subpolicy resubmitted for review!');
        
        // Only close the edit modal, keep subpolicies modal open
        this.showEditSubpolicyModal = false;
        
        // Update the approval ID to point to the newly created record
        this.editingSubpolicyParent.ApprovalId = response.data.ApprovalId;
        this.editingSubpolicyParent.Version = response.data.Version;
        this.fetchRejectedPolicies();
      })
      .catch(error => {
        alert('Error resubmitting subpolicy');
        console.error(error);
      });
    },
    openSubpoliciesModal(policy) {
      this.selectedPolicyForSubpolicies = policy;
      this.showSubpoliciesModal = true;
    },
    closeSubpoliciesModal() {
      this.selectedPolicyForSubpolicies = null;
      this.showSubpoliciesModal = false;
    },
    approveSubpolicyFromModal(subpolicy) {
      subpolicy.approval = subpolicy.approval || {};
      subpolicy.approval.approved = true;
      subpolicy.approval.remarks = '';
      // No API call, just update local model
    },
    rejectSubpolicyFromModal(subpolicy) {
      // Open rejection modal for subpolicy
      this.rejectingType = 'subpolicy';
      this.rejectingSubpolicy = subpolicy;
      this.showRejectModal = true;
    },
    submitReview() {
      if (!this.isComplianceApproval) {
        // Existing policy review submission
        this.submitPolicy();
        return;
      }
      
      // For compliance reviews
      const reviewData = {
        ExtractedData: JSON.parse(JSON.stringify(this.selectedApproval.ExtractedData)),
        ApprovedNot: this.selectedApproval.ApprovedNot
      };
      
      axios.put(
        `http://localhost:8000/api/compliance-approvals/${this.selectedApproval.ApprovalId}/review/`,
        reviewData
      )
      .then(response => {
        console.log('Response:', response.data);
        if (response.data.ApprovalId) {
          this.selectedApproval.ApprovalId = response.data.ApprovalId;
          this.selectedApproval.Version = response.data.Version;
          alert('Compliance review submitted successfully!');
          
          // First close the details view
          this.closeApprovalDetails();
          
          // Then refresh the approvals list to update the UI
          this.refreshApprovals();
          
          // Force reload the page to ensure everything is updated
          setTimeout(() => {
            window.location.reload();
          }, 500);
        } else {
          alert('Received response but no approval ID was returned');
        }
      })
      .catch(error => {
        console.error('Error submitting review:', error);
        alert('Error submitting review: ' + (error.response?.data?.error || error.message));
      });
    },
    submitPolicy() {
      // Auto-approve policy if all subpolicies are approved
      if (!this.hasUnreviewedSubpolicies && this.allSubpoliciesApproved) {
        // Initialize policy approval if doesn't exist
        if (!this.selectedApproval.ExtractedData.policy_approval) {
          this.selectedApproval.ExtractedData.policy_approval = {};
        }
        
        // Set approval status
        this.selectedApproval.ExtractedData.policy_approval.approved = true;
        this.selectedApproval.ExtractedData.policy_approval.remarks = '';
        
        // Update the overall approval status
        this.selectedApproval.ApprovedNot = true;
      }
      
      // Create review data from the current approval state
      const reviewData = {
        ExtractedData: JSON.parse(JSON.stringify(this.selectedApproval.ExtractedData)),
        ApprovedNot: this.selectedApproval.ApprovedNot
      };
      
      axios.put(
        `http://localhost:8000/api/policy-approvals/${this.selectedApproval.ApprovalId}/review/`,
        reviewData
      )
      .then(response => {
        console.log('Response:', response.data);
        if (response.data.ApprovalId) {
          this.selectedApproval.ApprovalId = response.data.ApprovalId;
          this.selectedApproval.Version = response.data.Version;
          alert('Policy review submitted successfully!');
          
          // Close the details view
          this.closeApprovalDetails();
          
          // Refresh the approvals list
          this.refreshApprovals();
        } else {
          alert('Received response but no approval ID was returned');
        }
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
      this.rejectingType = 'compliance';
      this.showRejectModal = true;
    },
    openRejectedItem(item) {
      if (item.is_compliance) {
        // For compliance items
        this.editingCompliance = JSON.parse(JSON.stringify(item)); // Deep copy
        this.showEditComplianceModal = true;
      } else {
        // For policy items
        this.openSubpoliciesModal(item);
      }
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
        this.fetchRejectedPolicies();
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
    showEditFormInline(subpolicy) {
      // In Vue 3, you can directly set properties
      subpolicy.showEditForm = true;
    },
    hideEditFormInline(subpolicy) {
      subpolicy.showEditForm = false;
    },
    resubmitSubpolicyDirect(subpolicy) {
      // Mark as pending (null) and clear remarks
      if (!subpolicy.approval) subpolicy.approval = {};
      subpolicy.approval.approved = null;
      subpolicy.approval.remarks = subpolicy.remarks || '';
      
      // Mark as resubmitted
      subpolicy.resubmitted = true;
      
      // Get the parent policy (selectedPolicyForSubpolicies)
      const parent = this.selectedPolicyForSubpolicies;
      
      // Update via API
      axios.put(`http://localhost:8000/api/policy-approvals/resubmit/${parent.ApprovalId}/`, {
        ExtractedData: parent.ExtractedData
      })
      .then(response => {
        alert('Subpolicy resubmitted for review!');
        
        // Hide the inline edit form
        this.hideEditFormInline(subpolicy);
        
        // Update the approval ID to point to the newly created record
        parent.ApprovalId = response.data.ApprovalId;
        parent.Version = response.data.Version;
        this.fetchRejectedPolicies();
      })
      .catch(error => {
        alert('Error resubmitting subpolicy');
        console.error(error);
      });
    }
  },
  computed: {
    policyApprovals() {
      // Only include policy items (exclude compliance items)
      return this.approvals.filter(approval => approval.ExtractedData?.type !== 'compliance');
    },
    pendingApprovalsCount() {
      return this.policyApprovals.filter(a => a.ApprovedNot === null).length;
    },
    approvedApprovalsCount() {
      return this.policyApprovals.filter(a => a.ApprovedNot === true).length;
    },
    rejectedApprovalsCount() {
      return this.policyApprovals.filter(a => a.ApprovedNot === false).length;
    },
    hasUnreviewedSubpolicies() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData || 
          !this.selectedApproval.ExtractedData.subpolicies) {
        return true;
      }
      
      const subpolicies = this.selectedApproval.ExtractedData.subpolicies;
      return subpolicies.some(sub => {
        return sub.approval?.approved === null || sub.approval?.approved === undefined;
      });
    },
    hasRejectedSubpolicies() {
      return this.rejectedSubpolicies.length > 0;
    },
    rejectedSubpolicies() {
      if (!this.editingPolicy || !this.editingPolicy.ExtractedData || !this.editingPolicy.ExtractedData.subpolicies) {
        return [];
      }
      
      return this.editingPolicy.ExtractedData.subpolicies.filter(sub => 
        sub.approval?.approved === false
      );
    },
    isComplianceApproval() {
      return this.selectedApproval?.ExtractedData?.type === 'compliance';
    },
    approvalStatus() {
      if (!this.selectedApproval || !this.selectedApproval.ExtractedData) return null;
      
      if (this.isComplianceApproval) {
        return this.selectedApproval.ExtractedData.compliance_approval || { approved: null, remarks: '' };
      } else {
        return this.selectedApproval.ExtractedData.policy_approval || { approved: null, remarks: '' };
      }
    },
    allSubpoliciesApproved() {
      if (!this.selectedApproval || 
          !this.selectedApproval.ExtractedData || 
          !this.selectedApproval.ExtractedData.subpolicies ||
          this.selectedApproval.ExtractedData.subpolicies.length === 0) {
        return false;
      }
      
      const subpolicies = this.selectedApproval.ExtractedData.subpolicies;
      return subpolicies.every(sub => sub.approval?.approved === true);
    },
    isReviewer() {
      // Assuming reviewer has userId = 2 as in your hardcoded value
      return this.userId === 2;
    }
  }
}
</script>

<style scoped>
@import './PolicyApprover.css';

/* Completely revised modal layering with much higher z-indices */
.subpolicies-modal {
  z-index: 9000 !important;
}

.edit-subpolicy-modal {
  z-index: 10000 !important; /* Dramatically higher z-index */
  position: fixed;
  top: 0; 
  left: 0; 
  right: 0; 
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto !important; /* Force pointer events */
}

.edit-policy-content {
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2), 0 0 0 1000px rgba(0, 0, 0, 0.3);
  position: relative;
  max-height: 80vh;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  animation: fadeIn 0.3s ease-in-out;
  z-index: 10001 !important; /* Content even higher */
}

.reject-modal {
  z-index: 11000 !important; /* Highest z-index to appear on top */
}

/* Override any potential conflicting styles in the base CSS */
.policy-details-modal,
.reject-modal,
.edit-policy-modal,
.subpolicies-modal,
.edit-subpolicy-modal {
  position: fixed !important;
  z-index: auto !important; /* Let our specific z-index values take precedence */
}

/* The rest of your styling remains the same */
.edit-subpolicy-modal label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
  color: #4b5563;
}

.edit-subpolicy-modal input,
.edit-subpolicy-modal textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.edit-subpolicy-modal input:focus,
.edit-subpolicy-modal textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.edit-subpolicy-modal button.resubmit-btn {
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.2s;
}

.edit-subpolicy-modal button.resubmit-btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Inline edit form styles */
.subpolicy-inline-edit {
  background: #f8fafc;
  border: 2px solid #6366f1;
  border-radius: 8px;
  padding: 20px;
  margin: 15px 0;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.subpolicy-inline-edit h4 {
  margin-top: 0;
  color: #6366f1;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.subpolicy-inline-edit label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
  color: #4b5563;
}

.subpolicy-inline-edit input,
.subpolicy-inline-edit textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  margin-bottom: 12px;
}

.subpolicy-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.resubmit-btn {
  background: #6366f1;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}

.cancel-btn {
  background: #e5e7eb;
  color: #4b5563;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}

.badge.resubmitted {
  background-color: #3b82f6;
  color: white;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.25);
  padding: 5px 12px;
  font-weight: 600;
  position: relative;
}

/* Add a subtle animation to resubmitted badge */
.badge.resubmitted::after {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 20px;
  border: 2px solid rgba(59, 130, 246, 0.5);
  animation: pulse-blue 2s infinite;
}

@keyframes pulse-blue {
  0% { opacity: 0.8; transform: scale(1); }
  50% { opacity: 0.2; transform: scale(1.1); }
  100% { opacity: 0.8; transform: scale(1); }
}
</style> 