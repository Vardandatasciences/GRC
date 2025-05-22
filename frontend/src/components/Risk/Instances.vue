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

.risk-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 12px;
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
</style> 