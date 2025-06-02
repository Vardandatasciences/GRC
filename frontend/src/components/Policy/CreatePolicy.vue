<template>
  <div class="create-policy-container">
    <h2>Create New Policy</h2>
    
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
      handleFrameworkFormSubmit
    }
  }
}
</script>

<style scoped>
.create-policy-container {
    margin-left: 230px;
    padding: 20px;
}

.search-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    gap: 24px;
}

.search-container {
    display: flex;
    align-items: center;
    border: 1px solid #ccc;
    padding: 4px 8px;
    border-radius: 4px;
}

.search-container input {
    border: none;
    outline: none;
    padding: 4px;
    font-size: 11px;
    width: 250px;
}

.search-icon {
    color: #888;
    margin-right: 8px;
    font-size: 12px;
}

.button-group {
    display: flex;
    align-items: center;
    gap: 12px;
}

.create-framework-btn {
    padding: 6px 12px;
    font-size: 11px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin: 0;
}

.create-framework-btn:hover {
    background-color: #218838;
}

.create-policy-btn {
    padding: 6px 12px;
    font-size: 11px;
    background-color: #007BFF;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin: 0;
}

.create-policy-btn:hover {
    background-color: #0056b3;
}

.policy-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin-top: 20px;
    background-color: white;
    font-size: 11px;
    border: 2px solid #000;
    border-radius: 8px;
}

.policy-table th, .policy-table td {
    padding: 12px 10px;
    text-align: left;
    border: 1px solid #454545;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.policy-table th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: #495057;
    text-transform: uppercase;
    font-size: 10px;
    letter-spacing: 0.5px;
    position: sticky;
    top: 0;
    z-index: 1;
}

.policy-table tr:first-child th:first-child {
    border-top-left-radius: 8px;
}
.policy-table tr:first-child th:last-child {
    border-top-right-radius: 8px;
}
.policy-table tr:last-child td:first-child {
    border-bottom-left-radius: 8px;
}
.policy-table tr:last-child td:last-child {
    border-bottom-right-radius: 8px;
}

.policy-table tbody tr:hover {
    background-color: #f8f9fa;
}

.policy-table tbody tr:last-child td {
    border-bottom: 1px solid #3c3c3c;
}

/* Status Badges */
.status-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: 500;
    text-transform: capitalize;
    display: inline-block;
    min-width: 80px;
    text-align: center;
}

.status-active {
    background-color: #d4edda;
    color: #155724;
}

.status-onhold {
    background-color: #fff3cd;
    color: #856404;
}

.status-under-review {
    background-color: #cce5ff;
    color: #004085;
}

/* Responsive Table Container */
.policy-list-container {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    margin: 0 auto;
    max-width: 100%;
}

/* Media Queries for Different Screen Sizes */
@media screen and (max-width: 1600px) {
    .policy-table {
        font-size: 10px;
    }
    
    .policy-table th, .policy-table td {
        padding: 6px 8px;
    }
    
    .version-dropdown select {
        font-size: 9px;
        padding: 2px 18px 2px 5px;
    }
}

@media screen and (max-width: 1366px) {
    .policy-table {
        font-size: 9px;
    }
    
    .policy-table th, .policy-table td {
        padding: 5px 6px;
    }
    
    .status-badge {
        padding: 1px 5px;
        font-size: 8px;
        min-width: 50px;
    }
}

@media screen and (max-width: 1024px) {
    .policy-table {
        font-size: 10px;
    }
    
    .policy-table th, .policy-table td {
        padding: 5px 6px;
        max-width: 100px;
    }
    
    .status-badge {
        padding: 2px 5px;
        font-size: 9px;
        min-width: 60px;
    }
}

