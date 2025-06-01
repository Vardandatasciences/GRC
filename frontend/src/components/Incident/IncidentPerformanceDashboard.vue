<template>
    <div class="dashboard-container">
      <div class="dashboard-header">
        <h2 class="dashboard-heading">Incident  Dashboard</h2>
        <div class="dashboard-actions">
          <button class="action-btn"><i class="fas fa-sync-alt"></i></button>
          <button class="action-btn"><i class="fas fa-download"></i></button>
          <!-- <button class="action-btn primary"><i class="fas fa-plus"></i> New Risk</button> -->
        </div>
      </div>
      
      <!-- Dashboard Filters -->
      <div class="dashboard-filters">
        <div class="filter-group">
          <label>Time Range</label>
          <select v-model="filters.timeRange" class="filter-select">
            <option value="all">All Time</option>
            <option value="7days">Last 7 Days</option>
            <option value="30days">Last 30 Days</option>
            <option value="90days">Last 90 Days</option>
            <option value="1year">Last Year</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Category</label>
          <select v-model="filters.category" class="filter-select">
            <option value="all">All Categories</option>
            <option value="operational">Operational</option>
            <option value="financial">Financial</option>
            <option value="strategic">Strategic</option>
            <option value="compliance">Compliance</option>
            <option value="it-security">IT Security</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Priority</label>
          <select v-model="filters.priority" class="filter-select">
            <option value="all">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>
      
      <!-- Performance Summary Cards -->
      <div class="performance-summary">
        <div v-if="!hasData" class="no-data-message">
          No data found for the selected filters
        </div>
        <template v-else>
          <div class="summary-card">
            <div class="summary-icon">
              <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="summary-content">
              <div class="summary-label">Total Incidents</div>
              <div class="summary-value">{{ metrics.total }}</div>
              <div class="summary-trend" :class="getMetricTrendClass(5)">
                {{ formatTrendValue(5) }}
              </div>
            </div>
          </div>
          
          <div class="summary-card">
            <div class="summary-icon">
              <i class="fas fa-clock"></i>
            </div>
            <div class="summary-content">
              <div class="summary-label">Pending Incidents</div>
              <div class="summary-value">{{ metrics.pending }}</div>
              <div class="summary-trend" :class="getMetricTrendClass(12)">
                {{ formatTrendValue(12) }}
              </div>
            </div>
          </div>
          
          <div class="summary-card">
            <div class="summary-icon">
              <i class="fas fa-check-circle"></i>
            </div>
            <div class="summary-content">
              <div class="summary-label">Accepted Incidents</div>
              <div class="summary-value">{{ metrics.accepted }}</div>
              <div class="summary-trend" :class="getMetricTrendClass(-3)">
                {{ formatTrendValue(-3) }}
              </div>
            </div>
          </div>
          
          <div class="summary-card">
            <div class="summary-icon">
              <i class="fas fa-times-circle"></i>
            </div>
            <div class="summary-content">
              <div class="summary-label">Rejected Incidents</div>
              <div class="summary-value">{{ metrics.rejected }}</div>
              <div class="summary-trend" :class="getMetricTrendClass(8)">
                {{ formatTrendValue(8) }}
              </div>
            </div>
          </div>
          
          <div class="summary-card">
            <div class="summary-icon">
              <i class="fas fa-check-double"></i>
            </div>
            <div class="summary-content">
              <div class="summary-label">Resolved Incidents</div>
              <div class="summary-value">{{ metrics.resolved }}</div>
              <div class="summary-trend" :class="getMetricTrendClass(-3)">
                {{ formatTrendValue(-3) }}
              </div>
            </div>
          </div>
        </template>
      </div>
  
      <!-- Main Row: Asset Performance and Recent Activity -->
      <div class="dashboard-main-row dashboard-main-row-3col" style="display: flex; width: 100%;">
        <!-- Left: Asset Performance Card -->
        <div class="dashboard-main-col asset-performance-col" style="width: 70%;">
          <div class="chart-card tabbed-chart-card">
            <div class="card-header">
              <div class="header-left">
                <span>Incident performance</span>
                <div class="axis-selectors">
                  <select v-model="selectedXAxis" class="axis-select">
                    <option value="Priority">Priority</option>
                    <option value="Category">Category</option>
                    <option value="status">Status</option>
                    <option value="date">Date</option>
                  </select>
                  <select v-model="selectedYAxis" class="axis-select">
                    <option value="count">Count of Incidents</option>
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
            
            <!-- Debug info -->
            <div v-if="!hasData" class="no-data-message">
              No data available for the selected filters
            </div>
            <div v-else>
              <div class="debug-info" style="font-size: 12px; color: #666; margin: 10px;">
                Active Chart: {{ activeChart }}<br>
                Has Data: {{ hasData }}<br>
                Data Points: {{ 
                  activeChart === 'bar' ? (barChartData.datasets?.[0]?.data?.length || 0) :
                  activeChart === 'line' ? (lineChartData.datasets?.[0]?.data?.length || 0) :
                  activeChart === 'doughnut' ? (donutChartData.datasets?.[0]?.data?.length || 0) :
                  (horizontalBarChartData.datasets?.[0]?.data?.length || 0)
                }}
  
              </div>
              
              <div class="chart-container">
                <div class="chart-wrapper">
                  <canvas ref="chartContainer" height="350"></canvas>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Right: Recent Activity Card -->
        <div class="dashboard-main-col recent-activity-col" style="width: 30%;">
          <div class="activity-card">
            <div class="card-header">
              <h3>Recent Activity</h3>
              <button class="card-action"><i class="fas fa-ellipsis-v"></i></button>
            </div>
            <div class="activity-list">
              <div class="activity-item">
                <div class="activity-icon"><i class="fas fa-plus-circle"></i></div>
                <div class="activity-content">
                  <div class="activity-title">New Risk Added</div>
                  <div class="activity-desc">Data Breach Risk Assessment</div>
                  <div class="activity-time">2 hours ago</div>
                </div>
              </div>
              <div class="activity-item">
                <div class="activity-icon update"><i class="fas fa-edit"></i></div>
                <div class="activity-content">
                  <div class="activity-title">Risk Updated</div>
                  <div class="activity-desc">Operational Risk Review</div>
                  <div class="activity-time">Yesterday</div>
                </div>
              </div>
              <div class="activity-item">
                <div class="activity-icon alert"><i class="fas fa-exclamation-circle"></i></div>
                <div class="activity-content">
                  <div class="activity-title">Risk Alert</div>
                  <div class="activity-desc">Critical risk threshold exceeded</div>
                  <div class="activity-time">2 days ago</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, reactive, watch, onMounted, nextTick } from 'vue'
  import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    ArcElement
  } from 'chart.js'
  import axios from 'axios'
  
  // Register Chart.js components
  ChartJS.register(
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    ArcElement
  )
  
  export default {
    name: 'IncidentPerformanceDashboard',
    setup() {
      // Add a ref for the chart container
      const chartContainer = ref(null)
      // Create a variable to store the chart instance
      let chartInstance = null
      
      // State declarations
      const showRiskDetails = ref(true)
      const selectedXAxis = ref('Priority')
      const selectedYAxis = ref('count')
      const incidents = ref([])
      const hasData = ref(true)
      const activeChart = ref('bar')
      const metrics = reactive({
        total: 0,
        pending: 0,
        accepted: 0,
        rejected: 0,
        resolved: 0
      })
  
      // Define chart data objects
      const barChartData = reactive({
        labels: [],
        datasets: []
      })
      
      const lineChartData = reactive({
        labels: [],
        datasets: []
      })
      
      const donutChartData = reactive({
        labels: [],
        datasets: []
      })
      
      const horizontalBarChartData = reactive({
        labels: [],
        datasets: []
      })
  
      const filters = reactive({
        timeRange: 'all',
        category: 'all',
        priority: 'all'
      })
  
      const dashboardMetrics = ref({})
      const trends = ref({})
      const loading = ref(true)
  
      // Function to fetch incident data from the backend
      const fetchIncidentData = async () => {
        try {
          loading.value = true
          console.log('Fetching incident data...')
          
          // Use the list_incidents endpoint directly since counts endpoint is not working
          const response = await axios.get('/api/incidents')
          console.log('Incidents response:', response.data)
          
          if (response.data && Array.isArray(response.data)) {
            incidents.value = response.data
            
            // Log the first incident to see its structure
            if (incidents.value.length > 0) {
              console.log('Sample incident:', incidents.value[0])
              console.log('Available date fields:', 
                incidents.value[0].CreatedAt ? 'CreatedAt' : '',
                incidents.value[0].Date ? 'Date' : '',
                incidents.value[0].created_at ? 'created_at' : '',
                incidents.value[0].date ? 'date' : ''
              )
            }
            
            // Calculate counts from the incidents data
            metrics.total = incidents.value.length
            metrics.pending = incidents.value.filter(i => i.Status === 'Scheduled').length
            metrics.accepted = incidents.value.filter(i => i.Status === 'Approved').length
            metrics.rejected = incidents.value.filter(i => i.Status === 'Rejected').length
            metrics.resolved = metrics.accepted // Same as accepted in your case
            
            hasData.value = incidents.value.length > 0
          } else {
            console.warn('Invalid response format from API, using dummy data')
            useDummyData()
          }
          
          loading.value = false
          
          // Update the chart
          prepareChartData()
          renderChart()
        } catch (error) {
          console.error('Error fetching incidents:', error)
          // Use dummy data if the API call fails
          useDummyData()
          loading.value = false
        }
      }
      
      // Function to use dummy data (for both metrics and charts)
      const useDummyData = () => {
        console.log('Using dummy data for both metrics and charts')
        
        // Get the current date for dummy dates
        const currentDate = new Date()
        
        // Create dummy incidents that match your database
        incidents.value = [
          // 6 Scheduled incidents
          { IncidentId: 1, Status: 'Scheduled', RiskPriority: 'High', RiskCategory: 'IT Security', Date: new Date(currentDate.getFullYear(), 0, 15), CreatedAt: new Date(currentDate.getFullYear(), 0, 15) },
          { IncidentId: 2, Status: 'Scheduled', RiskPriority: 'Medium', RiskCategory: 'IT Security', Date: new Date(currentDate.getFullYear(), 1, 10), CreatedAt: new Date(currentDate.getFullYear(), 1, 10) },
          { IncidentId: 3, Status: 'Scheduled', RiskPriority: 'Low', RiskCategory: 'Compliance', Date: new Date(currentDate.getFullYear(), 2, 5), CreatedAt: new Date(currentDate.getFullYear(), 2, 5) },
          { IncidentId: 4, Status: 'Scheduled', RiskPriority: 'Medium', RiskCategory: 'Compliance', Date: new Date(currentDate.getFullYear(), 3, 20), CreatedAt: new Date(currentDate.getFullYear(), 3, 20) },
          { IncidentId: 5, Status: 'Scheduled', RiskPriority: 'High', RiskCategory: 'IT Security', Date: new Date(currentDate.getFullYear(), 4, 8), CreatedAt: new Date(currentDate.getFullYear(), 4, 8) },
          { IncidentId: 6, Status: 'Scheduled', RiskPriority: 'Medium', RiskCategory: 'Operational', Date: new Date(currentDate.getFullYear(), 4, 15), CreatedAt: new Date(currentDate.getFullYear(), 4, 15) },
          
          // 1 Approved incident
          { IncidentId: 7, Status: 'Approved', RiskPriority: 'Low', RiskCategory: 'Financial', Date: new Date(currentDate.getFullYear(), 4, 20), CreatedAt: new Date(currentDate.getFullYear(), 4, 20) },
          
          // 5 Rejected incidents
          { IncidentId: 8, Status: 'Rejected', RiskPriority: 'Medium', RiskCategory: 'IT Security', Date: new Date(currentDate.getFullYear(), 4, 25), CreatedAt: new Date(currentDate.getFullYear(), 4, 25) },
          { IncidentId: 9, Status: 'Rejected', RiskPriority: 'High', RiskCategory: 'Compliance', Date: new Date(currentDate.getFullYear(), 4, 28), CreatedAt: new Date(currentDate.getFullYear(), 4, 28) },
          { IncidentId: 10, Status: 'Rejected', RiskPriority: 'Low', RiskCategory: 'Operational', Date: new Date(currentDate.getFullYear(), 5, 2), CreatedAt: new Date(currentDate.getFullYear(), 5, 2) },
          { IncidentId: 11, Status: 'Rejected', RiskPriority: 'Medium', RiskCategory: 'Compliance', Date: new Date(currentDate.getFullYear(), 5, 5), CreatedAt: new Date(currentDate.getFullYear(), 5, 5) },
          { IncidentId: 12, Status: 'Rejected', RiskPriority: 'High', RiskCategory: 'IT Security', Date: new Date(currentDate.getFullYear(), 5, 10), CreatedAt: new Date(currentDate.getFullYear(), 5, 10) },
        ]
        
        // Calculate metrics from dummy data
        metrics.total = incidents.value.length
        metrics.pending = incidents.value.filter(i => i.Status === 'Scheduled').length
        metrics.accepted = incidents.value.filter(i => i.Status === 'Approved').length
        metrics.rejected = incidents.value.filter(i => i.Status === 'Rejected').length
        metrics.resolved = metrics.accepted
        
        hasData.value = true
        
        // Update chart with dummy data
        prepareChartData()
        renderChart()
      }
      
      // Prepare chart data based on the selected X-axis
      const prepareChartData = () => {
        if (!incidents.value.length) {
          console.warn('No incidents data available for charts')
          hasData.value = false
          return
        }
  
        console.log('Preparing chart data for', selectedXAxis.value)
        let labels = []
        let data = []
        let colors = []
  
        if (selectedXAxis.value === 'Priority') {
          // Use the exact priorities from your database screenshots: High, Medium, Low
          const priorityOrder = ['High', 'Medium', 'Low']
          const priorityCounts = { 'High': 0, 'Medium': 0, 'Low': 0 }
          
          incidents.value.forEach(incident => {
            const priority = incident.RiskPriority || 'Unknown'
            if (priorityCounts[priority] !== undefined) {
              priorityCounts[priority]++
            }
          })
          
          // Use the specific order for display
          labels = priorityOrder
          data = priorityOrder.map(priority => priorityCounts[priority])
          colors = ['#ef4444', '#facc15', '#84cc16'] // Red for High, Yellow for Medium, Green for Low
        } 
        else if (selectedXAxis.value === 'Category') {
          // Get all unique categories from incidents
          const categories = {}
          incidents.value.forEach(incident => {
              const category = incident.RiskCategory || 'Uncategorized'
            categories[category] = (categories[category] || 0) + 1
          })
          
          labels = Object.keys(categories)
          data = Object.values(categories)
          
          // Use consistent colors for categories
          const palette = ['#4f6cff', '#06b6d4', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316']
          colors = labels.map((_, i) => palette[i % palette.length])
        }
        else if (selectedXAxis.value === 'status') {
          // Use the exact status values from your database: Scheduled, Approved, Rejected
          const statusOrder = ['Scheduled', 'Approved', 'Rejected']
          const statusCounts = { 'Scheduled': 0, 'Approved': 0, 'Rejected': 0 }
          
          incidents.value.forEach(incident => {
            const status = incident.Status || 'Unknown'
            if (statusCounts[status] !== undefined) {
              statusCounts[status]++
            }
          })
          
          labels = statusOrder
          data = statusOrder.map(status => statusCounts[status])
          
          // Use meaningful colors for status
          colors = ['#fbbf24', '#4ade80', '#f87171'] // Yellow, Green, Red
        }
        else if (selectedXAxis.value === 'date') {
          // Group by month
          const monthLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
          const monthCounts = Array(12).fill(0)
          
          incidents.value.forEach(incident => {
            // Check all possible date field names since field names might be inconsistent
            const dateField = incident.CreatedAt || incident.Date || incident.created_at || incident.date
            
            if (dateField) {
              try {
                const date = new Date(dateField)
                if (!isNaN(date.getTime())) { // Check if valid date
                  const month = date.getMonth()
                  monthCounts[month]++
                }
              } catch (e) {
                console.warn('Invalid date format:', dateField)
              }
            }
          })
          
          labels = monthLabels
          data = monthCounts
          colors = Array(12).fill('#4f6cff')
        }
  
        console.log('Chart data prepared:', { labels, data, colors })
  
        // Update reactive chart data objects
        updateChartDatasets(labels, data, colors)
        
        // Ensure hasData reflects if we have valid data
        hasData.value = data.some(value => value > 0)
      }
  
      // Helper function to update all chart datasets
      const updateChartDatasets = (labels, data, colors) => {
        // Bar chart
        barChartData.labels = [...labels]
        barChartData.datasets = [{
          label: `${selectedXAxis.value} Distribution`,
          data: [...data],
          backgroundColor: colors,
          borderRadius: 4
        }]
        
        // Line chart
        lineChartData.labels = [...labels]
        lineChartData.datasets = [{
          label: `${selectedXAxis.value} Distribution`,
          data: [...data],
          borderColor: '#4f6cff',
          tension: 0.4,
          fill: false
        }]
        
        // Donut chart
        donutChartData.labels = [...labels]
        donutChartData.datasets = [{
          data: [...data],
          backgroundColor: colors,
          borderWidth: 0
        }]
        
        // Horizontal bar chart
        horizontalBarChartData.labels = [...labels]
        horizontalBarChartData.datasets = [{
          label: `${selectedXAxis.value} Distribution`,
          data: [...data],
          backgroundColor: colors,
          borderRadius: 4
        }]
      }
  
      // Create a function to render the chart
      const renderChart = () => {
        nextTick(() => {
          if (!chartContainer.value) {
            console.error('Chart container not found')
            return
          }
          
          // Destroy existing chart if it exists
          if (chartInstance) {
            chartInstance.destroy()
          }
          
          // Get the context for the chart
          const ctx = chartContainer.value.getContext('2d')
          if (!ctx) {
            console.error('Could not get chart context')
            return
          }
          
          // Prepare chart type and options
          let chartType = activeChart.value
          let chartData
          let chartOptions = {
            responsive: true,
            maintainAspectRatio: false
          }
          
          // Configure based on chart type
          if (chartType === 'horizontalBar') {
            chartType = 'bar'
            chartData = horizontalBarChartData
            chartOptions.indexAxis = 'y'
          } else if (chartType === 'line') {
            chartData = lineChartData
          } else if (chartType === 'doughnut') {
            chartData = donutChartData
          } else {
            // Default bar chart
            chartType = 'bar'
            chartData = barChartData
          }
          
          // Create the chart
          try {
            console.log('Creating chart with type:', chartType)
            chartInstance = new ChartJS(ctx, {
              type: chartType,
              data: chartData,
              options: chartOptions
            })
          } catch (error) {
            console.error('Error creating chart:', error)
          }
        })
      }
      
      // Initialize chart on mount
      onMounted(() => {
        console.log('Component mounted, fetching data...')
        
        // Fetch data immediately
        fetchIncidentData()
        
        // Fallback to dummy data if fetching fails
        setTimeout(() => {
          if (!incidents.value.length) {
            console.warn('No data after timeout, using dummy data')
            useDummyData()
          }
        }, 3000)
      })
      
      // Watch for changes to active chart or axes
      watch([activeChart, selectedXAxis, selectedYAxis], () => {
        prepareChartData()
        renderChart()
      })
      
      // Watch for filter changes
      watch([() => filters.timeRange, () => filters.category, () => filters.priority], 
        async () => {
          await fetchIncidentData()
        }
      )
  
      // Chart configurations
      const chartTypes = [
        { type: 'bar', icon: 'fas fa-chart-bar', label: 'Bar Chart' },
        { type: 'line', icon: 'fas fa-chart-line', label: 'Line Chart' },
        { type: 'doughnut', icon: 'fas fa-chart-pie', label: 'Donut Chart' },
        { type: 'horizontalBar', icon: 'fas fa-bars', label: 'Horizontal Bar Chart' }
      ]
  
      return {
        chartContainer,
        showRiskDetails,
        selectedXAxis,
        selectedYAxis,
        incidents,
        hasData,
        activeChart,
        metrics,
        filters,
        chartTypes,
        dashboardMetrics,
        trends,
        loading,
        getMetricIcon: (metricKey) => {
          const icons = {
            total_incidents: 'fas fa-exclamation-triangle',
            pending_incidents: 'fas fa-clock',
            accepted_incidents: 'fas fa-check-circle',
            rejected_incidents: 'fas fa-times-circle',
            resolved_incidents: 'fas fa-check-double'
          }
          return icons[metricKey] || 'fas fa-chart-line'
        },
        getMetricLabel: (metricKey) => {
          const labels = {
            total_incidents: 'Total Incidents',
            pending_incidents: 'Pending Incidents',
            accepted_incidents: 'Accepted Incidents',
            rejected_incidents: 'Rejected Incidents',
            resolved_incidents: 'Resolved Incidents'
          }
          return labels[metricKey] || metricKey
        },
        getMetricTrendClass: (percentage) => {
          return percentage > 0 ? 'positive' : 'negative'
        },
        formatTrendValue: (percentage) => {
          return `${percentage > 0 ? '+' : ''}${percentage}% from last month`
        },
        kpiData: reactive({
          mttd: { value: 0, unit: 'minutes', trend: [], change_percentage: 0 },
          mttr: { value: 0, unit: 'hours', trend: [] },
          mttc: { value: 0, unit: 'hours', trend: [] },
          mttrv: { value: 0, unit: 'hours', trend: [] }
        }),
        lineChartData,
        barChartData,
        donutChartData,
        horizontalBarChartData
      }
    }
  }
  </script>
  
  <style scoped>
  @import './IncidentPerformanceDashboard.css';
  
  .chart-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
    border: 1px solid rgba(0, 0, 0, 0.05);
    height: auto;
    min-height: 500px;
  }
  
  .chart-container {
    min-height: 400px;
    width: 100%;
    position: relative;
    margin: 20px 0;
    padding: 20px;
    background: #fff;
  }
  
  .chart-wrapper {
    width: 100%;
    height: 100%;
    min-height: 350px;
    position: relative;
  }
  
  .debug-info {
    background: #f8f9fa;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 10px;
  }
  
  .no-data-message {
    text-align: center;
    padding: 40px;
    color: #666;
    font-size: 16px;
    background: #f8f9fa;
    border-radius: 8px;
    margin: 20px 0;
  }
  
  .chart-tabs {
    display: flex;
    gap: 8px;
    margin-left: 16px;
  }
  
  .chart-tab-btn {
    background: none;
    border: none;
    padding: 8px;
    cursor: pointer;
    color: #666;
    border-radius: 4px;
    transition: all 0.2s;
  }
  
  .chart-tab-btn:hover,
  .chart-tab-btn.active {
    background: #f3f4f6;
    color: #4f6cff;
  }
  
  .chart-tab-btn i {
    font-size: 16px;
  }
  
  .tabbed-chart-card {
    display: flex;
    flex-direction: column;
  }
  
  .tabbed-chart-card .card-header {
    margin-bottom: 20px;
  }
  </style> 
  