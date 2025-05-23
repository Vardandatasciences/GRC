<template>
  <div class="all-policies-container">
    <div class="tabs-container">
      <div class="tabs-wrapper">
        <div 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="['tab', tab.id, { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          <i :class="tab.icon"></i>
          {{ tab.name }}
        </div>
      </div>
      
      <div class="framework-dropdown">
        <select id="framework" v-model="selectedFramework">
          <option value="" disabled selected>Select Framework</option>
          <option value="ISO 27001">ISO 27001</option>
          <option value="NIST">NIST</option>
          <option value="SOC 2">SOC 2</option>
          <option value="GDPR">GDPR</option>
        </select>
      </div>
    </div>

    <div class="policies-table-container">
      <table class="policies-table">
        <thead>
          <tr>
            <th>Policy Name</th>
            <th>Version</th>
            <th>Category</th>
            <th>Framework</th>
            <th>Status</th>
            <th>Created By</th>
            <th>Created On</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="policy in filteredPolicies" :key="policy.id">
            <tr>
              <td @click="togglePolicyDocument(policy.id)" class="policy-name">
                {{ policy.name }}
                <i 
                  v-if="policy.subpolicies && policy.subpolicies.length" 
                  class="fas fa-chevron-right expand-icon" 
                  :class="{ 'rotated': expandedPolicies.includes(policy.id) }"
                  @click.stop="toggleSubpolicies(policy.id)"
                ></i>
              </td>
              <td>{{ policy.version }}</td>
              <td>{{ policy.category }}</td>
              <td>{{ policy.framework }}</td>
              <td>
                <span :class="['status-badge', getPolicyStatusClass(policy.status)]">
                  {{ getPolicyStatusLabel(policy.status) }}
                </span>
              </td>
              <td>{{ policy.createdBy }}</td>
              <td>{{ policy.createdOn }}</td>
            </tr>
            
            <!-- Policy Document Section -->
            <tr v-if="expandedDocuments.includes(policy.id)">
              <td colspan="7">
                <div class="policy-document expanded">
                  <div class="policy-document-section">
                    <h4>Project Description</h4>
                    <p>{{ policy.description || 'This policy establishes guidelines and requirements for ' + policy.name.toLowerCase() + ' within the organization to ensure compliance with relevant regulations and standards.' }}</p>
                  </div>
                  <div class="policy-document-section">
                    <h4>Scope</h4>
                    <p>{{ policy.scope || 'This policy applies to all employees, contractors, and third-party entities that interact with organizational assets and systems.' }}</p>
                  </div>
                  <div class="policy-document-section">
                    <h4>Objectives</h4>
                    <p>{{ policy.objectives || 'To define roles and responsibilities, establish controls, and provide guidance for maintaining compliance with ' + policy.framework + ' standards.' }}</p>
                  </div>
                </div>
              </td>
            </tr>
            
            <!-- Subpolicies -->
            <template v-if="policy.subpolicies && policy.subpolicies.length">
              <template v-for="(subpolicy, index) in policy.subpolicies" :key="`${policy.id}-sub-${index}`">
                <tr class="subpolicy-row" :class="{ 'expanded': expandedPolicies.includes(policy.id) }">
                  <td @click="toggleSubpolicyDocument(`${policy.id}-sub-${index}`)">{{ subpolicy.name }}</td>
                  <td>{{ subpolicy.version || policy.version }}</td>
                  <td>{{ subpolicy.category || policy.category }}</td>
                  <td>{{ subpolicy.framework || policy.framework }}</td>
                  <td>
                    <span :class="['status-badge', getPolicyStatusClass(subpolicy.status)]">
                      {{ getPolicyStatusLabel(subpolicy.status) }}
                    </span>
                  </td>
                  <td>{{ subpolicy.createdBy || policy.createdBy }}</td>
                  <td>{{ subpolicy.createdOn || policy.createdOn }}</td>
                </tr>
                
                <!-- Subpolicy Document Section -->
                <tr v-if="expandedDocuments.includes(`${policy.id}-sub-${index}`)">
                  <td colspan="7">
                    <div class="policy-document expanded">
                      <div class="policy-document-section">
                        <h4>Project Description</h4>
                        <p>{{ subpolicy.description || 'This is a sub-policy of ' + policy.name + ' that focuses specifically on ' + subpolicy.name.toLowerCase() + '.' }}</p>
                      </div>
                      <div class="policy-document-section">
                        <h4>Scope</h4>
                        <p>{{ subpolicy.scope || 'This sub-policy applies to all aspects of ' + subpolicy.name.toLowerCase() + ' within the organization.' }}</p>
                      </div>
                      <div class="policy-document-section">
                        <h4>Objectives</h4>
                        <p>{{ subpolicy.objectives || 'To ensure consistent implementation and management of ' + subpolicy.name + ' controls in alignment with ' + policy.framework + '.' }}</p>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </template>
          </template>
        </tbody>
      </table>
      
      <!-- Empty state when no policies match the filter -->
      <div class="empty-state" v-if="filteredPolicies.length === 0">
        <i class="fas fa-file-alt"></i>
        <p>No policies found for the selected status</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import './AllPolicies.css'