/* Mobile Responsive */
@media screen and (max-width: 768px) {
    .policy-list-container {
        overflow-x: visible;
    }
    
    .policy-table {
        min-width: auto;
        width: 100%;
    }
    
    .policy-table th, .policy-table td {
        padding: 8px 10px;
        max-width: none;
    }
    
    .create-policy-container {
        padding: 10px;
    }
    
    .search-bar {
        flex-direction: column;
        gap: 10px;
    }
    
    .search-container {
        width: 100%;
    }
    
    .create-policy-btn {
        width: 100%;
        margin-left: 0;
    }
    
    .version-dropdown {
        min-width: 70px;
    }
    
    .version-dropdown select {
        padding: 3px 20px 3px 6px;
        font-size: 11px;
    }
    
    .version-dropdown .dropdown-icon {
        right: 6px;
        font-size: 9px;
    }
}

/* Pagination Styling */
.policy-pagination {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 15px;
    padding: 8px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    font-size: 11px;
}

.policy-pagination button {
    padding: 4px 10px;
    border: 1px solid #dee2e6;
    color: #495057;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 11px;
}

.policy-pagination button:hover:not(:disabled) {
    background-color: #f8f9fa;
    border-color: #adb5bd;
}

.policy-pagination button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.policy-pagination span {
    color: #6c757d;
    font-size: 12px;
}

/* Scrollbar Styling */
.policy-list-container::-webkit-scrollbar {
    height: 8px;
    width: 8px;
}

.policy-list-container::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.policy-list-container::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}

.policy-list-container::-webkit-scrollbar-thumb:hover {
    background: #555;
}

/* Form Popup Styling */
.form-popup {
    position: fixed;
    top: 0;
    left: 210px;
    right: 0;
    bottom: 0;
    width: calc(95% - 190px);
    height: 95vh;
    background-color: #fff;
    border: 1px solid #bbbbbb;
    z-index: 100;
    font-size: 11px;
    display: flex;
    flex-direction: column;
    overflow-x: hidden;
}

.form-container.form-scrollable {
    height: 100%;
    overflow-y: auto;
    padding: 0;
    display: flex;
    flex-direction: column;
}

.form-header {
    background: #f4f4f4;
    border-bottom: 1px solid #e0e0e0;
    padding: 18px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 1;
}

.form-header h3 {
    font-size: 18px;
    margin: 0;
    font-weight: 500;
}

.form-header button {
    background: none;
    border: none;
    font-size: 22px;
    cursor: pointer;
    color: #222;
    margin-left: 10px;
}

.form-body {
    padding: 24px;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 24px;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}

.form-section {
    margin-bottom: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
    background: #fff;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.form-section label {
    font-size: 14px;
    font-weight: 500;
    color: #333;
}

.form-section input,
.form-section select {
    width: 100%;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 14px;
    background: #fff;
    outline: none;
    transition: border-color 0.2s;
}

.form-section input:focus,
.form-section select:focus {
    border-color: #007bff;
}

.form-subsection {
    background: #f8f9fa;
    border-radius: 6px;
    padding: 16px;
    margin: 12px 0;
    border: 1px solid #e9ecef;
}

.create-btn {
    background-color: #007bff;
    color: #fff;
    padding: 12px 24px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    margin: 24px auto;
    width: auto;
    min-width: 200px;
    transition: background-color 0.2s;
}

.create-btn:hover {
    background-color: #0056b3;
}

/* Framework and Policy Selection Section */
.framework-policy-section {
    display: flex;
    gap: 16px;
    align-items: flex-start;
    margin-bottom: 24px;
}

.framework-policy-section .form-section {
    flex: 1;
}

/* Sub Policy Section */
.sub-policy-section {
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 16px;
    margin-top: 16px;
    background: #fff;
}

.sub-policy-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

.sub-policy-header h4 {
    margin: 0;
    font-size: 16px;
    color: #333;
}

.add-sub-policy-btn {
    background: none;
    border: none;
    color: #007bff;
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
}

.add-sub-policy-btn:hover {
    color: #0056b3;
}

/* Version Dropdown Styling */
.version-dropdown {
    position: relative;
    display: inline-block;
    min-width: 80px;
}

