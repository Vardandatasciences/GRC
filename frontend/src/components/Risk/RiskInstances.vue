<template>
  <div class="risk-instance-container">
    <div class="header-row">
      <h2 class="risk-title"><i class="fas fa-exclamation-triangle risk-icon"></i> Risk Instances Table</h2>
    </div>
    
    <div class="filters-row">
      <div class="filter-group">
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
    </div>
    
    <div class="risk-list-table-container">
      <table v-if="filteredInstances.length" class="risk-list-table">
        <thead>
          <tr>
            <th class="risk-id">RiskID</th>
            <th>Origin</th>
            <th>Category</th>
            <th>Criticality</th>
            <th>Risk Description</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="instance in filteredInstances" :key="instance.RiskInstanceId">
            <td class="risk-id" style="background: none !important; border-radius: 0 !important;">{{ instance.RiskId }}</td>
            <td><span class="origin-badge">MANUAL</span></td>
            <td><span class="category-badge">{{ instance.Category }}</span></td>
            <td>
              <span :class="'priority-' + instance.Criticality.toLowerCase()">
                {{ instance.Criticality }}
              </span>
            </td>
            <td>
              <router-link :to="{ name: 'RiskInstanceDetails', params: { id: instance.RiskInstanceId }}" class="risk-title-link">
                {{ instance.RiskDescription }}
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="no-incident-data">No risk instances found for selected filters.</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import '../Risk/RiskInstances.css'

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
      // Using the direct endpoint as shown in Postman
      axios.get('http://localhost:8000/risk-instances')
        .then(response => {
          this.instances = response.data
          console.log('Fetched risk instances:', response.data.length)
        })
        .catch(error => {
          console.error('Error fetching risk instances:', error)
          // Try alternative endpoint if the first one fails
          this.tryAlternativeEndpoint()
        })
    },
    tryAlternativeEndpoint() {
      console.log('Trying alternative endpoint...')
      axios.get('http://localhost:8000/api/risk-instances')
        .then(response => {
          this.instances = response.data
          console.log('Fetched risk instances from alternative endpoint:', response.data.length)
        })
        .catch(error => {
          console.error('Error with alternative endpoint:', error)
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
      
      axios.post('http://localhost:8000/risk-instances/', formData)
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


