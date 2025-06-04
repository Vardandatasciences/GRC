<template>
  <div class="risk-register-container">
    <div class="risk-register-header-row">
      <h2 class="risk-register-title"><i class="fas fa-exclamation-triangle risk-register-icon"></i> Risk Register List</h2>
    </div>
    
    <div class="risk-register-filters-row">
      <div class="search-container">
        <i class="fas fa-search search-icon"></i>
        <input type="text" v-model="searchQuery" placeholder="Search risks..." class="risk-search-input">
      </div>
      <div class="filter-group">
        <select v-model="selectedCriticality" class="sort-select">
          <option value="">All Criticality</option>
          <option v-for="c in uniqueCriticality" :key="c">{{ c }}</option>
        </select>
        <select v-model="selectedCategory" class="sort-select">
          <option value="">All Category</option>
          <option v-for="cat in uniqueCategory" :key="cat">{{ cat }}</option>
        </select>
      </div>
    </div>

    <div class="risk-list-table-container">
      <table v-if="filteredRisks.length" class="risk-list-table">
        <thead>
          <tr>
            <th>RiskID</th>
            <th>Origin</th>
            <th>Category</th>
            <th>Criticality</th>
            <th>Risk Description</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="risk in paginatedRisks" :key="risk.RiskId">
            <td class="risk-id">{{ risk.RiskId }}</td>
            <td>
              <div class="origin-badge">{{ risk.Origin || 'MANUAL' }}</div>
            </td>
            <td>
              <div class="category-badge">{{ risk.Category }}</div>
            </td>
            <td>
              <div :class="getCriticalityClass(risk.Criticality)">{{ risk.Criticality }}</div>
            </td>
            <td>
              <router-link :to="`/risk/details/${risk.RiskId}`" class="risk-title-link">{{ risk.RiskDescription }}</router-link>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="no-incident-data">No risks found for selected filters.</div>
    </div>

    <div class="pagination-controls">
      <button class="pagination-btn" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">
        <i class="fas fa-chevron-left pagination-icon"></i> Previous
      </button>
      
      <div class="pagination-numbers">
        <button v-if="showPreviousEllipsis" class="page-number" @click="changePage(1)">1</button>
        <button v-if="showPreviousEllipsis" class="page-number">...</button>
        
        <button 
          v-for="page in displayedPageNumbers" 
          :key="page" 
          @click="changePage(page)" 
          :class="['page-number', currentPage === page ? 'active-page' : '']">
          {{ page }}
        </button>
        
        <button v-if="showNextEllipsis" class="page-number">...</button>
        <button v-if="showNextEllipsis" class="page-number" @click="changePage(totalPages)">{{ totalPages }}</button>
      </div>
      
      <div class="pagination-info">Page {{ currentPage }} of {{ totalPages || 1 }}</div>
      
      <button class="pagination-btn" :disabled="currentPage === totalPages || totalPages === 0" @click="changePage(currentPage + 1)">
        Next <i class="fas fa-chevron-right pagination-icon"></i>
      </button>
    </div>
  </div>
</template>

<script>
import './RiskRegisterList.css'
import axios from 'axios'

export default {
  name: 'RiskRegisterList',
  data() {
    return {
      risks: [],
      selectedCriticality: '',
      selectedCategory: '',
      searchQuery: '',
      currentPage: 1,
      itemsPerPage: 15,
      maxDisplayedPages: 5
    }
  },
  computed: {
    uniqueCriticality() {
      return [...new Set(this.risks.map(i => i.Criticality).filter(Boolean))]
    },
    uniqueCategory() {
      return [...new Set(this.risks.map(i => i.Category).filter(Boolean))]
    },
    filteredRisks() {
      let filtered = this.risks.filter(i =>
        (!this.selectedCriticality || i.Criticality === this.selectedCriticality) &&
        (!this.selectedCategory || i.Category === this.selectedCategory)
      )
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(risk => 
          risk.RiskDescription.toLowerCase().includes(query) ||
          (risk.RiskId && risk.RiskId.toString().includes(query)) ||
          (risk.Origin && risk.Origin.toLowerCase().includes(query)) ||
          (risk.Category && risk.Category.toLowerCase().includes(query))
        )
      }
      
      return filtered
    },
    paginatedRisks() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredRisks.slice(start, end)
    },
    totalPages() {
      return Math.ceil(this.filteredRisks.length / this.itemsPerPage)
    },
    displayedPageNumbers() {
      if (this.totalPages <= this.maxDisplayedPages) {
        return Array.from({ length: this.totalPages }, (_, i) => i + 1)
      }

      let startPage = Math.max(1, this.currentPage - Math.floor(this.maxDisplayedPages / 2))
      let endPage = startPage + this.maxDisplayedPages - 1
      
      if (endPage > this.totalPages) {
        endPage = this.totalPages
        startPage = Math.max(1, endPage - this.maxDisplayedPages + 1)
      }
      
      return Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i)
    },
    showPreviousEllipsis() {
      return this.totalPages > this.maxDisplayedPages && this.displayedPageNumbers[0] > 1
    },
    showNextEllipsis() {
      return this.totalPages > this.maxDisplayedPages && this.displayedPageNumbers[this.displayedPageNumbers.length - 1] < this.totalPages
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
    getCriticalityClass(criticality) {
      if (!criticality) return ''
      criticality = criticality.toLowerCase()
      if (criticality === 'critical') return 'priority-critical'
      if (criticality === 'high') return 'priority-high'
      if (criticality === 'medium') return 'priority-medium'
      if (criticality === 'low') return 'priority-low'
      return ''
    },
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
    }
  }
}
</script> 