.version-dropdown select {
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    background-color: white;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 4px 20px 4px 8px;
    font-size: 11px;
    cursor: pointer;
    width: 100%;
    outline: none;
}

.version-dropdown .dropdown-icon {
    position: absolute;
    right: 6px;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    font-size: 8px;
    color: #6c757d;
}

.version-dropdown select:hover {
    border-color: #adb5bd;
}

.version-dropdown select:focus {
    border-color: #80bdff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

/* Update table cell widths */
.policy-table th:nth-child(1), /* Policy Name */
.policy-table td:nth-child(1) {
    min-width: 180px;
    max-width: 200px;
    border-left: 1px solid #000;
}

.policy-table th:nth-child(2), /* Version */
.policy-table td:nth-child(2) {
    min-width: 80px;
    max-width: 100px;
}

.policy-table th:nth-child(3), /* Category */
.policy-table td:nth-child(3) {
    min-width: 80px;
    max-width: 100px;
}

.policy-table th:nth-child(4), /* Status */
.policy-table td:nth-child(4) {
    min-width: 80px;
    max-width: 100px;
}

.policy-table th:nth-child(5), /* Effective Start Date */
.policy-table td:nth-child(5) {
    min-width: 100px;
    max-width: 120px;
}

.policy-table th:nth-child(6), /* Effective End Date */
.policy-table td:nth-child(6) {
    min-width: 100px;
    max-width: 120px;
}

.policy-table th:nth-child(7), /* Created By */
.policy-table td:nth-child(7) {
    min-width: 100px;
    max-width: 120px;
}

.policy-table th:nth-child(8), /* Authorized By */
.policy-table td:nth-child(8) {
    min-width: 100px;
    max-width: 120px;
    border-right: 1px solid #000;
}

/* Add subtle hover effect */
.policy-table tbody tr {
    transition: background-color 0.2s ease;
}

.policy-table tbody tr:hover {
    background-color: #f5f5f5;
}

/* Policy Grid Body */
.policy-grid-body {
  font-size: 12px;
  background: #f5f5f5;
  padding: 16px 0 32px 0;
}

.framework-policy-row {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 18px;
  margin-left: 18px;
}
.framework-policy-selects {
  display: flex;
  align-items: center;
  gap: 28px;
}
.add-policy-btn {
  background: #fff;
  color: #222;
  border: 1px solid #bbb;
  border-radius: 16px;
  font-size: 12px;
  padding: 2px 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  margin-left: 8px;
  transition: background 0.2s;
}
.add-policy-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.add-policy-btn:hover:not(:disabled) {
  background: #f0f0f0;
}

.policy-rows {
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow-x: auto;
  padding-bottom: 16px;
}
.policy-row {
  display: flex;
  align-items: flex-start;
  gap: 18px;
  margin-bottom: 8px;
  flex-wrap: nowrap;
  overflow-x: auto;
  min-width: 100%;
}
.policy-card, .subpolicy-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  padding: 12px 14px 10px 14px;
  min-width: 220px;
  max-width: 260px;
  font-size: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 0 0 auto;
}
.policy-card {
  min-width: 260px;
  max-width: 300px;
  border-left: 3px solid #007bff;
}
.subpolicies-row {
  display: flex;
  gap: 12px;
  flex-wrap: nowrap;
  overflow-x: auto;
  min-width: 0;
}
.subpolicy-card {
  border-left: 3px solid #28a745;
  min-width: 220px;
  max-width: 260px;
}
.policy-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}
.policy-card-header b {
  font-size: 13px;
  font-weight: 600;
}
.remove-btn {
  background: none;
  border: none;
  color: #d00;
  font-size: 15px;
  cursor: pointer;
  margin-left: 6px;
}
.remove-btn:hover {
  color: #a00;
}
input, select, textarea {
  font-size: 12px !important;
  padding: 4px 8px !important;
  border-radius: 4px !important;
  border: 1px solid #bbb !important;
  margin-bottom: 2px;
  background: #fafbfc;
}
input[type="date"] {
  font-size: 12px !important;
}
textarea {
  min-height: 28px;
  resize: vertical;
}
.upload-btn, .add-sub-policy-btn {
  background: #f8f9fa;
  color: #222;
  border: 1px solid #bbb;
  border-radius: 16px;
  font-size: 12px;
  padding: 2px 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  margin: 2px 0 2px 0;
  transition: background 0.2s;
}
.upload-btn:hover, .add-sub-policy-btn:hover {
  background: #e9ecef;
}
.add-sub-policy-btn {
  margin-top: 6px;
  background: #e6f7ea;
  border: 1px solid #28a745;
  color: #28a745;
}
.add-sub-policy-btn:hover {
  background: #d4f5e3;
}
.form-section.form-subsection {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 8px 10px;
  margin: 6px 0;
  border: 1px solid #e9ecef;
  font-size: 11px;
}
.form-subsection-header {
  display: flex;
  justify-content: flex-end;
  font-size: 11px;
  color: #222;
  margin-bottom: 2px;
}
.create-btn {
  background-color: #007bff;
  color: #fff;
  padding: 8px 0;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  width: 120px;
  font-size: 13px;
  margin: 18px auto 0 auto;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  display: block;
  font-weight: 500;
  transition: background 0.2s;
}
.create-btn:hover {
  background: #0056b3;
}
@media (max-width: 1200px) {
  .policy-row {
    flex-direction: column;
    gap: 10px;
  }
  .subpolicies-row {
    flex-direction: column;
    gap: 10px;
  }
}

