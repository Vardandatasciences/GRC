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

    <!-- Review panel with Accept/Reject options -->
    <div class="floating-review-panel">
      <div class="review-header">
        <h3>Overall Review Controls</h3>
      </div>
      <div class="review-body">
        <div class="review-comments">
          <label>Overall Review Comments:</label>
          <textarea 
            v-model="reviewComments" 
            class="review-comments-textarea"
            placeholder="Add your overall review comments here..."
          ></textarea>
        </div>
        <div class="review-note">
          <p>Note: You can also review each compliance item individually below.</p>
        </div>
        <div class="review-actions">
          <button @click="saveReviewProgress" class="review-save-btn" :disabled="savingProgress">
            {{ savingProgress ? 'Saving...' : 'Save Progress' }}
          </button>
          <button @click="submitReview" class="review-submit-btn" :disabled="submittingReview">
            {{ submittingReview ? 'Submitting...' : 'Submit Review' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Loading compliances...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="fetchCompliances" class="retry-btn">Retry</button>
    </div>
    <div v-else-if="!versionData && !policies.length" class="no-data-message">
      <div class="no-data-icon">📋</div>
      <h3>No Audit Data Available</h3>
      <p>There is no audit data available for review. This might happen if the auditor hasn't submitted any findings yet.</p>
      <button @click="goBackToDashboard" class="btn-back">Return to Dashboard</button>
    </div>
    <div v-else>
      <div class="audit-content">
        <div class="page-header">
          <div class="back-nav">
            <button @click="goBackToDashboard" class="back-button">
              ← Back to Review Dashboard
            </button>
          </div>
          <h1 class="framework-title">
            {{ frameworkName }}
            <span class="review-mode-indicator">(Review Mode)</span>
            <span v-if="versionData" class="version-indicator">
              Version: {{ versionData.version_info?.Version || 'A1' }} | 
              {{ versionData.version_info?.VersionType || 'Auditor' }} | 
              Snapshot from: {{ formatDate(versionData.version_info?.Date) }}
            </span>
          </h1>
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
        
        <!-- Warning notification for fallback version -->
        <div v-if="usingFallbackVersion && versionWarning" class="version-warning">
          <div class="warning-icon">⚠️</div>
          <div class="warning-message">{{ versionWarning }}</div>
        </div>
        
        <!-- Version info alert box -->
        <div v-if="versionData" class="version-alert" 
          :class="{
            'reviewer-version': versionData.version_info?.Version?.startsWith('R'), 
            'auditor-version': versionData.version_info?.Version?.startsWith('A'),
            'rejected-version': versionData.version_info?.ApprovedRejected === 'Rejected',
            'fallback-version': usingFallbackVersion
          }">
          <h3 class="version-title">
            <span v-if="versionData.version_info?.Version?.startsWith('R')">
              Review Version ({{ versionData.version_info?.Version }})
            </span>
            <span v-else>
              Auditor Submission ({{ versionData.version_info?.Version }})
            </span>
          </h3>
          <p>
            <strong>📸 You are reviewing a snapshot of this audit</strong> - 
            <span v-if="versionData.version_info?.Version?.startsWith('R')">
              This is a reviewer version containing previous review data.
              <span v-if="versionData.version_info?.metadata?.review_date">
                Last review was performed on {{ formatDate(versionData.version_info?.metadata?.review_date) }}.
              </span>
            </span>
            <span v-else>
              <strong>This is the latest submission from the auditor for your review.</strong>
              This data was captured when the auditor submitted the findings for review.
            </span>
          </p>
          <p>
            <span v-if="versionData.version_info?.UserId && versionData.version_info?.VersionType === 'Auditor'">
              <strong>Submitted by:</strong> {{ versionData.version_info?.Auditor || 'Auditor' }} on {{ formatDate(versionData.version_info?.Date) }}
            </span>
            <span v-else-if="versionData.version_info?.metadata?.reviewer_id">
              <strong>Reviewed by:</strong> Reviewer on {{ formatDate(versionData.version_info?.metadata?.review_date) }}
            </span>
          </p>
          <div v-if="versionData.version_info?.ApprovedRejected" class="version-status">
            <strong>Status:</strong> 
            <span :class="getApprovalStatusClass(versionData.version_info?.ApprovedRejected)">
              {{ versionData.version_info?.ApprovedRejected }}
            </span>
          </div>
          
          <!-- Show overall review status if available in metadata -->
          <div v-if="versionData.version_info?.metadata?.overall_status" class="version-status">
            <strong>Overall Review Status:</strong> 
            <span :class="{'status-accept': versionData.version_info.metadata.overall_status === 'Accept', 
                           'status-reject': versionData.version_info.metadata.overall_status === 'Reject',
                           'status-review': versionData.version_info.metadata.overall_status === 'In Review'}">
              {{ versionData.version_info.metadata.overall_status }}
            </span>
          </div>
          
          <!-- Show rejection hint for rejected versions -->
          <div v-if="versionData.version_info?.ApprovedRejected === 'Rejected'" class="rejection-hint">
            <strong>Note:</strong> Rejected items are highlighted in red. Please review and fix these items.
          </div>
          
          <!-- Color legend -->
          <div class="color-legend">
            <div class="legend-item">
              <div class="color-box accepted"></div>
              <span>Accepted items</span>
            </div>
            <div class="legend-item">
              <div class="color-box rejected"></div>
              <span>Rejected items</span>
            </div>
            <div class="legend-item">
              <div class="color-box in-review"></div>
              <span>In review</span>
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
              </div>
            </div>
            
            <div class="compliance-list" v-show="!isSubpolicyCollapsed(subpolicy.subpolicy_id)">
              <div v-for="compliance in subpolicy.compliances" :key="compliance.compliance_id" class="compliance-item" :class="{'rejected': compliance.review_status === 'Reject', 'accepted': compliance.review_status === 'Accept'}">
                <div class="compliance-header">
                  <span class="compliance-description">{{ compliance.description }}</span>
                  <div class="compliance-indicators">
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
                      disabled
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
                        disabled
                      >
                        <option value="Major">Major</option>
                        <option value="Minor">Minor</option>
                        <option value="Not Applicable">Not Applicable</option>
                      </select>
                    </div>
                  </div>
                </div>
                
                <!-- Add compliance-level review controls -->
                <div class="compliance-review-panel">
                  <h4 class="review-panel-title">Review Controls</h4>
                  <div class="compliance-review-content">
                    <div class="review-field-group">
                      <label>Review Status:</label>
                      <select 
                        v-model="compliance.review_status" 
                        class="review-status-dropdown"
                        @change="updateComplianceReviewField(compliance, 'review_status', compliance.review_status)"
                      >
                        <option value="In Review">In Review</option>
                        <option value="Accept">Accept</option>
                        <option value="Reject">Reject</option>
                      </select>
                    </div>
                    
                    <div class="review-field-group">
                      <label>Review Comments:</label>
                      <textarea 
                        v-model="compliance.review_comments" 
                        class="review-comments-field"
                        placeholder="Add your review comments here..."
                        @input="updateComplianceReviewField(compliance, 'review_comments', compliance.review_comments)"
                      ></textarea>
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
                      disabled
                    ></textarea>
                  </div>
                  
                  <div class="field-group">
                    <label>Impact:</label>
                    <textarea 
                      v-model="compliance.impact" 
                      class="compliance-textarea"
                      placeholder="Describe the impact..."
                      disabled
                    ></textarea>
                  </div>
                  
                  <div class="field-group">
                    <label>Details of Findings:</label>
                    <textarea 
                      v-model="compliance.details_of_finding" 
                      class="compliance-textarea"
                      placeholder="Enter detailed findings..."
                      disabled
                    ></textarea>
                  </div>
                  
                  <div class="field-group">
                    <label>Recommendation:</label>
                    <textarea 
                      v-model="compliance.recommendation" 
                      class="compliance-textarea"
                      placeholder="Provide recommendations..."
                      disabled
                    ></textarea>
                  </div>
                  
                  <div class="field-group">
                    <label>Comments:</label>
                    <textarea 
                      v-model="compliance.comments" 
                      class="compliance-textarea"
                      placeholder="Add comments..."
                      disabled
                    ></textarea>
                  </div>
                </div>
                
                <div class="evidence-upload">
                  <label>Evidence:</label>
                  <div class="upload-container">
                    <span class="file-name">{{ compliance.file_name || 'No file uploaded' }}</span>
                    <button v-if="compliance.file_name" class="view-evidence-btn">View Evidence</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Overall review section at the bottom -->
        <div class="bottom-review-section">
          <h2 class="bottom-review-title">Overall Review Comments</h2>
          <div class="bottom-review-content">
            <div class="bottom-review-field">
              <label>Overall Review Comments:</label>
              <textarea 
                v-model="reviewComments" 
                class="bottom-review-comments"
                placeholder="Add your overall review comments here..."
              ></textarea>
            </div>
            
            <div class="bottom-review-actions">
              <button @click="saveReviewProgress" class="bottom-review-save" :disabled="savingProgress">
                {{ savingProgress ? 'Saving...' : 'Save Progress' }}
              </button>
              <button @click="submitReview" class="bottom-review-submit" :disabled="submittingReview">
                {{ submittingReview ? 'Submitting...' : 'Submit Review' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../../data/api';

export default {
  name: 'ReviewTaskView',
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
      
      // Review specific data
      reviewComments: '',
      submittingReview: false,
      savingProgress: false,
      
      changedFields: {}, // Track which fields have been modified
      versionData: null,
      usingFallbackVersion: false,
      versionWarning: null,
    };
  },
  async created() {
    try {
      this.loading = true;
    await this.fetchAuditDetails();
      
    // Load the latest auditor version (A-prefix) for review
      const versionLoaded = await this.loadLatestAuditorVersion();
      
      if (!versionLoaded || !this.versionData) {
        console.log('No version data loaded, fetching live compliance data');
      // Only fetch live compliance data if no version data is available
      await this.fetchCompliances();
    }
      
    await this.fetchReviewData();
    } catch (error) {
      console.error('Error initializing review task view:', error);
      this.error = 'Failed to load audit data. Please try again or contact support.';
    } finally {
      this.loading = false;
    }
  },
  methods: {
    async loadLatestAuditorVersion() {
      try {
        console.log('Loading latest auditor version data for audit ID:', this.auditId);
        
        // First check if versions exist for this audit
        const versionCheckResponse = await api.checkAuditVersion(this.auditId);
        console.log('Version check response:', versionCheckResponse.data);
        
        // Look specifically for auditor versions (A-prefix)
        if (versionCheckResponse.data.auditor_versions_found > 0) {
          // Sort auditor versions by version number to ensure we get the latest one
          const auditorVersions = versionCheckResponse.data.auditor_versions.sort((a, b) => {
            // Extract numeric part from version strings (e.g., A2 -> 2)
            const numA = parseInt(a.Version.substring(1));
            const numB = parseInt(b.Version.substring(1));
            // Sort in descending order (newest first)
            return numB - numA;
          });
          
          const latestAuditorVersion = auditorVersions[0].Version;
          console.log(`Found latest auditor version: ${latestAuditorVersion}`);
          
          try {
          // Get the details for this version
          const versionDetails = await api.getAuditVersionDetails(this.auditId, latestAuditorVersion);
          this.versionData = versionDetails.data;
          console.log('Loaded auditor version data successfully');
          console.log('Version info:', this.versionData.version_info);
          console.log(`Found ${this.versionData.findings ? this.versionData.findings.length : 0} findings in auditor version`);
          
          // Process and transform the version data to match our expected format
          await this.processVersionData();
          return true;
          } catch (versionError) {
            console.error(`Error loading version ${latestAuditorVersion}:`, versionError);
            
            // If there was an error with the first version, try the next one
            if (auditorVersions.length > 1) {
              console.log(`Trying fallback to previous auditor version: ${auditorVersions[1].Version}`);
              try {
                const fallbackVersionDetails = await api.getAuditVersionDetails(this.auditId, auditorVersions[1].Version);
                this.versionData = fallbackVersionDetails.data;
                console.log('Loaded fallback auditor version successfully');
                
                // Set flags to indicate we're using a fallback version
                this.usingFallbackVersion = true;
                this.versionWarning = `Note: Using an older version (${auditorVersions[1].Version}) because the latest version had errors.`;
                
                await this.processVersionData();
                return true;
              } catch (fallbackError) {
                console.error('Error loading fallback version:', fallbackError);
              }
            }
            
            // If we get here, both attempts failed
            throw new Error('Failed to load any auditor version');
          }
        } else {
          console.log('No auditor versions found for this audit. Will try to load any available version.');
          
          // Fallback to the loadLatestVersionData method which will get any version
          return await this.loadLatestVersionData();
        }
      } catch (error) {
        console.error('Error loading latest auditor version:', error);
        // Fallback to the loadLatestVersionData method
        return await this.loadLatestVersionData();
      }
    },
    
    async loadLatestVersionData() {
      try {
        console.log('Loading latest version data for audit ID:', this.auditId);
        // Use the new endpoint to get the latest version regardless of prefix
        const response = await api.loadLatestReviewVersion(this.auditId);
        
        if (response.data && response.data.review_data) {
          console.log(`Loaded latest version: ${response.data.version} with timestamp ${response.data.timestamp}`);
          
          // Create a compatible version data structure
          this.versionData = {
            version_info: {
              Version: response.data.version,
              Date: response.data.timestamp,
              VersionType: response.data.version.startsWith('R') ? 'Reviewer' : 'Auditor',
              // Copy metadata if available
              metadata: response.data.review_data.__metadata__ || {}
            },
            findings: []
          };
          
          // Process the JSON data into the expected format for our component
          const jsonData = response.data.review_data;
          
          // Extract findings from the JSON data
          for (const [key, value] of Object.entries(jsonData)) {
            // Skip metadata and overall_comments keys
            if (key === '__metadata__' || key === 'overall_comments') {
              continue;
            }
            
            if (typeof value === 'object') {
              // Add compliance ID to the finding data
              const finding = {
                ...value,
                compliance_id: key
              };
              this.versionData.findings.push(finding);
            }
          }
          
          // Extract overall comments if available
          if (jsonData.overall_comments) {
            this.reviewComments = jsonData.overall_comments;
          }
          
          // Process the version data into the format expected by the component
          await this.processVersionData();
          return true;
        }
        
        return false;
      } catch (error) {
        console.error('Error loading latest version data:', error);
        this.versionData = null;
        return false;
      }
    },
    
    async fetchVersionData() {
      try {
        console.log('Checking for version data for audit ID:', this.auditId);
        // First check if versions exist for this audit
        const versionCheckResponse = await api.checkAuditVersion(this.auditId);
        console.log('Version check response:', versionCheckResponse.data);
        
        // Get the audit status to determine workflow state
        const statusResponse = await api.getAuditStatus(this.auditId);
        const auditStatus = statusResponse.data.status;
        console.log('Current audit status:', auditStatus);
        
        // If the audit was rejected and is now back in "Work In Progress", 
        // we should show the rejected version to help the auditor fix issues
        let useRejectedVersion = false;
        let rejectedVersion = null;
        
        if (auditStatus === 'Work In Progress' && versionCheckResponse.data.reviewer_versions_found > 0) {
          // Look for the most recent rejected reviewer version
          for (const version of versionCheckResponse.data.reviewer_versions) {
            if (version.ApprovedRejected === 'Rejected') {
              rejectedVersion = version.Version;
              useRejectedVersion = true;
              console.log(`Found rejected version ${rejectedVersion}, will load it to show rejected items`);
              break;
            }
          }
        }
        
        // Determine which version to load
        let versionToUse = null;
        
        if (useRejectedVersion && rejectedVersion) {
          // Use the rejected version to show what was rejected
          versionToUse = rejectedVersion;
          console.log(`Loading rejected version: ${versionToUse}`);
        } else if (versionCheckResponse.data.recommended_version) {
          // Use the recommended version from the API
          versionToUse = versionCheckResponse.data.recommended_version;
          console.log(`Loading recommended version: ${versionToUse}`);
        } else if (versionCheckResponse.data.auditor_versions_found > 0) {
          // Fallback to the first auditor version
          versionToUse = versionCheckResponse.data.auditor_versions[0].Version;
          console.log(`No recommended version, falling back to auditor version: ${versionToUse}`);
        }
        
        if (versionToUse) {
          // Get the details for this version
          const versionDetails = await api.getAuditVersionDetails(this.auditId, versionToUse);
          this.versionData = versionDetails.data;
          console.log('Loaded version data:', this.versionData);
          
          // Process and transform the version data to match our expected format
          await this.processVersionData();
          return true;
        } else {
          console.log('No version data found for this audit.');
          this.versionData = null;
          return false;
        }
      } catch (error) {
        console.error('Error fetching version data:', error);
        this.versionData = null;
        return false;
      }
    },
    
    async processVersionData() {
      try {
        if (!this.versionData || !this.versionData.findings) {
          console.error('No version findings data to process');
          return;
        }
        
        console.log('Processing version data');
        const isReviewerVersion = this.versionData.version_info?.Version?.startsWith('R') || false;
        console.log(`This is a ${isReviewerVersion ? 'reviewer' : 'auditor'} version`);
        
        // Debug full version data structure
        console.log('Full version data structure:', JSON.stringify(this.versionData));
        
        // Group findings by policy and subpolicy
        const policyMap = new Map();
        
        // First organize findings by policy and subpolicy
        this.versionData.findings.forEach(finding => {
          // Debug each finding
          console.log(`Processing finding for compliance ID ${finding.compliance_id}:`, finding);
          
          const policyName = finding.policy_name;
          const subpolicyName = finding.subpolicy_name;
          const complianceId = finding.compliance_id;
          
          if (!policyName || !subpolicyName) {
            console.warn(`Missing policy or subpolicy name for compliance ${complianceId}`, finding);
            return; // Skip this finding
          }
          
          // Add policy if not exists
          if (!policyMap.has(policyName)) {
            policyMap.set(policyName, {
              policy_name: policyName,
              subpolicies: new Map()
            });
          }
          
          const policy = policyMap.get(policyName);
          
          // Add subpolicy if not exists
          if (!policy.subpolicies.has(subpolicyName)) {
            policy.subpolicies.set(subpolicyName, {
              subpolicy_name: subpolicyName,
              compliances: []
            });
          }
          
          // Normalize finding fields - ensure consistent field names between R and A versions
          this.normalizeVersionFields(finding, isReviewerVersion);
          
          // Process compliance data from finding
          // First get all possible field names from the finding
          const compliance = {
            compliance_id: complianceId,
            description: finding.description || finding.ComplianceItemDescription || '',
            // For status, check all possible field names
            compliance_status: finding.compliance_status || 
                               this.mapCheckStatusToComplianceStatus(finding.Check) || 
                               this.mapCheckStatusToComplianceStatus(finding.status) || 
                               'Not Compliant',
            criticality: finding.criticality || 
                         this.mapMajorMinorToCriticality(finding.MajorMinor) || 
                         this.mapMajorMinorToCriticality(finding.majorminor) ||
                         'Minor',
            // Check all possible field names for each field
            how_to_verify: finding.how_to_verify || finding.HowToVerify || '',
            impact: finding.impact || finding.Impact || '',
            details_of_finding: finding.details_of_finding || finding.DetailsOfFinding || '',
            recommendation: finding.recommendation || finding.Recommendation || '',
            comments: finding.comments || finding.Comments || '',
            evidence: finding.evidence || finding.Evidence || '',
            
            // Review fields are now normalized through normalizeVersionFields function
            review_status: finding.review_status || 'In Review',
            review_comments: finding.review_comments || '',
            accept_reject: finding.accept_reject || '0',
            
            // Store original status code
            status: finding.Check || finding.status || '0',
            
            // Set evidence file name if available
            file_name: finding.Evidence || finding.evidence_filename || ''
          };
          
          console.log(`Processed compliance ${complianceId}:`, compliance);
          
          policy.subpolicies.get(subpolicyName).compliances.push(compliance);
        });
        
        // Extract metadata if available
        if (this.versionData.version_info?.metadata) {
          const metadata = this.versionData.version_info.metadata;
          console.log('Found metadata in version_info:', metadata);
          if (metadata.overall_comments) {
            this.reviewComments = metadata.overall_comments;
            console.log('Loaded overall review comments from version metadata:', this.reviewComments);
          }
        } else if (this.versionData.overall_comments) {
          // Try to get overall comments from root level (backward compatibility)
          this.reviewComments = this.versionData.overall_comments;
          console.log('Loaded overall review comments from root level:', this.reviewComments);
        }
        
        // Convert to expected format for our component
        const processedPolicies = [];
        let policyId = 1; // Generate IDs
        
        policyMap.forEach((policy, policyName) => {
          const processedPolicy = {
            policy_id: policyId++,
            policy_name: policyName,
            subpolicies: []
          };
          
          let subpolicyId = 1;
          policy.subpolicies.forEach((subpolicy, subpolicyName) => {
            const processedSubpolicy = {
              subpolicy_id: subpolicyId++,
              subpolicy_name: subpolicyName,
              compliances: subpolicy.compliances
            };
            
            processedPolicy.subpolicies.push(processedSubpolicy);
          });
          
          processedPolicies.push(processedPolicy);
        });
        
        // Set the processed data as our policies
        this.policies = processedPolicies;
        console.log('Processed version data into policies:', this.policies);
        
        // Verify that each compliance has the expected fields
        this.policies.forEach(policy => {
          policy.subpolicies.forEach(subpolicy => {
            subpolicy.compliances.forEach(compliance => {
              // Check for missing required fields
              const requiredFields = ['compliance_id', 'description', 'compliance_status', 'criticality', 'review_status', 'review_comments', 'accept_reject'];
              const missingFields = requiredFields.filter(field => !compliance[field]);
              
              if (missingFields.length > 0) {
                console.warn(`Compliance ${compliance.compliance_id} is missing required fields:`, missingFields);
              }
            });
          });
        });
        
        // Mark loading as complete
        this.loading = false;
      } catch (error) {
        console.error('Error processing version data:', error);
        this.error = 'Failed to process version data. Please try again.';
        this.loading = false;
      }
    },
    
    // New helper method to normalize field names between R and A versions
    normalizeVersionFields(finding, isReviewerVersion) {
      // Ensure review_status is present and consistent
      if (!finding.review_status) {
        // If accept_reject is available, map it to review_status
        if (finding.accept_reject !== undefined) {
          finding.review_status = this.mapAcceptRejectToReviewStatus(finding.accept_reject);
        } else {
          // Default review_status
          finding.review_status = 'In Review';
        }
      }
      
      // Ensure accept_reject is present and consistent (needed for serialization)
      if (!finding.accept_reject) {
        // Map from review_status to accept_reject if available
        if (finding.review_status) {
          switch(finding.review_status) {
            case 'Accept': finding.accept_reject = '1'; break;
            case 'Reject': finding.accept_reject = '2'; break;
            default: finding.accept_reject = '0'; break;
          }
        } else {
          // Default accept_reject
          finding.accept_reject = '0';
        }
      }
      
      // Ensure review_comments is present
      if (!finding.review_comments) {
        finding.review_comments = finding.reviewer_comments || '';
      }
      
      // If it's auditor version (A), ensure it has all reviewer fields 
      if (!isReviewerVersion) {
        // Make sure A versions have the same fields as R versions
        finding.reviewer_comments = finding.review_comments;
      }
      
      // Log the normalized fields
      console.log(`Normalized finding fields for compliance ${finding.compliance_id}:`, {
        review_status: finding.review_status,
        accept_reject: finding.accept_reject,
        review_comments: finding.review_comments
      });
      
      return finding;
    },
    
    // Add a helper method to map accept_reject codes to review_status strings
    mapAcceptRejectToReviewStatus(acceptReject) {
      if (acceptReject === undefined || acceptReject === null) {
        return 'In Review';
      }
      
      // Handle both string and numeric values
      if (typeof acceptReject === 'string') {
        switch(acceptReject.toLowerCase()) {
          case '0': return 'In Review';
          case '1': return 'Accept';
          case '2': return 'Reject';
          case 'in review': return 'In Review';
          case 'accept': return 'Accept';
          case 'reject': return 'Reject';
          default: return 'In Review';
        }
      } else if (typeof acceptReject === 'number') {
        switch(acceptReject) {
          case 0: return 'In Review';
          case 1: return 'Accept';
          case 2: return 'Reject';
          default: return 'In Review';
        }
      }
      
      return 'In Review';
    },
    
    // Utility methods for mapping version data fields
    mapCheckStatusToComplianceStatus(check) {
      if (check === undefined || check === null) {
        return 'Not Compliant';
      }
      
      // Convert to string for comparison
      const checkStr = String(check);
      
      switch(checkStr) {
        case '0': return 'Not Compliant';
        case '1': return 'Partially Compliant';
        case '2': return 'Fully Compliant';
        case '3': return 'Not Applicable';
        case 'Not Compliant': return 'Not Compliant';
        case 'Partially Compliant': return 'Partially Compliant';
        case 'Fully Compliant': return 'Fully Compliant';
        case 'Not Applicable': return 'Not Applicable';
        default: return 'Not Compliant';
      }
    },
    
    mapMajorMinorToCriticality(majorMinor) {
      if (majorMinor === undefined || majorMinor === null) {
        return 'Minor';
      }
      
      // Convert to string for comparison
      const majorMinorStr = String(majorMinor);
      
      switch(majorMinorStr) {
        case '0': return 'Minor';
        case '1': return 'Major';
        case '2': return 'Not Applicable';
        case 'Minor': return 'Minor';
        case 'Major': return 'Major';
        case 'Not Applicable': return 'Not Applicable';
        default: return 'Minor';
      }
    },
    
    async fetchReviewData() {
      try {
        // Fetch existing review data if available
        const response = await api.getAuditDetails(this.auditId);
        if (response.data.review_comments) {
          this.reviewComments = response.data.review_comments;
        }
        console.log('Loaded review data:', { comments: this.reviewComments });
      } catch (error) {
        console.error('Error fetching review data:', error);
      }
    },
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
    async fetchCompliances() {
      try {
        this.loading = true;
        this.error = null;
        console.log('Fetching compliances for audit ID:', this.auditId);
        const response = await api.getAuditCompliances(this.auditId);
        console.log('Compliance data:', response.data);
        
        // Check if we have data
        if (!response.data || !response.data.policies) {
          console.error('Invalid compliance data received from API:', response.data);
          throw new Error('Invalid data structure received from server');
        }
        
        // Log the raw data for debugging
        console.log('Raw compliance data:', JSON.stringify(response.data));
        
        // Process the data to include additional fields if not present
        const policies = response.data.policies;
        
        // First validate the data structure
        if (!Array.isArray(policies)) {
          console.error('Policies is not an array:', policies);
          throw new Error('Invalid policies data structure');
        }
        
        policies.forEach(policy => {
          if (!policy.subpolicies || !Array.isArray(policy.subpolicies)) {
            console.error('Invalid subpolicies structure for policy:', policy);
            policy.subpolicies = []; // Initialize to prevent errors
            return;
          }
          
          policy.subpolicies.forEach(subpolicy => {
            if (!subpolicy.compliances || !Array.isArray(subpolicy.compliances)) {
              console.error('Invalid compliances structure for subpolicy:', subpolicy);
              subpolicy.compliances = []; // Initialize to prevent errors
              return;
            }
            
            subpolicy.compliances.forEach(compliance => {
              // Debug log for each compliance
              console.log(`Processing compliance ${compliance.compliance_id}:`, compliance);
              
              // Ensure compliance_id exists and is a string
              if (!compliance.compliance_id) {
                console.error('Missing compliance_id for compliance:', compliance);
                return; // Skip this compliance
              }
              
              compliance.compliance_id = String(compliance.compliance_id);
              
              // Debug log for criticality and status values
              console.log(`Original criticality value for compliance ${compliance.compliance_id}: ${compliance.criticality} (type: ${typeof compliance.criticality})`);
              console.log(`Original compliance status: ${compliance.compliance_status}, status code: ${compliance.status}`);
              
              // Use the compliance_status from backend if available
              if (!compliance.compliance_status) {
                // Only do the mapping if compliance_status is not already set by backend
                compliance.compliance_status = this.mapCheckStatusToComplianceStatus(compliance.status);
                console.log(`Mapped compliance status from ${compliance.status} to ${compliance.compliance_status}`);
              }
              
              // Convert criticality values using our mapping function
              compliance.criticality = this.mapMajorMinorToCriticality(compliance.criticality);
              console.log(`Final criticality value: ${compliance.criticality}`);
              
              // Ensure all fields are initialized
              compliance.description = compliance.description || compliance.ComplianceItemDescription || 'No description';
              compliance.how_to_verify = compliance.how_to_verify || '';
              compliance.impact = compliance.impact || '';
              compliance.details_of_finding = compliance.details_of_finding || '';
              compliance.recommendation = compliance.recommendation || '';
              compliance.comments = compliance.comments || '';
              compliance.file_name = compliance.file_name || '';
              
              // Initialize review fields
              compliance.review_status = compliance.review_status || 'In Review';
              compliance.review_comments = compliance.review_comments || compliance.reviewer_comments || '';
              
              // Double-check required fields
              const missingFields = [];
              ['compliance_id', 'description', 'compliance_status', 'criticality'].forEach(field => {
                if (!compliance[field]) {
                  missingFields.push(field);
                }
              });
              
              if (missingFields.length > 0) {
                console.warn(`Compliance ${compliance.compliance_id} is missing required fields:`, missingFields);
              }
            });
          });
        });
        
        this.policies = policies;
        console.log('Processed compliance data into policies structure:', this.policies);
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
    submitChangedFields() {
      alert('Review mode is read-only. Use the review panel to submit your review.');
    },
    async submitReview() {
      if (!this.auditId) return;
      
      this.submittingReview = true;
      
      try {
        // Collect all compliance review data
        const complianceReviews = [];
        let hasRejected = false;
        let allAccepted = true;
        
        this.policies.forEach(policy => {
          policy.subpolicies.forEach(subpolicy => {
            subpolicy.compliances.forEach(compliance => {
              complianceReviews.push({
                compliance_id: compliance.compliance_id,
                review_status: compliance.review_status,
                review_comments: compliance.review_comments
              });
              
              // Track rejection and acceptance for determining overall status
              if (compliance.review_status === 'Reject') {
                hasRejected = true;
                allAccepted = false;
              } else if (compliance.review_status !== 'Accept') {
                allAccepted = false;
              }
            });
          });
        });
        
        // Determine overall status based on compliance statuses
        let determinedStatus = 'In Review'; // Default
        if (hasRejected) {
          determinedStatus = 'Reject';
        } else if (allAccepted) {
          determinedStatus = 'Accept';
        }
        
        // Display a confirmation with the determined status
        const approvedRejected = hasRejected ? 'Rejected' : (allAccepted ? 'Approved' : 'In Review');
        const auditStatus = hasRejected ? 'Work In Progress' : (allAccepted ? 'Completed' : 'Under review');
        const confirmMessage = `You are about to submit the review with status: ${determinedStatus}\n\nThe audit will be marked as: ${approvedRejected}\n\nAudit status will be changed to: ${auditStatus}\n\nDo you want to continue?`;
        
        if (!confirm(confirmMessage)) {
          this.submittingReview = false;
          return;
        }
        
        console.log(`Submitting review for audit ${this.auditId} with determined status ${determinedStatus}`);
        
        // Add version information if available
        const versionInfo = this.versionData?.version_info || null;
        let versionId = null;
        if (versionInfo) {
          versionId = versionInfo.Version;
          console.log(`Including version information: ${versionId}`);
        }
        
        const response = await api.updateAuditReviewStatus(this.auditId, {
          review_status: determinedStatus,
          review_comments: this.reviewComments,
          compliance_reviews: complianceReviews,
          version_id: versionId // Include version ID if available
        });
        
        console.log('Review submitted successfully:', response.data);
        
        // Show success message with audit status
        const updatedAuditStatus = response.data.audit_status || (hasRejected ? 'Work In Progress' : (allAccepted ? 'Completed' : 'Under review'));
        alert(`Review submitted successfully!\nAudit status updated to: ${updatedAuditStatus}`);
        
        // Navigate back to the reviewer dashboard
        this.$router.push('/auditor/reviews');
        
      } catch (error) {
        console.error('Error submitting review:', error);
        alert(error.response?.data?.error || 'Failed to submit review. Please try again.');
      } finally {
        this.submittingReview = false;
      }
    },
    async saveReviewProgress() {
      if (!this.auditId) return;
      
      this.savingProgress = true;
      
      try {
        // Collect all compliance review data
        const complianceReviews = [];
        let reviewCount = 0;
        let acceptCount = 0;
        let rejectCount = 0;
        let inReviewCount = 0;
        
        this.policies.forEach(policy => {
          policy.subpolicies.forEach(subpolicy => {
            subpolicy.compliances.forEach(compliance => {
              reviewCount++;
              
              // Count statuses for reporting
              if (compliance.review_status === 'Accept') {
                acceptCount++;
              } else if (compliance.review_status === 'Reject') {
                rejectCount++;
              } else {
                inReviewCount++;
              }
              
              complianceReviews.push({
                compliance_id: compliance.compliance_id,
                review_status: compliance.review_status || 'In Review',
                review_comments: compliance.review_comments || ''
              });
            });
          });
        });
        
        console.log(`Saving review progress for audit ${this.auditId}`);
        console.log(`Total findings: ${reviewCount}, Accepted: ${acceptCount}, Rejected: ${rejectCount}, In Review: ${inReviewCount}`);
        console.log(`Overall comments length: ${this.reviewComments?.length || 0} characters`);
        
        // Save the current state without changing the review status
        const response = await api.saveReviewProgress(this.auditId, {
          review_comments: this.reviewComments || '',
          compliance_reviews: complianceReviews
        });
        
        console.log('Review progress saved successfully:', response.data);
        
        // Show success message
        this.saveStatus = 'Saved';
        setTimeout(() => {
          this.saveStatus = null;
        }, 3000);
        
        // Clear the changed fields tracking
        this.changedFields = {};
        
        // If a new version was created, reload it
        if (response.data.review_version) {
          console.log(`New review version created: ${response.data.review_version}`);
          await this.fetchVersionData();
        }
        
      } catch (error) {
        console.error('Error saving review progress:', error);
        alert(error.response?.data?.error || 'Failed to save review progress. Please try again.');
        this.saveStatus = 'Error saving';
        setTimeout(() => {
          this.saveStatus = null;
        }, 3000);
      } finally {
        this.savingProgress = false;
      }
    },
    updateComplianceReviewField(compliance, field, value) {
      // Track changes to individual compliance review fields
      const key = `${compliance.compliance_id}_${field}`;
      this.changedFields[key] = {
        complianceId: compliance.compliance_id,
        field: field,
        value: value
      };
      
      // Ensure the review fields are correctly set on the compliance object
      if (field === 'review_status') {
        compliance.review_status = value;
        console.log(`Updated review status for compliance ${compliance.compliance_id} to ${value}`);
      } else if (field === 'review_comments') {
        compliance.review_comments = value;
        console.log(`Updated review comments for compliance ${compliance.compliance_id}`);
      }
    },
    formatDate(date) {
      if (!date) return 'N/A';
      const formattedDate = new Date(date).toLocaleDateString();
      return formattedDate;
    },
    // Debug function to check version data availability
    async checkVersionData() {
      try {
        console.log('Checking version data for audit:', this.auditId);
        const response = await api.checkAuditVersion(this.auditId);
        console.log('Version check result:', response.data);
        return response.data;
      } catch (error) {
        console.error('Error checking version data:', error);
        return null;
      }
    },
    goBackToDashboard() {
      this.$router.push('/auditor/reviews');
    },
    getApprovalStatusClass(status) {
      if (!status) return 'not-assessed';
      
      switch(status) {
        case 'Approved':
          return 'approved';
        case 'Rejected':
          return 'rejected';
        case 'Pending':
          return 'pending';
        default:
          return 'not-assessed';
      }
    },
  }
};
</script>

<style scoped>
@import '../Auditor/Reviewer.css';

.task-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  margin-left: 170px;
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

.review-mode-indicator {
  font-size: 16px;
  color: #4f7cff;
  font-weight: normal;
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
  background-color: #c82333;
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

.compliance-item.rejected {
  border-left: 4px solid #dc3545;
  background-color: #fff8f8;
}

.compliance-item.accepted {
  border-left: 4px solid #28a745;
  background-color: #f8fff8;
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
  background-color: #f9f9f9;
  cursor: not-allowed;
}

.compliance-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-height: 100px;
  resize: vertical;
  background-color: #f9f9f9;
  cursor: not-allowed;
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
  gap: 10px;
}

.file-name {
  color: #666;
  font-style: italic;
}

.view-evidence-btn {
  background-color: #4f7cff;
  color: white;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.view-evidence-btn:hover {
  background-color: #3a63cc;
}

/* Floating review panel */
.floating-review-panel {
  position: fixed;
  right: 20px;
  top: 80px;
  width: 300px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.15);
  z-index: 100;
  overflow: hidden;
}

.review-header {
  background-color: #4f7cff;
  color: white;
  padding: 12px 15px;
}

.review-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.review-body {
  padding: 15px;
}

.review-comments {
  margin-bottom: 15px;
}

.review-comments label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
  color: #555;
}

.review-comments-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-height: 100px;
  resize: vertical;
}

