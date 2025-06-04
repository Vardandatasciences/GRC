<template>
  <div class="notifications-container" :class="{'show-mapped-risks': showMappedRisks}">
    <!-- Only show notifications header when not showing mapped risks -->
    <div class="notifications-header-row" v-if="!showMappedRisks">
      <h1 class="notifications-title">
        Notifications
        <i class="fas fa-bell notifications-bell"></i>
      </h1>
    </div>
    
    <!-- List of Notifications -->
    <div class="notification-list" v-if="notifications.length > 0 && !showMappedRisks && !showRiskInstanceForm">
      <div class="notification-card" v-for="(notification, index) in notifications" :key="index">
        <div class="notification-header">
          <h3>{{ getRiskDescription(notification) }}</h3>
          <span class="notification-date">
            <i class="fas fa-calendar-alt"></i> 
            {{ formatDate(notification.review_date || notification.timestamp || notification.createdAt) }}
          </span>
        </div>
        <div class="notification-pill">{{ notification.category || notification.Category || notification.documents || notification.security || 'N/A' }}</div>
        <div class="notification-details-grid">
          <div class="details-box">
            <div class="details-row">
              <div class="details-label">PRIORITY:</div>
              <div class="details-value">{{ notification.priority || notification.Priority || 'N/A' }}</div>
            </div>
            <div class="details-row">
              <div class="details-label">CATEGORY:</div>
              <div class="details-value">{{ notification.category || notification.Category || 'N/A' }}</div>
            </div>
            <div class="details-row">
              <div class="details-label">ORIGIN:</div>
              <div class="details-value">{{ notification.origin || notification.Origin || 'Audit Finding' }}</div>
            </div>
            <div class="details-row">
              <div class="details-label">COMPLIANCE ID:</div>
              <div class="details-value">{{ notification.complianceId || notification.ComplianceId || 'N/A' }}</div>
            </div>
          </div>
        </div>
        <div class="notification-actions">
          <button class="view-details-btn" @click="viewRiskDetails(notification)">
            <i class="fas fa-eye"></i> View Details
          </button>
          <button class="accept-btn" @click="acceptIncident(notification)">
            <i class="fas fa-check"></i> Accept
          </button>
          <button class="reject-btn" @click="rejectIncident(notification)">
            <i class="fas fa-times"></i> Reject
          </button>
        </div>
      </div>
    </div>
    
    <!-- Mapped Risks View as a separate full-page view -->
    <div v-if="showMappedRisks" class="mapped-risks-container">
      <div class="mapped-risks-header">
        <button class="back-btn" @click="returnToNotifications">
          &larr; Back to Notifications
        </button>
        <h2>Risk Management for Incident: {{ selectedIncident.Title }}</h2>
      </div>
      
      <!-- Display risk form inline instead of as a popup -->
      <div v-if="showCreateRiskForm" class="add-risk-form">
        <h3>Create New Risk</h3>
        <form @submit.prevent="submitNewRisk" class="risk-form">
          <div class="form-grid">
            <div class="form-group">
              <label>Compliance ID</label>
              <input 
                type="number" 
                v-model="riskForm.ComplianceId" 
                readonly 
                class="readonly-field"
              />
            </div>
            
            <div class="form-group">
              <label>Category *</label>
              <select v-model="riskForm.Category" required>
                <option value="">Select Category</option>
                <option value="Operational">Operational</option>
                <option value="Compliance">Compliance</option>
                <option value="IT Security">IT Security</option>
                <option value="Financial">Financial</option>
                <option value="Strategic">Strategic</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Criticality *</label>
              <select v-model="riskForm.Criticality" required>
                <option value="">Select Criticality</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            
            <div class="form-group wide">
              <label>Risk Description *</label>
              <textarea v-model="riskForm.RiskDescription" required></textarea>
            </div>
            
            <div class="form-group wide">
              <label>Possible Damage</label>
              <textarea v-model="riskForm.PossibleDamage"></textarea>
            </div>
            
            <div class="form-group">
              <label>Risk Likelihood *</label>
              <input 
                type="number" 
                step="0.1" 
                v-model="riskForm.RiskLikelihood" 
                required 
                placeholder="Enter value (e.g. 8.5)"
              />
            </div>
            
            <div class="form-group">
              <label>Risk Impact *</label>
              <input 
                type="number" 
                step="0.1" 
                v-model="riskForm.RiskImpact" 
                required 
                placeholder="Enter value (e.g. 6.0)"
              />
            </div>
            
            <div class="form-group">
              <label>Risk Exposure Rating</label>
              <input 
                type="number" 
                step="0.1" 
                v-model="riskForm.RiskExposureRating" 
                placeholder="Enter value (e.g. 7.2)"
              />
            </div>
            
            <div class="form-group">
              <label>Risk Priority *</label>
              <select v-model="riskForm.RiskPriority" required>
                <option value="">Select Priority</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            
            <div class="form-group wide">
              <label>Risk Mitigation</label>
              <textarea v-model="riskForm.RiskMitigation"></textarea>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showCreateRiskForm = false">
              Cancel
            </button>
            <button type="submit" class="submit-btn">Create Risk</button>
          </div>
        </form>
      </div>
      
      <!-- Fixed the double v-if with a v-else-if structure -->
      <div v-else-if="mappedRisks.length > 0" class="risk-list">
        <table class="risk-table">
          <thead>
            <tr>
              <th width="40">
                <input 
                  type="checkbox" 
                  :checked="allRisksSelected" 
                  @change="toggleAllRisks"
                  class="checkbox"
                />
              </th>
              <th>Risk ID</th>
              <th>Category</th>
              <th>Criticality</th>
              <th>Description</th>
              <th>Likelihood</th>
              <th>Impact</th>
              <th>Priority</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="risk in mappedRisks" :key="risk.RiskId">
              <td>
                <input 
                  type="checkbox" 
                  :value="risk.RiskId" 
                  v-model="selectedRisks"
                  class="checkbox"
                />
              </td>
              <td>{{ risk.RiskId }}</td>
              <td>{{ risk.Category }}</td>
              <td>{{ risk.Criticality }}</td>
              <td>{{ risk.RiskDescription }}</td>
              <td>{{ risk.RiskLikelihood }}</td>
              <td>{{ risk.RiskImpact }}</td>
              <td>{{ risk.RiskPriority }}</td>
            </tr>
          </tbody>
        </table>
        
        <div class="risk-action-bar" v-if="hasSelectedRisks">
          <button class="create-instance-btn" @click="showCreateRiskInstanceForm">
            Create Risk Instance{{ selectedRisks.length > 1 ? 's' : '' }}
          </button>
        </div>
      </div>
      
      <!-- Fixed the double directive issue -->
      <div v-else class="empty-risks">
        <div class="risk-management-card">
          <h3>Risk Management</h3>
          <p v-if="loadingRisks">Loading mapped risks...</p>
          <p v-else>No risks mapped to this incident</p>
          
          <div class="risk-buttons">
            <button class="create-risk-btn own-risk" @click="showOwnRiskForm">
              <i class="fas fa-plus-circle"></i>
              Create Own Risk
            </button>
            <button class="create-risk-btn ai-risk" @click="showNewRiskForm">
              <i class="fas fa-robot"></i>
              Create AI Suggestion Risk
            </button>
          </div>
        </div>
      </div>
      
      <div v-if="loadingRiskAnalysis" class="loading-analysis">
        <p>Analyzing incident with AI assistant...</p>
      </div>
    </div>
    
    <!-- Risk Instance Form -->
    <CreateRiskInstance
      v-if="showRiskInstanceForm"
      :risk-id="currentRisk ? currentRisk.RiskId : null"
      :incident-id="selectedIncident ? selectedIncident.IncidentId : null"
    />
    
    <!-- Accept Options Modal -->
    <div v-if="showAcceptModal" class="modal-overlay">
      <div class="stylish-accept-modal">
        <div class="stylish-header">
          <i class="fas fa-check-circle header-icon"></i>
          <h2>Select Action</h2>
          <button class="close-btn" @click="showAcceptModal = false">×</button>
        </div>
        <div class="accept-options">
          <p>How would you like to proceed with this incident?</p>
          <div class="options-buttons">
            <button class="stylish-btn map-btn" @click="navigateToMappedRisks">
              <i class="fas fa-link"></i>
              Map Risk
            </button>
            <button class="stylish-btn create-btn" @click="proceedWithNewRisk">
              <i class="fas fa-plus-circle"></i>
              Create Risk
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="modal-overlay">
      <div class="stylish-accept-modal">
        <div class="stylish-header">
          <i class="fas fa-exclamation-circle header-icon" style="color: #dc3545;"></i>
          <h2>Incident Rejected</h2>
          <button class="close-btn" @click="showRejectModal = false">×</button>
        </div>
        <div class="success-content">
          <p>Would you like to create a risk instance?</p>
          <div class="options-buttons">
            <button class="stylish-btn create-btn" @click="createRiskInstanceForRejected">
              <i class="fas fa-clipboard-list"></i>
              Create Instance
            </button>
            <button class="stylish-btn map-btn" @click="closeRejectModal">
              <i class="fas fa-times"></i>
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Risk Instance Created Success Modal -->
    <div v-if="showRiskInstanceCreatedModal" class="modal-overlay">
      <div class="stylish-accept-modal">
        <div class="stylish-header">
          <i class="fas fa-check-circle header-icon" style="color: #28a745;"></i>
          <h2>Risk Instance Created</h2>
          <button class="close-btn" @click="closeRiskInstanceCreatedModal">×</button>
        </div>
        <div class="success-content">
          <p>Risk instance has been successfully created for the rejected incident.</p>
          <div class="options-buttons">
            <button class="stylish-btn map-btn" @click="closeRiskInstanceCreatedModal">
              <i class="fas fa-check"></i>
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div class="empty-state" v-if="!loading && notifications.length === 0 && !showMappedRisks && !showRiskInstanceForm">
      <div class="empty-state-icon">
        <i class="fas fa-bell-slash"></i>
      </div>
      <h3 class="empty-state-title">No incidents found</h3>
      <p class="empty-state-message">
        There are no scheduled incidents at this time.
      </p>
      <p class="empty-state-hint">
        You'll be notified when new incidents are scheduled.
      </p>
    </div>
    
    <!-- Loading State -->
    <div class="loading-state" v-if="loading && !showMappedRisks && !showRiskInstanceForm">
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
      </div>
      <p>Loading notifications...</p>
    </div>
    
    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="stylish-accept-modal">
        <div class="stylish-header">
          <i class="fas fa-check-circle header-icon success-icon"></i>
          <h2>Risk Created Successfully</h2>
          <button class="close-btn" @click="showSuccessModal = false">×</button>
        </div>
        <div class="success-content">
          <p>Your risk has been created and added to the system.</p>
          <div class="options-buttons">
            <button class="stylish-btn create-btn" @click="createInstanceFromNewRisk">
              <i class="fas fa-clipboard-list"></i>
              Create Instance
            </button>
            <button class="stylish-btn map-btn" @click="showSuccessModal = false">
              <i class="fas fa-check"></i>
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import './Notifications.css'  // Make sure this is imported
import CreateRiskInstance from './CreateRiskInstance.vue'

