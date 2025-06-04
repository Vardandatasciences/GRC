<template>
  <div class="workflow-container">
    <h1>Risk Workflow Management</h1>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Loading risk data...</span>
    </div>
    
    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div v-else-if="risks.length === 0" class="no-data">
      <p>No risk instances found. Please create some risk instances first.</p>
    </div>
    
    <div v-else class="table-responsive">
      <table class="risk-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Risk Description</th>
            <th>Category</th>
            <th>Criticality</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Assigned To</th>
            <th>Review Count</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="risk in risks" :key="risk.RiskInstanceId" :class="getRowClass(risk.RiskStatus)">
            <td>{{ risk.RiskInstanceId }}</td>
            <td>{{ risk.RiskDescription || 'No description' }}</td>
            <td>{{ risk.Category }}</td>
            <td><span class="criticality-badge" :class="getCriticalityClass(risk.Criticality)">{{ risk.Criticality }}</span></td>
            <td><span class="priority-badge" :class="getPriorityClass(risk.RiskPriority)">{{ risk.RiskPriority }}</span></td>
            <td>{{ risk.RiskStatus }}</td>
            <td>
              <!-- If risk is assigned to a real user (not System Owner), just show the user name -->
              <div v-if="risk.RiskOwner && risk.RiskOwner !== 'System Owner' && risk.RiskOwner !== 'System User'">
                {{ risk.RiskOwner }}
              </div>
              <!-- If risk is unassigned or assigned to System Owner/System User, show assignment option -->
              <div v-else class="assign-section">
                <select v-model="selectedUsers[risk.RiskInstanceId]" class="user-dropdown">
                  <option value="">Select User</option>
                  <option v-for="user in users" :key="user.user_id" :value="user.user_id">
                    {{ user.user_name }}
                  </option>
                </select>
                <button @click="openMitigationModal(risk)" class="assign-btn" :disabled="!selectedUsers[risk.RiskInstanceId]">Assign</button>
              </div>
            </td>
            <td>{{ risk.ReviewerCount || 0 }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Mitigation Modal -->
    <div v-if="showMitigationModal" class="modal-overlay" @click.self="closeMitigationModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Risk Mitigation Workflow</h2>
          <button class="close-btn" @click="closeMitigationModal">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingMitigations" class="loading">
            <div class="spinner"></div>
            <span>Loading mitigation steps...</span>
          </div>
          <div v-else>
            <div class="risk-summary">
              <h3>{{ selectedRisk.RiskDescription || 'Risk #' + selectedRisk.RiskInstanceId }}</h3>
              <div class="risk-details">
                <p><strong>ID:</strong> {{ selectedRisk.RiskInstanceId }}</p>
                <p><strong>Category:</strong> {{ selectedRisk.Category }}</p>
                <p><strong>Criticality:</strong> {{ selectedRisk.Criticality }}</p>
              </div>
            </div>
            
            <div class="mitigation-workflow">
              <h3>Mitigation Steps</h3>
              
              <!-- Existing Mitigation Steps -->
              <div v-if="mitigationSteps.length" class="workflow-timeline">
                <div v-for="(step, index) in mitigationSteps" :key="index" class="workflow-step">
                  <div class="step-number">{{ index + 1 }}</div>
                  <div class="step-content">
                    <textarea 
                      v-model="step.description" 
                      class="mitigation-textarea"
                      placeholder="Enter mitigation step description"
                    ></textarea>
                    <div class="step-actions">
                      <button @click="removeMitigationStep(index)" class="remove-step-btn">
                        <i class="fas fa-trash"></i> Remove
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-else class="no-mitigations">
                <p>No mitigation steps defined for this risk. Add steps below.</p>
              </div>
              
              <!-- Add New Mitigation Step -->
              <div class="add-mitigation">
                <textarea 
                  v-model="newMitigationStep" 
                  class="mitigation-textarea"
                  placeholder="Enter a new mitigation step description"
                ></textarea>
                <button @click="addMitigationStep" class="add-step-btn" :disabled="!newMitigationStep.trim()">
                  <i class="fas fa-plus"></i> Add Mitigation Step
                </button>
              </div>
              
              <!-- Due Date Input -->
              <div class="due-date-section">
                <h4>Due Date for Mitigation Completion</h4>
                <input 
                  type="date" 
                  v-model="mitigationDueDate" 
                  class="due-date-input" 
                  :min="getTodayDate()"
                />
              </div>
              
              <!-- Risk Form Section -->
              <div class="risk-form-section">
                <h4>Risk Mitigation Questionnaire</h4>
                <p class="form-note">Please complete these details about the risk mitigation:</p>
                
                <div class="form-field">
                  <label for="cost-input">What is the cost for this mitigation?</label>
                  <textarea 
                    id="cost-input" 
                    v-model="riskFormDetails.cost" 
                    placeholder="Describe the cost..."
                    class="form-textarea"
                  ></textarea>
                </div>
                
                <div class="form-field">
                  <label for="impact-input">What is the impact for this mitigation?</label>
                  <textarea 
                    id="impact-input" 
                    v-model="riskFormDetails.impact" 
                    placeholder="Describe the impact..."
                    class="form-textarea"
                  ></textarea>
                </div>
                
                <div class="form-field">
                  <label for="financial-impact-input">What is the financial impact for this mitigation?</label>
                  <textarea 
                    id="financial-impact-input" 
                    v-model="riskFormDetails.financialImpact" 
                    placeholder="Describe the financial impact..."
                    class="form-textarea"
                  ></textarea>
                </div>
                
                <div class="form-field">
                  <label for="reputational-impact-input">What is the reputational impact for this mitigation?</label>
                  <textarea 
                    id="reputational-impact-input" 
                    v-model="riskFormDetails.reputationalImpact" 
                    placeholder="Describe the reputational impact..."
                    class="form-textarea"
                  ></textarea>
                </div>
              </div>
              
              <!-- Submit Section -->
              <div class="mitigation-actions">
                <button 
                  @click="assignRiskWithMitigations" 
                  class="submit-mitigations-btn"
                  :disabled="mitigationSteps.length === 0 || !mitigationDueDate || !isFormComplete()"
                >
                  <i class="fas fa-user-plus"></i> Assign with Mitigations
                </button>
                <div v-if="!isFormComplete()" class="form-warning">
                  <i class="fas fa-exclamation-circle"></i> Please complete all questionnaire fields
                </div>
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

export default {
  name: 'RiskWorkflow',
  data() {
    return {
      risks: [],
      users: [],
      selectedUsers: {},
      loading: true,
      error: null,
      // New properties for mitigation modal
      showMitigationModal: false,
      selectedRisk: {},
      mitigationSteps: [],
      newMitigationStep: '',
      loadingMitigations: false,
      mitigationDueDate: '',
      riskFormDetails: {
        cost: '',
        impact: '',
        financialImpact: '',
        reputationalImpact: ''
      }
    }
  },
  mounted() {
    this.fetchRisks();
    this.fetchUsers();
  },
  methods: {
    fetchRisks() {
      axios.get('http://localhost:8000/risk-instances/')
        .then(response => {
          console.log('Risk data received:', response.data);
          this.risks = response.data;
          this.loading = false;
        })
        .catch(error => {
          console.error('Error fetching risks:', error);
          this.error = `Failed to fetch risks: ${error.message}`;
          this.loading = false;
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
    openMitigationModal(risk) {
      const userId = this.selectedUsers[risk.RiskInstanceId];
      if (!userId) return;
      
      this.selectedRisk = risk;
      this.showMitigationModal = true;
      this.loadingMitigations = true;
      
      // Fetch existing mitigations for this risk
      axios.get(`http://localhost:8000/api/risk-mitigations/${risk.RiskInstanceId}/`)
        .then(response => {
          console.log('Existing mitigations:', response.data);
          this.mitigationSteps = this.parseMitigations(response.data);
          this.loadingMitigations = false;
        })
        .catch(error => {
          console.error('Error fetching mitigations:', error);
          // Initialize with empty array if no mitigations exist
          this.mitigationSteps = [];
          this.loadingMitigations = false;
        });
    },
    closeMitigationModal() {
      this.showMitigationModal = false;
      this.selectedRisk = {};
      this.mitigationSteps = [];
      this.newMitigationStep = '';
      this.mitigationDueDate = '';
      this.riskFormDetails = {
        cost: '',
        impact: '',
        financialImpact: '',
        reputationalImpact: ''
      };
    },
    parseMitigations(data) {
      // Convert different mitigation formats to our standard format
      if (!data || data.length === 0) {
        return [];
      }
      
      // If it's already an array of objects with descriptions
      if (Array.isArray(data) && data[0] && data[0].description) {
        return data.map(item => ({
          description: item.description || item.title || '',
          status: item.status || 'Not Started'
        }));
      }
      
      // If it's an array of strings or simple objects
      if (Array.isArray(data)) {
        return data.map((item, index) => ({
          description: typeof item === 'string' ? item : (item.description || item.title || `Step ${index + 1}`),
          status: item.status || 'Not Started'
        }));
      }
      
      // If it's an object with numbered keys (e.g., {"1": "Step 1", "2": "Step 2"})
      if (typeof data === 'object' && !Array.isArray(data)) {
        const steps = [];
        Object.keys(data).forEach(key => {
          const value = data[key];
          steps.push({
            description: typeof value === 'string' ? value : (value.description || value.title || `Step ${key}`),
            status: value.status || 'Not Started'
          });
        });
        return steps;
      }
      
      // Fallback: if it's a string, create a single step
      if (typeof data === 'string') {
        return [{
          description: data,
          status: 'Not Started'
        }];
      }
      
      return [];
    },
    addMitigationStep() {
      if (!this.newMitigationStep.trim()) return;
      
      this.mitigationSteps.push({
        description: this.newMitigationStep,
        status: 'Not Started'
      });
      
      this.newMitigationStep = '';
    },
    removeMitigationStep(index) {
      this.mitigationSteps.splice(index, 1);
    },
    assignRiskWithMitigations() {
      const riskId = this.selectedRisk.RiskInstanceId;
      const userId = this.selectedUsers[riskId];
      
      if (!userId || this.mitigationSteps.length === 0 || !this.mitigationDueDate || !this.isFormComplete()) return;
      
      this.loading = true;
      
      // Convert mitigations to the expected JSON format
      // Format: {"1": "Description 1", "2": "Description 2", ...}
      const mitigationsJson = {};
      this.mitigationSteps.forEach((step, index) => {
        mitigationsJson[index + 1] = step.description;
      });
      
      console.log('Sending mitigation data:', mitigationsJson);
      console.log('Sending form details:', this.riskFormDetails);
      
      // Assign the risk to the user with mitigations and form details
      axios.post('http://localhost:8000/api/risk-assign/', {
        risk_id: riskId,
        user_id: userId,
        mitigations: mitigationsJson,
        due_date: this.mitigationDueDate,
        risk_form_details: this.riskFormDetails
      })
      .then(response => {
        console.log('Assignment response:', response.data);
        
        // Update the local risk data to show assignment
        const index = this.risks.findIndex(r => r.RiskInstanceId === riskId);
        if (index !== -1) {
          const assignedUser = this.users.find(u => u.user_id === userId);
          this.risks[index].RiskOwner = assignedUser.user_name;
          this.risks[index].RiskStatus = 'Assigned';
          this.risks[index].UserId = userId;
          this.risks[index].RiskMitigation = mitigationsJson;
          this.risks[index].MitigationDueDate = this.mitigationDueDate;
          this.risks[index].MitigationStatus = 'Yet to Start';
          this.risks[index].RiskFormDetails = this.riskFormDetails;
        }
        
        this.loading = false;
        this.closeMitigationModal();
        
        // Show success message
        alert('Risk assigned successfully with mitigation steps and details!');
      })
      .catch(error => {
        console.error('Error assigning risk:', error);
        this.loading = false;
        alert('Failed to assign risk. Please try again.');
      });
    },
    getCriticalityClass(criticality) {
      if (!criticality) return '';
      const level = criticality.toLowerCase();
      if (level.includes('high')) return 'high';
      if (level.includes('medium')) return 'medium';
      if (level.includes('low')) return 'low';
      if (level.includes('critical')) return 'critical';
      return '';
    },
    getPriorityClass(priority) {
      if (!priority) return '';
      const level = priority.toLowerCase();
      if (level.includes('high')) return 'high';
      if (level.includes('medium')) return 'medium';
      if (level.includes('low')) return 'low';
      return '';
    },
    getStatusClass(status) {
      if (!status) return '';
      const statusLower = status.toLowerCase();
      if (statusLower.includes('approved')) return 'approved';
      if (statusLower.includes('review')) return 'review';
      if (statusLower.includes('progress')) return 'progress';
      if (statusLower.includes('assigned')) return 'assigned';
      if (statusLower.includes('revision')) return 'revision';
      if (statusLower.includes('open')) return 'open';
      return '';
    },
    getRowClass(status) {
      if (!status) return '';
      const statusLower = status.toLowerCase();
      if (statusLower.includes('approved')) return 'row-approved';
      if (statusLower.includes('review')) return 'row-review';
      return '';
    },
    getTodayDate() {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    isFormComplete() {
      return (
        this.riskFormDetails.cost.trim() !== '' &&
        this.riskFormDetails.impact.trim() !== '' &&
        this.riskFormDetails.financialImpact.trim() !== '' &&
        this.riskFormDetails.reputationalImpact.trim() !== ''
      );
    }
  }
}
</script>

<style>
@import './Workflow.css';
</style> 