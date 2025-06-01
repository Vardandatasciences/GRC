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
            <div class="export-controls">
              <select v-model="exportFormat" class="export-format-select">
                <option value="xlsx">Excel (.xlsx)</option>
                <option value="csv">CSV (.csv)</option>
                <option value="pdf">PDF (.pdf)</option>
                <option value="json">JSON (.json)</option>
                <option value="xml">XML (.xml)</option>
                <option value="txt">Text (.txt)</option>
              </select>
              <button 
                @click="exportIncidents" 
                class="export-btn"
                :disabled="isExporting"
              >
                <span v-if="isExporting">Exporting...</span>
                <span v-else>Export</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Checklist View -->
        <div v-if="!isCardView" class="incident-checklist-container">
          <div class="checklist-header-row">
            <div class="incident-id-header">ID</div>
            <div class="incident-title-header">Title</div>
            <div class="incident-priority-header">Priority</div>
            <div class="incident-date-header">Date</div>
            <div class="incident-actions-header">Actions</div>
          </div>

          <div v-if="paginatedIncidents.length === 0" class="no-incidents-message">
            No incidents found. Create your first incident.
          </div>
          
          <div class="incident-checklist-item" v-for="incident in paginatedIncidents" :key="incident.IncidentId">
            <div class="incident-id">{{ incident.IncidentId }}</div>
            <div class="incident-title">
              <router-link :to="`/incident/${incident.IncidentId}`" class="incident-title-link">
                {{ incident.IncidentTitle }}
              </router-link>
            </div>
            <div class="incident-priority">
              <span :class="['priority-badge', getPriorityClass(incident.RiskPriority)]">
                {{ incident.RiskPriority }}
              </span>
            </div>
            <div class="incident-date">{{ formatDate(incident.Date) }}</div>
            <div class="incident-actions">
              <div v-if="incident.Status === 'Scheduled'">
                <span class="status-badge scheduled">Mitigated to Risk</span>
              </div>
              <div v-else-if="incident.Status === 'Rejected'">
                <span class="status-badge rejected">Rejected</span>
              </div>
              <div v-else>
                <button @click="openSolveModal(incident)" class="solve-btn">ESCALATE TO RISK</button>
                <button @click="openRejectModal(incident)" class="no-btn">REJECT INCIDENT</button>
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
            <h3 class="incident-card-title">
              <router-link :to="`/incident/${incident.IncidentId}`" class="incident-title-link">
                {{ incident.IncidentTitle }}
              </router-link>
            </h3>
            <p class="incident-card-description">{{ incident.Description }}</p>
            
            <div class="incident-card-details">
              <div class="incident-card-priority">
                <span class="priority-label">Priority:</span>
                <span :class="getPriorityClass(incident.RiskPriority)">{{ incident.RiskPriority }}</span>
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
                <div v-if="incident.Status === 'Scheduled'">
                  <span class="status-badge scheduled">Mitigated to Risk</span>
                </div>
                <div v-else-if="incident.Status === 'Rejected'">
                  <span class="status-badge rejected">Rejected</span>
                </div>
                <div v-else>
                  <button @click="openSolveModal(incident)" class="solve-btn">
                    ESCALATE TO RISK
                  </button>
                  <button @click="openRejectModal(incident)" class="no-btn">
                    REJECT INCIDENT
                  </button>
                </div>
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
              <p class="modal-subtitle">You will be directed to the Risk module</p>
              <div class="modal-footer">
                <button @click="confirmSolve" class="modal-btn confirm-btn">Confirm Forward</button>
                <button @click="closeModal" class="modal-btn cancel-btn">Cancel</button>
              </div>
            </div>
            
            <div v-else-if="modalAction === 'reject'" class="rejected-container">
              <div class="rejected-icon">✕</div>
              <h3 class="modal-title rejected">REJECTED</h3>
              <div class="modal-footer">
                <button @click="confirmReject" class="modal-btn reject-btn">Confirm Reject</button>
                <button @click="closeModal" class="modal-btn cancel-btn">Cancel</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Add export success notification -->
      <div v-if="showExportSuccess" class="export-success-notification">
        <div class="notification-content">
          <span class="success-icon">✓</span>
          <div class="notification-message">
            <p>Export successful!</p>
            <a :href="exportFileUrl" target="_blank" class="download-link">Download {{ exportFileName }}</a>
          </div>
          <button @click="showExportSuccess = false" class="close-notification-btn">✕</button>
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
        showIncidentDetails: false,
        exportFormat: 'xlsx',
        isExporting: false,
        showExportSuccess: false,
        exportFileUrl: '',
        exportFileName: ''
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
        this.selectedIncident = incident;
        this.modalAction = 'solve';
        this.showModal = true;
      },
      openRejectModal(incident) {
        this.selectedIncident = incident;
        this.modalAction = 'reject';
        this.showModal = true;
      },
      closeModal() {
        this.showModal = false;
        this.selectedIncident = null;
      },
      confirmSolve() {
        // Update incident status to "Scheduled"
        axios.put(`http://localhost:8000/incidents/${this.selectedIncident.IncidentId}/status/`, {
          status: 'Scheduled'
        })
        .then(response => {
          console.log('Incident escalated to risk:', response.data);
          // Refresh incidents list after status update
          this.fetchIncidents();
          
          // Auto close and redirect after 2 seconds
          setTimeout(() => {
            this.closeModal();
            // Redirect to Risk module
            // this.$router.push('/risk');
          }, 2000);
        })
        .catch(error => {
          console.error('Error updating incident status:', error);
        });
      },
      confirmReject() {
        // Update incident status to "Rejected"
        axios.put(`http://localhost:8000/incidents/${this.selectedIncident.IncidentId}/status/`, {
          status: 'Rejected'
        })
        .then(response => {
          console.log('Incident rejected:', response.data);
          // Refresh incidents list after status update
          this.fetchIncidents();
          
          // Auto close the modal after 2 seconds
          setTimeout(() => {
            this.closeModal();
          }, 2000);
        })
        .catch(error => {
          console.error('Error updating incident status:', error);
        });
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
      closeIncidentDetails() {
        this.selectedIncident = null;
        this.showIncidentDetails = false;
      },
      async exportIncidents() {
        try {
          this.isExporting = true;
          
          const response = await axios.post('http://localhost:8000/api/incidents/export/', {
            file_format: this.exportFormat,
            user_id: 'user123', // Ideally, use a logged-in user's ID
            timeRange: 'all', // You can extend this to use your filters
            category: 'all',
            priority: 'all'
          });
          
          console.log('Export response:', response.data);
          
          if (response.data.success) {
            this.exportFileUrl = response.data.file_url;
            this.exportFileName = response.data.file_name;
            this.showExportSuccessMessage();
            
            // Auto-download the file
            const link = document.createElement('a');
            link.href = response.data.file_url;
            link.download = response.data.file_name;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          }
        } catch (error) {
          console.error('Error exporting incidents:', error);
          alert('Failed to export incidents. Please try again.');
        } finally {
          this.isExporting = false;
        }
      },
      
      showExportSuccessMessage() {
        this.showExportSuccess = true;
        // Auto-hide the notification after 5 seconds
        setTimeout(() => {
          this.showExportSuccess = false;
        }, 5000);
      }
    }
  }
  </script>
  