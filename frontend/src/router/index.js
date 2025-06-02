import { createRouter, createWebHistory } from 'vue-router'
import PolicyDashboard from '../components/Policy/PolicyDashboard.vue'
import CreatePolicy from '../components/Policy/CreatePolicy.vue'
import PerformancePage from '../components/Policy/PerformancePage.vue'
import AssignAudit from '../components/Auditor/AssignAudit.vue'
import AuditorDashboard from '../components/Auditor/AuditorDashboard.vue'
import Reviewer from '../components/Auditor/Reviewer.vue'
import TaskView from '../components/Auditor/TaskView.vue'
import ReviewTaskView from '../components/Auditor/ReviewTaskView.vue'
import AuditReport from '../components/Auditor/AuditReport.vue'
import PerformanceAnalysis from '../components/Auditor/PerformanceAnalysis.vue'
import KPIsAnalysis from '../components/Auditor/KPIsAnalysis.vue'
import PerformanceDashboard from '../components/Auditor/PerformanceDashboard.vue'

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
    path: '/auditor/reports',
    name: 'AuditReports',
    component: AuditReport
  },
  {
    path: '/auditor/performance',
    component: PerformanceAnalysis,
    children: [
      {
        path: '',
        redirect: '/auditor/performance/dashboard'
      },
      {
        path: 'dashboard',
        name: 'PerformanceDashboard',
        component: PerformanceDashboard
      },
      {
        path: 'kpis',
        name: 'KPIsAnalysis',
        component: KPIsAnalysis
      }
    ]
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 
