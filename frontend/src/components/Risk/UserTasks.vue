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
    
    <!-- User Tasks Section with Table -->
    <div v-if="activeTab === 'user'">
      <div v-if="!selectedUserId" class="no-data">
        <p>Please select a user to view their assigned risks.</p>
      </div>
      <div v-else-if="userRisks.length === 0" class="no-data">
        <p>No risks assigned to this user.</p>
      </div>
      <div v-else class="table-container">
        <table class="risk-table">
          <thead>
            <tr>
              <th>RiskID</th>
              <th>Origin</th>
              <th>Category</th>
              <th>Criticality</th>
              <th>Risk Description</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="risk in userRisks" :key="risk.RiskInstanceId">
              <td>{{ risk.RiskInstanceId }}</td>
              <td>{{ risk.Origin || 'MANUAL' }}</td>
              <td>{{ risk.Category }}</td>
              <td>
                <span 
                  class="criticality-badge"
                  :class="{
                    'criticality-critical': risk.Criticality && risk.Criticality.toLowerCase() === 'critical',
                    'criticality-high': risk.Criticality && risk.Criticality.toLowerCase() === 'high',
                    'criticality-medium': risk.Criticality && risk.Criticality.toLowerCase() === 'medium',
                    'criticality-low': risk.Criticality && risk.Criticality.toLowerCase() === 'low'
                  }"
                >
                  {{ risk.Criticality }}
                </span>
              </td>
              <td class="risk-description">{{ risk.RiskDescription }}</td>
              <td>
                <div class="status-wrapper">
                  <div class="status-line">
              <span :class="'status-' + risk.RiskStatus?.toLowerCase().replace(/\s+/g, '-')">
                {{ risk.RiskStatus || 'Not Assigned' }}
              </span>
              <span class="mitigation-status" :class="getMitigationStatusClass(risk.MitigationStatus)">
                {{ risk.MitigationStatus || 'Yet to Start' }}
              </span>
            </div>
            
                  <!-- Due date info -->
                  <div v-if="risk.MitigationDueDate" class="due-date">
                    {{ formatDate(risk.MitigationDueDate) }}
                    <span class="due-status" :class="getDueStatusClass(risk.MitigationDueDate)">
                      {{ getDueStatusText(risk.MitigationDueDate) }}
                    </span>
              </div>
            </div>
              </td>
              <td class="actions-column">
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
              @click="viewMitigations(risk.RiskInstanceId)" 
              class="view-btn"
              :disabled="risk.MitigationStatus === 'Yet to Start'"
              :class="{'disabled-btn': risk.MitigationStatus === 'Yet to Start'}">
                  <i class="fas fa-eye"></i> View
                </button>
                
                <!-- Show revision notice if applicable -->
                <div v-if="risk.RiskStatus === 'Revision Required'" class="revision-notice">
                  <button @click="viewMitigations(risk.RiskInstanceId)" class="view-feedback-btn">
                    <i class="fas fa-eye"></i> View Feedback
            </button>
          </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Reviewer Tasks Section with Table -->
    <div v-if="activeTab === 'reviewer'">
      <div v-if="!selectedUserId" class="no-data">
        <p>Please select a user to view their reviewer tasks.</p>
      </div>
      <div v-else-if="reviewerTasks.length === 0" class="no-data">
        <p>No review tasks assigned to this user.</p>
      </div>
      <div v-else class="table-container">
        <table class="risk-table">
          <thead>
            <tr>
              <th>RiskID</th>
              <th>Origin</th>
              <th>Category</th>
              <th>Criticality</th>
              <th>Risk Description</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in reviewerTasks" :key="task.RiskInstanceId"
             :class="{
                  'completed-row': task.RiskStatus === 'Approved',
                  'revision-row': task.RiskStatus === 'Revision Required'
             }">
              <td>{{ task.RiskInstanceId }}</td>
              <td>{{ task.Origin || 'MANUAL' }}</td>
              <td>{{ task.Category }}</td>
              <td>
                <span 
                  class="criticality-badge"
                  :class="{
                    'criticality-critical': task.Criticality && task.Criticality.toLowerCase() === 'critical',
                    'criticality-high': task.Criticality && task.Criticality.toLowerCase() === 'high',
                    'criticality-medium': task.Criticality && task.Criticality.toLowerCase() === 'medium',
                    'criticality-low': task.Criticality && task.Criticality.toLowerCase() === 'low'
                  }"
                >
                  {{ task.Criticality }}
                </span>
              </td>
              <td class="risk-description">{{ task.RiskDescription }}</td>
              <td>
                <div class="status-wrapper">
                  <div class="status-line">
                    <span :class="'status-' + task.RiskStatus?.toLowerCase().replace(/\s+/g, '-')">
                      {{ task.RiskStatus || 'Not Started' }}
                    </span>
                    <span class="mitigation-status">{{ task.MitigationStatus || 'Yet to Start' }}</span>
          </div>
          
                  <!-- Due date info -->
                  <div v-if="task.MitigationDueDate" class="due-date">
                {{ formatDate(task.MitigationDueDate) }}
                <span class="due-status" :class="getDueStatusClass(task.MitigationDueDate)">
                  {{ getDueStatusText(task.MitigationDueDate) }}
                </span>
          </div>
          
                  <div class="submitted-by">
                    By: {{ getUserName(task.UserId) }}
                  </div>
                </div>
              </td>
              <td class="actions-column">
            <button 
              @click="reviewMitigations(task)" 
              class="review-btn"
              :disabled="!hasApprovalVersion(task)"
              :class="{'disabled-btn': !hasApprovalVersion(task)}">
                  <i class="fas fa-tasks"></i> Review
            </button>
              </td>
            </tr>
          </tbody>
        </table>
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
            
            <!-- Update the form details review section in the reviewer modal -->
            <div class="form-details-review">
              <h4>Risk Mitigation Questionnaire</h4>
              
              <div class="form-review-item">
                <h5>Cost for Mitigation:</h5>
                <p>{{ formDetails.cost || 'Not specified' }}</p>
              </div>
              
              <div class="form-review-item">
                <h5>Impact for Mitigation:</h5>
                <p>{{ formDetails.impact || 'Not specified' }}</p>
              </div>
              
              <div class="form-review-item">
                <h5>Financial Impact:</h5>
                <p>{{ formDetails.financialImpact || 'Not specified' }}</p>
              </div>
              
              <div class="form-review-item">
                <h5>Reputational Impact:</h5>
                <p>{{ formDetails.reputationalImpact || 'Not specified' }}</p>
              </div>
              
              <!-- Add questionnaire approval controls -->
              <div class="questionnaire-approval">
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
      showReviewerModal: false,
      loadingMitigations: false,
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
      latestReview: null,
      activeTab: 'user'
    }
  },
  computed: {
    canSubmitReview() {
      const allMitigationsReviewed = Object.values(this.mitigationReviewData).every(m => 
        m.approved === true || (m.approved === false && m.remarks && m.remarks.trim() !== '')
      );
      
      // Also require the questionnaire to be reviewed
      const questionnaireReviewed = 
        this.formDetails.approved === true || 
        (this.formDetails.approved === false && this.formDetails.remarks && this.formDetails.remarks.trim() !== '');
      
      return allMitigationsReviewed && questionnaireReviewed;
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
      this.$router.push({ 
        name: 'MitigationWorkflow', 
        params: { riskId: riskId } 
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
    reviewMitigations(task) {
      this.$router.push({
        name: 'ReviewerWorkflow',
        params: { riskId: task.RiskInstanceId }
      });
    },
    approveQuestionnaire(approved) {
      // Don't use this.$set directly, just update the property
      this.formDetails.approved = approved;
      
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
  background-color: transparent;
  color: #f5222d;
  border: 1px solid #ffa39e;
}

.due-status.urgent {
  background-color: transparent;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.due-status.warning {
  background-color: transparent;
  color: #faad14;
  border: 1px solid #ffe58f;
}

.due-status.on-track {
  background-color: transparent;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.mitigation-status {
  margin-left: 10px;
  font-size: 12px;
  color: #606266;
  padding: 2px 8px;
  background-color: transparent;
  border-radius: 10px;
}

/* Add styles for mitigation status badges */
.mitigation-status.status-completed {
  background-color: transparent;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.mitigation-status.status-progress {
  background-color: transparent;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.mitigation-status.status-revision {
  background-color: transparent;
  color: #f5222d;
  border: 1px solid #ffa39e;
}

.mitigation-status.status-not-started {
  background-color: transparent;
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
</style>

