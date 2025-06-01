<template>
  <div class="workflow-container">
    <h1>User Risk Management</h1>
    
    <div class="user-filter">
      <label for="user-select">Select User:</label>
      <select id="user-select" v-model="selectedUserId" @change="fetchData" class="user-dropdown">
        <option value="">All Users</option>
        <option v-for="user in users" :key="user.user_id" :value="user.user_id">
          {{ user.user_name }} ({{ user.department }})
        </option>
      </select>
    </div>
    
    <!-- Tabs for User Tasks and Reviewer Tasks -->
    <div class="tabs">
      <div 
        class="tab" 
        :class="{ 'active': activeTab === 'user' }" 
        @click="activeTab = 'user'"
      >
        My Tasks
      </div>
      <div 
        class="tab" 
        :class="{ 'active': activeTab === 'reviewer' }" 
        @click="activeTab = 'reviewer'"
      >
        Reviewer Tasks
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      Loading data...
    </div>
    
    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>
    
    <!-- User Tasks Section -->
    <div v-if="activeTab === 'user'">
      <div v-if="!selectedUserId" class="no-data">
        <p>Please select a user to view their assigned risks.</p>
      </div>
      <div v-else-if="userRisks.length === 0" class="no-data">
        <p>No risks assigned to this user.</p>
      </div>
      <div v-else>
        <!-- Match the card layout in the screenshot -->
        <div v-for="risk in userRisks" :key="risk.RiskInstanceId" class="risk-card">
          <h3>{{ risk.RiskDescription || 'Risk #' + risk.RiskInstanceId }}</h3>
          
          <!-- Add status icon - green check for approved, red exclamation for rejected -->
          <div class="status-icon" :class="{
            'approved': risk.RiskStatus === 'Approved', 
            'rejected': risk.RiskStatus === 'Revision Required'
          }">
            <i class="fas" :class="{
              'fa-check-circle': risk.RiskStatus === 'Approved', 
              'fa-exclamation-circle': risk.RiskStatus === 'Revision Required'
            }"></i>
          </div>
          
          <div class="risk-info">
            <p><strong>ID:</strong> {{ risk.RiskInstanceId }}</p>
            <p><strong>Category:</strong> {{ risk.Category }}</p>
            <p><strong>Criticality:</strong> {{ risk.Criticality }}</p>
            <p><strong>Due Date:</strong> 
              <template v-if="risk.MitigationDueDate">
                {{ formatDate(risk.MitigationDueDate) }}
                <span class="due-status" :class="getDueStatusClass(risk.MitigationDueDate)">
                  {{ getDueStatusText(risk.MitigationDueDate) }}
                </span>
              </template>
              <template v-else>Not set</template>
            </p>
            <p><strong>Status:</strong> 
              <span :class="'status-' + risk.RiskStatus?.toLowerCase().replace(/\s+/g, '-')">
                {{ risk.RiskStatus || 'Not Assigned' }}
              </span>
              <span class="mitigation-status" :class="getMitigationStatusClass(risk.MitigationStatus)">
                {{ risk.MitigationStatus || 'Yet to Start' }}
              </span>
            </p>
            <p><strong>Priority:</strong> {{ risk.RiskPriority }}</p>
            <p><strong>Assigned To:</strong> {{ getUserName(risk.UserId) }}</p>
            
            <!-- Add the last submitted date if available -->
            <p v-if="risk.last_submitted"><strong>Last Submitted:</strong> {{ formatDateTime(risk.last_submitted) }}</p>
            
            <!-- Show rejection message if applicable -->
            <div v-if="risk.RiskStatus === 'Revision Required'" class="rejection-notice">
              <p><strong>Your submission requires revision.</strong></p>
              <div class="reviewer-feedback">
                <h5>Check the mitigations for specific feedback</h5>
                <button @click="viewMitigations(risk.RiskInstanceId)" class="view-feedback-btn">
                  <i class="fas fa-eye"></i> View Reviewer Feedback
                </button>
              </div>
            </div>
            
            <div v-else-if="risk.RiskStatus === 'Approved'" class="approval-notice">
              <p><strong>Your submission has been approved!</strong></p>
              <div class="green-check">
                <i class="fas fa-check-circle"></i>
              </div>
            </div>
          </div>
          
          <div class="action-buttons">
            <button 
              v-if="risk.MitigationStatus === 'Revision Required by User'" 
              @click="startWork(risk.RiskInstanceId)" 
              class="start-btn">
              Start Revision
            </button>
            <button 
              v-else-if="risk.MitigationStatus !== 'Work In Progress' && risk.MitigationStatus !== 'Completed'" 
              @click="startWork(risk.RiskInstanceId)" 
              class="start-btn">
              Start Work
            </button>
            <button 
              v-if="risk.MitigationStatus === 'Work In Progress'" 
              @click="completeMitigation(risk.RiskInstanceId)" 
              class="complete-btn">
              Mark as Completed
            </button>
            <button 
              @click="viewMitigations(risk.RiskInstanceId)" 
              class="view-btn"
              :disabled="risk.MitigationStatus === 'Yet to Start'"
              :class="{'disabled-btn': risk.MitigationStatus === 'Yet to Start'}">
              <i class="fas fa-eye"></i> View Mitigations
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Reviewer Tasks Section -->
    <div v-if="activeTab === 'reviewer'">
      <div v-if="!selectedUserId" class="no-data">
        <p>Please select a user to view their reviewer tasks.</p>
      </div>
      <div v-else-if="reviewerTasks.length === 0" class="no-data">
        <p>No review tasks assigned to this user.</p>
      </div>
      <div v-else>
        <!-- Reviewer task cards with same layout as user tasks -->
        <div v-for="task in reviewerTasks" :key="task.RiskInstanceId" 
             class="risk-card reviewer-card"
             :class="{
               'completed-card': task.RiskStatus === 'Approved',
               'revision-card': task.RiskStatus === 'Revision Required'
             }">
          <h3>{{ task.RiskDescription || 'Risk #' + task.RiskInstanceId }}</h3>
          
          <!-- Add status badge -->
          <div class="status-badge" :class="getStatusClass(task.RiskStatus)">
            {{ task.RiskStatus }}
          </div>
          
          <div class="risk-info">
            <p><strong>ID:</strong> {{ task.RiskInstanceId }}</p>
            <p><strong>Category:</strong> {{ task.Category }}</p>
            <p><strong>Criticality:</strong> {{ task.Criticality }}</p>
            <p><strong>Due Date:</strong> 
              <template v-if="task.MitigationDueDate">
                {{ formatDate(task.MitigationDueDate) }}
                <span class="due-status" :class="getDueStatusClass(task.MitigationDueDate)">
                  {{ getDueStatusText(task.MitigationDueDate) }}
                </span>
              </template>
              <template v-else>Not set</template>
            </p>
            <p><strong>Status:</strong> 
              <span :class="'status-' + task.RiskStatus?.toLowerCase().replace(/\s+/g, '-')">
                {{ task.RiskStatus || 'Not Started' }}
              </span>
              <span class="mitigation-status">{{ task.MitigationStatus || 'Yet to Start' }}</span>
            </p>
            <p><strong>Priority:</strong> {{ task.RiskPriority }}</p>
            <p><strong>Submitted By:</strong> {{ getUserName(task.UserId) }}</p>
            
            <!-- Add the submission date from ExtractedInfo -->
            <p v-if="getSubmissionDate(task)"><strong>Submitted Date:</strong> {{ formatDateTime(getSubmissionDate(task)) }}</p>
          </div>
          
          <div class="action-buttons">
            <button 
              @click="reviewMitigations(task)" 
              class="review-btn"
              :disabled="!hasApprovalVersion(task)"
              :class="{'disabled-btn': !hasApprovalVersion(task)}">
              <i class="fas fa-tasks"></i> {{ task.RiskStatus === 'Under Review' ? 'Review Mitigations' : 'View Mitigations' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Mitigation Workflow Modal -->
    <div v-if="showMitigationModal" class="modal-overlay" @click.self="closeMitigationModal">
      <div class="modal-content">
        <div class="modal-header">
          <div class="shield-icon"><i class="fas fa-shield-alt"></i></div>
          <h2>Risk Mitigation Workflow</h2>
          <button class="close-btn" @click="closeMitigationModal">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingMitigations" class="loading">
            <div class="spinner"></div>
            <span>Loading mitigation steps...</span>
          </div>
          <div v-else-if="!mitigationSteps.length" class="no-data">
            No mitigation steps found for this risk.
          </div>
          <div v-else class="simplified-workflow">
            <!-- Vertical timeline with connected steps -->
            <div class="timeline">
              <div 
                v-for="(step, index) in mitigationSteps" 
                :key="index" 
                class="timeline-step"
                :class="{
                  'completed': step.status === 'Completed',
                  'active': isStepActive(index),
                  'locked': isStepLocked(index),
                  'approved': step.approved === true,
                  'rejected': step.approved === false
                }"
              >
                <!-- Step circle with number -->
                <div class="step-circle">
                  <span v-if="step.status === 'Completed'"><i class="fas fa-check"></i></span>
                  <span v-else>{{ step.title.replace('Step ', '') }}</span>
                </div>
                
                <!-- Step content -->
                <div class="step-box">
                  <h3>{{ step.description }}</h3>
                  
                  <!-- Add submission dates when available -->
                  <div v-if="step.user_submitted_date" class="submission-date user-date">
                    <i class="fas fa-clock"></i> Submitted: {{ formatDateTime(step.user_submitted_date) }}
                  </div>
                  <div v-if="step.reviewer_submitted_date" class="submission-date reviewer-date">
                    <i class="fas fa-clock"></i> Reviewed: {{ formatDateTime(step.reviewer_submitted_date) }}
                  </div>
                  
                  <!-- Status indicators -->
                  <div v-if="step.approved === true" class="status-tag approved">
                    <i class="fas fa-check-circle"></i> Approved
                  </div>
                  <div v-else-if="step.approved === false" class="status-tag rejected">
                    <i class="fas fa-times-circle"></i> Rejected
                    <div v-if="step.remarks" class="remarks">
                      <strong>Feedback:</strong> {{ step.remarks }}
                    </div>
                  </div>
                  <div v-else-if="step.status === 'Completed'" class="status-tag completed">
                    <i class="fas fa-check"></i> Completed
                  </div>
                  <div v-else-if="isStepActive(index)" class="status-tag active">
                    <i class="fas fa-circle-notch fa-spin"></i> In Progress
                  </div>
                  <div v-else class="status-tag locked">
                    <i class="fas fa-lock"></i> Locked
                  </div>
                  
                  <!-- Only show editable fields for active steps or rejected steps -->
                  <div v-if="isStepActive(index) || step.approved === false" class="step-inputs">
                    <div class="input-group">
                      <label>Your Comments:</label>
                      <textarea 
                        v-model="step.comments" 
                        placeholder="Add any notes or comments about this step..."
                        :disabled="isStepLocked(index)"
                      ></textarea>
                    </div>
                    
                    <div class="input-group">
                      <label>Upload Evidence:</label>
                      <div class="file-upload">
                        <input 
                          type="file" 
                          @change="handleFileUpload($event, index)" 
                          :disabled="isStepLocked(index)"
                          :id="`file-upload-${index}`"
                        />
                        <label :for="`file-upload-${index}`" class="upload-btn">
                          <i class="fas fa-upload"></i> Select File
                        </label>
                        <span v-if="step.fileName" class="file-name">{{ step.fileName }}</span>
                      </div>
                    </div>
                    
                    <div class="status-control">
                      <button 
                        v-if="step.status !== 'Completed'" 
                        @click="completeStep(index)" 
                        class="complete-btn"
                        :disabled="isStepLocked(index)"
                      >
                        <i class="fas fa-check-circle"></i> Mark as Completed
                      </button>
                      <button 
                        v-else 
                        @click="resetStep(index)" 
                        class="reset-btn"
                      >
                        <i class="fas fa-undo"></i> Reset
                      </button>
                    </div>
                  </div>
                  
                  <!-- For non-editable steps, just show the available info -->
                  <div v-else-if="step.comments || step.fileData" class="step-info">
                    <div v-if="step.comments" class="comments-display">
                      <h4><i class="fas fa-comment"></i> Your Comments</h4>
                      <p>{{ step.comments }}</p>
                    </div>
                    
                    <div v-if="step.fileData" class="file-display">
                      <h4><i class="fas fa-file-alt"></i> Uploaded Evidence</h4>
                      <a :href="step.fileData" download :filename="step.fileName">
                        <i class="fas fa-download"></i> {{ step.fileName }}
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Update the mitigation-questionnaire div in the mitigation modal -->
            <div class="mitigation-questionnaire" v-if="allStepsCompleted">
              <h3>Risk Mitigation Questionnaire</h3>
              
              <!-- Add questionnaire status indicator -->
              <div v-if="questionnaireReviewed" class="questionnaire-status" :class="{ 'approved': questionnaireApproved, 'rejected': !questionnaireApproved }">
                <i class="fas" :class="questionnaireApproved ? 'fa-check-circle' : 'fa-times-circle'"></i>
                {{ questionnaireApproved ? 'Approved' : 'Revision Required' }}
                
                <!-- Add submission dates when available -->
                <div v-if="formDetails.user_submitted_date" class="submission-date user-date">
                  <i class="fas fa-clock"></i> Submitted: {{ formatDateTime(formDetails.user_submitted_date) }}
                </div>
                <div v-if="formDetails.reviewer_submitted_date" class="submission-date reviewer-date">
                  <i class="fas fa-clock"></i> Reviewed: {{ formatDateTime(formDetails.reviewer_submitted_date) }}
                </div>
              </div>
              
              <p class="questionnaire-note">Please complete all fields to proceed with submission</p>
              
              <div class="question-group">
                <label for="cost-input">What is the cost for this mitigation?</label>
                <textarea 
                  id="cost-input" 
                  v-model="formDetails.cost" 
                  placeholder="Describe the cost..."
                  :disabled="questionnaireApproved || !allStepsCompleted"
                  @input="validateQuestionnaire"
                ></textarea>
              </div>
              
              <div class="question-group" :class="{ 'disabled': !formDetails.cost && !questionnaireApproved }">
                <label for="impact-input">What is the impact for this mitigation?</label>
                <textarea 
                  id="impact-input" 
                  v-model="formDetails.impact" 
                  placeholder="Describe the impact..."
                  :disabled="(questionnaireApproved || !formDetails.cost) && !questionnaireRejected"
                  @input="validateQuestionnaire"
                ></textarea>
              </div>
              
              <div class="question-group" :class="{ 'disabled': !formDetails.impact && !questionnaireApproved }">
                <label for="financial-impact-input">What is the financial impact for this mitigation?</label>
                <textarea 
                  id="financial-impact-input" 
                  v-model="formDetails.financialImpact" 
                  placeholder="Describe the financial impact..."
                  :disabled="(questionnaireApproved || !formDetails.impact) && !questionnaireRejected"
                  @input="validateQuestionnaire"
                ></textarea>
              </div>
              
              <div class="question-group" :class="{ 'disabled': !formDetails.financialImpact && !questionnaireApproved }">
                <label for="reputational-impact-input">What is the reputational impact for this mitigation?</label>
                <textarea 
                  id="reputational-impact-input" 
                  v-model="formDetails.reputationalImpact" 
                  placeholder="Describe the reputational impact..."
                  :disabled="(questionnaireApproved || !formDetails.financialImpact) && !questionnaireRejected"
                  @input="validateQuestionnaire"
                ></textarea>
              </div>
              
              <!-- Add to the mitigation-questionnaire div, after the questionnaire fields -->
              <div v-if="questionnaireRejected" class="questionnaire-feedback">
                <h4><i class="fas fa-exclamation-circle"></i> Reviewer Feedback</h4>
                <p>{{ questionnaireRemarks }}</p>
              </div>
            </div>
            
            <!-- Update the submission-area div to check for questionnaire completion -->
            <div class="submission-area" :class="{ 'ready': canSubmit }">
              <h3>Review Assignment</h3>
              
              <div class="reviewer-select">
                <label for="reviewer-select">Select a Reviewer:</label>
                <select 
                  id="reviewer-select" 
                  v-model="selectedReviewer" 
                  :disabled="!allStepsCompleted || !!selectedReviewer"
                >
                  <option value="">Select Reviewer...</option>
                  <option v-for="user in users" :key="user.user_id" :value="user.user_id">
                    {{ user.user_name }} ({{ user.department }})
                  </option>
                </select>
              </div>
              
              <button 
                @click="submitForReview" 
                class="submit-btn" 
                :disabled="!canSubmit"
              >
                <i class="fas fa-paper-plane"></i> Submit for Review
              </button>
              
              <div v-if="!allStepsCompleted" class="submit-message">
                <i class="fas fa-info-circle"></i>
                Complete all mitigation steps before submitting
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Reviewer Modal -->
    <div v-if="showReviewerModal" class="modal-overlay" @click.self="closeReviewerModal">
      <div class="modal-content reviewer-modal">
        <div class="modal-header">
          <h2>Review Risk Mitigations</h2>
          <button class="close-btn" @click="closeReviewerModal">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingMitigations" class="loading">
            Loading mitigation data...
          </div>
          <div v-else>
            <div class="risk-summary">
              <h3>{{ currentReviewTask?.RiskDescription || 'Risk #' + currentReviewTask?.RiskInstanceId }}</h3>
              <p><strong>ID:</strong> {{ currentReviewTask?.RiskInstanceId }}</p>
              <p><strong>Submitted By:</strong> {{ getUserName(currentReviewTask?.UserId) }}</p>
            </div>
            
            <div v-if="reviewCompleted" class="review-status-banner" :class="{ 'approved': reviewApproved, 'rejected': !reviewApproved }">
              <div v-if="reviewApproved" class="status-message">
                <i class="fas fa-check-circle"></i> This risk has been approved
              </div>
              <div v-else class="status-message">
                <i class="fas fa-times-circle"></i> This risk was rejected and is awaiting revision
              </div>
            </div>
            
            <!-- Mitigation review list with split view design -->
            <div class="mitigation-review-list">
              <div 
                v-for="(mitigation, id) in mitigationReviewData" 
                :key="id" 
                class="mitigation-review-item"
                :data-id="id"
              >
                <!-- Mitigation header with status badge -->
                <div class="mitigation-heading">
                  <h4>Mitigation #{{ id }}</h4>
                  
                  <!-- Status badge -->
                  <div v-if="mitigation.approved !== undefined" 
                      class="mitigation-status-badge" 
                      :class="{ 
                        'approved': mitigation.approved === true, 
                        'rejected': mitigation.approved === false,
                        'pending': mitigation.approved === undefined
                      }">
                    <i class="fas" :class="{
                      'fa-check-circle': mitigation.approved === true,
                      'fa-times-circle': mitigation.approved === false,
                      'fa-clock': mitigation.approved === undefined
                    }"></i>
                    {{ mitigation.approved === true ? 'Approved' : 
                       mitigation.approved === false ? 'Rejected' : 'Pending Review' }}
                  </div>
                </div>
                
                <!-- Split view container -->
                <div class="mitigation-split-content">
                  <!-- Previous version (left side) -->
                  <div class="mitigation-previous">
                    <div class="version-label">Previous Version</div>
                    
                    <div v-if="getPreviousMitigation(id)" class="mitigation-content">
                      <h5>Description</h5>
                      <p>{{ getPreviousMitigation(id).description || 'No description available' }}</p>
                      
                      <!-- Previous metadata section -->
                      <div class="metadata-section">
                        <h5>Metadata</h5>
                        <div class="metadata-item">
                          <div class="metadata-label">Status:</div>
                          <div class="metadata-value">{{ getPreviousMitigation(id).status || 'Not specified' }}</div>
                        </div>
                        <div v-if="getPreviousMitigation(id).user_submitted_date" class="metadata-item">
                          <div class="metadata-label">Submitted:</div>
                          <div class="metadata-value">{{ formatDateTime(getPreviousMitigation(id).user_submitted_date) }}</div>
                        </div>
                      </div>
                      
                      <!-- Previous comments -->
                      <div v-if="getPreviousMitigation(id).comments" class="comments-section">
                        <h5><i class="fas fa-comment-alt"></i> User Comments</h5>
                        <p class="comments-text">{{ getPreviousMitigation(id).comments }}</p>
                      </div>
                      
                      <!-- Previous evidence -->
                      <div v-if="getPreviousMitigation(id).fileData" class="evidence-section">
                        <h5><i class="fas fa-file-alt"></i> Evidence</h5>
                        <a :href="getPreviousMitigation(id).fileData" download :filename="getPreviousMitigation(id).fileName" class="evidence-link">
                          <i class="fas fa-download"></i> {{ getPreviousMitigation(id).fileName }}
                        </a>
                      </div>
                      
                      <!-- Previous decision -->
                      <div v-if="getPreviousMitigation(id).approved !== undefined" class="decision-tag" 
                           :class="{ 
                             'approved': getPreviousMitigation(id).approved === true, 
                             'rejected': getPreviousMitigation(id).approved === false 
                           }">
                        <i class="fas" :class="{
                          'fa-check-circle': getPreviousMitigation(id).approved === true,
                          'fa-times-circle': getPreviousMitigation(id).approved === false
                        }"></i>
                        {{ getPreviousMitigation(id).approved ? 'Approved' : 'Rejected' }}
                      </div>
                    </div>
                    
                    <!-- Empty state for no previous version -->
                    <div v-else class="mitigation-empty">
                      <i class="fas fa-history"></i>
                      <p>No previous version available</p>
                    </div>
                  </div>
                  
                  <!-- Current version (right side) -->
                  <div class="mitigation-current">
                    <div class="version-label">Current Version</div>
                    
                    <div class="mitigation-content">
                      <h5>Description</h5>
                      <p>{{ mitigation.description }}</p>
                      
                      <!-- Current metadata -->
                      <div class="metadata-section">
                        <h5>Metadata</h5>
                        <div class="metadata-item">
                          <div class="metadata-label">Status:</div>
                          <div class="metadata-value">{{ mitigation.status || 'Not specified' }}</div>
                        </div>
                        <div v-if="mitigation.user_submitted_date" class="metadata-item">
                          <div class="metadata-label">Submitted:</div>
                          <div class="metadata-value">{{ formatDateTime(mitigation.user_submitted_date) }}</div>
                        </div>
                        <div v-if="mitigation.reviewer_submitted_date" class="metadata-item">
                          <div class="metadata-label">Reviewed:</div>
                          <div class="metadata-value">{{ formatDateTime(mitigation.reviewer_submitted_date) }}</div>
                        </div>
                      </div>
                      
                      <!-- Current comments -->
                      <div v-if="mitigation.comments" class="comments-section">
                        <h5><i class="fas fa-comment-alt"></i> User Comments</h5>
                        <p class="comments-text">{{ mitigation.comments }}</p>
                      </div>
                      
                      <!-- Current evidence -->
                      <div v-if="mitigation.fileData" class="evidence-section">
                        <h5><i class="fas fa-file-alt"></i> Evidence</h5>
                        <a :href="mitigation.fileData" download :filename="mitigation.fileName" class="evidence-link">
                          <i class="fas fa-download"></i> {{ mitigation.fileName }}
                        </a>
                      </div>
                      
                      <!-- Current decision -->
                      <div v-if="mitigation.approved !== undefined" class="decision-tag" 
                           :class="{ 
                             'approved': mitigation.approved === true, 
                             'rejected': mitigation.approved === false 
                           }">
                        <i class="fas" :class="{
                          'fa-check-circle': mitigation.approved === true,
                          'fa-times-circle': mitigation.approved === false
                        }"></i>
                        {{ mitigation.approved ? 'Approved' : 'Rejected' }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Approval controls section -->
                <div class="approval-controls">
                  <!-- Only show approval buttons if not yet approved or rejected -->
                  <div v-if="mitigation.approved !== true && mitigation.approved !== false && !reviewCompleted" class="approval-buttons">
                    <button 
                      @click="approveMitigation(id, true)" 
                      class="approve-btn"
                    >
                      <i class="fas fa-check"></i> Approve
                    </button>
                    <button 
                      @click="approveMitigation(id, false)" 
                      class="reject-btn"
                    >
                      <i class="fas fa-times"></i> Reject
                    </button>
                  </div>
                  
                  <!-- Show remarks field only when rejected -->
                  <div v-if="mitigation.approved === false && !reviewCompleted" class="remarks-field">
                    <label for="remarks">Feedback (required for rejection):</label>
                    <textarea 
                      id="remarks" 
                      v-model="mitigation.remarks" 
                      class="remarks-input" 
                      placeholder="Provide feedback explaining why this mitigation was rejected..."
                    ></textarea>
                    
                    <!-- Add a button to save remarks -->
                    <button @click="updateRemarks(id)" class="save-remarks-btn">
                      <i class="fas fa-save"></i> Save Feedback
                    </button>
                    
                    <!-- Allow changing decision -->
                    <button @click="approveMitigation(id, true)" class="change-decision-btn">
                      <i class="fas fa-exchange-alt"></i> Change to Approve
                    </button>
                  </div>
                  
                  <!-- Show status and action buttons for approved items -->
                  <div v-if="mitigation.approved === true && !reviewCompleted" class="approved-actions">
                    <button @click="approveMitigation(id, false)" class="change-decision-btn">
                      <i class="fas fa-exchange-alt"></i> Change to Reject
                    </button>
                  </div>
                  
                  <!-- Show remarks if already rejected and submitted -->
                  <div v-if="mitigation.approved === false && reviewCompleted && mitigation.remarks" class="reviewer-remarks-display">
                    <h5><i class="fas fa-comment-exclamation"></i> Rejection Feedback</h5>
                    <p>{{ mitigation.remarks }}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Update the form details review section in the reviewer modal -->
            <div class="form-details-review">
              <h4>Risk Mitigation Questionnaire</h4>
              
              <!-- Add status badge at the top -->
              <div v-if="formDetails.approved !== undefined" class="approval-status" :class="{ 
                'approved': formDetails.approved, 
                'rejected': formDetails.approved === false 
              }">
                <i class="fas" :class="formDetails.approved ? 'fa-check-circle' : 'fa-times-circle'"></i>
                {{ formDetails.approved ? 'Questionnaire Approved' : 'Revisions Requested' }}
              </div>
              
              <!-- Add submission dates when available -->
              <div class="submission-dates">
                <div v-if="formDetails.user_submitted_date" class="submission-date user-date">
                  <i class="fas fa-clock"></i> Submitted: {{ formatDateTime(formDetails.user_submitted_date) }}
                </div>
                <div v-if="formDetails.reviewer_submitted_date" class="submission-date reviewer-date">
                  <i class="fas fa-check-circle"></i> Reviewed: {{ formatDateTime(formDetails.reviewer_submitted_date) }}
                </div>
              </div>
              
              <!-- Split view for each form item -->
              <div class="form-split-content" v-for="field in ['cost', 'impact', 'financialImpact', 'reputationalImpact']" :key="field">
                <div class="form-field-label">
                  <h5>{{ getFieldLabel(field) }}:</h5>
                </div>
                
                <div class="form-field-split">
                  <!-- Previous version -->
                  <div class="form-field-previous" v-if="previousFormDetails">
                    <div class="version-label">Previous Version</div>
                    <p>{{ getPreviousFormDetail(field) }}</p>
                  </div>
                  
                  <!-- Current version -->
                  <div class="form-field-current" :class="{ 'highlight-changed': hasFormFieldChanged(field) }">
                    <div class="version-label">Current Version</div>
                    <p>{{ formDetails[field] || 'Not specified' }}</p>
                  </div>
                </div>
              </div>
              
              <!-- Add questionnaire approval controls -->
              <div class="questionnaire-approval" v-if="!reviewCompleted">
                <div v-if="formDetails.approved === undefined" class="approval-buttons">
                  <button @click="approveQuestionnaire(true)" class="approve-btn">
                    <i class="fas fa-check"></i> Approve Questionnaire
                  </button>
                  <button @click="approveQuestionnaire(false)" class="reject-btn">
                    <i class="fas fa-times"></i> Request Revisions
                  </button>
                </div>
                
                <div v-if="formDetails.approved === true" class="approval-status approved">
                  <i class="fas fa-check-circle"></i> Questionnaire Approved
                  <button @click="approveQuestionnaire(false)" class="change-decision-btn">
                    <i class="fas fa-exchange-alt"></i> Change to Reject
                  </button>
                </div>
                
                <div v-if="formDetails.approved === false" class="approval-status rejected">
                  <i class="fas fa-times-circle"></i> Revisions Requested
                  
                  <div class="remarks-field">
                    <label for="questionnaire-remarks">Feedback (required):</label>
                    <textarea 
                      id="questionnaire-remarks" 
                      v-model="formDetails.remarks" 
                      class="remarks-input" 
                      placeholder="Provide feedback on the questionnaire..."
                    ></textarea>
                    
                    <div class="approval-actions">
                      <button @click="saveQuestionnaireRemarks" class="save-remarks-btn">
                        <i class="fas fa-save"></i> Save Feedback
                      </button>
                      
                      <button @click="approveQuestionnaire(true)" class="change-decision-btn">
                        <i class="fas fa-exchange-alt"></i> Change to Approve
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="review-actions">
              <button 
                class="submit-review-btn" 
                :disabled="!canSubmitReview || reviewCompleted" 
                @click="submitReview(true)"
              >
                <i class="fas fa-check-double"></i> Approve Risk
              </button>
              <button 
                class="reject-review-btn" 
                :disabled="!canSubmitReview || reviewCompleted" 
                @click="submitReview(false)"
              >
                <i class="fas fa-ban"></i> Reject Risk
              </button>
              
              <div v-if="reviewCompleted" class="review-complete-notice">
                This review has been completed
              </div>
              
              <div v-else-if="!canSubmitReview" class="review-warning">
                <i class="fas fa-exclamation-circle"></i>
                You must approve or reject each mitigation before submitting
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import './UserTask.css'; // Import the CSS file

