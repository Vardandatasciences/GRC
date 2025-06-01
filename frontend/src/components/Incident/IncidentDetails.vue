<template>
    <div class="incident-details-page">
      <div class="incident-details-header">
        <router-link to="/incident/incident" class="back-link">
          <span class="back-arrow">←</span>
          <span class="back-text">Back to Incidents</span>
        </router-link>
      </div>
  
      <div v-if="loading" class="loading-state">
        Loading incident details...
      </div>
  
      <div v-else-if="error" class="error-state">
        {{ error }}
      </div>
  
      <div class="incident-details-content" v-else-if="incident">
        <div class="incident-details-grid">
          <!-- Title Section with Incident ID -->
          <div class="detail-item full-width title-container">
            <div class="title-section">
              <span class="detail-label">Title</span>
              <span class="detail-value title-value">{{ incident.IncidentTitle }}</span>
            </div>
            <div class="incident-id">
              Incident #{{ incident?.IncidentId }}
            </div>
          </div>
  
          <!-- Info Row -->
          <div class="detail-item">
            <span class="detail-label">Priority</span>
            <span :class="['priority-badge', getPriorityClass(incident.RiskPriority)]">
              {{ incident.RiskPriority }}
            </span>
          </div>
  
          <div class="detail-item">
            <span class="detail-label">Category</span>
            <span class="category-badge" :class="getRiskCategoryClass(incident.RiskCategory)">
              {{ incident.RiskCategory }}
            </span>
          </div>
  
          <div class="detail-item">
            <span class="detail-label">Date</span>
            <span class="detail-value">{{ formatDate(incident.Date) }}</span>
          </div>
  
          <div class="detail-item">
            <span class="detail-label">Origin</span>
            <span class="origin-badge" :class="getOriginClass(incident.Origin)">
              {{ incident.Origin }}
            </span>
          </div>
  
          <!-- Description Section -->
          <div class="detail-item full-width">
            <span class="detail-label">Description</span>
            <div class="detail-value description-value">{{ incident.Description }}</div>
          </div>
  
          <!-- Comments and Mitigation Row -->
          <div class="detail-item comments-section">
            <span class="detail-label">Comments</span>
            <div class="detail-value">{{ incident.Comments || 'No comments' }}</div>
          </div>
  
          <div class="detail-item mitigation-section">
            <span class="detail-label">Mitigation</span>
            <div class="detail-value">{{ incident.Mitigation || 'No mitigation plan' }}</div>
          </div>
        </div>
  
        <div class="incident-details-footer">
          <div v-if="incident.Status === 'Scheduled'">
            <span class="status-badge scheduled">Mitigated to Risk</span>
          </div>
          <div v-else-if="incident.Status === 'Rejected'">
            <span class="status-badge rejected">Rejected</span>
          </div>
          <div v-else>
            <button @click="openSolveModal" class="solve-btn">ESCALATE TO RISK</button>
            <button @click="openRejectModal" class="no-btn">REJECT INCIDENT</button>
          </div>
        </div>
      </div>
  
      <!-- Modal for Solve/No Actions -->
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-container" @click.stop>
          <button class="modal-close-btn" @click="closeModal">✕</button>
          <div class="modal-content">
            <div v-if="modalAction === 'solve'" class="solve-container">
              <div class="solve-icon">🔄</div>
              <h3 class="modal-title solve">Forwarded to Risk</h3>
              <p class="modal-subtitle">You will be directed to the Risk module</p>
              <div class="modal-footer">
                <button @click="confirmSolve" class="modal-btn confirm-btn">Confirm Forward</button>
                <button @click="closeModal" class="modal-btn cancel-btn">Cancel</button>
              </div>
            </div>
            
            <div v-else-if="modalAction === 'reject'" class="rejected-container">
              <div class="rejected-icon">✕</div>
              <h3 class="modal-title rejected">Rejected</h3>
              <div class="modal-footer">
                <button @click="confirmReject" class="modal-btn reject-btn">Confirm Reject</button>
                <button @click="closeModal" class="modal-btn cancel-btn">Cancel</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import './IncidentDetails.css';
  
  export default {
    name: 'IncidentDetails',
    data() {
      return {
        incident: null,
        loading: true,
        error: null,
        showModal: false,
        modalAction: '' // 'solve' or 'reject'
      }
    },
    async created() {
      await this.fetchIncidentDetails();
    },
    methods: {
      async fetchIncidentDetails() {
        try {
          this.loading = true;
          this.error = null;
          const incidentId = this.$route.params.id;
          console.log('Fetching incident:', incidentId);
          
          // Get all incidents and filter for the one we want
          const response = await axios.get('http://localhost:8000/incidents/');
          const allIncidents = response.data;
          
          // Find the specific incident
          this.incident = allIncidents.find(inc => inc.IncidentId.toString() === incidentId.toString());
          
          if (!this.incident) {
            throw new Error('Incident not found');
          }
          
          console.log('Fetched incident:', this.incident);
        } catch (error) {
          console.error('Failed to fetch incident details:', error);
          this.error = 'Failed to load incident details. Please try again.';
        } finally {
          this.loading = false;
        }
      },
      openSolveModal() {
        this.modalAction = 'solve';
        this.showModal = true;
      },
      openRejectModal() {
        this.modalAction = 'reject';
        this.showModal = true;
      },
      closeModal() {
        this.showModal = false;
      },
      confirmSolve() {
        // Update incident status to "Scheduled"
        axios.put(`http://localhost:8000/incidents/${this.incident.IncidentId}/status/`, {
          status: 'Scheduled'
        })
        .then(response => {
          console.log('Incident escalated to risk:', response.data);
          
          // Update local incident status
          this.incident.Status = 'Scheduled';
          
          // Auto close and redirect after 2 seconds
          setTimeout(() => {
            this.closeModal();
            // Redirect to Risk module
            // this.$router.push('/risk');
          }, 2000);
        })
        .catch(error => {
          console.error('Error updating incident status:', error);
        });
      },
      confirmReject() {
        // Update incident status to "Rejected"
        axios.put(`http://localhost:8000/incidents/${this.incident.IncidentId}/status/`, {
          status: 'Rejected'
        })
        .then(response => {
          console.log('Incident rejected:', response.data);
          
          // Update local incident status
          this.incident.Status = 'Rejected';
          
          // Auto close the modal after 2 seconds
          setTimeout(() => {
            this.closeModal();
          }, 2000);
        })
        .catch(error => {
          console.error('Error updating incident status:', error);
        });
      },
      getPriorityClass(priority) {
        switch(priority?.toLowerCase()) {
          case 'high': return 'priority-high';
          case 'medium': return 'priority-medium';
          case 'low': return 'priority-low';
          default: return '';
        }
      },
      getRiskCategoryClass(category) {
        if (!category) return '';
        const categoryLower = category.toLowerCase();
        if (categoryLower.includes('security')) return 'category-security';
        if (categoryLower.includes('compliance')) return 'category-compliance';
        if (categoryLower.includes('operational')) return 'category-operational';
        if (categoryLower.includes('financial')) return 'category-financial';
        if (categoryLower.includes('strategic')) return 'category-strategic';
        return 'category-other';
      },
      getOriginClass(origin) {
        const originType = origin?.toLowerCase() || '';
        if (originType.includes('manual')) return 'origin-manual';
        if (originType.includes('audit')) return 'origin-audit';
        if (originType.includes('siem')) return 'origin-siem';
        return 'origin-other';
      },
      formatDate(dateString) {
        if (!dateString) return '';
        const [year, month, day] = dateString.split('-');
        return `${month}/${day}/${year}`;
      }
    }
  }
  </script> 