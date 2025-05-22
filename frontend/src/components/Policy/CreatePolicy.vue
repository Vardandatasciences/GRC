<template>
  <div class="create-policy-container">
    <h2>{{ getPageTitle() }}</h2>
    
    <!-- Search Bar and Create Policy Button -->
    <div class="search-bar">
      <div class="search-container">
        <i class="fas fa-search search-icon"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search Policy..." 
        />
      </div>
      <div class="button-group">
        <button class="create-framework-btn" @click="isFrameworkFormVisible = true">
          <i class="fas fa-plus icon"></i> Create Framework
        </button>
        <button class="create-policy-btn" @click="toggleForm">
          <i class="fas fa-plus icon"></i> Create Policy
        </button>
      </div>
    </div>

    <!-- Framework Dropdown -->
    <div class="framework-dropdown">
      <select v-model="selectedFramework" @change="handleFrameworkChange">
        <option value="ISO 27001">ISO 27001</option>
        <option value="NIST">NIST</option>
      </select>
    </div>
    
    <!-- Policy Table -->
    <div class="policy-list-container">
      <table class="policy-table">
        <thead>
          <tr>
            <th>Policy Name</th>
            <th>Version</th>
            <th>Category</th>
            <th>Framework</th>
            <th>Status</th>
            <th>Created By</th>
            <th>Authorized By</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="policy in paginatedPolicies" :key="`${policy.name}-${policy.version}`">
            <!-- Main Policy Row -->
            <tr class="main-policy-row">
              <td>{{ policy.name }}</td>
              <td>
                <div class="version-dropdown">
                  <select
                    :value="selectedVersions[policy.name]"
                    @change="handleVersionChange(policy.name, $event.target.value)"
                  >
                    <option 
                      v-for="version in groupedPolicies[policy.name]" 
                      :key="version.version" 
                      :value="version.version"
                    >
                      {{ version.version }}
                    </option>
                  </select>
                  <i class="fas fa-chevron-down dropdown-icon"></i>
                </div>
              </td>
              <td>{{ policy.category }}</td>
              <td>{{ policy.framework }}</td>
              <td>
                <span :class="['status-badge', `status-${policy.status.toLowerCase().replace(' ', '-')}`]">
                  {{ policy.status }}
                </span>
              </td>
              <td>{{ policy.createdBy }}</td>
              <td>{{ policy.authorizedBy }}</td>
            </tr>
            <!-- Subpolicies Rows -->
            <tr 
              v-for="(subPolicy, index) in policy.subPolicies" 
              :key="`${subPolicy.id}-${index}`" 
              class="sub-policy-row"
            >
              <td class="sub-policy-cell">
                <div class="sub-policy-indicator"></div>
                {{ subPolicy.name }}
              </td>
              <td>{{ subPolicy.version }}</td>
              <td>{{ policy.category }}</td>
              <td>{{ policy.framework }}</td>
              <td>
                <span :class="['status-badge', `status-${subPolicy.status.toLowerCase().replace(' ', '-')}`]">
                  {{ subPolicy.status }}
                </span>
              </td>
              <td>{{ subPolicy.createdBy }}</td>
              <td>{{ subPolicy.authorizedBy }}</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="policy-pagination">
      <span>{{ indexOfFirstPolicy + 1 }} - {{ Math.min(indexOfLastPolicy, currentPolicies.length) }} of {{ currentPolicies.length }}</span>
      <div>
        <button @click="prevPage" :disabled="currentPage === 1">Prev</button>
        <button @click="nextPage" :disabled="currentPage === totalPages">Next</button>
      </div>
    </div>

    <!-- Create Policy Form Popup -->
    <div v-if="isFormVisible" class="form-popup">
      <div class="form-container form-scrollable">
        <div class="form-header">
          <h3 style="font-size: 1rem">Control Info</h3>
          <button @click="toggleForm">X</button>
        </div>
        <div class="form-body policy-grid-body">
          <!-- Framework and Policy Selection -->
          <div class="framework-policy-row">
            <div class="framework-policy-selects">
              <div>
                <label>Frame work</label>
                <select v-model="selectedFramework" style="font-size: 0.9rem">
                  <option value="">Select</option>
                  <option v-for="f in frameworks" :key="f.id" :value="f.id">{{ f.name }}</option>
                </select>
              </div>
              <div>
                <label>Policy</label>
                <select 
                  v-model="selectedPolicy" 
                  @change="handleSelectPolicy" 
                  :disabled="!selectedFramework" 
                  style="font-size: 0.9rem"
                >
                  <option value="">Select</option>
                  <option v-for="p in frameworkPolicies" :key="p.name" :value="p.name">{{ p.name }}</option>
                </select>
              </div>
              <button 
                class="add-policy-btn" 
                @click="handleAddPolicy" 
                :disabled="!selectedFramework" 
                style="font-size: 0.9rem"
              >
                <i class="fas fa-plus"></i> Add Policy
              </button>
            </div>
          </div>

          <!-- Policies and Subpolicies Grid -->
          <div class="policy-rows">
            <div v-for="(policy, idx) in policiesForm" :key="idx" class="policy-row">
              <!-- Policy Card -->
              <div class="policy-card">
                <div class="policy-card-header">
                  <b style="font-size: 0.95rem">{{ policy.policyName || `Policy ${idx + 1}` }}</b>
                  <button class="remove-btn" @click="handleRemovePolicy(idx)" title="Remove Policy">✕</button>
                </div>
                <input 
                  type="text" 
                  placeholder="Policy Name" 
                  v-model="policy.policyName" 
                  @input="handlePolicyChange(idx, 'policyName', $event.target.value)" 
                />
                <input 
                  type="text" 
                  placeholder="Category" 
                  v-model="policy.category" 
                  @input="handlePolicyChange(idx, 'category', $event.target.value)" 
                />
                <input 
                  type="text" 
                  placeholder="Version" 
                  v-model="policy.version" 
                  @input="handlePolicyChange(idx, 'version', $event.target.value)" 
                />
                <input 
                  type="date" 
                  placeholder="Effective Start date" 
                  v-model="policy.effectiveStartDate" 
                  @input="handlePolicyChange(idx, 'effectiveStartDate', $event.target.value)" 
                />
                <input 
                  type="date" 
                  placeholder="Effective End Date" 
                  v-model="policy.effectiveEndDate" 
                  @input="handlePolicyChange(idx, 'effectiveEndDate', $event.target.value)" 
                />
                <input 
                  type="date" 
                  placeholder="Created at" 
                  v-model="policy.createdAt" 
                  @input="handlePolicyChange(idx, 'createdAt', $event.target.value)" 
                />
                <button class="upload-btn"><i class="fas fa-plus"></i> Upload Document</button>

                <!-- Add details -->
                <div class="form-section form-subsection">
                  <div class="form-subsection-header">
                    <span>Add details</span>
                  </div>
                  <input 
                    type="text" 
                    placeholder="Title" 
                    v-model="policy.details.title" 
                    @input="handlePolicyDetailsChange(idx, 'title', $event.target.value)" 
                  />
                  <input 
                    type="text" 
                    placeholder="Introduction" 
                    v-model="policy.details.introduction" 
                    @input="handlePolicyDetailsChange(idx, 'introduction', $event.target.value)" 
                  />
                  <input 
                    type="text" 
                    placeholder="Objectives" 
                    v-model="policy.details.objectives" 
                    @input="handlePolicyDetailsChange(idx, 'objectives', $event.target.value)" 
                  />
                  <input 
                    type="text" 
                    placeholder="Scope" 
                    v-model="policy.details.scope" 
                    @input="handlePolicyDetailsChange(idx, 'scope', $event.target.value)" 
                  />
                </div>

                <!-- Request Approvals -->
                <div class="form-section form-subsection">
                  <label><b>Request Approvals</b></label>
                  <input 
                    type="text" 
                    placeholder="Title" 
                    v-model="policy.approvals.title" 
                    @input="handlePolicyApprovalsChange(idx, 'title', $event.target.value)" 
                  />
                  <input 
                    type="text" 
                    placeholder="Description" 
                    v-model="policy.approvals.description" 
                    @input="handlePolicyApprovalsChange(idx, 'description', $event.target.value)" 
                  />
                  <input 
                    type="text" 
                    placeholder="Author" 
                    v-model="policy.approvals.author" 
                    @input="handlePolicyApprovalsChange(idx, 'author', $event.target.value)" 
                  />
                  <input 
                    type="date" 
                    placeholder="Due Date" 
                    v-model="policy.approvals.dueDate" 
                    @input="handlePolicyApprovalsChange(idx, 'dueDate', $event.target.value)" 
                  />
                </div>
                <button class="add-sub-policy-btn" @click="handleAddSubPolicy(idx)">
                  <i class="fas fa-plus"></i> Add Sub Policy
                </button>
              </div>

              <!-- Subpolicies Cards -->
              <div class="subpolicies-row">
                <div v-for="(sub, subIdx) in policy.subPolicies" :key="subIdx" class="subpolicy-card">
                  <div class="policy-card-header">
                    <b style="font-size: 0.9rem">{{ sub.policyName || `Sub Policy ${subIdx + 1}` }}</b>
                    <button class="remove-btn" @click="handleRemoveSubPolicy(idx, subIdx)" title="Remove Sub Policy">✕</button>
                  </div>
                  <input 
                    type="text" 
                    placeholder="Policy Name" 
                    v-model="sub.policyName" 
                    @input="handleSubPolicyChange(idx, subIdx, 'policyName', $event.target.value)" 
                  />
                  <input 
                    type="text" 
                    placeholder="Version" 
                    v-model="sub.version" 
                    @input="handleSubPolicyChange(idx, subIdx, 'version', $event.target.value)" 
                  />
                  <input 
                    type="text" 
                    placeholder="Sub policy" 
                    v-model="sub.subPolicy" 
                    @input="handleSubPolicyChange(idx, subIdx, 'subPolicy', $event.target.value)" 
                  />
                  <input 
                    type="text" 
                    placeholder="Created By" 
                    v-model="sub.createdBy" 
                    @input="handleSubPolicyChange(idx, subIdx, 'createdBy', $event.target.value)" 
                  />
                  <input 
                    type="date" 
                    placeholder="Created Date" 
                    v-model="sub.createdDate" 
                    @input="handleSubPolicyChange(idx, subIdx, 'createdDate', $event.target.value)" 
                  />
                  <button class="upload-btn"><i class="fas fa-plus"></i> Upload Document</button>

                  <!-- Add details -->
                  <div class="form-section form-subsection">
                    <div class="form-subsection-header">
                      <span>Add details</span>
                    </div>
                    <input 
                      type="text" 
                      placeholder="Title" 
                      v-model="sub.details.title" 
                      @input="handleSubPolicyDetailsChange(idx, subIdx, 'title', $event.target.value)" 
                    />
                    <input 
                      type="text" 
                      placeholder="Introduction" 
                      v-model="sub.details.introduction" 
                      @input="handleSubPolicyDetailsChange(idx, subIdx, 'introduction', $event.target.value)" 
                    />
                    <input 
                      type="text" 
                      placeholder="Objective" 
                      v-model="sub.details.objective" 
                      @input="handleSubPolicyDetailsChange(idx, subIdx, 'objective', $event.target.value)" 
                    />
                    <input 
                      type="text" 
                      placeholder="Scope" 
                      v-model="sub.details.scope" 
                      @input="handleSubPolicyDetailsChange(idx, subIdx, 'scope', $event.target.value)" 
                    />
                  </div>

                  <!-- Request Approvals -->
                  <div class="form-section form-subsection">
                    <label><b>Request Approvals</b></label>
                    <input 
                      type="text" 
                      placeholder="Title" 
                      v-model="sub.approvals.title" 
                      @input="handleSubPolicyApprovalsChange(idx, subIdx, 'title', $event.target.value)" 
                    />
                    <input 
                      type="text" 
                      placeholder="Description" 
                      v-model="sub.approvals.description" 
                      @input="handleSubPolicyApprovalsChange(idx, subIdx, 'description', $event.target.value)" 
                    />
                    <input 
                      type="text" 
                      placeholder="Author" 
                      v-model="sub.approvals.author" 
                      @input="handleSubPolicyApprovalsChange(idx, subIdx, 'author', $event.target.value)" 
                    />
                    <input 
                      type="date" 
                      placeholder="Due Date" 
                      v-model="sub.approvals.dueDate" 
                      @input="handleSubPolicyApprovalsChange(idx, subIdx, 'dueDate', $event.target.value)" 
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
          <button class="create-btn" style="font-size: 1rem; margin-top: 24px">Submit</button>
        </div>
      </div>
    </div>

    <!-- Create Framework Form Popup -->
    <div v-if="isFrameworkFormVisible" class="form-popup framework-form">
      <div class="form-container">
        <div class="form-header">
          <h3>Create Framework</h3>
          <button @click="isFrameworkFormVisible = false">X</button>
        </div>
        <div class="form-body">
          <form class="form-section" @submit.prevent="handleFrameworkFormSubmit">
            <div class="form-group">
              <label>Framework ID</label>
              <input type="text" placeholder="Enter framework id" />
            </div>
            
            <div class="form-group">
              <label>Framework Name</label>
              <input type="text" placeholder="Enter framework name" />
            </div>
            
            <div class="form-group">
              <label>Version</label>
              <input type="text" placeholder="Enter version" />
            </div>
            
            <div class="form-group">
              <label>Upload Document</label>
              <div class="upload-input-container">
                <input type="file" id="framework-doc" class="file-input" />
                <label for="framework-doc" class="upload-label">
                  <span class="upload-text">Choose File</span>
                </label>
              </div>
            </div>
            
            <div class="form-group">
              <label>Effective Start Date</label>
              <input type="date" />
            </div>
            
            <div class="form-group">
              <label>Effective End Date</label>
              <input type="date" />
            </div>
            
            <div class="form-group">
              <label>Created By</label>
              <input type="text" placeholder="Enter creator name" />
            </div>
            <button class="create-btn" type="submit">Submit</button>
          </form>
        </div>
      </div>
    </div>

    <!-- Extraction Screens Popup -->
    <div v-if="showExtractionScreens && extractionSlides.length > 0" class="extraction-popup-overlay">
      <div class="extraction-popup">
        <div class="form-header extraction-header" style="padding-bottom: 0">
          <!-- Stepper Navigation Bar as Tabs -->
          <div class="extraction-stepper">
            <div
              v-for="(slide, idx) in extractionSlides"
              :key="idx"
              :class="['extraction-step', { active: extractionStep === idx }]"
              @click="extractionStep = idx"
              :style="{ cursor: extractionStep !== idx ? 'pointer' : 'default' }"
            >
              {{ slide.type === 'framework' ? 'Framework' : 
                 slide.type === 'policy' ? `Policy ${slide.index !== undefined ? slide.index + 1 : ''}` : 
                 'Authorizer' }}
              <span
                class="tab-close"
                v-if="extractionStep === idx"
                @click.stop="showExtractionScreens = false"
              >
                X
              </span>
            </div>
          </div>
        </div>
        <div class="form-body extraction-body">
          <!-- Render slide content based on type -->
          <div v-if="extractionSlides[extractionStep].type === 'framework'">
            <label>Title:</label>
            <input :value="extractionSlides[extractionStep].data.title" readonly />
            <label>Description:</label>
            <textarea :value="extractionSlides[extractionStep].data.description" readonly></textarea>
          </div>
          <div v-else-if="extractionSlides[extractionStep].type === 'policy'">
            <div class="policy-main">
              <b>Policy</b>
              <label>Title:</label>
              <input :value="extractionSlides[extractionStep].data.title" readonly />
              <label>Description:</label>
              <textarea :value="extractionSlides[extractionStep].data.description" readonly></textarea>
              <label v-if="extractionSlides[extractionStep].data.objective">Objective:</label>
              <textarea v-if="extractionSlides[extractionStep].data.objective" :value="extractionSlides[extractionStep].data.objective" readonly></textarea>
              <label v-if="extractionSlides[extractionStep].data.scope">Scope:</label>
              <textarea v-if="extractionSlides[extractionStep].data.scope" :value="extractionSlides[extractionStep].data.scope" readonly></textarea>
            </div>
            <div v-if="extractionSlides[extractionStep].data.subPolicies && extractionSlides[extractionStep].data.subPolicies.length" class="subpolicies-group">
              <div v-for="(sub, i) in extractionSlides[extractionStep].data.subPolicies" :key="i" class="subpolicy-card extraction-subpolicy">
                <b>Sub Policy {{ i + 1 }}</b>
                <label>Title:</label>
                <input :value="sub.title" readonly />
                <label>Description:</label>
                <textarea :value="sub.description" readonly></textarea>
              </div>
            </div>
          </div>
          <div v-else-if="extractionSlides[extractionStep].type === 'authorizer'">
            <label>Title:</label>
            <input :value="extractionSlides[extractionStep].data.title" readonly />
            <label>Description:</label>
            <textarea :value="extractionSlides[extractionStep].data.description" readonly></textarea>
            <label>Created By:</label>
            <input :value="extractionSlides[extractionStep].data.createdBy" readonly />
            <label>Created date:</label>
            <input :value="extractionSlides[extractionStep].data.createdDate" readonly />
            <label>Authorized By:</label>
            <input :value="extractionSlides[extractionStep].data.authorizedBy" readonly />
            <label>Assign task for authorization:</label>
            <input :value="extractionSlides[extractionStep].data.assignTask" readonly />
          </div>
          <div style="text-align: right; margin-top: 24px">
            <button
              v-if="extractionStep < extractionSlides.length - 1"
              class="create-btn"
              style="min-width: 100px"
              @click="extractionStep = extractionStep + 1"
            >
              next &gt;
            </button>
            <button
              v-else
              class="create-btn"
              style="min-width: 100px"
              @click="showExtractionScreens = false"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Tree View Popup for Framework/Policy/Subpolicy Selection -->
    <div v-if="showTreePopup" class="tree-popup-overlay">
      <div class="tree-popup tree-popup-static">
        <div class="tree-popup-header">
          <div style="display:flex;align-items:center;gap:24px;">
            <select v-model="treeSelectedFramework" class="tree-framework-select">
              <option value="" disabled>Select Framework</option>
              <option v-for="(fw, idx) in treeFrameworks" :key="idx" :value="fw.title">{{ fw.title }}</option>
            </select>
            <button v-if="treeSelectedFramework" class="tree-expand-btn" @click="expandAllTree">Expand All</button>
          </div>
          <button class="tree-popup-close" @click="showTreePopup = false">×</button>
        </div>
        <div class="org-tree-root">
          <div v-if="treeSelectedFramework" class="org-tree-center">
            <!-- Framework Node -->
            <div class="org-tree-framework-row">
              <div class="org-tree-framework-node" ref="frameworkNode">
                <span>{{ treeSelectedFramework }}</span>
                <span v-if="!showPolicies" class="org-tree-arrow-down clickable" @click="togglePolicies">
                  <i class="fas fa-chevron-down"></i>
                </span>
              </div>
            </div>
            <!-- Policies Row -->
            <transition name="fade-slide">
              <div v-if="showPolicies" class="org-tree-policies-row" ref="policiesRow">
                <div v-for="(policy, pIdx) in treePolicies" :key="'policy-'+pIdx" class="org-tree-policy-block">
                  <div class="org-tree-policy-node">
                    <span>{{ policy.title }}</span>
                    <span v-if="!expandedPolicies[pIdx]" class="org-tree-arrow-down clickable" @click="togglePolicyExpand(pIdx)">
                      <i class="fas fa-chevron-down"></i>
                    </span>
                  </div>
                  <transition name="fade-slide">
                    <div v-if="expandedPolicies[pIdx] && policy.subPolicies && policy.subPolicies.length" class="org-tree-subpolicies-row">
                      <div class="org-tree-subpolicies-blocks">
                        <div v-for="(sub, sIdx) in policy.subPolicies" :key="'sub-'+sIdx" class="org-tree-subpolicy-block">
                          <div class="org-tree-subpolicy-node">
                            <span>{{ sub.title }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </transition>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import frameworkSample from '../../data/frameworkSample.json'

export default {
  name: 'CreatePolicy',
  setup() {
    const searchQuery = ref('')
    const currentPage = ref(1)
    const selectedVersions = ref({})
    const isFormVisible = ref(false)
    const selectedFramework = ref('')
    const selectedPolicy = ref('')
    const isFrameworkFormVisible = ref(false)
    const showExtractionScreens = ref(false)
    const extractedData = ref(null)
    const extractionStep = ref(0)
    const extractionSlides = ref([])
    const policiesForm = ref([])
    const frameworkPolicies = ref([])
    const selectedPolicyIdx = ref(null)
    const showTreePopup = ref(false)
    const treeSelectedFramework = ref('')
    const showPolicies = ref(false)
    const expandedPolicies = ref({})
    const treeFrameworks = computed(() => [{ title: frameworkSample.framework.title }])
    const treePolicies = computed(() => treeSelectedFramework.value ? frameworkSample.policies : [])
    const svgWidth = 700
    const svgPolicyLineHeight = 60
    const svgSubWidth = 260
    const svgSubLineHeight = 50

    const policiesPerPage = 4

    // Sample frameworks data
    const frameworks = [
      { id: 'iso27001', name: 'ISO 27001' },
      { id: 'nist', name: 'NIST' },
      { id: 'cobit', name: 'COBIT' }
    ]

    // Sample policies data
    const policies = [
      { 
        id: 'HR-001', 
        version: '1.0',
        name: 'Employee Code of Conduct',
        category: 'HR',
        status: 'Active',
        effectiveStartDate: '01/01/2024',
        effectiveEndDate: '31/12/2024',
        createdBy: 'John Doe',
        authorizedBy: 'Jane Smith',
        framework: 'ISO 27001',
        subPolicies: [
          {
            id: 'HR-001-SP1',
            name: 'Dress Code Policy',
            version: '1.0',
            status: 'Active',
            effectiveStartDate: '01/01/2024',
            effectiveEndDate: '31/12/2024',
            createdBy: 'John Doe',
            authorizedBy: 'Jane Smith'
          },
          {
            id: 'HR-001-SP2',
            name: 'Workplace Behavior Policy',
            version: '1.0',
            status: 'Active',
            effectiveStartDate: '01/01/2024',
            effectiveEndDate: '31/12/2024',
            createdBy: 'John Doe',
            authorizedBy: 'Jane Smith'
          }
        ]
      },
      // ... other policies
    ]

    // Group policies by name
    const groupedPolicies = computed(() => {
      return policies.reduce((acc, policy) => {
        if (!acc[policy.name]) {
          acc[policy.name] = []
        }
        acc[policy.name].push(policy)
        return acc
      }, {})
    })

    // Initialize selected versions
    onMounted(() => {
      const initialVersions = {}
      Object.keys(groupedPolicies.value).forEach(name => {
        if (groupedPolicies.value[name] && groupedPolicies.value[name].length > 0) {
          initialVersions[name] = groupedPolicies.value[name][0].version
        }
      })
      selectedVersions.value = initialVersions
    })

    const handleVersionChange = (policyName, version) => {
      selectedVersions.value = {
        ...selectedVersions.value,
        [policyName]: version
      }
    }

    // Get current policies based on selected versions
    const currentPolicies = computed(() => {
      return Object.entries(groupedPolicies.value)
        .filter(([name]) => name.toLowerCase().includes(searchQuery.value.toLowerCase()))
        .map(([name, versions]) => {
          const selectedVersion = selectedVersions.value[name]
          const policy = versions.find(v => v.version === selectedVersion)
          return policy || versions[0]
        })
        .filter(Boolean)
    })

    // Pagination Logic
    const indexOfLastPolicy = computed(() => currentPage.value * policiesPerPage)
    const indexOfFirstPolicy = computed(() => indexOfLastPolicy.value - policiesPerPage)
    const paginatedPolicies = computed(() => 
      currentPolicies.value.slice(indexOfFirstPolicy.value, indexOfLastPolicy.value)
    )
    const totalPages = computed(() => 
      Math.ceil(currentPolicies.value.length / policiesPerPage)
    )

    const nextPage = () => {
      if (currentPage.value < totalPages.value) currentPage.value++
    }

    const prevPage = () => {
      if (currentPage.value > 1) currentPage.value--
    }

    const toggleForm = () => {
      isFormVisible.value = !isFormVisible.value
    }

    const handleFrameworkChange = (e) => {
      selectedFramework.value = e.target.value
    }

    // Policy form handlers
    const handleAddPolicy = () => {
      policiesForm.value.push({
        policyName: '',
        version: '',
        category: '',
        effectiveStartDate: '',
        effectiveEndDate: '',
        createdAt: '',
        details: { title: '', introduction: '', objectives: '', scope: '' },
        approvals: { title: '', description: '', author: '', dueDate: '' },
        subPolicies: []
      })
      selectedPolicyIdx.value = policiesForm.value.length - 1
    }

    const handleSelectPolicy = (e) => {
      const policyName = e.target.value
      if (!policyName) return
      
      if (policiesForm.value.some(p => p.policyName === policyName)) {
        selectedPolicyIdx.value = policiesForm.value.findIndex(p => p.policyName === policyName)
        return
      }

      const found = frameworkPolicies.value.find(p => p.name === policyName)
      policiesForm.value.push({
        policyName: found.name,
        version: found.version,
        category: '',
        effectiveStartDate: '',
        effectiveEndDate: '',
        createdAt: '',
        details: { title: '', introduction: '', objectives: '', scope: '' },
        approvals: { title: '', description: '', author: '', dueDate: '' },
        subPolicies: []
      })
      selectedPolicyIdx.value = policiesForm.value.length - 1
    }

    const handleRemovePolicy = (idx) => {
      policiesForm.value = policiesForm.value.filter((_, i) => i !== idx)
      selectedPolicyIdx.value = null
    }

    const handlePolicyChange = (idx, field, value) => {
      policiesForm.value[idx][field] = value
    }

    const handlePolicyDetailsChange = (idx, field, value) => {
      policiesForm.value[idx].details[field] = value
    }

    const handlePolicyApprovalsChange = (idx, field, value) => {
      policiesForm.value[idx].approvals[field] = value
    }

    const handleAddSubPolicy = (policyIdx) => {
      policiesForm.value[policyIdx].subPolicies.push({
        policyName: '',
        version: '',
        subPolicy: '',
        createdBy: '',
        createdDate: '',
        details: { title: '', introduction: '', objective: '', scope: '' },
        approvals: { title: '', description: '', author: '', dueDate: '' }
      })
    }

    const handleRemoveSubPolicy = (policyIdx, subIdx) => {
      policiesForm.value[policyIdx].subPolicies = 
        policiesForm.value[policyIdx].subPolicies.filter((_, j) => j !== subIdx)
    }

    const handleSubPolicyChange = (policyIdx, subIdx, field, value) => {
      policiesForm.value[policyIdx].subPolicies[subIdx][field] = value
    }

    const handleSubPolicyDetailsChange = (policyIdx, subIdx, field, value) => {
      policiesForm.value[policyIdx].subPolicies[subIdx].details[field] = value
    }

    const handleSubPolicyApprovalsChange = (policyIdx, subIdx, field, value) => {
      policiesForm.value[policyIdx].subPolicies[subIdx].approvals[field] = value
    }

    // Framework form submit handler
    const handleFrameworkFormSubmit = (e) => {
      e.preventDefault()
      // Build slides dynamically based on JSON structure
      const slides = []
      if (frameworkSample.framework) {
        slides.push({
          type: 'framework',
          data: frameworkSample.framework
        })
      }
      if (frameworkSample.policies && Array.isArray(frameworkSample.policies)) {
        frameworkSample.policies.forEach((policy, idx) => {
          slides.push({
            type: 'policy',
            data: policy,
            index: idx
          })
        })
      }
      if (frameworkSample.authorizer) {
        slides.push({
          type: 'authorizer',
          data: frameworkSample.authorizer
        })
      }
      extractionSlides.value = slides
      showExtractionScreens.value = true
      extractionStep.value = 0
      isFrameworkFormVisible.value = false
    }

    function togglePolicies() { showPolicies.value = !showPolicies.value }
    function togglePolicyExpand(idx) {
      expandedPolicies.value = { ...expandedPolicies.value, [idx]: !expandedPolicies.value[idx] }
    }
    function expandAllTree() {
      showPolicies.value = true
      const all = {}
      treePolicies.value.forEach((_, idx) => { all[idx] = true })
      expandedPolicies.value = all
    }

    function getPolicyX(idx) {
      // Spread policies evenly
      const count = treePolicies.value.length
      if (count === 1) return svgWidth/2
      const gap = svgWidth/(count+1)
      return gap*(idx+1)
    }
    function getSubX(count, idx) {
      if (count === 1) return svgSubWidth/2
      const gap = svgSubWidth/(count+1)
      return gap*(idx+1)
    }

    // Adjust Y coordinates for SVG lines to connect to node edges
    const frameworkNodeHeight = 48 + 16; // node height + padding
    const policyNodeHeight = 40 + 12; // node height + padding
    // For framework to policy
    function getFrameworkToPolicyY1() { return frameworkNodeHeight; }
    function getFrameworkToPolicyY2() { return svgPolicyLineHeight - 8; }
    // For policy to subpolicy
    function getPolicyToSubY1() { return policyNodeHeight; }
    function getPolicyToSubY2() { return svgSubLineHeight - 8; }

    return {
      searchQuery,
      currentPage,
      selectedVersions,
      isFormVisible,
      selectedFramework,
      selectedPolicy,
      isFrameworkFormVisible,
      showExtractionScreens,
      extractedData,
      extractionStep,
      extractionSlides,
      policiesForm,
      frameworkPolicies,
      selectedPolicyIdx,
      frameworks,
      policies,
      groupedPolicies,
      currentPolicies,
      paginatedPolicies,
      indexOfFirstPolicy,
      indexOfLastPolicy,
      totalPages,
      handleVersionChange,
      nextPage,
      prevPage,
      toggleForm,
      handleFrameworkChange,
      handleAddPolicy,
      handleSelectPolicy,
      handleRemovePolicy,
      handlePolicyChange,
      handlePolicyDetailsChange,
      handlePolicyApprovalsChange,
      handleAddSubPolicy,
      handleRemoveSubPolicy,
      handleSubPolicyChange,
      handleSubPolicyDetailsChange,
      handleSubPolicyApprovalsChange,
      handleFrameworkFormSubmit,
      showTreePopup,
      treeSelectedFramework,
      showPolicies,
      expandedPolicies,
      treeFrameworks,
      treePolicies,
      togglePolicies,
      togglePolicyExpand,
      expandAllTree,
      svgWidth,
      svgPolicyLineHeight,
      svgSubWidth,
      svgSubLineHeight,
      getPolicyX,
      getSubX,
      getFrameworkToPolicyY1,
      getFrameworkToPolicyY2,
      getPolicyToSubY1,
      getPolicyToSubY2
    }
  }
}
</script>

<style scoped>
/* Import the existing CSS file */
@import './CreatePolicy.css';
</style> 