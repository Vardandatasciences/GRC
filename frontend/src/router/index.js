import { createRouter, createWebHistory } from 'vue-router'
import PolicyDashboard from '../components/Policy/PolicyDashboard.vue'
import CreatePolicy from '../components/Policy/CreatePolicy.vue'
import PerformancePage from '../components/Policy/PerformancePage.vue'
import PolicyApprover from '../components/Policy/PolicyApprover.vue'
import AllPolicies from '../components/Policy/AllPolicies.vue'
import AssignAudit from '../components/Auditor/AssignAudit.vue'
import ActivePolicies from '../components/Policy/ActivePolicies.vue'
import Framework from '../components/Policy/Framework.vue'
import Tailoring from '../components/Policy/Tailoring.vue'
import Versioning from '../components/Policy/Versioning.vue'
import TreePolicies from '../components/Policy/TreePolicies.vue'

// import AuditorDashboard from '../components/Auditor/AuditorDashboard.vue'
import Reviewer from '../components/Auditor/Reviewer.vue'
import CreateIncident from '../components/Incident/CreateIncident.vue'
import IncidentDashboard from '../components/Incident/IncidentDashboard.vue'
import ComplianceApprover from '../components/Compliance/ComplianceApprover.vue'
// import CreateCompliance from '../components/Compliance/CreateCompliance.vue'
// import CrudCompliance from '../components/Compliance/CrudCompliance.vue'
// import ComplianceVersioning from '../components/Compliance/ComplianceVersioning.vue'
import CreateRisk from '../components/Risk/CreateRisk.vue'
import RiskRegister from '../components/Risk/RiskRegister.vue'
import RiskDashboard from '../components/Risk/RiskDashboard.vue'
import RiskInstances from '../components/Risk/RiskInstances.vue'
import ApprovalAndHandling from '../components/Risk/ApprovalAndHandling.vue'
import Notifications from '../components/Risk/Notifications.vue'
import UserTasks from '../components/Risk/UserTasks.vue'
import TaskView from '../components/Auditor/TaskView.vue'
import ReviewTaskView from '../components/Auditor/ReviewTaskView.vue'
import Audits from '../components/Auditor/Audits.vue'

// import AllCompliance from '../components/Compliance/AllCompliance.vue'
// import ComplianceDashboard from '../components/Compliance/ComplianceDashboard.vue'
import CreateCompliance from '../components/Compliance/CreateCompliance.vue'
// import ComplianceVersioning from '../components/Compliance/ComplianceVersioning.vue'
// import ComplianceApprover from '../components/Compliance/ComplianceApprover.vue'
// import ComplianceVersionList from '../components/Compliance/ComplianceVersionList.vue'
 

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
    path: '/policy/approver',
    name: 'PolicyApprover',
    component: PolicyApprover
  },
  {
    path: '/policies-list/all',
    name: 'AllPolicies',
    component: AllPolicies
  },
  {
    path: '/policies-list/active',
    name: 'ActivePolicies',
    component: ActivePolicies
  },
  {
    path: '/create-policy/create',
    name: 'CreatePolicy',
    component: CreatePolicy
  },
  {
    path: '/create-policy/framework',
    name: 'Framework',
    component: Framework
  },
  {
    path: '/create-policy/tailoring',
    name: 'Tailoring',
    component: Tailoring
  },
  {
    path: '/create-policy/versioning',
    name: 'Versioning',
    component: Versioning
  },
  {
    path: '/tree-policies',
    name: 'TreePolicies',
    component: TreePolicies
  },
  {
    path: '/compliance/create',
    name: 'CreateCompliance',
    component: CreateCompliance
  },
  // {
  //   path: '/compliance/versioning',
  //   name: 'ComplianceVersioning',
  //   component: ComplianceVersioning
  // },
  {
    path: '/compliance/approver',
    name: 'ComplianceApprover',
    component: ComplianceApprover
  },
  // {
  //   path: '/compliance/version-list',
  //   name: 'ComplianceVersionList',
  //   component: ComplianceVersionList
  // },
  // {
  //   path: '/compliance/list',
  //   name: 'AllCompliance',
  //   component: AllCompliance
  // },
 
  {
    path: '/auditor/dashboard',
    name: 'AuditorDashboard',
    component: () => import('../components/Auditor/AuditorDashboard.vue')
  },
  {
    path: '/auditor/assign',
    name: 'AssignAudit',
    component: AssignAudit
  },
  {
    path: '/auditor/reviews',
    name: 'ReviewAudits',
    component: Reviewer
  },
  {
    path: '/auditor/reviewer',
    name: 'AuditorReviewer',
    component: Reviewer
  },
  {
    path: '/audit/:auditId/tasks',
    name: 'TaskView',
    component: TaskView,
    props: true
  },
  {
    path: '/reviewer/task/:auditId',
    name: 'ReviewTaskView',
    component: ReviewTaskView,
    props: true
  },
  {
    path: '/auditor/audits',
    name: 'Audits',
    component: Audits
  },
  {
    path: '/auditor/kpi',
    name: 'AuditorKPI',
    component: () => import('../components/Auditor/AuditorDashboard.vue')
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
    path: '/compliance/approver',
    name: 'ComplianceApprover',
    component: ComplianceApprover
  },
  {
    path: '/incident/incident',
    name: 'IncidentManagement',
    component: () => import('../components/Incident/Incident.vue')
  },
  {
    path: '/incident/performance/dashboard',
    name: 'IncidentPerformanceDashboard',
    component: () => import('../components/Incident/IncidentPerformanceDashboard.vue')


  },
  {
    path: '/risk/create',
    name: 'CreateRisk',
    component: CreateRisk
  },

{

  path: '/risk/riskregister',
  name: 'RiskRegister',
  component: RiskRegister
},

{
  path: '/risk/ApprovalAndHandling',
  name: 'ApprovalAndHandling',
  component: ApprovalAndHandling

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
    path: '/risk/notifications',
    name: 'RiskNotifications',
    component: Notifications
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


  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 
