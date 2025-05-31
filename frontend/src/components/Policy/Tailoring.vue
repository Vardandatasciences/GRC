<template>
  <div class="tailoring-container">
    <h2 class="page-title">Policy Tailoring & Templating</h2>
    
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
        <button class="switch-btn" @click="switchToPolicy">Switch to Policy Dropdown</button>
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
      <button v-if="selectedPolicy === ''" class="switch-btn" @click="switchToFramework">Switch to Framework Dropdown</button>
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
        <button v-if="stepTabs.length > 1 && !showPolicyDropdown" class="add-btn add-policy-btn" @click="addPolicy">+ Add Policy</button>
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
            <!-- Add Remove Policy Button for Framework Copy Mode -->
            <!-- <div v-if="!showPolicyDropdown && stepIndex !== 0" class="policy-header">
              <h4>Policy {{ stepIndex }}</h4>
              <button type="button" class="remove-btn" @click="removePolicy(stepIndex-1)">Remove Policy</button>
            </div> -->
            <!-- Add Framework Selection Dropdown -->
            <div v-if="showPolicyDropdown" class="form-group span-full">i
              <label>Select Target Framework</label>
              <select v-model="selectedFramework" class="framework-select" required>
                <option value="">Select a framework</option>
                <option v-for="framework in frameworks" :key="framework.id" :value="framework.id">
                  {{ framework.name }}
                </option>
              </select>
              <p class="helper-text">Select the framework where you want to copy this policy</p>
              
              <!-- Add Policy Button -->
              <button type="button" class="add-btn" @click="addPolicyToCopy" v-if="selectedFramework">+ Add Another Policy</button>
            </div>
            <!-- Policy Forms Container -->
            <div v-for="(policy, policyIndex) in policiesData" :key="policyIndex" class="policy-form-container">
              <div class="policy-header">
                <h4>Policy {{ policyIndex + 1 }}</h4>
                <div class="policy-actions">
                  <button 
                    type="button" 
                    class="exclude-btn" 
                    :class="{ 'excluded': policy.exclude }"
                    @click="togglePolicyExclusion(policyIndex)"
                  >
                    {{ policy.exclude ? 'Excluded' : 'Exclude' }}
                  </button>
                  <button 
                    type="button" 
                    class="remove-btn" 
                    @click="removePolicyFromCopy(policyIndex)"
                  >
                    Remove Policy
                  </button>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Title</label>
                  <input type="text" v-model="policy.title" :required="!policy.exclude" placeholder="Enter policy title" />
                </div>
                <div class="form-group">
                  <label>Description</label>
                  <textarea v-model="policy.description" :required="!policy.exclude" placeholder="Enter policy description"></textarea>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Objective</label>
                  <textarea v-model="policy.objective" :required="!policy.exclude" placeholder="Enter policy objective"></textarea>
                </div>
                <div class="form-group">
                  <label>Scope</label>
                  <textarea v-model="policy.scope" :required="!policy.exclude" placeholder="Enter policy scope"></textarea>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Department</label>
                  <input type="text" v-model="policy.department" :required="!policy.exclude" placeholder="Enter department" />
                </div>
                <div class="form-group">
                  <label>Applicability</label>
                  <input type="text" v-model="policy.applicability" :required="!policy.exclude" placeholder="Enter applicability" />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Start Date</label>
                  <input type="date" v-model="policy.startDate" :required="!policy.exclude" />
                </div>
                <div class="form-group">
                  <label>End Date</label>
                  <input type="date" v-model="policy.endDate" :required="!policy.exclude" />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Document URL</label>
                  <input type="url" v-model="policy.docURL" placeholder="Enter document URL" />
                </div>
                <div class="form-group">
                  <label>Identifier</label>
                  <input type="text" v-model="policy.identifier" :required="!policy.exclude" placeholder="Enter identifier" />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Created By</label>
                  <select v-model="policy.createdByName" :required="!policy.exclude">
                    <option value="">Select Creator</option>
                    <option v-for="user in users" :key="user.UserId" :value="user.UserName">
                      {{ user.UserName }}
                    </option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Reviewer</label>
                  <select v-model="policy.reviewer" :required="!policy.exclude">
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
                    :required="!policy.exclude"
                  />
                </div>
              </div>
              
              <div class="subpolicies-section">
                <h4>Sub Policies</h4>
                <div class="subpolicies-row">
                  <div v-for="(sub, subIdx) in policy.subPolicies" :key="subIdx" class="subpolicy-card">
                    <div class="subpolicy-header">
                      <span class="subpolicy-title">Sub Policy {{ subIdx + 1 }}</span>
                      <div class="subpolicy-actions">
                        <button 
                          type="button" 
                          class="exclude-btn" 
                          :class="{ 'excluded': sub.exclude }"
                          @click="toggleSubPolicyExclusion(policyIndex, subIdx)"
                        >
                          {{ sub.exclude ? 'Excluded' : 'Exclude' }}
                        </button>
                      </div>
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                      <label>Title</label>
                      <input type="text" v-model="sub.title" required :disabled="sub.exclude" placeholder="Enter sub-policy title" />
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                      <label>Description</label>
                      <textarea v-model="sub.description" required :disabled="sub.exclude" placeholder="Enter sub-policy description"></textarea>
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                      <label>Control</label>
                      <textarea v-model="sub.control" required :disabled="sub.exclude" placeholder="Enter control details"></textarea>
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                      <label>Identifier</label>
                      <input type="text" v-model="sub.identifier" required :disabled="sub.exclude" placeholder="Enter identifier" />
                    </div>
                  </div>
                </div>
                <button type="button" class="add-btn" @click="addSubPolicy(policyIndex)">+ Add Sub Policy</button>
              </div>
            </div>
            <button class="create-btn" type="submit">
              {{ showPolicyDropdown ? 'Copy Policy' : 'Create Framework' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
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
      subPolicies: []
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
          objective: p.Objective,
          scope: p.Scope,
          department: p.Department,
          applicability: p.Applicability,
          startDate: p.StartDate,
          endDate: p.EndDate,
          docURL: p.DocURL,
          identifier: p.Identifier,
          createdByName: p.CreatedByName || '',
          reviewer: p.Reviewer || '',
          coverageRate: p.CoverageRate || null,
          subPolicies: p.subpolicies.map(sp => ({
            id: sp.SubPolicyId,
            title: sp.SubPolicyName,
            description: sp.Description,
            control: sp.Control,
            identifier: sp.Identifier
          }))
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
          throw new Error('Only Approved and Active policies can be copied')
        }
        
        // Reset framework selection
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
          coverageRate: response.data.CoverageRate || null,
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

        // Fetch available frameworks for the target selection
        await selectTargetFramework()
      } catch (err) {
        console.error('Error fetching policy details:', err)
        error.value = err.message || 'Failed to fetch policy details'
        policiesData.value = []
      } finally {
        loading.value = false
      }
    }

    // Update the selectTargetFramework function to filter out the current framework
    const selectTargetFramework = async () => {
      try {
        loading.value = true
        const response = await axios.get(`${API_BASE_URL}/frameworks/`)
        
        // Filter out inactive frameworks and sort by name
        frameworks.value = response.data
          .filter(fw => fw.ActiveInactive === 'Active')
          .map(fw => ({
            id: fw.FrameworkId,
            name: fw.FrameworkName
          }))
          .sort((a, b) => a.name.localeCompare(b.name))
      } catch (err) {
        console.error('Error fetching frameworks:', err)
        error.value = 'Failed to fetch frameworks'
      } finally {
        loading.value = false
      }
    }

    // Add watch for framework selection
    watch(selectedFramework, (newValue) => {
      if (newValue && showPolicyDropdown.value) {
        error.value = null // Clear any previous errors
      }
    })

    const switchToPolicy = () => {
      showPolicyDropdown.value = true
      selectedFramework.value = ''
      showStepper.value = false
      policiesData.value = []
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
      policiesData.value = []
      frameworkData.value = { title: '', description: '' }
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
        startDate: '',
        endDate: '',
        docURL: '',
        identifier: '',
        createdByName: '',
        reviewer: '',
        coverageRate: null,
        subPolicies: [],
        exclude: false
      })
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
      const subPolicy = policiesData.value[policyIdx].subPolicies[subIdx]
      subPolicy.exclude = !subPolicy.exclude
    }

    const removeSubPolicy = (policyIdx, subIdx) => {
      const subPolicy = policiesData.value[policyIdx].subPolicies[subIdx]
      if (subPolicy.id) {
        // If this is an existing subpolicy, mark it for exclusion
        subPolicy.exclude = true
      } else {
        // If it's a new subpolicy, remove it from the array
        policiesData.value[policyIdx].subPolicies.splice(subIdx, 1)
      }
    }

    const addSubPolicy = (policyIdx) => {
      policiesData.value[policyIdx].subPolicies.push({
        title: '',
        description: '',
        control: '',
        identifier: '',
        exclude: false
      })
    }

    const closeTab = (idx) => {
      if (idx === 0) return // Don't close framework tab
      removePolicy(idx - 1)
    }

    // Add these methods in the setup function
    const addPolicyToCopy = () => {
      policiesData.value.push({
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
        subPolicies: [],
        exclude: false
      })
    }

    const removePolicyFromCopy = (index) => {
      try {
        // Create a new array to ensure reactivity
        const updatedPolicies = [...policiesData.value];
        
        if (updatedPolicies[index]?.id) {
          // For existing policies, mark for exclusion
          updatedPolicies[index] = {
            ...updatedPolicies[index],
            exclude: true
          };
        } else {
          // For new policies, remove from array
          updatedPolicies.splice(index, 1);
        }
        
        // Update the reactive reference
        policiesData.value = updatedPolicies;
        
        // Update step index if needed
        if (stepIndex.value > index) {
          stepIndex.value--;
        }
        if (stepIndex.value >= stepTabs.value.length) {
          stepIndex.value = stepTabs.value.length - 1;
        }
      } catch (error) {
        console.error('Error removing policy:', error);
      }
    }

    // Update togglePolicyExclusion function
    const togglePolicyExclusion = (index) => {
      try {
        console.log('Toggling policy exclusion for index:', index);
        console.log('Current policy state:', policiesData.value[index]);
        
        const updatedPolicies = [...policiesData.value];
        updatedPolicies[index] = {
          ...updatedPolicies[index],
          exclude: !updatedPolicies[index].exclude
        };
        
        console.log('Updated policy state:', updatedPolicies[index]);
        console.log('Policy excluded:', updatedPolicies[index].exclude);
        
        policiesData.value = updatedPolicies;
      } catch (error) {
        console.error('Error toggling policy exclusion:', error);
      }
    }

    // Update submitFrameworkForm function
    const submitFrameworkForm = async () => {
      try {
        loading.value = true;
        console.log('Starting form submission...');
        console.log('Current policies data:', policiesData.value);

        if (showPolicyDropdown.value) {
          console.log('Processing policy copy mode...');
          // Copy policy/policies
          for (const policy of policiesData.value) {
            // Skip excluded policies
            if (policy.exclude) {
              console.log('Skipping excluded policy:', {
                id: policy.id,
                title: policy.title
              });
              continue;
            }

            // --- Updated subpolicies mapping for copy policy ---
            const subpolicies = policy.subPolicies
              .map(sp => {
                if (sp.id) {
                  // Existing subpolicy
                  return {
                    original_subpolicy_id: sp.id,
                    SubPolicyName: sp.title,
                    Description: sp.description,
                    Control: sp.control,
                    Identifier: sp.identifier,
                    Status: 'Under Review',
                    exclude: !!sp.exclude
                  };
                } else if (!sp.exclude) {
                  // New subpolicy (only send if not excluded)
                  return {
                    SubPolicyName: sp.title,
                    Description: sp.description,
                    Control: sp.control,
                    Identifier: sp.identifier,
                    Status: 'Under Review'
                  };
                }
                // If new and excluded, don't send at all
                return null;
              })
              .filter(Boolean);
            // --- End updated subpolicies mapping ---

            const policyData = {
              PolicyName: policy.title,
              TargetFrameworkId: parseInt(selectedFramework.value),
              PolicyDescription: policy.description,
              StartDate: policy.startDate,
              EndDate: policy.endDate,
              Department: policy.department,
              Applicability: policy.applicability,
              DocURL: policy.docURL || '',
              Scope: policy.scope,
              Objective: policy.objective,
              Identifier: policy.identifier,
              CreatedByName: policy.createdByName,
              Reviewer: policy.reviewer,
              CoverageRate: policy.coverageRate,
              CreatedByDate: new Date().toISOString().split('T')[0],
              PermanentTemporary: 'Permanent',
              subpolicies // <-- use the mapped subpolicies
            }

            if (!policy.id) {
              // Use the selected framework as the target for new policy
              await axios.post(`${API_BASE_URL}/frameworks/${selectedFramework.value}/policies/`, policyData);
            } else {
              // For existing policies, copy to new framework
              await axios.post(`${API_BASE_URL}/policies/${policy.id}/copy/`, policyData);
            }
          }
          
          // Show success message with correct count
          const activePolicies = policiesData.value.filter(p => !p.exclude).length;
          console.log('Submission complete. Active policies:', activePolicies);
          alert(`Successfully processed ${activePolicies} policy/policies to framework "${frameworks.value.find(f => f.id === selectedFramework.value)?.name || 'Unknown'}"`);
        } else {
          console.log('Processing framework copy mode...');
          // Copy framework
          const allPolicies = policiesData.value;

          const policies = allPolicies
            .filter(p => p.id)
            .map(p => ({
              original_policy_id: p.id,
              PolicyName: p.title,
              PolicyDescription: p.description,
              Objective: p.objective,
              Scope: p.scope,
              Department: p.department,
              Applicability: p.applicability,
              StartDate: p.startDate,
              EndDate: p.endDate,
              DocURL: p.docURL || '',
              Identifier: p.identifier,
              CreatedByName: p.createdByName,
              Reviewer: p.reviewer,
              CoverageRate: p.coverageRate,
              exclude: !!p.exclude,
              subpolicies: p.subPolicies
                .map(sp => {
                  if (sp.id) {
                    // Existing subpolicy
                    return {
                      original_subpolicy_id: sp.id,
                      SubPolicyName: sp.title,
                      Description: sp.description,
                      Control: sp.control,
                      Identifier: sp.identifier,
                      Status: 'Under Review',
                      exclude: !!sp.exclude
                    };
                  } else if (!sp.exclude) {
                    // New subpolicy (only send if not excluded)
                    return {
                      SubPolicyName: sp.title,
                      Description: sp.description,
                      Control: sp.control,
                      Identifier: sp.identifier,
                      Status: 'Under Review'
                    };
                  }
                  // If new and excluded, don't send at all
                  return null;
                })
                .filter(Boolean)
            }));

          const new_policies = allPolicies
            .filter(p => !p.id)
            .filter(p => !p.exclude)
            .map(p => ({
              PolicyName: p.title,
              PolicyDescription: p.description,
              Objective: p.objective,
              Scope: p.scope,
              Department: p.department,
              Applicability: p.applicability,
              StartDate: p.startDate,
              EndDate: p.endDate,
              DocURL: p.docURL || '',
              Identifier: p.identifier,
              CreatedByName: p.createdByName,
              Reviewer: p.reviewer,
              CoverageRate: p.coverageRate,
              subpolicies: p.subPolicies
                .filter(sp => !sp.exclude && !sp.id)
                .map(sp => ({
                  SubPolicyName: sp.title,
                  Description: sp.description,
                  Control: sp.control,
                  Identifier: sp.identifier,
                  Status: 'Under Review'
                }))
            }));

          const apiData = {
            FrameworkName: frameworkData.value.title,
            FrameworkDescription: frameworkData.value.description,
            Category: frameworkData.value.category,
            EffectiveDate: frameworkData.value.effectiveDate,
            StartDate: frameworkData.value.startDate,
            EndDate: frameworkData.value.endDate,
            DocURL: frameworkData.value.docURL || '',
            Identifier: frameworkData.value.identifier,
            CreatedByName: frameworkData.value.createdByName,
            Reviewer: frameworkData.value.reviewer,
            policies,
            new_policies
          };

          console.log('Submitting framework data:', apiData);
          const result = await axios.post(`${API_BASE_URL}/frameworks/${selectedFramework.value}/copy/`, apiData);
          console.log('Framework copy response:', result.data);
          alert(`Successfully created framework with ID: ${result.data.FrameworkId}`);
        }

        // Reset form after successful submission
        resetForm();
      } catch (err) {
        console.error('Error in form submission:', err);
        handleError(err);
      } finally {
        loading.value = false;
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
      console.error('Error submitting form:', err)
      const errorMessage = err.response?.data?.error || err.response?.data?.details?.error || 'Failed to submit form'
      error.value = errorMessage
      console.log('Full error details:', {
        error: err.response?.data,
        status: err.response?.status,
        headers: err.response?.headers
      })
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
      addPolicyToCopy,
      removePolicyFromCopy,
      togglePolicyExclusion
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
  gap: 10px;
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

/* Add new styles for policy actions */
.policy-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.exclude-btn {
  padding: 4px 12px;
  font-size: 12px;
  height: 28px;
  background: transparent;
  border: 1px solid #2575fc;
  color: #2575fc;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.exclude-btn.excluded {
  background: #ffebee;
  color: #d32f2f;
  border-color: #d32f2f;
}

.exclude-btn:hover {
  background: #2575fc;
  color: white;
}

.exclude-btn.excluded:hover {
  background: #d32f2f;
  color: white;
}
</style> 