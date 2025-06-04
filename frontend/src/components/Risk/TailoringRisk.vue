<template>
  <div class="tailoring-risk-container">
    <h1>Tailoring Existing Risk</h1>
    
    <form @submit.prevent="submitRisk" class="risk-form">
      <div class="form-group">
        <label for="riskId"><i class="fas fa-hashtag"></i> Risk ID:</label>
        <select id="riskId" v-model="selectedRiskId" class="form-control" @change="loadRiskDetails">
          <option value="">Select a Risk ID</option>
          <option v-for="id in riskIds" :key="id" :value="id">{{ id }}</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="compliance"><i class="fas fa-clipboard-check"></i> Compliance ID:</label>
        <input type="number" id="compliance" v-model="risk.ComplianceId" class="form-control">
      </div>
      
      <div class="form-group">
        <label for="criticality"><i class="fas fa-exclamation-triangle"></i> Criticality:</label>
        <select id="criticality" v-model="risk.Criticality" class="form-control">
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
          <option value="Critical">Critical</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="category"><i class="fas fa-tag"></i> Category:</label>
        <input type="text" id="category" v-model="risk.Category" class="form-control">
      </div>
      
      <div class="form-group">
        <label for="likelihood"><i class="fas fa-chart-line"></i> Risk Likelihood:</label>
        <input type="number" id="likelihood" v-model.number="risk.RiskLikelihood" class="form-control" min="1" max="10" step="1">
      </div>
      
      <div class="form-group">
        <label for="impact"><i class="fas fa-bomb"></i> Risk Impact:</label>
        <input type="number" id="impact" v-model.number="risk.RiskImpact" class="form-control" min="1" max="10" step="1">
      </div>
      
      <div class="form-group">
        <label for="exposure"><i class="fas fa-chart-bar"></i> Risk Exposure Rating:</label>
        <input type="number" id="exposure" v-model.number="risk.RiskExposureRating" class="form-control" step="0.1">
      </div>
      
      <div class="form-group">
        <label for="priority"><i class="fas fa-flag"></i> Risk Priority:</label>
        <select id="priority" v-model="risk.RiskPriority" class="form-control">
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
          <option value="Critical">Critical</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="damage"><i class="fas fa-skull-crossbones"></i> Possible Damage:</label>
        <textarea id="damage" v-model="risk.PossibleDamage" class="form-control"></textarea>
      </div>
      
      <div class="form-group">
        <label for="description"><i class="fas fa-align-left"></i> Risk Description:</label>
        <textarea id="description" v-model="risk.RiskDescription" class="form-control"></textarea>
      </div>
      
      <div class="form-group">
        <label for="mitigation"><i class="fas fa-shield-alt"></i> Risk Mitigation:</label>
        <textarea id="mitigation" v-model="risk.RiskMitigation" class="form-control"></textarea>
      </div>
      
      <div class="button-group">
        <button type="button" class="clear-btn" @click="clearForm">Clear</button>
        <button type="submit" class="submit-btn">Create</button>
      </div>
    </form>
    
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import './TailoringRisk.css';

