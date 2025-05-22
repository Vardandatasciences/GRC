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
          </tr>
        </thead>
        <tbody>
          <tr v-for="risk in risks" :key="risk.RiskInstanceId" :class="getRowClass(risk.RiskStatus)">
            <td>{{ risk.RiskInstanceId }}</td>
            <td>{{ risk.RiskDescription || 'No description' }}</td>
            <td>{{ risk.Category }}</td>
            <td><span class="criticality-badge" :class="getCriticalityClass(risk.Criticality)">{{ risk.Criticality }}</span></td>
            <td><span class="priority-badge" :class="getPriorityClass(risk.RiskPriority)">{{ risk.RiskPriority }}</span></td>
            <td><span class="status-badge" :class="getStatusClass(risk.RiskStatus)">{{ risk.RiskStatus }}</span></td>
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
              
              <!-- Submit Section -->
              <div class="mitigation-actions">
                <button 
                  @click="assignRiskWithMitigations" 
                  class="submit-mitigations-btn"
                  :disabled="mitigationSteps.length === 0"
                >
                  <i class="fas fa-user-plus"></i> Assign with Mitigations
                </button>
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
      loadingMitigations: false
    }
  },
  mounted() {
    this.fetchRisks();
    this.fetchUsers();
  },
  methods: {
    fetchRisks() {
      axios.get('http://localhost:8000/api/risk-instances/')
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
      
      if (!userId || this.mitigationSteps.length === 0) return;
      
      this.loading = true;
      
      // Convert mitigations to the expected JSON format
      // Format: {"1": "Description 1", "2": "Description 2", ...}
      const mitigationsJson = {};
      this.mitigationSteps.forEach((step, index) => {
        mitigationsJson[index + 1] = step.description;
      });
      
      // Convert to JSON string for storage in database
      const mitigationsJsonString = JSON.stringify(mitigationsJson);
      
      console.log('Sending mitigation data:', mitigationsJsonString);
      
      // Assign the risk to the user with mitigations
      axios.post('http://localhost:8000/api/risk-assign/', {
        risk_id: riskId,
        user_id: userId,
        mitigations: mitigationsJsonString
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
          this.risks[index].RiskMitigation = mitigationsJsonString;
        }
        
        this.loading = false;
        this.closeMitigationModal();
        
        // Show success message
        alert('Risk assigned successfully with mitigation steps!');
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
    }
  }
}
</script>

<style scoped>
.workflow-container {
  padding: 20px;
  background-color: white;
  min-height: 100vh;
  margin-left: 196px; /* Match the sidebar width */
}

h1 {
  margin-bottom: 25px;
  color: #2c3e50;
  font-weight: 600;
  padding-bottom: 10px;
  border-bottom: 1px solid #eaecef;
}

.table-responsive {
  overflow-x: auto;
  background: white;
}

.risk-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  table-layout: fixed;
}

.risk-table th,
.risk-table td {
  padding: 15px 10px;
  text-align: left;
  border-bottom: 1px solid #eaecef;
  vertical-align: middle;
}

.risk-table th {
  color: #606266;
  font-weight: normal;
  background-color: #ffffff;
  border-bottom: 1px solid #dcdfe6;
}

.risk-table tr:hover {
  background-color: #f5f7fa;
}

/* Column widths */
.risk-table th:nth-child(1), 
.risk-table td:nth-child(1) {
  width: 5%;
}

.risk-table th:nth-child(2), 
.risk-table td:nth-child(2) {
  width: 25%;
}

.risk-table th:nth-child(3), 
.risk-table td:nth-child(3) {
  width: 15%;
}

.risk-table th:nth-child(4), 
.risk-table td:nth-child(4),
.risk-table th:nth-child(5), 
.risk-table td:nth-child(5),
.risk-table th:nth-child(6), 
.risk-table td:nth-child(6) {
  width: 10%;
  text-align: center;
}

.risk-table th:nth-child(7), 
.risk-table td:nth-child(7) {
  width: 25%;
}

.criticality-badge,
.priority-badge,
.status-badge {
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
  text-align: center;
  min-width: 80px;
}

.criticality-badge.high,
.priority-badge.high {
  background-color: #fff1f0;
  color: #ff4d4f;
}

.criticality-badge.medium,
.priority-badge.medium {
  background-color: #fff7e6;
  color: #fa8c16;
}

.criticality-badge.low,
.priority-badge.low {
  background-color: #f6ffed;
  color: #52c41a;
}

.criticality-badge.critical {
  background-color: #ff4d4f;
  color: white;
}

.status-badge.approved {
  background-color: #f6ffed;
  color: #52c41a;
}

.status-badge.review {
  background-color: #fff7e6;
  color: #fa8c16;
}

.status-badge.progress {
  background-color: #e6f7ff;
  color: #1890ff;
}

.status-badge.open,
.status-badge.assigned {
  background-color: #f9f0ff;
  color: #722ed1;
}

.status-badge.revision {
  background-color: #fff1f0;
  color: #ff4d4f;
}

.assign-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-dropdown {
  padding: 4px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 2px;
  font-size: 12px;
  color: #606266;
  background-color: #fff;
  flex-grow: 1;
  max-width: 200px;
}

