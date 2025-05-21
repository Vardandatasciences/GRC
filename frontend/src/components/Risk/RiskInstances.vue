<template>
  <div class="risk-container">
    <div class="risk-card">
      <div class="header-row">
        <h2 class="risk-title"><i class="fas fa-exclamation-triangle risk-icon"></i> Risk Instances Table</h2>
        <button @click="showAddForm = !showAddForm" class="add-instance-btn">
          <i class="fas fa-plus"></i> {{ showAddForm ? 'Cancel' : 'Add Instance' }}
        </button>
      </div>
      
      <!-- Add Instance Form -->
      <div v-if="showAddForm" class="add-instance-form">
        <h3>Add New Risk Instance</h3>
        <form @submit.prevent="submitInstance">
          <div class="form-grid">
            <div class="form-group">
              <label>Risk ID</label>
              <input type="number" v-model="newInstance.RiskId" required />
            </div>
            
            <div class="form-group">
              <label>Criticality</label>
              <select v-model="newInstance.Criticality" required>
                <option value="">Select Criticality</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Category</label>
              <select v-model="newInstance.Category" required>
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
              <label>Appetite</label>
              <select v-model="newInstance.Appetite">
                <option value="">Select Appetite</option>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
                <option value="Risk Averse">Risk Averse</option>
                <option value="Risk Neutral">Risk Neutral</option>
                <option value="Risk Seeking">Risk Seeking</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Risk Likelihood</label>
              <input type="number" step="0.1" v-model="newInstance.RiskLikelihood" placeholder="Enter value (e.g. 8.5)" required />
            </div>
            
            <div class="form-group">
              <label>Risk Impact</label>
              <input type="number" step="0.1" v-model="newInstance.RiskImpact" placeholder="Enter value (e.g. 7.0)" required />
            </div>
            
            <div class="form-group">
              <label>Risk Exposure Rating</label>
              <input type="number" step="0.1" v-model="newInstance.RiskExposureRating" placeholder="Enter value (e.g. 7.5)" />
            </div>
            
            <div class="form-group">
              <label>Risk Priority</label>
              <select v-model="newInstance.RiskPriority" required>
                <option value="">Select Priority</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Risk Response Type</label>
              <select v-model="newInstance.RiskResponseType">
                <option value="">Select Response Type</option>
                <option value="Avoidance">Avoidance</option>
                <option value="Mitigation">Mitigation</option>
                <option value="Transfer">Transfer</option>
                <option value="Acceptance">Acceptance</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Risk Owner</label>
              <input type="text" v-model="newInstance.RiskOwner" required />
            </div>
            
            <div class="form-group">
              <label>Risk Status</label>
              <select v-model="newInstance.RiskStatus" required>
                <option value="">Select Status</option>
                <option value="Open">Open</option>
                <option value="In Progress">In Progress</option>
                <option value="Closed">Closed</option>
                <option value="Resolved">Resolved</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>User ID</label>
              <input type="number" v-model="newInstance.UserId" />
            </div>
            
            <div class="form-group wide">
              <label>Risk Description</label>
              <textarea v-model="newInstance.RiskDescription" required></textarea>
            </div>
            
            <div class="form-group wide">
              <label>Possible Damage</label>
              <textarea v-model="newInstance.PossibleDamage"></textarea>
            </div>
            
            <div class="form-group wide">
              <label>Risk Response Description</label>
              <textarea v-model="newInstance.RiskResponseDescription"></textarea>
            </div>
            
            <div class="form-group wide">
              <label>Risk Mitigation</label>
              <textarea v-model="newInstance.RiskMitigation"></textarea>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="showAddForm = false" class="cancel-btn">Cancel</button>
            <button type="submit" class="submit-btn">Add Instance</button>
          </div>
        </form>
      </div>
      
      <div class="filters-row">
        <select v-model="selectedCriticality" class="filter-select">
          <option value="">All Criticality</option>
          <option v-for="c in uniqueCriticality" :key="c">{{ c }}</option>
        </select>
        <select v-model="selectedStatus" class="filter-select">
          <option value="">All Status</option>
          <option v-for="s in uniqueStatus" :key="s">{{ s }}</option>
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
        <table v-if="filteredInstances.length" class="risk-table">
          <thead>
            <tr>
              <th>RiskInstanceId</th>
              <th>RiskId</th>
              <th>Criticality</th>
              <th>PossibleDamage</th>
              <th>Category</th>
              <th>Appetite</th>
              <th>RiskDescription</th>
              <th>RiskLikelihood</th>
              <th>RiskImpact</th>
              <th>RiskExposureRating</th>
              <th>RiskPriority</th>
              <th>RiskResponseType</th>
              <th>RiskResponseDescription</th>
              <th>RiskMitigation</th>
              <th>RiskOwner</th>
              <th>RiskStatus</th>
              <th>UserId</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="instance in filteredInstances" :key="instance.RiskInstanceId">
              <td>{{ instance.RiskInstanceId }}</td>
              <td>{{ instance.RiskId }}</td>
              <td>{{ instance.Criticality }}</td>
              <td>{{ instance.PossibleDamage }}</td>
              <td>{{ instance.Category }}</td>
              <td>{{ instance.Appetite }}</td>
              <td>{{ instance.RiskDescription }}</td>
              <td>{{ instance.RiskLikelihood }}</td>
              <td>{{ instance.RiskImpact }}</td>
              <td>{{ instance.RiskExposureRating }}</td>
              <td>{{ instance.RiskPriority }}</td>
              <td>{{ instance.RiskResponseType }}</td>
              <td>{{ instance.RiskResponseDescription }}</td>
              <td>{{ instance.RiskMitigation }}</td>
              <td>{{ instance.RiskOwner }}</td>
              <td>{{ instance.RiskStatus }}</td>
              <td>{{ instance.UserId }}</td>
              <td>{{ instance.Date }}</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="loading">No risk instances found for selected filters.</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RiskInstances',
  data() {
    return {
      instances: [],
      selectedCriticality: '',
      selectedStatus: '',
      selectedCategory: '',
      selectedPriority: '',
      showAddForm: false,
      newInstance: {
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
        RiskStatus: 'Open',
        UserId: 1,
        Date: new Date().toISOString().split('T')[0]
      }
    }
  },
  computed: {
    uniqueCriticality() {
      return [...new Set(this.instances.map(i => i.Criticality).filter(Boolean))]
    },
    uniqueStatus() {
      return [...new Set(this.instances.map(i => i.RiskStatus).filter(Boolean))]
    },
    uniqueCategory() {
      return [...new Set(this.instances.map(i => i.Category).filter(Boolean))]
    },
    uniquePriority() {
      return [...new Set(this.instances.map(i => i.RiskPriority).filter(Boolean))]
    },
    filteredInstances() {
      return this.instances.filter(i =>
        (!this.selectedCriticality || i.Criticality === this.selectedCriticality) &&
        (!this.selectedStatus || i.RiskStatus === this.selectedStatus) &&
        (!this.selectedCategory || i.Category === this.selectedCategory) &&
        (!this.selectedPriority || i.RiskPriority === this.selectedPriority)
      )
    }
  },
  mounted() {
    this.fetchInstances()
  },
  methods: {
    fetchInstances() {
      axios.get('http://localhost:8000/api/risk-instances/')
        .then(response => {
          this.instances = response.data
        })
        .catch(error => {
          console.error('Error fetching risk instances:', error)
        })
    },
    submitInstance() {
      // Convert numeric string values to actual numbers
      const formData = {
        ...this.newInstance,
        RiskId: parseInt(this.newInstance.RiskId) || null,
        RiskLikelihood: parseFloat(this.newInstance.RiskLikelihood) || 0,
        RiskImpact: parseFloat(this.newInstance.RiskImpact) || 0,
        RiskExposureRating: this.newInstance.RiskExposureRating ? 
          parseFloat(this.newInstance.RiskExposureRating) : null,
        UserId: parseInt(this.newInstance.UserId) || null
      }
      
      axios.post('http://localhost:8000/api/risk-instances/', formData)
        .then(response => {
          // Add the new instance to the table
          this.instances.push(response.data)
          
          // Reset the form
          this.newInstance = {
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
            RiskStatus: 'Open',
            UserId: 1,
            Date: new Date().toISOString().split('T')[0]
          }
          
          // Hide the form
          this.showAddForm = false
          
          // Show success message
          alert('Risk instance added successfully!')
        })
        .catch(error => {
          console.error('Error adding risk instance:', error.response?.data || error.message)
          alert('Error adding risk instance. Please check your data and try again.')
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
  min-height: 80vh;
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

.add-instance-btn {
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

.add-instance-btn:hover {
  background-color: #3367d6;
}

.risk-icon {
  color: #fbbc05;
  font-size: 2.1rem;
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

/* Add Instance Form Styles */
.add-instance-form {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.add-instance-form h3 {
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