export default {
  name: 'AllPolicies',
  setup() {
    const activeTab = ref('under-review')
    const selectedFramework = ref('')
    const expandedPolicies = ref([])
    const expandedDocuments = ref([])
    
    const tabs = [
      { id: 'rejected', name: 'Rejected', icon: 'fas fa-times-circle' },
      { id: 'scheduled', name: 'Scheduled', icon: 'fas fa-clock' },
      { id: 'under-review', name: 'Under Review', icon: 'fas fa-search' },
      { id: 'approved', name: 'Approved', icon: 'fas fa-check-circle' }
    ]
    
    // Sample policies data with subpolicies
    const policies = [
      {
        id: 'POL-001',
        name: 'Information Security Policy',
        version: '1.2',
        category: 'Security',
        framework: 'ISO 27001',
        status: 'Approved',
        createdBy: 'John Smith',
        createdOn: '2023-10-15',
        description: 'This policy outlines the organization\'s approach to information security management.',
        scope: 'All information assets owned, controlled, or processed by the organization.',
        objectives: 'To establish a framework for protecting the confidentiality, integrity, and availability of information.',
        subpolicies: [
          {
            name: 'Data Classification Policy',
            version: '1.1',
            status: 'Approved',
            description: 'Guidelines for classifying organizational data based on sensitivity and criticality.'
          },
          {
            name: 'Access Control Policy',
            version: '1.0',
            status: 'Approved',
            description: 'Rules and guidelines for controlling access to information systems and data.'
          }
        ]
      },
      {
        id: 'POL-002',
        name: 'Data Protection Policy',
        version: '2.0',
        category: 'Privacy',
        framework: 'GDPR',
        status: 'Under Review',
        createdBy: 'Sarah Johnson',
        createdOn: '2023-11-03',
        subpolicies: [
          {
            name: 'Data Subject Rights Procedure',
            version: '1.2',
            status: 'Under Review',
            description: 'Procedures for handling data subject access requests and other rights.'
          }
        ]
      },
      {
        id: 'POL-003',
        name: 'Acceptable Use Policy',
        version: '1.0',
        category: 'HR',
        framework: 'ISO 27001',
        status: 'Rejected',
        createdBy: 'Michael Brown',
        createdOn: '2023-09-21'
      },
      {
        id: 'POL-004',
        name: 'Access Control Policy',
        version: '1.1',
        category: 'Security',
        framework: 'NIST',
        status: 'Scheduled',
        createdBy: 'Emma Davis',
        createdOn: '2023-12-05',
        subpolicies: [
          {
            name: 'Password Management Standard',
            version: '1.0',
            status: 'Scheduled',
            description: 'Standards for creating, managing, and securing passwords across organizational systems.'
          },
          {
            name: 'Privileged Access Management',
            version: '1.0',
            status: 'Scheduled',
            description: 'Guidelines for managing and monitoring privileged access to systems and data.'
          }
        ]
      },
      {
        id: 'POL-005',
        name: 'Risk Management Policy',
        version: '1.3',
        category: 'Governance',
        framework: 'SOC 2',
        status: 'Under Review',
        createdBy: 'David Wilson',
        createdOn: '2023-11-18'
      },
      {
        id: 'POL-006',
        name: 'Business Continuity Policy',
        version: '2.1',
        category: 'Operations',
        framework: 'ISO 27001',
        status: 'Approved',
        createdBy: 'Jennifer Lee',
        createdOn: '2023-10-30'
      },
      {
        id: 'POL-007',
        name: 'Third-Party Risk Policy',
        version: '1.0',
        category: 'Vendor',
        framework: 'NIST',
        status: 'Rejected',
        createdBy: 'Robert Taylor',
        createdOn: '2023-09-12'
      },
      {
        id: 'POL-008',
        name: 'Physical Security Policy',
        version: '1.4',
        category: 'Security',
        framework: 'SOC 2',
        status: 'Scheduled',
        createdBy: 'Lisa Martinez',
        createdOn: '2023-12-10'
      }
    ]
    
    const filteredPolicies = computed(() => {
      // Map tab IDs to status values
      const statusMap = {
        'rejected': 'Rejected',
        'scheduled': 'Scheduled',
        'under-review': 'Under Review',
        'approved': 'Approved'
      }
      
      return policies.filter(policy => {
        const matchesStatus = policy.status === statusMap[activeTab.value]
        const matchesFramework = selectedFramework.value === '' || policy.framework === selectedFramework.value
        
        return matchesStatus && matchesFramework
      })
    })
    
    const toggleSubpolicies = (policyId) => {
      if (expandedPolicies.value.includes(policyId)) {
        expandedPolicies.value = expandedPolicies.value.filter(id => id !== policyId)
      } else {
        expandedPolicies.value.push(policyId)
      }
    }
    
    const togglePolicyDocument = (policyId) => {
      if (expandedDocuments.value.includes(policyId)) {
        expandedDocuments.value = expandedDocuments.value.filter(id => id !== policyId)
      } else {
        expandedDocuments.value.push(policyId)
      }
    }
    
    const toggleSubpolicyDocument = (subpolicyId) => {
      if (expandedDocuments.value.includes(subpolicyId)) {
        expandedDocuments.value = expandedDocuments.value.filter(id => id !== subpolicyId)
      } else {
        expandedDocuments.value.push(subpolicyId)
      }
    }
    
    const getPolicyStatusLabel = (status) => {
      // Map original statuses to Active/Inactive
      switch(status) {
        case 'Approved':
        case 'Under Review':
          return 'Active';
        case 'Rejected':
        case 'Scheduled':
        default:
          return 'Inactive';
      }
    }
    
    const getPolicyStatusClass = (status) => {
      // Map original statuses to active/inactive classes
      switch(status) {
        case 'Approved':
        case 'Under Review':
          return 'active';
        case 'Rejected':
        case 'Scheduled':
        default:
          return 'inactive';
      }
    }
    
    return {
      activeTab,
      selectedFramework,
      tabs,
      policies,
      filteredPolicies,
      expandedPolicies,
      expandedDocuments,
      toggleSubpolicies,
      togglePolicyDocument,
      toggleSubpolicyDocument,
      getPolicyStatusLabel,
      getPolicyStatusClass
    }
  }
}
</script> 