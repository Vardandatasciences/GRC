<template>
  <div class="compliance-versioning-container">
    <div class="compliance-heading">
      <h1>Compliance Tailoring & Templating</h1>
      <div class="heading-underline"></div>
    </div>
    <div class="selection-row">
      <select v-model="selectedFramework" class="select">
        <option disabled value="">Select Framework</option>
        <option v-for="fw in frameworks" :key="fw.id" :value="fw">{{ fw.name }}</option>
      </select>
      <select v-model="selectedPolicy" class="select" :disabled="!selectedFramework">
        <option disabled value="">Select Policy</option>
        <option v-for="p in policies" :key="p.id" :value="p">{{ p.name }}</option>
      </select>
      <select v-model="selectedSubPolicy" class="select" :disabled="!selectedPolicy">
        <option disabled value="">Select Sub Policy</option>
        <option v-for="sp in subPolicies" :key="sp.id" :value="sp">{{ sp.name }}</option>
      </select>
    </div>

    <div v-if="loading" class="loading">Loading compliances...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="selectedSubPolicy" class="compliance-table-container">
      <h3>Compliances for Selected Subpolicy</h3>
      <div v-if="loading" class="loading">Loading compliances...</div>
      <div v-else-if="subPolicyCompliances.length === 0" class="no-compliances">No compliances found for this subpolicy.</div>
      <table v-else class="compliance-table">
        <thead>
          <tr>
            <th>Description</th>
            <th>Possible Damage</th>
            <th>Mitigation</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(compliance, idx) in subPolicyCompliances" :key="compliance.ComplianceId">
            <!-- If in edit mode, show the full form -->
            <template v-if="editIdx === idx">
              <td colspan="4">
                <form @submit.prevent="saveEdit(compliance)" class="edit-form-grid">
                  <div class="form-row">
                    <div class="form-group">
                      <label>Description</label>
                      <input v-model="editRow.ComplianceItemDescription" class="compliance-input" />
                    </div>
                    <div class="form-group">
                      <label>Is Risk</label>
                      <select v-model="editRow.IsRisk" class="compliance-select">
                        <option :value="true">Yes</option>
                        <option :value="false">No</option>
                      </select>
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Possible Damage</label>
                      <input v-model="editRow.PossibleDamage" class="compliance-input" />
                    </div>
                    <div class="form-group">
                      <label>Mitigation</label>
                      <input v-model="editRow.mitigation" class="compliance-input" />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Criticality</label>
                      <select v-model="editRow.Criticality" class="compliance-select">
                        <option>High</option>
                        <option>Medium</option>
                        <option>Low</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>Mandatory/Optional</label>
                      <select v-model="editRow.MandatoryOptional" class="compliance-select">
                        <option>Mandatory</option>
                        <option>Optional</option>
                      </select>
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Manual/Automatic</label>
                      <select v-model="editRow.ManualAutomatic" class="compliance-select">
                        <option>Manual</option>
                        <option>Automatic</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>Impact (1-10)</label>
                      <input type="number" v-model.number="editRow.Impact" min="1" max="10" step="0.1" class="compliance-input" />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Probability (1-10)</label>
                      <input type="number" v-model.number="editRow.Probability" min="1" max="10" step="0.1" class="compliance-input" />
                    </div>
                    <div class="form-group">
                      <label>Maturity Level</label>
                      <select v-model="editRow.MaturityLevel">
                        <option>Initial</option>
                        <option>Developing</option>
                        <option>Defined</option>
                        <option>Managed</option>
                        <option>Optimizing</option>
                      </select>
                    </div>
                  </div>
                  <div class="form-actions">
                    <button type="submit">Save as New Version</button>
                    <button type="button" @click="cancelEdit">Cancel</button>
                  </div>
                </form>
              </td>
            </template>
            <!-- If in copy mode, show the copy form inline -->
            <template v-else-if="copyIdx === idx">
              <td colspan="4">
                <form @submit.prevent="confirmCopy" class="edit-form-grid">
                  <div class="form-row">
                    <div class="form-group">
                      <label>Description</label>
                      <input v-model="copyRow.ComplianceItemDescription" class="compliance-input" />
                    </div>
                    <div class="form-group">
                      <label>Is Risk</label>
                      <select v-model="copyRow.IsRisk" class="compliance-select">
                        <option :value="true">Yes</option>
                        <option :value="false">No</option>
                      </select>
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Possible Damage</label>
                      <input v-model="copyRow.PossibleDamage" class="compliance-input" />
                    </div>
                    <div class="form-group">
                      <label>Mitigation</label>
                      <input v-model="copyRow.mitigation" class="compliance-input" />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Criticality</label>
                      <select v-model="copyRow.Criticality" class="compliance-select">
                        <option>High</option>
                        <option>Medium</option>
                        <option>Low</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>Mandatory/Optional</label>
                      <select v-model="copyRow.MandatoryOptional" class="compliance-select">
                        <option>Mandatory</option>
                        <option>Optional</option>
                      </select>
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Manual/Automatic</label>
                      <select v-model="copyRow.ManualAutomatic" class="compliance-select">
                        <option>Manual</option>
                        <option>Automatic</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>Impact (1-10)</label>
                      <input type="number" v-model.number="copyRow.Impact" min="1" max="10" step="0.1" class="compliance-input" />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Probability (1-10)</label>
                      <input type="number" v-model.number="copyRow.Probability" min="1" max="10" step="0.1" class="compliance-input" />
                    </div>
                    <div class="form-group">
                      <label>Maturity Level</label>
                      <select v-model="copyRow.MaturityLevel">
                        <option>Initial</option>
                        <option>Developing</option>
                        <option>Defined</option>
                        <option>Managed</option>
                        <option>Optimizing</option>
                      </select>
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Framework</label>
                      <select v-model="copyTarget.frameworkId">
                        <option disabled value="">Select Framework</option>
                        <option v-for="fw in frameworks" :key="fw.id" :value="fw.id">{{ fw.name }}</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>Policy</label>
                      <select v-model="copyTarget.policyId" :disabled="!copyTarget.frameworkId">
                        <option disabled value="">Select Policy</option>
                        <option v-for="p in copyPolicies" :key="p.id" :value="p.id">{{ p.name }}</option>
                      </select>
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Sub Policy</label>
                      <select v-model="copyTarget.subPolicyId" :disabled="!copyTarget.policyId">
                        <option disabled value="">Select Sub Policy</option>
                        <option v-for="sp in filteredCopySubPolicies" :key="sp.id" :value="sp.id">{{ sp.name }}</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>&nbsp;</label>
                      <div>
                        <button type="submit" :disabled="!canSaveCopy">Save Copy</button>
                        <button type="button" @click="cancelCopy">Cancel</button>
                      </div>
                    </div>
                  </div>
                  <div v-if="copyError" class="copy-error">{{ copyError }}</div>
                </form>
              </td>
            </template>
            <!-- Normal view: only 3 fields + actions -->
            <template v-else>
              <td>{{ compliance.ComplianceItemDescription }}</td>
              <td>{{ compliance.PossibleDamage }}</td>
              <td>{{ compliance.mitigation }}</td>
              <td>
                <div class="action-btn-group">
                  <button @click="startEdit(idx, compliance)" title="Edit" class="action-btn edit-btn"><i class="fas fa-edit"></i></button>
                  <button @click="openCopyInline(idx, compliance)" title="Copy" class="action-btn copy-btn"><i class="fas fa-copy"></i></button>
                </div>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { complianceService } from '@/services/api';