export default {
  name: 'UserTasks',
  data() {
    return {
      userRisks: [],
      reviewerTasks: [],
      users: [],
      selectedUserId: '',
      loading: true,
      error: null,
      showMitigationModal: false,
      loadingMitigations: false,
      mitigationSteps: [],
      selectedRiskId: null,
      selectedReviewer: '',
      activeTab: 'user',
      showReviewerModal: false,
      mitigationReviewData: {},
      currentReviewTask: null,
      userNotifications: [],
      reviewCompleted: false,
      reviewApproved: false,
      formDetails: {
        cost: '',
        impact: '',
        financialImpact: '',
        reputationalImpact: ''
      },
      previousVersions: {},
      previousFormDetails: null
    }
  },
  computed: {
    allStepsCompleted() {
      const stepsToCheck = this.mitigationSteps.filter(step => Boolean(step.approved) !== true);
      return stepsToCheck.length > 0 && 
             stepsToCheck.every(step => step.status === 'Completed');
    },
    canSubmit() {
      const hasRejectedOrNewSteps = this.mitigationSteps.some(step => Boolean(step.approved) !== true);
      const formCompleted = this.isQuestionnaireComplete();
      return this.allStepsCompleted && this.selectedReviewer && hasRejectedOrNewSteps && formCompleted;
    },
    canSubmitReview() {
      const allMitigationsReviewed = Object.values(this.mitigationReviewData).every(m => 
        m.approved === true || (m.approved === false && m.remarks && m.remarks.trim() !== '')
      );
      
      // Also require the questionnaire to be reviewed
      const questionnaireReviewed = 
        this.formDetails.approved === true || 
        (this.formDetails.approved === false && this.formDetails.remarks && this.formDetails.remarks.trim() !== '');
      
      return allMitigationsReviewed && questionnaireReviewed;
    },
    questionnaireReviewed() {
      return this.latestReview && 
             this.latestReview.risk_form_details && 
             (this.latestReview.risk_form_details.approved === true || 
              this.latestReview.risk_form_details.approved === false);
    },
    questionnaireApproved() {
      return this.latestReview && 
             this.latestReview.risk_form_details && 
             this.latestReview.risk_form_details.approved === true;
    },
    questionnaireRejected() {
      return this.latestReview && 
             this.latestReview.risk_form_details && 
             this.latestReview.risk_form_details.approved === false;
    },
    questionnaireRemarks() {
      if (this.latestReview && 
          this.latestReview.risk_form_details && 
          this.latestReview.risk_form_details.remarks) {
        return this.latestReview.risk_form_details.remarks;
      }
      return '';
    }
  },
  mounted() {
    this.fetchUsers();
  },
  methods: {
    fetchUsers() {
      axios.get('http://localhost:8000/api/custom-users/')
        .then(response => {
          console.log('User data received:', response.data);
          this.users = response.data;
          this.loading = false;
        })
        .catch(error => {
          console.error('Error fetching users:', error);
          this.error = `Failed to fetch users: ${error.message}`;
          this.loading = false;
        });
    },
    fetchData() {
      if (!this.selectedUserId) {
        this.userRisks = [];
        this.reviewerTasks = [];
        return;
      }
      
      this.loading = true;
      
      // Only fetch user risks and reviewer tasks, not notifications
      Promise.all([
        axios.get(`http://localhost:8000/api/user-risks/${this.selectedUserId}/`),
        axios.get(`http://localhost:8000/api/reviewer-tasks/${this.selectedUserId}/`)
      ])
      .then(([userResponse, reviewerResponse]) => {
        this.userRisks = userResponse.data;
        this.reviewerTasks = reviewerResponse.data;
        
        // Add last submitted date to user risks by fetching latest review
        this.userRisks.forEach(risk => {
          axios.get(`http://localhost:8000/api/latest-review/${risk.RiskInstanceId}/`)
            .then(response => {
              if (response.data && response.data.user_submitted_date) {
                this.$set(risk, 'last_submitted', response.data.user_submitted_date);
              } else if (response.data && response.data.submission_date) {
                this.$set(risk, 'last_submitted', response.data.submission_date);
              }
            })
            .catch(error => {
              console.error(`Error fetching latest review for risk ${risk.RiskInstanceId}:`, error);
            });
        });
        
        console.log('User risks:', this.userRisks); // Log to verify data
        
        // Add notification icons based on risk status directly
        this.userRisks.forEach(risk => {
          if (risk.RiskStatus === 'Revision Required') {
            risk.hasNotification = true;
            risk.approved = false;
          } else if (risk.RiskStatus === 'Approved') {
            risk.hasNotification = true;
            risk.approved = true;
          }
        });
        
        this.loading = false;
        this.error = null;
      })
      .catch(error => {
        console.error('Error fetching data:', error);
        this.error = `Failed to fetch data: ${error.message}`;
        this.loading = false;
      });
    },
    getUserName(userId) {
      const user = this.users.find(u => u.user_id == userId);
      return user ? user.user_name : 'Unknown';
    },
    startWork(riskId) {
      this.loading = true;
      console.log(`Starting work on risk ID: ${riskId}`);
      
      // Ensure we're sending the correct data format
      const requestData = {
        risk_id: riskId,
        status: 'Work In Progress'
      };
      
      console.log('Sending request data:', requestData);
      
      // Update mitigation status instead of risk status
      axios.post('http://localhost:8000/api/update-mitigation-status/', requestData)
        .then(response => {
          console.log('Status updated:', response.data);
          // Update the local risk status
          const index = this.userRisks.findIndex(r => r.RiskInstanceId === riskId);
          if (index !== -1) {
            this.userRisks[index].MitigationStatus = 'Work In Progress';
          }
          this.loading = false;
        })
        .catch(error => {
          console.error('Error updating status:', error);
          console.error('Error response:', error.response ? error.response.data : 'No response data');
          this.error = `Failed to update status: ${error.message}`;
          this.loading = false;
        });
    },
    completeMitigation(riskId) {
      this.loading = true;
      axios.post('http://localhost:8000/api/update-mitigation-status/', {
        risk_id: riskId,
        status: 'Completed'
      })
      .then(response => {
        console.log('Status updated:', response.data);
        // Update the local risk status
        const index = this.userRisks.findIndex(r => r.RiskInstanceId === riskId);
        if (index !== -1) {
          this.userRisks[index].MitigationStatus = 'Completed';
          this.userRisks[index].RiskStatus = 'Approved'; // Also update risk status
        }
        this.loading = false;
        alert('Mitigation marked as completed!');
      })
      .catch(error => {
        console.error('Error updating status:', error);
        this.error = `Failed to update status: ${error.message}`;
        this.loading = false;
      });
    },
    viewMitigations(riskId) {
      this.selectedRiskId = riskId;
      this.loadingMitigations = true;
      this.showMitigationModal = true;
      
      // First, get the basic mitigation steps
      axios.get(`http://localhost:8000/api/risk-mitigations/${riskId}/`)
        .then(response => {
          console.log('Mitigations received:', response.data);
          this.mitigationSteps = this.parseMitigations(response.data);
          
          // Get the risk form details
          axios.get(`http://localhost:8000/api/risk-form-details/${riskId}/`)
            .then(formResponse => {
              console.log('Form details received:', formResponse.data);
              this.formDetails = formResponse.data;
              
              // Get the latest R version from risk_approval table to get approval status
              axios.get(`http://localhost:8000/api/latest-review/${riskId}/`)
                .then(reviewResponse => {
                  const reviewData = reviewResponse.data;
                  console.log('Latest review data:', reviewData);
                  
                  // Store the latest review
                  this.latestReview = reviewData;
                  
                  // Update form details with submission dates from the review data
                  if (reviewData && reviewData.risk_form_details) {
                    this.formDetails = {
                      ...this.formDetails,
                      approved: reviewData.risk_form_details.approved,
                      remarks: reviewData.risk_form_details.remarks || '',
                      user_submitted_date: reviewData.user_submitted_date || reviewData.submission_date,
                      reviewer_submitted_date: reviewData.reviewer_submitted_date || reviewData.review_date
                    };
                  }
                  
                  if (reviewData && reviewData.mitigations) {
                    // Create new steps array with proper boolean values for approved
                    const updatedSteps = [];
                    
                    // Process each mitigation from the review data
                    Object.keys(reviewData.mitigations).forEach(stepId => {
                      const mitigation = reviewData.mitigations[stepId];
                      
                      // Ensure approved is a proper boolean value if it exists, otherwise leave it undefined
                      let isApproved = undefined;
                      if ('approved' in mitigation) {
                        isApproved = mitigation.approved === true || mitigation.approved === "true";
                      }
                      
                      updatedSteps.push({
                        title: `Step ${stepId}`,
                        description: mitigation.description,
                        status: mitigation.status || 'Completed',
                        approved: isApproved,  // This could be undefined, true, or false
                        remarks: mitigation.remarks || '',
                        comments: mitigation.comments || '',
                        fileData: mitigation.fileData,
                        fileName: mitigation.fileName,
                        user_submitted_date: mitigation.user_submitted_date,  // Add user submission date
                        reviewer_submitted_date: mitigation.reviewer_submitted_date  // Add reviewer submission date
                      });
                    });
                    
                    // Replace the mitigation steps with the properly formatted data
                    this.mitigationSteps = updatedSteps;
                  }
                  
                  // Check if a reviewer is already assigned
                  axios.get(`http://localhost:8000/api/get-assigned-reviewer/${riskId}/`)
                    .then(reviewerResponse => {
                      if (reviewerResponse.data && reviewerResponse.data.reviewer_id) {
                        this.selectedReviewer = reviewerResponse.data.reviewer_id;
                      }
                      this.loadingMitigations = false;
                    })
                    .catch(error => {
                      console.error('Error fetching assigned reviewer:', error);
                      this.loadingMitigations = false;
                    });
                })
                .catch(error => {
                  console.error('Error fetching latest review:', error);
                  this.loadingMitigations = false;
                });
            })
            .catch(error => {
              console.error('Error fetching form details:', error);
              // Continue with default empty form details
              this.formDetails = {
                cost: '',
                impact: '',
                financialImpact: '',
                reputationalImpact: ''
              };
              this.loadingMitigations = false;
            });
        })
        .catch(error => {
          console.error('Error fetching mitigations:', error);
          this.mitigationSteps = [];
          this.loadingMitigations = false;
        });
    },
    fetchLatestReviewerData(riskId) {
      axios.get(`http://localhost:8000/api/latest-review/${riskId}/`)
        .then(response => {
          console.log('Latest review data:', response.data);
          
          if (response.data && response.data.mitigations) {
            // Update our mitigation steps with approval status and remarks
            const reviewData = response.data;
            
            this.mitigationSteps.forEach((step, index) => {
              const stepNumber = step.title.replace('Step ', '') || (index + 1).toString();
              if (reviewData.mitigations[stepNumber]) {
                const reviewInfo = reviewData.mitigations[stepNumber];
                step.approved = reviewInfo.approved;
                step.remarks = reviewInfo.remarks || '';
                
                // If this mitigation was already reviewed and had attached data
                if (reviewInfo.comments) step.comments = reviewInfo.comments;
                if (reviewInfo.fileData) {
                  step.fileData = reviewInfo.fileData;
                  step.fileName = reviewInfo.fileName;
                }
              }
            });
          }
          
          this.loadingMitigations = false;
        })
        .catch(error => {
          console.error('Error fetching review data:', error);
          this.loadingMitigations = false;
        });
    },
    parseMitigations(data) {
      // Handle the numbered object format like {"1": "Step 1 text", "2": "Step 2 text", ...}
      if (data && typeof data === 'object' && !Array.isArray(data)) {
        // Check if it's a numbered format
        const keys = Object.keys(data);
        if (keys.length > 0 && !isNaN(Number(keys[0]))) {
          const steps = [];
          // Sort keys numerically
          keys.sort((a, b) => Number(a) - Number(b));
          
          for (const key of keys) {
            steps.push({
              title: `Step ${key}`,
              description: data[key],
              status: 'Not Started'
            });
          }
          
          // Add these lines after creating steps
          for (const step of steps) {
            step.comments = step.comments || '';
            step.fileData = step.fileData || null;
            step.fileName = step.fileName || null;
          }
          return steps;
        }
      }
      
      // If it's already an array, return it
      if (Array.isArray(data)) {
        return data;
      }
      
      // If data is a string, try to parse it as JSON
      if (typeof data === 'string') {
        try {
          const parsedData = JSON.parse(data);
          // Check if the parsed data matches the numbered format
          if (parsedData && typeof parsedData === 'object' && !Array.isArray(parsedData)) {
            return this.parseMitigations(parsedData); // Recursively call to handle the parsed object
          }
          return Array.isArray(parsedData) ? parsedData : [parsedData];
        } catch (e) {
          console.error('Error parsing mitigation JSON:', e);
          return [{ title: 'Mitigation', description: data }];
        }
      }
      
      // Default fallback - create a single step with the data
      return [{ title: 'Mitigation', description: 'No detailed mitigation steps available' }];
    },
    closeMitigationModal() {
      this.showMitigationModal = false;
      this.mitigationSteps = [];
      this.selectedRiskId = null;
    },
    updateStepStatus(index, status) {
      console.log(`Updating step ${index + 1} status to ${status}`);
      
      // Update the step status locally
      this.mitigationSteps[index].status = status;
      
      // If all steps are completed, we don't need to update the backend yet
      // It will be sent when the user submits for review
    },
    submitForReview() {
      if (!this.canSubmit) return;
      
      this.loading = true;
      
      // Prepare the mitigation data
      const mitigationData = {};
      this.mitigationSteps.forEach((step, index) => {
        // Extract step number from title or use index+1
        const stepNumber = step.title.replace('Step ', '') || (index + 1).toString();
        
        // If this step was previously approved, keep its approval
        if (step.approved === true) {
          mitigationData[stepNumber] = {
            description: step.description,
            status: step.status || 'Completed',
            approved: true,
            remarks: "",
            comments: step.comments || "",
            fileData: step.fileData,
            fileName: step.fileName
          };
        } else {
          // For rejected or new mitigations, include the updated data
          // but don't set 'approved' for new submissions
          const mitigationInfo = {
            description: step.description,
            status: step.status || 'Completed',
            comments: step.comments || "",
            fileData: step.fileData,
            fileName: step.fileName
          };
          
          // Only include approved and remarks if they were previously set
          if (step.approved === false) {
            mitigationInfo.approved = false;
            mitigationInfo.remarks = step.remarks || "";
          }
          
          mitigationData[stepNumber] = mitigationInfo;
        }
      });
      
      // Add timestamp to form details
      const formDetailsWithTimestamp = {
        ...this.formDetails,
        user_submitted_date: new Date().toISOString()
      };
      
      axios.post('http://localhost:8000/api/assign-reviewer/', {
        risk_id: this.selectedRiskId,
        reviewer_id: this.selectedReviewer,
        user_id: this.selectedUserId,
        mitigations: mitigationData,
        risk_form_details: formDetailsWithTimestamp  // Use the updated form details with timestamp
      })
      .then(response => {
        console.log('Reviewer assigned:', response.data);
        // Update the risk mitigation status to indicate it's under review
        return axios.post('http://localhost:8000/api/update-mitigation-status/', {
          risk_id: this.selectedRiskId,
          status: 'Revision Required by Reviewer'
        });
      })
      .then(response => {
        console.log('Status updated to under review:', response.data);
        // Update the local risk data to show the new status
        const index = this.userRisks.findIndex(r => r.RiskInstanceId === this.selectedRiskId);
        if (index !== -1) {
          this.userRisks[index].MitigationStatus = 'Revision Required by Reviewer';
          // Keep RiskStatus as 'Assigned'
        }
        this.loading = false;
        // Close the modal
        this.closeMitigationModal();
        // Show success message
        alert('Risk submitted for review successfully!');
      })
      .catch(error => {
        console.error('Error assigning reviewer:', error);
        this.loading = false;
        alert('Failed to submit for review. Please try again.');
      });
    },
    closeReviewerModal() {
      this.showReviewerModal = false;
      this.currentReviewTask = null;
      this.mitigationReviewData = {};
    },
    approveMitigation(id, approved) {
      // Don't use this.$set directly - modify the object properly for Vue reactivity
      
      // Create a new object with all existing properties
      const updatedMitigation = {
        ...this.mitigationReviewData[id],
        approved: approved,
        reviewer_submitted_date: new Date().toISOString()
      };
      
      // If approved, clear any existing remarks
      if (approved) {
        updatedMitigation.remarks = '';
      }
      
      // Update the entire object at once (Vue will detect this change)
      this.mitigationReviewData = {
        ...this.mitigationReviewData,
        [id]: updatedMitigation
      };
      
      // Find the mitigation element and update visual feedback
      const mitigationElement = document.querySelector(`.mitigation-review-item[data-id="${id}"]`);
      if (mitigationElement) {
        // Update visual feedback
        const statusBadge = mitigationElement.querySelector('.mitigation-status-badge');
        if (statusBadge) {
          statusBadge.className = `mitigation-status-badge ${approved ? 'approved' : 'rejected'}`;
          statusBadge.innerHTML = approved ? 
            '<i class="fas fa-check-circle"></i> Approved' : 
            '<i class="fas fa-times-circle"></i> Rejected';
        }
      }
    },
    submitReview(approved) {
      if (!this.canSubmitReview) {
        alert('Please complete the review of all mitigations and the questionnaire');
        return;
      }
      
      this.loading = true;
      
      // Prepare the final data with all mitigations and questionnaire
      const reviewData = {
        approval_id: this.currentReviewTask.RiskInstanceId,
        risk_id: this.currentReviewTask.RiskInstanceId,
        approved: approved,
        mitigations: this.mitigationReviewData,
        risk_form_details: {
          ...this.formDetails,
          approved: this.formDetails.approved,
          remarks: this.formDetails.remarks || ''
        }
      };
      
      // Print the complete review data for debugging
      console.log('SUBMITTING REVIEW DATA:', JSON.stringify(reviewData, null, 2));
      
      // Send the complete review with all mitigations and questionnaire in one request
      axios.post('http://localhost:8000/api/complete-review/', reviewData)
        .then(response => {
          console.log('Review completed:', response.data);
          this.loading = false;
          
          // Remove this task from the list
          const index = this.reviewerTasks.findIndex(t => t.RiskInstanceId === this.currentReviewTask.RiskInstanceId);
          if (index !== -1) {
            this.reviewerTasks.splice(index, 1);
          }
          
          // Close the modal
          this.closeReviewerModal();
          
          // Show success message
          alert(`Risk ${approved ? 'approved' : 'rejected'} successfully!`);
        })
        .catch(error => {
          console.error('Error completing review:', error);
          this.loading = false;
          alert('Failed to submit review. Please try again.');
        });
    },
    updateRemarks(id) {
      if (!this.mitigationReviewData[id].remarks.trim()) {
        alert('Please provide remarks for rejection');
        return;
      }
      
      // Create a new object with spread operator to trigger reactivity
      this.mitigationReviewData = {
        ...this.mitigationReviewData
      };
      
      // Show visual confirmation
      console.log(`Mitigation ${id} remarks updated successfully`);
    },
    handleFileUpload(event, index) {
      const file = event.target.files[0];
      if (!file) return;
      
      // Check file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('File size exceeds 5MB limit');
        event.target.value = '';
        return;
      }
      
      const reader = new FileReader();
      reader.onload = (e) => {
        // Store file data as base64 string for preview
        this.mitigationSteps[index].fileData = e.target.result;
        this.mitigationSteps[index].fileName = file.name;
        
        // First save locally, then upload to S3
        axios.post('http://localhost:8000/api/save-uploaded-file/', {
          fileData: e.target.result,
          fileName: file.name,
          riskId: this.selectedRiskId,
          category: this.userRisks.find(r => r.RiskInstanceId === this.selectedRiskId)?.Category || 'general',
          mitigationNumber: index + 1
        })
        .then(response => {
          console.log('File processed successfully:', response.data);
          
          // Store the S3 information
          this.mitigationSteps[index].savedFileName = response.data.savedFileName;
          this.mitigationSteps[index].s3FileInfo = response.data.s3FileInfo;
          
          // Optional: Add alert or notification
          alert('File uploaded successfully');
        })
        .catch(error => {
          console.error('Error processing file:', error);
          alert('Error uploading file. Please try again.');
        });
      };
      reader.readAsDataURL(file);
    },
    removeFile(index) {
      this.mitigationSteps[index].fileData = null;
      this.mitigationSteps[index].fileName = null;
      // Reset the file input
      document.getElementById(`file-upload-${index}`).value = '';
    },
    fetchReviewerComments(riskId) {
      axios.get(`http://localhost:8000/api/reviewer-comments/${riskId}/`)
        .then(response => {
          // Find the risk in the userRisks array and add the reviewer comments
          const riskIndex = this.userRisks.findIndex(r => r.RiskInstanceId === riskId);
          if (riskIndex !== -1) {
            this.$set(this.userRisks[riskIndex], 'reviewerComments', response.data);
          }
        })
        .catch(error => {
          console.error('Error fetching reviewer comments:', error);
        });
    },
    getStatusClass(status) {
      if (status === 'Approved') return 'status-approved';
      if (status === 'Revision Required') return 'status-revision';
      if (status === 'Under Review') return 'status-review';
      if (status === 'Work In Progress') return 'status-progress';
      return '';
    },
    // Complete a step
    completeStep(index) {
      // Only allow completing if previous steps are completed
      if (this.isStepLocked(index)) return;
      
      this.mitigationSteps[index].status = 'Completed';
      
      // Animate the timeline progress
      this.$nextTick(() => {
        // Use setTimeout to ensure the DOM has updated
        setTimeout(() => {
          const timelineEl = document.querySelector('.timeline');
          if (timelineEl) {
            timelineEl.classList.add('step-completed');
            setTimeout(() => {
              timelineEl.classList.remove('step-completed');
            }, 1000);
          }
        }, 50);
      });
    },
    
    // Reset a step to not completed
    resetStep(index) {
      this.mitigationSteps[index].status = 'In Progress';
    },
    isStepActive(index) {
      // A step is active if all previous steps are completed
      // and this step is not completed or is rejected
      if (this.mitigationSteps[index].approved === false) return true;
      
      for (let i = 0; i < index; i++) {
        if (this.mitigationSteps[i].status !== 'Completed') return false;
      }
      
      return this.mitigationSteps[index].status !== 'Completed';
    },
    
    isStepLocked(index) {
      // A step is locked if any previous step is not completed
      if (index === 0) return false; // First step is never locked
      
      for (let i = 0; i < index; i++) {
        if (this.mitigationSteps[i].status !== 'Completed') return true;
      }
      
      return false;
    },
    formatDate(dateString) {
      if (!dateString) return 'Not set';
      
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    getDueStatusClass(dateString) {
      if (!dateString) return '';
      
      const dueDate = new Date(dateString);
      const today = new Date();
      
      // Reset the time part for accurate day comparison
      dueDate.setHours(0, 0, 0, 0);
      today.setHours(0, 0, 0, 0);
      
      const daysLeft = Math.floor((dueDate - today) / (1000 * 60 * 60 * 24));
      
      if (daysLeft < 0) return 'overdue';
      if (daysLeft <= 3) return 'urgent';
      if (daysLeft <= 7) return 'warning';
      return 'on-track';
    },
    getDueStatusText(dateString) {
      if (!dateString) return '';
      
      const dueDate = new Date(dateString);
      const today = new Date();
      
      // Reset the time part for accurate day comparison
      dueDate.setHours(0, 0, 0, 0);
      today.setHours(0, 0, 0, 0);
      
      const daysLeft = Math.floor((dueDate - today) / (1000 * 60 * 60 * 24));
      
      if (daysLeft < 0) return `(Delayed by ${Math.abs(daysLeft)} days)`;
      if (daysLeft === 0) return '(Due today)';
      if (daysLeft === 1) return '(Due tomorrow)';
      return `(${daysLeft} days left)`;
    },
    getMitigationStatusClass(status) {
      if (!status) return '';
      
      const statusLower = status.toLowerCase();
      if (statusLower.includes('completed')) return 'status-completed';
      if (statusLower.includes('progress')) return 'status-progress';
      if (statusLower.includes('revision')) return 'status-revision';
      if (statusLower.includes('yet to start')) return 'status-not-started';
      return '';
    },
    hasApprovalVersion(task) {
      // Check if we have extracted info, which means there's a version
      try {
        if (task.ExtractedInfo) {
          const extractedInfo = JSON.parse(task.ExtractedInfo);
          return extractedInfo && extractedInfo.version;
        }
      } catch (error) {
        console.error('Error checking approval version:', error);
      }
      return false;
    },
    isQuestionnaireComplete() {
      return (
        this.formDetails.cost.trim() !== '' &&
        this.formDetails.impact.trim() !== '' &&
        this.formDetails.financialImpact.trim() !== '' &&
        this.formDetails.reputationalImpact.trim() !== ''
      );
    },
    validateQuestionnaire() {
      // This will be called on each input to ensure sequential completion
    },
    reviewMitigations(task) {
      this.currentReviewTask = task;
      this.selectedRiskId = task.RiskInstanceId;
      this.loadingMitigations = true;
      this.showReviewerModal = true;
      this.previousVersions = {}; // Initialize empty object for previous versions
      
      try {
        // Extract the mitigations from the ExtractedInfo JSON
        const extractedInfo = JSON.parse(task.ExtractedInfo);
        console.log('Extracted info:', extractedInfo);
        
        if (extractedInfo && extractedInfo.mitigations) {
          this.mitigationReviewData = extractedInfo.mitigations;
          
          // Also get form details if available
          if (extractedInfo.risk_form_details) {
            // Preserve approval status and remarks if they exist
            this.formDetails = {
              cost: extractedInfo.risk_form_details.cost || '',
              impact: extractedInfo.risk_form_details.impact || '',
              financialImpact: extractedInfo.risk_form_details.financialImpact || '',
              reputationalImpact: extractedInfo.risk_form_details.reputationalImpact || '',
              approved: extractedInfo.risk_form_details.approved,
              remarks: extractedInfo.risk_form_details.remarks || '',
              user_submitted_date: extractedInfo.risk_form_details.user_submitted_date || extractedInfo.user_submitted_date,
              reviewer_submitted_date: extractedInfo.risk_form_details.reviewer_submitted_date
            };
          } else {
            // Reset form details to empty
            this.formDetails = {
              cost: '',
              impact: '',
              financialImpact: '',
              reputationalImpact: '',
              approved: undefined,
              remarks: ''
            };
          }
          
          // Get previous versions from the task data that now includes it
          if (task.PreviousVersion && task.PreviousVersion.mitigations) {
            this.previousVersions = task.PreviousVersion.mitigations;
            
            // If there are previous form details, save them for comparison
            if (task.PreviousVersion.risk_form_details) {
              this.previousFormDetails = task.PreviousVersion.risk_form_details;
            }
          }
          
          // Add task status info for completed tasks
          const isCompleted = task.RiskStatus === 'Approved' || task.RiskStatus === 'Revision Required';
          this.reviewCompleted = isCompleted;
          this.reviewApproved = task.RiskStatus === 'Approved';
          
          this.loadingMitigations = false;
        } else {
          this.mitigationReviewData = {};
          console.error('No mitigations found in ExtractedInfo');
          this.loadingMitigations = false;
        }
      } catch (error) {
        console.error('Error parsing ExtractedInfo:', error);
        this.mitigationReviewData = {};
        this.loadingMitigations = false;
      }
    },
    approveQuestionnaire(approved) {
      // Update approval status
      this.formDetails.approved = approved;
      
      // Add timestamp for reviewer
      this.formDetails.reviewer_submitted_date = new Date().toISOString();
      
      // If rejecting, ensure there's a remarks field
      if (!approved && !this.formDetails.remarks) {
        this.formDetails.remarks = '';
      }
      
      // If approving, clear any remarks
      if (approved) {
        this.formDetails.remarks = '';
      }
    },
    saveQuestionnaireRemarks() {
      // Validate that remarks are provided when rejecting
      if (this.formDetails.approved === false && !this.formDetails.remarks.trim()) {
        alert('Please provide feedback for the questionnaire');
        return;
      }
      
      // Show confirmation to the user
      alert('Questionnaire feedback saved');
    },
    // Format date and time
    formatDateTime(dateString) {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    },
    // Extract submission date from task
    getSubmissionDate(task) {
      try {
        if (task.ExtractedInfo) {
          const extractedInfo = JSON.parse(task.ExtractedInfo);
          return extractedInfo.user_submitted_date || extractedInfo.submission_date;
        }
      } catch (error) {
        console.error('Error parsing submission date:', error);
      }
      return null;
    },
    getPreviousMitigation(id) {
      // Check if we have previous versions stored
      if (!this.previousVersions || !this.previousVersions[id]) {
        return null;
      }
      return this.previousVersions[id];
    },
    getPreviousFormDetail(field) {
      if (!this.previousFormDetails) {
        return null;
      }
      return this.previousFormDetails[field] || 'Not specified';
    },
    // Add this method to check if form field has changed
    hasFormFieldChanged(field) {
      if (!this.previousFormDetails) {
        return false;
      }
      
      const prevValue = this.previousFormDetails[field] || '';
      const currentValue = this.formDetails[field] || '';
      
      return prevValue !== currentValue;
    },
    getFieldLabel(field) {
      const labels = {
        'cost': 'Cost for Mitigation',
        'impact': 'Impact for Mitigation',
        'financialImpact': 'Financial Impact',
        'reputationalImpact': 'Reputational Impact'
      };
      return labels[field] || field;
    }
  }
}
</script>

