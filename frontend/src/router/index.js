import { createRouter, createWebHistory } from 'vue-router'
import PolicyDashboard from '../components/Policy/PolicyDashboard.vue'
import PerformancePage from '../components/Policy/PerformancePage.vue'
import PolicyApprover from '../components/Policy/PolicyApprover.vue'
import AllPolicies from '../components/Policy/AllPolicies.vue'
import ActivePolicies from '../components/Policy/ActivePolicies.vue'
import Framework from '../components/Policy/Framework.vue'
import Tailoring from '../components/Policy/Tailoring.vue'
import Versioning from '../components/Policy/Versioning.vue'
import TreePolicies from '../components/Policy/TreePolicies.vue'
import CreatePolicy from '../components/Policy/CreatePolicy.vue'
import FrameworkExplorer from '../components/Policy/FrameworkExplorer.vue'
import FrameworkPolicies from '../components/Policy/FrameworkPolicies.vue'
import KPIDashboard from '../components/Policy/KPIDashboard.vue'
import FrameworkApprover from '../components/Framework/FrameworkApprover.vue'

import CreateIncident from '../components/Incident/CreateIncident.vue'
import IncidentDashboard from '../components/Incident/IncidentDashboard.vue'
import IncidentManagement from '../components/Incident/Incident.vue'
import IncidentDetails from '@/components/Incident/IncidentDetails.vue'
// import CreateRisk from '../components/Risk/CreateRisk.vue'
import RiskRegister from '../components/Risk/RiskRegister.vue'
import RiskDashboard from '../components/Risk/RiskDashboard.vue'
import RiskInstances from '../components/Risk/RiskInstances.vue'
import ApprovalAndHandling from '../components/Risk/ApprovalAndHandling.vue'
import Notifications from '../components/Risk/Notifications.vue'
import UserTasks from '../components/Risk/UserTasks.vue'

const routes = [
  {
    path: '/',
    name: 'HomePage',
    component: () => import('../components/Home.vue')
  },
  {
    path: '/policy',
    name: 'Policy',
    component: () => import('../components/Policy/PolicyDashboard.vue')
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
    path: '/framework-explorer',
    name: 'FrameworkExplorer',
    component: FrameworkExplorer
  },
  {
    path: '/framework-explorer/policies/:frameworkId',
    name: 'FrameworkPolicies',
    component: FrameworkPolicies,
    props: true
  },
  {
    path: '/policy/approval',
    name: 'PolicyApproval',
    component: PolicyApprover
  },
  {
    path: '/framework-approval',
    name: 'FrameworkApprover',
    component: FrameworkApprover
  },
  {
    path: '/policy/performance/dashboard',
    name: 'PolicyPerformanceDashboard',
    component: PolicyDashboard
  },
  {
    path: '/policy/performance/kpis',
    name: 'KPIDashboard',
    component: KPIDashboard
  },
  {
    path: '/incident/create',
    name: 'CreateIncident',
    component: CreateIncident
  },
  {
    path: '/incident/incident',
    name: 'Incident',
    component: IncidentManagement
  },
  {
    path: '/incident/dashboard',
    name: 'IncidentDashboard',
    component: IncidentDashboard
  },
  {
    path: '/incident/:id',
    name: 'IncidentDetails',
    component: IncidentDetails,
    props: true
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
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router 
