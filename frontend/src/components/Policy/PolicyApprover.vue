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
        <li v-for="policy in sortedPolicies" 
            :key="policy.ApprovalId" 
            :class="{'new-policy': isNewPolicy(policy)}">
          <strong class="clickable" @click="openApprovalDetails(policy)">
            {{ getPolicyId(policy) }}
          </strong>
          <span class="item-type-badge" :class="{
            'policy-badge': !policy.ExtractedData.type || policy.ExtractedData.type === 'policy',
            'subpolicy-badge': policy.ExtractedData.type === 'subpolicy'
          }">
            {{ policy.ExtractedData.type === 'subpolicy' ? 'Subpolicy' : 'Policy' }}
          </span>
          <span class="date-info">
            {{ formatDate(policy.ExtractedData?.CreatedByDate || policy.created_at) }}
          </span>
          <span v-if="isNewPolicy(policy)" class="new-badge">NEW</span>
          <span class="policy-scope">{{ policy.ExtractedData.Scope || 'No Scope' }}</span>
          <span class="assigned-by">
            <img class="assigned-avatar" :src="policy.ExtractedData.CreatedByAvatar || 'https://randomuser.me/api/portraits/men/32.jpg'" alt="avatar" />
            {{ policy.ExtractedData.CreatedByName || 'System' }}
          </span>
          <span v-if="policy.ApprovedNot === null" class="approval-status pending">(Pending)</span>
          <span v-else-if="policy.ApprovedNot === true" class="approval-status approved">(Approved)</span>
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
          Details: {{ getPolicyId(selectedApproval) }}
          <span v-if="selectedApproval.showingApprovedOnly" class="approved-only-badge">
            Showing Approved Only
          </span>
        </h3>
        <button class="close-btn" @click="closeApprovalDetails">Close</button>
        
        <!-- Policy/Compliance Approval Section -->
        <div class="policy-approval-section">
          <h4>{{ isComplianceApproval ? 'Compliance' : 'Policy' }} Approval</h4>
          
          <!-- Add policy status indicator -->
          <div class="policy-status-indicator">
            <span class="status-label">Status:</span>
            <span class="status-value" :class="{
              'status-approved': selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved',
              'status-rejected': selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected',
              'status-pending': selectedApproval.ApprovedNot === null && selectedApproval.ExtractedData?.Status !== 'Approved' && selectedApproval.ExtractedData?.Status !== 'Rejected'
            }">
              {{ selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved' ? 'Approved' : 
                 selectedApproval.ApprovedNot === false || selectedApproval.ExtractedData?.Status === 'Rejected' ? 'Rejected' : 
                 'Under Review' }}
            </span>
          </div>
          
          <div class="policy-actions">
            <button class="submit-btn" @click="submitReview()" :disabled="isComplianceApproval ? false : hasUnreviewedSubpolicies">
              <i class="fas fa-paper-plane"></i> Submit Review
            </button>
          </div>
          
          <!-- Add this section to show policy approval status - hide when already showing in the indicator -->
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
            
            <!-- Show approved date if approved -->
            <div v-if="approvalStatus.approved === true && selectedApproval.ApprovedDate" class="policy-approved-date">
              <div class="date-label">Approved Date:</div>
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
                        approved: sub.approval?.approved === true || (selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved'),
                        rejected: sub.approval?.approved === false && !(selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved'),
                        pending: sub.approval?.approved === null && !sub.resubmitted && !(selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved'),
                        resubmitted: sub.approval?.approved === null && sub.resubmitted && !(selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved')
                      }"
                    >
                      {{
                        (sub.approval?.approved === true || (selectedApproval.ApprovedNot === true || selectedApproval.ExtractedData?.Status === 'Approved'))
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
                  <!-- Add these buttons inside the subpolicies view, under the approval buttons -->
                  <div class="subpolicy-actions">
                    <template v-if="isReviewer">
                      <!-- Show approve/reject buttons for reviewer -->
                      <button 
                        v-if="sub.Status === 'Under Review' || !sub.Status"
                        @click="approveSubpolicy(sub)" 
                        class="approve-button"
                      >
                        Approve
                      </button>
                      <button 
                        v-if="sub.Status === 'Under Review' || !sub.Status"
                        @click="rejectSubpolicy(sub)" 
                        class="reject-button"
                      >
                        Reject
                      </button>
                    </template>
                    
                    <!-- For users (not reviewers), add edit button for rejected subpolicies -->
                    <template v-else>
                      <button 
                        v-if="sub.Status === 'Rejected'"
                        @click="openEditSubpolicyModal(sub)" 
                        class="edit-button"
                      >
                        Edit & Resubmit
                      </button>
                    </template>
                  </div>
                </li>
              </ul>
            </template>
          </div>
        </div>

        <!-- Add this inside the policy-details-content div -->
        <div v-if="selectedApproval && selectedApproval.PolicyId" class="policy-detail-row">
          <strong>Policy ID:</strong> <span>{{ getPolicyId(selectedApproval) }}</span>
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
              {{ getPolicyId(policy) }}
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
        <h3>Edit & Resubmit Compliance: {{ getPolicyId(editingCompliance) }}</h3>
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
        <h3>Edit & Resubmit Policy: {{ getPolicyId(editingPolicy) }}</h3>
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
          
          <div v-for="sub in rejectedSubpoliciesInPolicy" :key="sub.Identifier" class="subpolicy-edit-item">
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
    <div v-if="showEditSubpolicyModal" class="modal">
      <div class="modal-content edit-modal">
        <span class="close" @click="closeEditSubpolicyModal">&times;</span>
        <h2>Edit Rejected Subpolicy</h2>
        <div v-if="editingSubpolicy">
          <div class="form-group">
            <label>Subpolicy Name:</label>
            <input type="text" v-model="editingSubpolicy.SubPolicyName" disabled />
        </div>
          <div class="form-group">
            <label>Identifier:</label>
            <input type="text" v-model="editingSubpolicy.Identifier" disabled />
          </div>
          <div class="form-group">
          <label>Description:</label>
            <textarea v-model="editingSubpolicy.Description" @input="trackChanges"></textarea>
        </div>
          <div class="form-group">
          <label>Control:</label>
            <textarea v-model="editingSubpolicy.Control" @input="trackChanges"></textarea>
        </div>
          <div class="form-group">
            <label>Rejection Reason:</label>
            <p class="rejection-reason">{{ editingSubpolicy.approval?.remarks || 'No reason provided' }}</p>
        </div>
          
          <div v-if="hasChanges" class="changes-summary">
            <div class="changes-header">
              <i class="fas fa-exclamation-circle"></i> Changes detected
            </div>
            <div class="changes-content">
              <div v-if="editingSubpolicy.Description !== editingSubpolicy.originalDescription" class="change-item">
                Description has been modified
              </div>
              <div v-if="editingSubpolicy.Control !== editingSubpolicy.originalControl" class="change-item">
                Control has been modified
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button 
              class="resubmit-btn" 
              @click="resubmitSubpolicy()" 
              :disabled="!hasChanges"
            >
              {{ hasChanges ? 'Resubmit with Changes' : 'Make changes to resubmit' }}
            </button>
            <button class="cancel-btn" @click="closeEditSubpolicyModal">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Subpolicies Modal -->
    <div v-if="showSubpoliciesModal && selectedPolicyForSubpolicies" class="subpolicies-modal">
      <div class="subpolicies-modal-content">
        <h3>
          <span v-if="isReviewer">Subpolicies for {{ getPolicyId(selectedPolicyForSubpolicies) }}</span>
          <span v-else>Edit Rejected Subpolicies for {{ getPolicyId(selectedPolicyForSubpolicies) }}</span>
        </h3>
        <button class="close-btn" @click="closeSubpoliciesModal">Close</button>
        
        <!-- Filter to only show rejected subpolicies in user mode -->
        <div v-for="sub in filteredSubpolicies" :key="sub.Identifier" class="subpolicy-status" :class="{'resubmitted-item': sub.resubmitted}">
          <div class="subpolicy-header">
          <div>
            <span class="subpolicy-id">{{ sub.Identifier }}</span> :
            <span class="subpolicy-name">{{ sub.SubPolicyName }}</span>
            </div>
            <span
              class="badge"
              :class="{
                approved: sub.approval?.approved === true || (selectedPolicyForSubpolicies.ApprovedNot === true || selectedPolicyForSubpolicies.ExtractedData?.Status === 'Approved'),
                rejected: sub.approval?.approved === false && !(selectedPolicyForSubpolicies.ApprovedNot === true || selectedPolicyForSubpolicies.ExtractedData?.Status === 'Approved'),
                pending: sub.approval?.approved === null && !sub.resubmitted && !(selectedPolicyForSubpolicies.ApprovedNot === true || selectedPolicyForSubpolicies.ExtractedData?.Status === 'Approved'),
                resubmitted: sub.approval?.approved === null && sub.resubmitted && !(selectedPolicyForSubpolicies.ApprovedNot === true || selectedPolicyForSubpolicies.ExtractedData?.Status === 'Approved')
              }"
            >
              {{
                (sub.approval?.approved === true || (selectedPolicyForSubpolicies.ApprovedNot === true || selectedPolicyForSubpolicies.ExtractedData?.Status === 'Approved'))
                  ? 'Approved'
                  : sub.approval?.approved === false
                  ? 'Rejected'
                  : sub.resubmitted
                  ? 'Resubmitted'
                  : 'Pending'
              }}
            </span>
          </div>
          
          <div class="subpolicy-version" v-if="sub.resubmitted && isReviewer">
            <span class="version-tag">Version: {{ getSubpolicyVersion(sub) }}</span>
          </div>

          <div class="subpolicy-content">
          <div><strong>Description:</strong> {{ sub.Description }}</div>
          <div><strong>Control:</strong> {{ sub.Control }}</div>
            
            <!-- Show rejection reason for rejected items -->
          <div v-if="sub.approval?.approved === false">
              <strong>Rejection Reason:</strong> {{ sub.approval?.remarks }}
          </div>
            
            <!-- Show edit history for resubmitted items -->
            <div v-if="sub.resubmitted && isReviewer" class="edit-history">
              <div class="edit-history-header">
                <i class="fas fa-history"></i> Resubmitted with Changes
              </div>
              <div class="edit-history-content">
                <div class="edit-field">
                  <div v-if="sub.previousVersion">
                    <div class="field-label">Original Description:</div>
                    <div class="field-previous">{{ sub.previousVersion.Description || 'Not available' }}</div>
                  </div>
                  <div class="field-current">
                    <div class="field-label">Updated Description:</div>
                    <div class="field-value">{{ sub.Description }}</div>
                  </div>
                </div>
                <div class="edit-field">
                  <div v-if="sub.previousVersion">
                    <div class="field-label">Original Control:</div>
                    <div class="field-previous">{{ sub.previousVersion.Control || 'Not available' }}</div>
                  </div>
                  <div class="field-current">
                    <div class="field-label">Updated Control:</div>
                    <div class="field-value">{{ sub.Control }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Show Approve/Reject buttons if pending and in reviewer mode -->
          <div v-if="isReviewer && (sub.approval?.approved === null || sub.approval?.approved === undefined)" class="subpolicy-actions">
            <button class="approve-btn" @click="approveSubpolicyFromModal(sub)">Approve</button>
            <button class="reject-btn" @click="rejectSubpolicyFromModal(sub)">Reject</button>
          </div>
          
          <!-- Edit form for rejected subpolicies -->
          <div v-if="sub.approval?.approved === false || sub.Status === 'Rejected'">
            <div v-if="sub.showEditForm">
              <!-- Inline edit form -->
              <div class="subpolicy-inline-edit">
                <h4>Edit Rejected Subpolicy</h4>
                <div>
                  <label>Name:</label>
                  <input v-model="sub.SubPolicyName" disabled />
                </div>
                <div>
                  <label>Description:</label>
                  <textarea v-model="sub.Description"></textarea>
                </div>
                <div>
                  <label>Control:</label>
                  <textarea v-model="sub.Control"></textarea>
                </div>
                <div class="subpolicy-edit-actions">
                  <button class="resubmit-btn" @click="resubmitSubpolicyDirect(sub)">Resubmit for Review</button>
                  <button v-if="isReviewer" class="cancel-btn" @click="hideEditFormInline(sub)">Cancel</button>
                </div>
              </div>
            </div>
            <button v-else class="edit-btn" @click="showEditFormInline(sub)">Edit & Resubmit</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Role toggle for testing -->
    <div class="role-toggle">
      <label>
        <input type="checkbox" v-model="isReviewer">
        <span>{{ isReviewer ? 'Reviewer Mode' : 'User Mode' }}</span>
      </label>
      <div v-if="!isReviewer" class="debug-info">
        Found {{ rejectedSubpolicies.length }} rejected subpolicies
      </div>
    </div>

    <!-- Tabs for different sections -->
    <div class="tabs">
      <button 
        :class="{'active': activeTab === 'pending'}"
        @click="activeTab = 'pending'"
      >
        Pending Tasks
      </button>
      <button 
        :class="{'active': activeTab === 'rejected'}"
        @click="activeTab = 'rejected'"
      >
        Rejected Items
      </button>
    </div>
    
    <!-- Pending Tasks Tab -->
    <div v-if="activeTab === 'pending'" class="tab-content">
      <!-- Existing content for pending tasks -->
      <div v-if="isReviewer">
        <h2>Pending Approvals</h2>
        <ul class="approval-list">
          <li v-for="approval in approvals" :key="approval.ApprovalId" class="approval-item">
            <!-- Existing content -->
          </li>
        </ul>
      </div>
      
      <div v-else>
        <h2>No pending tasks for users</h2>
        <p>Switch to Reviewer Mode to see pending approvals</p>
      </div>
    </div>
    
    <!-- Rejected Items Tab -->
    <div v-if="activeTab === 'rejected'" class="tab-content">
      <div v-if="!isReviewer">
        <h2>Rejected Subpolicies</h2>
        <div v-if="rejectedSubpolicies.length === 0" class="no-items">
          No rejected subpolicies found.
        </div>
        <ul v-else class="rejected-list">
          <li v-for="item in rejectedSubpolicies" :key="item.SubPolicyId" class="rejected-item">
            <div class="rejected-header">
              <h3>{{ item.SubPolicyName }}</h3>
              <span class="status rejected">Rejected</span>
            </div>
            <div class="rejected-details">
              <p><strong>Policy:</strong> {{ item.PolicyName }}</p>
              <p><strong>Identifier:</strong> {{ item.Identifier }}</p>
              <p><strong>Description:</strong> {{ item.Description }}</p>
              <p v-if="item.approval && item.approval.remarks">
                <strong>Rejection Reason:</strong> {{ item.approval.remarks }}
              </p>
            </div>
            <div class="rejected-actions">
              <button @click="openEditSubpolicyModal(item)" class="edit-button">
                Edit & Resubmit
              </button>
            </div>
          </li>
        </ul>
      </div>
      
      <div v-else>
        <h2>Rejected Policies</h2>
        <div v-if="rejectedPolicies.length === 0" class="no-items">
          No rejected policies found.
        </div>
        <ul v-else class="rejected-list">
          <li v-for="policy in rejectedPolicies" :key="policy.PolicyId" class="rejected-item">
            <div class="rejected-header">
              <h3>{{ policy.ExtractedData.PolicyName }}</h3>
              <span class="status rejected">Rejected</span>
            </div>
            <div class="rejected-details">
              <p><strong>Identifier:</strong> {{ policy.ExtractedData.Identifier || 'N/A' }}</p>
              <p><strong>Scope:</strong> {{ policy.ExtractedData.Scope || 'No Scope' }}</p>
              <p><strong>Description:</strong> {{ policy.ExtractedData.PolicyDescription || 'No description' }}</p>
            </div>
            <div class="rejected-actions">
              <button @click="openEditModal = true; editingPolicy = policy" class="edit-button">
                Edit & Resubmit
              </button>
              <button @click="openSubpoliciesModal(policy)" class="view-button">
                View Subpolicies
              </button>
            </div>
          </li>
        </ul>
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
      rejectedSubpolicies: [],
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
      isReviewer: true, // Set based on user role, for testing
      activeTab: 'pending', // Track active tab
    }
  },
  mounted() {
    // Replace this method to fetch policies instead of approvals
    this.fetchPolicies();
    this.fetchRejectedPolicies();
    
    // Also fetch rejected subpolicies if in user mode
    if (!this.isReviewer) {
      this.fetchRejectedSubpolicies();
    }
  },
  watch: {
    // Watch for changes in isReviewer and fetch appropriate data
    isReviewer(newVal) {
      if (newVal) {
        // If switched to reviewer mode
        this.fetchPolicies();
        this.fetchRejectedPolicies();
      } else {
        // If switched to user mode
        this.fetchRejectedSubpolicies();
      }
    }
  },
  methods: {
    // Update the method to fetch policies and policy approvals
    fetchPolicies() {
      // Always fetch from policies endpoint regardless of mode
      console.log('Fetching policies...');
      axios.get('http://localhost:8000/api/policies/')
        .then(response => {
          console.log('Policies response:', response.data);
          // Map policies to the expected format
          this.approvals = response.data.map(policy => {
            // For each policy, fetch the latest approval based on role
            const role = this.isReviewer ? 'reviewer' : 'user';
            this.fetchLatestApprovalForPolicy(policy.PolicyId, role);
            
            // Map subpolicies to include proper SubPolicyId
            const mappedSubpolicies = policy.subpolicies?.map(sub => ({
              ...sub,
              SubPolicyId: sub.SubPolicyId,
              PolicyId: policy.PolicyId
            })) || [];
            
            return {
              PolicyId: policy.PolicyId,
              ExtractedData: {
                type: 'policy',
                PolicyName: policy.PolicyName,
                CreatedByName: policy.CreatedByName,
                CreatedByDate: policy.CreatedByDate,
                Scope: policy.Scope,
                Status: policy.Status,
                Objective: policy.Objective,
                subpolicies: mappedSubpolicies
              },
              ApprovedNot: policy.Status === 'Approved' ? true : 
                          policy.Status === 'Rejected' ? false : null
            };
          });
          console.log('Processed policies:', this.approvals.length);
        })
        .catch(error => {
          console.error('Error fetching policies:', error);
        });
    },
    // Add this new method
    fetchLatestApprovalForPolicy(policyId, role) {
      axios.get(`http://localhost:8000/api/policy-approvals/latest-by-role/${policyId}/${role}/`)
        .then(response => {
          console.log(`Latest ${role} approval for policy ${policyId}:`, response.data);
          
          // Find the policy in our array and update it with the latest approval data
          const policyIndex = this.approvals.findIndex(p => 
            p.PolicyId === policyId || 
            (typeof p.PolicyId === 'object' && p.PolicyId.PolicyId === policyId)
          );
          
          if (policyIndex !== -1) {
            // Update the policy with the latest approval data
            const policy = this.approvals[policyIndex];
            
            // Merge the ExtractedData from the approval with our existing policy data
            if (response.data.ExtractedData) {
              this.approvals[policyIndex].ExtractedData = {
                ...policy.ExtractedData,
                ...response.data.ExtractedData
              };
            }
            
            // Update approval status
            this.approvals[policyIndex].ApprovedNot = response.data.ApprovedNot;
            this.approvals[policyIndex].Version = response.data.Version;
            this.approvals[policyIndex].ApprovedDate = response.data.ApprovedDate;
          }
        })
        .catch(error => {
          // If 404, it means no approval found, which is fine
          if (error.response && error.response.status !== 404) {
            console.error(`Error fetching latest ${role} approval for policy ${policyId}:`, error);
          }
        });
    },
    // Update the refresh method
    refreshData() {
      this.fetchPolicies();
      if (!this.isReviewer) {
        this.fetchRejectedSubpolicies();
      } else {
      this.fetchRejectedPolicies();
      }
    },
    // Update the refresh approvals method
    refreshApprovals() {
      this.fetchPolicies();
    },
    // Update fetchRejectedPolicies to use policy table
    fetchRejectedPolicies() {
      console.log('Fetching rejected policies...');
      axios.get('http://localhost:8000/api/policies/?status=Rejected')
        .then(response => {
          console.log('Rejected policies response:', response.data);
          if (Array.isArray(response.data) && response.data.length > 0) {
            this.rejectedPolicies = response.data.map(policy => ({
              PolicyId: policy.PolicyId,
              ExtractedData: {
                type: 'policy',
                PolicyName: policy.PolicyName,
                CreatedByName: policy.CreatedByName,
                CreatedByDate: policy.CreatedByDate,
                Scope: policy.Scope,
                Status: policy.Status,
                Objective: policy.Objective,
                subpolicies: policy.subpolicies || []
              },
              ApprovedNot: false,
              main_policy_rejected: true
            }));
            console.log('Processed rejected policies:', this.rejectedPolicies.length);
          } else {
            console.log('No rejected policies found from API');
            // We'll check for policies with rejected subpolicies instead
            this.fetchPoliciesWithRejectedSubpolicies();
          }
        })
        .catch(error => {
          console.error('Error fetching rejected policies:', error);
        });
    },
    // Add a method to fetch policies that have rejected subpolicies
    fetchPoliciesWithRejectedSubpolicies() {
      console.log('Fetching policies with rejected subpolicies...');
      axios.get('http://localhost:8000/api/policies/')
        .then(response => {
          console.log('All policies response:', response.data.length);
          if (Array.isArray(response.data)) {
            // Filter policies that have at least one rejected subpolicy
            const policiesWithRejected = response.data.filter(policy => 
              policy.subpolicies && 
              policy.subpolicies.some(sub => sub.Status === 'Rejected')
            );
            
            console.log('Found policies with rejected subpolicies:', policiesWithRejected.length);
            
            if (policiesWithRejected.length > 0) {
              this.rejectedPolicies = policiesWithRejected.map(policy => ({
                PolicyId: policy.PolicyId,
                ExtractedData: {
                  type: 'policy',
                  PolicyName: policy.PolicyName,
                  CreatedByName: policy.CreatedByName,
                  CreatedByDate: policy.CreatedByDate,
                  Scope: policy.Scope,
                  Status: policy.Status,
                  Objective: policy.Objective,
                  subpolicies: policy.subpolicies || []
                },
                ApprovedNot: policy.Status === 'Rejected' ? false : null,
                main_policy_rejected: policy.Status === 'Rejected'
              }));
            }
          }
      })
      .catch(error => {
          console.error('Error fetching policies with rejected subpolicies:', error);
      });
    },
    // Modify submitReview to update policy status
    submitReview() {
      if (!this.isComplianceApproval) {
        // Policy review submission - now directly getting PolicyId
        const policyId = this.selectedApproval.PolicyId;
        
        // Determine the new status based on approval state
        const newStatus = this.selectedApproval.ApprovedNot === true 
          ? 'Approved' 
          : this.selectedApproval.ApprovedNot === false 
            ? 'Rejected' 
            : 'Under Review';
      
        // Update the policy status
        axios.put(`http://localhost:8000/api/policies/${policyId}/`, {
          Status: newStatus,
          // Include any other fields that might have been modified
          Scope: this.selectedApproval.ExtractedData.Scope,
          Objective: this.selectedApproval.ExtractedData.Objective
      })
      .then(response => {
          console.log('Policy updated successfully:', response.data);
          alert('Policy review submitted successfully!');
        
          // Close the details view
          this.closeApprovalDetails();
          
          // Refresh the policies list
          this.refreshApprovals();
      })
      .catch(error => {
          console.error('Error submitting review:', error);
          alert('Error submitting review: ' + (error.response?.data?.error || error.message));
        });
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
          // Update approved date if provided
          if (response.data.ApprovedDate) {
            this.selectedApproval.ApprovedDate = response.data.ApprovedDate;
          }
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
    // Update resubmitPolicy to change status back to "Under Review"
    resubmitPolicy(policy) {
      const policyId = typeof policy.PolicyId === 'object' 
        ? policy.PolicyId.PolicyId 
        : policy.PolicyId;
        
      axios.put(`http://localhost:8000/api/policies/${policyId}/`, {
        Status: 'Under Review',
        Scope: policy.ExtractedData.Scope,
        Objective: policy.ExtractedData.Objective
      })
      .then(() => {
        alert('Policy resubmitted for review!');
        this.showEditModal = false;
        this.fetchRejectedPolicies();
      })
      .catch(error => {
        alert('Error resubmitting policy');
        console.error(error);
      });
    },
    // Update approveSubpolicy to handle subpolicy approval
    approveSubpolicy(subpolicy) {
      // Set subpolicy approval status
      if (!subpolicy.approval) {
        subpolicy.approval = {};
      }
      subpolicy.approval.approved = true;
      subpolicy.approval.remarks = '';
      
      // Update subpolicy status via API
      axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/`, {
        Status: 'Approved'
      })
      .then(response => {
        console.log('Subpolicy status updated successfully:', response.data);
        
        // Create policy approval for this subpolicy approval
        return axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/review/`, {
          Status: 'Approved'
        });
      })
      .then(response => {
        console.log('Subpolicy approval created successfully:', response.data);
        
        // Check if parent policy status was updated (all subpolicies approved)
        if (response.data.PolicyUpdated) {
          console.log(`Policy status updated to: ${response.data.PolicyStatus}`);
          
          // If parent policy was updated, refresh the policies list
          this.fetchPolicies();
          
          // Also update the UI to show policy is now approved
          if (this.selectedApproval && this.selectedApproval.ExtractedData) {
            this.selectedApproval.ExtractedData.Status = response.data.PolicyStatus;
          }
        }
        
        // Check if all subpolicies are now approved
        this.checkAllSubpoliciesApproved();
      })
      .catch(error => {
        console.error('Error approving subpolicy:', error);
        alert('Error approving subpolicy. Please try again.');
      });
    },
    
    // Add a method to check if all subpolicies are approved
    checkAllSubpoliciesApproved() {
      if (!this.selectedApproval || 
          !this.selectedApproval.ExtractedData || 
          !this.selectedApproval.ExtractedData.subpolicies ||
          this.selectedApproval.ExtractedData.subpolicies.length === 0) {
        return;
      }
      
      const subpolicies = this.selectedApproval.ExtractedData.subpolicies;
      const allApproved = subpolicies.every(sub => sub.approval?.approved === true);
      
      if (allApproved) {
        console.log('All subpolicies are approved! The policy should be automatically approved');
        
        // Automatically set policy approval to true
        if (!this.selectedApproval.ExtractedData.policy_approval) {
          this.selectedApproval.ExtractedData.policy_approval = {};
        }
        this.selectedApproval.ExtractedData.policy_approval.approved = true;
        this.selectedApproval.ApprovedNot = true;
        
        // Show notification to user
        alert('All subpolicies are approved! The policy has been automatically approved.');
      }
    },
    // Add the missing rejectSubpolicy method
    rejectSubpolicy(subpolicy) {
      // Open rejection modal for subpolicy
      this.rejectingType = 'subpolicy';
      this.rejectingSubpolicy = subpolicy;
      this.showRejectModal = true;
    },
    // Add the missing cancelRejection method
    cancelRejection() {
      this.showRejectModal = false;
      this.rejectingSubpolicy = null;
      this.rejectingType = '';
      this.rejectionComment = '';
    },
    // Update rejectSubpolicy via confirmRejection
    confirmRejection() {
      if (this.rejectingType === 'policy' && this.rejectingPolicy) {
        // Handle policy rejection
        const policyId = typeof this.rejectingPolicy.PolicyId === 'object' 
          ? this.rejectingPolicy.PolicyId.PolicyId 
          : this.rejectingPolicy.PolicyId;
        
        console.log('Rejecting policy with ID:', policyId);
        
        axios.put(`http://localhost:8000/api/policies/${policyId}/`, {
          Status: 'Rejected'
        })
        .then(() => {
          // Update local state
          this.rejectingPolicy.ExtractedData.Status = 'Rejected';
          this.rejectingPolicy.policy_approval = { 
            approved: false, 
            remarks: this.rejectionComment 
          };
          
          // Close modal
          this.showRejectModal = false;
          this.rejectingPolicy = null;
          this.rejectingType = '';
          this.rejectionComment = '';
        })
        .catch(error => {
          console.error('Error rejecting policy:', error);
          alert('Error rejecting policy: ' + (error.response?.data?.error || error.message));
        });
      } 
      else if (this.rejectingType === 'subpolicy' && this.rejectingSubpolicy) {
        if (!this.rejectingSubpolicy.SubPolicyId) {
          console.error('Missing SubPolicyId, cannot reject subpolicy', this.rejectingSubpolicy);
          alert('Error: Cannot reject subpolicy - missing SubPolicyId');
          this.showRejectModal = false;
          this.rejectingSubpolicy = null;
          this.rejectingType = '';
          this.rejectionComment = '';
          return;
        }
        
        console.log('Rejecting subpolicy with ID:', this.rejectingSubpolicy.SubPolicyId);
        
        // Ensure Status is a string, not null
        const statusToSend = 'Rejected';
        console.log('Sending data:', { Status: statusToSend });
        
        // First update subpolicy status via API
        axios.put(`http://localhost:8000/api/subpolicies/${this.rejectingSubpolicy.SubPolicyId}/`, {
          Status: statusToSend
        })
      .then(response => {
          console.log('Subpolicy status updated successfully:', response.data);
          
          // Then save the rejection in the PolicyApproval table
          return axios.put(`http://localhost:8000/api/subpolicies/${this.rejectingSubpolicy.SubPolicyId}/review/`, {
            Status: statusToSend,
            remarks: this.rejectionComment
          });
        })
        .then(approvalResponse => {
          console.log('Policy approval created successfully:', approvalResponse.data);
          
          // Update local state
          if (!this.rejectingSubpolicy.approval) {
            this.rejectingSubpolicy.approval = {};
          }
          
          this.rejectingSubpolicy.Status = 'Rejected';
          this.rejectingSubpolicy.approval.approved = false;
          this.rejectingSubpolicy.approval.remarks = this.rejectionComment;
          
          // Close modal
          this.showRejectModal = false;
          this.rejectingSubpolicy = null;
          this.rejectingType = '';
          this.rejectionComment = '';
          
          // Fetch rejected subpolicies if in user mode
          if (!this.isReviewer) {
            this.fetchRejectedSubpolicies();
        }
      })
      .catch(error => {
          console.error('Error rejecting subpolicy:', error);
          alert('Error rejecting subpolicy. Please try again.');
        });
      }
    },
    getPolicyId(policy) {
      if (policy.PolicyId) {
        return typeof policy.PolicyId === 'object' ? policy.PolicyId.PolicyId : policy.PolicyId;
      }
      return policy.ApprovalId;
    },
    openApprovalDetails(approval) {
      // Fetch the latest approval data before opening details
      const role = this.isReviewer ? 'reviewer' : 'user';
      const policyId = this.getPolicyId(approval);
      
      axios.get(`http://localhost:8000/api/policy-approvals/latest-by-role/${policyId}/${role}/`)
        .then(response => {
          console.log(`Latest ${role} approval data:`, response.data);
          
          // Merge the approval data with our existing policy data
          this.selectedApproval = {
            ...approval,
            ExtractedData: {
              ...approval.ExtractedData,
              ...response.data.ExtractedData
            },
            ApprovedNot: response.data.ApprovedNot,
            Version: response.data.Version,
            ApprovedDate: response.data.ApprovedDate
          };
          
          // If policy is approved, filter subpolicies to only show approved ones
          if (this.selectedApproval.ExtractedData && 
              (this.selectedApproval.ApprovedNot === true || this.selectedApproval.ExtractedData.Status === 'Approved') && 
              this.selectedApproval.ExtractedData.subpolicies) {
            
            // When a policy is approved, all its subpolicies should be treated as approved
            this.selectedApproval.ExtractedData.subpolicies = this.selectedApproval.ExtractedData.subpolicies.map(sub => {
              // Mark all subpolicies as approved when parent policy is approved
              if (!sub.approval) {
                sub.approval = {};
              }
              sub.approval.approved = true;
              sub.Status = 'Approved';
              return sub;
            });
            
            // Add a flag to indicate this is showing only accepted items
            this.selectedApproval.showingApprovedOnly = true;
          }
          
          this.showDetails = true;
        })
        .catch(error => {
          // If no approval found, just use the existing data
          if (error.response && error.response.status === 404) {
            this.selectedApproval = approval;
            this.showDetails = true;
          } else {
            console.error(`Error fetching latest ${role} approval:`, error);
            alert('Error loading approval details. Please try again.');
          }
        });
    },
    closeApprovalDetails() {
      this.selectedApproval = null;
      this.showDetails = false;
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
      console.log('Opening inline edit form for subpolicy:', subpolicy.SubPolicyId);
      
      // Store original values before editing
      subpolicy.originalDescription = subpolicy.Description;
      subpolicy.originalControl = subpolicy.Control;
      
      // Show the edit form
      subpolicy.showEditForm = true;
    },
    hideEditFormInline(subpolicy) {
      subpolicy.showEditForm = false;
    },
    resubmitSubpolicy() {
      if (!this.editingSubpolicy || !this.editingSubpolicy.SubPolicyId) {
        console.error('Missing SubPolicyId, cannot resubmit subpolicy', this.editingSubpolicy);
        alert('Error: Cannot resubmit subpolicy - missing SubPolicyId');
        return;
      }
      
      // Check if any changes were made
      if (!this.hasChanges) {
        alert('No changes detected. Please modify the subpolicy before resubmitting.');
        return;
      }
      
      console.log('Resubmitting subpolicy with ID:', this.editingSubpolicy.SubPolicyId);
      console.log('Changes detected:');
      
      if (this.editingSubpolicy.Description !== this.editingSubpolicy.originalDescription) {
        console.log('- Description changed from:', this.editingSubpolicy.originalDescription);
        console.log('- Description changed to:', this.editingSubpolicy.Description);
      }
      
      if (this.editingSubpolicy.Control !== this.editingSubpolicy.originalControl) {
        console.log('- Control changed from:', this.editingSubpolicy.originalControl);
        console.log('- Control changed to:', this.editingSubpolicy.Control);
      }
      
      // Store previous version for comparison
      const previousVersion = {
        Description: this.editingSubpolicy.originalDescription,
        Control: this.editingSubpolicy.originalControl
      };
      
      // Prepare data to send to the backend
      const updateData = {
        Control: this.editingSubpolicy.Control,
        Description: this.editingSubpolicy.Description,
        previousVersion: previousVersion,
        SubPolicyId: this.editingSubpolicy.SubPolicyId
      };
      
      // Send the updated subpolicy data to the resubmit endpoint
      axios.put(`http://localhost:8000/api/subpolicies/${this.editingSubpolicy.SubPolicyId}/resubmit/`, updateData)
        .then(response => {
          console.log('Subpolicy resubmitted successfully:', response.data);
          
          // Update the local state if we have this subpolicy in our data
          const subpolicy = this.findSubpolicyById(this.editingSubpolicy.SubPolicyId);
          if (subpolicy) {
            // Update the subpolicy with new values
            subpolicy.Status = 'Under Review';
            subpolicy.Control = this.editingSubpolicy.Control;
            subpolicy.Description = this.editingSubpolicy.Description;
            subpolicy.resubmitted = true;
            subpolicy.previousVersion = previousVersion;
            
            if (!subpolicy.approval) {
              subpolicy.approval = {};
            }
      subpolicy.approval.approved = null;
            subpolicy.approval.remarks = '';
            
            if (response.data.Version) {
              subpolicy.version = response.data.Version;
            }
          }
          
          // Show success message
          alert(`Subpolicy "${this.editingSubpolicy.SubPolicyName}" resubmitted successfully with version ${response.data.Version || 'u1'}!`);
          
          // Close the edit modal
          this.closeEditSubpolicyModal();
          
          // Refresh data
          this.fetchRejectedSubpolicies();
        })
        .catch(error => {
          console.error('Error resubmitting subpolicy:', error.response || error);
          alert(`Error resubmitting subpolicy: ${error.response?.data?.error || error.message}`);
        });
    },
    resubmitSubpolicyDirect(subpolicy) {
      if (!subpolicy.SubPolicyId) {
        console.error('Missing SubPolicyId, cannot resubmit subpolicy', subpolicy);
        alert('Error: Cannot resubmit subpolicy - missing SubPolicyId');
        return;
      }
      
      // Check if any changes were made
      const hasChanges = (
        subpolicy.Description !== subpolicy.originalDescription ||
        subpolicy.Control !== subpolicy.originalControl
      );
      
      if (!hasChanges) {
        alert('No changes detected. Please modify the subpolicy before resubmitting.');
        return;
      }
      
      console.log('Resubmitting subpolicy with ID:', subpolicy.SubPolicyId);
      console.log('Changes detected in inline edit form');
      
      // Store original values before resubmitting
      const previousVersion = {
        Description: subpolicy.originalDescription,
        Control: subpolicy.originalControl
      };
      
      // Mark as resubmitted
      subpolicy.resubmitted = true;
      
      // Prepare data to send to the backend
      const updateData = {
        Control: subpolicy.Control,
        Description: subpolicy.Description,
        previousVersion: previousVersion,
        SubPolicyId: subpolicy.SubPolicyId
      };
      
      // Send the updated subpolicy data to the resubmit endpoint
      axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/resubmit/`, updateData)
      .then(response => {
          console.log('Subpolicy resubmitted successfully:', response.data);
          
          // Update the UI to show resubmitted status
          subpolicy.Status = 'Under Review';
          if (!subpolicy.approval) {
            subpolicy.approval = {};
          }
          subpolicy.approval.approved = null;
          subpolicy.previousVersion = previousVersion;
          
          if (response.data.Version) {
            subpolicy.version = response.data.Version;
          }
          
          // Show success message
          alert(`Subpolicy "${subpolicy.SubPolicyName}" resubmitted successfully with version ${response.data.Version || 'u1'}!`);
          
          // Hide the edit form
        this.hideEditFormInline(subpolicy);
        
          // Close the modal after successful resubmission
          this.closeSubpoliciesModal();
          
          // Refresh the data
          this.fetchRejectedSubpolicies();
          this.fetchPolicies();
      })
      .catch(error => {
          console.error('Error resubmitting subpolicy:', error.response || error);
          alert(`Error resubmitting subpolicy: ${error.response?.data?.error || error.message}`);
      });
    },
    getSubpolicyVersion(subpolicy) {
      if (subpolicy.version) {
        return subpolicy.version;
      } else if (subpolicy.approval && subpolicy.approval.version) {
        return subpolicy.approval.version;
      } else {
        return 'u1'; // Default version
      }
    },
    openSubpoliciesModal(policy) {
      this.selectedPolicyForSubpolicies = policy;
      
      // If policy is already approved, mark all subpolicies as approved
      if (policy.ExtractedData && 
          (policy.ApprovedNot === true || policy.ExtractedData.Status === 'Approved') && 
          policy.ExtractedData.subpolicies) {
        
        // Make a deep copy to avoid modifying the original data
        this.selectedPolicyForSubpolicies = JSON.parse(JSON.stringify(policy));
        
        // When a policy is approved, mark all subpolicies as approved too
        this.selectedPolicyForSubpolicies.ExtractedData.subpolicies = 
          this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.map(sub => {
            if (!sub.approval) {
              sub.approval = {};
            }
            sub.approval.approved = true;
            sub.Status = 'Approved';
            return sub;
          });
      }
      
      this.showSubpoliciesModal = true;

      // If in user mode, ensure rejected subpolicies show edit options immediately
      if (!this.isReviewer) {
        // Process each subpolicy to ensure rejected ones can be edited
        setTimeout(() => {
          if (this.selectedPolicyForSubpolicies && 
              this.selectedPolicyForSubpolicies.ExtractedData && 
              this.selectedPolicyForSubpolicies.ExtractedData.subpolicies) {
            
            this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.forEach(sub => {
              if (sub.Status === 'Rejected' || 
                 (sub.approval && sub.approval.approved === false)) {
                // Pre-populate the edit form for rejected subpolicies
                sub.showEditForm = true;
              }
            });
          }
        }, 100); // Small delay to ensure DOM is updated
      }
    },
    closeSubpoliciesModal() {
      this.selectedPolicyForSubpolicies = null;
      this.showSubpoliciesModal = false;
    },
    approveSubpolicyFromModal(subpolicy) {
      // Set subpolicy approval status in UI
      if (!subpolicy.approval) {
        subpolicy.approval = {};
      }
      subpolicy.approval.approved = true;
      subpolicy.approval.remarks = '';
      
      // Update subpolicy status via API
      axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/`, {
        Status: 'Approved'
      })
      .then(response => {
        console.log('Subpolicy status updated successfully:', response.data);
        
        // Create policy approval for this subpolicy approval
        return axios.put(`http://localhost:8000/api/subpolicies/${subpolicy.SubPolicyId}/review/`, {
          Status: 'Approved'
        });
      })
      .then(response => {
        console.log('Subpolicy approval created successfully:', response.data);
        
        // Check if parent policy status was updated (all subpolicies approved)
        if (response.data.PolicyUpdated) {
          console.log(`Policy status updated to: ${response.data.PolicyStatus}`);
          
          // If parent policy was updated, refresh the policies list
          this.fetchPolicies();
          
          // Update the UI to show the policy is now approved
          if (this.selectedPolicyForSubpolicies && 
              this.selectedPolicyForSubpolicies.ExtractedData) {
            this.selectedPolicyForSubpolicies.ExtractedData.Status = response.data.PolicyStatus;
          }
        }
        
        // Check if all subpolicies in the modal are approved
        this.checkAllModalSubpoliciesApproved();
      })
      .catch(error => {
        console.error('Error approving subpolicy:', error);
        alert('Error approving subpolicy. Please try again.');
      });
    },
    
    // Add a method to check if all subpolicies in the modal view are approved
    checkAllModalSubpoliciesApproved() {
      if (!this.selectedPolicyForSubpolicies || 
          !this.selectedPolicyForSubpolicies.ExtractedData || 
          !this.selectedPolicyForSubpolicies.ExtractedData.subpolicies ||
          this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.length === 0) {
        return;
      }
      
      const subpolicies = this.selectedPolicyForSubpolicies.ExtractedData.subpolicies;
      const allApproved = subpolicies.every(sub => sub.approval?.approved === true);
      
      if (allApproved) {
        console.log('All subpolicies in the modal are approved! The policy should be automatically approved');
        
        // Automatically set policy approval to true
        if (!this.selectedPolicyForSubpolicies.ExtractedData.policy_approval) {
          this.selectedPolicyForSubpolicies.ExtractedData.policy_approval = {};
        }
        this.selectedPolicyForSubpolicies.ExtractedData.policy_approval.approved = true;
        this.selectedPolicyForSubpolicies.ApprovedNot = true;
        
        // Show notification to user
        alert('All subpolicies are approved! The policy has been automatically approved.');
      }
    },
    rejectSubpolicyFromModal(subpolicy) {
      // Open rejection modal for subpolicy
      this.rejectingType = 'subpolicy';
      this.rejectingSubpolicy = subpolicy;
      this.showRejectModal = true;
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
    isNewPolicy(policy) {
      const createdDate = policy.ExtractedData?.CreatedByDate || policy.created_at;
      if (!createdDate) return false;
      
      const date = new Date(createdDate);
      if (isNaN(date.getTime())) return false; // Invalid date
      
      const threeDaysAgo = new Date();
      threeDaysAgo.setDate(threeDaysAgo.getDate() - 3); // Show new badge for 3 days
      
      return date > threeDaysAgo;
    },
    // Add a new method for opening the edit modal for a rejected subpolicy
    openEditSubpolicyModal(subpolicy) {
      // Create a deep copy of the subpolicy to edit
      this.editingSubpolicy = JSON.parse(JSON.stringify(subpolicy));
      
      // Store original values for comparison
      this.editingSubpolicy.originalDescription = subpolicy.Description;
      this.editingSubpolicy.originalControl = subpolicy.Control;
      
      // Show the edit modal
      this.showEditSubpolicyModal = true;
      
      console.log('Edit modal opened with subpolicy:', this.editingSubpolicy);
    },
    
    // Add a method to close the edit subpolicy modal
    closeEditSubpolicyModal() {
      this.showEditSubpolicyModal = false;
      this.editingSubpolicy = null;
    },
    
    // Helper method to find a subpolicy by ID
    findSubpolicyById(subpolicyId) {
      if (!this.selectedPolicyForSubpolicies || !this.selectedPolicyForSubpolicies.ExtractedData || !this.selectedPolicyForSubpolicies.ExtractedData.subpolicies) {
        return null;
      }
      
      return this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.find(
        sub => sub.SubPolicyId === subpolicyId
      );
    },
    // Add method to fetch rejected subpolicies
    fetchRejectedSubpolicies() {
      console.log('Fetching rejected subpolicies...');
      // For now, we'll fetch all policies and filter for rejected subpolicies
      axios.get('http://localhost:8000/api/policies/')
        .then(response => {
          console.log('Received policies for subpolicy check:', response.data.length);
          const allPolicies = response.data;
          let rejectedSubs = [];
          
          // Go through each policy and collect rejected subpolicies
          allPolicies.forEach(policy => {
            if (policy.subpolicies && policy.subpolicies.length > 0) {
              console.log(`Policy ${policy.PolicyId} has ${policy.subpolicies.length} subpolicies`);
              const rejected = policy.subpolicies.filter(sub => sub.Status === 'Rejected');
              console.log(`Policy ${policy.PolicyId} has ${rejected.length} rejected subpolicies`);
              
              // Add policy info to each subpolicy for context
              rejected.forEach(sub => {
                sub.PolicyName = policy.PolicyName;
                sub.PolicyId = policy.PolicyId;
              });
              
              rejectedSubs = [...rejectedSubs, ...rejected];
            }
          });
          
          console.log('Total rejected subpolicies found:', rejectedSubs.length);
          this.rejectedSubpolicies = rejectedSubs;
          
          // If we're in user mode and there are rejected subpolicies, update the view
          if (!this.isReviewer && rejectedSubs.length > 0) {
            this.updateRejectedSubpoliciesView();
          }
        })
        .catch(error => {
          console.error('Error fetching rejected subpolicies:', error);
        });
    },
    // Add a method to update the rejected subpolicies view in user mode
    updateRejectedSubpoliciesView() {
      // Set the active tab to rejected if we have rejected subpolicies
      if (this.rejectedSubpolicies.length > 0) {
        this.activeTab = 'rejected';
      }
    },
    // Method to track changes in the edit form
    trackChanges() {
      // No need for complex logic here - Vue's reactivity will handle updates to the model
      // We just need this method to trigger when input happens
      console.log('Changes detected in form');
    },
  },
  computed: {
    policyApprovals() {
      // Return all approvals since we're now directly using the policies data
      return this.approvals;
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
      return this.rejectedSubpolicies && this.rejectedSubpolicies.length > 0;
    },
    hasChanges() {
      if (!this.editingSubpolicy) return false;
      
      // Check if Description or Control have been modified
      return (
        this.editingSubpolicy.Description !== this.editingSubpolicy.originalDescription ||
        this.editingSubpolicy.Control !== this.editingSubpolicy.originalControl
      );
    },
    rejectedSubpoliciesInPolicy() {
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
    sortedPolicies() {
      return [...this.policyApprovals].sort((a, b) => {
        const dateA = new Date(a.ExtractedData?.CreatedByDate || 0);
        const dateB = new Date(b.ExtractedData?.CreatedByDate || 0);
        return dateB - dateA; // Most recent first
      });
    },
    filteredSubpolicies() {
      if (!this.selectedPolicyForSubpolicies || 
          !this.selectedPolicyForSubpolicies.ExtractedData || 
          !this.selectedPolicyForSubpolicies.ExtractedData.subpolicies) {
        return [];
      }
      
      // If in reviewer mode, show all subpolicies
      if (this.isReviewer) {
        return this.selectedPolicyForSubpolicies.ExtractedData.subpolicies;
      }
      
      // In user mode, only show rejected subpolicies
      return this.selectedPolicyForSubpolicies.ExtractedData.subpolicies.filter(sub => 
        sub.Status === 'Rejected' || 
        (sub.approval && sub.approval.approved === false)
      );
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

/* Improved styles for subpolicy-inline-edit */
.subpolicy-inline-edit {
  background: #f8fafc;
  border: 2px solid #6366f1;
  border-radius: 8px;
  padding: 24px;
  margin: 15px 0;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  animation: fadeIn 0.3s ease-out;
  transition: all 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.subpolicy-inline-edit h4 {
  margin-top: 0;
  color: #6366f1;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 10px;
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
}

.subpolicy-inline-edit label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #4b5563;
  font-size: 14px;
}

.subpolicy-inline-edit input,
.subpolicy-inline-edit textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.subpolicy-inline-edit input:focus,
.subpolicy-inline-edit textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.subpolicy-inline-edit input:disabled {
  background-color: #f3f4f6;
  color: #6b7280;
  cursor: not-allowed;
}

.subpolicy-inline-edit textarea {
  min-height: 100px;
  resize: vertical;
}

.subpolicy-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.resubmit-btn {
  background: #6366f1;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
}

.resubmit-btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

.cancel-btn {
  background: #e5e7eb;
  color: #4b5563;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: #d1d5db;
  transform: translateY(-2px);
}

.subpolicy-status {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
}

.subpolicy-status:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.badge.rejected {
  background-color: #ef4444;
  color: white;
  padding: 4px 12px;
  font-weight: 600;
  font-size: 12px;
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
}

.rejection-reason {
  background-color: #fee2e2;
  border-left: 4px solid #ef4444;
  padding: 12px;
  margin: 12px 0;
  color: #991b1b;
  font-size: 14px;
  border-radius: 0 4px 4px 0;
}

.badge.resubmitted {
  background-color: #3b82f6;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
  position: relative;
  animation: pulse-badge 2s infinite;
}

@keyframes pulse-badge {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
  70% { transform: scale(1.05); box-shadow: 0 0 0 5px rgba(59, 130, 246, 0); }
  100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}

/* Styles for resubmitted items */
.resubmitted-item {
  border-left: 4px solid #3b82f6 !important;
  background-color: rgba(59, 130, 246, 0.05);
  position: relative;
}

.resubmitted-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -4px;
  height: 100%;
  width: 4px;
  background-color: #3b82f6;
  animation: pulse-border 2s infinite;
}

@keyframes pulse-border {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

/* Subpolicy header with better layout */
.subpolicy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

/* Version tag styling */
.subpolicy-version {
  margin-bottom: 10px;
}

.version-tag {
  background-color: #3b82f6;
  color: white;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  font-weight: 600;
  margin-right: 10px;
}

/* Edit history styling */
.edit-history {
  margin-top: 15px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.edit-history-header {
  background-color: #3b82f6;
  color: white;
  padding: 10px 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.edit-history-content {
  padding: 15px;
  background-color: #f9fafb;
}

.edit-field {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #e5e7eb;
}

.edit-field:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.field-label {
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 5px;
  font-size: 13px;
}

.field-previous {
  padding: 10px;
  background-color: #fee2e2;
  border-radius: 4px;
  margin-bottom: 10px;
  position: relative;
  text-decoration: line-through;
  color: #991b1b;
  font-size: 14px;
}

.field-value {
  padding: 10px;
  background-color: #dcfce7;
  border-radius: 4px;
  color: #166534;
  font-size: 14px;
}

/* Subpolicy content section */
.subpolicy-content {
  margin-bottom: 15px;
}

.view-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
}

.view-button:hover {
  background-color: #2563eb;
}

/* Add styles for approved date display */
.policy-approved-date {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  padding: 8px 12px;
  background-color: #f0f9ff;
  border-radius: 6px;
  border-left: 4px solid #22c55e;
}

.date-label {
  font-weight: 600;
  color: #065f46;
}

.date-value {
  color: #059669;
  font-family: 'Courier New', monospace;
}

.approval-status.approved {
  background-color: #dcfce7;
  color: #166534;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 600;
}

/* Styles for changes summary in edit modal */
.changes-summary {
  margin: 15px 0;
  border: 1px solid #3b82f6;
  border-radius: 8px;
  overflow: hidden;
  background-color: rgba(59, 130, 246, 0.05);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.changes-header {
  background-color: #3b82f6;
  color: white;
  padding: 10px 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.changes-content {
  padding: 12px 15px;
}

.change-item {
  padding: 8px 0;
  color: #4b5563;
  font-size: 14px;
  border-bottom: 1px dashed #e5e7eb;
}

.change-item:last-child {
  border-bottom: none;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.form-actions .resubmit-btn {
  background-color: #6366f1;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.form-actions .resubmit-btn:hover:not(:disabled) {
  background-color: #4f46e5;
  transform: translateY(-2px);
}

.form-actions .resubmit-btn:disabled {
  background-color: #c7d2fe;
  cursor: not-allowed;
  color: #6366f1;
}

.form-actions .cancel-btn {
  background-color: #e5e7eb;
  color: #4b5563;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.form-actions .cancel-btn:hover {
  background-color: #d1d5db;
  transform: translateY(-2px);
}

/* Improve edit modal styling */
.edit-modal {
  width: 90%;
  max-width: 700px;
  padding: 30px;
  border-radius: 12px;
}

.edit-modal h2 {
  color: #4f46e5;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #c7d2fe;
  font-size: 22px;
}

.edit-modal .form-group {
  margin-bottom: 20px;
}

.edit-modal label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #4b5563;
  font-size: 14px;
}

.edit-modal input,
.edit-modal textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.edit-modal input:focus,
.edit-modal textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.edit-modal textarea {
  min-height: 120px;
  resize: vertical;
}

.edit-modal input:disabled {
  background-color: #f3f4f6;
  color: #6b7280;
  cursor: not-allowed;
}

/* Badge for approved-only view */
.approved-only-badge {
  background-color: #10b981;
  color: white;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 20px;
  margin-left: 10px;
  font-weight: 500;
  display: inline-block;
  vertical-align: middle;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

/* Policy status indicator styles */
.policy-status-indicator {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  background: #f8fafc;
  padding: 10px 15px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.status-label {
  font-weight: 600;
  margin-right: 10px;
  color: #4b5563;
}

.status-value {
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  text-align: center;
}

.status-approved {
  background-color: #10b981;
  color: white;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.status-rejected {
  background-color: #ef4444;
  color: white;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
}

.status-pending {
  background-color: #f59e0b;
  color: white;
  box-shadow: 0 2px 4px rgba(245, 158, 11, 0.2);
}
</style> 