export default {
  name: 'ComplianceVersioning',
  data() {
    return {
      selectedFramework: '',
      selectedPolicy: '',
      selectedSubPolicy: '',
      frameworks: [],
      policies: [],
      subPolicies: [],
      subPolicyCompliances: [],
      loading: false,
      error: null,
      editIdx: null,
      editRow: {},
      // Copy modal state
      showCopyModal: false,
      copyIdx: null,
      copyRow: {},
      copyTarget: { frameworkId: '', policyId: '', subPolicyId: '' },
      copyPolicies: [],
      copySubPolicies: [],
      copyError: '',
      sourceSubPolicyId: null, // Add this to track source subpolicy
    }
  },
  async created() {
    await this.loadFrameworks();
  },
  watch: {
    selectedFramework(newValue) {
      if (newValue && newValue.id) {
        this.loadPolicies(newValue.id);
        this.selectedPolicy = '';
        this.selectedSubPolicy = '';
        this.policies = [];
        this.subPolicies = [];
        this.subPolicyCompliances = [];
      }
    },
    selectedPolicy(newValue) {
      if (newValue && newValue.id) {
        this.loadSubPolicies(newValue.id);
        this.selectedSubPolicy = '';
        this.subPolicies = [];
        this.subPolicyCompliances = [];
      }
    },
    selectedSubPolicy: {
      handler: async function(newValue) {
        this.subPolicyCompliances = [];
        if (newValue && newValue.id) {
          try {
            this.loading = true;
            const response = await complianceService.getCompliancesBySubPolicy(newValue.id);
            this.subPolicyCompliances = response.data.data || [];
          } catch (error) {
            this.error = 'Failed to load compliances for subpolicy';
            console.error(error);
          } finally {
            this.loading = false;
          }
        }
      },
      immediate: true
    },
    'copyTarget.frameworkId': 'copyTarget_frameworkId',
    'copyTarget.policyId': 'copyTarget_policyId'
  },
  computed: {
    canSaveCopy() {
      return this.copyRow.ComplianceItemDescription &&
        this.copyRow.Criticality &&
        this.copyRow.MandatoryOptional &&
        this.copyRow.ManualAutomatic &&
        this.copyRow.Impact && this.copyRow.Impact >= 1 && this.copyRow.Impact <= 10 &&
        this.copyRow.Probability && this.copyRow.Probability >= 1 && this.copyRow.Probability <= 10 &&
        this.copyRow.MaturityLevel &&
        this.copyTarget.frameworkId &&
        this.copyTarget.policyId &&
        this.copyTarget.subPolicyId;
    },
    filteredCopySubPolicies() {
      // Filter out the source subpolicy from the dropdown
      return this.copySubPolicies.filter(sp => sp.id !== this.sourceSubPolicyId);
    }
  },
  methods: {
    async loadFrameworks() {
      try {
        this.loading = true;
        const response = await complianceService.getFrameworks();
        this.frameworks = response.data.data.map(fw => ({
          id: fw.FrameworkId,
          name: fw.FrameworkName
        }));
      } catch (error) {
        this.error = 'Failed to load frameworks';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    async loadPolicies(frameworkId) {
      try {
        this.loading = true;
        const response = await complianceService.getPolicies(frameworkId);
        this.policies = response.data.data.map(p => ({
          id: p.PolicyId,
          name: p.PolicyName
        }));
      } catch (error) {
        this.error = 'Failed to load policies';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    async loadSubPolicies(policyId) {
      try {
        this.loading = true;
        const response = await complianceService.getSubPolicies(policyId);
        this.subPolicies = response.data.data.map(sp => ({
          id: sp.SubPolicyId,
          name: sp.SubPolicyName
        }));
      } catch (error) {
        this.error = 'Failed to load sub-policies';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    startEdit(idx, compliance) {
      this.editIdx = idx;
      this.editRow = { ...compliance };
    },
    cancelEdit() {
      this.editIdx = null;
      this.editRow = {};
    },
    async saveEdit(compliance) {
      try {
        this.loading = true;
        await this.$nextTick();
        
        // Prepare the edited data with an incremented version
        const currentVersion = parseFloat(compliance.ComplianceVersion) || 1.0;
        const newVersion = Math.floor(currentVersion + 1).toFixed(1);
        
        // Always set new versions to Under Review and Inactive
        this.editRow = {
          ...this.editRow,
          ComplianceVersion: newVersion,
          Status: 'Under Review',
          ActiveInactive: 'Inactive',
          PreviousComplianceVersionId: compliance.ComplianceId
        };
        
        // Use the complianceService instead of direct axios
        await complianceService.editCompliance(compliance.ComplianceId, this.editRow);
        
        this.editIdx = null;
        this.editRow = {};
        
        // Refresh compliances
        const response = await complianceService.getCompliancesBySubPolicy(this.selectedSubPolicy.id);
        this.subPolicyCompliances = response.data.data || [];
        
      } catch (error) {
        console.error('Edit error:', error);
        this.error = 'Failed to save new version: ' + (error.response?.data?.message || error.message);
      } finally {
        this.loading = false;
      }
    },
    // Copy modal logic
    openCopyInline(idx, compliance) {
      this.editIdx = null; // Cancel edit mode if active
      this.copyIdx = idx;
      this.copyRow = { ...compliance };
      this.sourceSubPolicyId = this.selectedSubPolicy.id; // Store the source subpolicy ID
      this.copyTarget = { frameworkId: '', policyId: '', subPolicyId: '' };
      this.copyPolicies = [];
      this.copySubPolicies = [];
      this.copyError = '';
      this.showCopyModal = true;
      // Preload all frameworks, policies, and subpolicies for the modal
      this.loadFrameworks();
    },
    cancelCopy() {
      this.showCopyModal = false;
      this.copyIdx = null;
      this.copyRow = {};
      this.sourceSubPolicyId = null; // Reset source subpolicy ID
      this.copyTarget = { frameworkId: '', policyId: '', subPolicyId: '' };
      this.copyPolicies = [];
      this.copySubPolicies = [];
      this.copyError = '';
    },
    async confirmCopy() {
      if (!this.canSaveCopy) {
        this.copyError = 'Please fill all required fields and select a destination.';
        return;
      }
      try {
        this.loading = true;
        this.copyError = '';
        await this.$nextTick();

        const cloneData = {
          ...this.copyRow,
          Impact: String(this.copyRow.Impact),
          Probability: String(this.copyRow.Probability),
          target_subpolicy_id: this.copyTarget.subPolicyId,
          Status: 'Under Review',
          ActiveInactive: 'Inactive',
          PermanentTemporary: this.copyRow.PermanentTemporary || 'Permanent',
          ComplianceVersion: '1.0'
        };

        const response = await complianceService.cloneCompliance(
          this.subPolicyCompliances[this.copyIdx].ComplianceId,
          cloneData
        );

        if (response.data.success) {
          this.cancelCopy();
          // Refresh compliances
          const resp = await complianceService.getCompliancesBySubPolicy(this.selectedSubPolicy.id);
          this.subPolicyCompliances = resp.data.data || [];
          this.$toast && this.$toast.success('Compliance copied successfully');
        } else {
          this.copyError = response.data.message || 'Failed to copy compliance';
        }
      } catch (error) {
        console.error('Copy error:', error);
        this.copyError = 'Failed to copy compliance: ' + (error.response?.data?.message || error.message);
      } finally {
        this.loading = false;
      }
    },
    // Watchers for copy dropdowns
    async copyTarget_frameworkId(newValue) {
      if (newValue) {
        const response = await complianceService.getPolicies(newValue);
        this.copyPolicies = response.data.data.map(p => ({ id: p.PolicyId, name: p.PolicyName }));
        this.copyTarget.policyId = '';
        this.copyTarget.subPolicyId = '';
        this.copySubPolicies = [];
      }
    },
    async copyTarget_policyId(newValue) {
      if (newValue) {
        const response = await complianceService.getSubPolicies(newValue);
        this.copySubPolicies = response.data.data.map(sp => ({ id: sp.SubPolicyId, name: sp.SubPolicyName }));
        this.copyTarget.subPolicyId = '';
      }
    }
  }
}
</script>

<style scoped>
@import './ComplianceTailoring.css';
</style> 