<template>
  <div class="create-compliance-container">
    <!-- Header section -->
    <div class="compliance-header">
      <h2>Create Compliance Record</h2>
      <p>Add new compliance items to track in your GRC system</p>
    </div>

    <!-- Message display -->
    <div v-if="error" class="message error-message">
      {{ error }}
    </div>
    <div v-if="successMessage" class="message success-message">
      {{ successMessage }}
    </div>

    <!-- Selection controls -->
    <div class="compliance-form-row">
      <div class="select-wrapper">
        <label for="framework">Framework</label>
        <select id="framework" v-model="selectedFramework" class="compliance-select" required>
          <option value="" disabled>Select Framework</option>
          <option v-for="fw in frameworks" :key="fw.id" :value="fw">{{ fw.name }}</option>
        </select>
      </div>
      
      <div class="select-wrapper">
        <label for="policy">Policy</label>
        <select id="policy" v-model="selectedPolicy" class="compliance-select" required>
          <option value="" disabled>Select Policy</option>
          <option v-for="p in policies" :key="p.id" :value="p">{{ p.name }}</option>
        </select>
      </div>
      
      <div class="select-wrapper">
        <label for="subpolicy">Sub Policy</label>
        <select id="subpolicy" v-model="selectedSubPolicy" class="compliance-select" required>
          <option value="" disabled>Select Sub Policy</option>
          <option v-for="sp in subPolicies" :key="sp.id" :value="sp">{{ sp.name }}</option>
        </select>
      </div>
    </div>

    <!-- Compliance items list -->
    <div class="compliance-list">
      <div v-for="(compliance, idx) in complianceList" :key="idx" class="compliance-item-form">
        <!-- Header for each compliance item -->
        <div class="item-header">
          <span class="item-number">Compliance {{ idx + 1 }}</span>
          <div class="compliance-actions">
            <button 
              class="compliance-remove-btn" 
              @click="removeCompliance(idx)"
              :disabled="loading"
              title="Remove this item"
            >
              -
            </button>
            <button 
              v-if="idx === complianceList.length - 1" 
              class="compliance-add-btn" 
              @click="addCompliance"
              :disabled="loading"
              title="Add another item"
            >
              +
            </button>
          </div>
        </div>

        <!-- Compliance Description and Identifier/IsRisk in the same row -->
        <div class="compliance-field">
          <label>Compliance Description</label>
          <input 
            v-model="compliance.ComplianceItemDescription" 
            class="compliance-input" 
            :placeholder="`Compliance Description ${idx+1}`"
            required 
          />
        </div>
        <div class="compliance-field" style="display: flex; align-items: end; gap: 20px;">
          <div style="flex: 1;">
            <label>Identifier</label>
            <input 
              v-model="compliance.Identifier" 
              class="compliance-input" 
              placeholder="Auto-generated if left empty"
            />
            <small>Leave empty for auto-generated identifier</small>
          </div>
          <div style="flex: 1; display: flex; align-items: center; height: 100%; margin-left: 12px;">
            <label style="margin-bottom: 0; font-weight: 500; font-size: 1rem; display: flex; align-items: center; gap: 8px;">
              <input type="checkbox" v-model="compliance.IsRisk" style="margin-right: 8px;" />
              Is Risk
            </label>
          </div>
        </div>

        <!-- Possible Damage -->
        <div class="compliance-field">
          <label>Possible Damage</label>
          <input 
            v-model="compliance.PossibleDamage" 
            class="compliance-input" 
            placeholder="Possible Damage"
            :required="compliance.IsRisk" 
          />
        </div>
        <!-- Mitigation -->
        <div class="compliance-field">
          <label>Mitigation</label>
          <input 
            v-model="compliance.mitigation" 
            class="compliance-input" 
            placeholder="Mitigation" 
          />
        </div>
        <!-- Criticality -->
        <div class="compliance-field">
          <label>Criticality</label>
          <select v-model="compliance.Criticality" class="compliance-select" required>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
        <!-- Permanent/Temporary -->
        <div class="compliance-field">
          <label>Permanent/Temporary</label>
          <select v-model="compliance.PermanentTemporary" class="compliance-select" required>
            <option value="Permanent">Permanent</option>
            <option value="Temporary">Temporary</option>
          </select>
        </div>
        <!-- Mandatory/Optional -->
        <div class="compliance-field">
          <label>Mandatory/Optional</label>
          <select v-model="compliance.MandatoryOptional" class="compliance-select" required>
            <option value="Mandatory">Mandatory</option>
            <option value="Optional">Optional</option>
          </select>
        </div>
        <!-- Manual/Automatic -->
        <div class="compliance-field">
          <label>Manual/Automatic</label>
          <select v-model="compliance.ManualAutomatic" class="compliance-select" required>
            <option value="Manual">Manual</option>
            <option value="Automatic">Automatic</option>
          </select>
        </div>
        <!-- Impact (1-10) -->
        <div class="compliance-field">
          <label>Impact (1-10)</label>
          <input 
            type="number" 
            v-model.number="compliance.Impact" 
            @input="validateImpact($event, idx)"
            class="compliance-input" 
            step="0.1" 
            min="1" 
            max="10"
          />
          <span v-if="compliance.impactError" class="validation-error">
            Impact must be between 1 and 10
          </span>
        </div>
        <!-- Probability (1-10) -->
        <div class="compliance-field">
          <label>Probability (1-10)</label>
          <input 
            type="number" 
            v-model.number="compliance.Probability" 
            @input="validateProbability($event, idx)"
            class="compliance-input" 
            step="0.1" 
            min="1" 
            max="10"
          />
          <span v-if="compliance.probabilityError" class="validation-error">
            Probability must be between 1 and 10
          </span>
        </div>
        <!-- Assign Reviewer (now in same row as Probability) -->
        <div class="compliance-field">
          <label>Assign Reviewer</label>
          <select v-model="compliance.reviewer" class="compliance-select" required>
            <option v-for="user in users" :key="user.UserId" :value="user.UserId">
              {{ user.UserName }}
            </option>
          </select>
        </div>
      </div>
    </div>
    
    <button 
      class="compliance-submit-btn" 
      @click="submitCompliance"
      :disabled="loading"
    >
      <span v-if="loading">Saving...</span>
      <span v-else>Submit Compliance</span>
    </button>
  </div>
