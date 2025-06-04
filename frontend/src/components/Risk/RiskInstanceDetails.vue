<template>
  <div class="risk-instance-details-container">
    <div class="risk-instance-details-content">
      <div class="back-link">
        <router-link to="/risk/riskinstances" class="back-button">
          <i class="fas fa-arrow-left"></i> Back to Risk Instances
        </router-link>
        <span v-if="instance" class="risk-id-badge">ID: {{ instance.RiskId }}</span>
      </div>

      <div v-if="instance">
        <!-- Description as title at the top -->
        <div class="description-title">
          {{ instance.RiskDescription }}
        </div>

        <!-- Risk summary section in a more compact layout -->
        <div class="risk-summary">
          <div class="risk-summary-item">
            <div class="risk-summary-label">Priority</div>
            <div class="risk-summary-value" :class="'priority-' + instance.Criticality.toLowerCase()">
              {{ instance.Criticality }}
            </div>
          </div>
          <div class="risk-summary-item">
            <div class="risk-summary-label">Category</div>
            <div class="risk-summary-value">
              <span class="category-badge">{{ instance.Category }}</span>
            </div>
          </div>
          <div class="risk-summary-item">
            <div class="risk-summary-label">Date</div>
            <div class="risk-summary-value date-value">{{ formatDate(instance.Date) }}</div>
          </div>
          <div class="risk-summary-item">
            <div class="risk-summary-label">Origin</div>
            <div class="risk-summary-value origin-value">MANUAL</div>
          </div>
        </div>

        <!-- Comments and Mitigation in a row -->
        <div class="compact-sections-row">
          <div class="info-section">
            <h3 class="section-title">Comments</h3>
            <div class="info-content">
              No comments available
            </div>
          </div>

          <div class="info-section">
            <h3 class="section-title">Mitigation</h3>
            <div class="info-content">
              {{ instance.RiskMitigation || 'No mitigation plan provided' }}
            </div>
          </div>
        </div>

        <!-- Risk Assessment and Response in a compact layout -->
        <div class="compact-details">
          <!-- Risk Assessment details -->
          <div class="details-section">
            <h3 class="section-title">Risk Assessment</h3>
            <div class="details-grid">
              <div class="detail-item">
                <label>Risk ID</label>
                <div class="value">{{ instance.RiskId }}</div>
              </div>
              <div class="detail-item">
                <label>Likelihood</label>
                <div class="value rating-value">{{ instance.RiskLikelihood }}</div>
              </div>
              <div class="detail-item">
                <label>Impact</label>
                <div class="value rating-value">{{ instance.RiskImpact }}</div>
              </div>
              <div class="detail-item">
                <label>Exposure Rating</label>
                <div class="value rating-value" :class="getExposureClass(instance.RiskExposureRating)">
                  {{ instance.RiskExposureRating }}
                </div>
              </div>
              <div class="detail-item">
                <label>Risk Owner</label>
                <div class="value">{{ instance.RiskOwner }}</div>
              </div>
              <div class="detail-item">
                <label>Appetite</label>
                <div class="value">{{ instance.Appetite || 'Not specified' }}</div>
              </div>
              <div class="detail-item">
                <label>Status</label>
                <div class="value">
                  <span class="status-badge" :class="getStatusClass(instance.RiskStatus)">
                    {{ instance.RiskStatus }}
                  </span>
                </div>
              </div>
              <div class="detail-item">
                <label>User ID</label>
                <div class="value">{{ instance.UserId }}</div>
              </div>
            </div>
          </div>

          <!-- Response Section -->
          <div class="details-section response-section">
            <h3 class="section-title">Response</h3>
            <div class="details-grid">
              <div class="detail-item">
                <label>Response Type</label>
                <div class="value">{{ instance.RiskResponseType || 'Not specified' }}</div>
              </div>
              <div class="detail-item">
                <label>Response Description</label>
                <div class="value">{{ instance.RiskResponseDescription || 'No description provided' }}</div>
              </div>
              <div class="detail-item">
                <label>Possible Damage</label>
                <div class="value">{{ instance.PossibleDamage || 'Not specified' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="loading-state">
        Loading risk instance details...
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import './RiskInstanceDetails.css'

export default {
  name: 'RiskInstanceDetails',
  data() {
    return {
      instance: null
    }
  },
  mounted() {
    this.fetchInstanceDetails()
  },
  methods: {
    fetchInstanceDetails() {
      const id = this.$route.params.id
      console.log('Fetching risk instance with ID:', id)
      
      axios.get(`http://localhost:8000/api/risk-instances/${id}`)
        .then(response => {
          console.log('Fetched instance:', response.data)
          this.instance = response.data
        })
        .catch(error => {
          console.error('Error fetching risk instance details:', error)
          if (error.response) {
            console.error('Response status:', error.response.status)
            console.error('Response data:', error.response.data)
          }
          
          this.tryAlternativeEndpoint(id)
        })
    },
    tryAlternativeEndpoint(id) {
      console.log('Trying alternative endpoint...')
      axios.get(`http://localhost:8000/risk-instances/${id}`)
        .then(response => {
          console.log('Fetched instance from alternative endpoint:', response.data)
          this.instance = response.data
        })
        .catch(error => {
          console.error('Error with alternative endpoint:', error)
        })
    },
    formatDate(dateString) {
      if (!dateString) return 'Not set'
      const date = new Date(dateString)
      return date.toLocaleDateString()
    },
    getStatusClass(status) {
      if (!status) return ''
      return `status-${status.toLowerCase().replace(/\s+/g, '-')}`
    },
    getExposureClass(value) {
      const numValue = parseFloat(value)
      if (numValue >= 8) return 'exposure-critical'
      if (numValue >= 6) return 'exposure-high'
      if (numValue >= 4) return 'exposure-medium'
      return 'exposure-low'
    }
  }
}
</script>

