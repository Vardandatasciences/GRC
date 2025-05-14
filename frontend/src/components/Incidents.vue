<template>
  <div class="incidents-container">
    <div class="incidents-header">
      <h1>Incidents</h1>
      <button @click="goToCreateIncident" class="create-btn">Create New Incident</button>
    </div>

    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>

    <div v-if="uncheckedFindings.filter(f => !assignedFindings.map(a => a.date).includes(f.date)).length" class="notification">
      <div v-for="finding in uncheckedFindings.filter(f => !assignedFindings.map(a => a.date).includes(f.date))" :key="finding.date" class="finding-alert">
        <div class="finding-content">
          <strong>Audit Finding</strong><br>
          <span><b>Comment:</b> {{ finding.comment }}</span><br>
          <span><b>ComplianceId:</b> {{ finding.ComplianceId }}</span><br>
          <span><b>UserId:</b> {{ finding.UserId }}</span><br>
          <span><b>Date:</b> {{ formatDateTime(finding.date) }}</span><br>
          
          <!-- Show message and buttons if not yet decided -->
          <template v-if="!showDecisionButtons[finding.date]">
            <span v-if="finding.is_risk">
              <b>This has a risk. Do you want to continue with the workflow?</b>
            </span>
            <span v-else>
              <b>This task is non-compliant. Do you want to start workflow or not?</b>
            </span>
            <div style="margin-top: 0.5rem;">
              <button class="continue-btn" @click="handleContinue(finding)">Continue</button>
              <button class="notnow-btn" @click="rejectFinding(finding.date)">Not Now</button>
            </div>
          </template>

          <!-- Show assign dropdown if user clicked Continue -->
          <template v-else>
            <div class="assign-dropdown">
              <label>Assignee:
                <select v-model="selectedAssignee[finding.date]">
                  <option v-for="user in users" :key="user.UserId" :value="user.UserId">
                    {{ user.UserName }}
                  </option>
                </select>
              </label>
              <label>Reviewer:
                <select v-model="selectedReviewer[finding.date]">
                  <option v-for="user in users" :key="user.UserId" :value="user.UserId">
                    {{ user.UserName }}
                  </option>
                </select>
              </label>
              <button @click="assignUser(finding.date)">Done</button>
              <button class="notnow-btn" @click="showDecisionButtons[finding.date] = false">Back</button>
            </div>
          </template>
        </div>
        <div class="finding-actions">
          
          
          
        </div>
      </div>
    </div>

    <div v-if="incidents.length > 0" class="incident-notifications-row">
      <div v-for="incident in incidents" :key="incident.IncidentId" style="display: flex; flex-direction: column; align-items: center;">
        <IncidentNotification
          v-if="!incidentAssigned[incident.IncidentId]"
          :incident="incident"
          :showAssignDropdown="showIncidentAssignDropdown[incident.IncidentId]"
          :users="users"
          @solve="showAssignDropdownForIncident(incident.IncidentId)"
          @reject="handleReject(incident)"
          @assign="assignIncidentUser"
        />
        <div
          v-else
          class="incident-notification assigned-notification"
          style="background: #e9f7fe; border: 2px solid #007bff; color: #007bff; max-width: 400px; margin: 2rem auto; border-radius: 12px; padding: 2rem; text-align: left;"
        >
          <h2>Assigned Incident</h2>
          <p><strong>Incident ID:</strong> {{ incident.IncidentId }}</p>
          <p><strong>Title:</strong> {{ incident.incidenttitle }}</p>
          <p><strong>Description:</strong> {{ incident.description }}</p>
          <span class="assigned-badge" style="background: #007bff; color: #fff; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.875rem; font-weight: 600;">Assigned</span>
        </div>
      </div>
    </div>

    <div v-else class="no-incidents">
      <p>No incidents found. Click "Create New Incident" to add one.</p>
    </div>

    <div class="incidents-list" v-if="assignedFindings.length > 0">
      <div v-for="finding in assignedFindings" :key="finding.date" class="incident-card assigned-card">
        <div class="incident-header">
          <h3>Assigned Finding</h3>
          <span class="assigned-badge">Assigned</span>
        </div>
        <p class="description">{{ finding.comment }}</p>
        <div class="incident-details">
          <span class="category">Assignee: {{ finding.assignee }}</span>
          <span class="category">Reviewer: {{ finding.reviewer }}</span>
          <span class="date">Date: {{ formatDateTime(finding.date) }}</span>
        </div>
      </div>
    </div>

    <!-- Risk Workflow Modal -->
    <div v-if="showRiskModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Risk workflow starts now</h3>
        <p>You are about to start the risk workflow for this finding.</p>
        <button class="continue-btn" @click="confirmRiskWorkflow">OK</button>
        <button class="notnow-btn" @click="cancelRiskWorkflow">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import IncidentNotification from './IncidentNotification.vue';

