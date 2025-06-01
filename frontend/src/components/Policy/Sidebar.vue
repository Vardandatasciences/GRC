<template>
  <div :class="['sidebar', { collapsed: isCollapsed }]">
    <div class="logo-container">
      <img :src="logo" alt="GRC Logo" class="logo-image" />
      <span v-if="!isCollapsed" class="logo-text">GRC</span>
      <span class="toggle" @click="toggleCollapse">
        {{ isCollapsed ? '»' : '«' }}
      </span>
    </div>

    <div class="menu">
      <!-- Policy Section -->
      <div @click="toggleSubmenu('policy')" class="menu-item has-submenu" :class="{'expanded': openMenus.policy}">
        <i class="fas fa-file-alt icon"></i>
        <span v-if="!isCollapsed">Policy</span>
        <i v-if="!isCollapsed" class="fas fa-chevron-right submenu-arrow"></i>
      </div>
      <div v-if="!isCollapsed && openMenus.policy" class="submenu">
        <!-- 1. Policy Creation -->
        <div @click="toggleSubmenu('policyCreation')" class="menu-item has-submenu" :class="{'expanded': openMenus.policyCreation}">
          <i class="fas fa-plus-square icon"></i>
          <span>Policy Creation</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.policyCreation" class="submenu">
          <div class="menu-item" @click="navigate('/create-policy/create')">
            <i class="fas fa-plus icon"></i>
            <span>Create Policy</span>
          </div>
          <div class="menu-item" @click="navigate('/create-policy/framework')">
            <i class="fas fa-sitemap icon"></i>
            <span>Create Framework</span>
          </div>
          <div class="menu-item" @click="navigate('/create-policy/tailoring')">
            <i class="fas fa-edit icon"></i>
            <span>Tailoring & Templating</span>
          </div>
          <div class="menu-item" @click="navigate('/create-policy/versioning')">
            <i class="fas fa-code-branch icon"></i>
            <span>Versioning</span>
          </div>
        </div>

        <!-- 2. Policies List -->
        <div @click="toggleSubmenu('policiesList')" class="menu-item has-submenu" :class="{'expanded': openMenus.policiesList}">
          <i class="fas fa-list icon"></i>
          <span>Policies List</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.policiesList" class="submenu">
          <div class="menu-item" @click="navigate('/policies-list/all')">
            <i class="fas fa-list-alt icon"></i>
            <span>All Policies</span>
          </div>
          <div class="menu-item" @click="navigate('/tree-policies')">
            <i class="fas fa-sitemap icon"></i>
            <span>Tree Policies</span>
          </div>
        </div>
        
        <div @click="navigate('/framework-explorer')" class="menu-item">
            <i class="fas fa-cubes icon"></i>
            <span>Framework Explorer</span>
          </div>

        <!-- 3. Policy Approval -->
        <div class="menu-item" @click="navigate('/policy/approval')">
          <i class="fas fa-check-circle icon"></i>
          <span>Policy Approval</span>
        </div>
        <div class="menu-item" @click="navigate('/framework-approval')">
          <i class="fas fa-check-circle icon"></i>
          <span>Framework Approval</span>
        </div>

        <!-- 4. Performance Analysis -->
        <div @click="toggleSubmenu('performanceAnalysis')" class="menu-item has-submenu" :class="{'expanded': openMenus.performanceAnalysis}">
          <i class="fas fa-chart-line icon"></i>
          <span>Performance Analysis</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.performanceAnalysis" class="submenu">
          <div class="menu-item" @click="navigate('/policy/performance/kpis')">
            <i class="fas fa-chart-bar icon"></i>
            <span>KPIs Analysis</span>
          </div>
          <div class="menu-item" @click="navigate('/policy/performance/dashboard')">
            <i class="fas fa-tachometer-alt icon"></i>
            <span>User Dashboard</span>
          </div>
        </div>
      </div>
      
      <!-- Compliances Section -->
      <div @click="toggleSubmenu('compliances')" class="menu-item has-submenu" :class="{'expanded': openMenus.compliances}">
        <i class="fas fa-list-alt icon"></i>
        <span v-if="!isCollapsed">Compliances</span>
        <i v-if="!isCollapsed" class="fas fa-chevron-right submenu-arrow"></i>
      </div>
      <div v-if="!isCollapsed && openMenus.compliances" class="submenu">
        <!-- 1. Compliances View -->
        <div @click.stop="toggleSubmenu('compliancesView')" class="menu-item has-submenu" :class="{'expanded': openMenus.compliancesView}">
          <i class="fas fa-list-alt icon"></i>
          <span>Compliances View</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="openMenus.compliancesView" class="submenu">
          <div class="menu-item" @click="navigate('/compliance/list')">
            <i class="fas fa-clipboard-list icon"></i>
            <span>Compliances List</span>
          </div>
          <div class="menu-item" @click="navigate('/compliance/approver')">
            <i class="fas fa-check-circle icon"></i>
            <span>Compliance Approval</span>
          </div>
        </div>

        <!-- 2. Compliance Creation -->
        <div @click.stop="toggleSubmenu('complianceCreation')" class="menu-item has-submenu" :class="{'expanded': openMenus.complianceCreation}">
          <i class="fas fa-plus-square icon"></i>
          <span>Compliance Creation</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="openMenus.complianceCreation" class="submenu">
          <div class="menu-item" @click="navigate('/compliance/create')">
            <i class="fas fa-file-alt icon"></i>
            <span>Create Compliance</span>
          </div>
          <div class="menu-item" @click="navigate('/compliance/versioning')">
            <i class="fas fa-code-branch icon"></i>
            <span>Tailoring & Templating</span>
          </div>
        </div>

        <!-- 3. Performance Analysis -->
        <div @click.stop="toggleSubmenu('compliancesPerformanceAnalysis')" class="menu-item has-submenu" :class="{'expanded': openMenus.compliancesPerformanceAnalysis}">
          <i class="fas fa-chart-line icon"></i>
          <span>Performance Analysis</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="openMenus.compliancesPerformanceAnalysis" class="submenu">
          <div class="menu-item" @click="navigate('/compliance/kpi-dashboard')">
            <i class="fas fa-chart-bar icon"></i>
            <span>KPIs Dashboard</span>
          </div>
          <div class="menu-item" @click="navigate('/compliance/user-dashboard')">
            <i class="fas fa-tachometer-alt icon"></i>
            <span>User Dashboard</span>
          </div>
        </div>
      </div>
    
      <!-- Incident Section -->
