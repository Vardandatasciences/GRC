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
        <div class="menu-item" @click="navigate('/policy/notifications')">
          <i class="fas fa-bell icon"></i>
          <span>Notifications</span>
        </div>
      </div>

      <!-- Compliance Section -->
      <div @click="toggleSubmenu('compliance')" class="menu-item">
        <i class="fas fa-balance-scale icon"></i>
        <span v-if="!isCollapsed">Compliance</span>
      </div>
      <div v-if="!isCollapsed && openMenus.compliance" class="submenu">
        <div class="menu-item" @click="navigate('/compliance/dashboard')">
          <i class="fas fa-th-large icon"></i>
          <span>Dashboard</span>
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
        <div class="menu-item">
          <i class="fas fa-th-large icon"></i>
          <span>Dashboard</span>
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
          <span>Audits</span>
        </div>
        <div class="menu-item" @click="navigate('/auditor/assign')">
          <i class="fas fa-check-square icon"></i>
          <span>Assign Audit</span>
        </div>
        <div class="menu-item" @click="navigate('/auditor/reviews')">
          <i class="fas fa-tasks icon"></i>
          <span>Review Audits</span>
        </div>
        <div class="menu-item" @click="navigate('/auditor/reports')">
          <i class="fas fa-file-alt icon"></i>
          <span>Audit Reports</span>
        </div>
        <div class="menu-item" @click="navigate('/auditor/reviewer')">
          <i class="fas fa-user icon"></i>
          <span>Reviewer</span>
        </div>
        <div class="menu-item" @click="toggleSubmenu('performance')">
          <i class="fas fa-chart-bar icon"></i>
          <span>Performance Analysis</span>
        </div>
        <div v-if="openMenus.performance" class="sub-submenu">
          <div class="menu-item" @click="navigate('/auditor/performance/kpis')">
            <i class="fas fa-tachometer-alt icon"></i>
            <span>KPIs Analysis</span>
          </div>
          <div class="menu-item" @click="navigate('/auditor/performance/dashboard')">
            <i class="fas fa-chart-line icon"></i>
            <span>Dashboard</span>
          </div>
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
          <i class="fas fa-check-square icon"></i>
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
      risk: false,
      auditor: false,
      incident: false,
      performance: false
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