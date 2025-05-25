<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Incident Dashboard</h2>
      <div class="dashboard-actions">
        <button class="action-btn" @click="fetchIncidents"><i class="fas fa-sync-alt"></i></button>
        <button class="action-btn"><i class="fas fa-download"></i></button>
        <!-- <button class="action-btn primary"><i class="fas fa-plus"></i> New Policy</button> -->
      </div>
    </div>
    
    <!-- Performance Summary Cards -->
    <div class="performance-summary">
      <div class="summary-card growth">
        <div class="summary-icon"><i class="fas fa-chart-line"></i></div>
        <div class="summary-content">
          <div class="summary-label">Incident Performance</div>
          <div class="summary-value">+{{performanceData.changePercentage}}% <span class="period">today</span></div>
          <div class="summary-trend positive">+{{performanceData.weeklyChange}}% in 1W</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-file-alt"></i></div>
        <div class="summary-content">
          <div class="summary-label">Total Incidents</div>
          <div class="summary-value">{{incidents.length}}</div>
          <div class="summary-trend positive">+{{newIncidentsThisMonth}} this month</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-exclamation-triangle"></i></div>
        <div class="summary-content">
          <div class="summary-label">Critical Issues</div>
          <div class="summary-value">{{criticalIncidents.length}}</div>
          <div class="summary-trend negative">+{{newCriticalThisWeek}} this week</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-check-circle"></i></div>
        <div class="summary-content">
          <div class="summary-label">Resolved Incidents</div>
          <div class="summary-value">{{resolvedIncidents.length}}</div>
          <div class="summary-trend positive">+{{newResolvedThisMonth}} this month</div>
        </div>
      </div>
    </div>

    <!-- Main Row: Incident Performance and Recent Activity -->
    <div class="dashboard-main-row dashboard-main-row-3col" style="display: flex; width: 100%;">
      <!-- Left: Incident Performance Chart -->
      <div class="dashboard-main-col asset-performance-col" style="width: 70%;">
        <div class="chart-card tabbed-chart-card">
          <div class="card-header">
            <div class="header-left">
              <span>Incident performance</span>
              <div class="axis-selectors">
                <select v-model="selectedXAxis" class="axis-select">
                  <option value="time">Time</option>
                  <option value="categories">Categories</option>
                  <option value="origin">Origin</option>
                  <option value="priority">Priority</option>
                  <option value="status">Status</option>
                </select>
                
              </div>
            </div>
            <div class="chart-tabs">
              <button
                v-for="tab in chartTypes"
                :key="tab.type"
                :class="['chart-tab-btn', { active: activeChart === tab.type }]"
                @click="activeChart = tab.type"
                :title="tab.label"
              >
                <i :class="tab.icon"></i>
              </button>
            </div>
          </div>
          <div class="chart-container" style="height: 300px;">
            <div v-if="loading" class="loading-indicator">Loading chart data...</div>
            <Line v-else-if="activeChart === 'line'" :data="lineChartData" :options="lineChartOptions" @click="onClickLineChart" />
            <Bar v-else-if="activeChart === 'bar'" :data="barChartData" :options="barChartOptions" @click="onClickBarChart" />
            <Doughnut v-else-if="activeChart === 'doughnut'" :data="donutChartData" :options="donutChartOptions" />
            <Bar v-else-if="activeChart === 'horizontalBar'" :data="horizontalBarChartData" :options="horizontalBarChartOptions" />
          </div>
        </div>
      </div>
      
      <!-- Right: Recent Activity Card -->
      <div class="dashboard-main-col recent-activity-col" style="width: 30%;">
        <div class="activity-card">
          <div class="card-header">
            <h3>Recent Incidents</h3>
            <button class="card-action"><i class="fas fa-ellipsis-v"></i></button>
          </div>
          <div class="activity-list">
            <div v-for="incident in recentIncidents" :key="incident.IncidentId" class="activity-item">
              <div class="activity-icon" :class="getIncidentIconClass(incident)">
                <i :class="getIncidentIcon(incident)"></i>
              </div>
              <div class="activity-content">
                <div class="activity-title">{{incident.IncidentTitle}}</div>
                <div class="activity-desc">{{incident.Description.substring(0, 60)}}{{incident.Description.length > 60 ? '...' : ''}}</div>
                <div class="activity-time">{{formatDate(incident.CreatedAt || incident.Date)}}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { Chart, ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js'
import { Doughnut, Bar, Line } from 'vue-chartjs'
import axios from 'axios'
import '@fortawesome/fontawesome-free/css/all.min.css'

Chart.register(ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

export default {
  name: 'IncidentDashboard',
  components: {
    Doughnut,
    Bar,
    Line
  },
  setup() {
    const incidents = ref([])
    const loading = ref(true)
    const selectedXAxis = ref('time')
    const selectedYAxis = ref('performance')
    
    // Make these reactive so they update when data changes
    const newIncidentsThisMonth = ref(0)
    const newCriticalThisWeek = ref(0)
    const newResolvedThisMonth = ref(0)
    
    // Performance data (would be calculated from real data)
    const performanceData = reactive({
      changePercentage: 2.46,
      weeklyChange: 18.67
    })
    
    // Fetch incident data from backend
    const fetchIncidents = async () => {
      loading.value = true
      try {
        const response = await axios.get('http://localhost:8000/api/incidents/')
        incidents.value = response.data
        
        if (incidents.value.length === 0) {
          initializeChartData()
        } else {
          // Calculate dynamic metrics based on actual data
          calculateMetrics()
          updateChartData(selectedXAxis.value, selectedYAxis.value)
        }
      } catch (error) {
        console.error('Error fetching incidents:', error)
        incidents.value = []
        initializeChartData()
      } finally {
        loading.value = false
      }
    }
    
    // Calculate metrics based on real data
    const calculateMetrics = () => {
      // Calculate new incidents this month
      const today = new Date()
      const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
      
      // Count incidents created this month
      const incidentsThisMonth = incidents.value.filter(incident => {
        const createdDate = new Date(incident.CreatedAt || incident.Date)
        return createdDate >= firstDayOfMonth
      })
      newIncidentsThisMonth.value = incidentsThisMonth.length
      
      // Count critical incidents created this week
      const firstDayOfWeek = new Date(today)
      firstDayOfWeek.setDate(today.getDate() - today.getDay())
      
      const criticalThisWeek = incidents.value.filter(incident => {
        const createdDate = new Date(incident.CreatedAt || incident.Date)
        return (
          createdDate >= firstDayOfWeek && 
          (incident.RiskPriority === 'Critical' || incident.RiskPriority === 'High')
        )
      })
      newCriticalThisWeek.value = criticalThisWeek.length
      
      // Count resolved incidents this month
      const resolvedThisMonth = incidents.value.filter(incident => {
        const createdDate = new Date(incident.CreatedAt || incident.Date)
        return (
          createdDate >= firstDayOfMonth && 
          incident.Status === 'Resolved'
        )
      })
      newResolvedThisMonth.value = resolvedThisMonth.length
    }
    
    // Computed properties for dashboard metrics
    const criticalIncidents = computed(() => {
      return incidents.value.filter(incident => 
        incident.RiskPriority === 'Critical' || incident.RiskPriority === 'High'
      )
    })
    
    const resolvedIncidents = computed(() => {
      return incidents.value.filter(incident => incident.Status === 'Resolved')
    })
    
    const recentIncidents = computed(() => {
      return [...incidents.value]
        .sort((a, b) => new Date(b.CreatedAt) - new Date(a.CreatedAt))
        .slice(0, 5)
    })
    
    // Helper functions for UI
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      const now = new Date()
      const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
      
      if (diffInDays === 0) return 'Today'
      if (diffInDays === 1) return 'Yesterday'
      if (diffInDays < 7) return `${diffInDays} days ago`
      return date.toLocaleDateString()
    }
    
    const getIncidentIcon = (incident) => {
      const category = incident.RiskCategory?.toLowerCase() || ''
      if (category.includes('security') || category.includes('access')) return 'fas fa-shield-alt'
      if (category.includes('malware') || category.includes('ransomware')) return 'fas fa-bug'
      if (category.includes('data') || category.includes('privacy')) return 'fas fa-database'
      if (category.includes('phishing') || category.includes('social')) return 'fas fa-fish'
      return 'fas fa-exclamation-circle'
    }
    
    const getIncidentIconClass = (incident) => {
      const priority = incident.RiskPriority?.toLowerCase() || ''
      if (priority.includes('critical') || priority.includes('high')) return 'alert'
      if (priority.includes('medium')) return 'update'
      return ''
    }
    
    // Watch for axis changes and update chart data accordingly
    watch([selectedXAxis, selectedYAxis], ([newXAxis, newYAxis]) => {
      updateChartData(newXAxis, newYAxis)
    })

    // Chart types
    const chartTypes = [
      { type: 'line', icon: 'fas fa-chart-line', label: 'Line' },
      { type: 'bar', icon: 'fas fa-chart-bar', label: 'Bar' },
      { type: 'doughnut', icon: 'fas fa-dot-circle', label: 'Donut' },
      { type: 'horizontalBar', icon: 'fas fa-align-left', label: 'Horizontal Bar' }
    ];
    const activeChart = ref('line');
    
    // Chart data
    const lineChartData = reactive({
      labels: [],
      datasets: [{
        label: 'Incident Performance',
        data: [],
        fill: false,
        borderColor: '#4f6cff',
        tension: 0.4,
        pointBackgroundColor: '#4f6cff',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    })
    
    const donutChartData = reactive({
      labels: [],
      datasets: [{
        data: [],
        backgroundColor: ['#4ade80', '#f87171', '#fbbf24'],
        borderWidth: 0,
        hoverOffset: 5
      }]
    })
    
    const barChartData = reactive({
      labels: [],
      datasets: []
    })
    
    const horizontalBarChartData = reactive({
      labels: [],
      datasets: [{
        label: 'Incidents',
        data: [],
        backgroundColor: '#4ade80',
        borderRadius: 6,
        barPercentage: 0.5,
        categoryPercentage: 0.7
      }]
    })
    
    // Chart options
    const lineChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            display: true,
            color: 'rgba(0,0,0,0.05)'
          },
          ticks: {
            font: { size: 11 }
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            font: { size: 11 }
          }
        }
      },
      animation: {
        duration: 1500,
        easing: 'easeOutQuart'
      },
      onClick: (event, elements) => {
        if (elements.length > 0) {
          const index = elements[0].index;
          const label = lineChartData.labels[index];
          console.log(`Clicked on ${label} with value ${lineChartData.datasets[0].data[index]}`);
          // You can filter or display detailed data here
        }
      }
    }
    
    const donutChartOptions = {
      cutout: '70%',
      plugins: {
        legend: { display: false }
      },
      maintainAspectRatio: false,
      animation: {
        animateRotate: true,
        animateScale: true,
        duration: 1000,
        easing: 'easeOutCubic'
      }
    }
    
    const barChartOptions = {
      plugins: { legend: { display: false } },
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { 
          stacked: true, 
          grid: { display: false },
          ticks: { color: '#222', font: { size: 10 } }
        },
        y: { 
          stacked: true, 
          grid: { color: 'rgba(0,0,0,0.05)' },
          ticks: { color: '#222', font: { size: 10 } }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      },
      onClick: (event, elements) => {
        if (elements.length > 0) {
          const index = elements[0].index;
          const label = barChartData.labels[index];
          console.log(`Clicked on ${label} with value ${barChartData.datasets[0].data[index]}`);
          // You can filter or display detailed data here
        }
      }
    }
    
    const horizontalBarChartOptions = {
      indexAxis: 'y',
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: { color: 'rgba(0,0,0,0.05)' },
          ticks: { color: '#222', font: { size: 10 } }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#222', font: { size: 10 } }
        }
      },
      maintainAspectRatio: false,
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      }
    }

    const updateChartData = (xAxis, yAxis) => {
      if (incidents.value.length === 0) return;
      
      // Update dataset label based on selected Y axis
      lineChartData.datasets[0].label = getYAxisLabel(yAxis);
      horizontalBarChartData.datasets[0].label = getYAxisLabel(yAxis);
      
      if (xAxis === 'origin') {
        // Group incidents by origin - specifically SIEM, Audit Findings, Manual
        const origins = {
          'SIEM': 0,
          'Audit Findings': 0,
          'Manual': 0,
          'Other': 0
        }
        
        incidents.value.forEach(incident => {
          const origin = incident.Source || incident.IncidentSource || incident.Origin || 'Unknown'
          
          // Map to standardized origin categories
          if (origin.toLowerCase().includes('siem') || origin.toLowerCase().includes('alert')) {
            origins['SIEM']++
          } else if (origin.toLowerCase().includes('audit') || origin.toLowerCase().includes('finding')) {
            origins['Audit Findings']++
          } else if (origin.toLowerCase().includes('manual')) {
            origins['Manual']++
          } else {
            origins['Other']++
          }
        })
        
        // Remove any categories with zero incidents
        Object.keys(origins).forEach(key => {
          if (origins[key] === 0) delete origins[key]
        })
        
        const labels = Object.keys(origins)
        const data = Object.values(origins)
        
        // Update charts with origin data
        lineChartData.labels = labels
        lineChartData.datasets[0].data = data
        
        donutChartData.labels = labels
        donutChartData.datasets[0].data = data
        
        horizontalBarChartData.labels = labels
        horizontalBarChartData.datasets[0].data = data
        
        // For bar chart, split by priority within each origin
        barChartData.labels = labels
        barChartData.datasets = ['Critical', 'High', 'Medium', 'Low'].map(priority => {
          return {
            label: priority,
            data: labels.map(label => {
              // Count incidents with this priority and origin
              return incidents.value.filter(incident => {
                const incidentOrigin = incident.Source || incident.IncidentSource || incident.Origin || 'Unknown'
                const matchesOrigin = 
                  (label === 'SIEM' && incidentOrigin.toLowerCase().includes('siem')) ||
                  (label === 'Audit Findings' && incidentOrigin.toLowerCase().includes('audit')) ||
                  (label === 'Manual' && incidentOrigin.toLowerCase().includes('manual')) ||
                  (label === 'Other' && !incidentOrigin.toLowerCase().includes('siem') && 
                   !incidentOrigin.toLowerCase().includes('audit') && 
                   !incidentOrigin.toLowerCase().includes('manual'))
                
                return matchesOrigin && incident.RiskPriority === priority
              }).length
            }),
            backgroundColor: getColorForPriority(priority),
            stack: 'Stack 0',
            borderRadius: 4
          }
        })
        
        return
      }
      
      if (xAxis === 'priority') {
        // Group incidents by priority
        const priorities = {}
        incidents.value.forEach(incident => {
          const priority = incident.RiskPriority || 'Unknown'
          if (!priorities[priority]) priorities[priority] = 0
          priorities[priority]++
        })
        
        const labels = Object.keys(priorities)
        const data = Object.values(priorities)
        
        // Update charts with priority data
        lineChartData.labels = labels
        lineChartData.datasets[0].data = data
        
        donutChartData.labels = labels
        donutChartData.datasets[0].data = data
        
        horizontalBarChartData.labels = labels
        horizontalBarChartData.datasets[0].data = data
        
        // For bar chart, use priority colors
        barChartData.labels = labels
        barChartData.datasets = [{
          label: 'Count',
          data: data,
          backgroundColor: labels.map(getColorForPriority),
          borderRadius: 4
        }]
        
        return
      }
      
      if (xAxis === 'categories') {
        // Group incidents by category
        const categories = {}
        incidents.value.forEach(incident => {
          const category = incident.RiskCategory || 'Other'
          if (!categories[category]) categories[category] = 0
          categories[category]++
        })
        
        const labels = Object.keys(categories)
        const data = Object.values(categories)
        
        // Update charts with category data
        lineChartData.labels = labels
        lineChartData.datasets[0].data = data
        
        donutChartData.labels = labels
        donutChartData.datasets[0].data = data
        
        horizontalBarChartData.labels = labels
        horizontalBarChartData.datasets[0].data = data
        
        // For bar chart, split by priority within each category
        const priorityCategories = { 'Critical': {}, 'High': {}, 'Medium': {}, 'Low': {} }
        
        incidents.value.forEach(incident => {
          const category = incident.RiskCategory || 'Other'
          const priority = incident.RiskPriority || 'Medium'
          
          if (!priorityCategories[priority]) priorityCategories[priority] = {}
          if (!priorityCategories[priority][category]) priorityCategories[priority][category] = 0
          priorityCategories[priority][category]++
        })
        
        barChartData.labels = labels
        barChartData.datasets = Object.keys(priorityCategories).map(priority => {
          return {
            label: priority,
            data: labels.map(label => priorityCategories[priority][label] || 0),
            backgroundColor: getColorForPriority(priority),
            stack: 'Stack 0',
            borderRadius: 4
          }
        })
        
        return
      }
      
      if (xAxis === 'status') {
        // Group incidents by status
        const statuses = {}
        incidents.value.forEach(incident => {
          const status = incident.Status || 'Unknown'
          if (!statuses[status]) statuses[status] = 0
          statuses[status]++
        })
        
        const labels = Object.keys(statuses)
        const data = Object.values(statuses)
        
        // Update all charts with status data
        lineChartData.labels = labels
        lineChartData.datasets[0].data = data
        
        donutChartData.labels = labels
        donutChartData.datasets[0].data = data
        
        horizontalBarChartData.labels = labels
        horizontalBarChartData.datasets[0].data = data
        
        // For bar chart, group by priority within each status
        barChartData.labels = labels
        barChartData.datasets = [{
          label: 'Count',
          data: data,
          backgroundColor: labels.map(getColorForStatus),
          borderRadius: 4
        }]
        
        return
      }
      
      if (xAxis === 'time') {
        // Group incidents by day of week or by month
        const dateMap = {
          'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0, 'Fri': 0, 'Sat': 0, 'Sun': 0
        }
        
        incidents.value.forEach(incident => {
          const date = new Date(incident.CreatedAt || incident.Date)
          const dayOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][date.getDay()]
          dateMap[dayOfWeek]++
        })
        
        const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        const data = labels.map(day => dateMap[day])
        
        // Update charts with time data
        lineChartData.labels = labels
        lineChartData.datasets[0].data = data
        
        donutChartData.labels = labels
        donutChartData.datasets[0].data = data
        
        horizontalBarChartData.labels = labels
        horizontalBarChartData.datasets[0].data = data
        
        // For bar chart, split by priority
        const priorityByDay = { 'Critical': {}, 'High': {}, 'Medium': {}, 'Low': {} }
        
        labels.forEach(day => {
          Object.keys(priorityByDay).forEach(priority => {
            priorityByDay[priority][day] = 0
          })
        })
        
        incidents.value.forEach(incident => {
          const date = new Date(incident.CreatedAt || incident.Date)
          const dayOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][date.getDay()]
          const priority = incident.RiskPriority || 'Medium'
          
          if (priorityByDay[priority]) {
            priorityByDay[priority][dayOfWeek]++
          }
        })
        
        barChartData.labels = labels
        barChartData.datasets = Object.keys(priorityByDay).map(priority => {
          return {
            label: priority,
            data: labels.map(day => priorityByDay[priority][day] || 0),
            backgroundColor: getColorForPriority(priority),
            stack: 'Stack 0',
            borderRadius: 4
          }
        })
      }
    }
    
    // Helper function to get color based on priority
    const getColorForPriority = (priority) => {
      const colors = {
        'Critical': '#f87171', // Red
        'High': '#fbbf24',     // Orange
        'Medium': '#4ade80',   // Green
        'Low': '#60a5fa'       // Blue
      }
      return colors[priority] || '#9ca3af' // Default gray
    }
    
    // Helper function to get color based on status
    const getColorForStatus = (status) => {
      const colors = {
        'Active': '#f87171',       // Red
        'Investigating': '#fbbf24', // Orange
        'Resolved': '#4ade80',     // Green
        'Closed': '#60a5fa'        // Blue
      }
      return colors[status] || '#9ca3af' // Default gray
    }
    
    // Helper function to get label for Y axis
    const getYAxisLabel = (yAxis) => {
      switch(yAxis) {
        case 'performance': return 'Performance Score'
        case 'risk': return 'Risk Score'
        default: return 'Value'
      }
    }

    // Initialize chart data with default values
    const initializeChartData = () => {
      // Set default data even when empty
      lineChartData.labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      lineChartData.datasets[0].data = [0, 0, 0, 0, 0, 0, 0]
      
      donutChartData.labels = ['No Data']
      donutChartData.datasets[0].data = [1]
      
      barChartData.labels = ['No Data'] 
      barChartData.datasets = [{
        label: 'Count',
        data: [0],
        backgroundColor: '#e5e7eb'
      }]
      
      horizontalBarChartData.labels = ['No Data']
      horizontalBarChartData.datasets[0].data = [0]
    }

    // Call initializeChartData before fetchIncidents in onMounted
    onMounted(() => {
      initializeChartData()
      fetchIncidents()
    })

    return {
      incidents,
      loading,
      criticalIncidents,
      resolvedIncidents,
      recentIncidents,
      newIncidentsThisMonth,
      newCriticalThisWeek,
      newResolvedThisMonth,
      performanceData,
      lineChartData,
      lineChartOptions,
      donutChartData,
      donutChartOptions,
      barChartData,
      barChartOptions,
      horizontalBarChartData,
      horizontalBarChartOptions,
      chartTypes,
      activeChart,
      selectedXAxis,
      selectedYAxis,
      formatDate,
      getIncidentIcon,
      getIncidentIconClass,
      fetchIncidents
    }
  }
}
</script>

<style scoped>
@import './IncidentPerformanceDashboard.css';
.chart-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.chart-tab-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #888;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 4px;
  transition: background 0.2s, color 0.2s;
}
.chart-tab-btn.active, .chart-tab-btn:hover {
  background: #eef2ff;
  color: #4f6cff;
}
.tabbed-chart-card {
  max-width: 900px;
  min-width: 480px;
  min-height: 300px;
  margin: 0 auto 32px auto;
  padding: 32px 32px 24px 32px;
  border-radius: 16px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.04);
  background: #fff;
}
.chart-performance-summary {
  margin-top: 18px;
  font-size: 1rem;
}
.dashboard-main-row {
  margin-top: 32px;
}
</style> 