/* Framework Form Styles */
.form-popup.framework-form {
  width: 420px;
  min-width: 320px;
  max-width: 90vw;
  height: 95vh;
  right: auto;
  left: 50%;
  transform: translateX(-50%);
  overflow-y: auto;
  overflow-x: hidden;
  font-size: 12px;
  padding-bottom: 16px;
  box-sizing: border-box;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-popup.framework-form .form-container {
  width: 100%;
  height: 100%;
  overflow-x: hidden;
}

.form-popup.framework-form .form-section {
  padding: 16px;
  gap: 12px;
  width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  box-sizing: border-box;
}

.form-group label {
  font-size: 12px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  box-sizing: border-box;
  max-width: 100%;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
  background: #fff;
}

/* Upload Input Styling */
.upload-input-container {
  position: relative;
  width: 100%;
  box-sizing: border-box;
}

.file-input {
  position: absolute;
  width: 0.1px;
  height: 0.1px;
  opacity: 0;
  overflow: hidden;
  z-index: -1;
}

.upload-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 6px 10px;
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
  color: #333;
  box-sizing: border-box;
}

.upload-label:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.upload-text {
  color: #666;
}

.upload-icon {
  font-size: 14px;
  color: #666;
  margin-left: 8px;
}

.form-subsection {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 12px;
  margin-top: 8px;
}

