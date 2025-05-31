import { createRouter, createWebHistory } from 'vue-router'
import PolicyDashboard from '../components/Policy/PolicyDashboard.vue'
import PerformancePage from '../components/Policy/PerformancePage.vue'
import AssignAudit from '../components/Auditor/AssignAudit.vue'
import AuditorDashboard from '../components/Auditor/AuditorDashboard.vue'
import Reviewer from '../components/Auditor/Reviewer.vue'
import CreateIncident from '../components/Incident/CreateIncident.vue'
import IncidentDashboard from '../components/Incident/IncidentDashboard.vue'
import CreateCompliance from '../components/Compliance/CreateCompliance.vue'
import CrudCompliance from '../components/Compliance/CrudCompliance.vue'
import ComplianceVersioning from '../components/Compliance/ComplianceVersioning.vue'
import RiskRegister from '../components/Risk/RiskRegister.vue'
import RiskDashboard from '../components/Risk/RiskDashboard.vue'
import RiskInstances from '../components/Risk/RiskInstances.vue'
import ApprovalAndHandling from '../components/Risk/ApprovalAndHandling.vue'
import RiskKPI from '../components/Risk/RiskKPI.vue'
import TailoringRisk from '../components/Risk/TailoringRisk.vue'

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
    path: '/compliance/crud',
    name: 'CrudCompliance',
    component: CrudCompliance
  },
  {
    path: '/compliance/versioning',
    name: 'ComplianceVersioning',
    component: ComplianceVersioning
  },
  {
    path: '/risk/riskregister',
    name: 'RiskRegister',
    component: RiskRegister
  },
  {
    path: '/risk/riskdashboard',
    name: 'RiskDashboard',
    component: RiskDashboard
  },
  {
    path: '/risk/riskinstances',
    name: 'RiskInstances',
    component: RiskInstances
  },
  {
    path: '/risk/ApprovalAndHandling',
    name: 'ApprovalAndHandling',
    component: ApprovalAndHandling
  },
  {
    path: '/risk/riskkpi',
    name: 'RiskKPI',
    component: RiskKPI
  },
  {
    path: '/risk/tailoring',
    name: 'RiskTailoring',
    component: TailoringRisk
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 
