<template>
  <div class="create-risk-instance-container">
    <div class="create-risk-instance-card">
      <div class="create-risk-instance-header">
        <h2>Create Risk Instance</h2>
      </div>
      
      <form @submit.prevent="submitInstance" class="create-risk-instance-form">
        <div class="form-group">
          <label for="criticality"><i class="fas fa-exclamation-triangle"></i> Criticality*</label>
          <select id="criticality" class="priority-select" v-model="newInstance.Criticality" required>
            <option value="">Select Criticality</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="category"><i class="fas fa-tag"></i> Category*</label>
          <select id="category" class="category-select" v-model="newInstance.Category" required>
            <option value="">Select Category</option>
            <option value="IT Security">IT Security</option>
            <option value="IT Security, Compliance">IT Security, Compliance</option>
            <option value="Operational">Operational</option>
            <option value="Compliance">Compliance</option>
            <option value="Financial">Financial</option>
            <option value="Strategic">Strategic</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="appetite"><i class="fas fa-balance-scale"></i> Appetite</label>
          <input type="number" id="appetite" v-model="newInstance.Appetite" min="1" max="10" step="1" placeholder="Select Appetite (1-10)">
        </div>
        
        <div class="form-group field-full">
          <label for="riskDescription"><i class="fas fa-align-left"></i> Risk Description*</label>
          <textarea 
            id="riskDescription" 
            v-model="newInstance.RiskDescription" 
            required
            placeholder="Describe the risk..."
            rows="3"
          ></textarea>
        </div>
        
        <div class="form-group field-full">
          <label for="possibleDamage"><i class="fas fa-exclamation-circle"></i> Possible Damage</label>
          <textarea 
            id="possibleDamage" 
            v-model="newInstance.PossibleDamage" 
            placeholder="Describe possible damage..."
            rows="2"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label for="riskLikelihood"><i class="fas fa-chart-line"></i> Risk Likelihood*</label>
          <input type="number" step="0.1" id="riskLikelihood" v-model="newInstance.RiskLikelihood" placeholder="Enter value (e.g. 8.5)" required>
        </div>
        
        <div class="form-group">
          <label for="riskImpact"><i class="fas fa-bolt"></i> Risk Impact*</label>
          <input type="number" step="0.1" id="riskImpact" v-model="newInstance.RiskImpact" placeholder="Enter value (e.g. 7.0)" required>
        </div>
        
        <div class="form-group">
          <label for="riskExposureRating"><i class="fas fa-thermometer-half"></i> Risk Exposure Rating</label>
          <input type="number" step="0.1" id="riskExposureRating" v-model="newInstance.RiskExposureRating" placeholder="Enter value (e.g. 7.5)">
        </div>
        
        <div class="form-group">
          <label for="riskPriority"><i class="fas fa-flag"></i> Risk Priority*</label>
          <select id="riskPriority" class="priority-select" v-model="newInstance.RiskPriority" required>
            <option value="">Select Priority</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="riskResponseType"><i class="fas fa-shield-alt"></i> Response Type</label>
          <select id="riskResponseType" v-model="newInstance.RiskResponseType">
            <option value="">Select Response Type</option>
            <option value="Avoidance">Avoidance</option>
            <option value="Mitigation">Mitigation</option>
            <option value="Transfer">Transfer</option>
            <option value="Acceptance">Acceptance</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="riskOwner"><i class="fas fa-user"></i> Risk Owner*</label>
          <input type="text" id="riskOwner" v-model="newInstance.RiskOwner" required placeholder="Enter risk owner name">
        </div>
        
        <div class="form-group field-full">
          <label for="riskResponseDescription"><i class="fas fa-reply"></i> Response Description</label>
          <textarea 
            id="riskResponseDescription" 
            v-model="newInstance.RiskResponseDescription" 
            placeholder="Describe the response strategy..."
            rows="2"
          ></textarea>
        </div>
        
        <div class="form-group field-full">
          <label for="riskMitigation"><i class="fas fa-shield-virus"></i> Risk Mitigation</label>
          <textarea 
            id="riskMitigation" 
            v-model="newInstance.RiskMitigation" 
            placeholder="Describe mitigation actions..."
            rows="2"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label for="riskStatus"><i class="fas fa-info-circle"></i> Risk Status</label>
          <select id="riskStatus" v-model="newInstance.RiskStatus">
            <option value="Not Assigned">Not Assigned</option>
            <option value="Assigned">Assigned</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="userId"><i class="fas fa-id-badge"></i> User ID</label>
          <input type="number" id="userId" v-model="newInstance.UserId">
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="resetForm">Clear</button>
          <button type="submit" class="btn-submit">Create</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import './CreateRiskInstance.css'