<style>
@import './UserTask.css';

/* Update due status styling to be more visible */
.due-status {
  margin-left: 8px;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}

.due-status.overdue {
  background-color: #fff1f0;
  color: #f5222d;
  border: 1px solid #ffa39e;
}

.due-status.urgent {
  background-color: #fff7e6;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.due-status.warning {
  background-color: #fffbe6;
  color: #faad14;
  border: 1px solid #ffe58f;
}

.due-status.on-track {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.mitigation-status {
  margin-left: 10px;
  font-size: 12px;
  color: #606266;
  padding: 2px 8px;
  background-color: #f5f5f5;
  border-radius: 10px;
}

/* Add styles for mitigation status badges */
.mitigation-status.status-completed {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.mitigation-status.status-progress {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.mitigation-status.status-revision {
  background-color: #fff1f0;
  color: #f5222d;
  border: 1px solid #ffa39e;
}

.mitigation-status.status-not-started {
  background-color: #f5f5f5;
  color: #8c8c8c;
  border: 1px solid #d9d9d9;
}

.complete-btn {
  background-color: #52c41a;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.complete-btn:hover {
  background-color: #73d13d;
}

/* Add these new styles for submission dates */
.submission-date {
  font-size: 12px;
  margin-top: 5px;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 4px;
  width: fit-content;
}

.submission-date.user-date {
  background-color: #e6f7ff;
  color: #1890ff;
}

.submission-date.reviewer-date {
  background-color: #f6ffed;
  color: #52c41a;
}
</style>

