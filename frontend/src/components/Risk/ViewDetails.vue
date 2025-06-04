<template>
  <div class="view-details-container">
    <!-- Header: Back button on top, title below -->
    <div class="view-details-header">
      <button class="back-btn" @click="goBack">
        <i class="fas fa-arrow-left"></i> Back
      </button>
    </div>
    <h2 class="view-details-title">Incident Details</h2>

    <div class="details-content-grid" v-if="incident">
      <!-- Horizontal Info Band -->
      <div class="general-info-grid">
        <div class="info-field">
          <div class="info-label">ID</div>
          <div class="info-value">#{{ incident?.IncidentId || 'N/A' }}</div>
        </div>
        <div class="info-field">
          <div class="info-label">Status</div>
          <div class="status-badge" :class="statusClass(incident?.Status)">{{ incident?.Status || 'N/A' }}</div>
        </div>
        <div class="info-field">
          <div class="info-label">Date</div>
          <div class="datetime-value">{{ formatDate(incident?.Date) }}</div>
        </div>
        <div class="info-field">
          <div class="info-label">Time</div>
          <div class="datetime-value">{{ incident?.Time || 'N/A' }}</div>
        </div>
        <div class="info-field">
          <div class="info-label">Title</div>
          <div class="info-value">{{ incident?.IncidentTitle || 'N/A' }}</div>
        </div>
        <div class="info-field">
          <div class="info-label">Origin</div>
          <div class="info-value">{{ incident?.Origin || 'N/A' }}</div>
        </div>
      </div>
      
      <!-- Content Panel Layout -->
      <div class="details-panel-layout">
        <!-- Left Column - Timeline Sections -->
        <div class="details-left-column">
          <div class="details-timeline">
            <!-- Description -->
            <div class="description-section">
              <div class="section-header">
                <i class="fas fa-align-left"></i> Description
              </div>
              <div class="description-text">{{ incident?.Description || 'No description available' }}</div>
            </div>
            
            <!-- Mitigation Section -->
            <div class="description-section" v-if="incident?.Mitigation">
              <div class="section-header">
                <i class="fas fa-shield-alt"></i> Mitigation
              </div>
              <div class="description-text">{{ incident.Mitigation }}</div>
            </div>
            
            <!-- Comments Section -->
            <div class="description-section" v-if="incident?.Comments">
              <div class="section-header">
                <i class="fas fa-comments"></i> Comments
              </div>
              <div class="description-text">{{ incident.Comments }}</div>
            </div>
          </div>
        </div>
        
        <!-- Right Column - Risk Info -->
        <div class="risk-info-section">
          <div class="risk-info-title">
            <i class="fas fa-exclamation-triangle"></i> Risk Information
          </div>
          
          <div class="risk-item">
            <div class="info-label">Category</div>
            <div class="info-value">{{ incident?.RiskCategory || 'N/A' }}</div>
          </div>
          
          <div class="risk-item">
            <div class="info-label">Priority</div>
            <div class="priority-indicator" :class="'priority-' + (incident?.RiskPriority || 'low').toLowerCase()">
              {{ incident?.RiskPriority || 'N/A' }}
            </div>
          </div>
          
          <div class="risk-item">
            <div class="info-label">Compliance ID</div>
            <div class="info-value">{{ incident?.ComplianceId || 'N/A' }}</div>
          </div>
          
          <div class="risk-item">
            <div class="info-label">Audit ID</div>
            <div class="info-value">{{ incident?.AuditId || 'N/A' }}</div>
          </div>
          
          <div class="risk-item" v-if="incident?.CreatedAt">
            <div class="info-label">Created At</div>
            <div class="info-value">{{ formatDateTime(incident.CreatedAt) }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Loading State -->
    <div class="loading-state" v-else>
      <div class="loading-spinner"></div>
      <p>Loading incident details...</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ViewDetails',
  props: {
    id: {
      type: [Number, String],
      required: false
    }
  },
  data() {
    return {
      incident: null,
      loading: true
    }
  },
  created() {
    // Get the incident ID from either props or route params
    const incidentId = this.id || this.$route.params.id;
    
    if (!incidentId) {
      console.error('No incident ID provided');
      return;
    }
    
    this.fetchIncidentDetails(incidentId);
  },
  methods: {
    goBack() {
      this.$router.push({ name: 'RiskNotifications' });
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return 'N/A';
      const date = new Date(dateTimeString);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    statusClass(status) {
      if (!status) return '';
      const statusLower = status.toLowerCase();
      if (statusLower === 'scheduled') return 'status-scheduled';
      if (statusLower === 'active') return 'status-active';
      if (statusLower === 'resolved') return 'status-resolved';
      if (statusLower === 'rejected') return 'status-rejected';
      return 'status-default';
    },
    async fetchIncidentDetails(incidentId) {
      this.loading = true;
      try {
        const response = await axios.get(`http://localhost:8000/api/incidents/${incidentId}/`);
        this.incident = response.data;
        console.log('Fetched incident:', this.incident);
      } catch (error) {
        console.error('Error fetching incident details:', error);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style src="./ViewDetails.css"></style> 