export default {
  name: 'NotificationsPage',
  components: {
    CreateRiskInstance
  },
  data() {
    return {
      incidents: [],
      notifications: [],
      loading: true,
      showMappedRisks: false,
      showRiskInstanceForm: false,
      selectedIncident: null,
      mappedRisks: [],
      loadingRisks: false,
      selectedRisks: [],
      riskInstanceForm: {
        RiskId: null,
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
        UserId: 1,  // Default user ID or you can make this dynamic
        Date: new Date().toISOString().split('T')[0]
      },
      currentRisk: null,
      showCreateRiskForm: false,
      riskForm: {
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
      showAcceptModal: false,
      loadingRiskAnalysis: false,
      showSuccessModal: false,
      newlyCreatedRisk: null, // To store the newly created risk for instance creation
      showRejectModal: false,
      rejectedIncident: null,
      showRiskInstanceCreatedModal: false,
      processedIncidents: new Set(), // Track processed incidents
      incidentRiskInstances: {}, // Track which incidents have risk instances
      rejectedIncidents: new Set(), // Track rejected incidents
      userId: 1, // Default user ID - you may need to get this from authentication
    }
  },
  computed: {
    hasSelectedRisks() {
      return this.selectedRisks.length > 0
    },
    allRisksSelected() {
      return this.mappedRisks.length > 0 && this.selectedRisks.length === this.mappedRisks.length
    }
  },
  mounted() {
    // Fetch incidents once - we'll use them as notifications
    this.fetchIncidents()
    
    // Also fetch risk instances for reference
    this.fetchRiskInstances()
  },
  methods: {
    fetchIncidents() {
      // Set loading state
      this.loading = true;
      axios.get('http://localhost:8000/api/incidents/')
        .then(response => {
          console.log('Incidents data received:', response.data);
          // Store all incidents
          this.incidents = response.data;
          // Only filter out incidents that are actually marked as rejected or processed in the backend
          this.notifications = response.data
            .filter(incident => incident.Status && incident.Status.toLowerCase() === 'scheduled')
            .map(incident => ({
              ...incident,
              RiskInstanceId: incident.IncidentId, // Map incident ID to risk instance ID for compatibility
              review_date: incident.Date || incident.CreatedAt, // Use incident date for display
            }));
          this.loading = false;
        })
        .catch(error => {
          console.error('Error fetching incidents:', error);
          this.incidents = [];
          this.notifications = [];
          this.loading = false;
        });
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      
      // Try to parse the date string in different formats
      let date;
      try {
        date = new Date(dateString);
        
        // Check if date is valid
        if (isNaN(date.getTime())) {
          return 'Invalid Date';
        }
        
        return date.toLocaleDateString('en-US', { 
          year: 'numeric', 
          month: 'short', 
          day: 'numeric' 
        });
      } catch (e) {
        console.error('Error formatting date:', e);
        return dateString || 'N/A';
      }
    },
    priorityClass(priority) {
      if (!priority) return ''
      
      const priorityLower = priority.toLowerCase()
      if (priorityLower.includes('critical') || priorityLower.includes('high')) {
        return 'priority-high'
      } else if (priorityLower.includes('medium')) {
        return 'priority-medium'
      }
      return 'priority-low'
    },
    acceptIncident(incident) {
      // Set the selected incident
      this.selectedIncident = incident;
      
      // Show the options modal
      this.showAcceptModal = true;
    },
    fetchMappedRisks(complianceId) {
      // Fetch all risks and filter by ComplianceId
      axios.get('http://localhost:8000/api/risks/')
        .then(response => {
          // Filter risks with matching ComplianceId
          this.mappedRisks = response.data.filter(risk => 
            risk.ComplianceId === complianceId
          )
          this.loadingRisks = false
        })
        .catch(error => {
          console.error('Error fetching mapped risks:', error)
          this.loadingRisks = false
        })
    },
    toggleAllRisks(event) {
      if (event.target.checked) {
        // Select all risks
        this.selectedRisks = this.mappedRisks.map(risk => risk.RiskId)
      } else {
        // Deselect all risks
        this.selectedRisks = []
      }
    },
    showCreateRiskInstanceForm() {
      if (this.selectedRisks.length === 0) {
        alert('Please select at least one risk.')
        return
      }
      this.currentRisk = this.mappedRisks.find(risk => risk.RiskId === this.selectedRisks[0])
      if (!this.currentRisk || !this.selectedIncident) {
        alert('Risk or Incident not selected! Please try again.')
        return
      }
      // Debug log
      console.log('Passing to CreateRiskInstance:', {
        riskId: this.currentRisk.RiskId,
        incidentId: this.selectedIncident.IncidentId
      })
      this.showRiskInstanceForm = true
      this.showMappedRisks = false
    },
    async submitRiskInstance() {
      // Debug logs for troubleshooting
      console.log('riskInstanceForm before submit:', this.riskInstanceForm);
      console.log('selectedIncident:', this.selectedIncident);
      console.log('currentRisk:', this.currentRisk);
      const requestData = JSON.parse(JSON.stringify(this.riskInstanceForm));
      requestData.RiskOwner = 'System Owner';
      requestData.RiskStatus = '';
      // Always set both IDs before submitting
      requestData.IncidentId = this.riskInstanceForm.IncidentId || (this.selectedIncident && this.selectedIncident.IncidentId) || null;
      requestData.RiskId = this.riskInstanceForm.RiskId || (this.currentRisk && this.currentRisk.RiskId) || null;
      // Set RiskStatus to 'Rejected' if this is a reject flow
      if (this.rejectedIncident && this.selectedIncident && this.selectedIncident.IncidentId === this.rejectedIncident.IncidentId) {
        requestData.RiskStatus = 'Rejected';
      }
      // Ensure Appetite is a number
      if (requestData.Appetite && typeof requestData.Appetite !== 'number') {
        requestData.Appetite = parseFloat(requestData.Appetite) || null;
      }
      // Debug log
      console.log('Submitting with IncidentId:', requestData.IncidentId, 'RiskId:', requestData.RiskId);
      // Only require IncidentId, not RiskId
      if (!requestData.IncidentId) {
        alert('IncidentId is missing! Please try again.');
        return;
      }
      // Process RiskMitigation field dynamically
      if (requestData.RiskMitigation) {
        if (typeof requestData.RiskMitigation === 'string') {
          // Split the text into sentences
          let sentences = requestData.RiskMitigation
            .split('.')
            .map(sentence => sentence.trim())
            .filter(sentence => sentence.length > 0);
          // Create numbered object format
          let mitigationObj = {};
          sentences.forEach((sentence, index) => {
            mitigationObj[(index + 1).toString()] = sentence;
          });
          // If no valid sentences were found, create a simple entry
          if (Object.keys(mitigationObj).length === 0) {
            mitigationObj = {"1": requestData.RiskMitigation};
          }
          requestData.RiskMitigation = mitigationObj;
        }
      } else {
        // Set to empty object if not present
        requestData.RiskMitigation = {};
      }
      console.log('Submitting risk instance with data:', requestData);
      try {
        // Create the risk instance first
        const response = await axios.post('http://localhost:8000/api/risk-instances/', requestData, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        console.log('Risk instance created:', response.data);
        // If this was a reject flow, update the incident status to Rejected
        if (this.rejectedIncident && this.selectedIncident && this.selectedIncident.IncidentId === this.rejectedIncident.IncidentId) {
          await this.updateIncidentStatusWithPayload(this.selectedIncident.IncidentId, 'Rejected');
        } else {
          await this.updateIncidentStatusWithPayload(this.selectedIncident.IncidentId, 'Processed');
        }
        // Hide the risk instance form
        this.showRiskInstanceForm = false;
        // Show success modal
        this.showRiskInstanceCreatedModal = true;
        // Reset the form
        this.resetRiskInstanceForm();
      } catch (error) {
        console.error('Error creating risk instance:', error);
        let errorMessage = 'Unknown error';
        if (error.response) {
          if (typeof error.response.data === 'object') {
            errorMessage = JSON.stringify(error.response.data);
          } else if (error.response.data) {
            errorMessage = error.response.data;
          } else {
            errorMessage = `Status ${error.response.status}: ${error.response.statusText}`;
          }
        } else if (error.message) {
          errorMessage = error.message;
        }
        alert(`Error creating risk instance: ${errorMessage}`);
      }
    },
    resetRiskInstanceForm() {
      this.riskInstanceForm = {
        RiskId: null,
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
    },
    async rejectIncident(incident) {
      this.rejectedIncident = incident;
      this.showRejectModal = true;
    },
    proceedWithPredefinedRisk() {
      this.showAcceptModal = false;
      this.showMappedRisks = true;
      this.loadingRisks = true;
      this.selectedRisks = []; // Reset selections
      
      // Fetch risks that match the ComplianceId
      this.fetchMappedRisks(this.selectedIncident.ComplianceId);
    },
    proceedWithNewRisk() {
      this.showAcceptModal = false;
      this.showMappedRisks = true;
      
      // No form display here - just go to the mapped risks screen
      // Remove all of these form-related lines:
      // this.riskForm.ComplianceId = this.selectedIncident.ComplianceId;
      // this.riskForm.Criticality = '';
      // this.riskForm.PossibleDamage = '';
      // etc...
      
      // Don't show the form
      // this.showCreateRiskForm = true;
    },
    proceedWithAIRisk() {
      this.showAcceptModal = false;
      this.showMappedRisks = true;
      
      // Show loading indicator
      this.loadingRiskAnalysis = true;
      
      // Prepare the data for analysis
      const incidentData = {
        title: this.selectedIncident.Title,
        description: this.selectedIncident.Description
      };
      
      console.log('Sending to API:', incidentData);
      
      // Call the SLM API to get analysis
      axios.post('http://localhost:8000/api/analyze-incident/', incidentData)
        .then(response => {
          console.log('SLM Analysis:', response.data);
          
          // Map the SLM response to the form fields
          this.mapAnalysisToForm(response.data);
          
          // Pre-fill the ComplianceId from the incident
          this.riskForm.ComplianceId = this.selectedIncident.ComplianceId;
          
          // Show the create risk form
          this.showCreateRiskForm = true;
          this.loadingRiskAnalysis = false;
        })
        .catch(error => {
          console.error('Error analyzing incident:', error.response || error);
          alert('Failed to analyze incident. Creating blank form instead.');
          
          // Still pre-fill the ComplianceId
          this.riskForm.ComplianceId = this.selectedIncident.ComplianceId;
          
          // Show the create risk form anyway
          this.showCreateRiskForm = true;
          this.loadingRiskAnalysis = false;
        });
    },
    showAcceptOptions(incident) {
      this.selectedIncident = incident;
      this.showAcceptModal = true;
    },
    mapAnalysisToForm(analysis) {
      // Map the SLM analysis fields to the risk form fields
      
      // Map criticality (convert from text to the dropdown values if needed)
      if (analysis.criticality) {
        const criticalityMap = {
          'Severe': 'Critical',
          'Significant': 'High',
          'Moderate': 'Medium',
          'Minor': 'Low'
        };
        this.riskForm.Criticality = criticalityMap[analysis.criticality] || analysis.criticality;
      }
      
      // Map possible damage
      this.riskForm.PossibleDamage = analysis.possibleDamage || '';
      
      // Map category
      this.riskForm.Category = analysis.category || '';
      
      // Map risk description
      this.riskForm.RiskDescription = analysis.riskDescription || '';
      
      // Map risk likelihood (convert from text to number if needed)
      if (analysis.riskLikelihood) {
        const likelihoodMap = {
          'Highly Probable': '9.0',
          'Probable': '7.0',
          'Possible': '5.0',
          'Unlikely': '3.0',
          'Remote': '1.0'
        };
        this.riskForm.RiskLikelihood = likelihoodMap[analysis.riskLikelihood] || '5.0';
      }
      
      // Map risk impact (convert from text to number if needed)
      if (analysis.riskImpact) {
        const impactMap = {
          'Catastrophic': '9.0',
          'Major': '7.0',
          'Moderate': '5.0',
          'Minor': '3.0',
          'Negligible': '1.0'
        };
        this.riskForm.RiskImpact = impactMap[analysis.riskImpact] || '5.0';
      }
      
      // Map risk exposure rating
      this.riskForm.RiskExposureRating = analysis.riskExposureRating ? '7.0' : '';
      
      // Map risk priority
      if (analysis.riskPriority) {
        const priorityMap = {
          'P0': 'Critical',
          'P1': 'High',
          'P2': 'Medium',
          'P3': 'Low'
        };
        this.riskForm.RiskPriority = priorityMap[analysis.riskPriority] || 'Medium';
      }
      
      // Map risk mitigation
      if (analysis.riskMitigation && Array.isArray(analysis.riskMitigation)) {
        // Join but ensure it doesn't exceed 100 characters
        const fullMitigation = analysis.riskMitigation.join('\n');
        this.riskForm.RiskMitigation = fullMitigation.length > 100 
          ? fullMitigation.substring(0, 97) + '...' 
          : fullMitigation;
      }
    },
    showErrorAlert(title, message) {
      // Get a formatted error message
      const formattedMessage = typeof message === 'object' 
        ? JSON.stringify(message, null, 2) 
        : message;
      
      // For now, just use alert, but you could use a nicer modal
      alert(`${title}\n\n${formattedMessage}`);
    },
    showOwnRiskForm() {
      // Pre-fill only the ComplianceId from the incident
      this.riskForm.ComplianceId = this.selectedIncident.ComplianceId;
      
      // Reset other form fields
      this.riskForm.Criticality = '';
      this.riskForm.PossibleDamage = '';
      this.riskForm.Category = '';
      this.riskForm.RiskDescription = '';
      this.riskForm.RiskLikelihood = '';
      this.riskForm.RiskImpact = '';
      this.riskForm.RiskExposureRating = '';
      this.riskForm.RiskPriority = '';
      this.riskForm.RiskMitigation = '';
      
      // Show the create risk form
      this.showCreateRiskForm = true;
    },
    showNewRiskForm() {
      // Show loading indicator
      this.loadingRiskAnalysis = true;
      
      // Prepare the data for analysis
      const incidentData = {
        title: this.selectedIncident.Title,
        description: this.selectedIncident.Description
      };
      
      console.log('Sending to API:', incidentData);
      
      // Call the SLM API to get analysis
      axios.post('http://localhost:8000/api/analyze-incident/', incidentData)
        .then(response => {
          console.log('SLM Analysis:', response.data);
          
          // Map the SLM response to the form fields
          this.mapAnalysisToForm(response.data);
          
          // Pre-fill the ComplianceId from the incident
          this.riskForm.ComplianceId = this.selectedIncident.ComplianceId;
          
          // Show the create risk form
          this.showCreateRiskForm = true;
          this.loadingRiskAnalysis = false;
        })
        .catch(error => {
          console.error('Error analyzing incident:', error.response || error);
          alert('Failed to analyze incident. Creating blank form instead.');
          
          // Still pre-fill the ComplianceId
          this.riskForm.ComplianceId = this.selectedIncident.ComplianceId;
          
          // Show the create risk form anyway
          this.showCreateRiskForm = true;
          this.loadingRiskAnalysis = false;
        });
    },
    submitNewRisk() {
      // Convert numeric string values to actual numbers
      const formData = {
        ...this.riskForm,
        ComplianceId: parseInt(this.riskForm.ComplianceId) || null,
        RiskLikelihood: parseFloat(this.riskForm.RiskLikelihood) || 0,
        RiskImpact: parseFloat(this.riskForm.RiskImpact) || 0,
        RiskExposureRating: this.riskForm.RiskExposureRating ? 
          parseFloat(this.riskForm.RiskExposureRating) : null
      };
      
      console.log('Submitting new risk:', formData);
      
      axios.post('http://localhost:8000/api/risks/', formData)
        .then(response => {
          console.log('Risk created:', response.data);
          
          // Store the newly created risk
          this.newlyCreatedRisk = response.data;
          
          // Add the newly created risk to the mapped risks array
          this.mappedRisks.push(response.data);
          
          // Hide the form but stay on mapped risks view
          this.showCreateRiskForm = false;
          
          // Show success modal instead of alert
          this.showSuccessModal = true;
          
          // Reset the form for next time
          this.resetRiskForm();
        })
        .catch(error => {
          console.error('Error creating risk:', error.response?.data || error.message);
          
          let errorMessage = 'Please check your form data and try again.';
          if (error.response && error.response.data) {
            errorMessage = error.response.data;
          }
          
          this.showErrorAlert('Error creating risk', errorMessage);
        });
    },
    resetRiskForm() {
      this.riskForm = {
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
      };
    },
    createInstanceFromNewRisk() {
      // Close the success modal
      this.showSuccessModal = false;
      
      // Pre-fill the risk instance form with values from the newly created risk
      this.currentRisk = this.newlyCreatedRisk;
      
      // Similar to showCreateRiskInstanceForm method
      this.riskInstanceForm = {
        ...this.riskInstanceForm,
        RiskId: this.currentRisk.RiskId,
        Category: this.currentRisk.Category,
        Criticality: this.currentRisk.Criticality,
        PossibleDamage: this.currentRisk.PossibleDamage,
        RiskDescription: this.currentRisk.RiskDescription,
        RiskLikelihood: this.currentRisk.RiskLikelihood,
        RiskImpact: this.currentRisk.RiskImpact,
        RiskPriority: this.currentRisk.RiskPriority,
        RiskMitigation: this.currentRisk.RiskMitigation,
        Date: new Date().toISOString().split('T')[0]
      }
      
      // Show the risk instance form
      this.showRiskInstanceForm = true;
      this.showMappedRisks = false;
    },
    async createRiskInstanceForRejected() {
      // Close the reject modal
      this.showRejectModal = false;
      // Set the current incident for risk instance creation
      this.selectedIncident = this.rejectedIncident;
      // Initialize a blank risk instance form
      this.resetRiskInstanceForm();
      // Set incident-related fields
      this.riskInstanceForm.IncidentId = this.rejectedIncident.IncidentId;
      this.riskInstanceForm.Category = this.rejectedIncident.RiskCategory || '';
      this.riskInstanceForm.RiskDescription = this.rejectedIncident.Description || '';
      this.riskInstanceForm.Date = new Date().toISOString().split('T')[0];
      // Show the risk instance form
      this.showRiskInstanceForm = true;
    },
    returnToNotifications() {
      this.showMappedRisks = false;
    },
    returnToMappedRisks() {
      this.showRiskInstanceForm = false;
    },
    showIncidentDetailsModal(incident) {
      // Instead of showing a modal, navigate to the details page
      this.$router.push({
        name: 'ViewDetails',
        params: { id: incident.IncidentId }
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
    isIncidentProcessed(incident) {
      // Check both the in-memory set and if risk instances exist for this incident
      // Also consider rejected incidents with risk instances as processed
      return this.processedIncidents.has(incident.IncidentId) || 
             (this.incidentRiskInstances[incident.IncidentId] && 
              this.incidentRiskInstances[incident.IncidentId].length > 0) ||
             (incident.Status && (incident.Status.toLowerCase() === 'processed' || 
              incident.Status.toLowerCase() === 'rejected')) ||
             (this.rejectedIncidents.has(incident.IncidentId) && 
              this.incidentRiskInstances[incident.IncidentId] && 
              this.incidentRiskInstances[incident.IncidentId].length > 0);
    },
    async updateIncidentStatus(incidentId, status) {
      return await this.updateIncidentStatusWithPayload(incidentId, status);
    },
    async updateIncidentStatusWithPayload(incidentId, status) {
      try {
        // First, get the current incident data
        const currentIncidentResponse = await axios.get(`http://localhost:8000/api/incidents/${incidentId}/`);
        const currentIncident = currentIncidentResponse.data;
        
        // Update the status while preserving other fields
        const updatedIncident = {
          ...currentIncident,
          Status: status
        };
        
        // Send the full update
        const response = await axios.put(`http://localhost:8000/api/incidents/${incidentId}/`, updatedIncident, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        console.log(`Incident ${incidentId} status updated to ${status}`, response.data);
        
        // Update the local incident object to reflect the new status
        const incident = this.incidents.find(inc => inc.IncidentId === incidentId);
        if (incident) {
          incident.Status = status;
        }
        
        return response.data;
      } catch (error) {
        console.error('Error updating incident status:', error);
        
        // Fallback: try the simple update method
        try {
          const fallbackResponse = await axios.patch(`http://localhost:8000/api/incidents/${incidentId}/`, {
            Status: status
          }, {
            headers: {
              'Content-Type': 'application/json'
            }
          });
          
          console.log(`Fallback: Incident ${incidentId} status updated to ${status}`);
          
          // Update the local incident object
          const incident = this.incidents.find(inc => inc.IncidentId === incidentId);
          if (incident) {
            incident.Status = status;
          }
          
          return fallbackResponse.data;
        } catch (fallbackError) {
          console.error('Fallback update also failed:', fallbackError);
          throw fallbackError;
        }
      }
    },
    closeRejectModal() {
      this.showRejectModal = false;
      this.rejectedIncident = null;
    },
    closeRiskInstanceCreatedModal() {
      this.showRiskInstanceCreatedModal = false;
      this.rejectedIncident = null;
    },
    navigateToMappedRisks() {
      this.showAcceptModal = false;
      
      // Navigate to MappedRisks component with incident data
      this.$router.push({
        name: 'MappedRisks',
        params: {
          incidentId: this.selectedIncident.IncidentId,
          incident: this.selectedIncident
        }
      });
    },
    // New helper methods for notifications
    getRiskDescription(notification) {
      // For incidents, use the Title or Description
      if (notification.Title) {
        return notification.Title;
      }
      
      if (notification.Description) {
        return notification.Description;
      }
      
      // Try fallback to old notification format
      if (notification.RiskDescription) {
        return notification.RiskDescription;
      }
      
      // Default fallback
      return 'Incident Notification';
    },
    
    getNotificationMessage(notification) {
      // For incidents, provide a status message based on incident status
      if (notification.Status) {
        const status = notification.Status.toLowerCase();
        if (status === 'scheduled') {
          return "An incident has been scheduled and requires your attention.";
        } else if (status === 'processed') {
          return "This incident has been processed.";
        } else if (status === 'rejected') {
          return "This incident has been rejected.";
        } else if (status === 'active') {
          return "This incident is currently active.";
        }
      }
      
      // Default message
      return "You have a new incident that requires your attention.";
    },
    
    getApprovalStatus(notification) {
      // For incidents, map status to a simpler display status
      if (notification.Status) {
        const status = notification.Status.toLowerCase();
        if (status === 'scheduled') {
          return "Pending";
        } else if (status === 'processed') {
          return "Processed";
        } else if (status === 'rejected') {
          return "Rejected";
        } else if (status === 'active') {
          return "Active";
        }
        
        // Return capitalized status if not one of the known statuses
        return notification.Status.charAt(0).toUpperCase() + notification.Status.slice(1);
      }
      
      return "Pending";
    },
    
    getStatusClass(notification) {
      // For incidents, map status to a color class
      if (notification.Status) {
        const status = notification.Status.toLowerCase();
        if (status === 'scheduled') {
          return "priority-medium"; // Yellow
        } else if (status === 'processed') {
          return "priority-low"; // Green
        } else if (status === 'rejected') {
          return "priority-high"; // Red
        } else if (status === 'active') {
          return "priority-medium"; // Yellow
        }
      }
      
      return "priority-medium"; // Default yellow
    },
    
    viewRiskDetails(notification) {
      // For incidents, navigate to the incident detail page
      const incidentId = notification.IncidentId || notification.id;
      
      if (!incidentId) {
        // If we don't have a valid ID, show an alert
        alert('Unable to view incident details: No valid incident ID found');
        return;
      }
      
      // Navigate to the ViewDetails route which is specifically for incident details
      this.$router.push({
        name: 'ViewDetails',
        params: { id: incidentId }
      });
    },
    fetchRiskInstances() {
      axios.get('http://localhost:8000/api/risk-instances/')
        .then(response => {
          // Create a mapping of incident IDs to risk instances
          response.data.forEach(riskInstance => {
            if (riskInstance.IncidentId) {
              if (!this.incidentRiskInstances[riskInstance.IncidentId]) {
                this.incidentRiskInstances[riskInstance.IncidentId] = [];
              }
              this.incidentRiskInstances[riskInstance.IncidentId].push(riskInstance);
            }
          });
          console.log('Risk instances mapping:', this.incidentRiskInstances);
        })
        .catch(error => {
          console.error('Error fetching risk instances:', error);
        })
    },
  }
}
</script>
