<template>
  <div class="risk-container">
    <div class="risk-card">
      <h2 class="risk-title"><i class="fas fa-exclamation-triangle risk-icon"></i> Risk Instances Table</h2>
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
      selectedPriority: ''
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
    axios.get('http://localhost:8000/api/risk-instances/')
      .then(response => {
        this.instances = response.data
      })
      .catch(error => {
        console.error('Error fetching risk instances:', error)
      })
  }
}
</script>

<style>
@import './Instances.css';
</style>
