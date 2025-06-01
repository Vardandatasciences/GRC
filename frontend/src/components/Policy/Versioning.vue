<template>
  <div class="tailoring-container">
    <h2 class="page-title">Versioning</h2>
    <div class="version-info">
      <p>Create new versions of frameworks or policies. New versions go through the same approval process as the original items.</p>
    </div>
    
    <!-- Framework Dropdown -->
    <div class="dropdown-container">
      <div v-if="!showPolicyDropdown" class="filter-group">
        <label for="frameworkSelect">SELECT FRAMEWORK</label>
        <div class="select-wrapper">
          <select id="frameworkSelect" v-model="selectedFramework" @change="onFrameworkDropdown">
            <option value="" disabled selected>Select a framework</option>
            <option v-for="framework in frameworks" :key="framework.id" :value="framework.id">
              {{ framework.name }}
            </option>
          </select>
        </div>
        <button class="switch-btn" @click="switchToPolicy">Switch to Policy Versioning</button>
      </div>
    </div>
    
    <!-- Policy Dropdown -->
    <div v-if="showPolicyDropdown" class="filter-group">
      <label for="policySelect">Select Policy</label>
      <div class="select-wrapper">
        <select id="policySelect" v-model="selectedPolicy" @change="onPolicyDropdown">
          <option value="" disabled selected>Select a policy</option>
          <option v-for="(policy, idx) in policyOptions" :key="idx" :value="idx">
            {{ policy.title }}
          </option>
        </select>
      </div>
      <button v-if="selectedPolicy === ''" class="switch-btn" @click="switchToFramework">Switch to Framework Versioning</button>
    </div>

    <div v-if="showStepper" class="stepper-container">
      <div class="stepper">
        <div
          v-for="(tab, idx) in stepTabs"
          :key="tab.key"
          :class="['step', { active: stepIndex === idx }]"
          @click="stepIndex = idx"
        >
          {{ tab.label }}
          <span v-if="stepIndex === idx && idx !== 0 && !showPolicyDropdown" class="tab-close" @click.stop="closeTab(idx)">X</span>
        </div>
        <button v-if="stepTabs.length > 1 && !showPolicyDropdown" class="add-btn add-policy-btn" @click="addPolicy">+ Add Policy to Version</button>
      </div>
      <div class="step-content">
        <!-- Framework Form - Only show when not in policy mode -->
        <div v-if="stepIndex === 0 && !showPolicyDropdown">
          <form class="form-section" @submit.prevent="submitFrameworkForm">
            <div class="form-row">
              <div class="form-group">
                <label>Title:</label>
                <input type="text" v-model="frameworkData.title" required />
              </div>
              <div class="form-group">
                <label>Description:</label>
                <textarea v-model="frameworkData.description" required></textarea>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Category:</label>
                <input type="text" v-model="frameworkData.category" required />
              </div>
              <div class="form-group">
                <label>Effective Date:</label>
                <input type="date" v-model="frameworkData.effectiveDate" required />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Start Date:</label>
                <input type="date" v-model="frameworkData.startDate" required />
              </div>
              <div class="form-group">
                <label>End Date:</label>
                <input type="date" v-model="frameworkData.endDate" required />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Document URL:</label>
                <input type="url" v-model="frameworkData.docURL" />
              </div>
              <div class="form-group">
                <label>Identifier:</label>
                <input type="text" v-model="frameworkData.identifier" required />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Created By</label>
                <select v-model="frameworkData.createdByName" required>
                  <option value="">Select Creator</option>
                  <option v-for="user in users" :key="user.UserId" :value="user.UserName">
                    {{ user.UserName }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Reviewer</label>
                <select v-model="frameworkData.reviewer" required>
                  <option value="">Select Reviewer</option>
                  <option v-for="user in users" :key="user.UserId" :value="user.UserName">
                    {{ user.UserName }}
                  </option>
                </select>
              </div>
            </div>
          </form>
        </div>
        
        <!-- Policy Form -->
        <div v-else>
          <form class="form-section policy-form" @submit.prevent="submitFrameworkForm">
            <h3 class="form-title">Policy Details</h3>
            
            <!-- Policy Forms Container -->
            <div v-for="(policy, policyIndex) in policiesData" :key="policyIndex" class="policy-form-container">
              <div class="policy-header">
                <h4>Policy Details</h4>
                <span v-if="!policy.id" class="policy-badge new-badge">New Policy</span>
                <span v-else class="policy-badge existing-badge">Existing Policy</span>
                <!-- Exclude button for existing policies -->
                <button
                  v-if="policy.id"
                  type="button"
                  class="exclude-btn"
                  @click="excludePolicy(policyIndex)"
                  :class="{ 'excluded': policy.exclude }"
                  style="margin-left: 16px;"
                >
                  {{ policy.exclude ? 'Excluded' : 'Exclude' }}
                </button>
              </div>
              <div v-if="!policy.exclude">
              <div class="form-row">
                <div class="form-group">
                    <label>Title <span class="required-field">*</span></label>
                    <input 
                      type="text" 
                      v-model="policy.title" 
                      required 
                      placeholder="Enter policy title" 
                      :class="{ 'field-error': isSubmitting && !policy.title }"
                    />
                    <span v-if="isSubmitting && !policy.title" class="error-text">Title is required</span>
                </div>
                <div class="form-group">
                    <label>Description <span class="required-field">*</span></label>
                    <textarea 
                      v-model="policy.description" 
                      required 
                      placeholder="Enter policy description"
                      :class="{ 'field-error': isSubmitting && !policy.description }"
                    ></textarea>
                    <span v-if="isSubmitting && !policy.description" class="error-text">Description is required</span>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Objective</label>
                  <textarea v-model="policy.objective" required placeholder="Enter policy objective"></textarea>
                </div>
                <div class="form-group">
                  <label>Scope</label>
                  <textarea v-model="policy.scope" required placeholder="Enter policy scope"></textarea>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Department</label>
                  <input type="text" v-model="policy.department" required placeholder="Enter department" />
                </div>
                <div class="form-group">
                  <label>Applicability</label>
                  <input type="text" v-model="policy.applicability" required placeholder="Enter applicability" />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Start Date</label>
                  <input type="date" v-model="policy.startDate" required />
                </div>
                <div class="form-group">
                  <label>End Date</label>
                  <input type="date" v-model="policy.endDate" required />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Document URL</label>
                  <input type="url" v-model="policy.docURL" placeholder="Enter document URL" />
                </div>
                <div class="form-group">
                    <label>Identifier <span class="required-field">*</span></label>
                    <input 
                      type="text" 
                      v-model="policy.identifier" 
                      required 
                      placeholder="Enter identifier"
                      :class="{ 'field-error': isSubmitting && !policy.identifier }"
                    />
                    <span v-if="isSubmitting && !policy.identifier" class="error-text">Identifier is required</span>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Created By</label>
                  <select v-model="policy.createdByName" required>
                    <option value="">Select Creator</option>
                    <option v-for="user in users" :key="user.UserId" :value="user.UserName">
                      {{ user.UserName }}
                    </option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Reviewer</label>
                  <select v-model="policy.reviewer" required>
                    <option value="">Select Reviewer</option>
                    <option v-for="user in users" :key="user.UserId" :value="user.UserName">
                      {{ user.UserName }}
                    </option>
                  </select>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Coverage Rate (%)</label>
                  <input 
                    type="number" 
                    v-model="policy.coverageRate" 
                    min="0" 
                    max="100" 
                    step="0.01" 
                    placeholder="Enter coverage rate"
                  />
                </div>
              </div>
              
              <div class="subpolicies-section">
                  <div class="subpolicies-header">
                <h4>Sub Policies</h4>
                    <div>
                      <span class="subpolicy-counter">{{ policy.subPolicies.filter(sp => !sp.exclude).length }} sub-policies</span>
                      <button 
                        type="button" 
                        class="debug-btn" 
                        @click="debugSubpolicies(policyIndex)"
                      >
                        Debug
                      </button>
                    </div>
                  </div>
                  
                  <div v-for="(sub, subIdx) in policy.subPolicies" :key="subIdx" class="subpolicy-card" :class="{ 'collapsed': sub.collapsed }">
                    <div class="subpolicy-header">
                      <div class="subpolicy-header-left">
                      <span class="subpolicy-title">Sub Policy {{ subIdx + 1 }}</span>
                        <button 
                          type="button" 
                          class="collapse-btn"
                          @click="toggleSubPolicyCollapse(policyIndex, subIdx)"
                        >
                          {{ sub.collapsed ? 'Expand' : 'Collapse' }}
                        </button>
                      </div>
                      <div class="subpolicy-actions">
                        <button 
                          type="button" 
                          class="exclude-btn" 
                          :class="{ 'excluded': sub.exclude }"
                          @click="toggleSubPolicyExclusion(policyIndex, subIdx)"
                        >
                          {{ sub.exclude ? 'Excluded' : 'Exclude' }}
                        </button>
                        <button 
                          type="button" 
                          class="remove-btn"
                          @click="removeSubPolicy(policyIndex, subIdx)"
                        >
                          Remove
                          </button>
                      </div>
                    </div>
                    
                    <div v-if="!sub.collapsed" class="subpolicy-content">
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                        <label>Title <span class="required-field">*</span></label>
                        <input 
                          type="text" 
                          v-model="sub.title" 
                          required 
                          :disabled="sub.exclude" 
                          placeholder="Enter sub-policy title"
                          :class="{ 'field-error': isSubmitting && !sub.exclude && !sub.title }"
                        />
                        <span v-if="isSubmitting && !sub.exclude && !sub.title" class="error-text">Title is required</span>
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                        <label>Description <span class="required-field">*</span></label>
                        <textarea 
                          v-model="sub.description" 
                          required 
                          :disabled="sub.exclude" 
                          placeholder="Enter sub-policy description"
                          :class="{ 'field-error': isSubmitting && !sub.exclude && !sub.description }"
                        ></textarea>
                        <span v-if="isSubmitting && !sub.exclude && !sub.description" class="error-text">Description is required</span>
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                      <label>Control</label>
                      <textarea v-model="sub.control" required :disabled="sub.exclude" placeholder="Enter control details"></textarea>
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                        <label>Identifier <span class="required-field">*</span></label>
                        <input 
                          type="text" 
                          v-model="sub.identifier" 
                          required 
                          :disabled="sub.exclude" 
                          placeholder="Enter identifier"
                          :class="{ 'field-error': isSubmitting && !sub.exclude && !sub.identifier }"
                        />
                        <span v-if="isSubmitting && !sub.exclude && !sub.identifier" class="error-text">Identifier is required</span>
                    </div>
                  </div>
                    
                    <div v-if="sub.collapsed" class="subpolicy-summary">
                      <strong>{{ sub.title || 'Untitled Subpolicy' }}</strong>
                      <span v-if="sub.identifier">({{ sub.identifier }})</span>
                </div>
                  </div>
                </div>
                <div class="add-subpolicy-container">
                  <button 
                    type="button" 
                    class="add-btn add-subpolicy-btn prominent-btn" 
                    @click="addSubPolicy(policyIndex)"
                  >
                    + Add Sub Policy (Count: {{ getSubpolicyCount(policyIndex) }})
                  </button>
                  <button 
                    type="button" 
                    class="reset-btn" 
                    @click="resetSubPolicies(policyIndex)"
                    v-if="policy.subPolicies.length > 0"
                  >
                    Clear All Sub Policies
                  </button>
                </div>
              </div>
            </div>
            <button class="create-btn" type="submit">
              {{ showPolicyDropdown ? 'Create Policy Version' : 'Create New Version' }}
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- Add loading overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>Processing your request...</p>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

export default {
  name: 'PolicyTailoring',
  setup() {
    const selectedFramework = ref('')
    const selectedPolicy = ref('')
    const showStepper = ref(false)
    const showPolicyDropdown = ref(false)
    const stepIndex = ref(0)
    const loading = ref(false)
    const error = ref(null)
    const isSubmitting = ref(false)

    const frameworks = ref([])
    const policyOptions = ref([])
    const users = ref([])

    const frameworkData = ref({
      title: '',
      description: '',
      category: '',
      effectiveDate: '',
      startDate: '',
      endDate: '',
      docURL: '',
      identifier: '',
      createdByName: '',
      reviewer: ''
    })

    const policiesData = ref([{
      title: '',
      description: '',
      objective: '',
      scope: '',
      department: '',
      applicability: '',
      startDate: '',
      endDate: '',
      docURL: '',
      identifier: '',
      createdByName: '',
      reviewer: '',
      coverageRate: null,
      subPolicies: [], // Initialize as empty reactive array
      exclude: false
    }])

    // Fetch frameworks for dropdown
    const fetchFrameworks = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/frameworks/`)
        frameworks.value = response.data.map(fw => ({
          id: fw.FrameworkId,
          name: fw.FrameworkName
        }))
      } catch (err) {
        console.error('Error fetching frameworks:', err)
        error.value = 'Failed to fetch frameworks'
      }
    }

    // Fetch framework details when selected
    const onFrameworkDropdown = async () => {
      if (!selectedFramework.value) return
      
      try {
        loading.value = true
        const response = await axios.get(`${API_BASE_URL}/frameworks/${selectedFramework.value}/`)
        
        // Populate framework data
        frameworkData.value = {
          title: response.data.FrameworkName,
          description: response.data.FrameworkDescription,
          category: response.data.Category,
          effectiveDate: response.data.EffectiveDate,
          startDate: response.data.StartDate,
          endDate: response.data.EndDate,
          docURL: response.data.DocURL,
          identifier: response.data.Identifier,
          createdByName: response.data.CreatedByName,
          reviewer: response.data.Reviewer
        }

        // Populate policies data
        policiesData.value = response.data.policies.map(p => ({
          id: p.PolicyId,
          title: p.PolicyName,
          description: p.PolicyDescription,
          objective: p.Objective || '',
          scope: p.Scope || '',
          department: p.Department || '',
          applicability: p.Applicability || '',
          startDate: p.StartDate || '',
          endDate: p.EndDate || '',
          docURL: p.DocURL || '',
          identifier: p.Identifier || '',
          createdByName: p.CreatedByName || '',
          reviewer: p.Reviewer || '',
          coverageRate: p.CoverageRate || null,
          exclude: false,
          subPolicies: Array.isArray(p.subpolicies) 
            ? p.subpolicies.map(sp => ({
            id: sp.SubPolicyId,
                title: sp.SubPolicyName || '',
                description: sp.Description || '',
                control: sp.Control || '',
                identifier: sp.Identifier || '',
                exclude: false,
                collapsed: false,
                Status: sp.Status || 'Under Review',
                PermanentTemporary: sp.PermanentTemporary || 'Permanent'
          }))
            : []
        }))

        showStepper.value = true
        stepIndex.value = 0
        showPolicyDropdown.value = false
        selectedPolicy.value = ''
      } catch (err) {
        console.error('Error fetching framework details:', err)
        error.value = 'Failed to fetch framework details'
      } finally {
        loading.value = false
      }
    }

    // Fetch policies for dropdown
    const fetchPolicies = async () => {
      try {
        loading.value = true
        const response = await axios.get(`${API_BASE_URL}/policies/`)
        // Check if response.data has a policies property and filter for Approved and Active policies
        const policiesData = response.data.policies || response.data
        policyOptions.value = policiesData
          .filter(p => p.Status === 'Approved' && p.ActiveInactive === 'Active')
          .map(p => ({
            id: p.PolicyId,
            title: p.PolicyName,
            description: p.PolicyDescription
          }))
      } catch (err) {
        console.error('Error fetching policies:', err)
        error.value = 'Failed to fetch policies'
      } finally {
        loading.value = false
      }
    }

    // Fetch policy details when selected
    const onPolicyDropdown = async () => {
      if (selectedPolicy.value === '') return
      
      try {
        loading.value = true
        const selectedPolicyData = policyOptions.value[selectedPolicy.value]
        if (!selectedPolicyData?.id) {
          throw new Error('Invalid policy selection')
        }

        const response = await axios.get(`${API_BASE_URL}/policies/${selectedPolicyData.id}/`)
        
        // Verify policy is Approved and Active
        if (response.data.Status !== 'Approved' || response.data.ActiveInactive !== 'Active') {
          throw new Error('Only Approved and Active policies can be versioned')
        }
        
        // Reset framework selection since it's not needed for policy versioning
        selectedFramework.value = ''
        
        // Populate single policy data
        policiesData.value = [{
          id: response.data.PolicyId,
          title: response.data.PolicyName,
          description: response.data.PolicyDescription,
          objective: response.data.Objective || '',
          scope: response.data.Scope || '',
          department: response.data.Department || '',
          applicability: response.data.Applicability || '',
          startDate: response.data.StartDate || '',
          endDate: response.data.EndDate || '',
          docURL: response.data.DocURL || '',
          identifier: response.data.Identifier || '',
          createdByName: response.data.CreatedByName || '',
          reviewer: response.data.Reviewer || '',
          // Filter for only Approved and Active subpolicies
          subPolicies: (response.data.subpolicies || [])
            .filter(sp => sp.Status === 'Approved' && sp.PermanentTemporary === 'Permanent')
            .map(sp => ({
              id: sp.SubPolicyId,
              title: sp.SubPolicyName,
              description: sp.Description,
              control: sp.Control || '',
              identifier: sp.Identifier || ''
            }))
        }]

      showStepper.value = true
        stepIndex.value = 0 // Show policy details immediately
      showPolicyDropdown.value = true
      } catch (err) {
        console.error('Error fetching policy details:', err)
        error.value = err.message || 'Failed to fetch policy details'
        policiesData.value = []
      } finally {
        loading.value = false
      }
    }

    const switchToPolicy = () => {
      showPolicyDropdown.value = true
      selectedFramework.value = ''
      showStepper.value = false
      stepIndex.value = 0
      policiesData.value = [{
        title: '',
        description: '',
        objective: '',
        scope: '',
        department: '',
        applicability: '',
        startDate: '',
        endDate: '',
        docURL: '',
        identifier: '',
        createdByName: '',
        reviewer: '',
        coverageRate: null,
        subPolicies: []
      }]
      frameworkData.value = {
        title: '',
        description: '',
        category: '',
        effectiveDate: '',
        startDate: '',
        endDate: '',
        docURL: '',
        identifier: '',
        createdByName: '',
        reviewer: ''
      }
      fetchPolicies() // Fetch policies when switching to policy view
    }

    const switchToFramework = () => {
      showPolicyDropdown.value = false
      selectedPolicy.value = ''
      showStepper.value = false
      stepIndex.value = 0
      policiesData.value = [{
        title: '',
        description: '',
        objective: '',
        scope: '',
        department: '',
        applicability: '',
        startDate: '',
        endDate: '',
        docURL: '',
        identifier: '',
        createdByName: '',
        reviewer: '',
        coverageRate: null,
        subPolicies: []
      }]
      frameworkData.value = {
        title: '',
        description: '',
        category: '',
        effectiveDate: '',
        startDate: '',
        endDate: '',
        docURL: '',
        identifier: '',
        createdByName: '',
        reviewer: ''
      }
      fetchFrameworks()
    }

    const addPolicy = () => {
      policiesData.value.push({
        title: '',
        description: '',
        objective: '',
        scope: '',
        department: '',
        applicability: '',
        startDate: new Date().toISOString().split('T')[0], // Default to today
        endDate: '',
        docURL: '',
        identifier: '',
        createdByName: frameworkData.value.createdByName || '', // Inherit from framework
        reviewer: frameworkData.value.reviewer || '', // Inherit from framework
        coverageRate: null,
        subPolicies: [], // Initialize as empty array
        exclude: false
      })
      console.log('Added new policy. Policy count:', policiesData.value.length)
      console.log('New policy has subPolicies array:', Array.isArray(policiesData.value[policiesData.value.length-1].subPolicies))
      stepIndex.value = policiesData.value.length // Go to new policy tab
    }

    const removePolicy = (idx) => {
      // If this is an existing policy, mark it for exclusion in the API request
      if (policiesData.value[idx].id) {
        policiesData.value[idx].exclude = true
      } else {
        // If it's a new policy, remove it from the array
      policiesData.value.splice(idx, 1)
      }
      if (stepIndex.value > idx) stepIndex.value--
      if (stepIndex.value >= stepTabs.value.length) stepIndex.value = stepTabs.value.length - 1
    }

    const toggleSubPolicyExclusion = (policyIdx, subIdx) => {
      // Create a temp copy of the entire policies array
      const policiesCopy = JSON.parse(JSON.stringify(policiesData.value));
      
      // Toggle the exclude state in the copy
      policiesCopy[policyIdx].subPolicies[subIdx].exclude = 
        !policiesCopy[policyIdx].subPolicies[subIdx].exclude;
      
      // Replace the entire array to trigger reactivity
      policiesData.value = policiesCopy;
    }

    const removeSubPolicy = (policyIdx, subIdx) => {
      console.log('Removing subpolicy at index', subIdx, 'from policy', policyIdx);
      
      // Create a temp copy of the entire policies array
      const policiesCopy = JSON.parse(JSON.stringify(policiesData.value));
      
      // Remove the subpolicy from the copy
      policiesCopy[policyIdx].subPolicies.splice(subIdx, 1);
      
      // Replace the entire array to trigger reactivity
      policiesData.value = policiesCopy;
      
      console.log('Subpolicy removed. Total count:', policiesData.value[policyIdx].subPolicies.length);
    };

    const addSubPolicy = (policyIdx) => {
      console.log('Adding subpolicy to policy index:', policyIdx);
      
      // Create a temp copy of the entire policies array
      const policiesCopy = JSON.parse(JSON.stringify(policiesData.value));
      
      // Create the new subpolicy
      const newSubPolicy = {
        title: '',
        description: '',
        control: '',
        identifier: '',
        exclude: false,
        collapsed: false,
        Status: 'Under Review',
        PermanentTemporary: 'Permanent'
      };
      
      // Ensure the subPolicies array exists
      if (!Array.isArray(policiesCopy[policyIdx].subPolicies)) {
        policiesCopy[policyIdx].subPolicies = [];
      }
      
      // Add the new subpolicy to the copy
      policiesCopy[policyIdx].subPolicies.push(newSubPolicy);
      
      // Replace the entire array to trigger reactivity
      policiesData.value = policiesCopy;
      
      console.log('New subpolicy added. Total count:', policiesData.value[policyIdx].subPolicies.length);
    };

    const closeTab = (idx) => {
      if (idx === 0) return // Don't close framework tab
      removePolicy(idx - 1)
    }

    // Add a function to check and repair subpolicies array if needed
    const ensureSubPoliciesArray = () => {
      for (let i = 0; i < policiesData.value.length; i++) {
        const policy = policiesData.value[i];
        if (!Array.isArray(policy.subPolicies)) {
          console.warn(`Policy at index ${i} has invalid subPolicies. Fixing...`);
          policy.subPolicies = [];
        }
      }
    }

    // Modify the submitFrameworkForm function to handle policy versioning correctly
    const submitFrameworkForm = async () => {
      try {
        isSubmitting.value = true;
        error.value = null;
        
        // Ensure all policies have a valid subPolicies array
        ensureSubPoliciesArray();
        
        // Validate framework data in framework mode
        if (!showPolicyDropdown.value && stepIndex.value === 0) {
          if (!frameworkData.value.title) {
            error.value = 'Framework title is required';
            return;
          }
          if (!frameworkData.value.description) {
            error.value = 'Framework description is required';
            return;
          }
          if (!frameworkData.value.identifier) {
            error.value = 'Framework identifier is required';
            return;
          }
          if (!frameworkData.value.createdByName) {
            error.value = 'Created By is required';
            return;
          }
          if (!frameworkData.value.reviewer) {
            error.value = 'Reviewer is required';
            return;
          }
        }
        
        // Validate policies in both modes
          for (const policy of policiesData.value) {
          if (policy.exclude) continue;
          
          if (!policy.title) {
            error.value = 'Policy title is required';
            return;
          }
          if (!policy.description) {
            error.value = 'Policy description is required';
            return;
          }
          if (!policy.identifier) {
            error.value = 'Policy identifier is required';
            return;
          }
          
          // Validate subpolicies
          for (const subpolicy of policy.subPolicies) {
            if (subpolicy.exclude) continue;
            
            if (!subpolicy.title) {
              error.value = 'Subpolicy title is required';
              return;
            }
            if (!subpolicy.description) {
              error.value = 'Subpolicy description is required';
              return;
            }
            if (!subpolicy.identifier) {
              error.value = 'Subpolicy identifier is required';
              return;
            }
          }
        }
        
        // If validation passes, proceed with API calls
        loading.value = true;

        if (showPolicyDropdown.value) {
          // Create new policy version - should only have one policy
          if (policiesData.value.length === 0 || policiesData.value[0].exclude) {
            throw new Error('No policy data to submit')
          }
          
          const policy = policiesData.value[0] // Get the first (and only) policy

          // Separate existing and new subpolicies
          const existingSubpolicies = [];
          const newSubpolicies = [];
          for (const sp of policy.subPolicies) {
            if (sp.id) {
              // Existing subpolicy
              if (sp.exclude) {
                existingSubpolicies.push({ original_subpolicy_id: sp.id, exclude: true });
              } else {
                existingSubpolicies.push({
                  original_subpolicy_id: sp.id,
                  SubPolicyName: sp.title,
                  Description: sp.description,
                  Control: sp.control,
                  Identifier: sp.identifier,
                  PermanentTemporary: 'Permanent'
                });
              }
            } else if (!sp.exclude) {
              // New subpolicy (no id, not excluded)
              newSubpolicies.push({
                SubPolicyName: sp.title,
                Description: sp.description,
                Control: sp.control,
                Identifier: sp.identifier,
                PermanentTemporary: 'Permanent'
              });
            }
          }

            const policyData = {
              PolicyName: policy.title,
              PolicyDescription: policy.description,
              StartDate: policy.startDate,
              EndDate: policy.endDate,
              Department: policy.department,
              Applicability: policy.applicability,
              DocURL: policy.docURL,
              Scope: policy.scope,
              Objective: policy.objective,
              Identifier: policy.identifier,
              CreatedByName: policy.createdByName,
            Reviewer: users.value.find(u => u.UserName === policy.reviewer)?.UserId || null,
              CoverageRate: policy.coverageRate,
              CreatedByDate: new Date().toISOString().split('T')[0],
              PermanentTemporary: 'Permanent',
            subpolicies: existingSubpolicies,
            new_subpolicies: newSubpolicies
          };

          console.log('Submitting policy version with data:', policyData);

          try {
            await axios.post(`${API_BASE_URL}/policies/${policy.id}/create-version/`, policyData);
            alert(`Successfully created new version for policy "${policy.title}"`);
          } catch (err) {
            console.error('Policy version creation error:', err.response?.data);
            error.value = err.response?.data?.error || 'Failed to create policy version';
            return; // Stop execution on error
          }
        } else {
          // Create new framework version
          const existingPolicies = policiesData.value.filter(p => p.id); // include all existing policies
          const newPolicies = policiesData.value.filter(p => !p.id && !p.exclude);

          const apiData = {
            FrameworkName: frameworkData.value.title,
            FrameworkDescription: frameworkData.value.description,
            Category: frameworkData.value.category,
            EffectiveDate: frameworkData.value.effectiveDate,
            StartDate: frameworkData.value.startDate,
            EndDate: frameworkData.value.endDate,
            DocURL: frameworkData.value.docURL,
            Identifier: frameworkData.value.identifier,
            CreatedByName: frameworkData.value.createdByName,
            Reviewer: users.value.find(u => u.UserName === frameworkData.value.reviewer)?.UserId || null,
          };

          // Add existing policies (with original_policy_id)
          if (existingPolicies.length > 0) {
            apiData.policies = existingPolicies.map(p => {
              if (p.exclude) {
                return {
                  original_policy_id: p.id,
                  exclude: true
                };
              } else {
                return {
                original_policy_id: p.id,
                PolicyName: p.title,
                PolicyDescription: p.description,
                Objective: p.objective,
                Scope: p.scope,
                Department: p.department,
                Applicability: p.applicability,
                StartDate: p.startDate,
                EndDate: p.endDate,
                DocURL: p.docURL,
                Identifier: p.identifier,
                CreatedByName: p.createdByName,
                  Reviewer: users.value.find(u => u.UserName === p.reviewer)?.UserId || null,
                CoverageRate: p.coverageRate,
                  subpolicies: p.subPolicies.map(sp => {
                    if (sp.exclude) {
                      return { original_subpolicy_id: sp.id, exclude: true };
                    } else {
                      return {
                    original_subpolicy_id: sp.id,
                    SubPolicyName: sp.title,
                    Description: sp.description,
                    Control: sp.control,
                    Identifier: sp.identifier,
                    Status: 'Under Review'
                      };
                    }
                  })
                };
              }
            });
          }

          // Add new policies to new_policies array
          if (newPolicies.length > 0) {
            apiData.new_policies = newPolicies.map(p => {
              // Validate required fields for new policies
              if (!p.title || !p.description || !p.identifier) {
                error.value = `New policy missing required fields: ${!p.title ? 'Title, ' : ''}${!p.description ? 'Description, ' : ''}${!p.identifier ? 'Identifier' : ''}`;
                throw new Error(error.value);
              }
              
              return {
                PolicyName: p.title,
                PolicyDescription: p.description,
                Objective: p.objective,
                Scope: p.scope,
                Department: p.department,
                Applicability: p.applicability,
                StartDate: p.startDate,
                EndDate: p.endDate,
                DocURL: p.docURL,
                Identifier: p.identifier,
                CreatedByName: p.createdByName,
                Reviewer: users.value.find(u => u.UserName === p.reviewer)?.UserId || null,
                CoverageRate: p.coverageRate,
                subpolicies: p.subPolicies.filter(sp => !sp.exclude).map(sp => {
                  // Validate required fields for subpolicies
                  if (!sp.title || !sp.description || !sp.identifier) {
                    error.value = `Subpolicy missing required fields: ${!sp.title ? 'Title, ' : ''}${!sp.description ? 'Description, ' : ''}${!sp.identifier ? 'Identifier' : ''}`;
                    throw new Error(error.value);
                  }
                  return {
                    SubPolicyName: sp.title,
                    Description: sp.description,
                    Control: sp.control,
                    Identifier: sp.identifier,
                    Status: 'Under Review',
                    PermanentTemporary: 'Permanent'
                  };
                })
              };
            });
          }

          // Before the API call, add this debugging info
          console.log('Framework versioning - Existing policies:', existingPolicies.length);
          console.log('Framework versioning - New policies:', newPolicies.length);
          if (newPolicies.length > 0) {
            console.log('New policies details:', newPolicies.map(p => ({
              title: p.title,
              subPoliciesCount: p.subPolicies.filter(sp => !sp.exclude).length
            })));
          }
          console.log('Submitting framework version with data:', apiData);

          try {
            const result = await axios.post(`${API_BASE_URL}/frameworks/${selectedFramework.value}/create-version/`, apiData);
            alert(`Successfully created new framework version: ${result.data.FrameworkName} (Version ${result.data.NewVersion}.0)`);
          } catch (err) {
            console.error('Framework version creation error:', err.response?.data);
            error.value = err.response?.data?.error || 'Failed to create framework version';
            return; // Stop execution on error
          }
        }

        // Reset form after successful submission
        resetForm()
      } catch (err) {
        handleError(err)
      } finally {
        loading.value = false
        // Keep isSubmitting true if there were validation errors
        if (!error.value) {
          isSubmitting.value = false;
        }
      }
    }

    // Add helper function to reset form
    const resetForm = () => {
      showStepper.value = false
      selectedFramework.value = ''
      selectedPolicy.value = ''
      policiesData.value = [{
        title: '',
        description: '',
        objective: '',
        scope: '',
        department: '',
        applicability: '',
        startDate: '',
        endDate: '',
        docURL: '',
        identifier: '',
        createdByName: '',
        reviewer: '',
        coverageRate: null,
        subPolicies: []
      }]
      frameworkData.value = {
        title: '',
        description: '',
        category: '',
        effectiveDate: '',
        startDate: '',
        endDate: '',
        docURL: '',
        identifier: '',
        createdByName: '',
        reviewer: ''
      }
    }

    // Add helper function to handle errors
    const handleError = (err) => {
      console.error('Error submitting form:', err);
      const errorData = err.response?.data;
      let errorMessage = 'Failed to submit form';
      
      if (typeof errorData === 'object') {
        if (errorData.error) {
          errorMessage = errorData.error;
        } else if (errorData.details?.error) {
          errorMessage = errorData.details.error;
        } else {
          // Try to extract error message from the response object
          errorMessage = JSON.stringify(errorData);
        }
      } else if (typeof errorData === 'string') {
        errorMessage = errorData;
      }
      
      error.value = errorMessage;
      console.log('Full error details:', {
        error: errorData,
        status: err.response?.status,
        headers: err.response?.headers
      });
    }

    // Computed property for step tabs - show only policy tab in policy mode
    const stepTabs = computed(() => {
      if (showPolicyDropdown.value) {
        return [{ key: 'policy', label: 'Policy Details' }]
      }
      return [
        { key: 'framework', label: 'Framework' },
        ...policiesData.value.map((p, i) => ({ key: `policy${i+1}`, label: `Policy ${i+1}` }))
      ]
    })

    // Add function to fetch users
    const fetchUsers = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/users/`)
        users.value = response.data
      } catch (err) {
        console.error('Error fetching users:', err)
        error.value = 'Failed to fetch users'
      }
    }

    // Modify onMounted to fetch users
    onMounted(() => {
      fetchFrameworks()
      fetchUsers()
    })

    const toggleSubPolicyCollapse = (policyIdx, subIdx) => {
      // Create a temp copy of the entire policies array
      const policiesCopy = JSON.parse(JSON.stringify(policiesData.value));
      
      // Toggle the collapsed state in the copy
      policiesCopy[policyIdx].subPolicies[subIdx].collapsed = 
        !policiesCopy[policyIdx].subPolicies[subIdx].collapsed;
      
      // Replace the entire array to trigger reactivity
      policiesData.value = policiesCopy;
    };

    const debugSubpolicies = (policyIdx) => {
      console.log('DEBUG - Policy index:', policyIdx);
      console.log('DEBUG - Subpolicies count:', policiesData.value[policyIdx].subPolicies.length);
      console.log('DEBUG - Subpolicies array:', JSON.stringify(policiesData.value[policyIdx].subPolicies));
      
      // Show alert with count for immediate feedback
      alert(`This policy has ${policiesData.value[policyIdx].subPolicies.length} subpolicies. Check browser console for details.`);
    };

    // Update the resetSubPolicies function to use the same pattern
    const resetSubPolicies = (policyIdx) => {
      if (confirm('Are you sure you want to remove all subpolicies? This cannot be undone.')) {
        console.log('Resetting all subpolicies for policy at index', policyIdx);
        
        // Create a temp copy of the entire policies array
        const policiesCopy = JSON.parse(JSON.stringify(policiesData.value));
        
        // Reset the subpolicies to an empty array
        policiesCopy[policyIdx].subPolicies = [];
        
        // Replace the entire array to trigger reactivity
        policiesData.value = policiesCopy;
        
        console.log('All subpolicies removed. Current count:', policiesData.value[policyIdx].subPolicies.length);
      }
    };

    // Add a computed property to track subpolicy counts
    const getSubpolicyCount = (policyIndex) => {
      if (!policiesData.value[policyIndex] || 
          !Array.isArray(policiesData.value[policyIndex].subPolicies)) {
        return 0;
      }
      return policiesData.value[policyIndex].subPolicies.length;
    };

    // Add the excludePolicy method to setup()
    const excludePolicy = (policyIdx) => {
      // Create a deep copy to keep reactivity
      const policiesCopy = JSON.parse(JSON.stringify(policiesData.value));

      // Mark the policy as excluded instead of removing it
      policiesCopy[policyIdx].exclude = true;

      // Update the reactive array
      policiesData.value = policiesCopy;

      // Adjust stepIndex if needed
      if (stepIndex.value >= policiesData.value.length) {
        stepIndex.value = Math.max(0, policiesData.value.length - 1);
      }
    };


    return {
      selectedFramework,
      selectedPolicy,
      frameworks,
      showStepper,
      showPolicyDropdown,
      stepIndex,
      stepTabs,
      frameworkData,
      policiesData,
      policyOptions,
      loading,
      error,
      onFrameworkDropdown,
      onPolicyDropdown,
      switchToPolicy,
      switchToFramework,
      addPolicy,
      removePolicy,
      addSubPolicy,
      removeSubPolicy,
      closeTab,
      submitFrameworkForm,
      toggleSubPolicyExclusion,
      users,
      isSubmitting,
      toggleSubPolicyCollapse,
      debugSubpolicies,
      resetSubPolicies,
      getSubpolicyCount,
      excludePolicy
    }
  }
}
</script>