.review-note {
  margin: 15px 0;
  padding: 10px;
  background-color: #f0f4ff;
  border-left: 3px solid #4f7cff;
  font-size: 13px;
}

.review-note p {
  margin: 0;
  color: #333;
}

.review-actions {
  display: flex;
  justify-content: flex-end;
}

.review-save-btn {
  padding: 10px 15px;
  background-color: #3f7fff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  margin-right: 10px;
}

.review-save-btn:hover {
  background-color: #2c5fcc;
}

.review-save-btn:disabled {
  background-color: #a0a0a0;
  cursor: not-allowed;
}

.review-submit-btn {
  padding: 10px 15px;
  background-color: #4f7cff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.review-submit-btn:hover {
  background-color: #3a63cc;
}

.review-submit-btn:disabled {
  background-color: #a0a0a0;
  cursor: not-allowed;
}

/* Override for floating save button */
.floating-save {
  position: fixed;
  right: 20px;
  bottom: 80px;
  z-index: 100;
}

.submit-btn {
  padding: 12px 20px;
  background: #e0e0e0;
  color: #666;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: not-allowed;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.compliance-review-panel {
  margin-top: 20px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.review-panel-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #4f7cff;
}

.compliance-review-content {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.review-field-group {
  flex: 1;
  min-width: 250px;
}

.review-field-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
  color: #555;
}