export default {
  name: 'CreateRiskInstance',
  props: {
    riskId: {
      type: [String, Number],
      default: null
    },
    incidentId: {
      type: [String, Number],
      default: null
    }
  },
  data() {
    return {
      newInstance: {
        Criticality: '',
        PossibleDamage: '',
        Category: '',
        Appetite: '',
        RiskDescription: '',
        RiskLikelihood: '',
        RiskImpact: '',
        RiskExposureRating: '',
        RiskPriority: '',
        RiskResponseType: '',
        RiskResponseDescription: '',
        RiskMitigation: '',
        RiskOwner: '',
        RiskStatus: '',
        UserId: 1,
        Date: new Date().toISOString().split('T')[0],
        RiskId: null,
        IncidentId: null
      },
      isDebugging: false,
      testResults: []
    }
  },
  mounted() {
    // Prefer props over route query
    this.newInstance.RiskId = this.riskId !== undefined ? this.riskId : (this.$route.query.riskId || null);
    this.newInstance.IncidentId = this.incidentId !== undefined ? this.incidentId : (this.$route.query.incidentId || null);
  },
  methods: {
    testBackendConnection() {
      this.isDebugging = true;
      this.testResults = [];
      
      const endpoints = [
        'http://127.0.0.1:8000/api/risk-instances/', // Confirmed working endpoint (highest priority)
        'http://localhost:8000/api/risk-instances/',
        'http://localhost:8080/api/risk-instances/',
        'http://localhost:8080/risk-instances/',
        'http://127.0.0.1:8000/risk-instances/',
        'http://localhost:8000/risk-instances/'
      ];
      
      this.testResults.push('Testing API endpoints in order of priority...');
      this.testResults.push(`Primary endpoint: ${endpoints[0]} (confirmed working in browser)`);
      
      const testEndpoint = (index) => {
        if (index >= endpoints.length) {
          // Testing complete
          this.testResults.push('All tests completed.');
          return;
        }
        
        const endpoint = endpoints[index];
        this.testResults.push(`Testing: ${endpoint}`);
        
        fetch(endpoint, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        })
        .then(response => {
          if (!response.ok) {
            return response.text().then(() => {
              this.testResults.push(`❌ ${endpoint} - Status: ${response.status}`);
              // Continue testing the next endpoint
              testEndpoint(index + 1);
            });
          }
          return response.json().then((data) => {
            this.testResults.push(`✅ ${endpoint} - Connected successfully`);
            this.testResults.push(`Found ${data.length || 0} risk instances in the database`);
            testEndpoint(index + 1);
          });
        })
        .catch(error => {
          this.testResults.push(`❌ ${endpoint} - Error: ${error.message}`);
          testEndpoint(index + 1);
        });
      };
      
      // Start testing endpoints
      testEndpoint(0);
    },
    submitInstance() {
      // Debug logs for troubleshooting
      console.log('newInstance before submit:', this.newInstance);
      // Always set both IDs before submitting
      const formData = {
        ...this.newInstance,
        RiskId: this.newInstance.RiskId || null,
        IncidentId: this.newInstance.IncidentId || null,
        RiskLikelihood: parseFloat(this.newInstance.RiskLikelihood) || 0,
        RiskImpact: parseFloat(this.newInstance.RiskImpact) || 0,
        RiskExposureRating: this.newInstance.RiskExposureRating ? parseFloat(this.newInstance.RiskExposureRating) : null,
        UserId: parseInt(this.newInstance.UserId) || null
      }
      // Debug log
      console.log('Submitting with IncidentId:', formData.IncidentId, 'RiskId:', formData.RiskId);
      if (!formData.IncidentId) {
        alert('IncidentId is missing! Please try again.');
        return;
      }
      
      console.log('Submitting data:', formData);

      // Use the confirmed working endpoint
      const API_ENDPOINT = 'http://127.0.0.1:8000/api/risk-instances/';
      
      // Show debugging info
      this.isDebugging = true;
      this.testResults = [`Submitting to confirmed API endpoint: ${API_ENDPOINT}`];
      
      fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })
      .then(response => {
        if (!response.ok) {
          return response.text().then((errorText) => {
            this.testResults.push(`❌ API Error: ${response.status} ${response.statusText}`);
            this.testResults.push(`Response: ${errorText}`);
            console.error(`API Error: ${response.status}`, errorText);
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
          });
        }
        return response.json();
      })
      .then(data => {
        console.log('Success response:', data);
        this.testResults.push('✅ Success! Risk instance created successfully');
        
        // Show success message
        const successMessage = document.createElement('div');
        successMessage.className = 'form-success-message';
        successMessage.innerText = 'Risk instance created successfully!';
        document.body.appendChild(successMessage);
        
        // Remove success message after animation completes
        setTimeout(() => {
          if (document.body.contains(successMessage)) {
            document.body.removeChild(successMessage);
          }
        }, 3000);
        
        this.resetForm();
      })
      .catch(error => {
        this.testResults.push(`❌ Error: ${error.message}`);
        alert(`Error creating risk instance: ${error.message}`);
      });
    },
    resetForm() {
      this.newInstance = {
        Criticality: '',
        PossibleDamage: '',
        Category: '',
        Appetite: '',
        RiskDescription: '',
        RiskLikelihood: '',
        RiskImpact: '',
        RiskExposureRating: '',
        RiskPriority: '',
        RiskResponseType: '',
        RiskResponseDescription: '',
        RiskMitigation: '',
        RiskOwner: '',
        RiskStatus: '',
        UserId: 1,
        Date: new Date().toISOString().split('T')[0]
      }
    }
  }
}
</script>