<style scoped>
/* Add loading and error styles */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background: #ff4444;
  color: white;
  padding: 12px 20px;
  border-radius: 4px;
  margin-bottom: 20px;
}

/* Add new styles */
.framework-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-top: 4px;
}

.framework-select:focus {
  border-color: #2196f3;
  outline: none;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

.helper-text {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
  margin-bottom: 0;
}

/* Keep existing styles */
@import './tailoring.css';

/* Add new styles */
.policy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.subpolicy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.subpolicy-actions {
  display: flex;
  gap: 8px;
}

.exclude-btn {
  padding: 4px 8px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.exclude-btn.excluded {
  background-color: #ffebee;
  color: #d32f2f;
  border-color: #d32f2f;
}

.excluded {
  opacity: 0.6;
  background-color: #f5f5f5;
}

.remove-btn {
  padding: 4px 8px;
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #d32f2f;
  border-radius: 4px;
  cursor: pointer;
}

.remove-btn:hover {
  background-color: #d32f2f;
  color: white;
}

/* Add these styles */
select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-top: 4px;
}

select:focus {
  border-color: #2196f3;
  outline: none;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

/* Policy form container specific styles */
.policy-form-container {
  background: #f8fafc;
  padding: 24px;
  border-radius: 12px;
  margin-top: 24px;
  border: 2px solid #e2e8f0;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

/* Form row inside policy container */
.policy-form-container .form-row {
  display: flex;
  gap: 20px;
  width: 100%;
  box-sizing: border-box;
  padding: 0 10px;
  flex-wrap: wrap;
}

/* Form group inside policy container */
.policy-form-container .form-group {
  flex: 1 1 0;
  min-width: 220px;
  margin-bottom: 15px;
  box-sizing: border-box;
}

/* Input fields inside policy container */
.policy-form-container .form-group input,
.policy-form-container .form-group textarea,
.policy-form-container .form-group select {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  padding: 8px 12px;
  font-size: 14px;
}

/* Remove policy button */
.policy-form-container .remove-btn {
  padding: 4px 12px;
  font-size: 12px;
  height: 28px;
  background: transparent;
  border: 1px solid #e74c3c;
  color: #e74c3c;
}

/* Add responsive styles */
@media screen and (max-width: 768px) {
  .policy-form-container .form-group {
    flex: 1 1 100%;
    max-width: 100%;
  }
  
  .policy-form-container .form-row {
    gap: 10px;
  }
}

/* Add styles for version-info section */
.version-info {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 20px;
  border-left: 4px solid #2196f3;
}

.version-info p {
  margin: 0;
  color: #333;
  font-size: 14px;
  line-height: 1.4;
}

/* Add badge styles */
.policy-badge {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.new-badge {
  background-color: #e3f2fd;
  color: #1976d2;
  border: 1px solid #bbdefb;
}

.existing-badge {
  background-color: #e8f5e9;
  color: #388e3c;
  border: 1px solid #c8e6c9;
}

.required-field {
  color: #f44336;
  margin-left: 2px;
}

.field-error {
  border-color: #f44336 !important;
  background-color: rgba(244, 67, 54, 0.05);
}

.error-text {
  color: #f44336;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

.add-subpolicy-container {
  margin-top: 16px;
  text-align: center;
}

.add-subpolicy-btn {
  background-color: #e3f2fd;
  color: #1976d2;
  border: 1px solid #bbdefb;
  padding: 8px 16px;
  font-weight: 500;
}

.add-subpolicy-btn:hover {
  background-color: #bbdefb;
}

.subpolicy-card {
  position: relative;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  background-color: #fafafa;
}

.subpolicy-card:hover {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.subpolicies-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.subpolicy-counter {
  background-color: #e8f5e9;
  color: #388e3c;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.subpolicy-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.collapse-btn {
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.subpolicy-card.collapsed {
  padding: 10px 16px;
}

.subpolicy-summary {
  padding: 4px 0;
  color: #555;
}

.subpolicy-content {
  margin-top: 10px;
}

.prominent-btn {
  background-color: #2196f3;
  color: white;
  font-weight: bold;
  padding: 10px 20px;
  border-radius: 8px;
  margin-top: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transition: all 0.2s;
}

.prominent-btn:hover {
  background-color: #1976d2;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.prominent-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.debug-btn {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-left: 8px;
  cursor: pointer;
}

.debug-btn:hover {
  background-color: #e0e0e0;
}

.reset-btn {
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #ffcdd2;
  padding: 8px 16px;
  border-radius: 8px;
  margin-top: 16px;
  margin-left: 16px;
  font-weight: 500;
  cursor: pointer;
}

.reset-btn:hover {
  background-color: #ffcdd2;
}
</style> 