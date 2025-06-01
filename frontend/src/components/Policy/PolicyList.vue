<template>
  <div class="policy-list-container">
    <!-- Search Bar -->
    <div class="search-bar">
      <div class="search-container">
        <i class="fas fa-search search-icon"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search Policy..." 
        />
      </div>
      <div class="button-group">
        <button class="create-framework-btn" @click="$emit('show-framework-form')">
          <i class="fas fa-plus icon"></i> Create Framework
        </button>
        <button class="create-policy-btn" @click="$emit('create-policy')">
          <i class="fas fa-plus icon"></i> Create Policy
        </button>
      </div>
    </div>

    <!-- Framework Dropdown -->
    <div class="framework-dropdown">
      <select v-model="selectedFramework" @change="handleFrameworkChange">
        <option value="ISO 27001">ISO 27001</option>
        <option value="NIST">NIST</option>
      </select>
    </div>
    
    <!-- Policy Table -->
    <div class="policy-list-container">
      <table class="policy-table">
        <thead>
          <tr>
            <th>Policy Name</th>
            <th>Version</th>
            <th>Category</th>
            <th>Framework</th>
            <th>Status</th>
            <th>Created By</th>
            <th>Authorized By</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="policy in paginatedPolicies" :key="`${policy.name}-${policy.version}`">
            <!-- Main Policy Row -->
            <tr class="main-policy-row">
              <td>{{ policy.name }}</td>
              <td>
                <div class="version-dropdown">
                  <select
                    :value="selectedVersions[policy.name]"
                    @change="handleVersionChange(policy.name, $event.target.value)"
                  >
                    <option 
                      v-for="version in groupedPolicies[policy.name]" 
                      :key="version.version" 
                      :value="version.version"
                    >
                      {{ version.version }}
                    </option>
                  </select>
                  <i class="fas fa-chevron-down dropdown-icon"></i>
                </div>
              </td>
              <td>{{ policy.category }}</td>
              <td>{{ policy.framework }}</td>
              <td>
                <span :class="['status-badge', `status-${policy.status.toLowerCase().replace(' ', '-')}`]">
                  {{ policy.status }}
                </span>
              </td>
              <td>{{ policy.createdBy }}</td>
              <td>{{ policy.authorizedBy }}</td>
            </tr>
            <!-- Subpolicies Rows -->
            <tr 
              v-for="(subPolicy, index) in policy.subPolicies" 
              :key="`${subPolicy.id}-${index}`" 
              class="sub-policy-row"
            >
              <td class="sub-policy-cell">
                <div class="sub-policy-indicator"></div>
                {{ subPolicy.name }}
              </td>
              <td>{{ subPolicy.version }}</td>
              <td>{{ policy.category }}</td>
              <td>{{ policy.framework }}</td>
              <td>
                <span :class="['status-badge', `status-${subPolicy.status.toLowerCase().replace(' ', '-')}`]">
                  {{ subPolicy.status }}
                </span>
              </td>
              <td>{{ subPolicy.createdBy }}</td>
              <td>{{ subPolicy.authorizedBy }}</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="policy-pagination">
      <span>{{ indexOfFirstPolicy + 1 }} - {{ Math.min(indexOfLastPolicy, currentPolicies.length) }} of {{ currentPolicies.length }}</span>
      <div>
        <button @click="prevPage" :disabled="currentPage === 1">Prev</button>
        <button @click="nextPage" :disabled="currentPage === totalPages">Next</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'PolicyList',
  emits: ['show-framework-form', 'create-policy'],
  setup() {
    const searchQuery = ref('')
    const currentPage = ref(1)
    const selectedVersions = ref({})
    const selectedFramework = ref('')

    const policiesPerPage = 4

    // Sample policies data
    const policies = [
      { 
        id: 'HR-001', 
        version: '1.0',
        name: 'Employee Code of Conduct',
        category: 'HR',
        status: 'Active',
        effectiveStartDate: '01/01/2024',
        effectiveEndDate: '31/12/2024',
        createdBy: 'John Doe',
        authorizedBy: 'Jane Smith',
        framework: 'ISO 27001',
        subPolicies: [
          {
            id: 'HR-001-SP1',
            name: 'Dress Code Policy',
            version: '1.0',
            status: 'Active',
            effectiveStartDate: '01/01/2024',
            effectiveEndDate: '31/12/2024',
            createdBy: 'John Doe',
            authorizedBy: 'Jane Smith'
          },
          {
            id: 'HR-001-SP2',
            name: 'Workplace Behavior Policy',
            version: '1.0',
            status: 'Active',
            effectiveStartDate: '01/01/2024',
            effectiveEndDate: '31/12/2024',
            createdBy: 'John Doe',
            authorizedBy: 'Jane Smith'
          }
        ]
      },
      // Additional policies can be added here
    ]

    // Group policies by name
    const groupedPolicies = computed(() => {
      return policies.reduce((acc, policy) => {
        if (!acc[policy.name]) {
          acc[policy.name] = []
        }
        acc[policy.name].push(policy)
        return acc
      }, {})
    })

    // Initialize selected versions
    onMounted(() => {
      const initialVersions = {}
      Object.keys(groupedPolicies.value).forEach(name => {
        if (groupedPolicies.value[name] && groupedPolicies.value[name].length > 0) {
          initialVersions[name] = groupedPolicies.value[name][0].version
        }
      })
      selectedVersions.value = initialVersions
    })

    const handleVersionChange = (policyName, version) => {
      selectedVersions.value = {
        ...selectedVersions.value,
        [policyName]: version
      }
    }

    const handleFrameworkChange = (e) => {
      selectedFramework.value = e.target.value
    }

    // Get current policies based on selected versions and search query
    const currentPolicies = computed(() => {
      return Object.entries(groupedPolicies.value)
        .filter(([name]) => name.toLowerCase().includes(searchQuery.value.toLowerCase()))
        .map(([name, versions]) => {
          const selectedVersion = selectedVersions.value[name]
          const policy = versions.find(v => v.version === selectedVersion)
          return policy || versions[0]
        })
        .filter(Boolean)
    })

    // Pagination Logic
    const indexOfLastPolicy = computed(() => currentPage.value * policiesPerPage)
    const indexOfFirstPolicy = computed(() => indexOfLastPolicy.value - policiesPerPage)
    const paginatedPolicies = computed(() => 
      currentPolicies.value.slice(indexOfFirstPolicy.value, indexOfLastPolicy.value)
    )
    const totalPages = computed(() => 
      Math.ceil(currentPolicies.value.length / policiesPerPage)
    )

    const nextPage = () => {
      if (currentPage.value < totalPages.value) currentPage.value++
    }

    const prevPage = () => {
      if (currentPage.value > 1) currentPage.value--
    }

    return {
      searchQuery,
      currentPage,
      selectedVersions,
      selectedFramework,
      policies,
      groupedPolicies,
      currentPolicies,
      paginatedPolicies,
      indexOfFirstPolicy,
      indexOfLastPolicy,
      totalPages,
      handleVersionChange,
      handleFrameworkChange,
      nextPage,
      prevPage
    }
  }
}
</script>

<style scoped>
@import './CreatePolicy.css';
</style> 