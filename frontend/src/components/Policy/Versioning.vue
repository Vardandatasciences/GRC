<template>
  <div class="versioning-container">
    <h2 class="page-title">Policy Versioning</h2>
    
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

    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>Loading...</p>
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
          <span v-if="showPolicyDropdown" class="tab-close" @click.stop="closeTab(idx)">×</span>
          <span v-if="idx !== 0 && !showPolicyDropdown" class="tab-close" @click.stop="closeTab(idx)">×</span>
        </div>
        <button v-if="!showPolicyDropdown" class="add-btn add-policy-btn" @click="addPolicy">+ Add Policy</button>
        <button v-if="showPolicyDropdown" class="add-btn add-policy-btn" @click="addPolicy">+ Add New Policy</button>
      </div>
      <div class="step-content">
        <!-- Framework Form -->
        <div v-if="stepIndex === 0">
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
            <div class="form-group">
              <label>Created By:</label>
              <select v-model="frameworkData.createdByName" required>
                <option value="" disabled>Select a user</option>
                <option v-for="user in users" :key="user.UserId" :value="user.UserName">
                  {{ user.UserName }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Reviewer:</label>
              <select v-model="frameworkData.reviewer" required>
                <option value="" disabled>Select a reviewer</option>
                <option v-for="user in users" :key="user.UserId" :value="user.UserId">
                  {{ user.UserName }}
                </option>
              </select>
            </div>
          </form>
        </div>
        <!-- Policy Form for Framework -->
        <div v-else>
          <form class="form-section policy-form" @submit.prevent="submitFrameworkForm">
            <div class="policy-header">
              <h3>Policy {{ stepIndex }}</h3>
              <div class="policy-actions">
                <button type="button" class="exclude-btn" @click="togglePolicyExclusion(stepIndex-1)">
                  {{ policiesData[stepIndex-1].exclude ? 'Excluded' : 'Exclude' }}
                </button>
              </div>
            </div>
            <div class="form-group" :class="{ 'excluded': policiesData[stepIndex-1].exclude }">
              <label>Policy Name:</label>
              <input type="text" v-model="policiesData[stepIndex-1].title" required />
            </div>
            <div class="form-group" :class="{ 'excluded': policiesData[stepIndex-1].exclude }">
              <label>Policy Description:</label>
              <textarea v-model="policiesData[stepIndex-1].description" required></textarea>
            </div>
            <div class="form-group" :class="{ 'excluded': policiesData[stepIndex-1].exclude }">
              <label>Objective:</label>
              <textarea v-model="policiesData[stepIndex-1].objective" required></textarea>
            </div>
            <div class="form-group" :class="{ 'excluded': policiesData[stepIndex-1].exclude }">
              <label>Scope:</label>
              <textarea v-model="policiesData[stepIndex-1].scope" required></textarea>
            </div>
            <div class="form-group" :class="{ 'excluded': policiesData[stepIndex-1].exclude }">
              <label>Department:</label>
              <input type="text" v-model="policiesData[stepIndex-1].department" required />
            </div>
            <div class="form-group" :class="{ 'excluded': policiesData[stepIndex-1].exclude }">
              <label>Applicability:</label>
              <input type="text" v-model="policiesData[stepIndex-1].applicability" required />
            </div>
            <div class="form-group" :class="{ 'excluded': policiesData[stepIndex-1].exclude }">
              <label>Start Date:</label>
              <input type="date" v-model="policiesData[stepIndex-1].startDate" required />
            </div>
            <div class="form-group" :class="{ 'excluded': policiesData[stepIndex-1].exclude }">
              <label>End Date:</label>
              <input type="date" v-model="policiesData[stepIndex-1].endDate" required />
            </div>
            <div class="form-group" :class="{ 'excluded': policiesData[stepIndex-1].exclude }">
              <label>Document URL:</label>
              <input type="url" v-model="policiesData[stepIndex-1].docURL" />
            </div>
            <div class="form-group" :class="{ 'excluded': policiesData[stepIndex-1].exclude }">
              <label>Identifier:</label>
              <input type="text" v-model="policiesData[stepIndex-1].identifier" required />
            </div>
            <div class="form-group" :class="{ 'excluded': policiesData[stepIndex-1].exclude }">
              <label>Created By:</label>
              <select v-model="policiesData[stepIndex-1].createdByName" required>
                <option value="" disabled>Select a user</option>
                <option v-for="user in users" :key="user.UserId" :value="user.UserName">
                  {{ user.UserName }}
                </option>
              </select>
            </div>
            <div class="form-group" :class="{ 'excluded': policiesData[stepIndex-1].exclude }">
              <label>Reviewer:</label>
              <select v-model="policiesData[stepIndex-1].reviewer" required>
                <option value="" disabled>Select a reviewer</option>
                <option v-for="user in users" :key="user.UserId" :value="user.UserId">
                  {{ user.UserName }}
                </option>
              </select>
            </div>
            <div class="subpolicies-section">
              <h4>Sub Policies</h4>
              <div class="subpolicies-row">
                <div v-for="(sub, subIdx) in policiesData[stepIndex-1].subPolicies" :key="subIdx" class="subpolicy-card">
                  <div class="subpolicy-header">
                    <span class="subpolicy-title">Sub Policy {{ subIdx + 1 }}</span>
                    <div class="subpolicy-actions">
                      <button type="button" class="exclude-btn" @click="toggleSubPolicyExclusion(stepIndex-1, subIdx)">
                        {{ sub.exclude ? 'Excluded' : 'Exclude' }}
                      </button>
                    </div>
                  </div>
                  <div class="form-group" :class="{ 'excluded': sub.exclude }">
                    <label>Title:</label>
                    <input type="text" v-model="sub.title" required />
                  </div>
                  <div class="form-group" :class="{ 'excluded': sub.exclude }">
                    <label>Description:</label>
                    <textarea v-model="sub.description" required></textarea>
                  </div>
                  <div class="form-group" :class="{ 'excluded': sub.exclude }">
                    <label>Control:</label>
                    <textarea v-model="sub.control" required></textarea>
                  </div>
                  <div class="form-group" :class="{ 'excluded': sub.exclude }">
                    <label>Identifier:</label>
                    <input type="text" v-model="sub.identifier" required />
                  </div>
                </div>
              </div>
              <button type="button" class="add-btn" @click="addSubPolicy(stepIndex-1)">+ Add Sub Policy</button>
            </div>
            <button class="create-btn" type="submit">Create New Version</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

export default {
  name: 'PolicyVersioning',
  setup() {
    const selectedFramework = ref('')
    const selectedPolicy = ref('')
    const showStepper = ref(false)
    const showPolicyDropdown = ref(false)
    const stepIndex = ref(0)
    const loading = ref(false)
    const error = ref(null)
    const users = ref([])

    const frameworks = ref([])
    const policyOptions = ref([])

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

    const policiesData = ref([])

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
          createdByName: response.data.CreatedByName || '',
          reviewer: response.data.Reviewer || ''
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
          exclude: false,
          subPolicies: p.subpolicies.map(sp => ({
            id: sp.SubPolicyId,
            title: sp.SubPolicyName,
            description: sp.Description,
            control: sp.Control,
            identifier: sp.Identifier,
            exclude: false
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
        // Filter for approved and active policies
        const policiesData = response.data.policies || response.data
        policyOptions.value = policiesData
          .filter(p => p.Status === 'Approved' && p.ActiveInactive === 'Active')
          .map(p => ({
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
            createdByName: p.CreatedByName,
            reviewer: p.Reviewer,
            subPolicies: (p.subpolicies || []).map(sp => ({
              id: sp.SubPolicyId,
              title: sp.SubPolicyName,
              description: sp.Description,
              control: sp.Control,
              identifier: sp.Identifier
            }))
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
        
        // Populate single policy data with all fields
        policiesData.value = [{
          id: response.data.PolicyId,
          title: response.data.PolicyName,
          description: response.data.PolicyDescription,
          objective: response.data.Objective,
          scope: response.data.Scope,
          department: response.data.Department,
          applicability: response.data.Applicability,
          startDate: response.data.StartDate,
          endDate: response.data.EndDate,
          docURL: response.data.DocURL,
          identifier: response.data.Identifier,
          createdByName: response.data.CreatedByName,
          reviewer: response.data.Reviewer,
          subPolicies: (response.data.subpolicies || []).map(sp => ({
            id: sp.SubPolicyId,
            title: sp.SubPolicyName,
            description: sp.Description,
            control: sp.Control,
            identifier: sp.Identifier
          }))
        }]

      showStepper.value = true
        stepIndex.value = 1 // Change to show policy details instead of framework
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
      fetchPolicies()
    }

    const switchToFramework = () => {
      showPolicyDropdown.value = false
      selectedPolicy.value = ''
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
      fetchFrameworks()
    }

    const addPolicy = () => {
      if (showPolicyDropdown.value) {
        // For policy versioning
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
          exclude: false,
          subPolicies: []
        })
      } else {
        // For framework versioning
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
          exclude: false,
          subPolicies: []
        })
      }
      stepIndex.value = policiesData.value.length // Go to new policy tab
    }

    const removePolicy = (idx) => {
      if (showPolicyDropdown.value) {
        // For policy versioning, clear all data
        policiesData.value = []
        showStepper.value = false
        selectedPolicy.value = ''
      } else {
        // For framework versioning
        if (policiesData.value[idx].id) {
          // If this is an existing policy, mark it for exclusion
          policiesData.value[idx].exclude = true
        } else {
          // If it's a new policy, remove it from the array
      policiesData.value.splice(idx, 1)
        }
      if (stepIndex.value > idx) stepIndex.value--
      if (stepIndex.value >= stepTabs.value.length) stepIndex.value = stepTabs.value.length - 1
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

    const togglePolicyExclusion = (idx) => {
      const policy = policiesData.value[idx]
      policy.exclude = !policy.exclude
      // When excluding a policy, also exclude all its subpolicies
      if (policy.exclude) {
        policy.subPolicies.forEach(sub => {
          sub.exclude = true
        })
      }
    }

    const toggleSubPolicyExclusion = (policyIdx, subIdx) => {
      const subPolicy = policiesData.value[policyIdx].subPolicies[subIdx]
      subPolicy.exclude = !subPolicy.exclude
    }

    const closeTab = (idx) => {
      if (idx === 0) return // Don't close framework tab
      
      // Mark the policy as excluded
      policiesData.value[idx - 1].exclude = true
      
      // Move to the previous tab
      if (stepIndex.value >= idx) {
        stepIndex.value = idx - 1
      }
      
      // Also exclude all subpolicies of the excluded policy
      if (policiesData.value[idx - 1].subPolicies) {
        policiesData.value[idx - 1].subPolicies.forEach(sub => {
          sub.exclude = true
        })
      }
    }

    // Submit form to create new version
    const submitFrameworkForm = async () => {
      try {
        loading.value = true
        error.value = null

        if (showPolicyDropdown.value) {
          // Create new policy version
          const policyData = {
            PolicyName: policiesData.value[0].title,
            PolicyDescription: policiesData.value[0].description,
            Objective: policiesData.value[0].objective,
            Scope: policiesData.value[0].scope,
            Department: policiesData.value[0].department,
            Applicability: policiesData.value[0].applicability,
            StartDate: policiesData.value[0].startDate,
            EndDate: policiesData.value[0].endDate,
            DocURL: policiesData.value[0].docURL,
            Identifier: policiesData.value[0].identifier,
            CreatedByName: policiesData.value[0].createdByName,
            Reviewer: policiesData.value[0].reviewer,
            subpolicies: policiesData.value[0].subPolicies.map(sp => ({
              original_subpolicy_id: parseInt(sp.id),
              SubPolicyName: sp.title,
              Description: sp.description,
              Control: sp.control,
              Identifier: sp.identifier
            }))
          }

          const result = await axios.post(
            `${API_BASE_URL}/policies/${policiesData.value[0].id}/create-version/`,
            policyData
          )

          alert(`Successfully created new policy version: ${result.data.PolicyName} (Version ${result.data.NewVersion})`)
        } else {
          // Create new framework version
          const frameworkPayload = {
            FrameworkName: frameworkData.value.title,
            FrameworkDescription: frameworkData.value.description,
            Category: frameworkData.value.category,
            EffectiveDate: frameworkData.value.effectiveDate,
            StartDate: frameworkData.value.startDate,
            EndDate: frameworkData.value.endDate,
            DocURL: frameworkData.value.docURL,
            Identifier: frameworkData.value.identifier,
            CreatedByName: frameworkData.value.createdByName,
            CreatedByDate: new Date().toISOString().split('T')[0],
            Reviewer: frameworkData.value.reviewer,
            policies: policiesData.value
              .filter(p => !p.exclude)
              .map(p => ({
                original_policy_id: parseInt(p.id),
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
                Reviewer: p.reviewer,
                subpolicies: p.subPolicies
                  .filter(sp => !sp.exclude)
                  .map(sp => ({
                    original_subpolicy_id: parseInt(sp.id),
                    SubPolicyName: sp.title,
                    Description: sp.description,
                    Control: sp.control,
                    Identifier: sp.identifier
                  }))
              }))
          }

          console.log('Sending framework version data:', frameworkPayload)

          const result = await axios.post(
            `${API_BASE_URL}/frameworks/${selectedFramework.value}/create-version/`,
            frameworkPayload
          )

          alert(`Successfully created new framework version: ${result.data.FrameworkName} (Version ${result.data.NewVersion})`)
        }

        // Reset form after successful submission
        showStepper.value = false
        selectedFramework.value = ''
        selectedPolicy.value = ''
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
      } catch (err) {
        console.error('Error creating new version:', err)
        const errorMessage = err.response?.data?.error || err.response?.data?.details?.error || 'Failed to create new version'
        error.value = errorMessage
        console.log('Full error details:', {
          error: err.response?.data,
          status: err.response?.status,
          headers: err.response?.headers
        })
      } finally {
        loading.value = false
      }
    }

    // Computed property for step tabs
    const stepTabs = computed(() => {
      if (showPolicyDropdown.value) {
        return policiesData.value.map((p, i) => ({ key: `newpolicy${i+1}`, label: `New Policy ${i+1}` }))
      }
      return [
        { key: 'framework', label: 'Framework' },
        ...policiesData.value.map((p, i) => ({ key: `policy${i+1}`, label: `Policy ${i+1}` }))
      ]
    })

    // Add fetchUsers function
    const fetchUsers = async () => {
      try {
        loading.value = true
        const response = await axios.get(`${API_BASE_URL}/users/`)
        users.value = response.data
      } catch (err) {
        console.error('Error fetching users:', err)
        error.value = 'Failed to fetch users'
      } finally {
        loading.value = false
      }
    }

    // Initialize data
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
      users,
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
      togglePolicyExclusion,
      toggleSubPolicyExclusion
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

/* Keep existing styles */
@import './Versioning.css';

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
  padding: 6px 12px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.exclude-btn.excluded {
  background-color: #ffebee;
  color: #d32f2f;
  border-color: #d32f2f;
}

.excluded {
  opacity: 0.6;
  background-color: #f5f5f5;
  pointer-events: none;
}

.remove-btn {
  padding: 6px 12px;
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #d32f2f;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background-color: #d32f2f;
  color: white;
}

.create-btn {
  margin-top: 24px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 117, 252, 0.2);
}

.create-btn:active {
  transform: translateY(0);
}

.create-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.subpolicy-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  background-color: white;
  transition: all 0.2s ease;
}

.subpolicy-card.excluded {
  opacity: 0.6;
  background-color: #f5f5f5;
}

.subpolicy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.subpolicy-title {
  font-weight: 600;
  color: #333;
}

.subpolicy-actions {
  display: flex;
  gap: 8px;
}

.tab-close {
  margin-left: 8px;
  cursor: pointer;
  font-size: 18px;
  font-weight: bold;
  color: #666;
  padding: 0 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.tab-close:hover {
  background-color: rgba(0, 0, 0, 0.1);
  color: #d32f2f;
}

/* Add to existing styles */
select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  font-size: 14px;
  margin-top: 4px;
}

select:focus {
  outline: none;
  border-color: #2575fc;
  box-shadow: 0 0 0 2px rgba(37, 117, 252, 0.1);
}

select:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #333;
}
</style> 