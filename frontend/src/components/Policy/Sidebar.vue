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
      <div @click="toggleSubmenu('policy')" class="menu-item">
        <i class="fas fa-file-alt icon"></i>
        <span v-if="!isCollapsed">Policy</span>
      </div>
      <div v-if="!isCollapsed && openMenus.policy" class="submenu">
        <div class="menu-item" @click="navigate('/policy/dashboard')">
          <i class="fas fa-th-large icon"></i>
          <span>Dashboard</span>
        </div>
        <div class="menu-item" @click="navigate('/create-policy')">
          <i class="fas fa-check-square icon"></i>
          <span>Policy</span>
        </div>
        <div class="menu-item" @click="navigate('/policy/performance')">
          <i class="fas fa-chart-line icon"></i>
          <span>Performance</span>
        </div>
      </div>

      <!-- Compliance Section -->
      <div @click="toggleSubmenu('compliance')" class="menu-item">
        <i class="fas fa-balance-scale icon"></i>
        <span v-if="!isCollapsed">Compliance</span>
      </div>
      <div v-if="!isCollapsed && openMenus.compliance" class="submenu">
        <!-- 1. Compliances -->
        <div @click="toggleSubmenu('compliancesList')" class="menu-item has-submenu">
          <i class="fas fa-list-alt icon"></i>
          <span>Compliances</span>
        </div>
        <div v-if="openMenus.compliancesList" class="submenu">
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
        <div @click="toggleSubmenu('complianceCreation')" class="menu-item has-submenu">
          <i class="fas fa-plus-square icon"></i>
          <span>Compliance Creation</span>
        </div>
        <div v-if="openMenus.complianceCreation" class="submenu">
          <div class="menu-item" @click="navigate('/compliance/create')">
            <i class="fas fa-file-alt icon"></i>
            <span>Create Compliance</span>
          </div>
          <div class="menu-item" @click="navigate('/compliance/tailoring')">
            <i class="fas fa-cut icon"></i>
            <span>Tailoring & Templating</span>
          </div>
          <div class="menu-item" @click="navigate('/compliance/versioning')">
            <i class="fas fa-code-branch icon"></i>
            <span>Versioning</span>
          </div>
        </div>

        <!-- 3. Performance Analysis -->
        <div @click="toggleSubmenu('performanceAnalysis')" class="menu-item has-submenu">
          <i class="fas fa-chart-line icon"></i>
          <span>Performance Analysis</span>
        </div>
        <div v-if="openMenus.performanceAnalysis" class="submenu">
          <div class="menu-item" @click="navigate('/compliance/kpi-dashboard')">
            <i class="fas fa-tachometer-alt icon"></i>
            <span>KPIs Dashboard</span>
          </div>
          <div class="menu-item" @click="navigate('/compliance/user-dashboard')">
            <i class="fas fa-user-chart icon"></i>
            <span>User Dashboard</span>
          </div>
        </div>
      </div>

      <!-- Risk Section -->
      <div @click="toggleSubmenu('risk')" class="menu-item">
        <i class="fas fa-exclamation-triangle icon"></i>
        <span v-if="!isCollapsed">Risk</span>
      </div>
      <div v-if="!isCollapsed && openMenus.risk" class="submenu">
        <div class="menu-item" @click="navigate('/risk/dashboard')">
          <i class="fas fa-th-large icon"></i>
          <span>Dashboard</span>
        </div>
        <div class="menu-item" @click="navigate('/risk/create')">
          <i class="fas fa-plus icon"></i>
          <span>Create Risk</span>
        </div>
        <div class="menu-item" @click="navigate('/risk/instances')">
          <i class="fas fa-th-list icon"></i>
          <span>Instances</span>
        </div>
        <div class="menu-item" @click="navigate('/risk/notifications')">
          <i class="fas fa-bell icon"></i>
          <span>Notifications</span>
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
        <div class="menu-item" @click="navigate('/incident/dashboard')">
          <i class="fas fa-th-large icon"></i>
          <span>Dashboard</span>
        </div>
        <div class="menu-item" @click="navigate('/incident/create')">
          <i class="fas fa-plus icon"></i>
          <span>Create Incident</span>
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
      compliancesList: false,
      complianceCreation: false,
      performanceAnalysis: false,
      risk: false,
      auditor: false,
      incident: false
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

    return {
      isCollapsed,
      openMenus,
      logo,
      toggleCollapse,
      toggleSubmenu,
      navigate
    }
  }
}

</script>

<style scoped>
/* Import the existing CSS file */
@import './sidebar.css';
</style> 