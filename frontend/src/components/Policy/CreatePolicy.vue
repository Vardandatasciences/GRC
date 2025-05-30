<template>
  <div class="create-policy-container">
    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>Loading...</p>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      {{ error }}
      <button class="close-btn" @click="error = null">✕</button>
    </div>

    <!-- Policy Form Section -->
    <div v-if="!showApprovalForm">
      <h2>Create New Policy</h2>
     
      <!-- Framework Selection - Show only when no framework is selected -->
      <div class="framework-policy-row" v-if="!selectedFramework || showFrameworkForm">
        <div class="framework-policy-selects">
          <div>
            <label>Framework</label>
            <select v-model="selectedFramework" style="font-size: 0.9rem" :disabled="loading">
              <option value="">Select</option>
              <option value="create">+ Create New Framework</option>
              <option v-for="f in frameworks" :key="f.id" :value="f.id">{{ f.name }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Framework Creation Form -->
      <div v-if="showFrameworkForm" class="framework-form-container">
        <div class="framework-form">
          <div class="form-row">
            <div class="form-group policy-name">
              <label>Framework Name</label>
              <div class="input-with-icon">
                <i class="fas fa-file-alt"></i>
                <input
                  type="text"
                  placeholder="Enter Framework name"
                  v-model="newFramework.FrameworkName"
                  style="text-align: left !important;"
                />
              </div>
            </div>
            <div class="form-group created-by">
              <label>Created By</label>
              <div class="input-with-icon">
                <i class="fas fa-user"></i>
                <select v-model="newFramework.CreatedByName">
                  <option value="">Select Creator</option>
                  <option v-for="user in users" :key="user.UserId" :value="user.UserName">
                    {{ user.UserName }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <div class="form-row single-column">
            <div class="form-group description">
              <label>Description</label>
              <div class="input-with-icon">
                <i class="fas fa-align-left"></i>
                <textarea
                  placeholder="Enter framework description"
                  v-model="newFramework.FrameworkDescription"
                  rows="3"
                ></textarea>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group version">
              <label>Identifier</label>
              <div class="input-with-icon">
                <i class="fas fa-code-branch"></i>
                <input
                  type="text"
                  placeholder="Enter Identifier"
                  v-model="newFramework.Version"
                />
              </div>
            </div>
            <div class="form-group category">
              <label>Category</label>
              <div class="input-with-icon">
                <i class="fas fa-tag"></i>
                <input
                  type="text"
                  placeholder="Enter category"
                  v-model="newFramework.Category"
                />
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group date">
              <label>Effective Date</label>
              <div class="input-with-icon">
                <i class="fas fa-calendar"></i>
                <input
                  type="date"
                  v-model="newFramework.EffectiveDate"
                />
              </div>
            </div>
            <div class="form-group date">
              <label>Effective Start Date</label>
              <div class="input-with-icon">
                <i class="fas fa-calendar"></i>
                <input
                  type="date"
                  v-model="newFramework.StartDate"
                />
              </div>
            </div>
            <div class="form-group date">
              <label>Effective End Date</label>
              <div class="input-with-icon">
                <i class="fas fa-calendar"></i>
                <input
                  type="date"
                  v-model="newFramework.EndDate"
                />
              </div>
            </div>
            <div class="form-group upload">
              <label>Upload Document</label>
              <div class="input-with-icon">
                <i class="fas fa-file-upload"></i>
                <span>Choose File</span>
                <button class="browse-btn">Browse</button>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group reviewer">
              <label>Reviewer</label>
              <div class="input-with-icon">
                <i class="fas fa-user-check"></i>
                <select v-model="newFramework.Reviewer">
                  <option value="">Select Reviewer</option>
                  <option v-for="user in users" :key="user.UserId" :value="user.UserId">
                    {{ user.UserName }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button class="submit-btn" @click="handleCreateFramework">Submit</button>
            <button class="cancel-btn" @click="showFrameworkForm = false">Cancel</button>
          </div>
        </div>
      </div>

      <!-- Policy Actions - Show when framework is selected -->
      <div v-if="selectedFramework && !showFrameworkForm" class="policy-actions-container">
        <div class="selected-framework-info">
          <span>Selected Framework: {{ getSelectedFrameworkName() }}</span>
          <button class="change-framework-btn" @click="handleChangeFramework">
            <i class="fas fa-exchange-alt"></i> Change Framework
          </button>
        </div>
        <button
          class="add-policy-btn"
          @click="handleAddPolicy"
          :disabled="loading"
          style="font-size: 0.9rem"
        >
          <i class="fas fa-plus"></i> Add Policy
        </button>
      </div>

      <!-- Policies and Subpolicies Grid -->
      <div class="policy-rows">
        <div v-for="(policy, idx) in policiesForm" :key="idx" class="policy-row">
          <!-- Policy Card -->
          <div class="policy-card">
            <div class="policy-card-header">
              <b style="font-size: 0.95rem">{{ policy.PolicyName || `Policy ${idx + 1}` }}</b>
              <button class="remove-btn" @click="handleRemovePolicy(idx)" title="Remove Policy">✕</button>
            </div>
           
            <!-- Policy Card Fields -->
            <div class="policy-form-row">
              <div class="form-group">
                <label>Policy Name</label>
                <div class="input-with-icon">
                  <i class="fas fa-file-alt"></i>
                  <input
                    type="text"
                    placeholder="Enter policy name"
                    v-model="policy.PolicyName"
                    @input="handlePolicyChange(idx, 'PolicyName', $event.target.value)"
                  />
                </div>
              </div>
              <div class="form-group">
                <label>Policy Identifier</label>
                <div class="input-with-icon">
                  <i class="fas fa-fingerprint"></i>
                  <input
                    type="text"
                    placeholder="Enter policy identifier"
                    v-model="policy.Identifier"
                    @input="handlePolicyChange(idx, 'Identifier', $event.target.value)"
                  />
                </div>
              </div>
            </div>

            <!-- Description -->
            <div class="form-group description">
              <label>Description</label>
              <div class="input-with-icon">
                <i class="fas fa-align-left"></i>
                <textarea
                  placeholder="Enter policy description"
                  v-model="policy.PolicyDescription"
                  @input="handlePolicyChange(idx, 'PolicyDescription', $event.target.value)"
                  rows="3"
                ></textarea>
              </div>
            </div>

            <!-- Scope and Department -->
            <div class="policy-form-row">
              <div class="form-group">
                <label>Scope</label>
                <div class="input-with-icon">
                  <i class="fas fa-bullseye"></i>
                  <input
                    type="text"
                    placeholder="Enter policy scope"
                    v-model="policy.Scope"
                    @input="handlePolicyChange(idx, 'Scope', $event.target.value)"
                  />
                </div>
              </div>
              <div class="form-group">
                <label>Department</label>
                <div class="input-with-icon">
                  <i class="fas fa-building"></i>
                  <input
                    type="text"
                    placeholder="Enter department"
                    v-model="policy.Department"
                    @input="handlePolicyChange(idx, 'Department', $event.target.value)"
                  />
                </div>
              </div>
            </div>

            <!-- Objective and Applicability -->
            <div class="policy-form-row objective-applicability-row">
              <div class="form-group">
                <label>Objective</label>
                <div class="input-with-icon">
                  <i class="fas fa-bullseye"></i>
                  <textarea
                    placeholder="Enter policy objective"
                    v-model="policy.Objective"
                    @input="handlePolicyChange(idx, 'Objective', $event.target.value)"
                    rows="3"
                  ></textarea>
                </div>
              </div>
              <div class="form-group">
                <label>Applicability</label>
                <div class="input-with-icon">
                  <i class="fas fa-users"></i>
                  <input
                    type="text"
                    placeholder="Enter applicability"
                    v-model="policy.Applicability"
                    @input="handlePolicyChange(idx, 'Applicability', $event.target.value)"
                  />
                </div>
              </div>
            </div>

            <!-- Coverage Rate -->
            <div class="policy-form-row">
              <div class="form-group">
                <label>Coverage Rate (%)</label>
                <div class="input-with-icon">
                  <i class="fas fa-percentage"></i>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.01"
                    placeholder="Enter coverage rate"
                    v-model="policy.CoverageRate"
                    @input="handlePolicyChange(idx, 'CoverageRate', $event.target.value)"
                  />
                </div>
              </div>
            </div>

            <!-- Start and End Date -->
            <div class="policy-form-row date-row">
              <div class="form-group">
                <label>Start Date</label>
                <div class="input-with-icon">
                  <i class="fas fa-calendar-alt"></i>
                  <input
                    type="date"
                    v-model="policy.StartDate"
                    @input="handlePolicyChange(idx, 'StartDate', $event.target.value)"
                  />
                </div>
              </div>
              <div class="form-group">
                <label>End Date</label>
                <div class="input-with-icon">
                  <i class="fas fa-calendar-alt"></i>
                  <input
                    type="date"
                    v-model="policy.EndDate"
                    @input="handlePolicyChange(idx, 'EndDate', $event.target.value)"
                  />
                </div>
              </div>
            </div>

            <button class="upload-btn"><i class="fas fa-plus"></i> Upload Document</button>
            <button class="add-sub-policy-btn" @click="handleAddSubPolicy(idx)">
              <i class="fas fa-plus"></i> Add Sub Policy
            </button>
          </div>
 
          <!-- Subpolicies Cards -->
          <div class="subpolicies-row">
            <div v-for="(sub, subIdx) in policy.subpolicies" :key="subIdx" class="subpolicy-card">
              <div class="policy-card-header">
                <b style="font-size: 0.9rem">{{ sub.SubPolicyName || `Sub Policy ${subIdx + 1}` }}</b>
                <button class="remove-btn" @click="handleRemoveSubPolicy(idx, subIdx)" title="Remove Sub Policy">✕</button>
              </div>
 
              <!-- Sub Policy Card Fields -->
              <div class="form-group">
                <label>Sub Policy Name</label>
                <div class="input-with-icon">
                  <i class="fas fa-file-alt"></i>
                  <input
                    type="text"
                    placeholder="Enter sub policy name"
                    v-model="sub.SubPolicyName"
                    @input="handleSubPolicyChange(idx, subIdx, 'SubPolicyName', $event.target.value)"
                  />
                </div>
              </div>
 
              <div class="form-group">
                <label>Identifier</label>
                <div class="input-with-icon">
                  <i class="fas fa-fingerprint"></i>
                  <input
                    type="text"
                    placeholder="Enter identifier"
                    v-model="sub.Identifier"
                    @input="handleSubPolicyChange(idx, subIdx, 'Identifier', $event.target.value)"
                  />
                </div>
              </div>
 
              <div class="form-group">
                <label>Control</label>
                <div class="input-with-icon">
                  <i class="fas fa-shield-alt"></i>
                  <input
                    type="text"
                    placeholder="Enter control"
                    v-model="sub.Control"
                    @input="handleSubPolicyChange(idx, subIdx, 'Control', $event.target.value)"
                  />
                </div>
              </div>
 
              <div class="form-group">
                <label>Description</label>
                <div class="input-with-icon">
                  <i class="fas fa-align-left"></i>
                  <textarea
                    placeholder="Enter description"
                    v-model="sub.Description"
                    @input="handleSubPolicyChange(idx, subIdx, 'Description', $event.target.value)"
                    rows="3"
                  ></textarea>
                </div>
              </div>
 
              <button class="upload-btn"><i class="fas fa-plus"></i> Upload Document</button>
            </div>
          </div>
        </div>
      </div>
      <div class="form-actions" v-if="policiesForm.length > 0">
        <button 
          class="create-btn" 
          @click="handleSubmitPolicy" 
          :disabled="loading"
          style="font-size: 1rem; margin-top: 24px"
        >
          {{ loading ? 'Submitting...' : 'Submit' }}
        </button>
      </div>
    </div>
 
    <!-- Approval Form Section -->
    <div v-else class="approval-section">
      <div class="approval-header">
        <h2>Request Approvals</h2>
        <button class="back-btn" @click="showApprovalForm = false">
          <i class="fas fa-arrow-left"></i> Back to Policy Form
        </button>
      </div>
     
      <div class="approval-form-container">
        <div class="approval-form">
          <div class="form-group">
            <label>Created By</label>
            <select
              v-model="approvalForm.createdBy"
              :disabled="loading"
            >
              <option value="">Select Creator</option>
              <option v-for="user in users" :key="user.UserId" :value="user.UserId">
                {{ user.UserName }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Reviewer</label>
            <select
              v-model="approvalForm.reviewer"
              :disabled="loading"
            >
              <option value="">Select Reviewer</option>
              <option v-for="user in users" :key="user.UserId" :value="user.UserId">
                {{ user.UserName }}
              </option>
            </select>
          </div>
          <button 
            class="create-btn" 
            @click="handleFinalSubmit"
            :disabled="loading || !approvalForm.createdBy || !approvalForm.reviewer"
          >
            {{ loading ? 'Submitting...' : 'Submit' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
 
<script>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'
 
export default {
  name: 'CreatePolicy',
  setup() {
    const selectedFramework = ref('')
    const policiesForm = ref([])
    const selectedPolicyIdx = ref(null)
    const showApprovalForm = ref(false)
    const showFrameworkForm = ref(false)
    const approvalForm = ref({
      createdBy: '',
      reviewer: ''
    })
    const frameworks = ref([])
    const loading = ref(false)
    const error = ref(null)
    const users = ref([])
    const frameworkFormData = ref(null)
 
    const newFramework = ref({
      FrameworkName: '',
      Identifier: '',
      FrameworkDescription: '',
      Category: '',
      EffectiveDate: '',
      StartDate: '',
      EndDate: '',
      CreatedByName: '',
      DocURL: '',
      Reviewer: ''
    })
 
    // Fetch all frameworks on component mount
    async function fetchFrameworks() {
      try {
        loading.value = true
        const response = await axios.get(`${API_BASE_URL}/frameworks/`)
        frameworks.value = response.data.map(fw => ({
          id: fw.FrameworkId,
          name: fw.FrameworkName
        }))
      } catch (err) {
        console.error('Error fetching frameworks:', err)
        error.value = 'Failed to fetch frameworks'
      } finally {
        loading.value = false
      }
    }
 
    // Watch for framework selection changes
    watch(selectedFramework, (newValue) => {
      if (newValue === 'create') {
        showFrameworkForm.value = true
        selectedFramework.value = ''
      }
    })
 
    const handleCreateFramework = async () => {
      // Only store framework details in memory and move to add policy
      error.value = null
      frameworkFormData.value = { ...newFramework.value }
      showFrameworkForm.value = false
      // Add an initial empty policy
      handleAddPolicy()
      // Set selectedFramework to a dummy value to show the policy form
      selectedFramework.value = '__new__'
      // Reset the framework form
      newFramework.value = {
        FrameworkName: '',
        Identifier: '',
        FrameworkDescription: '',
        Category: '',
        EffectiveDate: '',
        StartDate: '',
        EndDate: '',
        CreatedByName: '',
        DocURL: '',
        Reviewer: ''
      }
    }
 
    // Policy form handlers
    const handleAddPolicy = () => {
      policiesForm.value.push({
        PolicyName: '',
        Identifier: '',
        PolicyDescription: '',
        Scope: '',
        Objective: '',
        Department: '',
        Applicability: '',
        StartDate: '',
        EndDate: '',
        CreatedByName: '',
        DocURL: '',
        subpolicies: []
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
 
    const handleAddSubPolicy = (policyIdx) => {
      policiesForm.value[policyIdx].subpolicies.push({
        SubPolicyName: '',
        Identifier: '',
        Control: '',
        Description: '',
        CreatedByName: '',
        PermanentTemporary: 'Permanent'
      })
    }
 
    const handleRemoveSubPolicy = (policyIdx, subIdx) => {
      policiesForm.value[policyIdx].subpolicies =
        policiesForm.value[policyIdx].subpolicies.filter((_, j) => j !== subIdx)
    }
 
    const handleSubPolicyChange = (policyIdx, subIdx, field, value) => {
      policiesForm.value[policyIdx].subpolicies[subIdx][field] = value
    }
 
    const handleSubmitPolicy = () => {
      showApprovalForm.value = true
    }
 
    // Add this function to fetch users
    async function fetchUsers() {
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

    const handleFinalSubmit = async () => {
      try {
        loading.value = true
        error.value = null

        // Only check framework fields if creating a new framework
        const isCreatingNewFramework = selectedFramework.value === '__new__';
        if (isCreatingNewFramework) {
          if (!frameworkFormData.value || !frameworkFormData.value.FrameworkName) {
            error.value = 'Please fill in all required framework fields.'
            loading.value = false
            return
          }
        }

        // Find the selected creator and reviewer users
        const creatorUser = users.value.find(u => u.UserId === approvalForm.value.createdBy)
        const reviewerUser = users.value.find(u => u.UserId === approvalForm.value.reviewer)

        if (!creatorUser) {
          error.value = 'Please select a creator'
          loading.value = false
          return
        }

        // Validate required fields for each policy
        for (const policy of policiesForm.value) {
          if (!policy.PolicyName || !policy.Identifier || !policy.StartDate) {
            error.value = 'Please fill in all required fields (Policy Name, Identifier, and Start Date) for all policies'
            loading.value = false
            return
          }

          // Set default values for optional fields
          policy.Status = policy.Status || 'Under Review'
          policy.ActiveInactive = policy.ActiveInactive || 'Inactive'
          policy.CreatedByName = creatorUser.UserName
          policy.Reviewer = reviewerUser ? reviewerUser.UserId : null

          // Validate subpolicies
          for (const sub of policy.subpolicies) {
            if (!sub.SubPolicyName || !sub.Identifier) {
              error.value = 'Please fill in all required fields (Name and Identifier) for all subpolicies'
              loading.value = false
              return
            }
            // Set default values for subpolicies
            sub.Status = sub.Status || 'Under Review'
            sub.PermanentTemporary = sub.PermanentTemporary || 'Permanent'
            sub.CreatedByName = creatorUser.UserName
          }
        }

        if (isCreatingNewFramework) {
          // Prepare the full payload for new framework
          const payload = {
            ...frameworkFormData.value,
            CreatedByName: creatorUser.UserName,
            Reviewer: reviewerUser ? reviewerUser.UserId : null,
            policies: policiesForm.value.map(policy => ({
              ...policy,
              CoverageRate: policy.CoverageRate !== '' && policy.CoverageRate !== null && policy.CoverageRate !== undefined ? Number(policy.CoverageRate) : null,
              CreatedByName: creatorUser.UserName,
              Reviewer: reviewerUser ? reviewerUser.UserId : null,
              subpolicies: policy.subpolicies.map(sub => ({
                ...sub,
                CreatedByName: creatorUser.UserName,
                CreatedByDate: new Date().toISOString().split('T')[0],
                Status: 'Under Review',
                PermanentTemporary: 'Permanent'
              }))
            }))
          }

          // Send a single API call to create the framework with policies and subpolicies
          const response = await axios.post(`${API_BASE_URL}/frameworks/`, payload)
          if (response.data.error) {
            throw new Error(response.data.error)
          }
        } else {
          // Add policies to existing framework
          const frameworkId = selectedFramework.value;
          for (const policy of policiesForm.value) {
            const policyPayload = {
              ...policy,
              CoverageRate: policy.CoverageRate !== '' && policy.CoverageRate !== null && policy.CoverageRate !== undefined ? Number(policy.CoverageRate) : null,
              CreatedByName: creatorUser.UserName,
              Reviewer: reviewerUser ? reviewerUser.UserId : null,
              subpolicies: policy.subpolicies.map(sub => ({
                ...sub,
                CreatedByName: creatorUser.UserName,
                CreatedByDate: new Date().toISOString().split('T')[0],
                Status: 'Under Review',
                PermanentTemporary: 'Permanent'
              }))
            };
            try {
              const response = await axios.post(`${API_BASE_URL}/frameworks/${frameworkId}/policies/`, policyPayload);
              if (response.data.error) {
                throw new Error(response.data.error)
              }
            } catch (err) {
              console.error('Error submitting policy:', err);
              const errorMessage = err.response?.data?.details || err.response?.data?.error || 'Failed to submit policy';
              error.value = typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage;
              loading.value = false;
              return;
            }
          }
        }

        // Reset forms
        policiesForm.value = []
        approvalForm.value = {
          createdBy: '',
          reviewer: ''
        }
        selectedFramework.value = ''
        showApprovalForm.value = false
        frameworkFormData.value = null

      } catch (err) {
        console.error('Error submitting policies:', err)
        const errorMessage = err.response?.data?.details || err.response?.data?.error || 'Failed to submit policies';
        error.value = typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage;
      } finally {
        loading.value = false
      }
    }

    const getSelectedFrameworkName = () => {
      const framework = frameworks.value.find(f => f.id === selectedFramework.value)
      return framework ? framework.name : ''
    }

    const handleChangeFramework = () => {
      selectedFramework.value = ''
      policiesForm.value = []
    }

    // Fetch frameworks and users on mount
    onMounted(() => {
      fetchFrameworks()
      fetchUsers()
    })
 
    return {
      selectedFramework,
      policiesForm,
      selectedPolicyIdx,
      frameworks,
      showApprovalForm,
      showFrameworkForm,
      approvalForm,
      newFramework,
      loading,
      error,
      users,
      handleAddPolicy,
      handleRemovePolicy,
      handlePolicyChange,
      handleAddSubPolicy,
      handleRemoveSubPolicy,
      handleSubPolicyChange,
      handleSubmitPolicy,
      handleFinalSubmit,
      handleCreateFramework,
      getSelectedFrameworkName,
      handleChangeFramework,
      frameworkFormData,
    }
  }
}
</script>
 
<style scoped>
/* Import the existing CSS file */
@import './CreatePolicy.css';

/* Enhanced Loading and Error States */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-overlay p {
  margin-top: 16px;
  color: #4a5568;
  font-size: 1rem;
  font-weight: 500;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  position: fixed;
  top: 20px;
  right: 20px;
  background: linear-gradient(135deg, #fc8181, #f56565);
  color: white;
  padding: 16px 24px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
  box-shadow: 0 6px 16px rgba(245, 101, 101, 0.2);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.close-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 4px;
  opacity: 0.8;
  transition: all 0.2s ease;
}

.close-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}

/* Form Animations */
.policy-card, .subpolicy-card {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Enhanced Button States */
button {
  position: relative;
  overflow: hidden;
}

button::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5px;
  height: 5px;
  background: rgba(255, 255, 255, 0.5);
  opacity: 0;
  border-radius: 100%;
  transform: scale(1, 1) translate(-50%);
  transform-origin: 50% 50%;
}

button:focus:not(:active)::after {
  animation: ripple 1s ease-out;
}

@keyframes ripple {
  0% {
    transform: scale(0, 0);
    opacity: 0.5;
  }
  100% {
    transform: scale(100, 100);
    opacity: 0;
  }
}

/* Enhanced Form Field Focus States */
input:focus, select:focus, textarea:focus {
  transform: translateY(-1px);
}

/* Card Hover Effects */
.policy-card:hover, .subpolicy-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

/* Framework Form Field Styling */
.framework-form-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-top: 20px;
}

.framework-form {
  max-width: 100%;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.form-group {
  position: relative;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 8px;
}

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-with-icon i {
  position: absolute;
  left: 16px;
  color: #718096;
  font-size: 16px;
}

.form-group input,
.form-group select {
  width: 100%;
  height: 45px;
  padding: 8px 16px 8px 45px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #2d3748;
  background: white;
}

/* Colored borders */
.blue-border .input-with-icon input,
.blue-border .input-with-icon select {
  border-left: 3px solid #4299e1;
}

.green-border .input-with-icon input,
.green-border .input-with-icon select {
  border-left: 3px solid #48bb78;
}

.orange-border .input-with-icon input,
.orange-border .input-with-icon select {
  border-left: 3px solid #ed8936;
}

.red-border .input-with-icon input,
.red-border .input-with-icon select {
  border-left: 3px solid #f56565;
}

/* Upload field styling */
.upload-field {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  height: 45px;
}

.upload-field span {
  margin-left: 30px;
  color: #718096;
  font-size: 14px;
}

.browse-btn {
  margin-left: auto;
  padding: 4px 12px;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

/* Date input styling */
input[type="date"] {
  padding-right: 16px;
}

input[type="date"]::-webkit-calendar-picker-indicator {
  position: absolute;
  right: 8px;
  cursor: pointer;
}

/* Select styling */
select {
  appearance: none;
  padding-right: 30px;
  background-image: url("data:image/svg+xml,...");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;
  cursor: pointer;
}

/* Framework selection styling */
.framework-policy-row {
  margin-bottom: 24px;
}

.framework-policy-selects {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 24px;
}

.framework-policy-selects > div {
  flex: 0 0 300px; /* Fixed width for the select container */
}

.framework-policy-selects label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 8px;
}

.framework-policy-selects select {
  width: 100%;
  height: 40px;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  color: #2d3748;
  background: white;
  cursor: pointer;
  outline: none;
  transition: all 0.2s ease;
}

.framework-policy-selects select:focus {
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.framework-policy-selects select:hover {
  border-color: #cbd5e0;
}

/* Approval Form Transitions */
.approval-section {
  animation: fadeScale 0.4s ease-out;
}

@keyframes fadeScale {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Enhanced Scrollbar Styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* Policy Actions Container */
.policy-actions-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 16px 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.selected-framework-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.selected-framework-info span {
  font-size: 0.95rem;
  color: #2d3748;
  font-weight: 500;
}

.change-framework-btn {
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 8px 16px;
  color: #4a5568;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.change-framework-btn:hover {
  background: #f7fafc;
  border-color: #cbd5e0;
  color: #2d3748;
}

/* Update these specific styles */

.policy-card {
  width: 320px;
  padding: 16px; /* Reduced padding */
  box-sizing: border-box; /* Important: include padding in width calculation */
}

/* Base styles for all inputs in policy card */
.policy-card input,
.policy-card textarea {
  width: 100%;
  max-width: 100%; /* Changed from fixed width to 100% */
  padding: 6px 8px;
  height: 32px;
  font-size: 12px;
  box-sizing: border-box; /* Important: include padding in width calculation */
}

/* Form row styling */
.policy-form-row {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  width: 100%; /* Ensure row takes full width */
}

/* Description field specific styling */
.policy-card .form-group.description {
  width: 70%; /* Decreased from 80% to 70% */
  margin: 0 auto;
  max-width: 280px; /* Add max-width to prevent overflow */
}

.policy-card .form-group.description textarea {
  width: 100%;
  min-height: 80px;
  max-width: 100%; /* Ensure textarea doesn't overflow its container */
  box-sizing: border-box;
  overflow-x: hidden; /* Prevent horizontal scrolling */
}

/* Date fields row styling */
.policy-card .date-row {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  width: 100%;
}

.policy-card .date-row .form-group {
  flex: 1;
  min-width: 0;
}

.policy-card .date-row input {
  width: 100%;
}

/* Objective and Applicability row */
.policy-card .objective-applicability-row {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  width: 100%;
}

.policy-card .objective-applicability-row .form-group {
  flex: 1;
  min-width: 0;
}

.policy-card .objective-applicability-row textarea,
.policy-card .objective-applicability-row input {
  width: 100%;
  height: 32px;
}

/* Form groups in a row */
.policy-form-row .form-group {
  flex: 1; /* Changed to flex: 1 to ensure equal width */
  min-width: 0; /* Prevent flex items from overflowing */
  width: calc(50% - 4px); /* Ensure exact half width minus gap */
}

/* Date input specific styling */
.policy-form-row input[type="date"] {
  width: 100%; /* Changed from fixed width to 100% */
  min-width: 0; /* Allow shrinking */
  padding-right: 20px; /* Space for calendar icon */
}

/* Single form groups (not in a row) */
.policy-card .form-group:not(.policy-form-row .form-group) {
  width: 100%;
}

/* Textarea specific styling */
.policy-card textarea {
  height: auto;
  min-height: 50px;
  width: 100%;
  resize: vertical;
}

/* Remove any fixed max-width constraints */
.policy-form-row input,
.policy-form-row .form-group input {
  max-width: none;
}

/* Add these new styles for subpolicy card */
.subpolicy-card {
  width: 300px; /* Smaller than policy card */
  padding: 16px;
  box-sizing: border-box;
}

.subpolicy-card .form-group {
  margin-bottom: 10px;
}

.subpolicy-card input,
.subpolicy-card textarea {
  width: 100%;
  max-width: 100%;
  padding: 6px 8px;
  height: 32px;
  font-size: 12px;
  box-sizing: border-box;
}

.subpolicy-card textarea {
  height: auto;
  min-height: 50px;
  resize: vertical;
}

.subpolicy-card label {
  font-size: 13px;
  margin-bottom: 4px;
}

/* Form row styling for subpolicy */
.subpolicy-card .policy-form-row {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  width: 100%;
}

.subpolicy-card .policy-form-row .form-group {
  flex: 1;
  min-width: 0;
  width: calc(50% - 4px);
}

/* Ensure all inputs stay within boundaries */
.subpolicy-card .form-group input,
.subpolicy-card .form-group textarea {
  width: 100%;
  max-width: none;
}

/* Adjust the subpolicies row spacing */
.subpolicies-row {
  margin-top: 16px;
  gap: 16px;
}
</style>