.review-status-dropdown {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
}

.review-comments-field {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-height: 100px;
  resize: vertical;
}

/* Version indicator styles */
.version-indicator {
  font-size: 14px;
  color: #4f7cff;
  font-weight: normal;
  background-color: #eef2ff;
  padding: 4px 10px;
  border-radius: 4px;
  margin-left: 10px;
}

.version-alert {
  background-color: #fff8e6;
  border-left: 4px solid #ffaa00;
  padding: 12px 20px;
  margin-bottom: 20px;
  border-radius: 4px;
}

.reviewer-version {
  background-color: #e6f7ff;
  border-left: 4px solid #0099ff;
}

.auditor-version {
  background-color: #e6f7ff;
  border-left: 4px solid #1890ff;
}

.rejected-version {
  background-color: #fff0f0;
  border-left: 4px solid #ff0000;
}

.rejection-hint {
  margin-top: 10px;
  padding: 8px 12px;
  background-color: #ffebeb;
  border-left: 4px solid #ff0000;
  color: #800000;
  border-radius: 4px;
}

.color-legend {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.color-box {
  width: 15px;
  height: 15px;
  border-radius: 3px;
  border: 1px solid #ccc;
}

.color-box.accepted {
  background-color: #f8fff8;
  border-left: 3px solid #28a745;
}

.color-box.rejected {
  background-color: #fff8f8;
  border-left: 3px solid #dc3545;
}

.color-box.in-review {
  background-color: white;
  border-left: 3px solid #ccc;
}

.version-title {
  font-size: 18px;
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

.version-alert p {
  margin: 0 0 10px 0;
  color: #664400;
  font-size: 14px;
  line-height: 1.4;
}

.reviewer-version p {
  color: #004466;
}

.version-alert strong {
  color: #333;
}

.version-status {
  margin-top: 10px;
  padding: 5px 10px;
  border-radius: 4px;
  background-color: #f5f5f5;
  display: inline-block;
}

.version-status .approved {
  color: #00aa00;
  font-weight: bold;
}

.version-status .rejected {
  color: #aa0000;
  font-weight: bold;
}

.version-status .pending {
  color: #aaaa00;
  font-weight: bold;
}

.back-nav {
  margin-bottom: 15px;
}

.back-button {
  background-color: #f0f4ff;
  color: #4f7cff;
  border: 1px solid #d6e0ff;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.back-button:hover {
  background-color: #e0e8ff;
  color: #3a63cc;
}

/* Bottom review section */
.bottom-review-section {
  margin-top: 40px;
  padding: 30px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-left: 5px solid #4f7cff;
}

.bottom-review-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #4f7cff;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
}

.bottom-review-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.bottom-review-field {
  width: 100%;
}

.bottom-review-field label {
  display: block;
  font-weight: bold;
  margin-bottom: 8px;
  color: #555;
  font-size: 16px;
}

.bottom-review-comments {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  min-height: 150px;
  resize: vertical;
}

.bottom-review-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 10px;
}