.assign-btn {
  padding: 6px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: normal;
  font-size: 12px;
  white-space: nowrap;
  text-align: center;
  background-color: #1890ff;
  color: white;
}

.assign-btn:hover {
  background-color: #40a9ff;
}

.assign-btn:disabled {
  background-color: #bae7ff;
  cursor: not-allowed;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background-color: #ffffff;
  gap: 15px;
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1890ff;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

.error-message {
  padding: 15px;
  background-color: #fff1f0;
  color: #ff4d4f;
  margin-bottom: 20px;
}

.no-data {
  padding: 30px;
  text-align: center;
  color: #8c8c8c;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .workflow-container {
    margin-left: 0;
    padding: 10px;
  }
  
  .assign-section {
    flex-direction: column;
  }
  
  .risk-table th,
  .risk-table td {
    padding: 8px 5px;
    font-size: 12px;
  }
  
  .criticality-badge,
  .priority-badge,
  .status-badge {
    padding: 2px 6px;
    font-size: 10px;
    min-width: 60px;
  }
  
  .modal-content {
    width: 95%;
  }
}

/* New styles for mitigation modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(3px);
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 85%;
  max-width: 850px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease-out;
  border: none;
}

@keyframes slideIn {
  from { transform: translateY(30px); opacity: 0.8; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eaecef;
  background: linear-gradient(to right, #f8f9fa, #ffffff);
}

.modal-header h2 {
  margin: 0;
  font-size: 22px;
  color: #2c3e50;
  font-weight: 600;
  position: relative;
  padding-left: 30px;
}

.modal-header h2::before {
  content: '\f0ae'; /* tasks icon */
  font-family: "Font Awesome 5 Free";
  font-weight: 900;
  position: absolute;
  left: 0;
  color: #1890ff;
}

.close-btn {
  background: rgba(0, 0, 0, 0.05);
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: #606266;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: rgba(0, 0, 0, 0.1);
  color: #2c3e50;
  transform: rotate(90deg);
}

.modal-body {
  padding: 24px;
}

.risk-summary {
  margin-bottom: 25px;
  padding: 16px;
  background-color: #f9f9fa;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
}

.risk-summary h3 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.risk-details p {
  margin: 5px 0;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.risk-details p strong {
  min-width: 100px;
  display: inline-block;
  color: #606266;
}

.mitigation-workflow {
  padding: 10px 0;
}

.mitigation-workflow h3 {
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.mitigation-workflow h3::before {
  content: '\f0ad'; /* wrench icon */
  font-family: "Font Awesome 5 Free";
  font-weight: 900;
  margin-right: 10px;
  color: #1890ff;
}

.workflow-timeline {
  position: relative;
  padding-left: 30px;
  margin-left: 10px;
  margin-bottom: 30px;
}

.workflow-timeline::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 20px;
  width: 3px;
  background: linear-gradient(to bottom, 
    #52c41a 0%, 
    #1890ff 50%, 
    #eaecef 100%);
  border-radius: 3px;
}

.workflow-step {
  position: relative;
  padding: 10px 0 30px 60px;
}

.workflow-step:last-child {
  padding-bottom: 10px;
}

.step-number {
  position: absolute;
  left: 0;
  top: 15px;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  font-size: 20px;
  z-index: 2;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
  background: linear-gradient(135deg, #1890ff, #40a9ff);
  border: 2px solid white;
}

.step-content {
  background-color: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #1890ff;
}

.mitigation-textarea {
  width: 100%;
  min-height: 80px;
  padding: 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
  transition: all 0.3s;
}

.mitigation-textarea:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.step-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.remove-step-btn {
  background-color: #ff4d4f;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s;
}

.remove-step-btn:hover {
  background-color: #ff7875;
}

.no-mitigations {
  padding: 20px;
  text-align: center;
  background-color: #f9f9fa;
  border-radius: 8px;
  color: #8c8c8c;
  margin-bottom: 20px;
}

.add-mitigation {
  margin-top: 20px;
  padding: 20px;
  background-color: #f9f9fa;
  border-radius: 8px;
  border: 1px dashed #d9d9d9;
}

.add-step-btn {
  margin-top: 12px;
  background-color: #52c41a;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s;
}

.add-step-btn:hover {
  background-color: #73d13d;
}

.add-step-btn:disabled {
  background-color: #d9f7be;
  cursor: not-allowed;
}

.mitigation-actions {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.submit-mitigations-btn {
  background: linear-gradient(to right, #1890ff, #096dd9);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 0 rgba(0, 0, 0, 0.045);
  transition: all 0.3s;
}

.submit-mitigations-btn:hover {
  background: linear-gradient(to right, #40a9ff, #1890ff);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(24, 144, 255, 0.25);
}

.submit-mitigations-btn:disabled {
  background: #bae7ff;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.assign-btn {
  background-color: #1890ff;
  color: white;
  box-shadow: 0 2px 0 rgba(0, 0, 0, 0.045);
}

.assign-btn:hover:not(:disabled) {
  background-color: #40a9ff;
  transform: translateY(-1px);
}
</style> 