export default {
  name: 'TailoringRisk',
  setup() {
    const selectedRiskId = ref('');
    const risk = ref({
      RiskId: '',
      ComplianceId: null,
      Criticality: '',
      PossibleDamage: '',
      Category: '',
      RiskDescription: '',
      RiskLikelihood: null,
      RiskImpact: null,
      RiskExposureRating: null,
      RiskPriority: '',
      RiskMitigation: ''
    });
    
    const riskIds = ref([]);
    const message = ref('');
    const messageType = ref('');
    
    // Fetch all risk IDs on component mount
    onMounted(async () => {
      try {
        // Make API request to fetch all risks
        console.log('Fetching all risks from API...');
        const response = await axios.get('http://127.0.0.1:8000/api/risks/');
        console.log('API response:', response.data);
        
        // Extract all risk IDs from the response
        if (Array.isArray(response.data)) {
          // Get all risk IDs from the database
          riskIds.value = response.data.map(risk => risk.RiskId);
          console.log('Extracted risk IDs:', riskIds.value);
        } else {
          console.error('Unexpected response format:', response.data);
          message.value = 'Error: Unexpected response format from server';
          messageType.value = 'error';
        }
      } catch (error) {
        console.error('Error fetching risk IDs:', error);
        message.value = 'Error loading risk IDs: ' + (error.response?.data?.detail || error.message);
        messageType.value = 'error';
      }
    });
    
    // Parse numeric values from API response
    const parseNumericValue = (value) => {
      if (value === null || value === undefined) return null;
      
      // If it's already a number, return it
      if (typeof value === 'number') return value;
      
      // Try to parse string to number
      const parsed = parseFloat(value);
      return isNaN(parsed) ? null : parsed;
    };
    
    // Load risk details when a risk ID is selected
    const loadRiskDetails = async () => {
      if (!selectedRiskId.value) {
        // Reset form if no risk is selected
        clearForm();
        return;
      }
      
      try {
        console.log(`Loading details for risk ID: ${selectedRiskId.value}`);
        const response = await axios.get(`http://127.0.0.1:8000/api/risks/${selectedRiskId.value}/`);
        console.log('Risk details response:', response.data);
        
        const riskData = response.data;
        
        // Update form fields with the selected risk data, ensuring numeric fields are parsed correctly
        risk.value = {
          RiskId: '', // We set this empty as we want to create a new risk on submit
          ComplianceId: parseNumericValue(riskData.ComplianceId),
          Criticality: riskData.Criticality || '',
          PossibleDamage: riskData.PossibleDamage || '',
          Category: riskData.Category || '',
          RiskDescription: riskData.RiskDescription || '',
          RiskLikelihood: parseNumericValue(riskData.RiskLikelihood),
          RiskImpact: parseNumericValue(riskData.RiskImpact),
          RiskExposureRating: parseNumericValue(riskData.RiskExposureRating),
          RiskPriority: riskData.RiskPriority || '',
          RiskMitigation: riskData.RiskMitigation || ''
        };
      } catch (error) {
        console.error('Error loading risk details:', error);
        message.value = 'Error loading risk details: ' + (error.response?.data?.detail || error.message);
        messageType.value = 'error';
      }
    };
    
    const clearForm = () => {
      risk.value = {
        RiskId: '',
        ComplianceId: null,
        Criticality: '',
        PossibleDamage: '',
        Category: '',
        RiskDescription: '',
        RiskLikelihood: null,
        RiskImpact: null,
        RiskExposureRating: null,
        RiskPriority: '',
        RiskMitigation: ''
      };
      selectedRiskId.value = '';
      message.value = '';
    };
    
    const submitRisk = async () => {
      try {
        console.log('Submitting risk:', risk.value);
        
        // Create a copy of risk data for submission, ensuring numeric fields are converted properly
        const riskData = {
          ...risk.value,
          RiskLikelihood: parseNumericValue(risk.value.RiskLikelihood),
          RiskImpact: parseNumericValue(risk.value.RiskImpact),
          RiskExposureRating: parseNumericValue(risk.value.RiskExposureRating)
        };
        
        // Always create a new risk, never update an existing one
        console.log('Creating new risk based on selected template');
        const response = await axios.post('http://127.0.0.1:8000/api/risks/', riskData);
        console.log('Create response:', response.data);
        
        const newRiskId = response.data.RiskId;
        message.value = `Risk successfully added with new ID: ${newRiskId}!`;
        messageType.value = 'success';
        
        // Reset form
        clearForm();
        
        // Refresh risk IDs after submission
        const refreshResponse = await axios.get('http://127.0.0.1:8000/api/risks/');
        if (Array.isArray(refreshResponse.data)) {
          riskIds.value = refreshResponse.data.map(risk => risk.RiskId);
        }
      } catch (error) {
        console.error('Error submitting risk:', error);
        message.value = 'Error saving risk: ' + (error.response?.data?.detail || error.message);
        messageType.value = 'error';
      }
    };
    
    return {
      selectedRiskId,
      risk,
      riskIds,
      submitRisk,
      loadRiskDetails,
      clearForm,
      message,
      messageType
    };
  }
}
</script> 