</template>

<script>
import { complianceService } from '@/data/api';

export default {
  name: 'CreateCompliance',
  data() {
    return {
      selectedFramework: '',
      selectedPolicy: '',
      selectedSubPolicy: '',
      frameworks: [],
      policies: [],
      subPolicies: [],
      users: [],
      complianceList: [
        {
          ComplianceItemDescription: '',
          Identifier: '',
          IsRisk: false,
          PossibleDamage: '',
          mitigation: '',
          Criticality: 'Medium',
          MandatoryOptional: 'Mandatory',
          ManualAutomatic: 'Manual',
          Impact: 5.0,
          Probability: 5.0,
          Status: 'Under Review',
          PermanentTemporary: 'Permanent',
          reviewer: 2, // Default reviewer
          impactError: false,
          probabilityError: false
        }
      ],
      loading: false,
      error: null,
      successMessage: null
    }
  },
  async created() {
    await this.loadFrameworks();
    await this.loadUsers();
  },
  watch: {
    selectedFramework(newValue) {
      if (newValue && newValue.id) {
        this.loadPolicies(newValue.id);
        this.selectedPolicy = '';
        this.selectedSubPolicy = '';
        this.policies = [];
        this.subPolicies = [];
      }
    },
    selectedPolicy(newValue) {
      if (newValue && newValue.id) {
        this.loadSubPolicies(newValue.id);
        this.selectedSubPolicy = '';
        this.subPolicies = [];
      }
    }
  },
  methods: {
    async loadFrameworks() {
      try {
        this.loading = true;
        const response = await complianceService.getFrameworks();
        console.log('Frameworks response:', response);
        
        // Handle the actual response format from the API
        // Check if response.data is an array directly instead of expecting data.data
        if (Array.isArray(response.data)) {
          this.frameworks = response.data.map(fw => ({
            id: fw.FrameworkId,
            name: fw.FrameworkName
          }));
        } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
          // Fallback to original expected format
        this.frameworks = response.data.data.map(fw => ({
          id: fw.FrameworkId,
          name: fw.FrameworkName
        }));
        } else {
          console.error('Unexpected framework data format:', response.data);
          this.error = 'Unexpected data format from server';
        }
      } catch (error) {
        this.error = 'Failed to load frameworks';
        console.error('Error loading frameworks:', error);
      } finally {
        this.loading = false;
      }
    },
    async loadPolicies(frameworkId) {
      try {
        this.loading = true;
        const response = await complianceService.getPolicies(frameworkId);
        console.log('Policies response:', response);
        
        // Handle different response formats
        if (Array.isArray(response.data)) {
          this.policies = response.data.map(p => ({
            id: p.PolicyId,
            name: p.PolicyName
          }));
        } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
        this.policies = response.data.data.map(p => ({
          id: p.PolicyId,
          name: p.PolicyName
        }));
        } else {
          console.error('Unexpected policy data format:', response.data);
          this.error = 'Unexpected data format from server';
          this.policies = [];
        }
      } catch (error) {
        this.error = 'Failed to load policies';
        console.error('Error loading policies:', error);
        this.policies = [];
      } finally {
        this.loading = false;
      }
    },
    async loadSubPolicies(policyId) {
      try {
        this.loading = true;
        const response = await complianceService.getSubPolicies(policyId);
        console.log('SubPolicies response:', response);
        
        // Handle different response formats
        if (Array.isArray(response.data)) {
          this.subPolicies = response.data.map(sp => ({
            id: sp.SubPolicyId,
            name: sp.SubPolicyName
          }));
        } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
        this.subPolicies = response.data.data.map(sp => ({
          id: sp.SubPolicyId,
          name: sp.SubPolicyName
        }));
        } else {
          console.error('Unexpected subpolicy data format:', response.data);
          this.error = 'Unexpected data format from server';
          this.subPolicies = [];
        }
      } catch (error) {
        this.error = 'Failed to load sub-policies';
        console.error('Error loading sub-policies:', error);
        this.subPolicies = [];
      } finally {
        this.loading = false;
      }
    },
    async loadUsers() {
      try {
        const response = await complianceService.getUsers();
        console.log('Users response:', response);
        
        // Handle different response formats
        if (response.data && response.data.success && Array.isArray(response.data.users)) {
          this.users = response.data.users;
        } else if (Array.isArray(response.data)) {
          this.users = response.data;
        } else {
          console.error('Unexpected users data format:', response.data);
          // Set default user if we can't load real users
          this.users = [{ UserId: 1, UserName: 'Default User' }];
        }
      } catch (error) {
        console.error('Failed to load users:', error);
        // Set default user if we can't load real users
        this.users = [{ UserId: 1, UserName: 'Default User' }];
      }
    },
    addCompliance() {
      this.complianceList.push({
        ComplianceItemDescription: '',
        Identifier: '',
        IsRisk: false,
        PossibleDamage: '',
        mitigation: '',
        Criticality: 'Medium',
        MandatoryOptional: 'Mandatory',
        ManualAutomatic: 'Manual',
        Impact: 5.0,
        Probability: 5.0,
        Status: 'Under Review',
        PermanentTemporary: 'Permanent',
        reviewer: 2, // Default reviewer
        impactError: false,
        probabilityError: false
      });
    },
    removeCompliance(idx) {
      if (this.complianceList.length > 1) {
        this.complianceList.splice(idx, 1);
      }
    },
    validateImpact(event, idx) {
      const value = parseFloat(event.target.value);
      if (value < 1 || value > 10) {
        this.complianceList[idx].impactError = true;
      } else {
        this.complianceList[idx].impactError = false;
      }
    },
    validateProbability(event, idx) {
      const value = parseFloat(event.target.value);
      if (value < 1 || value > 10) {
        this.complianceList[idx].probabilityError = true;
      } else {
        this.complianceList[idx].probabilityError = false;
      }
    },
    async submitCompliance() {
      // Reset messages
      this.error = null;
      this.successMessage = null;

      // Validate selections
      if (!this.selectedFramework || !this.selectedFramework.id) {
        this.error = 'Please select a framework';
        return;
      }
      if (!this.selectedPolicy || !this.selectedPolicy.id) {
        this.error = 'Please select a policy';
        return;
      }
      if (!this.selectedSubPolicy || !this.selectedSubPolicy.id) {
        this.error = 'Please select a sub-policy';
        return;
      }

      // Validate compliance items
      let hasErrors = false;
      this.complianceList.forEach((compliance, idx) => {
        if (!compliance.ComplianceItemDescription.trim()) {
          this.error = `Please enter a compliance description for item ${idx + 1}`;
          hasErrors = true;
        }
        if (compliance.IsRisk && !compliance.PossibleDamage.trim()) {
          this.error = `Please enter possible damage for risk item ${idx + 1}`;
          hasErrors = true;
        }
        if (!compliance.Impact) {
          this.error = `Please select Impact for item ${idx + 1}`;
          hasErrors = true;
        }
        if (!compliance.Probability) {
          this.error = `Please select Probability for item ${idx + 1}`;
          hasErrors = true;
        }
        if (!compliance.MandatoryOptional) {
          this.error = `Please select Mandatory/Optional for item ${idx + 1}`;
          hasErrors = true;
        }
        if (!compliance.ManualAutomatic) {
          this.error = `Please select Manual/Automatic for item ${idx + 1}`;
          hasErrors = true;
        }
        if (!compliance.Criticality) {
          this.error = `Please select Criticality for item ${idx + 1}`;
          hasErrors = true;
        }
        if (!compliance.PermanentTemporary) {
          this.error = `Please select Permanent/Temporary for item ${idx + 1}`;
          hasErrors = true;
        }
        if (compliance.impactError || compliance.probabilityError) {
          hasErrors = true;
        }
      });

      if (hasErrors) {
        this.error = 'Please correct the Impact and Probability values';
        return;
      }

      try {
        this.loading = true;
        const complianceData = this.complianceList.map(compliance => ({
          SubPolicyId: this.selectedSubPolicy.id,
          ComplianceItemDescription: compliance.ComplianceItemDescription.trim(),
          Identifier: compliance.Identifier.trim() || '',
          IsRisk: Boolean(compliance.IsRisk),
          PossibleDamage: compliance.PossibleDamage.trim(),
          mitigation: compliance.mitigation.trim(),
          Criticality: compliance.Criticality,
          MandatoryOptional: compliance.MandatoryOptional,
          ManualAutomatic: compliance.ManualAutomatic,
          Impact: compliance.Impact,
          Probability: compliance.Probability,
          Status: compliance.Status,
          PermanentTemporary: compliance.PermanentTemporary,
          ComplianceVersion: "1.0", // Always set to 1.0 for new compliances
          reviewer: compliance.reviewer
        }));

        // Submit all compliance items
        for (const data of complianceData) {
          console.log('Submitting compliance data:', data);
          try {
          const response = await complianceService.createCompliance(data);
          console.log('Response:', response);
          
          if (!response.data.success) {
            console.error('Validation errors:', response.data.errors);
            throw new Error(JSON.stringify(response.data.errors) || 'Failed to create compliance');
            }
          } catch (error) {
            console.error('API call error:', error);
            if (error.response) {
              console.error('Error response:', error.response.data);
              console.error('Error status:', error.response.status);
            }
            throw error;
          }
        }

        // Show success message
        this.successMessage = 'Compliance items successfully saved!';
        
        // Reset form
        this.$emit('compliance-created');
        this.complianceList = [
          {
            ComplianceItemDescription: '',
            Identifier: '',
            IsRisk: false,
            PossibleDamage: '',
            mitigation: '',
            Criticality: 'Medium',
            MandatoryOptional: 'Mandatory',
            ManualAutomatic: 'Manual',
            Impact: 5.0,
            Probability: 5.0,
            Status: 'Under Review',
            PermanentTemporary: 'Permanent',
            reviewer: 2, // Default reviewer
            impactError: false,
            probabilityError: false
          }
        ];

        // Clear selections
        this.selectedSubPolicy = '';
        this.selectedPolicy = '';
        this.selectedFramework = '';
      } catch (error) {
        console.error('Error submitting compliance:', error);
        let errorMessage = 'Failed to submit compliance. Please try again.';
        if (error.response?.data?.errors) {
          errorMessage = Object.entries(error.response.data.errors)
            .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
            .join('\n');
        } else if (error.message) {
          try {
            const parsedError = JSON.parse(error.message);
            errorMessage = Object.entries(parsedError)
              .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
              .join('\n');
          } catch {
            errorMessage = error.message;
          }
        }
        this.error = errorMessage;
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
@import './CreateCompliance.css';
</style> 