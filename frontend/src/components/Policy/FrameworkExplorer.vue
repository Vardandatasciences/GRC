<template>
  <div class="framework-explorer-container">
    <div class="summary-cards">
      <div class="summary-card active-framework" @click="filterByStatus('Active', 'framework')">
        <div class="summary-icon-wrapper">
          <i class="fas fa-shield-alt"></i>
        </div>
        <div>Active Framework</div>
        <span class="summary-value">{{ summary.active_frameworks }}</span>
      </div>
      <div class="summary-card inactive-framework" @click="filterByStatus('Inactive', 'framework')">
        <div class="summary-icon-wrapper">
          <i class="fas fa-shield"></i>
        </div>
        <div>Inactive Framework</div>
        <span class="summary-value">{{ summary.inactive_frameworks }}</span>
      </div>
      <div class="summary-card active-policy" @click="filterByStatus('Active', 'policy')">
        <div class="summary-icon-wrapper">
          <i class="fas fa-file-circle-check"></i>
        </div>
        <div>Active Policy</div>
        <span class="summary-value">{{ summary.active_policies }}</span>
      </div>
      <div class="summary-card inactive-policy" @click="filterByStatus('Inactive', 'policy')">
        <div class="summary-icon-wrapper">
          <i class="fas fa-file-circle-xmark"></i>
        </div>
        <div>Inactive Policy</div>
        <span class="summary-value">{{ summary.inactive_policies }}</span>
      </div>
    </div>
    <div class="top-controls">
      <div class="framework-dropdown-section">
        <label>Framework</label>
        <select v-model="selectedFrameworkId" class="framework-dropdown">
          <option value="">Select Framework</option>
          <option v-for="fw in frameworks" :key="fw.id" :value="fw.id">{{ fw.name }}</option>
        </select>
      </div>
      <div v-if="activeFilter" class="active-filter">
        <span>Filtered by: {{ activeFilter }}</span>
        <button class="clear-filter-btn" @click="clearFilter">Clear Filter</button>
      </div>
    </div>
    <div class="export-controls">
      <div class="export-controls-inner">
        <select v-model="selectedExportFormat" class="export-dropdown">
          <option value="" disabled>Select format</option>
          <option value="xlsx">Excel (.xlsx)</option>
          <option value="pdf">PDF (.pdf)</option>
          <option value="csv">CSV (.csv)</option>
          <option value="json">JSON (.json)</option>
          <option value="xml">XML (.xml)</option>
          <option value="txt">Text (.txt)</option>
        </select>
        <button @click="exportFrameworkPolicies" :disabled="!selectedExportFormat || !selectedFrameworkId">
          Export
        </button>
      </div>
    </div>
    <div class="framework-card-grid">
      <div v-for="fw in filteredFrameworks" :key="fw.id" class="framework-card" @click="goToPolicies(fw.id)">
        <div class="framework-card-header">
          <div class="framework-title-section">
            <span class="framework-icon">
              <i class="fas fa-book"></i>
            </span>
            <span class="framework-card-title">{{ fw.name }}</span>
          </div>
          <span class="framework-card-status" :class="fw.status.toLowerCase()">{{ fw.status }}</span>
        </div>
        <div class="framework-card-category">Category: {{ fw.category }}</div>
        <div class="framework-card-desc">{{ fw.description }}</div>
        <div class="framework-card-actions">
          <div class="action-buttons">
            <button @click.stop="toggleStatus(fw)">
              {{ fw.status === 'Active' ? 'Inactive' : 'Active' }}
            </button>
          </div>
          <span class="document-icon" @click.stop="showFrameworkDetails(fw.id)">
            <i class="fas fa-file-alt"></i>
          </span>
        </div>
      </div>
    </div>

    <!-- Framework Details Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close-btn" @click="closeModal">&times;</button>
        <div class="modal-header">
          <h3>Framework Details</h3>
        </div>
        <div v-if="isLoadingDetails" class="modal-loading">
          <i class="fas fa-spinner fa-spin"></i> Loading details...
        </div>
        <div v-else-if="frameworkDetails" class="modal-body">
          <div class="framework-details">
            <div class="detail-row">
              <span class="detail-label">Framework Name:</span>
              <span class="detail-value">{{ frameworkDetails.FrameworkName }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Description:</span>
              <span class="detail-value">{{ frameworkDetails.FrameworkDescription }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Category:</span>
              <span class="detail-value">{{ frameworkDetails.Category }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Version:</span>
              <span class="detail-value">{{ frameworkDetails.CurrentVersion }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Status:</span>
              <span class="detail-value">{{ frameworkDetails.Status }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Active/Inactive:</span>
              <span class="detail-value">{{ frameworkDetails.ActiveInactive }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Identifier:</span>
              <span class="detail-value">{{ frameworkDetails.Identifier }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Effective Date:</span>
              <span class="detail-value">{{ formatDate(frameworkDetails.EffectiveDate) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Start Date:</span>
              <span class="detail-value">{{ formatDate(frameworkDetails.StartDate) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">End Date:</span>
              <span class="detail-value">{{ formatDate(frameworkDetails.EndDate) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Created By:</span>
              <span class="detail-value">{{ frameworkDetails.CreatedByName }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Created Date:</span>
              <span class="detail-value">{{ formatDate(frameworkDetails.CreatedByDate) }}</span>
            </div>
            <div class="detail-row" v-if="frameworkDetails.DocURL">
              <span class="detail-label">Documentation:</span>
              <a :href="frameworkDetails.DocURL" target="_blank" class="doc-link">View Documentation</a>
            </div>
          </div>
        </div>
        <div v-else class="modal-error">
          Failed to load framework details.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const frameworks = ref([])
const selectedFrameworkId = ref('')
const router = useRouter()
const summary = ref({
  active_frameworks: 0,
  inactive_frameworks: 0,
  active_policies: 0,
  inactive_policies: 0
})
const isLoading = ref(false)
const statusFilter = ref(null)
const typeFilter = ref(null)
const activeFilter = computed(() => {
  if (statusFilter.value && typeFilter.value) {
    return `${statusFilter.value} ${typeFilter.value}s`
  }
  return null
})

// Modal and details states
const showModal = ref(false)
const isLoadingDetails = ref(false)
const frameworkDetails = ref(null)

// Add export controls above the framework grid
const selectedExportFormat = ref('');
const exportFrameworkPolicies = async () => {
  if (!selectedFrameworkId.value || !selectedExportFormat.value) {
    alert('Please select a framework and format.');
    return;
  }
  try {
    const res = await axios.post(`/api/frameworks/${selectedFrameworkId.value}/export/`, {
      format: selectedExportFormat.value
    }, { responseType: 'blob' });
    // Download the file
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `framework_${selectedFrameworkId.value}_policies.${selectedExportFormat.value}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    alert('Export successful!');
  } catch (err) {
    alert('Export failed.');
    console.error(err);
  }
};

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString()
  } catch (e) {
    return dateString
  }
}

// Fetch frameworks from API
const fetchFrameworks = async () => {
  isLoading.value = true
  try {
    const response = await axios.get('/api/framework-explorer/')
    frameworks.value = response.data.frameworks
    summary.value = response.data.summary
  } catch (error) {
    console.error('Error fetching frameworks:', error)
  } finally {
    isLoading.value = false
  }
}

// Show framework details
const showFrameworkDetails = async (frameworkId) => {
  frameworkDetails.value = null
  showModal.value = true
  isLoadingDetails.value = true
  
  try {
    const response = await axios.get(`/api/frameworks/${frameworkId}/details/`)
    frameworkDetails.value = response.data
  } catch (error) {
    console.error('Error fetching framework details:', error)
  } finally {
    isLoadingDetails.value = false
  }
}

// Close the modal
const closeModal = () => {
  showModal.value = false
}

// Filter frameworks by status
const filterByStatus = (status, type) => {
  // Check if we're clicking the same filter that's already active
  if (statusFilter.value === status && typeFilter.value === type) {
    // Clear the filter if it's already active
    clearFilter();
  } else {
    // Apply the new filter
    statusFilter.value = status;
    typeFilter.value = type;
  }
}

// Clear all filters
const clearFilter = () => {
  statusFilter.value = null
  typeFilter.value = null
}

// Toggle framework status
const toggleStatus = async (fw) => {
  try {
    // Call the API to toggle framework status and cascade to policies
    const response = await axios.post(`/api/frameworks/${fw.id}/toggle-status/`, {
      cascadeToApproved: true // Add this flag to indicate we want to cascade the status change
    })
    
    // Update local state
    fw.status = response.data.status
    
    // Show feedback to the user
    let message = `Framework status changed to ${response.data.status}.`;
    
    if (response.data.other_versions_deactivated > 0) {
      message += ` ${response.data.other_versions_deactivated} other version(s) of this framework were automatically deactivated.`;
    }
    
    if (response.data.policies_affected > 0) {
      message += ` ${response.data.policies_affected} approved policies were also ${response.data.status === 'Active' ? 'activated' : 'deactivated'}.`;
    }
    
    if (response.data.subpolicies_affected > 0) {
      message += ` ${response.data.subpolicies_affected} subpolicies belong to affected policies (subpolicy status remains unchanged).`;
    }
    
    alert(message);
    
    // Refresh summary counts
    await fetchFrameworks()
  } catch (error) {
    console.error('Error toggling framework status:', error)
    alert('Failed to update framework status. Please try again.')
  }
}

const filteredFrameworks = computed(() => {
  let result = frameworks.value;
  
  // Apply framework ID filter if selected
  if (selectedFrameworkId.value) {
    result = result.filter(fw => fw.id === parseInt(selectedFrameworkId.value));
    return result;
  }
  
  // Apply status and type filters
  if (statusFilter.value && typeFilter.value) {
    if (typeFilter.value === 'framework') {
      // Filter frameworks by their status
      result = result.filter(fw => fw.status === statusFilter.value);
    } else if (typeFilter.value === 'policy') {
      // Filter frameworks that have active/inactive policies
      if (statusFilter.value === 'Active') {
        result = result.filter(fw => fw.active_policies_count > 0);
      } else {
        result = result.filter(fw => fw.inactive_policies_count > 0);
      }
    }
  }
  
  return result;
})

function goToPolicies(frameworkId) {
  router.push({ name: 'FrameworkPolicies', params: { frameworkId } })
}

// Fetch frameworks on component mount
onMounted(() => {
  fetchFrameworks()
})
</script>

<style scoped>
.framework-explorer-container {
  padding: 32px 40px;
  margin-left: 200px;
  max-width: calc(100vw - 240px);
}
.summary-cards {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
  flex-wrap: wrap;
  width: 100%;
  max-width: 100%;
}
.summary-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f2f2f7;
  border-radius: 18px;
  padding: 24px;
  font-size: 0.9rem;
  font-weight: 600;
  text-align: center;
  min-width: 240px;
  min-height: 160px;
  box-shadow: 0 2px 12px rgba(79,108,255,0.10);
  transition: box-shadow 0.18s, transform 0.18s;
  position: relative;
  cursor: pointer;
}
.summary-card.active-framework {
  background: linear-gradient(135deg, #e8f7ee 60%, #f2f2f7 100%);
}
.summary-card.inactive-framework {
  background: linear-gradient(135deg, #fbeaea 60%, #f2f2f7 100%);
}
.summary-card.active-policy {
  background: linear-gradient(135deg, #e6f7ff 60%, #f2f2f7 100%);
}
.summary-card.inactive-policy {
  background: linear-gradient(135deg, #fffbe6 60%, #f2f2f7 100%);
}
.summary-icon-wrapper {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  font-size: 1.6rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.active-framework .summary-icon-wrapper {
  background: #e8f7ee;
  color: #22a722;
}
.inactive-framework .summary-icon-wrapper {
  background: #fbeaea;
  color: #e53935;
}
.active-policy .summary-icon-wrapper {
  background: #e6f7ff;
  color: #4f6cff;
}
.inactive-policy .summary-icon-wrapper {
  background: #fff5e6;
  color: #f5a623;
}
.summary-card:hover .summary-icon-wrapper {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}
.summary-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(79,108,255,0.15);
}
.summary-value {
  display: block;
  font-size: 1.3rem;
  font-weight: 700;
  margin-top: 12px;
  color: #222;
}
.top-controls {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 24px;
  margin-bottom: 18px;
  width: 100%;
}
.framework-dropdown-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 0;
}
.framework-dropdown {
  min-width: 160px;
  height: 34px;
  border-radius: 8px;
  border: 1.5px solid #e2e8f0;
  font-size: 0.9rem;
  padding: 0 12px;
}
.active-filter {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f0f4ff;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #4f6cff;
}
.clear-filter-btn {
  background: #4f6cff;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.2s;
}
.clear-filter-btn:hover {
  background: #3a57e8;
}
.framework-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  width: 100%;
  margin-top: 24px;
}
.framework-card {
  background: #f7f7fa !important;
  border-radius: 16px !important;
  box-shadow: 0 4px 14px rgba(79,108,255,0.08) !important;
  padding: 24px 20px !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 12px !important;
  position: relative !important;
  font-size: 0.9rem !important;
  cursor: pointer !important;
  transition: box-shadow 0.18s, transform 0.18s !important;
  min-height: 200px !important;
}
.framework-card:hover {
  box-shadow: 0 8px 24px rgba(79,108,255,0.13) !important;
  transform: translateY(-2px) scale(1.025) !important;
}
.framework-card-header {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  font-size: 1.1rem !important;
  font-weight: 700 !important;
  width: 100% !important;
}
.framework-title-section {
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
}
.framework-icon {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 32px !important;
  height: 32px !important;
  background: #e8edfa !important;
  border-radius: 8px !important;
  color: #4f6cff !important;
  font-size: 1rem !important;
}
.framework-card-status {
  padding: 4px 12px !important;
  border-radius: 12px !important;
  font-size: 0.85rem !important;
  background: #f5f5f7 !important;
}
.framework-card-status.active {
  color: #22a722 !important;
  background: #e8f7ee !important;
}
.framework-card-status.inactive {
  color: #e53935 !important;
  background: #fbeaea !important;
}
.framework-card-category {
  font-size: 0.85rem !important;
  color: #4f6cff !important;
  font-weight: 600 !important;
  background: #e8edfa !important;
  border-radius: 8px !important;
  padding: 2px 8px !important;
  width: fit-content !important;
}
.framework-card-desc {
  font-size: 0.9rem !important;
  line-height: 1.5 !important;
  margin-top: 8px !important;
  color: #444 !important;
  font-weight: 400 !important;
  flex-grow: 1;
}
.framework-card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
}
.action-buttons {
  display: flex;
  gap: 8px;
}
button {
  padding: 4px 14px !important;
  border-radius: 8px !important;
  border: none !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  cursor: pointer !important;
  background: #4f6cff !important;
  color: #fff !important;
  transition: background 0.2s !important;
  width: fit-content !important;
}
.document-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #f0f4ff;
  border-radius: 50%;
  color: #4f6cff;
  cursor: pointer;
  transition: all 0.2s ease;
}
.document-icon:hover {
  background: #e0e7ff;
  transform: translateY(-2px);
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  position: relative;
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 5px 30px rgba(0, 0, 0, 0.15);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid #eee;
}
.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.6rem;
  font-weight: 700;
}
.modal-close-btn {
  position: absolute;
  top: 15px;
  right: 20px;
  font-size: 2.2rem;
  font-weight: bold;
  color: #666;
  cursor: pointer;
  transition: color 0.2s;
  background: transparent;
  border: none;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}
.modal-close-btn:hover {
  color: #e53935;
}
.modal-body {
  padding: 25px 30px;
}
.modal-loading, .modal-error {
  padding: 30px;
  text-align: center;
  color: #666;
  font-size: 1.1rem;
}
.detail-row {
  margin-bottom: 18px;
  display: flex;
  flex-wrap: wrap;
}
.detail-label {
  font-weight: 600;
  width: 160px;
  color: #444;
  font-size: 1rem;
  position: relative;
  padding-right: 12px;
}
.detail-label::after {
  content: ":";
  position: absolute;
  right: 4px;
}
.detail-value {
  flex: 1;
  min-width: 200px;
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 500;
}
.doc-link {
  color: #4f6cff;
  text-decoration: none;
  font-weight: 600;
  display: inline-block;
  padding: 6px 12px;
  background: #f0f4ff;
  border-radius: 6px;
  transition: all 0.2s ease;
  font-size: 0.95rem;
}
.doc-link:hover {
  text-decoration: none;
  background: #e0e7ff;
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(79,108,255,0.15);
}
.framework-details {
  margin-top: 10px;
  background: #fcfcff;
  border-radius: 8px;
  padding: 15px;
}
.export-controls {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 18px;
  width: 100%;
}
.export-controls-inner {
  display: flex;
  gap: 10px;
  align-items: center;
}
.export-dropdown {
  min-width: 140px;
  height: 34px;
  border-radius: 8px;
  border: 1.5px solid #e2e8f0;
  font-size: 0.95rem;
  padding: 0 12px;
  background: #fff;
  color: #222;
}
.export-controls button {
  padding: 7px 18px;
  border-radius: 8px;
  border: none;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  background: #4f6cff;
  color: #fff;
  transition: background 0.2s;
}
.export-controls button:disabled {
  background: #bfc8e6;
  cursor: not-allowed;
}
</style> 