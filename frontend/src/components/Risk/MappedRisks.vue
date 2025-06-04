<template>
  <div class="mapped-risks-container">
    <div class="mapped-risks-header">
      <button class="back-btn" @click="goBack">
        ← Back to Notifications
      </button>
      <h2>Mapped Risks</h2>
    </div>
    
    <div v-if="loading" class="mapped-risks-loading-state">
      <p>Loading mapped risks...</p>
    </div>

    <div v-else-if="mappedRisks.length > 0" class="mapped-risks-list">
      <table class="mapped-risks-table">
        <thead>
          <tr>
            <th><input type="checkbox" :checked="allRisksSelected" @change="toggleAllRisks" class="mapped-risks-checkbox"/></th>
            <th>ID</th>
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
            <td><input type="checkbox" :value="risk.RiskId" v-model="selectedRisks" class="mapped-risks-checkbox"/></td>
            <td>{{ risk.RiskId }}</td>
            <td>{{ risk.Category }}</td>
            <td><span :class="['mapped-risks-status-badge', risk.Criticality.toLowerCase()]">{{ risk.Criticality }}</span></td>
            <td class="mapped-risks-description-cell" @click="showDescription(risk.RiskDescription)">
              <div class="mapped-risks-description-content">{{ risk.RiskDescription }}</div>
            </td>
            <td>{{ risk.RiskLikelihood }}</td>
            <td>{{ risk.RiskImpact }}</td>
            <td><span :class="['mapped-risks-status-badge', risk.RiskPriority.toLowerCase()]">{{ risk.RiskPriority }}</span></td>
          </tr>
        </tbody>
      </table>

      <div class="mapped-risks-pagination-controls">
        <div class="mapped-risks-rows-per-page">
          Rows per page:
          <select class="mapped-risks-rows-select" v-model="rowsPerPage">
            <option value="5">5</option>
            <option value="10">10</option>
            <option value="20">20</option>
          </select>
        </div>
        
        <div class="mapped-risks-pagination-info">
          {{ startIndex }}-{{ endIndex }} of {{ totalItems }}
        </div>
        
        <div class="mapped-risks-pagination-buttons">
          <button class="mapped-risks-pagination-button" :disabled="currentPage === 1" @click="goToFirstPage">⟪</button>
          <button class="mapped-risks-pagination-button" :disabled="currentPage === 1" @click="previousPage">⟨</button>
          <button class="mapped-risks-pagination-button" :disabled="currentPage === totalPages" @click="nextPage">⟩</button>
          <button class="mapped-risks-pagination-button" :disabled="currentPage === totalPages" @click="goToLastPage">⟫</button>
        </div>
      </div>
      
      <div class="mapped-risks-action-bar" v-if="hasSelectedRisks">
        <button class="mapped-risks-create-instance-btn" @click="createRiskInstance">
          Create Risk Instance{{ selectedRisks.length > 1 ? 's' : '' }}
        </button>
      </div>
    </div>
    
    <div v-else class="mapped-risks-empty">
      <p>No risks mapped to this incident</p>
      
      <div class="mapped-risks-buttons">
        <button class="mapped-risks-create-btn own-risk" @click="createOwnRisk">
          Create Own Risk
        </button>
        <button class="mapped-risks-create-btn ai-risk" @click="createAIRisk">
          Create AI Suggestion Risk
        </button>
      </div>
    </div>

    <!-- Description Modal -->
    <div v-if="showModal" class="mapped-risks-modal-overlay" @click="closeModal">
      <div class="mapped-risks-modal-content" @click.stop>
        <div class="mapped-risks-modal-header">
          <h3>Risk Description</h3>
          <button class="mapped-risks-close-button" @click="closeModal">&times;</button>
        </div>
        <div class="mapped-risks-modal-body">
          {{ selectedDescription }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import './MappedRisks.css'

export default {
  name: 'MappedRisks',
  data() {
    return {
      loading: true,
      mappedRisks: [],
      selectedRisks: [],
      incidentTitle: '',
      incidentId: null,
      complianceId: null,
      rowsPerPage: 5,
      currentPage: 1,
      totalItems: 0,
      totalPages: 0,
      startIndex: 0,
      endIndex: 0,
      showModal: false,
      selectedDescription: ''
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
  created() {
    // Get incident details from route params
    const incidentId = this.$route.params.incidentId;
    const incident = this.$route.params.incident;

    if (incident) {
      this.incidentId = incident.IncidentId;
      this.incidentTitle = incident.IncidentTitle;
      this.complianceId = incident.ComplianceId;
      this.fetchMappedRisks();
    } else if (incidentId) {
      // If we only have the ID, fetch the incident details
      axios.get(`http://localhost:8000/api/incidents/${incidentId}/`)
        .then(response => {
          const incident = response.data;
          this.incidentId = incident.IncidentId;
          this.incidentTitle = incident.IncidentTitle;
          this.complianceId = incident.ComplianceId;
          this.fetchMappedRisks();
        })
        .catch(error => {
          console.error('Error fetching incident:', error);
          this.goBack();
        });
    } else {
      this.goBack();
    }
  },
  methods: {
    fetchMappedRisks() {
      this.loading = true
      axios.get('http://localhost:8000/api/risks/')
        .then(response => {
          this.mappedRisks = response.data.filter(risk => 
            risk.ComplianceId === this.complianceId
          )
          this.totalItems = this.mappedRisks.length;
          this.totalPages = Math.ceil(this.totalItems / this.rowsPerPage);
          this.startIndex = (this.currentPage - 1) * this.rowsPerPage + 1;
          this.endIndex = Math.min(this.startIndex + this.rowsPerPage - 1, this.totalItems);
          this.loading = false
        })
        .catch(error => {
          console.error('Error fetching mapped risks:', error)
          this.loading = false
        })
    },
    toggleAllRisks(event) {
      if (event.target.checked) {
        this.selectedRisks = this.mappedRisks.map(risk => risk.RiskId)
      } else {
        this.selectedRisks = []
      }
    },
    createRiskInstance() {
      // Only allow one risk instance at a time for now
      if (!this.incidentId || this.selectedRisks.length === 0) {
        alert('Please select a risk to create an instance.');
        return;
      }
      // Use the first selected risk for instance creation
      const riskId = this.selectedRisks[0];
      this.$router.push({
        name: 'CreateRiskInstance',
        query: {
          incidentId: this.incidentId,
          riskId: riskId
        }
      });
    },
    createOwnRisk() {
      this.$router.push({
        name: 'CreateRisk',
        params: {
          incidentId: this.incidentId,
          type: 'own'
        }
      })
    },
    createAIRisk() {
      this.$router.push({
        name: 'CreateRisk',
        params: {
          incidentId: this.incidentId,
          type: 'ai'
        }
      })
    },
    goBack() {
      this.$router.push({ name: 'RiskNotifications' });
    },
    goToFirstPage() {
      this.currentPage = 1;
      this.fetchMappedRisks();
    },
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.fetchMappedRisks();
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.fetchMappedRisks();
      }
    },
    goToLastPage() {
      this.currentPage = this.totalPages;
      this.fetchMappedRisks();
    },
    showDescription(description) {
      this.selectedDescription = description;
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
      this.selectedDescription = '';
    }
  }
}
</script>