<div 
  @click="toggleSubmenu('incident')" 
  class="menu-item has-submenu" 
  :class="{'expanded': openMenus.incident}"
>
  <i class="fas fa-file-alt icon"></i>
  <span v-if="!isCollapsed">Incident</span>
  <i v-if="!isCollapsed" class="fas fa-chevron-right submenu-arrow"></i> <!-- Arrow icon added -->
</div>

<div v-if="!isCollapsed && openMenus.incident" class="submenu">
  <!-- Incident Management -->
  <div 
    @click="toggleSubmenu('incidentManagement')" 
    class="menu-item has-submenu" 
    :class="{'expanded': openMenus.incidentManagement}"
  >
    <i class="fas fa-clipboard-list icon"></i>
    <span>Incident Management</span>
    <i class="fas fa-chevron-right submenu-arrow"></i>
  </div>
  <div v-if="!isCollapsed && openMenus.incidentManagement" class="submenu">
    <div class="menu-item" @click="navigate('/incident/incident')">
      <i class="fas fa-list icon"></i>
      <span>Incident List</span>
    </div>
    <div class="menu-item" @click="navigate('/incident/create')">
      <i class="fas fa-plus icon"></i>
      <span>Create Incident</span>
    </div>
  </div>

  <!-- Incident Performance -->
  <div 
    @click="toggleSubmenu('incidentPerformance')" 
    class="menu-item has-submenu" 
    :class="{'expanded': openMenus.incidentPerformance}"
  >
    <i class="fas fa-chart-line icon"></i>
    <span>Performance Analysis</span>
    <i class="fas fa-chevron-right submenu-arrow"></i>
  </div>
  <div v-if="!isCollapsed && openMenus.incidentPerformance" class="submenu">
    <div class="menu-item" @click="navigate('/incident/dashboard')">
      <i class="fas fa-chart-pie icon"></i>
      <span>KPIs Analysis</span>
    </div>
    <div class="menu-item" @click="navigate('/incident/performance/dashboard')">
      <i class="fas fa-tachometer-alt icon"></i>
      <span>Dashboard</span>
    </div>
  </div>
</div>


<!-- Risk Section -->
<div @click="toggleSubmenu('risk')" class="menu-item">
        <i class="fas fa-exclamation-triangle icon"></i>
        <span v-if="!isCollapsed">Risk</span>
      </div>
      <div v-if="!isCollapsed && openMenus.risk" class="submenu">
        <div class="menu-item" @click="navigate('/risk/riskdashboard')">
          <i class="fas fa-th-large icon"></i>
          <span>Dashboard</span>
        </div>
        <div class="menu-item" @click="navigate('/risk/riskregister')">
          <i class="fas fa-plus icon"></i>
          <span>Risk Register</span>
        </div>
        <div class="menu-item" @click="navigate('/risk/riskinstances')">
          <i class="fas fa-th-list icon"></i>
          <span>Instances</span>
        </div>
        <div class="menu-item" @click="navigate('/risk/notifications')">
          <i class="fas fa-bell icon"></i>
          <span>Notifications</span>
        </div>
        <div class="menu-item" @click="navigate('/risk/workflow')">
          <i class="fas fa-tasks icon"></i>
          <span>Risk Workflow</span>
        </div>
        <div class="menu-item" @click="navigate('/risk/user-tasks')">
          <i class="fas fa-user-check icon"></i>
          <span>User Tasks</span>
        </div>
      </div>

   
    </div>
    <div class="bottom-profile">
      <i class="fas fa-user icon"></i>
      <span v-if="!isCollapsed">User Profile</span>
    </div>
    </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import logo from '../../assets/grc_logo1.png'
import '@fortawesome/fontawesome-free/css/all.min.css'

export default {
  name: 'PolicySidebar',
  setup() {
    const router = useRouter()
    const isCollapsed = ref(false)
    const openMenus = ref({
      policy: false,
      policyCreation: false,
      policiesList: false,
      performanceAnalysis: false,
      compliance: false,
      risk: false,
      auditor: false,
      incident: false,
      compliances: false,
      compliancesView: false,
      complianceCreation: false,
      compliancesPerformanceAnalysis: false
    })

    const toggleCollapse = () => {
      isCollapsed.value = !isCollapsed.value
    }

    const toggleSubmenu = (section) => {
      openMenus.value[section] = !openMenus.value[section]
    }

    const navigate = (path) => {
      router.push(path)
    }

    const handleDashboardClick = () => {
      toggleSubmenu('dashboard')
      navigate('/policy/dashboard')
    }

    return {
      isCollapsed,
      openMenus,
      logo,
      toggleCollapse,
      toggleSubmenu,
      navigate,
      handleDashboardClick
    }
  }
}
</script>

<style scoped>
/* Import the existing CSS file */
@import './sidebar.css';
</style> 