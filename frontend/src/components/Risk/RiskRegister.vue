<template>
  <div class="risk-container">
    <div class="risk-card">
      <div class="header-row">
        <h2 class="risk-title"><i class="fas fa-exclamation-triangle risk-icon"></i> Risk Table</h2>
        <button @click="showAddForm = !showAddForm" class="add-risk-btn">
          <i class="fas fa-plus"></i> {{ showAddForm ? 'Cancel' : 'Add Risk' }}
        </button>
      </div>
      
      <!-- Add Risk Form -->
      <div v-if="showAddForm" class="add-risk-form">
        <h3>Add New Risk</h3>
        <form @submit.prevent="submitRisk">
          <div class="form-grid">
            <div class="form-group">
              <label>Compliance ID</label>
              <input type="number" v-model="newRisk.ComplianceId" required />
            </div>
            
            <div class="form-group">
              <label>Criticality</label>
              <select v-model="newRisk.Criticality" required>
                <option value="">Select Criticality</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Category</label>
              <select v-model="newRisk.Category" required>
                <option value="">Select Category</option>
                <option value="IT Security">IT Security</option>
                <option value="Operational">Operational</option>
                <option value="Compliance">Compliance</option>
                <option value="Financial">Financial</option>
                <option value="Strategic">Strategic</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Risk Priority</label>
              <select v-model="newRisk.RiskPriority" required>
                <option value="">Select Priority</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Risk Likelihood</label>
              <input type="number" step="0.1" v-model="newRisk.RiskLikelihood" placeholder="Enter value (e.g. 8.5)" required />
            </div>
            
            <div class="form-group">
              <label>Risk Impact</label>
              <input type="number" step="0.1" v-model="newRisk.RiskImpact" placeholder="Enter value (e.g. 7.0)" required />
            </div>
            
            <div class="form-group">
              <label>Risk Exposure Rating</label>
              <input type="number" step="0.1" v-model="newRisk.RiskExposureRating" placeholder="Enter value (e.g. 7.5)" />
            </div>
            
            <div class="form-group wide">
              <label>Risk Description</label>
              <textarea v-model="newRisk.RiskDescription" required></textarea>
            </div>
            
            <div class="form-group wide">
              <label>Possible Damage</label>
              <textarea v-model="newRisk.PossibleDamage"></textarea>
            </div>
            
            <div class="form-group wide">
              <label>Risk Mitigation</label>
              <textarea v-model="newRisk.RiskMitigation"></textarea>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="showAddForm = false" class="cancel-btn">Cancel</button>
            <button type="submit" class="submit-btn">Add Risk</button>
          </div>
        </form>
      </div>
      
      <div class="filters-row">
        <select v-model="selectedCriticality" class="filter-select">
          <option value="">All Criticality</option>
          <option v-for="c in uniqueCriticality" :key="c">{{ c }}</option>
        </select>
        <select v-model="selectedCategory" class="filter-select">
          <option value="">All Category</option>
          <option v-for="cat in uniqueCategory" :key="cat">{{ cat }}</option>
        </select>
        <select v-model="selectedPriority" class="filter-select">
          <option value="">All Priority</option>
          <option v-for="p in uniquePriority" :key="p">{{ p }}</option>
        </select>
      </div>
      <div class="table-wrapper">
        <table v-if="filteredRisks.length" class="risk-table">
          <thead>
            <tr>
              <th>RiskId</th>
              <th>ComplianceId</th>
              <th>Criticality</th>
              <th>PossibleDamage</th>
              <th>Category</th>
              <th>RiskDescription</th>
              <th>RiskLikelihood</th>
              <th>RiskImpact</th>
              <th>RiskExposureRating</th>
              <th>RiskPriority</th>
              <th>RiskMitigation</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="risk in filteredRisks" :key="risk.RiskId">
              <td>{{ risk.RiskId }}</td>
              <td>{{ risk.ComplianceId }}</td>
              <td>{{ risk.Criticality }}</td>
              <td>{{ risk.PossibleDamage }}</td>
              <td>{{ risk.Category }}</td>
              <td>{{ risk.RiskDescription }}</td>
              <td>{{ risk.RiskLikelihood }}</td>
              <td>{{ risk.RiskImpact }}</td>
              <td>{{ risk.RiskExposureRating }}</td>
              <td>{{ risk.RiskPriority }}</td>
              <td>{{ risk.RiskMitigation }}</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="loading">No risks found for selected filters.</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'CreateRisk',
  data() {
    return {
      risks: [],
      selectedCriticality: '',
      selectedCategory: '',
      selectedPriority: '',
      showAddForm: false,
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
      }
    }
  },
  computed: {
    uniqueCriticality() {
      return [...new Set(this.risks.map(i => i.Criticality).filter(Boolean))]
    },
    uniqueCategory() {
      return [...new Set(this.risks.map(i => i.Category).filter(Boolean))]
    },
    uniquePriority() {
      return [...new Set(this.risks.map(i => i.RiskPriority).filter(Boolean))]
    },
    filteredRisks() {
      return this.risks.filter(i =>
        (!this.selectedCriticality || i.Criticality === this.selectedCriticality) &&
        (!this.selectedCategory || i.Category === this.selectedCategory) &&
        (!this.selectedPriority || i.RiskPriority === this.selectedPriority)
      )
    }
  },
  mounted() {
    this.fetchRisks()
  },
  methods: {
    fetchRisks() {
      axios.get('http://localhost:8000/api/risks/')
        .then(response => {
          this.risks = response.data
        })
        .catch(error => {
          console.error('Error fetching risks:', error)
        })
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
        .then(response => {
          // Add the new risk to the table
          this.risks.push(response.data)
          
          // Reset the form
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
          
          // Hide the form
          this.showAddForm = false
          
          // Show success message
          alert('Risk added successfully!')
        })
        .catch(error => {
          console.error('Error adding risk:', error.response?.data || error.message)
          alert('Error adding risk. Please check your data and try again.')
        })
    }
  }
}
</script>

