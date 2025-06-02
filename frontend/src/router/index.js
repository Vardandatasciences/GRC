import { createRouter, createWebHistory } from 'vue-router'
import PolicyDashboard from '../components/Policy/PolicyDashboard.vue'
import CreatePolicy from '../components/Policy/CreatePolicy.vue'
import PerformancePage from '../components/Policy/PerformancePage.vue'
import AssignAudit from '../components/Auditor/AssignAudit.vue'
import AuditorDashboard from '../components/Auditor/AuditorDashboard.vue'
import Reviewer from '../components/Auditor/Reviewer.vue'
import CreateIncident from '../components/Incident/CreateIncident.vue'
import IncidentDashboard from '../components/Incident/IncidentDashboard.vue'
import CreateCompliance from '../components/Compliance/CreateCompliance.vue'
import ComplianceApprover from '../components/Compliance/ComplianceApprover.vue'
import CreateRisk from '../components/Risk/CreateRisk.vue'
import Dashboard from '../components/Risk/Dashboard.vue'
import Instances from '../components/Risk/Instances.vue'
import Notifications from '../components/Risk/Notifications.vue'
import AllCompliance from '../components/Compliance/AllCompliance.vue'
import ComplianceDashboard from '../components/Compliance/ComplianceDashboard.vue'
import ComplianceTailoring from '../components/Compliance/ComplianceTailoring.vue'
import ComplianceVersioning from '../components/Compliance/ComplianceVersioning.vue'
import ComplianceKPI from '../components/Compliance/ComplianceKPI.vue'

const routes = [
  {
    path: '/',
    redirect: '/policy/dashboard'
  },
  {
    path: '/policy/dashboard',
    name: 'PolicyDashboard',
    component: PolicyDashboard
  },
  {
    path: '/create-policy',
    name: 'CreatePolicy',
    component: CreatePolicy
  },
  {
    path: '/policy/performance',
    name: 'PerformancePage',
    component: PerformancePage
  },
  {
    path: '/auditor/dashboard',
    name: 'AuditorDashboard',
    component: AuditorDashboard
  },
  {
    path: '/auditor/assign',
    name: 'AssignAudit',
    component: AssignAudit
  },
  {
    path: '/auditor/reviewer',
    name: 'AuditorReviewer',
    component: Reviewer
  },
  {
    path: '/incident/create',
    name: 'CreateIncident',
    component: CreateIncident
  },
  {
    path: '/incident/dashboard',
    name: 'IncidentDashboard',
    component: IncidentDashboard
  },
  {
    path: '/compliance/create',
    name: 'CreateCompliance',
    component: CreateCompliance
  },
  {
    path: '/compliance/approver',
    name: 'ComplianceApprover',
    component: ComplianceApprover
  },

  {
    path: '/compliance/list',
    name: 'AllCompliance',
    component: AllCompliance
  },
  {
    path: '/risk/create',
    name: 'CreateRisk',
    component: CreateRisk
  },
  {
    path: '/risk/dashboard',
    name: 'RiskDashboard',
    component: Dashboard
  },
  {
    path: '/risk/instances',
    name: 'RiskInstances',
    component: Instances
  },
  {
    path: '/risk/notifications',
    name: 'RiskNotifications',
    component: Notifications
  },
  {
    path: '/compliance/user-dashboard',
    name: 'ComplianceDashboard',
    component: ComplianceDashboard
  },
  {
    path: '/compliance/kpi-dashboard',  
    name: 'ComplianceKPI',
    component: ComplianceKPI
  },
  {
    path: '/compliance/tailoring',
    name: 'ComplianceTailoring',
    component: ComplianceTailoring
  },
  {
    path: '/compliance/versioning',
    name: 'ComplianceVersioning',
    component: ComplianceVersioning
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 
