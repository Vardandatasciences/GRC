<template>
  <div class="risk-register-container create-risk">
    <div class="risk-register-header-row">
      <h2 class="risk-register-title"><i class="fas fa-plus risk-register-icon"></i> Create New Risk</h2>
    </div>
    
    <!-- Add Risk Form -->
    <div class="risk-register-add-form">
      <form @submit.prevent="submitRisk" class="risk-register-form-grid">
        <!-- Compliance ID -->
        <div class="risk-register-form-group">
          <label>
            <span><i class="fas fa-hashtag"></i> Compliance ID</span>
          </label>
          <input type="number" v-model="newRisk.ComplianceId" required />
        </div>
        
        <!-- Criticality -->
        <div class="risk-register-form-group">
          <label>
            <span><i class="fas fa-exclamation-triangle"></i> Criticality</span>
          </label>
          <select v-model="newRisk.Criticality" required>
            <option value="">Select Criticality</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
        
        <!-- Category -->
        <div class="risk-register-form-group">
          <label>
            <span><i class="fas fa-tags"></i> Category</span>
          </label>
          <select v-model="newRisk.Category" required>
            <option value="">Select Category</option>
            <option value="IT Security">IT Security</option>
            <option value="Operational">Operational</option>
            <option value="Compliance">Compliance</option>
            <option value="Financial">Financial</option>
            <option value="Strategic">Strategic</option>
          </select>
        </div>
        
        <!-- Risk Priority -->
        <div class="risk-register-form-group">
          <label>
            <span><i class="fas fa-level-up-alt"></i> Risk Priority</span>
          </label>
          <select v-model="newRisk.RiskPriority" required>
            <option value="">Select Priority</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
        
        <!-- Risk Likelihood -->
        <div class="risk-register-form-group">
          <label>
            <span><i class="fas fa-chart-line"></i> Risk Likelihood</span>
          </label>
          <input type="number" step="0.1" v-model="newRisk.RiskLikelihood" placeholder="Enter value (e.g. 8.5)" required />
        </div>
        
        <!-- Risk Impact -->
        <div class="risk-register-form-group">
          <label>
            <span><i class="fas fa-chart-bar"></i> Risk Impact</span>
          </label>
          <input type="number" step="0.1" v-model="newRisk.RiskImpact" placeholder="Enter value (e.g. 7.0)" required />
        </div>
        
        <!-- Risk Exposure Rating -->
        <div class="risk-register-form-group">
          <label>
            <span><i class="fas fa-tachometer-alt"></i> Risk Exposure Rating</span>
          </label>
          <input type="number" step="0.1" v-model="newRisk.RiskExposureRating" placeholder="Enter value (e.g. 7.5)" />
        </div>
        
        <!-- Risk Description -->
        <div class="risk-register-form-group wide">
          <label>
            <span><i class="fas fa-align-left"></i> Risk Description</span>
          </label>
          <textarea v-model="newRisk.RiskDescription" required></textarea>
        </div>
        
        <!-- Possible Damage -->
        <div class="risk-register-form-group wide">
          <label>
            <span><i class="fas fa-bomb"></i> Possible Damage</span>
          </label>
          <textarea v-model="newRisk.PossibleDamage"></textarea>
        </div>
        
        <!-- Risk Mitigation -->
        <div class="risk-register-form-group wide">
          <label>
            <span><i class="fas fa-shield-alt"></i> Risk Mitigation</span>
          </label>
          <textarea v-model="newRisk.RiskMitigation"></textarea>
        </div>
        
        <!-- Form Actions -->
        <div class="risk-register-form-actions">
          <button type="button" @click="resetForm" class="risk-register-cancel-btn">
            <i class="fas fa-times"></i> Cancel
          </button>
          <button type="submit" class="risk-register-submit-btn">
            <i class="fas fa-save"></i> Create Risk
          </button>
        </div>
      </form>
    </div>
    
    <!-- Success Message -->
    <div v-if="showSuccessMessage" class="form-success-message">
      <i class="fas fa-check-circle"></i> Risk added successfully!
    </div>
  </div>
</template>

<script>
import './CreateRisk.css'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
  name: 'CreateRisk',
  data() {
    return {
      newRisk: {
        ComplianceId: null,
        Criticality: '',
        PossibleDamage: '',
        Category: '',
        RiskDescription: '',
        RiskLikelihood: '',
        RiskImpact: '',
        RiskExposureRating: '',
        RiskPriority: '',
        RiskMitigation: ''
      },
      showSuccessMessage: false
    }
  },
  setup() {
    const router = useRouter()
    return { router }
  },
  methods: {
    resetForm() {
      this.newRisk = {
        ComplianceId: null,
        Criticality: '',
        PossibleDamage: '',
        Category: '',
        RiskDescription: '',
        RiskLikelihood: '',
        RiskImpact: '',
        RiskExposureRating: '',
        RiskPriority: '',
        RiskMitigation: ''
      }
    },
    submitRisk() {
      // Convert numeric string values to actual numbers
      const formData = {
        ...this.newRisk,
        ComplianceId: parseInt(this.newRisk.ComplianceId) || null,
        RiskLikelihood: parseFloat(this.newRisk.RiskLikelihood) || 0,
        RiskImpact: parseFloat(this.newRisk.RiskImpact) || 0,
        RiskExposureRating: this.newRisk.RiskExposureRating ? 
          parseFloat(this.newRisk.RiskExposureRating) : null
      }
      
      axios.post('http://localhost:8000/api/risks/', formData)
        .then(() => {
          // Reset the form
          this.resetForm()
          
          // Show success message
          this.showSuccessMessage = true
          setTimeout(() => {
            this.showSuccessMessage = false
          }, 3000)
          
          // Navigate to risk register list
          this.router.push('/risk/riskregister-list')
        })
        .catch(error => {
          console.error('Error adding risk:', error.response?.data || error.message)
          alert('Error adding risk. Please check your data and try again.')
        })
    }
  }
}
</script>