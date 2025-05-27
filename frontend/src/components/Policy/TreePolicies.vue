<template>
  <div :class="['tree-policies-container', { 'sidebar-collapsed': isSidebarCollapsed }]">
    <!-- Loading Overlay -->
    <div v-if="loading" class="tree-loading-overlay">
      <div class="tree-loading-spinner"></div>
      <p>Loading...</p>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="tree-error-message">
      {{ error }}
      <button class="tree-close-btn" @click="error = null">✕</button>
    </div>

    <!-- Header with controls -->
    <div class="tree-header">
      <select v-model="treeSelectedFramework" class="tree-framework-select" :disabled="loading">
        <option value="" disabled>Select Framework</option>
        <option v-for="fw in treeFrameworks" :key="fw.id" :value="fw.title">{{ fw.title }}</option>
      </select>
      <button v-if="treeSelectedFramework" class="tree-expand-btn" @click="expandAllTree" :disabled="loading">
        <i class="fas fa-expand-alt" style="margin-right: 8px;"></i>Expand All
      </button>
    </div>

    <!-- Tree Content -->
    <div class="org-tree-content">
      <div v-if="treeSelectedFramework" class="org-tree-center">
        <!-- Framework Node -->
        <div class="org-tree-framework-row">
          <div class="org-tree-framework-node" ref="frameworkNode">
            <span>{{ treeSelectedFramework }}</span>
            <span v-if="!showPolicies" class="org-tree-arrow-down clickable" @click="togglePolicies">
              <i class="fas fa-chevron-down"></i>
            </span>
          </div>
        </div>
        
        <!-- Policies Row -->
        <transition name="fade-slide">
          <div v-if="showPolicies" class="org-tree-policies-row" ref="policiesRow">
            <div v-for="(policy, pIdx) in treePolicies" :key="policy.id" class="org-tree-policy-block">
              <div class="org-tree-policy-node">
                <span>{{ policy.title }}</span>
                <span v-if="!expandedPolicies[pIdx] && policy.subPolicies?.length" class="org-tree-arrow-down clickable" @click="togglePolicyExpand(pIdx)">
                  <i class="fas fa-chevron-down"></i>
                </span>
              </div>
              <transition name="fade-slide">
                <div v-if="expandedPolicies[pIdx] && policy.subPolicies?.length" class="org-tree-subpolicies-row">
                  <div class="org-tree-subpolicies-blocks">
                    <div v-for="sub in policy.subPolicies" :key="sub.id" class="org-tree-subpolicy-block">
                      <div class="org-tree-subpolicy-node">
                        <span>{{ sub.title }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, inject, watch } from 'vue'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

