<template>
    <div class="incident-view-container">
      <div class="incident-view-header">
        <h2 class="incident-view-title">Incident Management</h2>
        <button @click="toggleView" class="view-toggle-btn" :title="isCardView ? 'Switch to Checklist View' : 'Switch to Card View'">
          <span v-if="isCardView" class="table-icon">📋</span>
          <span v-else class="card-icon">🗂️</span>
        </button>
      </div>
      <div class="incident-list-wrapper">
        <div class="incident-filter-controls">
          <div class="filter-group">
            <div class="search-container">
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Search incidents..." 
                class="incident-search-input"
                @input="filterIncidents"
              />
              <span class="search-icon">🔍</span>
            </div>
            <div class="sort-filter">
              <select v-model="sortField" @change="sortIncidents" class="sort-select">
                <option value="">Sort by</option>
                <option value="IncidentId">ID</option>
                <option value="IncidentTitle">Title</option>
                <option value="Date">Date</option>
                <option value="RiskPriority">Priority</option>
                <option value="RiskCategory">Category</option>
              </select>
              <button @click="toggleSortOrder" class="sort-direction-btn">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Checklist View -->
        <div v-if="!isCardView" class="incident-checklist-container">
          <div v-if="paginatedIncidents.length === 0" class="no-incidents-message">
            No incidents found. Create your first incident.
          </div>
          
          <div v-for="incident in paginatedIncidents" :key="incident.IncidentId" class="incident-checklist-item">
            <div class="checklist-checkbox">
              <input type="checkbox" :id="'incident-' + incident.IncidentId" />
              <label :for="'incident-' + incident.IncidentId"></label>
            </div>
            
            <div class="checklist-content">
              <div class="checklist-header">
                <div class="checklist-title-container">
                  <div class="checklist-id-badge">
                    #{{ incident.IncidentId }}
                  </div>
                  <h3 class="checklist-title">{{ incident.IncidentTitle }}</h3>
                  
                  <div class="checklist-category-badge" :class="getRiskCategoryClass(incident.RiskCategory)">
                    {{ incident.RiskCategory }}
                  </div>
                </div>
                
                <div class="checklist-meta">
                  <div class="checklist-status" :class="getSolvedStatusClass(incident)">
                    <span class="status-indicator"></span>
                    <span class="status-text">{{ getIncidentStatusDisplay(incident) }}</span>
                  </div>
                  
                  <div class="checklist-date-time">
                    <div class="date-time-container">
                      <span class="date-icon">📅</span>
                      <span class="date">{{ formatDate(incident.Date) }}</span>
                    </div>
                    <div class="date-time-container">
                      <span class="time-icon">⏱️</span>
                      <span class="time">{{ incident.Time }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="checklist-details">
                <div class="details-row description-row">
                  <span class="detail-label">Description:</span>
                  <span class="detail-value">{{ incident.Description }}</span>
                </div>
                
                <div class="details-grid">
                  <div class="details-item">
                    <h4 class="details-header">
                      <span class="details-icon">💬</span> Comments
                    </h4>
                    <div class="details-content">{{ incident.Comments || 'No comments' }}</div>
                  </div>
                  
                  <div class="details-item">
                    <h4 class="details-header">
                      <span class="details-icon">🛡️</span> Mitigation
                    </h4>
                    <div class="details-content">{{ incident.Mitigation || 'No mitigation plan' }}</div>
                  </div>
                </div>
                
                <div class="details-footer">
                  <div class="origin-container">
                    <span class="detail-label">Origin:</span>
                    <span class="origin-badge" :class="getOriginClass(incident.Origin)">{{ incident.Origin }}</span>
                  </div>
                  
                  <div v-if="incident.Attachments" class="files-container">
                    <a class="file-link" :href="incident.Attachments" target="_blank">
                      <span class="file-icon">📎</span>
                      View Files
                    </a>
                  </div>
                  
                  <div class="action-buttons">
                    <button 
                      @click="openSolveModal(incident)" 
                      class="solve-btn"
                      :disabled="isIncidentSolved(incident.IncidentId)"
                      :class="{ 'disabled': isIncidentSolved(incident.IncidentId) }"
                    >
                      Solve
                    </button>
                    <button 
                      @click="openRejectModal(incident)" 
                      class="no-btn"
                      :disabled="isIncidentSolved(incident.IncidentId)"
                      :class="{ 'disabled': isIncidentSolved(incident.IncidentId) }"
                    >
                      No
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Card View -->
        <div v-else class="incident-cards-container">
          <div v-if="paginatedIncidents.length === 0" class="no-incidents-message">
            No incidents found. Create your first incident.
          </div>
          
          <div v-for="incident in paginatedIncidents" :key="incident.IncidentId" class="incident-card">
            <div class="incident-card-badge" :class="getOriginClass(incident.Origin)">
              {{ incident.Origin }}
            </div>
            <h3 class="incident-card-title">{{ incident.IncidentTitle }}</h3>
            <p class="incident-card-description">{{ incident.Description }}</p>
            
            <div class="incident-card-details">
              <div class="incident-card-priority">
                <span class="priority-label">Status:</span>
                <span :class="getSolvedStatusClass(incident)">{{ getIncidentStatusDisplay(incident) }}</span>
              </div>
              <div class="incident-card-category">
                <span class="category-badge" :class="getRiskCategoryClass(incident.RiskCategory)">
                  {{ incident.RiskCategory }}
                </span>
              </div>
            </div>
            
            <div class="incident-card-section incident-card-comments">
              <div class="section-header">Comments</div>
              <div class="section-content">{{ incident.Comments || 'No comments' }}</div>
            </div>
            
            <div class="incident-card-section incident-card-mitigation">
              <div class="section-header">Mitigation</div>
              <div class="section-content">{{ incident.Mitigation || 'No mitigation plan' }}</div>
            </div>
            
            <div class="incident-card-meta">
              <div class="incident-card-date">
                <span class="calendar-icon">📅</span>
                <span>{{ formatDate(incident.Date) }}</span>
              </div>
              <div class="incident-card-id">#{{ incident.IncidentId }}</div>
            </div>
            
            <div class="incident-card-footer">
              <div class="action-buttons">
                <button 
                  @click="openSolveModal(incident)" 
                  class="solve-btn"
                  :disabled="isIncidentSolved(incident.IncidentId)"
                  :class="{ 'disabled': isIncidentSolved(incident.IncidentId) }"
                >
                  Solve
                </button>
                <button 
                  @click="openRejectModal(incident)" 
                  class="no-btn"
                  :disabled="isIncidentSolved(incident.IncidentId)"
                  :class="{ 'disabled': isIncidentSolved(incident.IncidentId) }"
                >
                  No
                </button>
              </div>
              
              <a v-if="incident.Attachments" class="incident-card-attachment" :href="incident.Attachments" target="_blank">
                <span>📎</span> View Attachments
              </a>
            </div>
          </div>
        </div>
        
        <!-- Pagination controls -->
        <div v-if="filteredIncidents.length > 0" class="pagination-controls">
          <button 
            @click="changePage(currentPage - 1)" 
            :disabled="currentPage === 1"
            class="pagination-btn prev-btn"
          >
            <span class="pagination-icon">«</span> Previous
          </button>
          
          <div class="pagination-numbers">
            <button 
              v-for="page in pageNumbers" 
              :key="page" 
              @click="changePage(page)"
              :class="['page-number', currentPage === page ? 'active-page' : '']"
            >
              {{ page }}
            </button>
          </div>
          
          <div class="pagination-info">
            Page {{ currentPage }} of {{ totalPages }}
          </div>
          
          <button 
            @click="changePage(currentPage + 1)" 
            :disabled="currentPage === totalPages"
            class="pagination-btn next-btn"
          >
            Next <span class="pagination-icon">»</span>
          </button>
        </div>
      </div>
      
      <!-- Modal for Solve/No Actions -->
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-container" @click.stop>
          <button class="modal-close-btn" @click="closeModal">✕</button>
          <div class="modal-content">
            <div v-if="modalAction === 'solve'" class="solve-container">
              <div class="solve-icon">🔄</div>
              <h3 class="modal-title solve">Forwarded to Risk</h3>
              <p class="solve-message">You will be directed to the Risk module</p>
              
              <!-- Add confirmation buttons -->
              <div class="modal-footer">
                <button @click="confirmSolve" class="confirm-btn">Confirm Forward</button>
                <button @click="closeModal" class="cancel-btn">Cancel</button>
              </div>
            </div>
            
            <div v-else-if="modalAction === 'reject'" class="rejected-container">
              <div class="rejected-icon">✕</div>
              <h3 class="modal-title rejected">Rejected</h3>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import './Incident.css';

  export default {
    name: 'IncidentManagement',
    data() {
      return {
        incidents: [],
        filteredIncidents: [],
        searchQuery: '',
        sortField: '',
        sortOrder: 'asc',
        currentPage: 1,
        incidentsPerPage: 10,
        isCardView: false,
        showModal: false,
        modalAction: '', // 'solve' or 'reject'
        selectedIncident: null,
        solvedIncidents: new Set() // Track solved incidents
      }
    },
    computed: {
      totalPages() {
        return Math.ceil(this.filteredIncidents.length / this.incidentsPerPage);
      },
      paginatedIncidents() {
        const startIndex = (this.currentPage - 1) * this.incidentsPerPage;
        const endIndex = startIndex + this.incidentsPerPage;
        return this.filteredIncidents.slice(startIndex, endIndex);
      },
      pageNumbers() {
        const pages = [];
        // Show max 5 page numbers
        let startPage = Math.max(1, this.currentPage - 2);
        let endPage = Math.min(this.totalPages, startPage + 4);
        
        // Adjust if we're near the end
        if (endPage - startPage < 4 && this.totalPages > 5) {
          startPage = Math.max(1, endPage - 4);
        }
        
        for (let i = startPage; i <= endPage; i++) {
          pages.push(i);
        }
        
        return pages;
      }
    },
    mounted() {
      this.loadSolvedIncidents(); // Load saved solved incidents
      this.fetchIncidents();
      // Ensure the main document scrolls to see all checklist data
      document.documentElement.style.overflow = 'auto';
      document.body.style.overflow = 'auto';
      
      // Add resize event listener to handle responsive behavior
      window.addEventListener('resize', this.handleResize);
    },
    beforeUnmount() {
      // Clean up event listener
      window.removeEventListener('resize', this.handleResize);
    },
    methods: {
      toggleView() {
        this.isCardView = !this.isCardView;
      },
      openSolveModal(incident) {
        // Don't open modal if incident is already solved
        if (this.isIncidentSolved(incident.IncidentId)) {
          return;
        }
        this.selectedIncident = incident;
        this.modalAction = 'solve';
        this.showModal = true;
      },
      openRejectModal(incident) {
        // Don't open modal if incident is already solved
        if (this.isIncidentSolved(incident.IncidentId)) {
          return;
        }
        this.selectedIncident = incident;
        this.modalAction = 'reject';
        this.showModal = true;
      },
      closeModal() {
        this.showModal = false;
        this.selectedIncident = null;
      },
      confirmSolve() {
        if (this.selectedIncident) {
          // Add incident to solved incidents set
          this.solvedIncidents.add(this.selectedIncident.IncidentId);
          
          // Save to localStorage immediately
          this.saveSolvedIncidents();
          
          console.log('Solving incident:', this.selectedIncident);
          
          // Auto close the modal after 2 seconds and show success
          setTimeout(() => {
            this.closeModal();
          }, 2000);
        }
      },
      confirmReject() {
        // Handle the rejection action
        console.log('Rejecting incident:', this.selectedIncident);
        
        // Auto close the modal after 2 seconds
        setTimeout(() => {
          this.closeModal();
        }, 2000);
      },
      getRiskCategoryClass(category) {
        if (!category) return '';
        const categoryLower = category.toLowerCase();
        if (categoryLower.includes('security')) return 'category-security';
        if (categoryLower.includes('compliance')) return 'category-compliance';
        if (categoryLower.includes('operational')) return 'category-operational';
        if (categoryLower.includes('financial')) return 'category-financial';
        if (categoryLower.includes('strategic')) return 'category-strategic';
        return 'category-other';
      },
      changePage(page) {
        if (page >= 1 && page <= this.totalPages) {
          this.currentPage = page;
          // Scroll to top of container when changing pages
          const container = document.querySelector('.incident-list-wrapper');
          if (container) {
            container.scrollTop = 0;
            window.scrollTo({ top: container.offsetTop, behavior: 'smooth' });
          }
        }
      },
      getStatusClass(priority) {
        const priorityLower = priority?.toLowerCase() || '';
        if (priorityLower === 'high') return 'status-active';
        if (priorityLower === 'medium') return 'status-medium';
        if (priorityLower === 'low') return 'status-inactive';
        return 'status-default';
      },
      getOriginClass(origin) {
        const originType = origin?.toLowerCase() || '';
        if (originType.includes('manual')) return 'origin-manual';
        if (originType.includes('audit')) return 'origin-audit';
        if (originType.includes('siem')) return 'origin-siem';
        return 'origin-other';
      },
      async fetchIncidents() {
        try {
          const response = await axios.get('http://localhost:8000/incidents/');
          this.incidents = response.data;
          this.filteredIncidents = [...this.incidents];
          console.log('Fetched incidents:', this.incidents);
          
          // Reset to first page when data is loaded
          this.currentPage = 1;
          
          // Force re-render after data is loaded to ensure proper layout
          this.$nextTick(() => {
            this.handleResize();
          });
        } catch (error) {
          console.error('Failed to fetch incidents:', error);
        }
      },
      filterIncidents() {
        if (!this.searchQuery.trim()) {
          this.filteredIncidents = [...this.incidents];
        } else {
          const query = this.searchQuery.toLowerCase();
          this.filteredIncidents = this.incidents.filter(incident => {
            return (
              (incident.IncidentId && incident.IncidentId.toString().includes(query)) ||
              (incident.IncidentTitle && incident.IncidentTitle.toLowerCase().includes(query)) ||
              (incident.Description && incident.Description.toLowerCase().includes(query)) ||
              (incident.RiskCategory && incident.RiskCategory.toLowerCase().includes(query)) ||
              (incident.RiskPriority && incident.RiskPriority.toLowerCase().includes(query)) ||
              (incident.Origin && incident.Origin.toLowerCase().includes(query))
            );
          });
        }
        
        // Reset to first page when filtering changes
        this.currentPage = 1;
        
        this.applySorting();
      },
      sortIncidents() {
        this.applySorting();
      },
      applySorting() {
        if (this.sortField) {
          this.filteredIncidents.sort((a, b) => {
            let valueA = a[this.sortField];
            let valueB = b[this.sortField];
            
            // Handle date sorting specially
            if (this.sortField === 'Date') {
              valueA = valueA ? new Date(valueA) : new Date(0);
              valueB = valueB ? new Date(valueB) : new Date(0);
            } else {
              // Handle string and number comparisons
              valueA = valueA !== undefined && valueA !== null ? valueA.toString().toLowerCase() : '';
              valueB = valueB !== undefined && valueB !== null ? valueB.toString().toLowerCase() : '';
            }
            
            if (this.sortOrder === 'asc') {
              return valueA > valueB ? 1 : valueA < valueB ? -1 : 0;
            } else {
              return valueA < valueB ? 1 : valueA > valueB ? -1 : 0;
            }
          });
        }
      },
      toggleSortOrder() {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
        this.applySorting();
      },
      handleResize() {
        // Update layout when window is resized
        const wrapper = document.querySelector('.incident-list-wrapper');
        if (wrapper) {
          wrapper.style.maxWidth = '100%';
        }
      },
      getPriorityClass(priority) {
        switch(priority?.toLowerCase()) {
          case 'high':
            return 'priority-high';
          case 'medium':
            return 'priority-medium';
          case 'low':
            return 'priority-low';
          default:
            return '';
        }
      },
      formatDate(dateString) {
        if (!dateString) return '';
        
        const [year, month, day] = dateString.split('-');
        return `${month}/${day}/${year}`;
      },
      // Add method to check if incident is solved
      isIncidentSolved(incidentId) {
        return this.solvedIncidents.has(incidentId);
      },
      
      // Add method to get incident status display
      getIncidentStatusDisplay(incident) {
        if (this.isIncidentSolved(incident.IncidentId)) {
          return 'Risk is forwarded to mitigated';
        }
        return incident.RiskPriority;
      },
      
      // Add method to get status class for solved incidents
      getSolvedStatusClass(incident) {
        if (this.isIncidentSolved(incident.IncidentId)) {
          return 'status-solved';
        }
        return this.getStatusClass(incident.RiskPriority);
      },
      
      // Load solved incidents from localStorage
      loadSolvedIncidents() {
        try {
          const saved = localStorage.getItem('solvedIncidents');
          if (saved) {
            const solvedArray = JSON.parse(saved);
            this.solvedIncidents = new Set(solvedArray);
            console.log('Loaded solved incidents:', solvedArray);
          }
        } catch (error) {
          console.error('Error loading solved incidents:', error);
          this.solvedIncidents = new Set();
        }
      },
      
      // Save solved incidents to localStorage
      saveSolvedIncidents() {
        try {
          const solvedArray = Array.from(this.solvedIncidents);
          localStorage.setItem('solvedIncidents', JSON.stringify(solvedArray));
          console.log('Saved solved incidents:', solvedArray);
        } catch (error) {
          console.error('Error saving solved incidents:', error);
        }
      },
      
      // Optional: Add method to clear solved incidents (for testing)
      clearSolvedIncidents() {
        this.solvedIncidents.clear();
        localStorage.removeItem('solvedIncidents');
        console.log('Cleared all solved incidents');
      }
    }
  }
  </script>
  