.bottom-review-save {
  padding: 12px 25px;
  background-color: #3f7fff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  font-size: 16px;
}

.bottom-review-save:hover {
  background-color: #2c5fcc;
}

.bottom-review-save:disabled {
  background-color: #a0a0a0;
  cursor: not-allowed;
}

.bottom-review-submit {
  padding: 12px 25px;
  background-color: #4f7cff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  font-size: 16px;
}

.bottom-review-submit:hover {
  background-color: #3a63cc;
}

.bottom-review-submit:disabled {
  background-color: #a0a0a0;
  cursor: not-allowed;
}

.version-status .status-accept {
  color: #28a745;
  font-weight: bold;
}

.version-status .status-reject {
  color: #dc3545;
  font-weight: bold;
}

.version-status .status-review {
  color: #007bff;
  font-weight: bold;
}

/* No data message styling */
.no-data-message {
  text-align: center;
  padding: 40px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 20px auto;
  max-width: 600px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.no-data-icon {
  font-size: 48px;
  margin-bottom: 20px;
  color: #aaa;
}

.no-data-message h3 {
  font-size: 24px;
  margin-bottom: 15px;
  color: #555;
}

.no-data-message p {
  color: #777;
  margin-bottom: 20px;
  line-height: 1.5;
}

.btn-back {
  background-color: #4f7cff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 20px;
  font-size: 14px;
  cursor: pointer;
}

.btn-back:hover {
  background-color: #3d5abb;
}

/* Fallback version warning styles */
.version-warning {
  display: flex;
  align-items: center;
  background-color: #fff3cd;
  border-left: 4px solid #ffc107;
  padding: 12px 20px;
  margin-bottom: 15px;
  border-radius: 4px;
}

.warning-icon {
  font-size: 24px;
  margin-right: 15px;
}

.warning-message {
  color: #856404;
  font-weight: 500;
}

.fallback-version {
  border-left: 4px solid #ffc107 !important;
  background-color: #fffcf2 !important;
}
</style> 