.form-subsection h4 {
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

/* Submit Button Styling */
.create-btn {
  background-color: #007bff;
  color: #fff;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  margin-top: 12px;
  width: 100%;
  transition: background-color 0.2s;
}

.create-btn:hover {
  background-color: #0056b3;
}

/* Date Input Styling */
input[type="date"] {
  font-family: inherit;
  font-size: 12px;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  color: #333;
}

input[type="date"]::-webkit-calendar-picker-indicator {
  cursor: pointer;
  opacity: 0.6;
}

input[type="date"]::-webkit-calendar-picker-indicator:hover {
  opacity: 1;
}

/* Adjust padding for smaller screens */
@media screen and (max-width: 480px) {
  .form-popup.framework-form {
    width: 100%;
    max-width: 100%;
    left: 0;
    transform: none;
  }
  
  .form-popup.framework-form .form-section {
    padding: 12px;
  }
}

/* Nested Table Styles */
.main-policy-row {
  background-color: #f8f9fa;
  font-weight: 500;
}

.sub-policy-row {
  background-color: #ffffff;
}

.sub-policy-row:hover {
  background-color: #f8f9fa;
}

.sub-policy-cell {
  position: relative;
  padding-left: 30px !important;
}

.sub-policy-indicator {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #28a745;
}

.sub-policy-row td {
  border-top: 1px solid #e9ecef;
  border-bottom: 1px solid #e9ecef;
}

.sub-policy-row:last-child td {
  border-bottom: 1px solid #3c3c3c;
}

/* Extraction Popup Styles */
.extraction-popup-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  z-index: 2000;
  display: flex;
  align-items: center;
}
.extraction-popup {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 32px rgba(0,0,0,0.18);
  width: 700px;
  height: 480px;
  min-width: 1200px;
  min-height: 600px;
  max-width: 700px;
  max-height: 480px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 2px solid #007bff;
  margin-left: 190px;
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
}
.extraction-header {
  background: #f4f8ff;
  border-bottom: 1px solid #e0e0e0;
  padding: 18px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.extraction-body {
  padding: 32px 32px 24px 32px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-width: 350px;
  min-height: 200px;
  overflow-y: auto;
}
.extraction-slide {
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 15px;
  background: #f8faff;
  border-radius: 8px;
  padding: 18px 18px 12px 18px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.policy-slide {
  flex-direction: row;
  gap: 32px;
  background: #f8faff;
  align-items: flex-start;
}
.policy-main {
  min-width: 220px;
  max-width: 260px;
  margin-right: 18px;
}
.subpolicies-group {
  display: flex;
  flex-direction: row;
  gap: 18px;
  align-items: flex-start;
}

.extraction-subpolicy {
  background: #f4f8ff;
  border: 1px solid #cce5ff;
  border-radius: 8px;
  padding: 12px 10px 10px 10px;
  min-width: 180px;
  max-width: 220px;
  font-size: 14px;
  box-shadow: 0 1px 2px rgba(0,123,255,0.04);
}

.extraction-slide label {
  font-size: 13px;
  font-weight: 500;
  color: #007bff;
  margin-bottom: 2px;
}

.extraction-slide input,
.extraction-slide textarea {
  width: 100%;
  border: 1px solid #bcdffb;
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 14px;
  background: #fff;
  outline: none;
  margin-bottom: 6px;
  color: #222;
}

.extraction-slide textarea {
  min-height: 36px;
  resize: vertical;
}

@media (max-width: 700px) {
  .extraction-popup {
    min-width: 90vw;
    max-width: 98vw;
    padding: 0;
  }
  .extraction-body {
    padding: 12px 6px 12px 6px;
    min-width: 0;
  }
  .policy-slide {
    flex-direction: column;
    gap: 12px;
  }
  .subpolicies-group {
    flex-direction: column;
    gap: 10px;
  }
}

.extraction-stepper {
  display: flex;
  align-items: flex-end;
  border-bottom: 2px solid #222;
  background: none;
  margin: 0;
  padding: 0;
  position: relative;
  z-index: 2;
}
.extraction-step {
  display: flex;
  align-items: center;
  background: #fff;
  border: 2px solid #222;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  font-size: 16x;
  font-weight: 300;
  color: #222;
  padding: 10px 24px 8px 18px;
  margin-right: -2px;
  position: relative;
  z-index: 2;
  min-width: 120px;
  cursor: pointer;
  box-sizing: border-box;
  transition: background 0.15s, color 0.15s, z-index 0.15s;
}
.extraction-step.active {
  background: #fff;
  color: #222;
  font-weight: 700;
  z-index: 3;
  border-bottom: 2px solid #fff;
}
.extraction-step .tab-close {
  font-size: 20px;
  font-weight: 400;
  margin-left: 10px;
  color: #222;
  cursor: pointer;
  user-select: none;
  transition: color 0.15s;
}
.extraction-step .tab-close:hover {
  color: #d00;
}
</style> 