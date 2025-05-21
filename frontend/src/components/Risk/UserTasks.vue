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
            <p><strong>Status:</strong> <span :class="'status-' + risk.RiskStatus?.toLowerCase().replace(/\s+/g, '-')">{{ risk.RiskStatus || 'Not Started' }}</span></p>
            <p><strong>Priority:</strong> {{ risk.RiskPriority }}</p>
            <p><strong>Assigned To:</strong> {{ getUserName(risk.UserId) }}</p>
            
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
              v-if="risk.RiskStatus === 'Revision Required'" 
              @click="startWork(risk.RiskInstanceId)" 
              class="start-btn">
              Start Revision
            </button>
            <button 
              v-else-if="risk.RiskStatus !== 'Work In Progress'" 
              @click="startWork(risk.RiskInstanceId)" 
              class="start-btn">
              Start Work
            </button>
            <button @click="viewMitigations(risk.RiskInstanceId)" class="view-btn">
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
            <p><strong>Status:</strong> <span :class="'status-' + task.RiskStatus?.toLowerCase().replace(/\s+/g, '-')">{{ task.RiskStatus || 'Under Review' }}</span></p>
            <p><strong>Priority:</strong> {{ task.RiskPriority }}</p>
            <p><strong>Submitted By:</strong> {{ getUserName(task.UserId) }}</p>
          </div>
          
          <div class="action-buttons">
            <button @click="reviewMitigations(task)" class="review-btn">
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
            
            <!-- Simplified submission section -->
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
            
            <div class="mitigation-review-list">
              <div 
                v-for="(mitigation, id) in mitigationReviewData" 
                :key="id" 
                class="mitigation-review-item"
                :data-id="id"
              >
                <div class="mitigation-description">
                  <h4>Mitigation #{{ id }}</h4>
                  <p>{{ mitigation.description }}</p>
                  
                  <!-- Display user comments if available -->
                  <div v-if="mitigation.comments" class="user-comments">
                    <h5>User Comments:</h5>
                    <p class="comment-text">{{ mitigation.comments }}</p>
                  </div>
                  
                  <!-- Display uploaded file if available -->
                  <div v-if="mitigation.fileData" class="uploaded-evidence">
                    <h5>Uploaded Evidence:</h5>
                    <a :href="mitigation.fileData" download :filename="mitigation.fileName" class="evidence-link">
                      <i class="fas fa-file-download"></i> {{ mitigation.fileName }}
                    </a>
                  </div>
                  
                  <!-- Add a status indicator when approved -->
                  <div v-if="mitigation.approved === true" class="approval-status approved">
                    <i class="fas fa-check-circle"></i> Approved
                  </div>
                </div>
                
                <div class="approval-controls">
                  <!-- Only show approval buttons if not yet approved or rejected -->
                  <div v-if="mitigation.approved !== true && mitigation.approved !== false" class="approval-buttons">
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
                  <div v-if="mitigation.approved === false" class="remarks-field">
                    <label for="remarks">Remarks (required for rejection):</label>
                    <textarea 
                      id="remarks" 
                      v-model="mitigation.remarks" 
                      class="remarks-input" 
                      placeholder="Provide feedback for the rejected mitigation..."
                    ></textarea>
                    
                    <!-- Add a button to save remarks -->
                    <button @click="updateRemarks(id)" class="save-remarks-btn">
                      <i class="fas fa-save"></i> Save Remarks
                    </button>
                    
                    <!-- Allow changing decision -->
                    <button @click="approveMitigation(id, true)" class="change-decision-btn">
                      <i class="fas fa-exchange-alt"></i> Change to Approve
                    </button>
                  </div>
                  
                  <!-- Show status and action buttons for approved items -->
                  <div v-if="mitigation.approved === true" class="approved-actions">
                    <button @click="approveMitigation(id, false)" class="change-decision-btn">
                      <i class="fas fa-exchange-alt"></i> Change to Reject
                    </button>
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
      reviewApproved: false
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
      return this.allStepsCompleted && this.selectedReviewer && hasRejectedOrNewSteps;
    },
    canSubmitReview() {
      return Object.values(this.mitigationReviewData).every(m => 
        m.approved === true || (m.approved === false && m.remarks && m.remarks.trim() !== '')
      );
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
      axios.post('http://localhost:8000/api/risk-update-status/', {
        risk_id: riskId,
        status: 'Work In Progress'
      })
      .then(response => {
        console.log('Status updated:', response.data);
        // Update the local risk status
        const index = this.userRisks.findIndex(r => r.RiskInstanceId === riskId);
        if (index !== -1) {
          this.userRisks[index].RiskStatus = 'Work In Progress';
        }
        this.loading = false;
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
          
          // Get the latest R version from risk_approval table to get approval status
          axios.get(`http://localhost:8000/api/latest-review/${riskId}/`)
            .then(reviewResponse => {
              const reviewData = reviewResponse.data;
              console.log('Latest review data:', reviewData);
              
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
                    fileName: mitigation.fileName
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
              
              // Try to get assigned reviewer even if review data fails
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
      
      // Prepare the mitigation data - only include rejected or not-yet-reviewed steps
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
      
      axios.post('http://localhost:8000/api/assign-reviewer/', {
        risk_id: this.selectedRiskId,
        reviewer_id: this.selectedReviewer,
        user_id: this.selectedUserId,
        mitigations: mitigationData
      })
      .then(response => {
        console.log('Reviewer assigned:', response.data);
        // Update the risk status to indicate it's under review
        return axios.post('http://localhost:8000/api/risk-update-status/', {
          risk_id: this.selectedRiskId,
          status: 'Under Review'
        });
      })
      .then(response => {
        console.log('Status updated to Under Review:', response.data);
        // Update the local risk data to show the new status
        const index = this.userRisks.findIndex(r => r.RiskInstanceId === this.selectedRiskId);
        if (index !== -1) {
          this.userRisks[index].RiskStatus = 'Under Review';
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
    reviewMitigations(task) {
      this.currentReviewTask = task;  // Store the entire task object for reference
      this.selectedRiskId = task.RiskInstanceId;
      this.loadingMitigations = true;
      this.showReviewerModal = true;
      
      try {
        // Extract the mitigations from the ExtractedInfo JSON
        const extractedInfo = JSON.parse(task.ExtractedInfo);
        console.log('Extracted info:', extractedInfo);
        
        if (extractedInfo && extractedInfo.mitigations) {
          this.mitigationReviewData = extractedInfo.mitigations;
          
          // Add task status info for completed tasks
          const isCompleted = task.RiskStatus === 'Approved' || task.RiskStatus === 'Revision Required';
          this.reviewCompleted = isCompleted;
          this.reviewApproved = task.RiskStatus === 'Approved';
        } else {
          this.mitigationReviewData = {};
          console.error('No mitigations found in ExtractedInfo');
        }
        
        this.loadingMitigations = false;
      } catch (error) {
        console.error('Error parsing ExtractedInfo:', error);
        this.mitigationReviewData = {};
        this.loadingMitigations = false;
      }
    },
    closeReviewerModal() {
      this.showReviewerModal = false;
      this.currentReviewTask = null;
      this.mitigationReviewData = {};
    },
    approveMitigation(id, approved) {
      // Update the mitigation approval status locally
      this.mitigationReviewData[id].approved = approved;
      
      // If approved, clear any existing remarks (no need for remarks on approved items)
      if (approved) {
        this.mitigationReviewData[id].remarks = '';
      }
      
      // Find the mitigation element without declaring unused statusText variable
      const mitigationElement = document.querySelector(`.mitigation-review-item[data-id="${id}"]`);
      if (mitigationElement) {
        // Update visual feedback
        if (approved) {
          const approvalStatus = mitigationElement.querySelector('.approval-status') || 
            document.createElement('div');
          approvalStatus.className = 'approval-status approved';
          approvalStatus.innerHTML = '<i class="fas fa-check-circle"></i> Approved';
          
          // Add it if not already present
          if (!mitigationElement.querySelector('.approval-status')) {
            mitigationElement.querySelector('.mitigation-description').appendChild(approvalStatus);
          }
        }
      }
    },
    submitReview(approved) {
      if (!this.canSubmitReview) return;
      
      this.loading = true;
      
      // Prepare the final data with all mitigations
      const reviewData = {
        approval_id: this.currentReviewTask.RiskInstanceId,
        risk_id: this.currentReviewTask.RiskInstanceId,
        approved: approved,
        mitigations: this.mitigationReviewData
      };
      
      // Print the complete review data for debugging
      console.log('SUBMITTING REVIEW DATA:', JSON.stringify(reviewData, null, 2));
      
      // Send the complete review with all mitigations in one request
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
      
      // Now update the backend with rejection and remarks
      this.updateMitigationOnServer(id);
    },
    updateMitigationOnServer(id) {
      const mitigation = this.mitigationReviewData[id];
      
      // Instead of sending to server, just update locally
      console.log(`Mitigation ${id} approval status updated locally: approved=${mitigation.approved}, remarks=${mitigation.remarks}`);
      
      // Create visual confirmation without using the statusText variable
      const icon = document.createElement('span');
      icon.className = `status-update-confirmation ${mitigation.approved ? 'approved' : 'rejected'}`;
      icon.innerHTML = mitigation.approved ? 
        '<i class="fas fa-check"></i> Saved' : 
        '<i class="fas fa-times"></i> Saved';
      
      // Find the mitigation element and append the confirmation
      const mitigationElement = document.querySelector(`.mitigation-review-item[data-id="${id}"]`);
      if (mitigationElement) {
        // Remove any existing confirmation
        const existingConfirmation = mitigationElement.querySelector('.status-update-confirmation');
        if (existingConfirmation) {
          existingConfirmation.remove();
        }
        mitigationElement.querySelector('.approval-controls').appendChild(icon);
        
        // Remove the confirmation after 2 seconds
        setTimeout(() => {
          icon.remove();
        }, 2000);
      }
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
        // Store file data as base64 string
        this.mitigationSteps[index].fileData = e.target.result;
        this.mitigationSteps[index].fileName = file.name;
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
    }
  }
}
</script>

<style>
@import './UserTask.css';
</style>

