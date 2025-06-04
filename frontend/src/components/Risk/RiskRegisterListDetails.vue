<template>
  <div class="risk-details-container">
    <button @click="navigateToRiskList" class="back-btn">
      Back to Risk Instances
    </button>
    
    <div v-if="loading" class="risk-details-loading">
      <i class="fas fa-spinner fa-spin"></i> Loading risk details...
    </div>
    
    <div v-else-if="error" class="risk-details-error">
      <i class="fas fa-exclamation-circle"></i> {{ error }}
    </div>
    
    <div v-else-if="risk" class="risk-details-content">
      <div class="title-section">
        <div class="title">{{ risk.RiskDescription || 'Risk Title' }}</div>
        <div class="risk-id">Risk #{{ risk.RiskId }}</div>
      </div>
      
      <div class="risk-metadata">
        <div class="metadata-item">
          <div class="metadata-label">PRIORITY</div>
          <div class="metadata-value">
            <div :class="getCriticalityClass(risk.Criticality)">{{ risk.Criticality }}</div>
          </div>
        </div>
        
        <div class="metadata-item">
          <div class="metadata-label">CATEGORY</div>
          <div class="metadata-value">
            <div class="category-badge">{{ risk.Category }}</div>
          </div>
        </div>
        
        <div class="metadata-item">
          <div class="metadata-label">DATE</div>
          <div class="metadata-value">{{ formatDate() }}</div>
        </div>
        
        <div class="metadata-item">
          <div class="metadata-label">ORIGIN</div>
          <div class="metadata-value">
            <div class="origin-badge">MANUAL</div>
          </div>
        </div>
      </div>
      
      <div class="description-section">
        <div class="section-label">DESCRIPTION</div>
        <div class="section-content">{{ risk.RiskDescription }}</div>
      </div>
      
      <div class="two-column-section">
        <div class="comments-section">
          <div class="section-label">COMMENTS</div>
          <div class="section-content">{{ risk.Comments || 'No comments available' }}</div>
        </div>
        
        <div class="mitigation-section">
          <div class="section-label">MITIGATION</div>
          <div class="section-content">{{ risk.RiskMitigation || 'No mitigation strategy specified' }}</div>
        </div>
      </div>
    </div>
    
    <div v-else class="risk-details-not-found">
      <i class="fas fa-exclamation-triangle"></i>
      <p>Risk not found. The requested risk may have been deleted or does not exist.</p>
      <button @click="navigateToRiskList" class="back-btn">
        Return to Risk Register
      </button>
    </div>
  </div>
</template>

<script>
import './RiskRegisterListDetails.css'
import axios from 'axios'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'RiskRegisterListDetails',
  data() {
    return {
      risk: null,
      loading: true,
      error: null
    }
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const navigateToRiskList = () => {
      router.push('/risk/riskregister-list')
    }
    
    return {
      navigateToRiskList,
      route
    }
  },
  mounted() {
    this.fetchRiskDetails()
  },
  methods: {
    fetchRiskDetails() {
      const riskId = this.route.params.id
      
      this.loading = true
      this.error = null
      
      axios.get(`http://localhost:8000/api/risks/${riskId}`)
        .then(response => {
          this.risk = response.data
          this.loading = false
        })
        .catch(error => {
          console.error('Error fetching risk details:', error)
          this.error = 'Failed to load risk details. Please try again later.'
          this.loading = false
        })
    },
    getCriticalityClass(criticality) {
      if (!criticality) return ''
      criticality = criticality.toLowerCase()
      if (criticality === 'critical') return 'priority-critical'
      if (criticality === 'high') return 'priority-high'
      if (criticality === 'medium') return 'priority-medium'
      if (criticality === 'low') return 'priority-low'
      return ''
    },
    formatDate() {
      // Return a formatted date similar to the image (05/15/2025)
      const date = new Date()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const year = date.getFullYear()
      return `${month}/${day}/${year}`
    }
  }
}
</script> 