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
import CrudCompliance from '../components/Compliance/CrudCompliance.vue'
import ComplianceVersioning from '../components/Compliance/ComplianceVersioning.vue'
import CreateRisk from '../components/Risk/CreateRisk.vue'
import RiskRegisterList from '../components/Risk/RiskRegisterList.vue'
import RiskRegisterListDetails from '../components/Risk/RiskRegisterListDetails.vue'
import RiskDashboard from '../components/Risk/RiskDashboard.vue'
import RiskInstances from '../components/Risk/RiskInstances.vue'
import CreateRiskInstance from '../components/Risk/CreateRiskInstance.vue'
import RiskInstanceDetails from '@/components/Risk/RiskInstanceDetails.vue'
// import ApprovalAndHandling from '../components/Risk/ApprovalAndHandling.vue'
import Notifications from '../components/Risk/Notifications.vue'
import ViewDetails from '../components/Risk/ViewDetails.vue'
import UserTasks from '../components/Risk/UserTasks.vue'
import MitigationWorkflow from '../components/Risk/MitigationWorkflow.vue'
import MappedRisks from '../components/Risk/MappedRisks.vue'
import TailoringRisk from '../components/Risk/TailoringRisk.vue'
import ReviewerWorkflow from '../components/Risk/ReviewerWorkflow.vue'

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
    path: '/risk/create',
    name: 'CreateRisk',
    component: CreateRisk
  },
  {
    path: '/risk/riskregister',
    name: 'RiskRegister',
    redirect: '/risk/riskregister-list'
  },
  {
    path: '/risk/riskregister-list',
    name: 'RiskRegisterList',
    component: RiskRegisterList
  },
  {
    path: '/risk/create-risk',
    name: 'CreateRiskForm',
    component: CreateRisk
  },
  // {
  //   path: '/risk/ApprovalAndHandling',
  //   name: 'ApprovalAndHandling',
  //   component: ApprovalAndHandling
  // },
  {
    path: '/risk/riskdashboard',
    name: 'RiskDashboard',
    component: RiskDashboard
  },
  {
    path: '/risk/riskinstances',
    name: 'RiskInstances',
    redirect: '/risk/riskinstances-list'
  },
  {
    path: '/risk/riskinstances-list',
    name: 'RiskInstancesList',
    component: RiskInstances
  },
  {
    path: '/risk/create-instance',
    name: 'CreateRiskInstance',
    component: CreateRiskInstance
  },
  {
    path: '/risk/riskinstances/:id',
    name: 'RiskInstanceDetails',
    component: RiskInstanceDetails
  },
  {
    path: '/risk/notifications',
    name: 'RiskNotifications',
    component: Notifications
  },
  {
    path: '/risk/incident-details/:id',
    name: 'ViewDetails',
    component: ViewDetails,
    props: true
  },
  {
    path: '/risk/mapped-risks/:incidentId?',
    name: 'MappedRisks',
    component: MappedRisks,
    props: true
  },
  {
    path: '/risk/workflow',
    name: 'RiskWorkflow',
    component: () => import('../components/Risk/Workflow.vue')
  },
  {
    path: '/risk/user-tasks',
    name: 'UserTasks',
    component: UserTasks
  },
  {
    path: '/risk/tailoring',
    name: 'RiskTailoring',
    component: TailoringRisk
  },
  {
    path: '/risk/details/:id',
    name: 'RiskRegisterListDetails',
    component: RiskRegisterListDetails,
    props: true
  },
  {
    path: '/risk/mitigation-workflow/:riskId',
    name: 'MitigationWorkflow',
    component: MitigationWorkflow,
    props: true
  },
  {
    path: '/risk/reviewer-workflow/:riskId',
    name: 'ReviewerWorkflow',
    component: ReviewerWorkflow,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 
