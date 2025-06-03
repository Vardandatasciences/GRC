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
          <strong class="clickable" @click="openApprovalDetails(framework)">
            {{ getFrameworkId(framework) }}
          </strong>
          <span class="item-type-badge framework-badge">Framework</span>
          <span v-if="framework.isResubmitted" class="resubmitted-badge">RESUBMITTED</span>
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
          <span v-else-if="framework.ApprovedNot === true || framework.ApprovedNot === 1" class="approval-status approved">(Approved)</span>
          <span v-else class="approval-status rejected">(Rejected)</span>
        </li>
      </ul>
    </div>

    <!-- Approved Frameworks List -->
    <div class="approved-frameworks-list" v-if="false">
      <h3>Recently Approved Frameworks</h3>
      <ul>
        <li v-for="framework in sortedApprovedFrameworks" 
            :key="framework.ApprovalId" 
            class="approved-framework-item">
          <strong class="clickable" @click="openApprovalDetails(framework)">
            {{ getFrameworkId(framework) }}
          </strong>
          <span class="item-type-badge framework-badge">Framework</span>
          <span class="approved-badge">APPROVED</span>
          <span class="date-info">
            Approved: {{ formatDate(framework.ApprovedDate) }}
          </span>
          <span class="framework-category">{{ framework.ExtractedData?.Category || 'No Category' }}</span>
          <span class="assigned-by">
            <img class="assigned-avatar" :src="framework.ExtractedData?.CreatedByAvatar || 'https://randomuser.me/api/portraits/men/32.jpg'" alt="avatar" />
            {{ framework.ExtractedData?.CreatedByName || 'System' }}
          </span>
          <span class="approval-status approved">(Approved)</span>
        </li>
      </ul>
    </div>

    <!-- Framework Details Modal -->
    <div v-if="showDetails && selectedApproval" class="framework-details-modal">
      <div class="framework-details-content">
        <h3>
          <span class="detail-type-indicator">Framework</span> 
          Details: {{ getFrameworkId(selectedApproval) }}
          <span class="version-pill">Version: {{ selectedApproval.version || 'u1' }}</span>
          <span v-if="selectedApproval.isResubmitted" class="resubmitted-pill">RESUBMITTED</span>
        </h3>
        
        <button class="close-btn" @click="closeApprovalDetails">Close</button>
        
        <!-- Framework Approval Section -->
        <div class="framework-approval-section">
          <h4>Framework Approval</h4>
          
          <!-- Framework status indicator -->
          <div class="framework-status-indicator">
            <span class="status-label">Status:</span>
            <span class="status-value" :class="{
              'status-approved': selectedApproval.ApprovedNot === true || selectedApproval.ApprovedNot === 1 || selectedApproval.ExtractedData?.Status === 'Approved',
              'status-rejected': selectedApproval.ApprovedNot === false || selectedApproval.ApprovedNot === 0 || selectedApproval.ExtractedData?.Status === 'Rejected',
              'status-pending': selectedApproval.ApprovedNot === null && selectedApproval.ExtractedData?.Status !== 'Approved' && selectedApproval.ExtractedData?.Status !== 'Rejected'
            }">
              {{ selectedApproval.ApprovedNot === true || selectedApproval.ApprovedNot === 1 || selectedApproval.ExtractedData?.Status === 'Approved' ? 'Approved' : 
                 selectedApproval.ApprovedNot === false || selectedApproval.ApprovedNot === 0 || selectedApproval.ExtractedData?.Status === 'Rejected' ? 'Rejected' : 
                 'Under Review' }}
            </span>
          </div>
          
          <div class="framework-actions">
            <button class="approve-btn" @click="approveFramework()" 
              v-if="isReviewer && selectedApproval.ApprovedNot === null && selectedApproval.canApproveFramework"
              :disabled="!selectedApproval.canApproveFramework">
              <i class="fas fa-check"></i> Approve Framework
            </button>
            <button class="reject-btn" @click="rejectFramework()" v-if="isReviewer && selectedApproval.ApprovedNot === null">
              <i class="fas fa-times"></i> Reject Framework
            </button>
            <button class="submit-btn" @click="submitReview()" v-if="isReviewer && (selectedApproval.ApprovedNot === 1 || selectedApproval.ApprovedNot === 0 || selectedApproval.ApprovedNot === true || selectedApproval.ApprovedNot === false)">
              <i class="fas fa-paper-plane"></i> Submit Review
            </button>
            
            <!-- Framework approval blocked message -->
            <div v-if="isReviewer && selectedApproval.ApprovedNot === null && !selectedApproval.canApproveFramework" class="approval-blocked-message">
              <i class="fas fa-exclamation-triangle"></i>
              Framework approval is blocked until all policies and subpolicies are approved.
            </div>
          </div>
        </div>
        
        <!-- Display framework details -->
        <div v-if="selectedApproval.ExtractedData">
          <div v-for="(value, key) in selectedApproval.ExtractedData" :key="key" class="framework-detail-row">
            <template v-if="key !== 'policies' && key !== 'framework_approval' && key !== 'type'">
              <strong>{{ formatFieldName(key) }}:</strong> <span>{{ value }}</span>
            </template>
          </div>
        </div>

        <!-- Policies and Subpolicies Approval Section -->
        <div v-if="selectedApproval.ExtractedData" class="policies-approval-section">
          <h4>Framework Policies & Subpolicies Approval</h4>
          <div class="approval-note">
            <i class="fas fa-info-circle"></i>
            All policies and their subpolicies must be approved before the framework can be approved.
          </div>
          
          <!-- Loading message -->
          <div v-if="!selectedApproval.ExtractedData.policies" class="loading-policies">
            <i class="fas fa-spinner fa-spin"></i>
            Loading policies and subpolicies...
          </div>
          
          <!-- Policies list -->
          <div v-else-if="selectedApproval.ExtractedData.policies.length > 0">
            <div v-for="policy in selectedApproval.ExtractedData.policies" :key="policy.PolicyId" class="policy-approval-item">
              <div class="policy-header">
                <div class="policy-info">
              <span class="policy-name">{{ policy.PolicyName }}</span>
              <span class="policy-status" :class="{
                'status-approved': policy.Status === 'Approved',
                'status-rejected': policy.Status === 'Rejected',
                'status-pending': policy.Status === 'Under Review'
              }">{{ policy.Status }}</span>
                </div>
                <div class="policy-description">{{ policy.PolicyDescription }}</div>
              </div>
              
              <!-- Subpolicies -->
              <div v-if="policy.subpolicies && policy.subpolicies.length > 0" class="subpolicies-list">
                <h5>Subpolicies:</h5>
                <div v-for="subpolicy in policy.subpolicies" :key="subpolicy.SubPolicyId" class="subpolicy-item">
                  <div class="subpolicy-info">
                    <div class="subpolicy-header">
                      <span class="subpolicy-name">{{ subpolicy.SubPolicyName }}</span>
                      <span class="subpolicy-status" :class="{
                        'status-approved': subpolicy.Status === 'Approved',
                        'status-rejected': subpolicy.Status === 'Rejected',
                        'status-pending': subpolicy.Status === 'Under Review'
                      }">{{ subpolicy.Status }}</span>
                    </div>
                    <div class="subpolicy-description">{{ subpolicy.Description }}</div>
                    <div class="subpolicy-control">
                      <strong>Control:</strong> {{ subpolicy.Control }}
                    </div>
                  </div>
                  
                  <!-- Subpolicy Actions -->
                  <div v-if="isReviewer && subpolicy.Status === 'Under Review'" class="subpolicy-actions">
                    <button class="approve-btn" @click="approveFrameworkSubpolicy(subpolicy, policy)">
                      <i class="fas fa-check"></i> Approve
                    </button>
                    <button class="reject-btn" @click="rejectFrameworkSubpolicy(subpolicy, policy)">
                      <i class="fas fa-times"></i> Reject
                    </button>
                  </div>
                  
                  <!-- Show rejection reason if rejected -->
                  <div v-if="subpolicy.Status === 'Rejected' && subpolicy.approval?.remarks" class="rejection-reason">
                    <strong>Rejection Reason:</strong> {{ subpolicy.approval.remarks }}
                  </div>
                </div>
              </div>
              
              <!-- No subpolicies message -->
              <div v-else class="no-subpolicies">
                <i class="fas fa-info-circle"></i>
                This policy has no subpolicies to approve.
              </div>
            </div>
            
            <!-- Framework Approval Eligibility -->
            <div class="framework-approval-eligibility">
              <div v-if="selectedApproval.canApproveFramework" class="eligibility-message approved">
                <i class="fas fa-check-circle"></i>
                All policies and subpolicies are approved. Framework is ready for approval.
              </div>
              <div v-else class="eligibility-message pending">
                <i class="fas fa-clock"></i>
                Framework cannot be approved until all policies and subpolicies are approved.
              </div>
            </div>
          </div>
          
          <!-- No policies message -->
          <div v-else class="no-policies">
            <div class="empty-state">
              <i class="fas fa-folder-open"></i>
              <h4>No Policies Found</h4>
              <p>This framework does not contain any policies yet. Add policies to enable the approval process.</p>
            </div>
          </div>
        </div>

        <!-- Add a message for rejected frameworks -->
        <div v-if="selectedApproval.ApprovedNot === false || selectedApproval.ApprovedNot === 0" class="rejected-framework-message">
          <div class="rejection-note">
            <i class="fas fa-exclamation-triangle"></i>
            This framework has been rejected. All policies and subpolicies within this framework have been automatically rejected.
          </div>
        </div>
      </div>
      
      <!-- Rejection Modal -->
      <div v-if="showRejectModal" class="reject-modal">
        <div class="reject-modal-content">
          <h4>Rejection Reason</h4>
          <p>Please provide a reason for rejecting this framework</p>
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
        <div class="framework-edit-section">
          <h4>Framework Details</h4>
          <div class="form-group">
          <label>Framework Name:</label>
          <input v-model="editingFramework.ExtractedData.FrameworkName" />
        </div>
          <div class="form-group">
          <label>Framework Description:</label>
          <textarea v-model="editingFramework.ExtractedData.FrameworkDescription"></textarea>
        </div>
          <div class="form-group">
          <label>Category:</label>
          <input v-model="editingFramework.ExtractedData.Category" />
        </div>
          <div class="form-group">
          <label>Effective Date:</label>
          <input type="date" v-model="editingFramework.ExtractedData.EffectiveDate" />
        </div>
          <div class="form-group">
          <label>Start Date:</label>
          <input type="date" v-model="editingFramework.ExtractedData.StartDate" />
        </div>
          <div class="form-group">
          <label>End Date:</label>
          <input type="date" v-model="editingFramework.ExtractedData.EndDate" />
          </div>
        </div>
        
        <!-- Show framework rejection reason -->
        <div v-if="editingFramework.ExtractedData?.approval?.remarks || editingFramework.rejection_reason" class="rejection-info-section">
          <h4>Framework Rejection Reason</h4>
          <div class="rejection-reason">
            {{ editingFramework.ExtractedData?.approval?.remarks || editingFramework.rejection_reason }}
          </div>
        </div>
        
        <!-- Rejected Policies and Subpolicies Section -->
        <div v-if="editingFramework.ExtractedData && editingFramework.ExtractedData.policies && editingFramework.ExtractedData.policies.length > 0" class="rejected-items-section">
          <h4>Rejected Policies & Subpolicies</h4>
          <div class="edit-note">
            <i class="fas fa-info-circle"></i>
            Edit the rejected items below and resubmit the framework for review.
          </div>
          
          <div v-for="policy in editingFramework.ExtractedData.policies" :key="policy.PolicyId" class="policy-edit-item">
            <div class="policy-edit-header">
              <div class="policy-edit-info">
                <span class="policy-name">{{ policy.PolicyName }}</span>
                <span class="policy-status" :class="{
                  'status-approved': policy.Status === 'Approved',
                  'status-rejected': policy.Status === 'Rejected',
                  'status-pending': policy.Status === 'Under Review'
                }">{{ policy.Status }}</span>
              </div>
              
              <!-- Policy editing fields (only if rejected) -->
              <div v-if="policy.Status === 'Rejected'" class="policy-edit-fields">
                <div class="form-group">
                  <label>Policy Name:</label>
                  <input v-model="policy.PolicyName" />
                </div>
                <div class="form-group">
                  <label>Policy Description:</label>
                  <textarea v-model="policy.PolicyDescription"></textarea>
                </div>
                <div class="form-group">
                  <label>Scope:</label>
                  <input v-model="policy.Scope" />
                </div>
                <div class="form-group">
                  <label>Objective:</label>
                  <textarea v-model="policy.Objective"></textarea>
                </div>
              </div>
            </div>
            
            <!-- Subpolicies -->
            <div v-if="policy.subpolicies && policy.subpolicies.length > 0" class="subpolicies-edit-list">
              <h5>Subpolicies:</h5>
              <div v-for="subpolicy in policy.subpolicies" :key="subpolicy.SubPolicyId" class="subpolicy-edit-item">
                <div class="subpolicy-edit-info">
                  <div class="subpolicy-edit-header">
                    <span class="subpolicy-name">{{ subpolicy.SubPolicyName }}</span>
                    <span class="subpolicy-status" :class="{
                      'status-approved': subpolicy.Status === 'Approved',
                      'status-rejected': subpolicy.Status === 'Rejected',
                      'status-pending': subpolicy.Status === 'Under Review'
                    }">{{ subpolicy.Status }}</span>
                  </div>
                  
                  <!-- Subpolicy editing fields (only if rejected) -->
                  <div v-if="subpolicy.Status === 'Rejected'" class="subpolicy-edit-fields">
                    <div class="form-group">
                      <label>Subpolicy Name:</label>
                      <input v-model="subpolicy.SubPolicyName" />
                    </div>
                    <div class="form-group">
                      <label>Description:</label>
                      <textarea v-model="subpolicy.Description"></textarea>
                    </div>
                    <div class="form-group">
                      <label>Control:</label>
                      <input v-model="subpolicy.Control" />
                    </div>
                    <div class="form-group">
                      <label>Identifier:</label>
                      <input v-model="subpolicy.Identifier" />
                    </div>
                    
                    <!-- Show rejection reason if available -->
                    <div v-if="subpolicy.approval?.remarks" class="subpolicy-rejection-reason">
                      <strong>Rejection Reason:</strong> {{ subpolicy.approval.remarks }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- No subpolicies message -->
            <div v-else class="no-subpolicies-edit">
              <i class="fas fa-info-circle"></i>
              This policy has no subpolicies.
            </div>
          </div>
        </div>
        
        <!-- No policies message -->
        <div v-else-if="editingFramework.ExtractedData && (!editingFramework.ExtractedData.policies || editingFramework.ExtractedData.policies.length === 0)" class="no-policies-edit">
          <div class="empty-state">
            <i class="fas fa-folder-open"></i>
            <h4>No Policies Found</h4>
            <p>This framework does not contain any policies.</p>
          </div>
        </div>
        
        <div class="modal-actions">
          <button class="validate-btn" @click="checkDataChanges()" style="background-color: #9f7aea; color: white; border: none; border-radius: 8px; padding: 12px 24px; font-weight: 600; cursor: pointer; margin-right: 12px;">
            <i class="fas fa-bug"></i> Validate Changes (Debug)
          </button>
          <button class="resubmit-btn" @click="resubmitFramework(editingFramework)">
            <i class="fas fa-paper-plane"></i> Resubmit Framework for Review
          </button>
        </div>
      </div>
    </div>

    <!-- Role toggle for testing -->
    <div class="role-toggle">
      <label>
        <input type="checkbox" v-model="isReviewer">
        <span>{{ isReviewer ? 'Reviewer Mode' : 'User Mode' }}</span>
      </label>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'FrameworkApprover',
  data() {
    return {
      approvals: [], // Pending approvals
      approvedFrameworks: [], // Approved frameworks
      rejectedFrameworks: [], // Rejected frameworks for editing
      selectedApproval: null,
      showDetails: false,
      showRejectModal: false,
      rejectionComment: '',
      showEditModal: false,
      editingFramework: null,
      userId: 2, // Default user id
      isReviewer: true, // Set based on user role, for testing
      rejectingType: '', // 'framework' or 'subpolicy'
      rejectingSubpolicy: null,
      rejectingPolicy: null,
    }
  },
  mounted() {
    console.log('FrameworkApprover component mounted');
    this.fetchFrameworks();
    this.fetchRejectedFrameworks();
  },
  methods: {
    fetchFrameworks() {
      console.log('Fetching all frameworks for reviewer dashboard...');
      
      // Fetch all framework approvals
      axios.get('http://localhost:8000/api/framework-approvals/')
        .then(response => {
          console.log('All framework approvals response:', response.data);
          
          // Group all frameworks by FrameworkId and keep only the latest approval
          const latestFrameworks = {};
          
          for (const approval of response.data) {
            const frameworkId = approval.FrameworkId;
            
            // Keep only the latest approval for each framework (highest ApprovalId)
            if (!latestFrameworks[frameworkId] || 
                approval.ApprovalId > latestFrameworks[frameworkId].ApprovalId) {
              latestFrameworks[frameworkId] = approval;
            }
          }
          
          // Process only the latest frameworks
          const allLatestFrameworks = Object.values(latestFrameworks).map(approval => {
            const isResubmitted = approval.Version && approval.Version !== 'u1';
            
            return {
              FrameworkId: approval.FrameworkId,
              ApprovalId: approval.ApprovalId,
              ExtractedData: approval.ExtractedData || {
                type: 'framework',
                FrameworkName: 'Unknown Framework',
                Status: approval.ApprovedNot === true || approval.ApprovedNot === 1 ? 'Approved' : 
                        approval.ApprovedNot === false || approval.ApprovedNot === 0 ? 'Rejected' : 'Under Review'
              },
              ApprovedNot: approval.ApprovedNot,
              ApprovedDate: approval.ApprovedDate,
              version: approval.Version || 'u1',
              UserId: approval.UserId,
              ReviewerId: approval.ReviewerId,
              isResubmitted: isResubmitted
            };
          });
          
          // Filter by status for counting
          const pendingFrameworks = allLatestFrameworks.filter(f => f.ApprovedNot === null);
          const approvedFrameworks = allLatestFrameworks.filter(f => f.ApprovedNot === true || f.ApprovedNot === 1);
          
          // Show both pending and approved in the main list
          this.approvals = [...pendingFrameworks, ...approvedFrameworks];
          
          // Keep approved frameworks separate for counting
          this.approvedFrameworks = approvedFrameworks;
          
          console.log(`Processed frameworks - Total in list: ${this.approvals.length}, Pending: ${pendingFrameworks.length}, Approved: ${approvedFrameworks.length}`);
          
          // Log any resubmitted frameworks
          const resubmittedFrameworks = this.approvals.filter(a => a.isResubmitted);
          if (resubmittedFrameworks.length > 0) {
            console.log(`Found ${resubmittedFrameworks.length} resubmitted frameworks:`, resubmittedFrameworks);
          }
        })
        .catch(error => {
          console.error('Error fetching framework approvals:', error);
          
          // Fallback: try the pending endpoint for pending frameworks
          axios.get('http://localhost:8000/api/pending-framework-approvals/')
            .then(response => {
              console.log('Pending framework approvals fallback response:', response.data);
              
              this.approvals = response.data.map(approval => {
                const isResubmitted = approval.isResubmitted || (approval.version && approval.version !== 'u1');
                
                return {
                  FrameworkId: approval.FrameworkId,
                  ApprovalId: approval.ApprovalId,
                  ExtractedData: approval.ExtractedData || {
                    type: 'framework',
                    FrameworkName: 'Unknown Framework',
                    Status: 'Under Review'
                  },
                  ApprovedNot: approval.ApprovedNot,
                  ApprovedDate: approval.ApprovedDate,
                  version: approval.Version || 'u1',
                  UserId: approval.UserId,
                  ReviewerId: approval.ReviewerId,
                  isResubmitted: isResubmitted
                };
              });
              
              console.log(`Processed ${this.approvals.length} pending framework approvals (fallback)`);
            })
            .catch(fallbackError => {
              console.error('Error fetching pending framework approvals (fallback):', fallbackError);
            });
        });
    },
    
    openApprovalDetails(approval) {
      // Get the framework ID
      const frameworkId = this.getFrameworkId(approval);
      console.log('Opening framework details for ID:', frameworkId);

      // Always fetch the framework details with policies and subpolicies for approval
      axios.get(`http://localhost:8000/api/frameworks/${frameworkId}/get-for-approval/`)
        .then(approvalResponse => {
          console.log('Framework details for approval response:', approvalResponse.data);
          
          // Always use the response data which should include policies and subpolicies
          if (approvalResponse.data && approvalResponse.data.ExtractedData) {
            const frameworkApproval = approvalResponse.data;
            
            // Ensure the ExtractedData has the policies array
            if (!frameworkApproval.ExtractedData.policies) {
              console.warn('No policies found in framework data');
              frameworkApproval.ExtractedData.policies = [];
            }
            
            console.log('Policies in framework:', frameworkApproval.ExtractedData.policies.length);
            
            // Create a complete approval object with the latest data
            const updatedApproval = {
              ...approval,
              ...frameworkApproval,
              version: frameworkApproval.Version || 'u1',
              ExtractedData: frameworkApproval.ExtractedData
            };
            
            // Always check framework approval eligibility
            this.checkFrameworkApprovalEligibility(updatedApproval);
            
            // Log the final approval object to debug
            console.log('Updated approval object:', updatedApproval);
            console.log('Can approve framework:', updatedApproval.canApproveFramework);
            
                  this.selectedApproval = updatedApproval;
                  this.showDetails = true;
            } else {
            console.error('Invalid response structure from get-for-approval endpoint');
            // Fallback: try to create a basic structure
            const basicApproval = {
              ...approval,
              ExtractedData: {
                ...approval.ExtractedData,
                policies: []
              },
              canApproveFramework: false
            };
            this.selectedApproval = basicApproval;
            this.showDetails = true;
          }
        })
        .catch(error => {
          console.error('Error fetching framework details for approval:', error);
          console.error('Error details:', error.response?.data);
          
          // Fallback: create a basic approval structure
          const fallbackApproval = {
            ...approval,
            ExtractedData: {
              ...approval.ExtractedData,
              policies: []
            },
            canApproveFramework: false
          };
          this.selectedApproval = fallbackApproval;
          this.showDetails = true;
          
          // Show user-friendly error
          alert('Error loading framework details. Please try again.');
        });
    },
    
    refreshData() {
      console.log('Refreshing framework approval data...');
      
      // Refresh the main frameworks list (including approved frameworks)
      this.fetchFrameworks();
      
      // Refresh rejected frameworks
      this.fetchRejectedFrameworks();
      
      // If we have a selected approval open, refresh its details too
      if (this.selectedApproval && this.selectedApproval.FrameworkId) {
        const frameworkId = this.getFrameworkId(this.selectedApproval);
        console.log('Refreshing selected framework details for ID:', frameworkId);
        
        // Re-fetch the framework details to get updated policy/subpolicy statuses
        axios.get(`http://localhost:8000/api/frameworks/${frameworkId}/get-for-approval/`)
          .then(response => {
            console.log('Refreshed framework details:', response.data);
            
            if (response.data && response.data.ExtractedData) {
              // Update the selected approval with fresh data
              const updatedApproval = {
                ...this.selectedApproval,
                ...response.data,
                ExtractedData: response.data.ExtractedData
              };
              
              // Re-check framework approval eligibility
              this.checkFrameworkApprovalEligibility(updatedApproval);
              
              this.selectedApproval = updatedApproval;
              console.log('Updated selected approval with fresh data');
            }
          })
          .catch(error => {
            console.error('Error refreshing framework details:', error);
          });
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
    
    closeApprovalDetails() {
      this.selectedApproval = null;
      this.showDetails = false;
    },
    
    approveFramework() {
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for approval');
        return;
      }
      
      const frameworkId = this.getFrameworkId(this.selectedApproval);
      
      // Initialize framework approval if doesn't exist
      if (!this.selectedApproval.ExtractedData.framework_approval) {
        this.selectedApproval.ExtractedData.framework_approval = {};
      }
      this.selectedApproval.ExtractedData.framework_approval.approved = true;
      this.selectedApproval.ExtractedData.framework_approval.remarks = '';
      
      // Update the overall approval status immediately in UI
      this.selectedApproval.ApprovedNot = 1;
      this.selectedApproval.ExtractedData.Status = 'Approved';
      
      // Call the API to save the approval
      const approvalData = {
        ExtractedData: JSON.parse(JSON.stringify(this.selectedApproval.ExtractedData)),
        ApprovedNot: 1,
        UserId: this.userId,
        ReviewerId: this.userId
      };
      
      axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/submit-approval/`, approvalData)
        .then(response => {
          console.log('Framework approved successfully:', response.data);
          
          // Update the local approval with the returned data
          this.selectedApproval.Version = response.data.Version;
          this.selectedApproval.ApprovedDate = response.data.ApprovedDate;
          
          alert(`Framework approved successfully! Version: ${response.data.Version}`);
          
          // Refresh the frameworks list to show it in approved section
          this.fetchFrameworks();
        })
        .catch(error => {
          console.error('Error approving framework:', error);
          alert('Error approving framework: ' + (error.response?.data?.error || error.message));
          
          // Revert UI changes on error
          this.selectedApproval.ApprovedNot = null;
          this.selectedApproval.ExtractedData.Status = 'Under Review';
          if (this.selectedApproval.ExtractedData.framework_approval) {
            this.selectedApproval.ExtractedData.framework_approval.approved = null;
          }
        });
    },
    
    rejectFramework() {
      this.rejectingType = 'framework';
      this.showRejectModal = true;
    },
    
    cancelRejection() {
      this.showRejectModal = false;
      this.rejectionComment = '';
    },
    
    confirmRejection() {
      if (this.rejectingType === 'subpolicy') {
        this.confirmFrameworkSubpolicyRejection();
        return;
      }
      
      // Handle framework rejection (existing logic)
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected for rejection');
        this.showRejectModal = false;
        return;
      }
      
      const frameworkId = this.getFrameworkId(this.selectedApproval);
      
      // Initialize framework approval if doesn't exist
      if (!this.selectedApproval.ExtractedData.framework_approval) {
        this.selectedApproval.ExtractedData.framework_approval = {};
      }
      this.selectedApproval.ExtractedData.framework_approval.approved = false;
      this.selectedApproval.ExtractedData.framework_approval.remarks = this.rejectionComment;
      
      // Update the overall approval status immediately in UI
      this.selectedApproval.ApprovedNot = 0;
      this.selectedApproval.ExtractedData.Status = 'Rejected';
      
      // Call the API to save the rejection
      const rejectionData = {
        ExtractedData: JSON.parse(JSON.stringify(this.selectedApproval.ExtractedData)),
        ApprovedNot: 0,
        UserId: this.userId,
        ReviewerId: this.userId,
        remarks: this.rejectionComment
      };
      
      axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/submit-approval/`, rejectionData)
        .then(response => {
          console.log('Framework rejected successfully:', response.data);
          
          // Update the local approval with the returned data
          this.selectedApproval.Version = response.data.Version;
          
          alert(`Framework rejected successfully! Version: ${response.data.Version}`);
          
          // Refresh the frameworks list
          this.fetchFrameworks();
      
      // Close the rejection modal
      this.showRejectModal = false;
      this.rejectionComment = '';
        })
        .catch(error => {
          console.error('Error rejecting framework:', error);
          alert('Error rejecting framework: ' + (error.response?.data?.error || error.message));
          
          // Revert UI changes on error
          this.selectedApproval.ApprovedNot = null;
          this.selectedApproval.ExtractedData.Status = 'Under Review';
          if (this.selectedApproval.ExtractedData.framework_approval) {
            this.selectedApproval.ExtractedData.framework_approval.approved = null;
            this.selectedApproval.ExtractedData.framework_approval.remarks = '';
          }
          
          // Close the rejection modal
          this.showRejectModal = false;
          this.rejectionComment = '';
        });
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
          
          // Close the details view
          this.closeApprovalDetails();
          
          // Refresh the frameworks list
          this.fetchFrameworks();
        })
        .catch(error => {
          console.error('Error submitting review:', error);
          alert('Error submitting review: ' + (error.response?.data?.error || error.message));
        });
    },
    
    fetchRejectedFrameworks() {
      console.log('Fetching rejected frameworks with hierarchy...');
      
      // Get rejected framework approvals with full hierarchy
      axios.get('http://localhost:8000/api/rejected-frameworks-with-hierarchy/')
        .then(response => {
          console.log('Rejected frameworks with hierarchy response:', response.data);
          
          this.rejectedFrameworks = response.data.map(framework => ({
            FrameworkId: framework.FrameworkId,
            ApprovalId: framework.ApprovalId,
            ExtractedData: framework.ExtractedData || {
              type: 'framework',
              FrameworkName: 'Unknown Framework',
              Status: 'Rejected',
              policies: []
            },
            ApprovedNot: framework.ApprovedNot,
            Version: framework.Version,
            rejection_reason: framework.rejection_reason || 'No reason provided'
          }));
          
          console.log('Processed rejected frameworks:', this.rejectedFrameworks);
        })
        .catch(error => {
          console.error('Error fetching rejected frameworks with hierarchy:', error);
          
          // Fallback to the original method
          axios.get('http://localhost:8000/api/framework-approvals/')
            .then(response => {
              console.log('Fallback: All framework approvals response:', response.data);
              
              // Filter for rejected frameworks
              const rejectedApprovals = response.data.filter(approval => 
                approval.ApprovedNot === 0 || approval.ApprovedNot === false
              );
              
              // Get unique framework IDs for rejected frameworks
              const uniqueRejectedFrameworks = {};
              
              for (const approval of rejectedApprovals) {
                const frameworkId = approval.FrameworkId;
                
                // If we haven't seen this framework yet, or if this is a newer version
                if (!uniqueRejectedFrameworks[frameworkId] || 
                    this.compareVersions(approval.Version || 'u1', uniqueRejectedFrameworks[frameworkId].Version || 'u1') > 0) {
                  uniqueRejectedFrameworks[frameworkId] = approval;
                }
              }
              
              this.rejectedFrameworks = Object.values(uniqueRejectedFrameworks).map(approval => ({
                FrameworkId: approval.FrameworkId,
                ApprovalId: approval.ApprovalId,
                ExtractedData: approval.ExtractedData || {
                  type: 'framework',
                  FrameworkName: 'Unknown Framework',
                  Status: 'Rejected'
                },
                ApprovedNot: approval.ApprovedNot,
                Version: approval.Version,
                rejection_reason: approval.ExtractedData?.framework_approval?.remarks || 'No reason provided'
              }));
              
              console.log('Processed rejected frameworks (fallback):', this.rejectedFrameworks);
            })
            .catch(fallbackError => {
              console.error('Error fetching rejected frameworks (fallback):', fallbackError);
            });
        });
    },
    
    openRejectedItem(framework) {
      console.log('Opening rejected framework for editing:', framework);
      console.log('Framework ExtractedData:', framework.ExtractedData);
      console.log('Policies count:', framework.ExtractedData?.policies?.length || 0);
      
      // Create a deep copy to avoid reference issues
      this.editingFramework = JSON.parse(JSON.stringify(framework));
      
      // Ensure the editing framework has the complete structure
      if (!this.editingFramework.ExtractedData) {
        this.editingFramework.ExtractedData = {};
      }
      if (!this.editingFramework.ExtractedData.policies) {
        this.editingFramework.ExtractedData.policies = [];
      }
      
      console.log('Editing framework prepared:', this.editingFramework);
      console.log('Editing framework policies:', this.editingFramework.ExtractedData.policies);
      
      this.showEditModal = true;
    },
    
    closeEditModal() {
      this.showEditModal = false;
      this.editingFramework = null;
    },
    
    resubmitFramework(framework) {
      console.log('Resubmitting framework with hierarchy:', framework);
      console.log('Original ExtractedData:', JSON.stringify(framework.ExtractedData, null, 2));
      
      const frameworkId = this.getFrameworkId(framework);
      
      // Create a deep copy of the ExtractedData to avoid modifying the original
      const updatedExtractedData = JSON.parse(JSON.stringify(framework.ExtractedData));
      
      // Reset approval status for framework
      if (updatedExtractedData.approval) {
        updatedExtractedData.approval.approved = null;
        updatedExtractedData.approval.remarks = '';
      }
      if (updatedExtractedData.framework_approval) {
        updatedExtractedData.framework_approval.approved = null;
        updatedExtractedData.framework_approval.remarks = '';
      }
      
      // Reset all policy and subpolicy statuses to "Under Review" and keep edited values
      if (updatedExtractedData.policies) {
        updatedExtractedData.policies.forEach(policy => {
          // Reset status to Under Review for rejected policies
          if (policy.Status === 'Rejected') {
            policy.Status = 'Under Review';
            if (policy.approval) {
              policy.approval.approved = null;
              policy.approval.remarks = '';
            }
          }
          
          // Reset rejected subpolicies
          if (policy.subpolicies) {
            policy.subpolicies.forEach(subpolicy => {
              if (subpolicy.Status === 'Rejected') {
                subpolicy.Status = 'Under Review';
                if (subpolicy.approval) {
                  subpolicy.approval.approved = null;
                  subpolicy.approval.remarks = '';
                }
              }
            });
          }
        });
      }
      
      // Set framework status to Under Review
      updatedExtractedData.Status = 'Under Review';
      
      console.log('Updated ExtractedData before sending:', JSON.stringify(updatedExtractedData, null, 2));
      
      // Prepare comprehensive data for resubmission with the complete updated ExtractedData
      const resubmitData = {
        // Framework basic info (legacy support)
        FrameworkName: updatedExtractedData.FrameworkName,
        FrameworkDescription: updatedExtractedData.FrameworkDescription,
        Category: updatedExtractedData.Category,
        EffectiveDate: updatedExtractedData.EffectiveDate,
        StartDate: updatedExtractedData.StartDate,
        EndDate: updatedExtractedData.EndDate,
        Identifier: updatedExtractedData.Identifier,
        
        // Include complete hierarchy data with all edits
        ExtractedData: updatedExtractedData,
        
        // Reset approval status
        ApprovedNot: null
      };
      
      console.log('Resubmit data prepared:', JSON.stringify(resubmitData, null, 2));
      
      // Submit resubmission request using approval ID if available, otherwise framework ID
      const resubmitUrl = framework.ApprovalId 
        ? `http://localhost:8000/api/framework-approvals/${framework.ApprovalId}/resubmit/`
        : `http://localhost:8000/api/frameworks/${frameworkId}/resubmit/`;
      
      console.log('Submitting to URL:', resubmitUrl);
      
      axios.put(resubmitUrl, resubmitData)
        .then(response => {
          console.log('Framework resubmitted successfully:', response.data);
          
          // Show version information in the alert
          const version = response.data.version || response.data.Version || 'New Version';
          alert(`Framework resubmitted for review! New version: ${version}\n\nAll edited changes have been saved.`);
          
          // Close the edit modal
          this.closeEditModal();
          
          // Refresh the data
          this.fetchRejectedFrameworks();
          this.fetchFrameworks();
          
          console.log('Framework resubmission completed successfully');
        })
        .catch(error => {
          console.error('Error resubmitting framework:', error);
          console.error('Error details:', error.response?.data);
          
          const errorMessage = error.response?.data?.error || error.message;
          alert('Error resubmitting framework: ' + errorMessage);
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
    },
    compareVersions(v1, v2) {
      const v1Parts = v1.split('.');
      const v2Parts = v2.split('.');

      for (let i = 0; i < Math.max(v1Parts.length, v2Parts.length); i++) {
        const num1 = parseInt(v1Parts[i] || '0', 10);
        const num2 = parseInt(v2Parts[i] || '0', 10);
        if (num1 < num2) return -1;
        if (num1 > num2) return 1;
      }
      return 0;
    },
    checkFrameworkApprovalEligibility(approval) {
      if (!approval.ExtractedData || !approval.ExtractedData.policies) {
        approval.canApproveFramework = false;
        return;
      }
      
      const policies = approval.ExtractedData.policies;
      
      // Check if all policies are approved
      const allPoliciesApproved = policies.every(policy => {
        // Check if all subpolicies in this policy are approved
        const allSubpoliciesApproved = policy.subpolicies.every(sub => 
          sub.Status === 'Approved' && sub.approval?.approved === true
        );
        
        return policy.Status === 'Approved' && allSubpoliciesApproved;
      });
      
      // Framework can only be approved if all policies and their subpolicies are approved
      approval.canApproveFramework = allPoliciesApproved && policies.length > 0;
      
      console.log('Framework approval eligibility:', {
        frameworkId: approval.FrameworkId,
        canApprove: approval.canApproveFramework,
        totalPolicies: policies.length,
        allPoliciesApproved
      });
    },
    
    approveFrameworkSubpolicy(subpolicy, policy) {
      console.log('Approving subpolicy:', subpolicy.SubPolicyName, 'for policy:', policy.PolicyName);
      
      if (!this.selectedApproval || !this.selectedApproval.FrameworkId) {
        console.error('No framework selected');
        return;
      }
      
      const frameworkId = this.getFrameworkId(this.selectedApproval);
      
      // Set subpolicy approval status in UI immediately
      const originalStatus = subpolicy.Status;
      const originalApproval = subpolicy.approval ? { ...subpolicy.approval } : null;
      
      if (!subpolicy.approval) {
        subpolicy.approval = {};
      }
      subpolicy.approval.approved = true;
      subpolicy.approval.remarks = '';
      subpolicy.Status = 'Approved';
      
      console.log('Updated subpolicy UI status to Approved');
      
      // Call API to approve subpolicy
      axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/policies/${policy.PolicyId}/approve-subpolicy/${subpolicy.SubPolicyId}/`)
        .then(response => {
          console.log('Subpolicy approved successfully:', response.data);
          
          // Update policy status if all subpolicies are approved
          if (response.data.PolicyUpdated) {
            policy.Status = response.data.PolicyStatus;
            if (!policy.approval) {
              policy.approval = {};
            }
            policy.approval.approved = true;
            policy.approval.remarks = '';
            console.log(`Policy ${policy.PolicyId} automatically approved`);
          }
          
          // Update framework status if all policies are approved
          if (response.data.FrameworkUpdated) {
            this.selectedApproval.ExtractedData.Status = response.data.FrameworkStatus;
            this.selectedApproval.ApprovedNot = 1;
            console.log(`Framework ${frameworkId} automatically approved`);
          }
          
          // Always refresh the framework approval eligibility after any status change
          this.checkFrameworkApprovalEligibility(this.selectedApproval);
          
          // Refresh the main frameworks list to show updated status
          this.fetchFrameworks();
          
          // Show success message
          alert(response.data.message);
          
          console.log('Approval process completed successfully');
        })
        .catch(error => {
          console.error('Error approving subpolicy:', error);
          
          // Revert UI changes on error
          subpolicy.Status = originalStatus;
          if (originalApproval) {
            subpolicy.approval = originalApproval;
          } else {
            subpolicy.approval = { approved: null, remarks: '' };
          }
          
          // Show error message
          const errorMessage = error.response?.data?.error || error.message;
          alert('Error approving subpolicy: ' + errorMessage);
          
          console.log('Reverted UI changes due to API error');
        });
    },
    
    rejectFrameworkSubpolicy(subpolicy, policy) {
      // Open rejection modal for subpolicy
      this.rejectingType = 'subpolicy';
      this.rejectingSubpolicy = subpolicy;
      this.rejectingPolicy = policy;
      this.showRejectModal = true;
    },
    
    confirmFrameworkSubpolicyRejection() {
      if (!this.rejectingSubpolicy || !this.rejectingPolicy || !this.selectedApproval) {
        console.error('Missing data for subpolicy rejection');
        this.showRejectModal = false;
        return;
      }
      
      const frameworkId = this.getFrameworkId(this.selectedApproval);
      const subpolicy = this.rejectingSubpolicy;
      const policy = this.rejectingPolicy;
      
      // Update UI immediately
      if (!subpolicy.approval) {
        subpolicy.approval = {};
      }
      subpolicy.approval.approved = false;
      subpolicy.approval.remarks = this.rejectionComment;
      subpolicy.Status = 'Rejected';
      
      // Call API to reject subpolicy
      axios.put(`http://localhost:8000/api/frameworks/${frameworkId}/policies/${policy.PolicyId}/reject-subpolicy/${subpolicy.SubPolicyId}/`, {
        remarks: this.rejectionComment
      })
        .then(response => {
          console.log('Subpolicy rejected successfully:', response.data);
          
          // Update policy status (should be automatically rejected)
          if (response.data.PolicyUpdated) {
            policy.Status = response.data.PolicyStatus;
            policy.approval = { approved: false, remarks: this.rejectionComment };
            console.log(`Policy ${policy.PolicyId} automatically rejected`);
          }
          
          // Update framework status (should be automatically rejected)
          if (response.data.FrameworkUpdated) {
            this.selectedApproval.ExtractedData.Status = response.data.FrameworkStatus;
            this.selectedApproval.ApprovedNot = 0;
            console.log(`Framework ${frameworkId} automatically rejected`);
            
            // Refresh the frameworks list
            this.fetchFrameworks();
          }
          
          // Update framework approval eligibility
          this.checkFrameworkApprovalEligibility(this.selectedApproval);
          
          alert(response.data.message);
          
          // Close modal
          this.showRejectModal = false;
          this.rejectingSubpolicy = null;
          this.rejectingPolicy = null;
          this.rejectingType = '';
          this.rejectionComment = '';
        })
        .catch(error => {
          console.error('Error rejecting subpolicy:', error);
          alert('Error rejecting subpolicy: ' + (error.response?.data?.error || error.message));
          
          // Revert UI changes
          subpolicy.approval.approved = null;
          subpolicy.Status = 'Under Review';
          
          // Close modal
          this.showRejectModal = false;
          this.rejectingSubpolicy = null;
          this.rejectingPolicy = null;
          this.rejectingType = '';
          this.rejectionComment = '';
        });
    },
    
    checkDataChanges() {
      if (!this.editingFramework) return;
      
      console.log('=== DATA CHANGES VALIDATION ===');
      console.log('Framework Name:', this.editingFramework.ExtractedData.FrameworkName);
      console.log('Framework Description:', this.editingFramework.ExtractedData.FrameworkDescription);
      console.log('Category:', this.editingFramework.ExtractedData.Category);
      console.log('Dates:', {
        EffectiveDate: this.editingFramework.ExtractedData.EffectiveDate,
        StartDate: this.editingFramework.ExtractedData.StartDate,
        EndDate: this.editingFramework.ExtractedData.EndDate
      });
      
      if (this.editingFramework.ExtractedData.policies) {
        this.editingFramework.ExtractedData.policies.forEach((policy, pIndex) => {
          console.log(`Policy ${pIndex + 1} (${policy.PolicyId}):`, {
            PolicyName: policy.PolicyName,
            PolicyDescription: policy.PolicyDescription,
            Scope: policy.Scope,
            Objective: policy.Objective,
            Status: policy.Status
          });
          
          if (policy.subpolicies) {
            policy.subpolicies.forEach((subpolicy, sIndex) => {
              console.log(`  Subpolicy ${sIndex + 1} (${subpolicy.SubPolicyId}):`, {
                SubPolicyName: subpolicy.SubPolicyName,
                Description: subpolicy.Description,
                Control: subpolicy.Control,
                Status: subpolicy.Status
              });
            });
          }
        });
      }
      console.log('=== END VALIDATION ===');
    },
  },
  computed: {
    pendingApprovalsCount() {
      return this.approvals.filter(a => a.ApprovedNot === null).length;
    },
    approvedApprovalsCount() {
      return this.approvedFrameworks.length;
    },
    rejectedApprovalsCount() {
      return this.rejectedFrameworks.length;
    },
    sortedFrameworks() {
      return [...this.approvals].sort((a, b) => {
        const dateA = new Date(a.ExtractedData?.CreatedByDate || 0);
        const dateB = new Date(b.ExtractedData?.CreatedByDate || 0);
        return dateB - dateA; // Most recent first
      });
    },
  }
}
</script>

<style scoped>
@import './FrameworkApprover.css';
</style> 