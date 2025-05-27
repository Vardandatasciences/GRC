<template>
  <div class="task-view">
    <!-- Fixed position save button -->
    <div class="floating-save">
      <button @click="submitChangedFields" class="submit-btn" :disabled="Object.keys(changedFields).length === 0">
        <span v-if="saving">Saving...</span>
        <span v-else>Save Changes</span>
        <span v-if="Object.keys(changedFields).length > 0" class="changes-count">
          ({{ Object.keys(changedFields).length }})
        </span>
      </button>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Loading compliances...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="fetchCompliances" class="retry-btn">Retry</button>
    </div>
    <div v-else>
      <div v-if="policies.length === 0" class="no-data">
        <p>No compliances found for this audit.</p>
      </div>
      <div v-else class="audit-content">
        <div class="page-header">
          <h1 class="framework-title">{{ frameworkName }}</h1>
          <div class="header-controls">
            <div class="collapse-controls">
              <button @click="expandAllSubpolicies" class="control-btn expand-all">Expand All</button>
              <button @click="collapseAllSubpolicies" class="control-btn collapse-all">Collapse All</button>
            </div>
            <div class="save-status" v-if="saveStatus">
              <span :class="saveStatus === 'Saved' ? 'save-success' : saveStatus === 'Saving...' ? 'save-progress' : 'save-error'">
                <span class="save-icon">{{ saveStatus === 'Saved' ? '✓' : saveStatus === 'Saving...' ? '⟳' : '✗' }}</span>
                {{ saveStatus }}
              </span>
            </div>
          </div>
        </div>
        
        <div v-for="policy in policies" :key="policy.policy_id" class="policy-section">
          <div class="policy-header">
            <h2 class="policy-title">{{ policy.policy_name }}</h2>
          </div>
          
          <div v-for="subpolicy in policy.subpolicies" :key="subpolicy.subpolicy_id" class="subpolicy-section" :class="{'subpolicy-completed': isSubpolicyCompleted(subpolicy)}">
            <div class="subpolicy-header">
              <div class="subpolicy-info">
                <h3 class="subpolicy-title">
                  {{ subpolicy.subpolicy_name }}
                  <span class="compliance-count">({{ subpolicy.compliances.length }} items)</span>
                </h3>
                <div class="subpolicy-progress">
                  <div 
                    class="progress-bar"
                  >
                    <div 
                      class="progress-fill"
                      :style="{ width: calculateSubpolicyProgress(subpolicy) + '%' }"
                      :class="getProgressClass(calculateSubpolicyProgress(subpolicy))"
                    ></div>
                  </div>
                  <span class="progress-text">{{ calculateSubpolicyProgress(subpolicy) }}% Complete</span>
                </div>
              </div>
              <div class="subpolicy-controls">
                <button 
                  class="toggle-btn"
                  @click="toggleSubpolicy(subpolicy.subpolicy_id)"
                >
                  <span class="toggle-icon">{{ isSubpolicyCollapsed(subpolicy.subpolicy_id) ? '▶' : '▼' }}</span>
                  {{ isSubpolicyCollapsed(subpolicy.subpolicy_id) ? 'Expand' : 'Collapse' }}
                </button>
                <button @click="openAddComplianceModal(policy, subpolicy)" class="add-compliance-btn">
                  <span class="add-icon">+</span> Add Compliance
                </button>
              </div>
            </div>
            
            <div class="compliance-list" v-show="!isSubpolicyCollapsed(subpolicy.subpolicy_id)">
              <div v-for="compliance in subpolicy.compliances" :key="compliance.compliance_id" class="compliance-item">
                <div class="compliance-header">
                  <span class="compliance-description">
                    {{ compliance.description }}
                  </span>
                  <div class="compliance-indicators">
                    <!-- Reviewer accept/reject status badge -->
                    <span v-if="compliance.review_status" :class="getReviewStatusClass(compliance.review_status)" class="review-status-badge">
                      {{ compliance.review_status }}
                    </span>
                    <span :class="getCriticalityClass(compliance.criticality)" class="criticality-badge">
                      {{ compliance.criticality }}
                    </span>
                    <span :class="['status-badge', getStatusClass(compliance.compliance_status)]">
                      {{ compliance.compliance_status || 'Not Assessed' }}
                    </span>
                  </div>
                </div>
                
                <div class="compliance-fields">
                  <div class="field-group">
                    <label>Compliant Status:</label>
                    <select 
                      v-model="compliance.compliance_status" 
                      class="compliance-dropdown"
                      @change="updateComplianceField(compliance, 'compliance_status', compliance.compliance_status)"
                    >
                      <option value="Not Compliant">Not Compliant</option>
                      <option value="Partially Compliant">Partially Compliant</option>
                      <option value="Fully Compliant">Fully Compliant</option>
                      <option value="Not Applicable">Not Applicable</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Major/Minor:</label>
                    <div class="criticality-container">
                      <select 
                        v-model="compliance.criticality" 
                        class="compliance-dropdown"
                        @change="updateComplianceField(compliance, 'criticality', compliance.criticality)"
                      >
                        <option value="Major">Major</option>
                        <option value="Minor">Minor</option>
                        <option value="Not Applicable">Not Applicable</option>
                      </select>
                    </div>
                  </div>
                </div>
                
                <div class="text-fields">
                  <div class="field-group">
                    <label>How to Verify:</label>
                    <textarea 
                      v-model="compliance.how_to_verify" 
                      class="compliance-textarea"
                      placeholder="Enter verification steps..."
                      @input="updateComplianceField(compliance, 'how_to_verify', compliance.how_to_verify)"
                    ></textarea>
                    <span 
                      v-if="isSavingField(compliance.compliance_id, 'how_to_verify')" 
                      class="field-indicator field-saving"
                    >Saving...</span>
                    <span 
                      v-else-if="isRecentlySaved(compliance.compliance_id, 'how_to_verify')" 
                      class="field-indicator field-saved"
                    >Saved</span>
                  </div>
                  
                  <div class="field-group">
                    <label>Impact:</label>
                    <textarea 
                      v-model="compliance.impact" 
                      class="compliance-textarea"
                      placeholder="Describe the impact..."
                      @input="updateComplianceField(compliance, 'impact', compliance.impact)"
                    ></textarea>
                    <span 
                      v-if="isSavingField(compliance.compliance_id, 'impact')" 
                      class="field-indicator field-saving"
                    >Saving...</span>
                    <span 
                      v-else-if="isRecentlySaved(compliance.compliance_id, 'impact')" 
                      class="field-indicator field-saved"
                    >Saved</span>
                  </div>
                  
                  <div class="field-group">
                    <label>Details of Findings:</label>
                    <textarea 
                      v-model="compliance.details_of_finding" 
                      class="compliance-textarea"
                      placeholder="Enter detailed findings..."
                      @input="updateComplianceField(compliance, 'details_of_finding', compliance.details_of_finding)"
                    ></textarea>
                    <span 
                      v-if="isSavingField(compliance.compliance_id, 'details_of_finding')" 
                      class="field-indicator field-saving"
                    >Saving...</span>
                    <span 
                      v-else-if="isRecentlySaved(compliance.compliance_id, 'details_of_finding')" 
                      class="field-indicator field-saved"
                    >Saved</span>
                  </div>
                  
                  <div class="field-group">
                    <label>Recommendation:</label>
                    <textarea 
                      v-model="compliance.recommendation" 
                      class="compliance-textarea"
                      placeholder="Provide recommendations..."
                      @input="updateComplianceField(compliance, 'recommendation', compliance.recommendation)"
                    ></textarea>
                    <span 
                      v-if="isSavingField(compliance.compliance_id, 'recommendation')" 
                      class="field-indicator field-saving"
                    >Saving...</span>
                    <span 
                      v-else-if="isRecentlySaved(compliance.compliance_id, 'recommendation')" 
                      class="field-indicator field-saved"
                    >Saved</span>
                  </div>
                  
                  <div class="field-group">
                    <label>Comments:</label>
                    <textarea 
                      v-model="compliance.comments" 
                      class="compliance-textarea"
                      placeholder="Add comments..."
                      @input="updateComplianceField(compliance, 'comments', compliance.comments)"
                    ></textarea>
                    <span 
                      v-if="isSavingField(compliance.compliance_id, 'comments')" 
                      class="field-indicator field-saving"
                    >Saving...</span>
                    <span 
                      v-else-if="isRecentlySaved(compliance.compliance_id, 'comments')" 
                      class="field-indicator field-saved"
                    >Saved</span>
                  </div>

                  <!-- Reviewer Comments (read-only) -->
                  <div class="field-group">
                    <label>Reviewer Comments:</label>
                    <textarea
                      class="compliance-textarea"
                      :value="compliance.reviewer_comments || compliance.review_comments || ''"
                      placeholder="No reviewer comments"
                      readonly
                      disabled
                      style="background: #f8f9fa; color: #666;"
                    ></textarea>
                  </div>
                </div>
                
                <div class="evidence-upload">
                  <label>Evidence:</label>
                  <div class="upload-container">
                    <input 
                      type="file" 
                      id="evidence-file" 
                      class="file-input" 
                      @change="handleFileUpload($event, compliance)"
                    >
                    <label for="evidence-file" class="upload-btn">Upload Evidence</label>
                    <span class="file-name">{{ compliance.file_name || 'No file selected' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Add the modal at the root level of the component template -->
    <div class="modal-overlay" v-if="showAddComplianceModal" @click.self="closeAddComplianceModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Add New Compliance Item</h3>
          <button @click="closeAddComplianceModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitComplianceForm">
            <!-- Framework, Policy, Subpolicy selection section -->
            <div class="form-section">
              <h4>Item Context</h4>
              
              <div class="form-group">
                <label>Framework:</label>
                <input type="text" v-model="selectedFrameworkName" disabled class="form-control disabled" />
              </div>
              
              <div class="form-group">
                <label>Policy:</label>
                <input v-if="isPolicyFrozen" type="text" v-model="selectedPolicyName" disabled class="form-control disabled" />
                <select v-else v-model="newCompliance.policy_id" @change="handlePolicyChange" class="form-control">
                  <option value="">-- Select Policy --</option>
                  <option v-for="policy in availablePolicies" :key="policy.PolicyId" :value="policy.PolicyId">
                    {{ policy.PolicyName }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label>SubPolicy:</label>
                <input v-if="isSubpolicyFrozen" type="text" v-model="selectedSubpolicyName" disabled class="form-control disabled" />
                <select v-else v-model="newCompliance.subpolicy_id" class="form-control">
                  <option value="">-- Select SubPolicy --</option>
                  <option v-for="subpolicy in availableSubpolicies" :key="subpolicy.SubPolicyId" :value="subpolicy.SubPolicyId">
                    {{ subpolicy.SubPolicyName }}
                  </option>
                </select>
              </div>
            </div>
            
            <!-- Compliance details section -->
            <div class="form-section">
              <h4>Compliance Details</h4>
              
              <div class="form-group required">
                <label>Description:</label>
                <textarea v-model="newCompliance.description" required class="form-control" rows="3"></textarea>
              </div>
              
              <div class="form-group">
                <label>Is Risk:</label>
                <select v-model="newCompliance.is_risk" class="form-control">
                  <option :value="false">No</option>
                  <option :value="true">Yes</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Possible Damage:</label>
                <textarea v-model="newCompliance.possible_damage" class="form-control" rows="2"></textarea>
              </div>
              
              <div class="form-group">
                <label>Mitigation:</label>
                <textarea v-model="newCompliance.mitigation" class="form-control" rows="2"></textarea>
              </div>
            </div>
            
            <!-- Classification section -->
            <div class="form-section">
              <h4>Classification</h4>
              
              <div class="form-row">
                <div class="form-group half">
                  <label>Criticality:</label>
                  <select v-model="newCompliance.criticality" class="form-control">
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
                
                <div class="form-group half">
                  <label>Mandatory/Optional:</label>
                  <select v-model="newCompliance.mandatory_optional" class="form-control">
                    <option value="Mandatory">Mandatory</option>
                    <option value="Optional">Optional</option>
                  </select>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group half">
                  <label>Impact:</label>
                  <select v-model="newCompliance.impact" class="form-control">
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
                
                <div class="form-group half">
                  <label>Probability:</label>
                  <select v-model="newCompliance.probability" class="form-control">
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeAddComplianceModal" class="cancel-btn">Cancel</button>
              <button type="submit" :disabled="isSubmitting" class="submit-btn">
                {{ isSubmitting ? 'Saving...' : 'Add Compliance' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../../data/api';

export default {
  name: 'TaskView',
  props: {
    auditId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      loading: true,
      policies: [],
      error: null,
      frameworkName: '',
      auditDetails: null,
      saveTimeout: null,
      saving: false,
      lastSaved: null,
      saveStatus: null,
      savingFields: {},
      savedFields: {},
      collapsedSubpolicies: {},
      isReviewVersion: false,
      versionId: null,
      
      // Add compliance modal state
      showAddComplianceModal: false,
      isSubmitting: false,
      selectedPolicy: null,
      selectedFrameworkName: '',
      selectedPolicyName: '',
      selectedSubpolicyName: '',
      isPolicyFrozen: false,
      isSubpolicyFrozen: false,
      availablePolicies: [],
      availableSubpolicies: [],
      newCompliance: {
        subpolicy_id: '',
        policy_id: '',
        description: '',
        is_risk: false,
        possible_damage: '',
        mitigation: '',
        criticality: 'Medium',
        mandatory_optional: 'Mandatory',
        manual_automatic: 'Manual',
        impact: 'Medium',
        probability: 'Medium',
        active_inactive: 'Active',
        permanent_temporary: 'Temporary',
        ComplianceVersion: '0'  // Use ComplianceVersion to match backend model
      },
      changedFields: {} // Track which fields have been modified
    };
  },
  async created() {
    await this.fetchAuditDetails();
    await this.loadAuditVersionData();
    await this.fetchCompliances();
  },
  methods: {
    async fetchAuditDetails() {
      try {
        console.log('Fetching audit details for audit ID:', this.auditId);
        const response = await api.getAuditDetails(this.auditId);
        this.auditDetails = response.data;
        this.frameworkName = this.auditDetails.framework || 'Framework';
        console.log('Audit details:', this.auditDetails);
      } catch (error) {
        console.error('Error fetching audit details:', error);
        this.frameworkName = 'Framework';
      }
    },
    async loadAuditVersionData() {
      try {
        console.log('Loading audit version data for audit ID:', this.auditId);
        
        // Call the backend to load the latest version
        const response = await api.loadAuditContinuingData(this.auditId);
        console.log('Loaded audit version data:', response.data);
        
        if (response.data) {
          this.isReviewVersion = response.data.is_reviewer_version || false;
          this.versionId = response.data.version_id;
          this.versionData = response.data.data;
          
          // Log info about the version
          console.log(`Using ${this.isReviewVersion ? 'reviewer' : 'auditor'} version: ${this.versionId}`);
        }
        
      } catch (error) {
        console.error('Error loading audit version data:', error);
        // We'll continue without version data if it fails
      }
    },
    async fetchCompliances() {
      try {
        this.loading = true;
        this.error = null;
        console.log('Fetching compliances for audit ID:', this.auditId);
        const response = await api.getAuditCompliances(this.auditId);
        console.log('Compliance data:', response.data);
        
        // Process the data to include additional fields if not present
        const policies = response.data.policies;
        policies.forEach(policy => {
          policy.subpolicies.forEach(subpolicy => {
            subpolicy.compliances.forEach(compliance => {
              // Debug log for criticality values
              console.log(`Original criticality value for compliance ${compliance.compliance_id}: ${compliance.criticality} (type: ${typeof compliance.criticality})`);
              console.log(`Original compliance status: ${compliance.compliance_status}, status code: ${compliance.status}`);
              
              // Add review status data from the version data if available
              if (this.versionData) {
                const complianceId = compliance.compliance_id.toString();
                const versionComplianceData = this.versionData[complianceId];
                
                if (versionComplianceData) {
                  // Get review status from accept_reject value
                  const acceptReject = versionComplianceData.accept_reject;
                  if (acceptReject) {
                    if (acceptReject === '1' || acceptReject === 1) {
                      compliance.review_status = 'Accept';
                    } else if (acceptReject === '2' || acceptReject === 2) {
                      compliance.review_status = 'Reject';
                    } else {
                      compliance.review_status = 'In Review';
                    }
                  }
                  
                  // Get reviewer comments from the version data
                  if (versionComplianceData.comments) {
                    compliance.reviewer_comments = versionComplianceData.comments;
                  } else if (versionComplianceData.review_comments) {
                    compliance.reviewer_comments = versionComplianceData.review_comments;
                  }
                  
                  console.log(`Added review status '${compliance.review_status}' for compliance ${complianceId} from version data`);
                }
              }
              
              // Use the compliance_status from backend if available
              if (!compliance.compliance_status) {
                // Only do the mapping if compliance_status is not already set by backend
                // Handle special case where status '3' is Not Applicable
                if (compliance.status === '3') {
                  compliance.compliance_status = 'Not Applicable';
                  console.log(`Setting compliance_status to 'Not Applicable' for ID: ${compliance.compliance_id} based on status '3'`);
                } 
                // Also check for Not Applicable marker in comments as fallback
                else if (compliance.comments && compliance.comments.includes("[Not Applicable]")) {
                  compliance.compliance_status = 'Not Applicable';
                  console.log(`Setting compliance_status to 'Not Applicable' for ID: ${compliance.compliance_id} based on comment marker`);
                  
                  // Only clean up the comments if it EXACTLY matches the marker
                  if (compliance.comments === "[Not Applicable]") {
                    console.log(`Cleaning up exact [Not Applicable] marker from comments for ID: ${compliance.compliance_id}`);
                    compliance.comments = '';
                  } else {
                    // Keep the original comments intact if the marker is just part of a larger comment
                    console.log(`Keeping original comments for ID: ${compliance.compliance_id}: "${compliance.comments}"`);
                  }
                } else if (compliance.status === '2') {
                  compliance.compliance_status = 'Fully Compliant';
                  console.log(`Setting compliance_status to 'Fully Compliant' for ID: ${compliance.compliance_id} based on status '2'`);
                } else if (compliance.status === '1') {
                  compliance.compliance_status = 'Partially Compliant';
                  console.log(`Setting compliance_status to 'Partially Compliant' for ID: ${compliance.compliance_id} based on status '1'`);
                } else {
                  compliance.compliance_status = 'Not Compliant';
                  console.log(`Setting compliance_status to 'Not Compliant' for ID: ${compliance.compliance_id} based on status '${compliance.status}'`);
                }
              } else {
                console.log(`Using compliance_status "${compliance.compliance_status}" from backend for ID: ${compliance.compliance_id}`);
              }
              
              // Convert numeric criticality values to text
              // Backend stores: 0 = Minor, 1 = Major, 2 = Not Applicable
              if (compliance.criticality === 0 || compliance.criticality === '0') {
                compliance.criticality = 'Minor';
              } else if (compliance.criticality === 1 || compliance.criticality === '1') {
                compliance.criticality = 'Major';
              } else if (compliance.criticality === 2 || compliance.criticality === '2') {
                compliance.criticality = 'Not Applicable';
              }
              // Fallback for any other values
              if (typeof compliance.criticality === 'number' || !isNaN(parseInt(compliance.criticality))) {
                console.log(`Converting unknown numeric criticality value: ${compliance.criticality}`);
                compliance.criticality = 'Minor'; // Default fallback
              }
              
              // Ensure all fields are initialized
              compliance.criticality = compliance.criticality || 'Not Applicable';
              compliance.how_to_verify = compliance.how_to_verify || '';
              compliance.impact = compliance.impact || '';
              compliance.details_of_finding = compliance.details_of_finding || '';
              compliance.recommendation = compliance.recommendation || '';
              compliance.comments = compliance.comments || '';
              compliance.reviewer_comments = compliance.reviewer_comments || '';
              compliance.review_status = compliance.review_status || '';
              compliance.file_name = '';
              
              // Store original values for change tracking
              this.storeOriginalValue(compliance, 'compliance_status', compliance.compliance_status);
              this.storeOriginalValue(compliance, 'criticality', compliance.criticality);
              this.storeOriginalValue(compliance, 'how_to_verify', compliance.how_to_verify);
              this.storeOriginalValue(compliance, 'impact', compliance.impact);
              this.storeOriginalValue(compliance, 'details_of_finding', compliance.details_of_finding);
              this.storeOriginalValue(compliance, 'recommendation', compliance.recommendation);
              this.storeOriginalValue(compliance, 'comments', compliance.comments);
            });
          });
        });
        
        // Auto-collapse completed subpolicies
        policies.forEach(policy => {
          policy.subpolicies.forEach(subpolicy => {
            const isCompleted = this.isSubpolicyCompleted(subpolicy);
            // Mark completed subpolicies as collapsed by default
            if (isCompleted) {
              this.collapsedSubpolicies[subpolicy.subpolicy_id] = true;
            }
          });
        });
        
        this.policies = policies;
      } catch (error) {
        console.error('Error fetching compliances:', error);
        this.error = error.response?.data?.error || 'Failed to load compliances';
      } finally {
        this.loading = false;
      }
    },
    getStatusClass(status) {
      if (!status) return 'not-assessed';
      
      switch(status) {
        case 'Fully Compliant':
          return 'fully-compliant';
        case 'Partially Compliant':
          return 'partially-compliant';
        case 'Not Compliant':
          return 'not-compliant';
        case 'Not Applicable':
          return 'not-applicable';
        default:
          return 'not-assessed';
      }
    },
    getCriticalityClass(criticality) {
      if (!criticality) return 'criticality-na';
      
      switch(criticality) {
        case 'Major':
          return 'criticality-major';
        case 'Minor':
          return 'criticality-minor';
        case 'Not Applicable':
          return 'criticality-na';
        default:
          return 'criticality-na';
      }
    },
    async updateComplianceField(compliance, field, value) {
      try {
        // Don't save immediately - just track the changes
        const originalValue = this.getOriginalValue(compliance, field);
        if (originalValue === value) {
          console.log(`Field ${field} not changed (${value})`);
          
          // Remove from changed fields if it's reverting to original value
          const fieldKey = `${compliance.compliance_id}_${field}`;
          if (this.changedFields[fieldKey]) {
            delete this.changedFields[fieldKey];
          }
          
          return;
        }
        
        console.log(`Field ${field} changed from "${originalValue}" to "${value}"`);
        
        // Track this change
        const fieldKey = `${compliance.compliance_id}_${field}`;
        this.changedFields[fieldKey] = {
          complianceId: compliance.compliance_id,
          field: field,
          value: value
        };
        
      } catch (error) {
        console.error(`Error tracking change for ${field}:`, error);
        }
    },
    
    // New method to submit only changed fields
    async submitChangedFields() {
      if (Object.keys(this.changedFields).length === 0) {
        alert("No changes to save");
        return;
      }
      
      try {
        this.saving = true;
        this.saveStatus = 'Saving...';
        
        const changeCount = Object.keys(this.changedFields).length;
        console.log(`Submitting ${changeCount} changed fields`);
        
        // Group changes by compliance ID to minimize API calls
        const changesByCompliance = {};
        
        for (const key in this.changedFields) {
          const change = this.changedFields[key];
          const complianceId = change.complianceId;
          
          if (!changesByCompliance[complianceId]) {
            changesByCompliance[complianceId] = {};
          }
          
          changesByCompliance[complianceId][change.field] = change.value;
        }
        
        // Make API calls for each compliance item with changes
        const savePromises = [];
        for (const complianceId in changesByCompliance) {
          const data = changesByCompliance[complianceId];
            
          // Remove auto_save flag as we're manually saving now
          data.auto_save = false;
          
          console.log(`Saving changes for compliance ${complianceId}:`, data);
          savePromises.push(api.updateComplianceStatus(complianceId, data));
        }
        
        // Wait for all save operations to complete
        const results = await Promise.all(savePromises);
        console.log('All changes saved successfully', results);
              
        // Update original values after saving
        for (const key in this.changedFields) {
          const change = this.changedFields[key];
          
          // Find this compliance in our local state
          this.policies.forEach(localPolicy => {
            localPolicy.subpolicies.forEach(localSubpolicy => {
              localSubpolicy.compliances.forEach(localCompliance => {
                if (localCompliance.compliance_id === change.complianceId) {
                  // Update the original value to mark it as no longer changed
                  this.storeOriginalValue(localCompliance, change.field, change.value);
                }
              });
            });
          });
            }
            
        // Clear the changed fields tracking
        this.changedFields = {};
        
        // Update save status
        this.saveStatus = 'Saved';
        this.lastSaved = new Date();
            
            // Reset save status after 3 seconds
            setTimeout(() => {
              this.saveStatus = null;
            }, 3000);
        
        // Show success message
        alert(`Successfully saved ${changeCount} changes`);
        
      } catch (error) {
        console.error('Error saving changes:', error);
        this.saveStatus = 'Save failed';
        alert('Failed to save changes: ' + (error.response?.data?.error || error.message));
      } finally {
        this.saving = false;
      }
    },
    
    // Store original values to track changes
    storeOriginalValue(compliance, field, value) {
      if (!compliance._originalValues) {
        compliance._originalValues = {};
      }
      compliance._originalValues[field] = value;
    },
    
    // Get original value or current value if not stored
    getOriginalValue(compliance, field) {
      if (compliance._originalValues && field in compliance._originalValues) {
        return compliance._originalValues[field];
      }
      return compliance[field];
    },
    async handleFileUpload(event, compliance) {
      const file = event.target.files[0];
      if (!file) return;
      
      compliance.file_name = file.name;
      
      // Just mark the file as changed, don't upload yet
      const fieldKey = `${compliance.compliance_id}_evidence`;
      this.changedFields[fieldKey] = {
        complianceId: compliance.compliance_id,
        field: 'evidence',
        value: file,
        isFile: true
      };
      
      console.log('File queued for upload', file.name);
    },
    async refreshCompliance(complianceId) {
      try {
        console.log(`Refreshing compliance data for ID: ${complianceId}`);
        // Fetch all compliances as we don't have an endpoint for a single item
        const response = await api.getAuditCompliances(this.auditId);
        
        // Find the matching compliance in the response
        let found = false;
        response.data.policies.forEach(policy => {
          policy.subpolicies.forEach(subpolicy => {
            subpolicy.compliances.forEach(compliance => {
              if (compliance.compliance_id === complianceId) {
                console.log(`Found compliance ${complianceId} in response with status: ${compliance.status}, compliance_status: ${compliance.compliance_status}`);
                
                // Find this compliance in our local state
                this.policies.forEach(localPolicy => {
                  localPolicy.subpolicies.forEach(localSubpolicy => {
                    localSubpolicy.compliances.forEach(localCompliance => {
                      if (localCompliance.compliance_id === complianceId) {
                        console.log(`Updating local compliance ${complianceId} from: ${localCompliance.compliance_status} to: ${compliance.compliance_status}`);
                        // Update fields that might have changed
                        localCompliance.status = compliance.status;
                        localCompliance.compliance_status = compliance.compliance_status;
                        localCompliance.criticality = compliance.criticality;
                        
                        // Update original values
                        this.storeOriginalValue(localCompliance, 'status', compliance.status);
                        this.storeOriginalValue(localCompliance, 'compliance_status', compliance.compliance_status);
                        this.storeOriginalValue(localCompliance, 'criticality', compliance.criticality);
                        
                        found = true;
                      }
                    });
                  });
                });
              }
            });
          });
        });
        
        if (!found) {
          console.warn(`Could not find compliance ${complianceId} in the response`);
        }
      } catch (error) {
        console.error(`Error refreshing compliance ${complianceId}:`, error);
      }
    },
    isSavingField(complianceId, field) {
      const key = `${complianceId}_${field}`;
      return this.savingFields && this.savingFields[key] === true;
    },
    isRecentlySaved(complianceId, field) {
      const key = `${complianceId}_${field}`;
      return this.savedFields && this.savedFields[key] === true;
    },
    toggleSubpolicy(subpolicyId) {
      const isCurrentlyCollapsed = this.isSubpolicyCollapsed(subpolicyId);
      this.collapsedSubpolicies = { 
        ...this.collapsedSubpolicies, 
        [subpolicyId]: !isCurrentlyCollapsed 
      };
    },
    isSubpolicyCollapsed(subpolicyId) {
      return this.collapsedSubpolicies[subpolicyId] === true;
    },
    expandAllSubpolicies() {
      const updatedCollapsedState = {};
      this.policies.forEach(policy => {
        policy.subpolicies.forEach(subpolicy => {
          updatedCollapsedState[subpolicy.subpolicy_id] = false;
        });
      });
      this.collapsedSubpolicies = updatedCollapsedState;
    },
    collapseAllSubpolicies() {
      const updatedCollapsedState = {};
      this.policies.forEach(policy => {
        policy.subpolicies.forEach(subpolicy => {
          updatedCollapsedState[subpolicy.subpolicy_id] = true;
        });
      });
      this.collapsedSubpolicies = updatedCollapsedState;
    },
    calculateSubpolicyProgress(subpolicy) {
      if (!subpolicy.compliances || subpolicy.compliances.length === 0) return 0;
      
      const totalItems = subpolicy.compliances.length;
      const completedItems = subpolicy.compliances.filter(compliance => 
        compliance.compliance_status === 'Fully Compliant' || 
        compliance.compliance_status === 'Not Applicable'
      ).length;
      
      return Math.round((completedItems / totalItems) * 100);
    },
    getProgressClass(percentage) {
      if (percentage < 30) return 'progress-low';
      if (percentage < 70) return 'progress-medium';
      return 'progress-high';
    },
    isSubpolicyCompleted(subpolicy) {
      if (!subpolicy.compliances || subpolicy.compliances.length === 0) return false;
      
      // A subpolicy is completed if all compliances are either Fully Compliant or Not Applicable
      return subpolicy.compliances.every(compliance => 
        compliance.compliance_status === 'Fully Compliant' || 
        compliance.compliance_status === 'Not Applicable'
      );
    },
    openAddComplianceModal(policy, subpolicy) {
      this.showAddComplianceModal = true;
      this.selectedPolicy = policy;
      
      // Reset form
      this.resetComplianceForm();
      
      // Initialize framework and policy data
      this.selectedFrameworkName = this.frameworkName;
      
      // Since the button is under a specific policy, always freeze the policy
      this.isPolicyFrozen = true;
      this.selectedPolicyName = policy.policy_name;
      
      // Since the button is now under a specific subpolicy, freeze the subpolicy too
        this.isSubpolicyFrozen = true;
      this.selectedSubpolicyName = subpolicy.subpolicy_name;
            this.newCompliance.subpolicy_id = subpolicy.subpolicy_id;
      
      // Set the policy ID in the form data for API calls
      if (policy && policy.policy_id) {
        this.newCompliance.policy_id = policy.policy_id;
      }
      
      // Load available subpolicies for this policy (for reference, not needed for selection now)
      this.loadAvailablePoliciesAndSubpolicies();
    },
    
    closeAddComplianceModal() {
      this.showAddComplianceModal = false;
      this.selectedPolicy = null;
      this.resetComplianceForm();
    },
    
    resetComplianceForm() {
      this.newCompliance = {
        subpolicy_id: '',
        policy_id: '',
        description: '',
        is_risk: false,
        possible_damage: '',
        mitigation: '',
        criticality: 'Medium',
        mandatory_optional: 'Mandatory',
        impact: 'Medium',
        probability: 'Medium',
        // Set default values for removed fields
        manual_automatic: 'Manual',      // Default to 'Manual'
        permanent_temporary: 'Temporary', // Default to 'Temporary' 
        active_inactive: 'Active',       // Default to 'Active'
        ComplianceVersion: '0'           // Default to '0'
      };
      this.isSubmitting = false;
    },
    
    async loadAvailablePoliciesAndSubpolicies() {
      try {
        // Since policy is frozen to the selected policy, we only need to load subpolicies
        if (this.selectedPolicy) {
          console.log(`Loading subpolicies for selected policy: ${this.selectedPolicy.policy_name} (ID: ${this.selectedPolicy.policy_id})`);
          
          // If we have the policy object with subpolicies, use those
          if (this.selectedPolicy.subpolicies && this.selectedPolicy.subpolicies.length > 0) {
            this.availableSubpolicies = this.selectedPolicy.subpolicies.map(sp => ({
              SubPolicyId: sp.subpolicy_id,
              SubPolicyName: sp.subpolicy_name
            }));
            console.log(`Loaded ${this.availableSubpolicies.length} subpolicies from selected policy object`);
          } else {
            // Otherwise use the policy ID from the form
            await this.loadSubpoliciesForPolicy(this.selectedPolicy.policy_id);
          }
        } else if (this.newCompliance.policy_id) {
          // If somehow we don't have selectedPolicy but do have the ID in the form
          await this.loadSubpoliciesForPolicy(this.newCompliance.policy_id);
        } else {
          console.warn("No policy selected or policy ID available to load subpolicies");
        }
      } catch (error) {
        console.error('Error loading subpolicies:', error);
      }
    },
    
    async loadSubpoliciesForPolicy(policyId) {
      try {
        console.log(`Loading subpolicies for policy ID: ${policyId}`);
        
        // Try to find subpolicies from existing data first
        if (this.selectedPolicy && this.selectedPolicy.subpolicies) {
          this.availableSubpolicies = this.selectedPolicy.subpolicies.map(sp => ({
            SubPolicyId: sp.subpolicy_id,
            SubPolicyName: sp.subpolicy_name
          }));
          console.log(`Loaded ${this.availableSubpolicies.length} subpolicies from selected policy`);
        } else {
          // Otherwise, fetch subpolicies from API via get_assign_data which has all the data
          const response = await api.getAssignData();
          // Filter subpolicies that belong to the selected policy
          this.availableSubpolicies = response.data.subpolicies.filter(sp => 
            sp.PolicyId == policyId
          );
          console.log(`Loaded ${this.availableSubpolicies.length} subpolicies from API for policy ${policyId}`);
        }
      } catch (error) {
        console.error(`Error loading subpolicies for policy ${policyId}:`, error);
      }
    },
    
    handlePolicyChange() {
      // When policy changes, reset subpolicy and load new options
      this.newCompliance.subpolicy_id = '';
      
      console.log(`Policy changed to: ${this.newCompliance.policy_id}`);
      
      if (this.newCompliance.policy_id) {
        // Load the subpolicies for the selected policy
        this.loadSubpoliciesForPolicy(this.newCompliance.policy_id);
      } else {
        // Clear subpolicies if no policy is selected
        this.availableSubpolicies = [];
      }
    },
    
    async submitComplianceForm() {
      if (!this.newCompliance.description) {
        alert('Description is required');
        return;
      }
      
      // No need to check for subpolicy selection since it's now guaranteed by the button placement
      // and automatically set in openAddComplianceModal
      
      try {
        this.isSubmitting = true;
        
        const complianceData = { ...this.newCompliance };
        
        // Set the ComplianceVersion field correctly instead of using compliance_version
        // This should match the field name expected by the backend model
        complianceData.ComplianceVersion = '0';
        
        // Delete any incorrectly named version fields
        delete complianceData.compliance_version;
        
        // Ensure the frozen policy ID is used
        if (this.isPolicyFrozen && this.selectedPolicy) {
          complianceData.policy_id = this.selectedPolicy.policy_id;
        }
        
        // If subpolicy is frozen, ensure we get it from the context
        if (this.isSubpolicyFrozen && this.selectedPolicy) {
          const subpolicy = this.selectedPolicy.subpolicies.find(
            sp => sp.subpolicy_name === this.selectedSubpolicyName
          );
          if (subpolicy) {
            complianceData.subpolicy_id = subpolicy.subpolicy_id;
          }
        }
        
        console.log('Submitting compliance data:', complianceData);
        
        // Add compliance to the audit
        const response = await api.addComplianceToAudit(this.auditId, complianceData);
        
        // On success
        console.log('Compliance added successfully:', response.data);
        
        // Close modal and refresh compliance list
        this.closeAddComplianceModal();
        await this.fetchCompliances();
        
        // Show success message
        alert('Compliance added successfully');
        
      } catch (error) {
        console.error('Error adding compliance:', error);
        alert('Failed to add compliance: ' + (error.response?.data?.error || error.message));
      } finally {
        this.isSubmitting = false;
      }
    },
    getReviewStatusClass(status) {
      if (!status) return '';
      
      switch(status) {
        case 'Accept':
          return 'review-accept';
        case 'Reject':
          return 'review-reject';
        case 'In Review':
          return 'review-inprogress';
        default:
          return '';
      }
    }
  }
};
</script>

<style scoped>
.task-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  border-bottom: 2px solid #4f7cff;
  padding-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.framework-title {
  font-size: 28px;
  color: #333;
  margin: 0;
  font-weight: bold;
  text-align: center;
}

.loading {
  text-align: center;
  padding: 40px;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 20px;
  color: #dc3545;
}

.retry-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-btn:hover {
  background: #c82333;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.audit-content {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.policy-title {
  color: #333;
  border-bottom: 2px solid #4f7cff;
  padding-bottom: 10px;
  margin-bottom: 20px;
  font-size: 24px;
}

.policy-section {
  margin-bottom: 40px;
}

.subpolicy-section {
  margin: 20px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #4f7cff;
}

.subpolicy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.subpolicy-info {
  flex: 1;
}

.subpolicy-title {
  color: #555;
  margin-bottom: 15px;
  font-size: 18px;
}

.compliance-list {
  margin-left: 15px;
}

.compliance-item {
  margin: 20px 0;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: white;
  transition: all 0.3s ease;
}

.compliance-item:hover {
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}

.compliance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

.compliance-indicators {
  display: flex;
  gap: 10px;
  align-items: center;
}

.compliance-description {
  font-size: 16px;
  font-weight: bold;
  flex: 1;
}

.compliance-fields {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.field-group {
  position: relative;
  margin-bottom: 15px;
  width: 100%;
}

.field-indicator {
  position: absolute;
  bottom: 10px;
  right: 10px;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 5;
}

.field-saving {
  color: #004085;
  border: 1px solid #b8daff;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.field-saved {
  color: #155724;
  border: 1px solid #c3e6cb;
  opacity: 0.8;
  animation: fadeOut 3s forwards;
}

@keyframes fadeOut {
  0% { opacity: 1; }
  70% { opacity: 1; }
  100% { opacity: 0; }
}

.field-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
  color: #555;
}

.compliance-dropdown {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
}

.compliance-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-height: 100px;
  resize: vertical;
  transition: border-color 0.3s;
}

.compliance-textarea:focus {
  border-color: #4f7cff;
  box-shadow: 0 0 5px rgba(79, 124, 255, 0.3);
  outline: none;
}

.evidence-upload {
  margin-top: 20px;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.upload-container {
  display: flex;
  align-items: center;
  margin-top: 5px;
}

.file-input {
  width: 0.1px;
  height: 0.1px;
  opacity: 0;
  overflow: hidden;
  position: absolute;
  z-index: -1;
}

.upload-btn {
  background-color: #4f7cff;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  display: inline-block;
  font-size: 14px;
  transition: background 0.3s;
}

.upload-btn:hover {
  background-color: #3a63cc;
}

.file-name {
  margin-left: 10px;
  color: #666;
  font-style: italic;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 500;
}

.fully-compliant {
  background: #c3e6cb;
  color: #155724;
}

.partially-compliant {
  background: #b8daff;
  color: #004085;
}

.not-compliant {
  background: #f8d7da;
  color: #721c24;
}

.not-applicable {
  background: #e2e3e5;
  color: #383d41;
}

.not-assessed {
  background: #ffeeba;
  color: #856404;
}

.actions {
  display: none;
}

.submit-btn {
  padding: 12px 20px;
  background: #4f7cff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.submit-btn:hover {
  background: #3a63cc;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.submit-btn:disabled {
  background: #a0a0a0;
  cursor: not-allowed;
}

.changes-count {
  display: inline-block;
  margin-left: 5px;
  font-size: 14px;
}

.save-status {
  font-size: 16px;
  padding: 5px 10px;
  border-radius: 4px;
  font-weight: bold;
}

.save-icon {
  margin-right: 6px;
  display: inline-block;
}

.save-progress .save-icon {
  animation: spin 1s linear infinite;
}

.save-success {
  color: #155724;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  padding: 8px 15px;
  border-radius: 4px;
}

.save-progress {
  color: #004085;
  background-color: #cce5ff;
  border: 1px solid #b8daff;
  padding: 8px 15px;
  border-radius: 4px;
}

.save-error {
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 8px 15px;
  border-radius: 4px;
}

.criticality-container {
  display: flex;
  width: 100%;
}

/* Ensure dropdown takes full width */
.criticality-container select {
  width: 100%;
}

.criticality-badge {
  display: inline-block;
  min-width: 60px;
  text-align: center;
  font-size: 0.8em;
  padding: 4px 8px;
  border-radius: 20px;
}

.criticality-major {
  background-color: #f8d7da;
  color: #721c24;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  font-weight: bold;
}

.criticality-minor {
  background-color: #d1ecf1;
  color: #0c5460;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  font-weight: bold;
}

.criticality-na {
  background-color: #e2e3e5;
  color: #383d41;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  font-weight: normal;
}

.text-fields {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.subpolicy-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-btn {
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  padding: 5px 12px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn:hover {
  background-color: #e3e3e3;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.collapse-controls {
  display: flex;
  gap: 10px;
}

.control-btn {
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  padding: 5px 12px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.control-btn:hover {
  background-color: #e3e3e3;
}

.expand-all {
  color: #28a745;
}

.collapse-all {
  color: #dc3545;
}

.toggle-icon {
  display: inline-block;
  margin-right: 5px;
  font-size: 10px;
}

.compliance-count {
  font-size: 14px;
  color: #666;
  font-weight: normal;
  margin-left: 8px;
}

.subpolicy-progress {
  display: flex;
  align-items: center;
  margin-top: 5px;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  max-width: 300px;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-low {
  background-color: #dc3545;
}

.progress-medium {
  background-color: #ffc107;
}

.progress-high {
  background-color: #28a745;
}

.progress-text {
  font-size: 12px;
  color: #6c757d;
  min-width: 80px;
}

.subpolicy-completed {
  border-left-color: #28a745;
}

.subpolicy-completed .subpolicy-title {
  color: #28a745;
}

.subpolicy-completed .subpolicy-title::after {
  content: "✓";
  margin-left: 8px;
  color: #28a745;
}

.policy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.add-compliance-btn {
  background-color: #4f7cff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  font-weight: 500;
  margin-left: 8px;
}

.add-compliance-btn:hover {
  background-color: #3664e6;
}

.add-icon {
  font-weight: bold;
  font-size: 14px;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

/* Form styles */
.form-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.form-section h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #4f7cff;
  font-size: 16px;
}

.form-group {
  margin-bottom: 15px;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-group.half {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #555;
}

.form-group.required label::after {
  content: " *";
  color: #dc3545;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
}

.form-control.disabled {
  background-color: #f8f9fa;
  color: #666;
}

textarea.form-control {
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn {
  padding: 10px 20px;
  background-color: #f8f9fa;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn {
  padding: 10px 20px;
  background-color: #4f7cff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn:disabled {
  background-color: #b3c5ff;
  cursor: not-allowed;
}

/* Media query for smaller screens */
@media (max-width: 768px) {
  .subpolicy-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .add-compliance-btn {
    margin-left: 0;
    font-size: 12px;
    padding: 4px 8px;
  }
  
  .toggle-btn {
    font-size: 12px;
    padding: 4px 8px;
  }
}

/* Floating save button styles */
.floating-save {
  position: fixed;
  right: 20px;
  bottom: 80px;
  z-index: 100;
}

/* Add new styles for the review status badge */
.review-status-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.8em;
  font-weight: bold;
  margin-right: 5px;
}

.review-accept {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.review-reject {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.review-inprogress {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeeba;
}
</style> 