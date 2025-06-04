<template>
  <div class="workflow-container">
    <h1>Risk Mitigation Workflow</h1>
    
    <div class="workflow-header">
      <div class="back-button">
        <button @click="goBack" class="return-btn">
          <i class="fas fa-arrow-left"></i> Return to Tasks
        </button>
      </div>
    </div>
    
    <div v-if="loading" class="loading">
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
      
      <!-- Add this after the timeline and before the submission area -->
      <div class="mitigation-questionnaire" v-if="allStepsCompleted">
        <h3>Risk Mitigation Questionnaire</h3>
        <p class="questionnaire-note">Please complete all fields to proceed with submission</p>
        
        <div class="question-group">
          <label for="cost-input">What is the cost for this mitigation?</label>
          <textarea 
            id="cost-input" 
            :value="formDetails.cost" 
            placeholder="Describe the cost..."
            :disabled="!allStepsCompleted"
            @input="e => { formDetails.cost = e.target.value; validateQuestionnaire(); }"
          ></textarea>
        </div>
        
        <div class="question-group" :class="{ 'disabled': !formDetails.cost }">
          <label for="impact-input">What is the impact for this mitigation?</label>
          <textarea 
            id="impact-input" 
            :value="formDetails.impact" 
            placeholder="Describe the impact..."
            :disabled="!formDetails.cost"
            @input="e => { formDetails.impact = e.target.value; validateQuestionnaire(); }"
          ></textarea>
        </div>
        
        <div class="question-group" :class="{ 'disabled': !formDetails.impact }">
          <label for="financial-impact-input">What is the financial impact for this mitigation?</label>
          <textarea 
            id="financial-impact-input" 
            :value="formDetails.financialImpact" 
            placeholder="Describe the financial impact..."
            :disabled="!formDetails.impact"
            @input="e => { formDetails.financialImpact = e.target.value; validateQuestionnaire(); }"
          ></textarea>
        </div>
        
        <div class="question-group" :class="{ 'disabled': !formDetails.financialImpact }">
          <label for="reputational-impact-input">What is the reputational impact for this mitigation?</label>
          <textarea 
            id="reputational-impact-input" 
            :value="formDetails.reputationalImpact" 
            placeholder="Describe the reputational impact..."
            :disabled="!formDetails.financialImpact"
            @input="e => { formDetails.reputationalImpact = e.target.value; validateQuestionnaire(); }"
          ></textarea>
        </div>
      </div>
      
      <!-- Add to the mitigation-questionnaire div, after the questionnaire fields -->
      <div v-if="questionnaireRejected" class="questionnaire-feedback">
        <h4><i class="fas fa-exclamation-circle"></i> Reviewer Feedback</h4>
        <p>{{ questionnaireRemarks }}</p>
      </div>
      
      <!-- Update the submission-area div to check for questionnaire completion -->
      <div class="submission-area" :class="{ 'ready': canSubmit }">
        <h3>Review Assignment</h3>
        
        <div class="reviewer-select">
          <label for="reviewer-select">Select a Reviewer:</label>
          <select 
            id="reviewer-select" 
            :value="selectedReviewer" 
            :disabled="!allStepsCompleted || !!selectedReviewer"
            @change="e => selectedReviewer = e.target.value"
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
</template>

<script>
import axios from 'axios';

