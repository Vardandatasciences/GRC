<template>
  <div class="all-compliances-container">
    <h1>Compliance Management</h1>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <span>{{ error }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-spinner">
      <i class="fas fa-circle-notch fa-spin"></i>
      <span>Loading...</span>
    </div>

    <!-- Breadcrumbs -->
    <div class="breadcrumbs" v-if="breadcrumbs.length > 0">
      <div v-for="(crumb, index) in breadcrumbs" :key="crumb.id" class="breadcrumb-chip">
        {{ crumb.name }}
        <span class="breadcrumb-close" @click="goToStep(index)">&times;</span>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- Frameworks Section -->
      <template v-if="showFrameworks">
        <div class="section-header">Frameworks</div>
        <div class="card-grid">
          <div v-for="fw in frameworks" :key="fw.id" class="card" @click="selectFramework(fw)">
            <div class="card-icon">
              <i :class="categoryIcon(fw.category)"></i>
            </div>
            <div class="card-content">
              <div class="card-title">{{ fw.name }}</div>
              <div class="card-category">{{ fw.category }}</div>
              <div class="card-status" :class="statusClass(fw.status)">{{ fw.status }}</div>
              <div class="card-desc">{{ fw.description }}</div>
              <div class="version-info">
                <span>Versions: {{ fw.versions.length }}</span>
                <button class="version-btn" @click.stop="showVersions('framework', fw)">
                  <i class="fas fa-history"></i>
                </button>
              </div>
              <div class="card-actions">
                <button class="action-btn primary" @click.stop="viewAllCompliances('framework', fw.id, fw.name)">
                  <i class="fas fa-list"></i> View All Compliances
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Policies Section -->
      <template v-else-if="showPolicies">
        <div class="section-header">Policies in {{ selectedFramework.name }}</div>
        <div class="card-grid">
          <div v-for="policy in policies" :key="policy.id" class="card" @click="selectPolicy(policy)">
            <div class="card-icon">
              <i :class="categoryIcon(policy.category)"></i>
            </div>
            <div class="card-content">
              <div class="card-title">{{ policy.name }}</div>
              <div class="card-category">{{ policy.category }}</div>
              <div class="card-status" :class="statusClass(policy.status)">{{ policy.status }}</div>
              <div class="card-desc">{{ policy.description }}</div>
              <div class="version-info">
                <span>Versions: {{ policy.versions.length }}</span>
                <button class="version-btn" @click.stop="showVersions('policy', policy)">
                  <i class="fas fa-history"></i>
                </button>
              </div>
              <div class="card-actions">
                <button class="action-btn primary" @click.stop="viewAllCompliances('policy', policy.id, policy.name)">
                  <i class="fas fa-list"></i> View All Compliances
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Subpolicies Section -->
      <template v-else-if="showSubpolicies">
        <div class="section-header">Subpolicies in {{ selectedPolicy.name }}</div>
        <div class="card-grid">
          <div v-for="subpolicy in subpolicies" :key="subpolicy.id" class="card" @click="selectSubpolicy(subpolicy)">
            <div class="card-icon">
              <i :class="categoryIcon(subpolicy.category)"></i>
            </div>
            <div class="card-content">
              <div class="card-title">{{ subpolicy.name }}</div>
              <div class="card-category">{{ subpolicy.category }}</div>
              <div class="card-status" :class="statusClass(subpolicy.status)">{{ subpolicy.status }}</div>
              <div class="card-desc">{{ subpolicy.description }}</div>
              <div class="card-metadata">
                <span>Control: {{ subpolicy.control }}</span>
                <span>{{ subpolicy.permanent_temporary }}</span>
              </div>
              <div class="card-actions">
                <button class="action-btn primary" @click.stop="viewAllCompliances('subpolicy', subpolicy.id, subpolicy.name)">
                  <i class="fas fa-list"></i> View All Compliances
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Compliances Section -->
      <template v-else-if="selectedSubpolicy">
        <div class="section-header">
          <span>Compliances in {{ selectedSubpolicy.name }}</span>
          <div class="section-actions">
            <!-- Export Controls -->
            <div class="inline-export-controls">
              <select v-model="selectedFormat" class="format-select">
                <option value="xlsx">Excel (.xlsx)</option>
                <option value="csv">CSV (.csv)</option>
                <option value="pdf">PDF (.pdf)</option>
                <option value="json">JSON (.json)</option>
                <option value="xml">XML (.xml)</option>
              </select>
              <button class="export-btn" @click="handleExport(selectedFormat)">
                <i class="fas fa-download"></i> Export
              </button>
            </div>
            <button class="view-toggle-btn" @click="toggleViewMode">
              <i :class="viewMode === 'card' ? 'fas fa-list' : 'fas fa-th-large'"></i>
              {{ viewMode === 'card' ? 'List View' : 'Card View' }}
            </button>
            <button class="action-btn" @click="goToStep(2)">
              <i class="fas fa-arrow-left"></i> Back to Subpolicies
            </button>
          </div>
        </div>
        
        <div v-if="loading" class="loading-spinner">
          <i class="fas fa-circle-notch fa-spin"></i>
          <span>Loading compliances...</span>
        </div>
        
        <div v-else-if="!hasCompliances" class="no-data">
          <i class="fas fa-inbox"></i>
          <p>No compliances found for this subpolicy</p>
        </div>
        
        <!-- Card View -->
        <div v-else-if="viewMode === 'card'" class="compliances-grid">
          <div v-for="compliance in filteredCompliances" 
               :key="compliance.id" 
               class="compliance-card"
               @click="handleComplianceExpand(compliance)">
            <div class="compliance-header">
              <span :class="['criticality-badge', 'criticality-' + compliance.category.toLowerCase()]">
                {{ compliance.category }}
              </span>
            </div>
            
            <div class="compliance-body">
              <h3>{{ compliance.name }}</h3>
              <div class="compliance-details">
                <div class="detail-row">
                  <span class="label">Maturity Level:</span>
                  <span class="value">{{ compliance.maturityLevel }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Type:</span>
                  <span class="value">{{ compliance.mandatoryOptional }} | {{ compliance.manualAutomatic }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Version:</span>
                  <span class="value">{{ compliance.version }}</span>
                </div>
                <div class="detail-row" v-if="compliance.isRisk">
                  <span class="label">Risk Status:</span>
                  <span class="value risk">Risk Identified</span>
                </div>
              </div>
              
              <!-- Expanded Details Section -->
              <div v-if="expandedCompliance === compliance.id" class="expanded-details">
                <h4>Compliance Details</h4>

                <div class="expanded-details-grid">
                  <div class="expanded-section-box">
                    <h5>Description:</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.description">
                        {{ compliance.description }}
                      </template>
                      <template v-else>
                        <span class="empty-value">No description available</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Possible Damage:</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.PossibleDamage">
                        {{ compliance.PossibleDamage }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Mitigation:</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.mitigation">
                        {{ compliance.mitigation }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Impact:</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.Impact">
                        {{ compliance.Impact }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Probability:</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.Probability">
                        {{ compliance.Probability }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Duration:</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.PermanentTemporary">
                        {{ compliance.PermanentTemporary }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Risk Status:</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.isRisk !== undefined">
                        {{ compliance.isRisk ? 'Risk Identified' : 'No Risk' }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Status:</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.status">
                        {{ compliance.status }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>
                  
                  <div class="expanded-section-box">
                    <h5>Active/Inactive:</h5>
                    <div class="expanded-content-box">
                      <template v-if="compliance.ActiveInactive">
                        {{ compliance.ActiveInactive }}
                      </template>
                      <template v-else>
                        <span class="empty-value">Not specified</span>
                      </template>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="compliance-footer">
                <div class="created-info">
                  <span>Created by {{ compliance.createdBy }}</span>
                  <span>{{ formatDate(compliance.createdDate) }}</span>
                </div>
                <div class="identifier">ID: {{ compliance.identifier }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- List View -->
        <div v-else class="compliances-list-view">
          <table class="compliances-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Compliance</th>
                <th>Status</th>
                <th>Criticality</th>
                <th>Maturity Level</th>
                <th>Type</th>
                <th>Version</th>
                <th>Created By</th>
                <th>Created Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="compliance in filteredCompliances" :key="compliance.id">
                <tr @click="handleComplianceExpand(compliance)" :class="{ 'expanded-row': expandedCompliance === compliance.id }">
                  <td class="compliance-id">{{ compliance.identifier }}</td>
                  <td class="compliance-name">{{ compliance.name }}</td>
                  <td>
                    <span :class="['status-badge', compliance.status.toLowerCase()]">
                      {{ compliance.status }}
                    </span>
                  </td>
                  <td>
                    <span :class="['criticality-badge', 'criticality-' + compliance.category.toLowerCase()]">
                      {{ compliance.category }}
                    </span>
                  </td>
                  <td>{{ compliance.maturityLevel }}</td>
                  <td>{{ compliance.mandatoryOptional }} | {{ compliance.manualAutomatic }}</td>
                  <td>{{ compliance.version }}</td>
                  <td>{{ compliance.createdBy }}</td>
                  <td>{{ formatDate(compliance.createdDate) }}</td>
                  <td>
                    <button class="expand-btn" @click.stop="handleComplianceExpand(compliance)">
                      <i :class="expandedCompliance === compliance.id ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                    </button>
                  </td>
                </tr>
                <tr v-if="expandedCompliance === compliance.id" class="details-row">
                  <td colspan="10" class="expanded-content">
                    <div class="expanded-details-grid">
                      <div class="expanded-section-box">
                        <h5>Description:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.description">
                            {{ compliance.description }}
                          </template>
                          <template v-else>
                            <span class="empty-value">No description available</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Possible Damage:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.PossibleDamage">
                            {{ compliance.PossibleDamage }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Mitigation:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.mitigation">
                            {{ compliance.mitigation }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Impact:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.Impact">
                            {{ compliance.Impact }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Probability:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.Probability">
                            {{ compliance.Probability }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Duration:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.PermanentTemporary">
                            {{ compliance.PermanentTemporary }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Risk Status:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.isRisk !== undefined">
                            {{ compliance.isRisk ? 'Risk Identified' : 'No Risk' }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Status:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.status">
                            {{ compliance.status }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Active/Inactive:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.ActiveInactive">
                            {{ compliance.ActiveInactive }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <!-- Versions Modal -->
    <div v-if="showVersionsModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ versionModalTitle }}</h3>
          <button class="close-btn" @click="closeVersionsModal">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="versions.length === 0" class="no-versions">
            No versions found.
          </div>
          <div v-else class="version-grid">
            <div v-for="version in versions" :key="version.id" class="version-card">
              <div class="version-header">
                <span class="version-number">Version {{ version.version }}</span>
                <div class="version-badges">
                  <span class="status-badge" :class="statusClass(version.status)">{{ version.status }}</span>
                  <span class="status-badge" :class="statusClass(version.activeInactive)">{{ version.activeInactive }}</span>
                </div>
              </div>
              <div class="version-details">
                <p class="version-desc">{{ version.description }}</p>
                <div class="version-info-grid">
                  <div class="info-group">
                    <span class="info-label">Maturity Level:</span>
                    <span class="info-value">{{ version.maturityLevel }}</span>
                  </div>
                  <div class="info-group">
                    <span class="info-label">Type:</span>
                    <span class="info-value">{{ version.mandatoryOptional }} | {{ version.manualAutomatic }}</span>
                  </div>
                  <div class="info-group">
                    <span class="info-label">Criticality:</span>
                    <span class="info-value" :class="'criticality-' + version.criticality.toLowerCase()">
                      {{ version.criticality }}
                    </span>
                  </div>
                  <div class="info-group" v-if="version.isRisk">
                    <span class="info-label">Risk Status:</span>
                    <span class="info-value risk">Risk Identified</span>
                  </div>
                </div>
                <div class="version-metadata">
                  <span>
                    <i class="fas fa-user"></i>
                    {{ version.createdBy }}
                  </span>
                  <span>
                    <i class="fas fa-calendar"></i>
                    {{ formatDate(version.createdDate) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- All Compliances Modal -->
    <div class="modal-overlay" v-if="showCompliancesModal">
      <div class="modal-container">
        <div class="modal-header">
          <h2>{{ modalTitle }}</h2>
          <div class="modal-controls">
            <!-- Export Controls for Modal -->
            <div class="inline-export-controls">
              <select v-model="selectedFormat" class="format-select">
                <option value="xlsx">Excel (.xlsx)</option>
                <option value="csv">CSV (.csv)</option>
                <option value="pdf">PDF (.pdf)</option>
                <option value="json">JSON (.json)</option>
                <option value="xml">XML (.xml)</option>
              </select>
              <button class="export-btn" @click="handleModalExport">
                <i class="fas fa-download"></i> Export
              </button>
            </div>
            <button class="view-toggle-btn" @click="toggleModalViewMode">
              <i :class="modalViewMode === 'card' ? 'fas fa-list' : 'fas fa-th-large'"></i>
              {{ modalViewMode === 'card' ? 'List View' : 'Card View' }}
            </button>
            <button class="close-button" @click="closeModal">×</button>
          </div>
        </div>
        
        <div class="modal-body">
          <!-- Compliances List -->
          <div class="compliances-list">
            <div v-if="loading" class="loading">
              <div class="spinner"></div>
              <p>Loading compliances...</p>
            </div>
            
            <div v-else-if="!compliances.length" class="no-data">
              <i class="fas fa-info-circle"></i>
              <p>No compliances found</p>
            </div>
            
            <!-- Card View for Modal -->
            <div v-else-if="modalViewMode === 'card'" class="compliances-grid">
              <div v-for="compliance in filteredModalCompliances" 
                   :key="compliance.ComplianceId" 
                   class="compliance-card"
                   @click="toggleModalExpand(compliance)">
                <div class="compliance-header">
                  <span :class="['criticality-badge', 'criticality-' + compliance.Criticality.toLowerCase()]">
                    {{ compliance.Criticality }}
                  </span>
                </div>
                
                <div class="compliance-body">
                  <h3>{{ compliance.ComplianceItemDescription }}</h3>
                  
                  <div class="compliance-details">
                    <div class="detail-row">
                      <span class="label">Maturity Level:</span>
                      <span class="value">{{ compliance.MaturityLevel }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="label">Type:</span>
                      <span class="value">{{ compliance.ManualAutomatic }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="label">Requirement:</span>
                      <span class="value">{{ compliance.MandatoryOptional }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="label">Version:</span>
                      <span class="value">{{ compliance.ComplianceVersion }}</span>
                    </div>
                  </div>
                  
                  <!-- Expanded Details Section for Modal -->
                  <div v-if="expandedModalCompliance === compliance.ComplianceId" class="expanded-details">
                    <h4>Compliance Details</h4>

                    <div class="expanded-details-grid">
                      <div class="expanded-section-box">
                        <h5>Description:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.ComplianceItemDescription">
                            {{ compliance.ComplianceItemDescription }}
                          </template>
                          <template v-else>
                            <span class="empty-value">No description available</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Possible Damage:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.PossibleDamage">
                            {{ compliance.PossibleDamage }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Mitigation:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.mitigation">
                            {{ compliance.mitigation }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Impact:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.Impact">
                            {{ compliance.Impact }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Probability:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.Probability">
                            {{ compliance.Probability }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Duration:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.PermanentTemporary">
                            {{ compliance.PermanentTemporary }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Risk Status:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.IsRisk !== undefined">
                            {{ compliance.IsRisk ? 'Risk Identified' : 'No Risk' }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Status:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.Status">
                            {{ compliance.Status }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                      
                      <div class="expanded-section-box">
                        <h5>Active/Inactive:</h5>
                        <div class="expanded-content-box">
                          <template v-if="compliance.ActiveInactive">
                            {{ compliance.ActiveInactive }}
                          </template>
                          <template v-else>
                            <span class="empty-value">Not specified</span>
                          </template>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="compliance-footer">
                    <div class="created-info">
                      <span>Created by {{ compliance.CreatedByName }}</span>
                      <span>{{ formatDate(compliance.CreatedByDate) }}</span>
                    </div>
                    <div class="identifier">ID: {{ compliance.Identifier }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- List View for Modal -->
            <div v-else class="compliances-list-view">
              <table class="compliances-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Compliance</th>
                    <th>Status</th>
                    <th>Criticality</th>
                    <th>Maturity Level</th>
                    <th>Type</th>
                    <th>Requirement</th>
                    <th>Version</th>
                    <th>Created By</th>
                    <th>Created Date</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="compliance in filteredModalCompliances" :key="compliance.ComplianceId">
                    <tr @click="toggleModalExpand(compliance)" :class="{ 'expanded-row': expandedModalCompliance === compliance.ComplianceId }">
                      <td class="compliance-id">{{ compliance.Identifier }}</td>
                      <td class="compliance-name">{{ compliance.ComplianceItemDescription }}</td>
                      <td>
                        <span :class="['status-badge', compliance.Status.toLowerCase()]">
                          {{ compliance.Status }}
                        </span>
                      </td>
                      <td>
                        <span :class="['criticality-badge', 'criticality-' + compliance.Criticality.toLowerCase()]">
                          {{ compliance.Criticality }}
                        </span>
                      </td>
                      <td>{{ compliance.MaturityLevel }}</td>
                      <td>{{ compliance.ManualAutomatic }}</td>
                      <td>{{ compliance.MandatoryOptional }}</td>
                      <td>{{ compliance.ComplianceVersion }}</td>
                      <td>{{ compliance.CreatedByName }}</td>
                      <td>{{ formatDate(compliance.CreatedByDate) }}</td>
                      <td>
                        <button class="expand-btn" @click.stop="toggleModalExpand(compliance)">
                          <i :class="expandedModalCompliance === compliance.ComplianceId ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                        </button>
                      </td>
                    </tr>
                    <tr v-if="expandedModalCompliance === compliance.ComplianceId" class="details-row">
                      <td colspan="11" class="expanded-content">
                        <!-- Complete details for modal list view -->
                        <div class="expanded-details-grid">
                          <div class="expanded-section-box">
                            <h5>Description:</h5>
                            <div class="expanded-content-box">
                              <template v-if="compliance.ComplianceItemDescription">
                                {{ compliance.ComplianceItemDescription }}
                              </template>
                              <template v-else>
                                <span class="empty-value">No description available</span>
                              </template>
                            </div>
                          </div>
                          
                          <div class="expanded-section-box">
                            <h5>Possible Damage:</h5>
                            <div class="expanded-content-box">
                              <template v-if="compliance.PossibleDamage">
                                {{ compliance.PossibleDamage }}
                              </template>
                              <template v-else>
                                <span class="empty-value">Not specified</span>
                              </template>
                            </div>
                          </div>
                          
                          <div class="expanded-section-box">
                            <h5>Mitigation:</h5>
                            <div class="expanded-content-box">
                              <template v-if="compliance.mitigation">
                                {{ compliance.mitigation }}
                              </template>
                              <template v-else>
                                <span class="empty-value">Not specified</span>
                              </template>
                            </div>
                          </div>
                          
                          <div class="expanded-section-box">
                            <h5>Impact:</h5>
                            <div class="expanded-content-box">
                              <template v-if="compliance.Impact">
                                {{ compliance.Impact }}
                              </template>
                              <template v-else>
                                <span class="empty-value">Not specified</span>
                              </template>
                            </div>
                          </div>
                          
                          <div class="expanded-section-box">
                            <h5>Probability:</h5>
                            <div class="expanded-content-box">
                              <template v-if="compliance.Probability">
                                {{ compliance.Probability }}
                              </template>
                              <template v-else>
                                <span class="empty-value">Not specified</span>
                              </template>
                            </div>
                          </div>
                          
                          <div class="expanded-section-box">
                            <h5>Duration:</h5>
                            <div class="expanded-content-box">
                              <template v-if="compliance.PermanentTemporary">
                                {{ compliance.PermanentTemporary }}
                              </template>
                              <template v-else>
                                <span class="empty-value">Not specified</span>
                              </template>
                            </div>
                          </div>
                          
                          <div class="expanded-section-box">
                            <h5>Risk Status:</h5>
                            <div class="expanded-content-box">
                              <template v-if="compliance.IsRisk !== undefined">
                                {{ compliance.IsRisk ? 'Risk Identified' : 'No Risk' }}
                              </template>
                              <template v-else>
                                <span class="empty-value">Not specified</span>
                              </template>
                            </div>
                          </div>
                          
                          <div class="expanded-section-box">
                            <h5>Status:</h5>
                            <div class="expanded-content-box">
                              <template v-if="compliance.Status">
                                {{ compliance.Status }}
                              </template>
                              <template v-else>
                                <span class="empty-value">Not specified</span>
                              </template>
                            </div>
                          </div>
                          
                          <div class="expanded-section-box">
                            <h5>Active/Inactive:</h5>
                            <div class="expanded-content-box">
                              <template v-if="compliance.ActiveInactive">
                                {{ compliance.ActiveInactive }}
                              </template>
                              <template v-else>
                                <span class="empty-value">Not specified</span>
                              </template>
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  </template>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// State
const frameworks = ref([])
const selectedFramework = ref(null)
const selectedPolicy = ref(null)
const selectedSubpolicy = ref(null)
const showVersionsModal = ref(false)
const versions = ref([])
const policies = ref([])
const subpolicies = ref([])
const loading = ref(false)
const error = ref(null)
const versionModalTitle = ref('')
const showCompliancesModal = ref(false)
const compliances = ref([])
const selectedFormat = ref('xlsx')
const currentItemType = ref(null)
const currentItemId = ref(null)
const currentItemName = ref('')
const isExporting = ref(false)
const exportError = ref(null)
const viewMode = ref('list') // Changed to list as default view
const modalViewMode = ref('list') // Changed to list as default view
const expandedCompliance = ref(null)
const expandedModalCompliance = ref(null)

// Computed
const breadcrumbs = computed(() => {
  const arr = []
  if (selectedFramework.value) arr.push({ id: 0, name: selectedFramework.value.name })
  if (selectedPolicy.value) arr.push({ id: 1, name: selectedPolicy.value.name })
  if (selectedSubpolicy.value) arr.push({ id: 2, name: selectedSubpolicy.value.name })
  return arr
})

const modalTitle = computed(() => {
  if (!currentItemName.value) return 'Compliances'
  return `All Compliances - ${currentItemName.value}`
})

const showFrameworks = computed(() => !selectedFramework.value)
const showPolicies = computed(() => selectedFramework.value && !selectedPolicy.value)
const showSubpolicies = computed(() => selectedPolicy.value && !selectedSubpolicy.value)

const hasCompliances = computed(() => {
  return selectedSubpolicy.value && 
         selectedSubpolicy.value.compliances && 
         selectedSubpolicy.value.compliances.length > 0;
})

// Replace the filtered computed properties
const filteredCompliances = computed(() => {
  if (!selectedSubpolicy.value || !selectedSubpolicy.value.compliances) return [];
  return selectedSubpolicy.value.compliances; // Return all compliances without filtering
});

const filteredModalCompliances = computed(() => {
  if (!compliances.value) return [];
  return compliances.value; // Return all compliances without filtering
});

// Lifecycle
onMounted(async () => {
  try {
    loading.value = true
    // Get all frameworks with their versions
    const response = await axios.get('/api/all-policies/frameworks/')
    if (response.data && Array.isArray(response.data)) {
      frameworks.value = response.data.map(framework => ({
        ...framework,
        versions: framework.versions || [] // Versions should be included in the framework response
      }))
    } else {
      frameworks.value = []
    }
  } catch (err) {
    error.value = 'Failed to load frameworks'
    console.error('Error fetching frameworks:', err)
    frameworks.value = []
  } finally {
    loading.value = false
  }
})

// Methods
async function selectFramework(fw) {
  try {
    loading.value = true
    selectedFramework.value = fw
    selectedPolicy.value = null
    selectedSubpolicy.value = null
    
    // Get active policies for the selected framework using the correct endpoint
    const response = await axios.get('/api/all-policies/policies/', {
      params: { 
        framework_id: fw.id
      }
    })
    
    if (response.data && Array.isArray(response.data)) {
      policies.value = response.data.map(policy => ({
        ...policy,
        versions: policy.versions || [] // Versions count should be included in the response
      }))
    } else {
      policies.value = []
    }
  } catch (err) {
    error.value = 'Failed to load policies'
    console.error('Error fetching policies:', err)
    policies.value = []
  } finally {
    loading.value = false
  }
}

async function selectPolicy(policy) {
  try {
    loading.value = true
    selectedPolicy.value = policy
    selectedSubpolicy.value = null
    
    // Get active subpolicies for the selected policy using the correct endpoint
    const response = await axios.get('/api/all-policies/subpolicies/', {
      params: { 
        policy_id: policy.id
      }
    })
    
    if (response.data && Array.isArray(response.data)) {
      subpolicies.value = response.data
    } else {
      subpolicies.value = []
    }
  } catch (err) {
    error.value = 'Failed to load subpolicies'
    console.error('Error fetching subpolicies:', err)
    subpolicies.value = []
  } finally {
    loading.value = false
  }
}

async function selectSubpolicy(subpolicy) {
  try {
    loading.value = true;
    selectedSubpolicy.value = subpolicy;
    
    const response = await axios.get(`/api/all-policies/subpolicies/${subpolicy.id}/compliances/`);
    console.log('Subpolicy compliances response:', response.data);
    
    if (response.data && response.data.success) {
      // Enhanced logging for debugging
      if (response.data.compliances.length > 0) {
        const firstCompliance = response.data.compliances[0];
        console.log('DETAILED COMPLIANCE OBJECT:', JSON.stringify(firstCompliance, null, 2));
        
        // Display all field names and values for better debugging
        console.log('COMPLIANCE FIELD VALUES:');
        Object.keys(firstCompliance).forEach(key => {
          console.log(`- ${key}: ${JSON.stringify(firstCompliance[key])}`);
        });
      }
      
      // Store the original compliance objects as they come from the API
      selectedSubpolicy.value = {
        ...subpolicy,
        compliances: response.data.compliances.map(compliance => {
          return {
            // IMPORTANT: Use the exact PascalCase field names from the API
            id: compliance.ComplianceId,
            name: compliance.ComplianceItemDescription,
            description: compliance.ComplianceItemDescription,
            status: compliance.Status,
            category: compliance.Criticality,
            maturityLevel: compliance.MaturityLevel,
            mandatoryOptional: compliance.MandatoryOptional,
            manualAutomatic: compliance.ManualAutomatic,
            createdBy: compliance.CreatedByName,
            createdDate: compliance.CreatedByDate,
            identifier: compliance.Identifier,
            version: compliance.ComplianceVersion,
            isRisk: compliance.IsRisk,
            
            // Keep the original Pascal case names for these fields
            PossibleDamage: compliance.PossibleDamage,
            mitigation: compliance.mitigation,
            Impact: compliance.Impact,
            Probability: compliance.Probability,
            PermanentTemporary: compliance.PermanentTemporary,
            ActiveInactive: compliance.ActiveInactive,
            
            // Store the original object to access all fields in the expanded view
            originalData: compliance
          };
        })
      };
    } else {
      selectedSubpolicy.value.compliances = [];
    }
  } catch (err) {
    console.error('Error fetching subpolicy compliances:', err);
    error.value = 'Failed to load compliances';
    selectedSubpolicy.value.compliances = [];
  } finally {
    loading.value = false;
  }
}

async function showVersions(type, item) {
  try {
    loading.value = true
    let endpoint = ''
    
    switch (type) {
      case 'policy':
        versionModalTitle.value = `Versions of ${item.name}`
        endpoint = `/api/all-policies/policies/${item.id}/versions/`
        break
      case 'compliance':
        versionModalTitle.value = `Versions of Compliance ${item.name}`
        endpoint = `/api/all-policies/compliances/${item.id}/versions/`
        break
    }
    
    const response = await axios.get(endpoint)
    if (response.data && Array.isArray(response.data)) {
      versions.value = response.data.map(version => ({
        id: version.ComplianceId,
        version: version.ComplianceVersion,
        name: version.ComplianceItemDescription,
        status: version.Status,
        description: version.ComplianceItemDescription,
        criticality: version.Criticality,
        maturityLevel: version.MaturityLevel,
        mandatoryOptional: version.MandatoryOptional,
        manualAutomatic: version.ManualAutomatic,
        createdBy: version.CreatedByName,
        createdDate: version.CreatedByDate,
        isRisk: version.IsRisk,
        activeInactive: version.ActiveInactive,
        identifier: version.Identifier
      }))
    } else {
      versions.value = []
    }
    showVersionsModal.value = true
  } catch (err) {
    error.value = `Failed to load ${type} versions`
    console.error(`Error fetching ${type} versions:`, err)
    versions.value = []
  } finally {
    loading.value = false
  }
}

function closeVersionsModal() {
  showVersionsModal.value = false
  versions.value = []
  versionModalTitle.value = ''
}

function goToStep(idx) {
  if (idx <= 0) {
    selectedFramework.value = null
    selectedPolicy.value = null
    selectedSubpolicy.value = null
  } else if (idx === 1) {
    selectedPolicy.value = null
    selectedSubpolicy.value = null
  } else if (idx === 2) {
    selectedSubpolicy.value = null
  }
}

function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

function categoryIcon(category) {
  switch ((category || '').toLowerCase()) {
    case 'governance': return 'fas fa-shield-alt'
    case 'access control': return 'fas fa-user-shield'
    case 'asset management': return 'fas fa-boxes'
    case 'cryptography': return 'fas fa-key'
    case 'data management': return 'fas fa-database'
    case 'device management': return 'fas fa-mobile-alt'
    case 'risk management': return 'fas fa-exclamation-triangle'
    case 'supplier management': return 'fas fa-handshake'
    case 'business continuity': return 'fas fa-business-time'
    case 'privacy': return 'fas fa-user-secret'
    case 'system protection': return 'fas fa-shield-virus'
    case 'incident response': return 'fas fa-ambulance'
    default: return 'fas fa-file-alt'
  }
}

function statusClass(status) {
  if (!status) return ''
  const s = status.toLowerCase()
  if (s.includes('active')) return 'active'
  if (s.includes('inactive')) return 'inactive'
  if (s.includes('pending')) return 'pending'
  return ''
}

const viewAllCompliances = async (type, id, name) => {
  try {
    loading.value = true;
    showCompliancesModal.value = true;
    currentItemType.value = type;
    currentItemId.value = id;
    currentItemName.value = name;

    console.log(`Fetching compliances for ${type} with ID ${id}`);
    
    let endpoint = '';
    switch(type) {
      case 'framework':
        endpoint = `/compliances/framework/${id}/`;
        break;
      case 'policy':
        endpoint = `/compliances/policy/${id}/`;
        break;
      case 'subpolicy':
        endpoint = `/compliances/subpolicy/${id}/compliances/`;
        break;
      default:
        throw new Error('Invalid type specified');
    }
    
    const response = await axios.get(endpoint);
    console.log('API Response:', response.data);
    
    if (response.data && response.data.success) {
      // Store the original compliance objects for modal view
      compliances.value = response.data.compliances.map(compliance => {
        // Log a sample compliance to check available fields
        if (response.data.compliances.indexOf(compliance) === 0) {
          console.log('Modal view - Full compliance object:', compliance);
        }
        return compliance;
      });
    } else {
      throw new Error(response.data.message || 'Failed to fetch compliances');
    }
  } catch (error) {
    console.error('Error fetching compliances:', error);
    compliances.value = [];
    error.value = 'Failed to fetch compliances. Please try again.';
  } finally {
    loading.value = false;
  }
}

async function handleExport(format) {
  try {
    isExporting.value = true;
    exportError.value = null;
    
    let itemType = '';
    let itemId = currentItemId.value;
    
    // Determine the item type
    switch(currentItemType.value) {
      case 'framework':
        itemType = 'framework';
        break;
      case 'policy':
        itemType = 'policy';
        break;
      case 'subpolicy':
        itemType = 'subpolicy';
        break;
      default:
        throw new Error('Invalid export type');
    }
    
    console.log(`Attempting export for ${itemType} ${itemId} in ${format} format`);
    
    // Update the API endpoint URL with path parameters
    const response = await axios({
      url: `/api/export/all-compliances/${format}/${itemType}/${itemId}/`,
      method: 'GET',
      responseType: 'blob',
      timeout: 30000,
      headers: {
        'Accept': 'application/json, application/pdf, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, text/csv, application/xml'
      }
    });

    // Handle successful download
    const contentType = response.headers['content-type'];
    const blob = new Blob([response.data], { type: contentType });
    
    // Get filename from header or create default
    let filename = `compliances_${itemType}_${itemId}.${format}`;
    const disposition = response.headers['content-disposition'];
    if (disposition && disposition.includes('filename=')) {
      filename = disposition.split('filename=')[1].replace(/"/g, '');
    }
    
    // Trigger download
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
    
    ElMessage({
      message: 'Export completed successfully',
      type: 'success',
      duration: 3000
    });
  } catch (error) {
    console.error('Export error:', error);
    const errorMessage = error.response?.data?.message || error.message || 'Failed to export compliances';
    exportError.value = errorMessage;
    ElMessage({
      message: errorMessage,
      type: 'error',
      duration: 5000
    });
  } finally {
    isExporting.value = false;
  }
}

const handleModalExport = () => {
  if (!currentItemType.value || !currentItemId.value) {
    ElMessage({
      message: 'No compliances selected for export',
      type: 'warning',
      duration: 3000
    });
    return;
  }
  handleExport(selectedFormat.value);
}

const closeModal = () => {
  showCompliancesModal.value = false;
  compliances.value = [];
  currentItemType.value = null;
  currentItemId.value = null;
  currentItemName.value = '';
  error.value = null; // Clear any error messages
}

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'card' ? 'list' : 'card';
}

const toggleModalViewMode = () => {
  modalViewMode.value = modalViewMode.value === 'card' ? 'list' : 'card';
}

const toggleExpand = (compliance) => {
  if (expandedCompliance.value === compliance.id) {
    expandedCompliance.value = null;
  } else {
    expandedCompliance.value = compliance.id;
  }
};

// Add a function to fetch detailed compliance data by ID
async function fetchComplianceDetails(complianceId) {
  try {
    console.log(`Fetching detailed compliance data for ID: ${complianceId}`);
    // Use the backend endpoint that provides full compliance details
    const response = await axios.get(`/compliance/${complianceId}/`);
    
    if (response.data && response.data.success) {
      console.log('Detailed compliance data received:', response.data.data);
      return response.data.data;
    } else {
      console.warn('Failed to fetch compliance details:', response.data?.message || 'Unknown error');
      return null;
    }
  } catch (error) {
    console.error('Error fetching compliance details:', error);
    return null;
  }
}

// Update the toggleModalExpand function to fetch detailed data
const toggleModalExpand = async (compliance) => {
  // Toggle the expanded state
  if (expandedModalCompliance.value === compliance.ComplianceId) {
    expandedModalCompliance.value = null;
  } else {
    expandedModalCompliance.value = compliance.ComplianceId;
    
    // Log the available data for debugging
    console.log('Initial modal compliance data:', compliance);
    
    // Try to fetch more detailed compliance data
    try {
      const detailedData = await fetchComplianceDetails(compliance.ComplianceId);
      if (detailedData) {
        // Update the compliance object with the detailed data
        Object.assign(compliance, detailedData);
        console.log('Enhanced compliance data after fetch:', compliance);
      }
    } catch (error) {
      console.error('Error enhancing compliance data:', error);
    }
    
    // Display all field names and values for debugging
    console.log('MODAL COMPLIANCE FIELD VALUES:');
    Object.keys(compliance).forEach(key => {
      console.log(`- ${key}: ${JSON.stringify(compliance[key])}`);
    });
  }
};

// Update the handleComplianceExpand function with improved debugging
async function handleComplianceExpand(compliance) {
  // Toggle the expanded state
  toggleExpand(compliance);
  
  // Log the available data for debugging
  if (expandedCompliance.value === compliance.id) {
    console.log('Expanded compliance data:', compliance);
    
    // Show full data structure with all fields for debugging
    console.log('EXPANDED COMPLIANCE ALL FIELDS:');
    console.log('- Description:', compliance.description);
    console.log('- Possible Damage:', compliance.PossibleDamage);
    console.log('- Mitigation:', compliance.mitigation);
    console.log('- Impact:', compliance.Impact);
    console.log('- Probability:', compliance.Probability);
    console.log('- Duration:', compliance.PermanentTemporary);
    console.log('- Risk Status:', compliance.isRisk);
    console.log('- Status:', compliance.status);
    console.log('- Active/Inactive:', compliance.ActiveInactive);
    
    // Log a specific property to check if it's undefined or just empty
    if (compliance.PossibleDamage === undefined) {
      console.log('PossibleDamage is undefined');
    } else if (compliance.PossibleDamage === null) {
      console.log('PossibleDamage is null');
    } else if (compliance.PossibleDamage === '') {
      console.log('PossibleDamage is empty string');
    } else {
      console.log('PossibleDamage value:', compliance.PossibleDamage);
    }
  }
}
</script>

<style src="./AllCompliance.css"></style>

<style>
/* Add these styles to your existing CSS */
.version-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.version-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
  color: #4b5563;
}

.version-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.version-desc {
  color: #4b5563;
  margin: 12px 0;
  line-height: 1.5;
}

.card {
  border: 1px solid #e5e7eb;
  background: #ffffff;
  transition: all 0.3s ease;
}

.card:hover {
  border-color: #4b5563;
  transform: translateY(-2px);
}

.card-title {
  color: #4b5563;
  font-weight: 600;
}

.card-desc {
  color: #4b5563;
}

.detail-label {
  color: #4b5563;
}

.detail-value {
  color: #4b5563;
  font-weight: 500;
}

.version-info-grid {
  background: #f9fafb;
  border-radius: 6px;
  padding: 12px;
  margin: 12px 0;
}

.info-group {
  margin-bottom: 8px;
}

.info-label {
  color: #4b5563;
  font-size: 0.85rem;
  font-weight: 500;
}

.info-value {
  color: #4b5563;
  font-size: 0.9rem;
}

.card-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.action-btn.primary {
  background-color: #4a90e2;
  color: white;
}

.action-btn.secondary {
  background-color: #f8f9fa;
  color: #4a90e2;
  border: 1px solid #4a90e2;
}

.action-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.export-options {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.export-options select {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.compliance-item {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.compliance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
}

.status-badge.approved {
  background-color: #4caf50;
  color: white;
}

.status-badge.under-review {
  background-color: #ff9800;
  color: white;
}

.status-badge.rejected {
  background-color: #f44336;
  color: white;
}

.criticality-high {
  color: #f44336;
}

.criticality-medium {
  color: #ff9800;
}

.criticality-low {
  color: #4caf50;
}

/* Modal Styles */
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

.modal-container {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(90vh - 80px);
}

/* Export Controls */
.export-controls {
  margin: 16px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.export-controls .format-selector {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.export-controls .format-selector label {
  font-weight: 500;
  color: #4b5563;
}

.export-controls .format-selector select {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background-color: #f9fafb;
  color: #374151;
  font-size: 0.95rem;
  min-width: 150px;
}

.export-btn.enhanced {
  background-color: #3b82f6;
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.export-btn.enhanced:hover {
  background-color: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.export-btn.enhanced:active {
  transform: translateY(0);
}

.export-btn.enhanced i {
  font-size: 1.1rem;
}

/* Compliances Grid */
.compliances-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.compliance-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.compliance-header {
  padding: 10px;
  display: flex;
  justify-content: space-between;
  background-color: #f8f9fa;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85em;
}

.status-badge.approved { background-color: #4CAF50; color: white; }
.status-badge.rejected { background-color: #f44336; color: white; }
.status-badge.under-review { background-color: #ff9800; color: white; }

.criticality-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  font-weight: 500;
}

.criticality-high { background-color: #ffebee; color: #d32f2f; }
.criticality-medium { background-color: #fff3e0; color: #f57c00; }
.criticality-low { background-color: #e8f5e9; color: #388e3c; }

.compliance-body {
  padding: 15px;
}

.compliance-body h3 {
  margin: 0 0 15px 0;
  font-size: 1.1em;
  color: #333;
}

.compliance-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9em;
}

.detail-row .label {
  color: #666;
}

.detail-row .value {
  font-weight: 500;
  color: #333;
}

.compliance-footer {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
  font-size: 0.85em;
  color: #666;
}

.created-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.identifier {
  font-family: monospace;
  color: #888;
}

/* Loading State */
.loading {
  text-align: center;
  padding: 40px;
}

.spinner {
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

/* No Data State */
.no-data {
  text-align: center;
  padding: 40px;
  color: #666;
}

.no-data i {
  font-size: 48px;
  margin-bottom: 20px;
  color: #ddd;
}

.export-buttons {
  margin: 16px 0;
  text-align: right;
}

.export-controls .el-alert {
  margin-top: 10px;
  text-align: left;
}

/* Styles for expanded details view */
.expanded-details {
  margin-top: 16px;
  padding: 16px;
  background-color: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.expanded-details h4 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #1f2937;
  font-size: 1.1rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 8px;
}

.expanded-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.expanded-section-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.expanded-section-box h5 {
  margin: 0;
  padding: 10px 15px;
  background-color: #f3f4f6;
  color: #374151;
  font-size: 0.9rem;
  font-weight: 600;
  border-bottom: 1px solid #e5e7eb;
}

.expanded-content-box {
  padding: 15px;
  min-height: 40px;
  color: #1f2937;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Add field category headings */
.expanded-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.expanded-details h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 0;
  margin-bottom: 16px;
  color: #1f2937;
  font-size: 1.1rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 12px;
}

.expanded-details h4:before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 20px;
  background-color: #4f46e5;
  border-radius: 2px;
}

/* Add "empty value" styling */
.empty-value {
  color: #d1d5db;
  font-style: italic;
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  background-color: #f3f4f6;
  border: 1px dashed #cbd5e1;
}

.expanded-row {
  background-color: #f8fafc !important;
}

.details-row {
  background-color: #f1f5f9;
}

.details-row td {
  padding: 20px !important;
  border-bottom: 1px solid #e2e8f0;
}

/* Make expanded boxes slightly larger in list view */
.details-row .expanded-content-box {
  padding: 15px;
  min-height: 50px;
  font-size: 1rem;
}

/* Override grid layout for list view for better readability */
.details-row .expanded-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

/* Add a subtle animation for expanding rows */
.details-row {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>