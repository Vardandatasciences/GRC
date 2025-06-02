<template>
  <div class="all-compliances-container">
    <h1>Compliance Management</h1>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <span>{{ error }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-spinner">
      <i class="fas fa-circle-notch fa-spin"></i>
      <span>Loading...</span>
    </div>

    <!-- Breadcrumbs -->
    <div class="breadcrumbs" v-if="breadcrumbs.length > 0">
      <div v-for="(crumb, index) in breadcrumbs" :key="crumb.id" class="breadcrumb-chip">
        {{ crumb.name }}
        <span class="breadcrumb-close" @click="goToStep(index)">&times;</span>
      </div>
    </div>

    <!-- Export Section -->
    <div class="export-section">
      <div class="export-dropdown">
        <select v-model="selectedFormat" class="format-select">
          <option value="" disabled>Select Format</option>
          <option value="xlsx">Excel</option>
          <option value="pdf">PDF</option>
          <option value="csv">CSV</option>
          <option value="json">JSON</option>
          <option value="xml">XML</option>
          <option value="txt">Text</option>
        </select>
        <button @click="exportData" class="export-btn" :disabled="!selectedFormat">
          <i class="fas fa-download"></i> Export
        </button>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- Frameworks Section -->
      <template v-if="!selectedFramework">
        <div class="section-header">Frameworks</div>
        <div class="card-grid">
          <div v-for="fw in frameworks" :key="fw.id" class="card" @click="selectFramework(fw)">
            <div class="card-icon">
              <i :class="categoryIcon(fw.category)"></i>
            </div>
            <div class="card-content">
              <div class="card-title">{{ fw.name }}</div>
              <div class="card-category">{{ fw.category }}</div>
              <div class="card-status" :class="statusClass(fw.status)">{{ fw.status }}</div>
              <div class="card-desc">{{ fw.description }}</div>
              <div class="version-info">
                <span>Versions: {{ fw.versions.length }}</span>
                <button class="version-btn" @click.stop="showVersions('framework', fw)">
                  <i class="fas fa-history"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Policies Section -->
      <template v-else-if="selectedFramework && !selectedPolicy">
        <div class="section-header">Policies in {{ selectedFramework.name }}</div>
        <div class="card-grid">
          <div v-for="policy in policies" :key="policy.id" class="card" @click="selectPolicy(policy)">
            <div class="card-icon">
              <i :class="categoryIcon(policy.category)"></i>
            </div>
            <div class="card-content">
              <div class="card-title">{{ policy.name }}</div>
              <div class="card-category">{{ policy.category }}</div>
              <div class="card-status" :class="statusClass(policy.status)">{{ policy.status }}</div>
              <div class="card-desc">{{ policy.description }}</div>
              <div class="version-info">
                <span>Versions: {{ policy.versions.length }}</span>
                <button class="version-btn" @click.stop="showVersions('policy', policy)">
                  <i class="fas fa-history"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Subpolicies Section -->
      <template v-else-if="selectedPolicy && !selectedSubpolicy">
        <div class="section-header">Subpolicies in {{ selectedPolicy.name }}</div>
        <div class="card-grid">
          <div v-for="subpolicy in subpolicies" :key="subpolicy.id" class="card" @click="selectSubpolicy(subpolicy)">
            <div class="card-icon">
              <i :class="categoryIcon(subpolicy.category)"></i>
            </div>
            <div class="card-content">
              <div class="card-title">{{ subpolicy.name }}</div>
              <div class="card-category">{{ subpolicy.category }}</div>
              <div class="card-status" :class="statusClass(subpolicy.status)">{{ subpolicy.status }}</div>
              <div class="card-desc">{{ subpolicy.description }}</div>
              <div class="card-metadata">
                <span>Control: {{ subpolicy.control }}</span>
                <span>{{ subpolicy.permanent_temporary }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Compliances Section -->
      <template v-else-if="selectedSubpolicy">
        <div class="section-header">
          <span>Compliances in {{ selectedSubpolicy.name }}</span>
          <div class="section-actions">
            <button class="action-btn" @click="goToStep(2)">
              <i class="fas fa-arrow-left"></i> Back to Subpolicies
            </button>
          </div>
        </div>
        <div v-if="selectedSubpolicy.compliances && selectedSubpolicy.compliances.length === 0" class="no-data">
          <i class="fas fa-inbox"></i>
          <p>No compliances found for this subpolicy</p>
        </div>
        <div v-else class="card-grid">
          <div v-for="compliance in selectedSubpolicy.compliances" :key="compliance.id" class="card" @click="showVersions('compliance', compliance)">
            <div class="card-icon">
              <i :class="compliance.isRisk ? 'fas fa-exclamation-triangle' : 'fas fa-shield-check'"></i>
            </div>
            <div class="card-content">
              <div class="card-header">
                <div class="card-title">{{ compliance.name }}</div>
                <div class="card-badges">
                  <span class="card-status" :class="statusClass(compliance.status)">{{ compliance.status }}</span>
                  <span class="card-status" :class="statusClass(compliance.activeInactive)">{{ compliance.activeInactive }}</span>
                </div>
              </div>
              <div class="card-desc">{{ compliance.description }}</div>
              <div class="compliance-details">
                <div class="detail-group">
                  <span class="detail-label">Maturity Level:</span>
                  <span class="detail-value">{{ compliance.maturityLevel }}</span>
                </div>
                <div class="detail-group">
                  <span class="detail-label">Type:</span>
                  <span class="detail-value">{{ compliance.mandatoryOptional }} | {{ compliance.manualAutomatic }}</span>
                </div>
                <div class="detail-group">
                  <span class="detail-label">Category:</span>
                  <span class="detail-value" :class="'criticality-' + compliance.category.toLowerCase()">
                    {{ compliance.category }}
                  </span>
                </div>
                <div class="detail-group" v-if="compliance.isRisk">
                  <span class="detail-label">Risk Status:</span>
                  <span class="detail-value risk">Risk Identified</span>
                </div>
              </div>
              <div class="compliance-metadata">
                <span>
                  <i class="fas fa-user"></i>
                  {{ compliance.createdBy }}
                </span>
                <span>
                  <i class="fas fa-calendar"></i>
                  {{ formatDate(compliance.createdDate) }}
                </span>
                <span>
                  <i class="fas fa-code-branch"></i>
                  Version {{ compliance.version }}
                </span>
                <span>
                  <i class="fas fa-fingerprint"></i>
                  {{ compliance.identifier }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- Versions Modal -->
    <div v-if="showVersionsModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ versionModalTitle }}</h3>
          <button class="close-btn" @click="closeVersionsModal">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="versions.length === 0" class="no-versions">
            No versions found.
          </div>
          <div v-else class="version-grid">
            <div v-for="version in versions" :key="version.id" class="version-card">
              <div class="version-header">
                <span class="version-number">Version {{ version.version }}</span>
                <div class="version-badges">
                  <span class="status-badge" :class="statusClass(version.status)">{{ version.status }}</span>
                  <span class="status-badge" :class="statusClass(version.activeInactive)">{{ version.activeInactive }}</span>
                </div>
              </div>
              <div class="version-details">
                <p class="version-desc">{{ version.description }}</p>
                <div class="version-info-grid">
                  <div class="info-group">
                    <span class="info-label">Maturity Level:</span>
                    <span class="info-value">{{ version.maturityLevel }}</span>
                  </div>
                  <div class="info-group">
                    <span class="info-label">Type:</span>
                    <span class="info-value">{{ version.mandatoryOptional }} | {{ version.manualAutomatic }}</span>
                  </div>
                  <div class="info-group">
                    <span class="info-label">Criticality:</span>
                    <span class="info-value" :class="'criticality-' + version.criticality.toLowerCase()">
                      {{ version.criticality }}
                    </span>
                  </div>
                  <div class="info-group" v-if="version.isRisk">
                    <span class="info-label">Risk Status:</span>
                    <span class="info-value risk">Risk Identified</span>
                  </div>
                </div>
                <div class="version-metadata">
                  <span>
                    <i class="fas fa-user"></i>
                    {{ version.createdBy }}
                  </span>
                  <span>
                    <i class="fas fa-calendar"></i>
                    {{ formatDate(version.createdDate) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useToast } from "vue-toastification"

// State
const frameworks = ref([])
const selectedFramework = ref(null)
const selectedPolicy = ref(null)
const selectedSubpolicy = ref(null)
const showVersionsModal = ref(false)
const versions = ref([])
const policies = ref([])
const subpolicies = ref([])
const loading = ref(false)
const error = ref(null)
const versionModalTitle = ref('')
const selectedFormat = ref('')

const toast = useToast()

// Computed
const breadcrumbs = computed(() => {
  const arr = []
  if (selectedFramework.value) arr.push({ id: 0, name: selectedFramework.value.name })
  if (selectedPolicy.value) arr.push({ id: 1, name: selectedPolicy.value.name })
  if (selectedSubpolicy.value) arr.push({ id: 2, name: selectedSubpolicy.value.name })
  return arr
})

// Lifecycle
onMounted(async () => {
  try {
    loading.value = true
    // Get all frameworks with their versions
    const response = await axios.get('/api/all-policies/frameworks/')
    if (response.data && Array.isArray(response.data)) {
      frameworks.value = response.data.map(framework => ({
        ...framework,
        versions: framework.versions || [] // Versions should be included in the framework response
      }))
    } else {
      frameworks.value = []
    }
  } catch (err) {
    error.value = 'Failed to load frameworks'
    console.error('Error fetching frameworks:', err)
    frameworks.value = []
  } finally {
    loading.value = false
  }
})

// Methods
async function selectFramework(fw) {
  try {
    loading.value = true
    selectedFramework.value = fw
    selectedPolicy.value = null
    selectedSubpolicy.value = null
    
    // Get active policies for the selected framework using the correct endpoint
    const response = await axios.get('/api/all-policies/policies/', {
      params: { 
        framework_id: fw.id
      }
    })
    
    if (response.data && Array.isArray(response.data)) {
      policies.value = response.data.map(policy => ({
        ...policy,
        versions: policy.versions || [] // Versions count should be included in the response
      }))
    } else {
      policies.value = []
    }
  } catch (err) {
    error.value = 'Failed to load policies'
    console.error('Error fetching policies:', err)
    policies.value = []
  } finally {
    loading.value = false
  }
}

async function selectPolicy(policy) {
  try {
    loading.value = true
    selectedPolicy.value = policy
    selectedSubpolicy.value = null
    
    // Get active subpolicies for the selected policy using the correct endpoint
    const response = await axios.get('/api/all-policies/subpolicies/', {
      params: { 
        policy_id: policy.id
      }
    })
    
    if (response.data && Array.isArray(response.data)) {
      subpolicies.value = response.data
    } else {
      subpolicies.value = []
    }
  } catch (err) {
    error.value = 'Failed to load subpolicies'
    console.error('Error fetching subpolicies:', err)
    subpolicies.value = []
  } finally {
    loading.value = false
  }
}

async function selectSubpolicy(subpolicy) {
  try {
    loading.value = true
    selectedSubpolicy.value = subpolicy
    
    // Use the correct endpoint for compliances
    const response = await axios.get(`/api/all-policies/subpolicies/${subpolicy.id}/compliances/`)
    
    if (response.data && Array.isArray(response.data)) {
      selectedSubpolicy.value.compliances = response.data.map(compliance => ({
        id: compliance.ComplianceId,
        name: compliance.ComplianceItemDescription,
        status: compliance.Status,
        description: compliance.ComplianceItemDescription,
        category: compliance.Criticality,
        maturityLevel: compliance.MaturityLevel,
        mandatoryOptional: compliance.MandatoryOptional,
        manualAutomatic: compliance.ManualAutomatic,
        createdBy: compliance.CreatedByName,
        createdDate: compliance.CreatedByDate,
        isRisk: compliance.IsRisk,
        activeInactive: compliance.ActiveInactive,
        identifier: compliance.Identifier,
        version: compliance.ComplianceVersion
      }))
    } else {
      selectedSubpolicy.value.compliances = []
    }
  } catch (err) {
    error.value = 'Failed to load compliances'
    console.error('Error fetching compliances:', err)
    selectedSubpolicy.value.compliances = []
  } finally {
    loading.value = false
  }
}

async function showVersions(type, item) {
  try {
    loading.value = true
    let endpoint = ''
    
    switch (type) {
      case 'policy':
        versionModalTitle.value = `Versions of ${item.name}`
        endpoint = `/api/all-policies/policies/${item.id}/versions/`
        break
      case 'compliance':
        versionModalTitle.value = `Versions of Compliance ${item.name}`
        endpoint = `/api/all-policies/compliances/${item.id}/versions/`
        break
    }
    
    const response = await axios.get(endpoint)
    if (response.data && Array.isArray(response.data)) {
      versions.value = response.data.map(version => ({
        id: version.ComplianceId,
        version: version.ComplianceVersion,
        name: version.ComplianceItemDescription,
        status: version.Status,
        description: version.ComplianceItemDescription,
        criticality: version.Criticality,
        maturityLevel: version.MaturityLevel,
        mandatoryOptional: version.MandatoryOptional,
        manualAutomatic: version.ManualAutomatic,
        createdBy: version.CreatedByName,
        createdDate: version.CreatedByDate,
        isRisk: version.IsRisk,
        activeInactive: version.ActiveInactive,
        identifier: version.Identifier
      }))
    } else {
      versions.value = []
    }
    showVersionsModal.value = true
  } catch (err) {
    error.value = `Failed to load ${type} versions`
    console.error(`Error fetching ${type} versions:`, err)
    versions.value = []
  } finally {
    loading.value = false
  }
}

function closeVersionsModal() {
  showVersionsModal.value = false
  versions.value = []
  versionModalTitle.value = ''
}

function goToStep(idx) {
  if (idx <= 0) {
    selectedFramework.value = null
    selectedPolicy.value = null
    selectedSubpolicy.value = null
  } else if (idx === 1) {
    selectedPolicy.value = null
    selectedSubpolicy.value = null
  } else if (idx === 2) {
    selectedSubpolicy.value = null
  }
}

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

function categoryIcon(category) {
  switch ((category || '').toLowerCase()) {
    case 'governance': return 'fas fa-shield-alt'
    case 'access control': return 'fas fa-user-shield'
    case 'asset management': return 'fas fa-boxes'
    case 'cryptography': return 'fas fa-key'
    case 'data management': return 'fas fa-database'
    case 'device management': return 'fas fa-mobile-alt'
    case 'risk management': return 'fas fa-exclamation-triangle'
    case 'supplier management': return 'fas fa-handshake'
    case 'business continuity': return 'fas fa-business-time'
    case 'privacy': return 'fas fa-user-secret'
    case 'system protection': return 'fas fa-shield-virus'
    case 'incident response': return 'fas fa-ambulance'
    default: return 'fas fa-file-alt'
  }
}

function statusClass(status) {
  if (!status) return ''
  const s = status.toLowerCase()
  if (s.includes('active')) return 'active'
  if (s.includes('inactive')) return 'inactive'
  if (s.includes('pending')) return 'pending'
  return ''
}

async function exportData() {
  if (!selectedFormat.value) {
    toast.error('Please select an export format')
    return
  }

  try {
    loading.value = true
    error.value = null

    // Show loading state
    const loadingToast = toast.info('Preparing export...', {
      duration: 0,
      position: 'top-right'
    })

    // Get the current data to export based on the view
    let exportData = {
      framework: selectedFramework.value,
      policy: selectedPolicy.value,
      subpolicy: selectedSubpolicy.value,
      compliances: selectedSubpolicy.value?.compliances || [],
      format: selectedFormat.value,
      user_id: 'user123'
    }

    // Call the new download endpoint
    const response = await axios.post('/export/download/', exportData, {
      responseType: 'blob'
    })

    // Close loading toast
    loadingToast.close()

    // Check if we got data
    if (!response.data || response.data.size === 0) {
      throw new Error('No data received from server')
    }

    // Create a download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    link.setAttribute('download', `compliance_export_${timestamp}.${selectedFormat.value}`)
    link.href = url
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    // Reset the format selection
    selectedFormat.value = ''

    toast.success('Export completed successfully')
  } catch (err) {
    console.error('Export error:', err)
    error.value = 'Failed to export data. Please try again.'
    toast.error(error.value)
  } finally {
    loading.value = false
  }
}
</script>

<style src="./AllCompliance.css"></style>

<style>
/* Toast customization */
.Vue-Toastification__toast {
  padding: 12px 20px !important;
  font-size: 14px !important;
}

.Vue-Toastification__toast--success {
  background-color: #22c55e !important;
}

.Vue-Toastification__toast--error {
  background-color: #ef4444 !important;
}

/* Version grid styles */
.version-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

/* ... rest of your existing styles ... */
</style>