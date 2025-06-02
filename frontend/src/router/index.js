import { createRouter, createWebHistory } from 'vue-router'





import CreateCompliance from '../components/Compliance/CreateCompliance.vue'
import ComplianceApprover from '../components/Compliance/ComplianceApprover.vue'

import AllCompliance from '../components/Compliance/AllCompliance.vue'
import ComplianceDashboard from '../components/Compliance/ComplianceDashboard.vue'
import ComplianceTailoring from '../components/Compliance/ComplianceTailoring.vue'
import ComplianceVersioning from '../components/Compliance/ComplianceVersioning.vue'
import ComplianceKPI from '../components/Compliance/ComplianceKPI.vue'





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

const routes = [


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
  },

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 