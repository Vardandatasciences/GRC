<template>
  <div class="all-compliances-container">
    <h1>Compliance Audit Status</h1>

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

    <div class="content-wrapper">
      <!-- Frameworks Section -->
      <template v-if="showFrameworks">
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
              <div class="card-actions">
                <button class="action-btn primary" @click.stop="viewAllCompliances('framework', fw.id, fw.name)">
                  <i class="fas fa-list"></i> View All Compliances
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Policies Section -->
      <template v-else-if="showPolicies">
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
              <div class="card-actions">
                <button class="action-btn primary" @click.stop="viewAllCompliances('policy', policy.id, policy.name)">
                  <i class="fas fa-list"></i> View All Compliances
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Subpolicies Section -->
      <template v-else-if="showSubpolicies">
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
              <div class="card-actions">
                <button class="action-btn primary" @click.stop="viewAllCompliances('subpolicy', subpolicy.id, subpolicy.name)">
                  <i class="fas fa-list"></i> View All Compliances
                </button>
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
            <!-- Export Controls for Main View -->
            <div class="inline-export-controls">
              <select v-model="selectedFormat" class="format-select">
                <option value="xlsx">Excel (.xlsx)</option>
                <option value="csv">CSV (.csv)</option>
                <option value="pdf">PDF (.pdf)</option>
                <option value="json">JSON (.json)</option>
                <option value="xml">XML (.xml)</option>
              </select>
              <button class="export-btn" @click="handleExport(selectedFormat)">
                <i class="fas fa-download"></i> Export
              </button>
            </div>
            <button class="view-toggle-btn" @click="toggleViewMode">
              <i :class="viewMode === 'card' ? 'fas fa-list' : 'fas fa-th-large'"></i>
              {{ viewMode === 'card' ? 'List View' : 'Card View' }}
            </button>
            <button class="action-btn" @click="goToStep(2)">
              <i class="fas fa-arrow-left"></i> Back to Subpolicies
            </button>
          </div>
        </div>
        
        <div v-if="loading" class="loading-spinner">
          <i class="fas fa-circle-notch fa-spin"></i>
          <span>Loading compliances...</span>
        </div>
        
        <div v-else-if="!hasCompliances" class="no-data">
          <i class="fas fa-inbox"></i>
          <p>No compliances found for this subpolicy</p>
        </div>
        
        <div v-else-if="filteredCompliances.length === 0" class="no-data">
          <i class="fas fa-filter"></i>
          <p>No approved compliances found for this subpolicy</p>
        </div>
        
        <!-- Card View -->
        <div v-else-if="viewMode === 'card'" class="compliances-grid">
          <div v-for="compliance in filteredCompliances" 
               :key="compliance.id" 
               class="compliance-card">
            <div class="compliance-header">
              <span :class="['criticality-badge', 'criticality-' + compliance.category.toLowerCase()]">
                {{ compliance.category }}
              </span>
            </div>
            
            <div class="compliance-body">
              <h3>{{ compliance.name }}</h3>
              
              <div class="clean-details-grid">
                <div class="fetch-audit-actions" v-if="!complianceAudits[compliance.id]">
                  <button class="fetch-audit-btn" @click="fetchAuditInfo(compliance.id)">
                    <i class="fas fa-sync"></i> Load Compliance Information
                  </button>
                </div>
                
                <div class="detail-row">
                  <span class="detail-label">Compliance Performed By:</span>
                  <span class="detail-value">{{ complianceAudits[compliance.id]?.audit_performer_name || 'N/A' }}</span>
                </div>
                
                <div class="detail-row">
                  <span class="detail-label">Compliance Approved By:</span>
                  <span class="detail-value">{{ complianceAudits[compliance.id]?.audit_approver_name || 'N/A' }}</span>
                </div>
                
                <div class="detail-row">
                  <span class="detail-label">Completion Date:</span>
                  <span class="detail-value">{{ complianceAudits[compliance.id]?.audit_date || 'N/A' }}</span>
                </div>
                
                <div class="detail-row">
                  <span class="detail-label">Completion Status:</span>
                  <span class="detail-value" :class="getAuditStatusClass(complianceAudits[compliance.id]?.audit_findings_status)">
                    <i :class="getAuditStatusIcon(complianceAudits[compliance.id]?.audit_findings_status)"></i>
                    {{ complianceAudits[compliance.id]?.audit_findings_status || 'N/A' }}
                  </span>
                </div>
              </div>
              
              <div class="compliance-footer">
                <div class="identifier">ID: {{ compliance.identifier }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- List View -->
        <div v-else class="compliances-list-view">
          <table class="compliances-table">
            <thead>
              <tr>
                <th>Audit Findings ID</th>
                <th>Compliance</th>
                <th>Criticality</th>
                <th>Completion Status</th>
                <th>Compliance Performed By</th>
                <th>Compliance Approved By</th>
                <th>Completion Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="compliance in filteredCompliances" :key="compliance.id">
                <td class="audit-id">
                  <a 
                    v-if="complianceAudits[compliance.id]?.audit_findings_id" 
                    href="#" 
                    class="audit-id-link"
                    @click.prevent="handleAuditLinkClick(complianceAudits[compliance.id]?.audit_findings_id)">
                    {{ complianceAudits[compliance.id]?.audit_findings_id }}
                  </a>
                  <span v-else>N/A</span>
                </td>
                <td class="compliance-name">{{ compliance.name }}</td>
                <td>
                  <span :class="['criticality-badge', 'criticality-' + compliance.category.toLowerCase()]">
                    {{ compliance.category }}
                  </span>
                </td>
                <td>
                  <span :class="getAuditStatusClass(complianceAudits[compliance.id]?.audit_findings_status)">
                    <i :class="getAuditStatusIcon(complianceAudits[compliance.id]?.audit_findings_status)"></i>
                    {{ complianceAudits[compliance.id]?.audit_findings_status || 'N/A' }}
                  </span>
                </td>
                <td>
                  <span v-if="!complianceAudits[compliance.id]">
                    <button class="mini-fetch-btn" @click="fetchAuditInfo(compliance.id)">
                      <i class="fas fa-sync"></i> Load
                    </button>
                  </span>
                  <span v-else>{{ complianceAudits[compliance.id]?.audit_performer_name || 'N/A' }}</span>
                </td>
                <td>{{ complianceAudits[compliance.id]?.audit_approver_name || 'N/A' }}</td>
                <td>{{ complianceAudits[compliance.id]?.audit_date || 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
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

    <!-- All Compliances Modal -->
    <div class="modal-overlay" v-if="showCompliancesModal">
      <div class="modal-container">
        <div class="modal-header">
          <h2>{{ modalTitle }}</h2>
          <div class="modal-controls">
            <!-- Export Controls for Modal -->
            <div class="inline-export-controls">
              <select v-model="selectedFormat" class="format-select">
                <option value="xlsx">Excel (.xlsx)</option>
                <option value="csv">CSV (.csv)</option>
                <option value="pdf">PDF (.pdf)</option>
                <option value="json">JSON (.json)</option>
                <option value="xml">XML (.xml)</option>
              </select>
              <button class="export-btn" @click="handleModalExport">
              <i class="fas fa-download"></i> Export
            </button>
            </div>
            <button class="view-toggle-btn" @click="toggleModalViewMode">
              <i :class="modalViewMode === 'card' ? 'fas fa-list' : 'fas fa-th-large'"></i>
              {{ modalViewMode === 'card' ? 'List View' : 'Card View' }}
            </button>
            <button class="close-button" @click="closeModal">×</button>
          </div>
          </div>

        <div class="modal-body">
          <!-- Compliances List -->
          <div class="compliances-list">
            <div v-if="loading" class="loading">
              <div class="spinner"></div>
              <p>Loading compliances...</p>
            </div>
            
            <div v-else-if="!compliances.length" class="no-data">
              <i class="fas fa-info-circle"></i>
              <p>No compliances found</p>
            </div>
            
            <div v-else-if="filteredModalCompliances.length === 0" class="no-data">
              <i class="fas fa-filter"></i>
              <p>No approved compliances found</p>
            </div>
            
            <!-- Card View for Modal -->
            <div v-else-if="modalViewMode === 'card'" class="compliances-grid">
              <div v-for="compliance in filteredModalCompliances" 
                   :key="compliance.ComplianceId" 
                   class="compliance-card">
                <div class="compliance-header">
                  <span :class="['criticality-badge', 'criticality-' + compliance.Criticality.toLowerCase()]">
                    {{ compliance.Criticality }}
                  </span>
                </div>
                
                <div class="compliance-body">
                  <h3>{{ compliance.ComplianceItemDescription }}</h3>
                  
                  <div class="compliance-details">
                    <!-- Show only audit information -->
                    <div class="detail-row">
                      <span class="label">Compliance Performed By:</span>
                      <span class="value">{{ getAuditInfoForCompliance(compliance.ComplianceId)?.audit_performer_name || 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="label">Compliance Approved By:</span>
                      <span class="value">{{ getAuditInfoForCompliance(compliance.ComplianceId)?.audit_approver_name || 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="label">Completion Date:</span>
                      <span class="value">{{ getAuditInfoForCompliance(compliance.ComplianceId)?.audit_date || 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="label">Completion Status:</span>
                      <span class="value" :class="getAuditStatusClass(getAuditInfoForCompliance(compliance.ComplianceId)?.audit_findings_status)">
                        <i :class="getAuditStatusIcon(getAuditInfoForCompliance(compliance.ComplianceId)?.audit_findings_status)"></i>
                        {{ getAuditInfoForCompliance(compliance.ComplianceId)?.audit_findings_status || 'N/A' }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="compliance-footer">
                    <div class="identifier">ID: {{ compliance.Identifier }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- List View for Modal -->
            <div v-else class="compliances-list-view">
              <table class="compliances-table">
                <thead>
                  <tr>
                    <th>Audit Findings ID</th>
                    <th>Compliance</th>
                    <th>Criticality</th>
                    <th>Completion Status</th>
                    <th>Compliance Performed By</th>
                    <th>Compliance Approved By</th>
                    <th>Completion Date</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="compliance in filteredModalCompliances" :key="compliance.ComplianceId">
                    <td class="audit-id">
                      <a 
                        v-if="getAuditInfoForCompliance(compliance.ComplianceId)?.audit_findings_id" 
                        href="#" 
                        class="audit-id-link"
                        @click.prevent="handleAuditLinkClick(getAuditInfoForCompliance(compliance.ComplianceId)?.audit_findings_id)">
                        {{ getAuditInfoForCompliance(compliance.ComplianceId)?.audit_findings_id }}
                      </a>
                      <span v-else>N/A</span>
                    </td>
                    <td class="compliance-name">{{ compliance.ComplianceItemDescription }}</td>
                    <td>
                      <span :class="['criticality-badge', 'criticality-' + compliance.Criticality.toLowerCase()]">
                        {{ compliance.Criticality }}
                      </span>
                    </td>
                    <td>
                      <span :class="getAuditStatusClass(getAuditInfoForCompliance(compliance.ComplianceId)?.audit_findings_status)">
                        <i :class="getAuditStatusIcon(getAuditInfoForCompliance(compliance.ComplianceId)?.audit_findings_status)"></i>
                        {{ getAuditInfoForCompliance(compliance.ComplianceId)?.audit_findings_status || 'N/A' }}
                      </span>
                    </td>
                    <td>
                      <span v-if="!getAuditInfoForCompliance(compliance.ComplianceId)">
                        <button class="mini-fetch-btn" @click="fetchModalAuditInfo(compliance.ComplianceId)">
                          <i class="fas fa-sync"></i> Load
                        </button>
                      </span>
                      <span v-else>{{ getAuditInfoForCompliance(compliance.ComplianceId)?.audit_performer_name || 'N/A' }}</span>
                    </td>
                    <td>{{ getAuditInfoForCompliance(compliance.ComplianceId)?.audit_approver_name || 'N/A' }}</td>
                    <td>{{ getAuditInfoForCompliance(compliance.ComplianceId)?.audit_date || 'N/A' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'ComplianceManagement',
  setup() {
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
const showCompliancesModal = ref(false)
const compliances = ref([])
const selectedFormat = ref('xlsx')
const currentItemType = ref(null)
const currentItemId = ref(null)
const currentItemName = ref('')
const isExporting = ref(false)
const exportError = ref(null)
    const complianceAudits = ref({})
const modalComplianceAudits = ref({}) // For storing audit info in modal view
const viewMode = ref('list') // Changed default to 'list' view
const modalViewMode = ref('list') // Changed default to 'list' view

// Computed
const breadcrumbs = computed(() => {
  const arr = []
  if (selectedFramework.value) arr.push({ id: 0, name: selectedFramework.value.name })
  if (selectedPolicy.value) arr.push({ id: 1, name: selectedPolicy.value.name })
  if (selectedSubpolicy.value) arr.push({ id: 2, name: selectedSubpolicy.value.name })
  return arr
})

const modalTitle = computed(() => {
  if (!currentItemName.value) return 'Compliances'
  return `All Compliances - ${currentItemName.value}`
})

const showFrameworks = computed(() => !selectedFramework.value)
const showPolicies = computed(() => selectedFramework.value && !selectedPolicy.value)
const showSubpolicies = computed(() => selectedPolicy.value && !selectedSubpolicy.value)

const hasCompliances = computed(() => {
  return selectedSubpolicy.value && 
         selectedSubpolicy.value.compliances && 
         selectedSubpolicy.value.compliances.length > 0;
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
    loading.value = true;
    selectedSubpolicy.value = subpolicy;
        complianceAudits.value = {}; // Reset audit data
        
        console.log(`Selecting subpolicy: ${subpolicy.id} - ${subpolicy.name}`);
    
    const response = await axios.get(`/api/all-policies/subpolicies/${subpolicy.id}/compliances/`);
    console.log('Subpolicy compliances response:', response.data);
    
    if (response.data && response.data.success) {
          const compliances = response.data.compliances.map(compliance => ({
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
          }));
          
          selectedSubpolicy.value = {
            ...subpolicy,
            compliances: compliances
          };
          
          console.log(`Found ${compliances.length} compliances for subpolicy ${subpolicy.id}`);
          
          // Fetch audit info for each compliance
          if (compliances.length > 0) {
            for (const compliance of compliances) {
              try {
                await fetchAuditInfo(compliance.id);
                // Add a small delay to prevent overwhelming the server
                await new Promise(resolve => setTimeout(resolve, 100));
              } catch (auditErr) {
                console.error(`Error fetching audit info for compliance ${compliance.id}:`, auditErr);
                // Continue with next compliance
              }
            }
            console.log('All audit information fetched:', complianceAudits.value);
          }
    } else {
          selectedSubpolicy.value = {
            ...subpolicy,
            compliances: []
          };
          console.log('No compliances found or API returned error');
    }
  } catch (err) {
    console.error('Error fetching subpolicy compliances:', err);
    error.value = 'Failed to load compliances';
        selectedSubpolicy.value = {
          ...subpolicy,
          compliances: []
        };
  } finally {
    loading.value = false;
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

const viewAllCompliances = async (type, id, name) => {
  try {
        loading.value = true;
    showCompliancesModal.value = true;
    currentItemType.value = type;
    currentItemId.value = id;
    currentItemName.value = name;

    console.log(`Fetching compliances for ${type} with ID ${id}`);
    
    let endpoint = '';
    switch(type) {
      case 'framework':
        endpoint = `/compliances/framework/${id}/`;
        break;
      case 'policy':
        endpoint = `/compliances/policy/${id}/`;
        break;
      case 'subpolicy':
        endpoint = `/compliances/subpolicy/${id}/compliances/`;
        break;
      default:
        throw new Error('Invalid type specified');
    }
    
    const response = await axios.get(endpoint);
    console.log('API Response:', response.data);
    
    if (response.data && response.data.success) {
      compliances.value = response.data.compliances;
    } else {
      throw new Error(response.data.message || 'Failed to fetch compliances');
    }
  } catch (error) {
    console.error('Error fetching compliances:', error);
    compliances.value = [];
    error.value = 'Failed to fetch compliances. Please try again.';
  } finally {
    loading.value = false;
  }
}

async function handleExport(format) {
  try {
    isExporting.value = true;
    exportError.value = null;
    
    let itemType = '';
    let itemId = currentItemId.value;
    
    // Determine the item type
    switch(currentItemType.value) {
      case 'framework':
        itemType = 'framework';
        break;
      case 'policy':
        itemType = 'policy';
        break;
      case 'subpolicy':
        itemType = 'subpolicy';
        break;
      default:
        throw new Error('Invalid export type');
    }
    
    console.log(`Attempting export for ${itemType} ${itemId} in ${format} format`);
    
    // Update the API endpoint URL with path parameters
    const response = await axios({
      url: `/api/export/all-compliances/${format}/${itemType}/${itemId}/`,
      method: 'GET',
      responseType: 'blob',
      timeout: 30000,
      headers: {
        'Accept': 'application/json, application/pdf, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, text/csv, application/xml'
      }
    });

    // Handle successful download
    const contentType = response.headers['content-type'];
    const blob = new Blob([response.data], { type: contentType });
    
    // Get filename from header or create default
    let filename = `compliances_${itemType}_${itemId}.${format}`;
    const disposition = response.headers['content-disposition'];
    if (disposition && disposition.includes('filename=')) {
      filename = disposition.split('filename=')[1].replace(/"/g, '');
    }
    
    // Trigger download
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
    
    ElMessage({
      message: 'Export completed successfully',
      type: 'success',
      duration: 3000
    });
  } catch (error) {
    console.error('Export error:', error);
    const errorMessage = error.response?.data?.message || error.message || 'Failed to export compliances';
    exportError.value = errorMessage;
    ElMessage({
      message: errorMessage,
      type: 'error',
      duration: 5000
    });
  } finally {
    isExporting.value = false;
  }
}

const handleModalExport = () => {
  if (!currentItemType.value || !currentItemId.value) {
    ElMessage({
      message: 'No compliances selected for export',
      type: 'warning',
      duration: 3000
    });
    return;
  }
  handleExport(selectedFormat.value);
}

const closeModal = () => {
  showCompliancesModal.value = false;
  compliances.value = [];
  currentItemType.value = null;
  currentItemId.value = null;
  currentItemName.value = '';
  error.value = null; // Clear any error messages
    }

    async function fetchAuditInfo(complianceId) {
      try {
        console.log(`Fetching audit info for compliance ID: ${complianceId}`);
        
        // Check if we already have this data to avoid unnecessary requests
        if (complianceAudits.value[complianceId] && 
            complianceAudits.value[complianceId].audit_findings_status !== 'Not Audited') {
          console.log(`Using cached audit data for compliance ID: ${complianceId}`);
          return;
        }
        
        // Set a temporary loading state in the audit data
        complianceAudits.value = {
          ...complianceAudits.value,
          [complianceId]: { 
            audit_findings_status: 'Loading...',
            isLoading: true
          }
        };
        
        const response = await axios.get(`/api/compliance/${complianceId}/audit-info/`);
        console.log(`Audit info response for compliance ID ${complianceId}:`, response.data);
        
        if (response.data && response.data.success) {
          complianceAudits.value = {
            ...complianceAudits.value,
            [complianceId]: {
              ...response.data.data,
              isLoading: false
            }
          };
          console.log(`Updated audit data for compliance ID ${complianceId}:`, complianceAudits.value[complianceId]);
        } else {
          throw new Error(response.data.message || 'Failed to fetch audit data');
        }
      } catch (err) {
        console.error(`Error fetching audit info for compliance ${complianceId}:`, err);
        // Set an empty object to prevent repeated requests
        complianceAudits.value = {
          ...complianceAudits.value,
          [complianceId]: { 
            audit_findings_status: 'Not Audited',
            isLoading: false,
            error: err.message
          }
        };
      }
    }

    function getAuditStatusClass(status) {
      if (!status) return 'not-audited';
      
      const statusLower = status.toLowerCase();
      if (statusLower.includes('non') || statusLower.includes('not compliant')) return 'non-compliant';
      if (statusLower.includes('partially')) return 'partially-compliant';
      if (statusLower.includes('fully')) return 'fully-compliant';
      if (statusLower.includes('not applicable')) return 'not-applicable';
      
      return 'not-audited';
    }

    function getAuditStatusIcon(status) {
      if (!status) return 'fas fa-question-circle';
      
      const statusLower = status.toLowerCase();
      if (statusLower.includes('non') || statusLower.includes('not compliant')) return 'fas fa-times-circle';
      if (statusLower.includes('partially')) return 'fas fa-exclamation-circle';
      if (statusLower.includes('fully')) return 'fas fa-check-circle';
      if (statusLower.includes('not applicable')) return 'fas fa-ban';
      
      return 'fas fa-question-circle';
    }

    // Method to get audit info for a compliance in the modal view
    function getAuditInfoForCompliance(complianceId) {
      // Check if we already have this data
      if (modalComplianceAudits.value[complianceId]) {
        return modalComplianceAudits.value[complianceId];
      }
      
      // If not, trigger an async fetch (this won't block rendering)
      fetchModalAuditInfo(complianceId);
      
      // Return undefined for now, the UI will show N/A and update when data arrives
      return undefined;
    }

    // Fetch audit info for modal compliances
    async function fetchModalAuditInfo(complianceId) {
      try {
        // Skip if already loading or loaded
        if (modalComplianceAudits.value[complianceId]) {
          return;
        }
        
        // Set a temporary loading state
        modalComplianceAudits.value = {
          ...modalComplianceAudits.value,
          [complianceId]: { 
            audit_findings_status: 'Loading...',
            isLoading: true
          }
        };
        
        const response = await axios.get(`/api/compliance/${complianceId}/audit-info/`);
        
        if (response.data && response.data.success) {
          modalComplianceAudits.value = {
            ...modalComplianceAudits.value,
            [complianceId]: {
              ...response.data.data,
              isLoading: false
            }
          };
        } else {
          throw new Error(response.data.message || 'Failed to fetch audit data');
        }
      } catch (err) {
        console.error(`Error fetching modal audit info for compliance ${complianceId}:`, err);
        modalComplianceAudits.value = {
          ...modalComplianceAudits.value,
          [complianceId]: { 
            audit_findings_status: 'Not Audited',
            isLoading: false,
            error: err.message
          }
        };
      }
    }

    const toggleViewMode = () => {
      viewMode.value = viewMode.value === 'card' ? 'list' : 'card'
    }

    const toggleModalViewMode = () => {
      modalViewMode.value = modalViewMode.value === 'card' ? 'list' : 'card'
    }

    const filteredCompliances = computed(() => {
      if (!selectedSubpolicy.value || !selectedSubpolicy.value.compliances) return [];
      return selectedSubpolicy.value.compliances.filter(compliance => compliance.status === 'Approved');
    });

    const filteredModalCompliances = computed(() => {
      if (!compliances.value) return [];
      return compliances.value.filter(compliance => compliance.Status === 'Approved');
    });

    return {
      frameworks,
      selectedFramework,
      selectedPolicy,
      selectedSubpolicy,
      showVersionsModal,
      versions,
      policies,
      subpolicies,
      loading,
      error,
      versionModalTitle,
      showCompliancesModal,
      compliances,
      selectedFormat,
      currentItemType,
      currentItemId,
      currentItemName,
      isExporting,
      exportError,
      complianceAudits,
      modalComplianceAudits,
      viewMode,
      modalViewMode,
      breadcrumbs,
      modalTitle,
      showFrameworks,
      showPolicies,
      showSubpolicies,
      hasCompliances,
      selectFramework,
      selectPolicy,
      selectSubpolicy,
      showVersions,
      closeVersionsModal,
      goToStep,
      formatDate,
      categoryIcon,
      statusClass,
      viewAllCompliances,
      closeModal,
      handleExport,
      handleModalExport,
      fetchAuditInfo,
      getAuditStatusClass,
      getAuditStatusIcon,
      getAuditInfoForCompliance,
      fetchModalAuditInfo,
      toggleViewMode,
      toggleModalViewMode,
      filteredCompliances,
      filteredModalCompliances,
      handleAuditLinkClick: (auditFindingsId) => {
        if (!auditFindingsId) return;
        console.log(`Clicked on audit findings ID: ${auditFindingsId}`);
        // This function will be used for redirecting in the future
        // You can implement the redirection logic here when needed
      }
    }
  }
}
</script>

<style src="./Compliances.css"></style>

<style>
/* Styling for audit status icons */
.fully-compliant i {
  color: #10b981;
  margin-right: 5px;
}

.partially-compliant i {
  color: #f59e0b;
  margin-right: 5px;
}

.non-compliant i {
  color: #ef4444;
  margin-right: 5px;
}

.not-applicable i {
  color: #6b7280;
  margin-right: 5px;
}

.not-audited i {
  color: #9ca3af;
  margin-right: 5px;
}

/* Add animation for loading state */
.fa-sync {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Add these styles for the list view of compliances */
.section-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.view-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  color: #4b5563;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.view-toggle-btn:hover {
  background-color: #e5e7eb;
  transform: translateY(-1px);
}

.view-toggle-btn i {
  color: #6b7280;
}

.compliances-list-view {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  overflow: auto;
  margin-top: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.compliances-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.compliances-table th {
  background-color: #f9fafb;
  padding: 12px 15px;
  text-align: left;
  font-weight: 600;
  color: #4b5563;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
  min-width: 140px; /* Ensure minimum width for columns */
  overflow: visible;
}

/* Specific sizing for different columns */
.compliances-table th:nth-child(1) { /* Audit Findings ID */
  min-width: 120px;
}

.compliances-table th:nth-child(2) { /* Compliance */
  min-width: 250px;
}

.compliances-table th:nth-child(3) { /* Criticality */
  min-width: 100px;
}

.compliances-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #e5e7eb;
  color: #1f2937;
}

.compliances-table tr:last-child td {
  border-bottom: none;
}

.compliances-table tr:hover {
  background-color: #f9fafb;
}

.compliance-name {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.audit-id {
  font-family: monospace;
  color: #6b7280;
}

.mini-fetch-btn {
  padding: 4px 8px;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mini-fetch-btn:hover {
  background-color: #e5e7eb;
}

.mini-fetch-btn i {
  margin-right: 4px;
  font-size: 0.8rem;
}

/* Modal Controls */
.modal-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Responsive styles */
@media (max-width: 1200px) {
  .compliances-table {
    min-width: 1000px; /* Ensure horizontal scroll on small screens */
  }
  
  .compliances-list-view {
    overflow-x: auto;
  }
}

/* Add these styles to enhance the audit information presentation */
.clean-details-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #f9fafb;
  border-radius: 8px;
  padding: 14px;
  margin: 15px 0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed #e5e7eb;
  padding-bottom: 8px;
  font-size: 0.95rem;
}

.detail-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.detail-label, .label {
  color: #4b5563;
  font-weight: 500;
  min-width: 150px;
}

.detail-value, .value {
  color: #111827;
  font-weight: 500;
}

/* Audit status classes */
.fully-compliant {
  color: #10b981;
  font-weight: 500;
}

.partially-compliant {
  color: #f59e0b;
  font-weight: 500;
}

.non-compliant {
  color: #ef4444;
  font-weight: 500;
}

.not-applicable {
  color: #6b7280;
  font-weight: 500;
}

.not-audited {
  color: #9ca3af;
  font-style: italic;
}

.fetch-audit-actions {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.fetch-audit-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  color: #4b5563;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.fetch-audit-btn:hover {
  background-color: #e5e7eb;
  transform: translateY(-1px);
}

.fetch-audit-btn i {
  color: #6b7280;
}

/* Enhanced compliance cards */
.compliance-card {
  transition: all 0.25s ease;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.compliance-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-color: #d1d5db;
}

.compliance-header {
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
}

.compliance-body {
  padding: 16px;
}

.compliance-body h3 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #1f2937;
  font-size: 1.1rem;
  line-height: 1.4;
}

.compliance-footer {
  padding-top: 12px;
  margin-top: 12px;
  border-top: 1px solid #e5e7eb;
  font-size: 0.85rem;
  color: #6b7280;
}

/* Add audit ID link styling */
.audit-id-link {
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.audit-id-link:hover {
  color: #1d4ed8;
  text-decoration: underline;
}
</style> 