export default {
  name: 'IncidentsList',
  components: { IncidentNotification },
  data() {
    return {
      incidents: [],
      uncheckedFindings: [],
      users: [],
      showAssignDropdown: {},
      selectedAssignee: {},
      selectedReviewer: {},
      successMessage: '',
      assignedFindings: [],
      showIncidentAssignDropdown: {},
      selectedIncidentAssignee: {},
      selectedIncidentReviewer: {},
      incidentAssigned: {},
      showIncidentNotification: false,
      newIncident: null,
      showDecisionButtons: {},
      showRiskModal: false,
      currentRiskFinding: null,
    }
  },
  methods: {
    goToCreateIncident() {
      this.$router.push('/incidents/create');
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString();
    },
    formatDateTime(dateString) {
      return new Date(dateString).toLocaleString();
    },
    async fetchIncidents() {
      try {
        const response = await axios.get('http://localhost:8000/incidents/');
        this.incidents = response.data;
        if (this.incidents.length > 0) {
          this.triggerIncidentNotification(this.incidents[0]);
        }
      } catch (error) {
        console.error('Error fetching incidents:', error);
      }
    },
    async fetchUncheckedFindings() {
      try {
        const response = await axios.get('http://localhost:8000/audit-findings/unchecked/');
        this.uncheckedFindings = response.data;
      } catch (error) {
        console.error('Error fetching audit findings:', error);
      }
    },
    async acceptFinding(date) {
      this.uncheckedFindings = this.uncheckedFindings.filter(f => f.date !== date);
    },
    async rejectFinding(date) {
      this.uncheckedFindings = this.uncheckedFindings.filter(f => f.date !== date);
    },
    async fetchUsers() {
      try {
        const response = await axios.get('http://localhost:8000/users/');
        this.users = response.data;
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    },
    showAssign(findingDate) {
      this.showAssignDropdown[findingDate] = true;
    },
    async assignUser(findingDate) {
      const finding = this.uncheckedFindings.find(f => f.date === findingDate);
      const assigneeId = this.selectedAssignee[findingDate];
      const reviewerId = this.selectedReviewer[findingDate];

      if (!assigneeId || !reviewerId) {
        alert('Please select both assignee and reviewer.');
        return;
      }

      try {
        await axios.post('http://localhost:8000/workflow/create/', {
          finding_id: finding.date,
          assignee_id: assigneeId,
          reviewer_id: reviewerId
        });
        await axios.post('http://localhost:8000/audit-findings/update-status/', {
          date: finding.date,
          check_status: '1'
        });
        this.successMessage = 'Workflow saved and finding assigned!';
        this.assignedFindings.push({
          ...finding,
          assignee: this.users.find(u => u.UserId === assigneeId)?.UserName,
          reviewer: this.users.find(u => u.UserId === reviewerId)?.UserName
        });
        this.uncheckedFindings = this.uncheckedFindings.filter(f => f.date !== findingDate);
        this.fetchAssignedFindings();
        setTimeout(() => { this.successMessage = ''; }, 3000);
      } catch (error) {
        alert('Failed to save workflow.');
      }

      this.showAssignDropdown[findingDate] = false;
      this.selectedAssignee[findingDate] = null;
      this.selectedReviewer[findingDate] = null;
    },
    async fetchAssignedFindings() {
      try {
        const response = await axios.get('http://localhost:8000/workflow/assigned/');
        this.assignedFindings = response.data.filter(item => item.type === 'finding');
        response.data
          .filter(item => item.type === 'incident')
          .forEach(item => {
            this.incidentAssigned[item.IncidentId] = true;
          });
      } catch (error) {
        console.error('Error fetching assigned findings:', error);
      }
    },
    showIncidentAssign(incidentId) {
      this.showIncidentAssignDropdown[incidentId] = true;
    },
    async assignIncidentUser({ incidentId, assigneeId, reviewerId }) {
      if (!assigneeId || !reviewerId) {
        alert('Please select both assignee and reviewer.');
        return;
      }
      try {
        await axios.post('http://localhost:8000/workflow/create/', {
          incident_id: incidentId,
          assignee_id: assigneeId,
          reviewer_id: reviewerId
        });
        this.successMessage = 'Incident assigned successfully!';
        this.incidentAssigned[incidentId] = true;
        this.incidents = this.incidents.filter(i => i.IncidentId !== incidentId);
        setTimeout(() => { this.successMessage = ''; }, 3000);
      } catch (error) {
        alert('Failed to assign incident.');
      }
      this.showIncidentAssignDropdown[incidentId] = false;
    },
    triggerIncidentNotification(incident) {
      this.newIncident = incident;
      this.showIncidentNotification = true;
    },
    handleSolve(incident) {
      this.incidents = this.incidents.filter(i => i.IncidentId !== incident.IncidentId);
    },
    handleReject(incident) {
      this.incidents = this.incidents.filter(i => i.IncidentId !== incident.IncidentId);
    },
    showAssignDropdownForIncident(incidentId) {
      this.showIncidentAssignDropdown[incidentId] = true;
    },
    handleContinue(finding) {
      if (finding.is_risk) {
        this.currentRiskFinding = finding;
        this.showRiskModal = true;
      } else {
        this.showDecisionButtons[finding.date] = true;
      }
    },
    confirmRiskWorkflow() {
      this.showRiskModal = false;
      this.$router.push({ path: '/risk-workflow', query: { findingDate: this.currentRiskFinding.date } });
    },
    cancelRiskWorkflow() {
      this.showRiskModal = false;
      this.currentRiskFinding = null;
    },
  },
  created() {
    this.fetchIncidents();
    this.fetchUncheckedFindings();
    this.fetchUsers();
    this.fetchAssignedFindings();
  }
}
</script>

<style scoped>
.incidents-container {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.incidents-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.create-btn {
  padding: 0.75rem 1.5rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.create-btn:hover {
  background-color: #45a049;
}

.incidents-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.incident-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.incident-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.incident-header h3 {
  margin: 0;
  color: #333;
}

.priority-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.priority-badge.low {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.priority-badge.medium {
  background-color: #fff3e0;
  color: #ef6c00;
}

.priority-badge.high {
  background-color: #ffebee;
  color: #c62828;
}

.priority-badge.critical {
  background-color: #fce4ec;
  color: #c2185b;
}

.description {
  color: #666;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.incident-details {
  display: flex;
  justify-content: space-between;
  color: #888;
  font-size: 0.875rem;
}

.no-incidents {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  color: #666;
}

.notification {
  background-color: #fff3cd;
  border: 1px solid #ffeeba;
  color: #856404;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.finding-alert {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  background: #fffbe6;
  border-radius: 6px;
  padding: 1rem;
  border: 1px solid #ffeeba;
}

.finding-content {
  flex: 1;
}

.finding-actions {
  display: flex;
  gap: 0.5rem;
}

.accept-btn {
  padding: 0.5rem 1.2rem;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}

.accept-btn:hover {
  background-color: #218838;
}

.reject-btn {
  padding: 0.5rem 1.2rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}

.reject-btn:hover {
  background-color: #b52a37;
}

.assign-dropdown {
  background: #f8f9fa;
  border: 1px solid #ccc;
  padding: 1rem;
  border-radius: 6px;
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.assign-btn {
  padding: 0.5rem 1.2rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  margin-left: 0.5rem;
  transition: background-color 0.2s;
}

.assign-btn:hover {
  background-color: #0056b3;
}

.success-message {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-align: center;
  font-weight: bold;
}

.assigned-card {
  border: 2px solid #007bff;
  background: #e9f7fe;
}

.assigned-badge {
  background: #007bff;
  color: #fff;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.incident-notifications-row {
  display: flex;
  flex-direction: row;
  gap: 2rem;
  justify-content: center;
  align-items: flex-start;
  margin: 2rem 0;
}

.continue-btn {
  padding: 0.5rem 1.2rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  margin-right: 0.5rem;
  transition: background-color 0.2s;
}

.continue-btn:hover {
  background-color: #0056b3;
}

.notnow-btn {
  padding: 0.5rem 1.2rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  margin-left: 0.5rem;
  transition: background-color 0.2s;
}

.notnow-btn:hover {
  background-color: #b52a37;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  padding: 2rem 2.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.2);
  text-align: center;
}
</style>
