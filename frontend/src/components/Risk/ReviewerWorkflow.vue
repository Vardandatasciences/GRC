<template>
  <div class="reviewer-workflow-container">
    <h1>Review Risk Mitigations</h1>
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Loading review data...</span>
    </div>
    <div v-else>
      <div class="mitigation-review-list">
        <div v-for="(mitigation, id) in mitigationReviewData" :key="id" class="mitigation-review-item">
          <div class="mitigation-description">
            <h4>Mitigation #{{ id }}</h4>
            <p>{{ mitigation.description }}</p>
            <div v-if="mitigation.comments" class="user-comments">
              <h5>User Comments:</h5>
              <p class="comment-text">{{ mitigation.comments }}</p>
            </div>
            <div v-if="mitigation.fileData" class="uploaded-evidence">
              <h5>Uploaded Evidence:</h5>
              <a :href="mitigation.fileData" download :filename="mitigation.fileName" class="evidence-link">
                <i class="fas fa-file-download"></i> {{ mitigation.fileName }}
              </a>
            </div>
            <div v-if="mitigation.approved === true" class="approval-status approved">
              <i class="fas fa-check-circle"></i> Approved
            </div>
          </div>
          <div class="approval-controls">
            <div v-if="mitigation.approved !== true && mitigation.approved !== false" class="approval-buttons">
              <button @click="approveMitigation(id, true)" class="approve-btn">
                <i class="fas fa-check"></i> Approve
              </button>
              <button @click="approveMitigation(id, false)" class="reject-btn">
                <i class="fas fa-times"></i> Reject
              </button>
            </div>
            <div v-if="mitigation.approved === false" class="remarks-field">
              <label for="remarks">Remarks (required for rejection):</label>
              <textarea id="remarks" v-model="mitigation.remarks" class="remarks-input" placeholder="Provide feedback for the rejected mitigation..."></textarea>
              <button @click="updateRemarks(id)" class="save-remarks-btn">
                <i class="fas fa-save"></i> Save Remarks
              </button>
              <button @click="approveMitigation(id, true)" class="change-decision-btn">
                <i class="fas fa-exchange-alt"></i> Change to Approve
              </button>
            </div>
            <div v-if="mitigation.approved === true" class="approved-actions">
              <button @click="approveMitigation(id, false)" class="change-decision-btn">
                <i class="fas fa-exchange-alt"></i> Change to Reject
              </button>
            </div>
          </div>
        </div>
      </div>
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
              <textarea id="questionnaire-remarks" v-model="formDetails.remarks" class="remarks-input" placeholder="Provide feedback on the questionnaire..."></textarea>
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
        <button class="submit-review-btn" :disabled="!canSubmitReview || reviewCompleted" @click="submitReview(true)">
          <i class="fas fa-check-double"></i> Approve Risk
        </button>
        <button class="reject-review-btn" :disabled="!canSubmitReview || reviewCompleted" @click="submitReview(false)">
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
</template>

<script>
import axios from 'axios';
import './ReviewerWorkflow.css';

export default {
  name: 'ReviewerWorkflow',
  props: {
    riskId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      loading: true,
      reviewTask: null,
      mitigationReviewData: {},
      formDetails: {},
      users: [],
      reviewCompleted: false,
      reviewApproved: false
    }
  },
  computed: {
    canSubmitReview() {
      const allMitigationsReviewed = Object.values(this.mitigationReviewData).every(m => 
        m.approved === true || (m.approved === false && m.remarks && m.remarks.trim() !== '')
      );
      const questionnaireReviewed = 
        this.formDetails.approved === true || 
        (this.formDetails.approved === false && this.formDetails.remarks && this.formDetails.remarks.trim() !== '');
      return allMitigationsReviewed && questionnaireReviewed;
    }
  },
  mounted() {
    this.fetchUsers();
    this.loadReviewData();
  },
  methods: {
    fetchUsers() {
      axios.get('http://localhost:8000/api/custom-users/')
        .then(response => {
          this.users = response.data;
        });
    },
    getUserName(userId) {
      const user = this.users.find(u => u.user_id == userId);
      return user ? user.user_name : 'Unknown';
    },
    loadReviewData() {
      this.loading = true;
      axios.get(`http://localhost:8000/api/reviewer-task-details/${this.riskId}/`)
        .then(response => {
          const data = response.data;
          this.reviewTask = data.task;
          this.mitigationReviewData = data.mitigations;
          this.formDetails = data.formDetails;
          this.reviewCompleted = data.reviewCompleted;
          this.reviewApproved = data.reviewApproved;
          this.loading = false;
        })
        .catch(() => { this.loading = false; });
    },
    approveMitigation(id, approved) {
      this.mitigationReviewData[id].approved = approved;
      if (approved) this.mitigationReviewData[id].remarks = '';
    },
    updateRemarks(id) {
      if (!this.mitigationReviewData[id].remarks.trim()) {
        alert('Please provide remarks for rejection');
        return;
      }
      alert('Remarks saved');
    },
    approveQuestionnaire(approved) {
      this.formDetails.approved = approved;
      if (!approved && !this.formDetails.remarks) this.formDetails.remarks = '';
      if (approved) this.formDetails.remarks = '';
    },
    saveQuestionnaireRemarks() {
      if (this.formDetails.approved === false && !this.formDetails.remarks.trim()) {
        alert('Please provide feedback for the questionnaire');
        return;
      }
      alert('Questionnaire feedback saved');
    },
    submitReview(approved) {
      if (!this.canSubmitReview) {
        alert('Please complete the review of all mitigations and the questionnaire');
        return;
      }
      this.loading = true;
      const reviewData = {
        approval_id: this.reviewTask.RiskInstanceId,
        risk_id: this.reviewTask.RiskInstanceId,
        approved: approved,
        mitigations: this.mitigationReviewData,
        risk_form_details: {
          ...this.formDetails,
          approved: this.formDetails.approved,
          remarks: this.formDetails.remarks || ''
        }
      };
      axios.post('http://localhost:8000/api/complete-review/', reviewData)
        .then(() => {
          this.loading = false;
          this.reviewCompleted = true;
          alert(`Risk ${approved ? 'approved' : 'rejected'} successfully!`);
        })
        .catch(() => {
          this.loading = false;
          alert('Failed to submit review. Please try again.');
        });
    }
  }
}
</script>

<style src="./ReviewerWorkflow.css"></style> 