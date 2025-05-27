<template>
  <div class="tailoring-container">
    <h2 class="page-title">Policy Tailoring & Templating</h2>
    
    <div class="filters-container">
      <!-- Framework Dropdown -->
      <div v-if="!showPolicyDropdown" class="filter-group">
        <label for="frameworkSelect">Select Framework</label>
        <div class="select-wrapper">
          <select id="frameworkSelect" v-model="selectedFramework" @change="onFrameworkDropdown">
            <option value="" disabled selected>Select a framework</option>
            <option v-for="framework in frameworks" :key="framework.id" :value="framework.id">
              {{ framework.name }}
            </option>
          </select>
        </div>
        <button v-if="selectedFramework === ''" class="switch-btn" @click="switchToPolicy">Switch to Policy Dropdown</button>
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
          <form class="form-section">
            <div class="form-group">
              <label>Title:</label>
              <input type="text" v-model="frameworkData.title" required />
            </div>
            <div class="form-group">
              <label>Description:</label>
              <textarea v-model="frameworkData.description" required></textarea>
            </div>
            <div class="form-group">
              <label>Category:</label>
              <input type="text" v-model="frameworkData.category" required />
            </div>
            <div class="form-group">
              <label>Effective Date:</label>
              <input type="date" v-model="frameworkData.effectiveDate" required />
            </div>
            <div class="form-group">
              <label>Start Date:</label>
              <input type="date" v-model="frameworkData.startDate" required />
            </div>
            <div class="form-group">
              <label>End Date:</label>
              <input type="date" v-model="frameworkData.endDate" required />
            </div>
            <div class="form-group">
              <label>Document URL:</label>
              <input type="url" v-model="frameworkData.docURL" />
            </div>
            <div class="form-group">
              <label>Identifier:</label>
              <input type="text" v-model="frameworkData.identifier" required />
            </div>
          </form>
        </div>
        <!-- Policy Form -->
        <div v-else>
          <form class="form-section policy-form" @submit.prevent="submitFrameworkForm">
            <h3>Policy Details</h3>
            <!-- Add Remove Policy Button for Framework Copy Mode -->
            <div v-if="!showPolicyDropdown && stepIndex !== 0" class="policy-header">
              <h4>Policy {{ stepIndex }}</h4>
              <button type="button" class="remove-btn" @click="removePolicy(stepIndex-1)">Remove Policy</button>
            </div>
            <!-- Add Framework Selection Dropdown -->
            <div v-if="showPolicyDropdown" class="form-group">
              <label>Select Target Framework:</label>
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
              <div class="policy-header" v-if="policyIndex > 0">
                <h4>Policy {{ policyIndex + 1 }}</h4>
                <button type="button" class="remove-btn" @click="removePolicyFromCopy(policyIndex)">Remove Policy</button>
              </div>
              
              <div class="form-group">
                <label>Title:</label>
                <input type="text" v-model="policy.title" required />
              </div>
              <div class="form-group">
                <label>Description:</label>
                <textarea v-model="policy.description" required></textarea>
              </div>
              <div class="form-group">
                <label>Objective:</label>
                <textarea v-model="policy.objective" required></textarea>
              </div>
              <div class="form-group">
                <label>Scope:</label>
                <textarea v-model="policy.scope" required></textarea>
              </div>
              <div class="form-group">
                <label>Department:</label>
                <input type="text" v-model="policy.department" required />
              </div>
              <div class="form-group">
                <label>Applicability:</label>
                <input type="text" v-model="policy.applicability" required />
              </div>
              <div class="form-group">
                <label>Start Date:</label>
                <input type="date" v-model="policy.startDate" required />
              </div>
              <div class="form-group">
                <label>End Date:</label>
                <input type="date" v-model="policy.endDate" required />
              </div>
              <div class="form-group">
                <label>Document URL:</label>
                <input type="url" v-model="policy.docURL" />
              </div>
              <div class="form-group">
                <label>Identifier:</label>
                <input type="text" v-model="policy.identifier" required />
              </div>
              <div class="form-group">
                <label>Created By:</label>
                <select v-model="policy.createdByName" required>
                  <option value="">Select Creator</option>
                  <option v-for="user in users" :key="user.UserId" :value="user.UserId">
                    {{ user.UserName }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Reviewer:</label>
                <select v-model="policy.reviewer" required>
                  <option value="">Select Reviewer</option>
                  <option v-for="user in users" :key="user.UserId" :value="user.UserId">
                    {{ user.UserName }}
                  </option>
                </select>
              </div>
              <div class="subpolicies-section">
                <h4>Sub Policies</h4>
                <div class="subpolicies-row">
                  <div v-for="(sub, subIdx) in policy.subPolicies" :key="subIdx" class="subpolicy-card">
                    <div class="subpolicy-header">
                      <span class="subpolicy-title">Sub Policy {{ subIdx + 1 }}</span>
                      <div class="subpolicy-actions">
                        <button 
                          v-if="sub.id" 
                          type="button" 
                          class="exclude-btn" 
                          :class="{ 'excluded': sub.exclude }"
                          @click="toggleSubPolicyExclusion(policyIndex, subIdx)"
                        >
                          {{ sub.exclude ? 'Excluded' : 'Exclude' }}
                        </button>
                        <button type="button" class="remove-btn" @click="removeSubPolicy(policyIndex, subIdx)">Remove</button>
                      </div>
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                      <label>Title:</label>
                      <input type="text" v-model="sub.title" required :disabled="sub.exclude" />
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                      <label>Description:</label>
                      <textarea v-model="sub.description" required :disabled="sub.exclude"></textarea>
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                      <label>Control:</label>
                      <textarea v-model="sub.control" required :disabled="sub.exclude"></textarea>
                    </div>
                    <div class="form-group" :class="{ 'excluded': sub.exclude }">
                      <label>Identifier:</label>
                      <input type="text" v-model="sub.identifier" required :disabled="sub.exclude" />
                    </div>
                  </div>
                </div>
                <button type="button" class="add-btn" @click="addSubPolicy(policyIndex)">+ Add Sub Policy</button>
              </div>
            </div>
            <button
              class="create-btn"
              type="submit"
            >
              Submit
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
      identifier: ''
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
          identifier: response.data.Identifier
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
        identifier: ''
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
        subPolicies: []
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
        identifier: ''
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
        subPolicies: []
      })
    }

    const removePolicyFromCopy = (index) => {
      policiesData.value.splice(index, 1)
    }

    // Modify the submitFrameworkForm function to handle multiple policies
    const submitFrameworkForm = async () => {
      try {
        loading.value = true

        if (showPolicyDropdown.value) {
          // Copy policy/policies
          for (const policy of policiesData.value) {
            const policyData = {
              PolicyName: policy.title,
              TargetFrameworkId: parseInt(selectedFramework.value),
              PolicyDescription: policy.description,
              StartDate: policy.startDate,
              EndDate: policy.endDate,
              Department: policy.department,
              Applicability: policy.applicability,
              DocURL: policy.docURL,
              Scope: policy.scope,
              Objective: policy.objective,
              Identifier: policy.identifier,
              CreatedByUserId: policy.createdByName, // This now contains UserId
              Reviewer: policy.reviewer, // This now contains UserId
              CreatedByDate: new Date().toISOString().split('T')[0],
              PermanentTemporary: 'Permanent',
              subpolicies: policy.subPolicies
                .filter(sp => !sp.exclude)
                .map(sp => ({
                  original_subpolicy_id: sp.id,
                  SubPolicyName: sp.title,
                  Description: sp.description,
                  Control: sp.control,
                  Identifier: sp.identifier,
                  PermanentTemporary: 'Permanent'
                }))
            }

            await axios.post(`${API_BASE_URL}/policies/${policy.id}/copy/`, policyData)
          }
          
          // Show success message
          alert(`Successfully copied ${policiesData.value.length} policy/policies to framework "${frameworks.value.find(f => f.id === selectedFramework.value)?.name || 'Unknown'}"`)
        } else {
          // Copy framework
          const apiData = {
            FrameworkName: frameworkData.value.title,
            FrameworkDescription: frameworkData.value.description,
            Category: frameworkData.value.category,
            EffectiveDate: frameworkData.value.effectiveDate,
            StartDate: frameworkData.value.startDate,
            EndDate: frameworkData.value.endDate,
            DocURL: frameworkData.value.docURL,
            Identifier: frameworkData.value.identifier,
            CreatedByUserId: policiesData.value[0].createdByName, // This now contains UserId
            Reviewer: policiesData.value[0].reviewer, // This now contains UserId
            policies: policiesData.value
              .filter(p => !p.exclude) // Filter out excluded policies
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
                DocURL: p.docURL,
                Identifier: p.identifier,
                CreatedByUserId: p.createdByName, // This now contains UserId
                Reviewer: p.reviewer, // This now contains UserId
                subpolicies: p.subPolicies
                  .filter(sp => !sp.exclude) // Filter out excluded subpolicies
                  .map(sp => ({
                    original_subpolicy_id: sp.id,
                    SubPolicyName: sp.title,
                    Description: sp.description,
                    Control: sp.control,
                    Identifier: sp.identifier,
                    Status: 'Under Review'
                  }))
              }))
          }

          const result = await axios.post(`${API_BASE_URL}/frameworks/${selectedFramework.value}/copy/`, apiData)
          alert(`Successfully created framework with ID: ${result.data.FrameworkId}`)
        }

        // Reset form after successful submission
        resetForm()
      } catch (err) {
        handleError(err)
      } finally {
        loading.value = false
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
        identifier: ''
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
      removePolicyFromCopy
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
@import './Tailoring.css';

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
</style> 