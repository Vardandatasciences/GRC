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
        <div @click="handleDashboardClick" class="menu-item has-submenu" :class="{'expanded': openMenus.dashboard}">
          <i class="fas fa-th-large icon"></i>
          <span>Dashboard</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.dashboard" class="submenu">
          <div @click="toggleSubmenu('performance')" class="menu-item has-submenu" :class="{'expanded': openMenus.performance}">
            <i class="fas fa-chart-line icon"></i>
            <span>Performance Analytics</span>
            <i class="fas fa-chevron-right submenu-arrow"></i>
          </div>
          <div v-if="!isCollapsed && openMenus.performance" class="submenu">
            <div class="menu-item" @click="navigate('/policy/performance/kpi')">
              <i class="fas fa-tachometer-alt icon"></i>
              <span>KPIs Analysis</span>
            </div>
            <div class="menu-item" @click="navigate('/policy/performance/dashboard')">
              <i class="fas fa-th icon"></i>
              <span>Dashboard</span>
            </div>
          </div>
          <div class="menu-item" @click="navigate('/policy/approver')">
            <i class="fas fa-user-check icon"></i>
            <span>Policy Approver</span>
          </div>
        </div>
        
        <!-- Policies submenu -->
        <div @click="toggleSubmenu('policyManagement')" class="menu-item has-submenu" :class="{'expanded': openMenus.policyManagement}">
          <i class="fas fa-check-square icon"></i>
          <span>Policy</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.policyManagement" class="submenu">
          <!-- Policies List with subdropdown -->
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
            <div class="menu-item" @click="navigate('/policies-list/active')">
              <i class="fas fa-check-circle icon"></i>
              <span>Active Policies</span>
            </div>
          </div>
          
          <!-- Create Policy with subdropdown -->
          <div @click="toggleSubmenu('createPolicy')" class="menu-item has-submenu" :class="{'expanded': openMenus.createPolicy}">
            <i class="fas fa-plus-square icon"></i>
            <span>Policy Creation</span>
            <i class="fas fa-chevron-right submenu-arrow"></i>
          </div>
          <div v-if="!isCollapsed && openMenus.createPolicy" class="submenu">
            <div class="menu-item" @click="navigate('/create-policy/new')">
              <i class="fas fa-file-medical icon"></i>
              <span>Create Policy</span>
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
          
          <div class="menu-item" @click="navigate('/tree-policies')">
            <i class="fas fa-sitemap icon"></i>
            <span>Tree Policies</span>
          </div>
        </div>
      </div>


      <!-- Compliance Section -->
      <div @click="toggleSubmenu('compliance')" class="menu-item">
        <i class="fas fa-balance-scale icon"></i>
        <span v-if="!isCollapsed">Compliance</span>
      </div>
      <div v-if="!isCollapsed && openMenus.compliance" class="submenu">
        <div @click="toggleSubmenu('complianceDashboard')" class="menu-item has-submenu" :class="{'expanded': openMenus.complianceDashboard}">
          <i class="fas fa-th-large icon"></i>
          <span>Dashboard</span>
          <i class="fas fa-chevron-right submenu-arrow"></i>
        </div>
        <div v-if="!isCollapsed && openMenus.complianceDashboard" class="submenu">
          <div class="menu-item" @click="navigate('/compliance/approver')">
            <i class="fas fa-user-check icon"></i>
            <span>Compliance Approver</span>
          </div>
        </div>
        <div class="menu-item" @click="navigate('/compliance/task')">
          <i class="fas fa-check-square icon"></i>
          <span>Tasks</span>
        </div>
        <div class="menu-item" @click="navigate('/compliance/audit')">
          <i class="fas fa-check-square icon"></i>
          <span>Audit</span>
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

      <!-- Auditor Section -->
      <div @click="toggleSubmenu('auditor')" class="menu-item">
        <i class="fas fa-user-tie icon"></i>
        <span v-if="!isCollapsed">Auditor</span>
      </div>
      <div v-if="!isCollapsed && openMenus.auditor" class="submenu">
        <div class="menu-item" @click="navigate('/auditor/dashboard')">
          <i class="fas fa-th-large icon"></i>
          <span>User Dashboard</span>
        </div>
        <div class="menu-item" @click="navigate('/auditor/assign')">
          <i class="fas fa-check-square icon"></i>
          <span>Assign Audit</span>
        </div>
        <div class="menu-item" @click="navigate('/auditor/reviewer')">
          <i class="fas fa-user icon"></i>
          <span>Reviewer</span>
        </div>
      </div>

      <!-- Incident Section -->
      <div @click="toggleSubmenu('incident')" class="menu-item">
        <i class="fas fa-exclamation-circle icon"></i>
        <span v-if="!isCollapsed">Incident</span>
      </div>
      <div v-if="!isCollapsed && openMenus.incident" class="submenu">
        <div @click="toggleSubmenu('incidentManagement')" class="menu-item has-submenu" :class="{'expanded': openMenus.incidentManagement}">
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
        <div @click="toggleSubmenu('incidentPerformance')" class="menu-item has-submenu" :class="{'expanded': openMenus.incidentPerformance}">
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
      compliance: false,
      risk: false,
      auditor: false,
      incident: false,
      dashboard: false,
      complianceDashboard: false,
      policyManagement: false,
      policiesList: false,
      createPolicy: false,
      performance: false,
      incidentManagement: false,
      incidentPerformance: false
    })

    const toggleCollapse = () => {
      isCollapsed.value = !isCollapsed.value
    }

    const toggleSubmenu = (section) => {
      openMenus.value[section] = !openMenus.value[section]
    }

    const handleDashboardClick = () => {
      toggleSubmenu('dashboard')
      if (!openMenus.value.dashboard) {
        router.push('/policy/dashboard')
      }
    }

    const navigate = (path) => {
      router.push(path)
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