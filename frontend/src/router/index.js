import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import IncidentsList from '../components/Incidents.vue'
import CreateIncident from '../components/CreateIncident.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/incidents',
    name: 'IncidentsList',
    component: IncidentsList,
    meta: { requiresAuth: true }
  },
  {
    path: '/incidents/create',
    name: 'CreateIncident',
    component: CreateIncident,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('user')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router 