export default {
  name: 'MitigationWorkflow',
  props: {
    riskId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      loading: true,
      mitigationSteps: [],
      currentRisk: null,
      selectedReviewer: '',
      users: [],
      formDetails: {
        cost: '',
        impact: '',
        financialImpact: '',
        reputationalImpact: ''
      },
      latestReview: null
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
    this.loadMitigationData();
    this.fetchRiskDetails();
  },
  methods: {
    goBack() {
      this.$router.push({ name: 'UserTasks' });
    },
    fetchRiskDetails() {
      // Fetch risk details based on riskId
      axios.get(`http://localhost:8000/api/risk-details/${this.riskId}/`)
        .then(response => {
          this.currentRisk = response.data;
        })
        .catch(error => {
          console.error('Error fetching risk details:', error);
        });
    },
    fetchUsers() {
      axios.get('http://localhost:8000/api/custom-users/')
        .then(response => {
          console.log('User data received:', response.data);
          this.users = response.data;
        })
        .catch(error => {
          console.error('Error fetching users:', error);
        });
    },
    loadMitigationData() {
      this.loading = true;
      
      // First, get the basic mitigation steps
      axios.get(`http://localhost:8000/api/risk-mitigations/${this.riskId}/`)
        .then(response => {
          console.log('Mitigations received:', response.data);
          this.mitigationSteps = this.parseMitigations(response.data);
          
          // Get the risk form details
          axios.get(`http://localhost:8000/api/risk-form-details/${this.riskId}/`)
            .then(formResponse => {
              console.log('Form details received:', formResponse.data);
              this.formDetails = formResponse.data;
              
              // Get the latest R version from risk_approval table to get approval status
              axios.get(`http://localhost:8000/api/latest-review/${this.riskId}/`)
                .then(reviewResponse => {
                  const reviewData = reviewResponse.data;
                  console.log('Latest review data:', reviewData);
                  
                  // Store the latest review
                  this.latestReview = reviewData;
                  
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
                  axios.get(`http://localhost:8000/api/get-assigned-reviewer/${this.riskId}/`)
                    .then(reviewerResponse => {
                      if (reviewerResponse.data && reviewerResponse.data.reviewer_id) {
                        this.selectedReviewer = reviewerResponse.data.reviewer_id;
                      }
                      this.loading = false;
                    })
                    .catch(error => {
                      console.error('Error fetching assigned reviewer:', error);
                      this.loading = false;
                    });
                })
                .catch(error => {
                  console.error('Error fetching latest review:', error);
                  this.loading = false;
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
              this.loading = false;
            });
        })
        .catch(error => {
          console.error('Error fetching mitigations:', error);
          this.mitigationSteps = [];
          this.loading = false;
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
    updateStepStatus(index, status) {
      console.log(`Updating step ${index + 1} status to ${status}`);
      
      // Update the step status locally
      this.mitigationSteps[index].status = status;
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
    completeStep(index) {
      // Only allow completing if previous steps are completed
      if (this.isStepLocked(index)) return;
      
      this.mitigationSteps[index].status = 'Completed';
    },
    resetStep(index) {
      this.mitigationSteps[index].status = 'In Progress';
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
      
      axios.post('http://localhost:8000/api/assign-reviewer/', {
        risk_id: this.riskId,
        reviewer_id: this.selectedReviewer,
        mitigations: mitigationData,
        risk_form_details: this.formDetails  // Add the form details here
      })
      .then(response => {
        console.log('Reviewer assigned:', response.data);
        // Update the risk mitigation status to indicate it's under review
        return axios.post('http://localhost:8000/api/update-mitigation-status/', {
          risk_id: this.riskId,
          status: 'Revision Required by Reviewer'
        });
      })
      .then(response => {
        console.log('Status updated to under review:', response.data);
        this.loading = false;
        // Show success message
        alert('Risk submitted for review successfully!');
        // Navigate back to tasks page
        this.$router.push({ name: 'UserTasks' });
      })
      .catch(error => {
        console.error('Error assigning reviewer:', error);
        this.loading = false;
        alert('Failed to submit for review. Please try again.');
      });
    }
  }
}
</script>

<style>
@import './MitigationWorkflow.css';

/* Additional styles to ensure no background containers */
.workflow-container, 
.simplified-workflow,
.step-box,
.mitigation-questionnaire,
.submission-area,
.timeline-step.active .step-box,
.timeline-step.completed .step-box,
.timeline-step.locked .step-box,
.step-info,
.status-tag,
.question-group textarea:disabled,
.reviewer-select select {
  background-color: transparent !important;
  box-shadow: none !important;
}
</style> 