export default {
  name: 'TreePolicies',
  setup() {
    // Define SVG constants as refs
    const svgWidth = ref(700)
    const svgPolicyLineHeight = ref(60)
    const svgSubWidth = ref(260)
    const svgSubLineHeight = ref(50)

    const treeSelectedFramework = ref('')
    const showPolicies = ref(false)
    const expandedPolicies = ref({})
    const isSidebarCollapsed = ref(false)
    const loading = ref(false)
    const error = ref(null)
    
    // Data refs
    const frameworks = ref([])
    const selectedFrameworkData = ref(null)
    
    // Try to inject the sidebar collapsed state if available
    try {
      const sidebarState = inject('sidebarCollapsed', null)
      if (sidebarState !== null) {
        watch(sidebarState, (newVal) => {
          isSidebarCollapsed.value = newVal
        }, { immediate: true })
      }
    } catch (e) {
      console.log('Sidebar state not available for injection')
    }

    // Fetch frameworks
    const fetchFrameworks = async () => {
      try {
        loading.value = true
        error.value = null
        const response = await axios.get(`${API_BASE_URL}/frameworks/`)
        frameworks.value = response.data.map(fw => ({
          id: fw.FrameworkId,
          title: fw.FrameworkName
        }))
      } catch (err) {
        console.error('Error fetching frameworks:', err)
        error.value = 'Failed to fetch frameworks'
      } finally {
        loading.value = false
      }
    }

    // Fetch framework details including policies
    const fetchFrameworkDetails = async (frameworkId) => {
      try {
        loading.value = true
        error.value = null
        const response = await axios.get(`${API_BASE_URL}/frameworks/${frameworkId}/`)
        selectedFrameworkData.value = response.data
      } catch (err) {
        console.error('Error fetching framework details:', err)
        error.value = 'Failed to fetch framework details'
      } finally {
        loading.value = false
      }
    }

    // Watch for framework selection changes
    watch(treeSelectedFramework, async (newFramework) => {
      if (newFramework) {
        const framework = frameworks.value.find(f => f.title === newFramework)
        if (framework) {
          await fetchFrameworkDetails(framework.id)
        }
      } else {
        selectedFrameworkData.value = null
      }
    })

    const treeFrameworks = computed(() => frameworks.value)
    
    const treePolicies = computed(() => {
      if (!selectedFrameworkData.value) return []
      
      return selectedFrameworkData.value.policies.map(policy => ({
        title: policy.PolicyName,
        id: policy.PolicyId,
        subPolicies: policy.subpolicies.map(sub => ({
          title: sub.SubPolicyName,
          id: sub.SubPolicyId
        }))
      }))
    })
    
    // Set default framework on mount
    onMounted(async () => {
      await fetchFrameworks()
      if (frameworks.value.length > 0) {
        treeSelectedFramework.value = frameworks.value[0].title
      }
      
      // Check if sidebar is collapsed on mount
      const sidebar = document.querySelector('.sidebar')
      if (sidebar && sidebar.classList.contains('collapsed')) {
        isSidebarCollapsed.value = true
      }
    })
    
    function togglePolicies() { 
      showPolicies.value = !showPolicies.value 
    }
    
    function togglePolicyExpand(idx) {
      expandedPolicies.value = { 
        ...expandedPolicies.value, 
        [idx]: !expandedPolicies.value[idx] 
      }
    }
    
    function expandAllTree() {
      showPolicies.value = true
      const all = {}
      treePolicies.value.forEach((_, idx) => { all[idx] = true })
      expandedPolicies.value = all
    }

    function getPolicyX(idx) {
      // Spread policies evenly
      const count = treePolicies.value.length
      if (count === 1) return svgWidth.value/2
      const gap = svgWidth.value/(count+1)
      return gap*(idx+1)
    }
    
    function getSubX(count, idx) {
      if (count === 1) return svgSubWidth.value/2
      const gap = svgSubWidth.value/(count+1)
      return gap*(idx+1)
    }

    // Adjust Y coordinates for SVG lines to connect to node edges
    const frameworkNodeHeight = 48 + 16 // node height + padding
    const policyNodeHeight = 40 + 12 // node height + padding
    
    // For framework to policy
    function getFrameworkToPolicyY1() { return frameworkNodeHeight }
    function getFrameworkToPolicyY2() { return svgPolicyLineHeight.value - 8 }
    
    // For policy to subpolicy
    function getPolicyToSubY1() { return policyNodeHeight }
    function getPolicyToSubY2() { return svgSubLineHeight.value - 8 }

    return {
      treeSelectedFramework,
      showPolicies,
      expandedPolicies,
      treeFrameworks,
      treePolicies,
      togglePolicies,
      togglePolicyExpand,
      expandAllTree,
      isSidebarCollapsed,
      loading,
      error,
      getPolicyX,
      getSubX,
      getFrameworkToPolicyY1,
      getFrameworkToPolicyY2,
      getPolicyToSubY1,
      getPolicyToSubY2,
      svgWidth,
      svgPolicyLineHeight,
      svgSubWidth,
      svgSubLineHeight
    }
  }
}
</script>

<style scoped>
@import './TreePolicies.css';
</style> 