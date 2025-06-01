<template>
  <div class="risk-container">
    <div class="risk-card">
      <h2 class="risk-title"><i class="fas fa-exclamation-triangle risk-icon"></i> Risk Table</h2>
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
      selectedPriority: ''
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
    axios.get('http://localhost:8000/api/risks/')
      .then(response => {
        this.risks = response.data
      })
      .catch(error => {
        console.error('Error fetching risks:', error)
      })
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
</style> 