<style scoped>
.risk-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 90vh;
  background: #f5f7fa;
  overflow: hidden;
}

.risk-card {
  background: #eaf1fb;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(44, 62, 80, 0.08), 0 1.5px 4px rgba(44, 62, 80, 0.03);
  padding: 2.5rem 2rem 2rem 2rem;
  margin-top: 1.0rem;
  margin-left: 200px;
  width: calc(95vw - 220px);
  max-width: none;
  overflow: visible;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.risk-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
}

.add-risk-btn {
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.add-risk-btn:hover {
  background-color: #3367d6;
}

.risk-icon {
  color: #fbbc05;
  font-size: 2.1rem;
}

.table-wrapper {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 60vh;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(44, 62, 80, 0.04);
  background: #fff;
}

.risk-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: #fff;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 1rem;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,60,180,0.04);
}

.risk-table th, .risk-table td {
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid #e6e6e6;
  vertical-align: top;
}

.risk-table th {
  background: #f4f7fb;
  color: #22314a;
  font-weight: 700;
  position: sticky;
  top: 0;
  z-index: 2;
  letter-spacing: 0.03em;
  box-shadow: 0 2px 4px rgba(44, 62, 80, 0.03);
  font-size: 1.08rem;
}

.risk-table tbody tr:hover {
  background: #f0f6ff;
  transition: background 0.2s;
}

.risk-table td {
  color: #2c3e50;
  background: #fff;
}

.loading {
  text-align: center;
  color: #888;
  font-size: 1.1rem;
  padding: 2rem 0;
}

.filters-row {
  display: flex;
  gap: 18px;
  margin-bottom: 1.2rem;
  align-items: center;
}

.filter-select {
  padding: 8px 18px;
  border-radius: 8px;
  border: 1.5px solid #e0e7ef;
  background: #f4f7fb;
  color: #22314a;
  font-size: 1rem;
  font-weight: 500;
  outline: none;
  transition: border 0.18s;
}

.filter-select:focus {
  border: 1.5px solid #4285f4;
}

/* Add Risk Form Styles */
.add-risk-form {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.add-risk-form h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 1.2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group.wide {
  grid-column: span 3;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #22314a;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 1rem;
  cursor: pointer;
}

.submit-btn {
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 1rem;
  cursor: pointer;
}

.submit-btn:hover {
  background-color: #3367d6;
}
</style> 