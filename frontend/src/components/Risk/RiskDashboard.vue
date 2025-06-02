<template>
  <div class="dashboard-container">
    <!-- Header Section -->
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Risk Dashboard</h2>
      <div class="dashboard-actions">
        <button class="action-btn refresh"><i class="fas fa-sync-alt"></i> Refresh</button>
        <button class="action-btn export"><i class="fas fa-download"></i> Export</button>
      </div>
    </div>
    
    <!-- Filters Section -->
    <div class="filters-section">
    <div class="dashboard-filters">
      <div class="filter-group">
        <label>Time Range</label>
        <select v-model="filters.timeRange" class="filter-select" @change="fetchRiskMetrics">
          <option value="all">All Time</option>
          <option value="7days">Last 7 Days</option>
          <option value="30days">Last 30 Days</option>
          <option value="90days">Last 90 Days</option>
          <option value="1year">Last Year</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Category</label>
        <select v-model="filters.category" class="filter-select" @change="fetchRiskMetrics">
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
        <select v-model="filters.priority" class="filter-select" @change="fetchRiskMetrics">
          <option value="all">All Priorities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>
      </div>
    </div>
    
    <!-- Metrics Cards Section -->
    <div class="metrics-section">
    <div class="performance-summary">
      <div v-if="!hasData" class="no-data-message">
        No data found for the selected filters
      </div>
      <template v-else>
        <div class="summary-card">
            <div class="summary-icon total"><i class="fas fa-exclamation-triangle"></i></div>
          <div class="summary-content">
            <div class="summary-label">Total Risks</div>
            <div v-if="metrics.total > 0" class="summary-value">{{ metrics.total }}</div>
            <div v-else class="summary-value empty">No data found</div>
            <div v-if="metrics.total > 0" class="summary-trend positive">+12 this month</div>
          </div>
        </div>
        
        <div class="summary-card">
            <div class="summary-icon accepted"><i class="fas fa-check-circle"></i></div>
          <div class="summary-content">
            <div class="summary-label">Accepted Risks</div>
            <div v-if="metrics.accepted > 0" class="summary-value">{{ metrics.accepted }}</div>
            <div v-else class="summary-value empty">No data found</div>
            <div v-if="metrics.accepted > 0" class="summary-trend positive">+5 this month</div>
          </div>
        </div>
        
        <div class="summary-card">
            <div class="summary-icon rejected"><i class="fas fa-times-circle"></i></div>
          <div class="summary-content">
            <div class="summary-label">Rejected Risks</div>
            <div v-if="metrics.rejected > 0" class="summary-value">{{ metrics.rejected }}</div>
            <div v-else class="summary-value empty">No data found</div>
            <div v-if="metrics.rejected > 0" class="summary-trend negative">+3 this week</div>
          </div>
        </div>
        
        <div class="summary-card">
            <div class="summary-icon mitigated"><i class="fas fa-shield-alt"></i></div>
          <div class="summary-content">
            <div class="summary-label">Mitigated Risks</div>
            <div v-if="metrics.mitigated > 0" class="summary-value">{{ metrics.mitigated }}</div>
            <div v-else class="summary-value empty">No data found</div>
            <div v-if="metrics.mitigated > 0" class="summary-trend positive">+8 this month</div>
          </div>
        </div>
        
        <div class="summary-card">
            <div class="summary-icon inprogress"><i class="fas fa-spinner"></i></div>
          <div class="summary-content">
            <div class="summary-label">In Progress Risks</div>
            <div v-if="metrics.inProgress > 0" class="summary-value">{{ metrics.inProgress }}</div>
            <div v-else class="summary-value empty">No data found</div>
            <div v-if="metrics.inProgress > 0" class="summary-trend positive">+6 this week</div>
          </div>
        </div>
      </template>
      </div>
    </div>
    
    <!-- Row 1: Pie Chart and Bar Chart -->
    <div class="charts-row">
      <!-- Chart 1: Risk Distribution by Category (Pie Chart) -->
      <div class="chart-card">
          <div class="card-header">
          <h3>Risk Distribution by Category</h3>
              </div>
        <div class="chart-container">
          <Doughnut :data="categoryDistributionData" :options="donutChartOptions" />
            </div>
        <div class="chart-insights">
          <div class="insight-item">
            <span class="insight-label">Highest Category:</span>
            <span class="insight-value">Operational ({{ getHighestCategory() }}%)</span>
            </div>
          </div>
      </div>
      
      <!-- Chart 2: Risk Severity Matrix (Bar Chart) -->
      <div class="chart-card">
        <div class="card-header">
          <h3>Risk Severity by Priority</h3>
          </div>
      <div class="chart-container">
          <Bar :data="mitigationStatusData" :options="barChartOptions" />
        </div>
        <div class="chart-insights">
          <div class="insight-item">
            <span class="insight-label">Mitigation Rate:</span>
            <span class="insight-value">{{ getMitigationRate() }}%</span>
          </div>
          </div>
        </div>
      </div>
      
    <!-- Row 2: Line Chart and Dynamic Chart -->
    <div class="charts-row-uneven">
      <!-- Chart 3: Risk Trend Over Time (Line Chart) -->
      <div class="chart-card risk-trend">
          <div class="card-header">
          <h3>Risk Trend Over Time</h3>
          </div>
        <div class="chart-container">
          <Line :data="riskTrendData" :options="lineChartOptions" />
              </div>
        <div class="chart-insights">
          <div class="insight-item">
            <span class="insight-label">Trend:</span>
            <span class="insight-value" :class="getTrendClass()">{{ getTrendText() }}</span>
            </div>
              </div>
            </div>
      
      <!-- Chart 4: Dynamic Chart (X and Y Axis Selectable) -->
      <div class="chart-card dynamic-chart">
        <div class="card-header">
          <h3>Custom Risk Analysis</h3>
          <div class="axis-controls">
            <div class="axis-control">
              <label>X-Axis</label>
              <select v-model="selectedXAxis" class="axis-select" @change="onAxisChange">
                <option value="time">Time</option>
                <option value="category">Category</option>
                <option value="priority">Risk Priority</option>
                <option value="criticality">Criticality</option>
                <option value="status">Status</option>
                <option value="appetite">Risk Appetite</option>
                <option value="mitigation">Mitigation Status</option>
              </select>
              </div>
            
            <div class="axis-control">
              <label>Y-Axis</label>
              <select v-model="selectedYAxis" class="axis-select" @change="onAxisChange">
                <option v-for="option in yAxisOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>
          </div>
        </div>
        <div class="chart-container">
          <div class="chart-tabs">
            <button 
              v-for="chartType in ['line', 'bar', 'doughnut']" 
              :key="chartType"
              :class="['chart-tab-btn', { active: activeChart === chartType }]"
              @click="activeChart = chartType"
            >
              <i :class="getChartIcon(chartType)"></i>
            </button>
          </div>
          
          <div class="chart-content">
            <Line v-if="activeChart === 'line'" :data="lineChartData" :options="customChartOptions" />
            <Bar v-if="activeChart === 'bar'" :data="barChartData" :options="customChartOptions" />
            <Doughnut v-if="activeChart === 'doughnut'" :data="donutChartData" :options="customDonutOptions" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch, onMounted } from 'vue'
import { Chart, ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js'
import { Doughnut, Bar, Line } from 'vue-chartjs'
import '@fortawesome/fontawesome-free/css/all.min.css'
import axios from 'axios'

Chart.register(ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

export default {
  name: 'RiskDashboard',
  components: {
    Doughnut,
    Bar,
    Line
  },
  setup() {
    const showRiskDetails = ref(true)
    const selectedXAxis = ref('time')
    const selectedYAxis = ref('performance')
    
    // Watch for axis changes and update chart data accordingly
    watch([selectedXAxis, selectedYAxis], ([newXAxis, newYAxis]) => {
      // Update chart data based on selected axes
      updateChartData(newXAxis, newYAxis)
    })

    // --- CATEGORY DATA FOR ACTIVE/INACTIVE/ON HOLD ---
    const categoryStatusData = {
      Operational: { active: 12, inactive: 3, onhold: 2 },
      Compliance: { active: 10, inactive: 4, onhold: 1 },
      'IT Security': { active: 8, inactive: 6, onhold: 2 },
      Financial: { active: 14, inactive: 2, onhold: 1 },
      Strategic: { active: 9, inactive: 5, onhold: 3 }
    }

    const updateChartData = (xAxis, yAxis) => {
      const labels = getLabelsForXAxis(xAxis)
      let data = getDataForYAxis(yAxis)
      
      // If categories, use status split
      if (xAxis === 'categories') {
        // For donut: sum all active/inactive/onhold
        const active = Object.values(categoryStatusData).reduce((a, c) => a + c.active, 0)
        const inactive = Object.values(categoryStatusData).reduce((a, c) => a + c.inactive, 0)
        const onhold = Object.values(categoryStatusData).reduce((a, c) => a + c.onhold, 0)
        donutChartData.labels = ['Active', 'Inactive', 'On Hold']
        donutChartData.datasets[0].data = [active, inactive, onhold]
        donutChartData.datasets[0].backgroundColor = ['#4ade80', '#f87171', '#fbbf24']

        // For bar/horizontal bar: show each category split
        barChartData.labels = labels
        barChartData.datasets = [
          {
            label: 'Active',
            data: labels.map(l => categoryStatusData[l]?.active || 0),
            backgroundColor: '#4ade80',
            stack: 'Stack 0',
            borderRadius: 4
          },
          {
            label: 'Inactive',
            data: labels.map(l => categoryStatusData[l]?.inactive || 0),
            backgroundColor: '#f87171',
            stack: 'Stack 0',
            borderRadius: 4
          },
          {
            label: 'On Hold',
            data: labels.map(l => categoryStatusData[l]?.onhold || 0),
            backgroundColor: '#fbbf24',
            stack: 'Stack 0',
            borderRadius: 4
          }
        ]
        // For line: show only active for demo
        lineChartData.labels = labels
        lineChartData.datasets[0].data = labels.map(l => categoryStatusData[l]?.active || 0)
        lineChartData.datasets[0].label = 'Active'
        return
      }
      // If status, show Active/Inactive/On Hold as X axis
      if (xAxis === 'status') {
        const statusLabels = ['Active', 'Inactive', 'On Hold']
        // Sum for each status across all categories
        const active = Object.values(categoryStatusData).reduce((a, c) => a + c.active, 0)
        const inactive = Object.values(categoryStatusData).reduce((a, c) => a + c.inactive, 0)
        const onhold = Object.values(categoryStatusData).reduce((a, c) => a + c.onhold, 0)
        const statusData = [active, inactive, onhold]
        // Donut
        donutChartData.labels = statusLabels
        donutChartData.datasets[0].data = statusData
        donutChartData.datasets[0].backgroundColor = ['#4ade80', '#f87171', '#fbbf24']
        // Bar
        barChartData.labels = statusLabels
        barChartData.datasets = [
          {
            label: getYAxisLabel(yAxis),
            data: statusData,
            backgroundColor: ['#4ade80', '#f87171', '#fbbf24'],
            borderRadius: 4
          }
        ]
        // Line
        lineChartData.labels = statusLabels
        lineChartData.datasets[0].data = statusData
        lineChartData.datasets[0].label = getYAxisLabel(yAxis)
        return
      }
      // Default (non-category, non-status) logic
      // Update Line Chart
      lineChartData.labels = labels
      lineChartData.datasets[0].data = data
      lineChartData.datasets[0].label = getYAxisLabel(yAxis)

      // Update Bar Chart
      barChartData.labels = labels
      barChartData.datasets = getBarChartDatasets(yAxis)

      // Update Donut Chart
      donutChartData.labels = labels
      donutChartData.datasets[0].data = data
    }

    const getYAxisLabel = (yAxis) => {
      const labelMap = {
        'count': 'Count',
        'exposure': 'Risk Exposure Rating',
        'impact': 'Risk Impact',
        'likelihood': 'Risk Likelihood',
        'avgExposure': 'Average Exposure',
        'maxExposure': 'Maximum Exposure',
        'mitigated': 'Mitigated Risks',
        'avgImpact': 'Average Impact',
        'avgLikelihood': 'Average Likelihood',
        'responseTime': 'Response Time (days)',
        'mitigationTime': 'Mitigation Time (days)',
        'openRisks': 'Open Risks',
        'reviewCount': 'Review Count',
        'daysInStatus': 'Days in Status',
        'exposureByStatus': 'Exposure by Status',
        'acceptedRisks': 'Accepted Risks',
        'rejectedRisks': 'Rejected Risks',
        'mitigationCost': 'Mitigation Cost',
        'completedMitigations': 'Completed Mitigations',
        'pendingMitigations': 'Pending Mitigations'
      };
      return labelMap[yAxis] || 'Value';
    }

    const getBarChartDatasets = (yAxis) => {
      const baseData = getDataForYAxis(yAxis)
      return [
        {
          label: 'High',
          data: baseData.map(val => Math.round(val * 0.4)),
          backgroundColor: '#4ade80',
          stack: 'Stack 0',
          borderRadius: 4
        },
        {
          label: 'Medium',
          data: baseData.map(val => Math.round(val * 0.35)),
          backgroundColor: '#fbbf24',
          stack: 'Stack 0',
          borderRadius: 4
        },
        {
          label: 'Low',
          data: baseData.map(val => Math.round(val * 0.25)),
          backgroundColor: '#f87171',
          stack: 'Stack 0',
          borderRadius: 4
        }
      ]
    }

    const getLabelsForXAxis = (xAxis) => {
      switch(xAxis) {
        case 'time':
          return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        case 'risks':
          return ['Data Breach', 'Operational', 'Compliance', 'Financial', 'Strategic']
        case 'categories':
          return ['Operational', 'Compliance', 'IT Security', 'Financial', 'Strategic']
        case 'status':
          return ['Active', 'Inactive', 'On Hold']
        default:
          return []
      }
    }

    const getDataForYAxis = (yAxis) => {
      switch(yAxis) {
        case 'performance':
          return [85, 88, 92, 87, 90, 95, 89]
        case 'compliance':
          return [92, 95, 88, 90, 93, 96, 91]
        case 'risk':
          return [65, 70, 68, 72, 75, 80, 78]
        default:
          return []
      }
    }

    // Chart tab logic
    const chartTypes = [
      { type: 'line', icon: 'fas fa-chart-line', label: 'Line' },
      { type: 'bar', icon: 'fas fa-chart-bar', label: 'Bar' },
      { type: 'doughnut', icon: 'fas fa-dot-circle', label: 'Donut' },
    ];
    const activeChart = ref('line');
    
    // Line Chart Data
    const lineChartData = reactive({
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Risk Performance',
        data: [42, 38, 35, 40, 56, 75, 82],
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
    
    // Line Chart Options
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
            font: { size: 10 },
            padding: 5
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            font: { size: 10 },
            padding: 5
          }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      },
      layout: {
        padding: 0
      }
    }
    
    // Donut Chart Data
    const donutChartData = reactive({
      labels: ['Active', 'Inactive', 'On Hold'],
          datasets: [{
        data: [60, 25, 15],
        backgroundColor: ['#4ade80', '#f87171', '#fbbf24'],
        borderWidth: 0,
        hoverOffset: 5
      }]
    })
    
    // Donut Chart Options
    const donutChartOptions = {
      cutout: '65%',
      plugins: {
        legend: { display: false }
      },
      maintainAspectRatio: false,
      animation: {
        animateRotate: true,
        animateScale: true,
        duration: 800,
        easing: 'easeOutCubic'
      },
      layout: {
        padding: 0
      }
    }
    
    // Bar Chart Data
    const barChartData = reactive({
      labels: ['Operational', 'Compliance'],
      datasets: [
        {
          label: 'Active',
          data: [8, 5],
          backgroundColor: '#4ade80',
          stack: 'Stack 0',
          borderRadius: 4
        },
        {
          label: 'Inactive',
          data: [6, 7],
          backgroundColor: '#f87171',
          stack: 'Stack 0',
          borderRadius: 4
        },
        {
          label: 'On Hold',
          data: [3, 0],
          backgroundColor: '#fbbf24',
          stack: 'Stack 0',
          borderRadius: 4
        }
      ]
    })
    
    // Bar Chart Options
    const barChartOptions = {
      plugins: { legend: { display: false } },
          responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { 
          stacked: true, 
          grid: { display: false },
          ticks: { color: '#222', font: { size: 9 }, padding: 5 }
        },
        y: { 
          stacked: true, 
          grid: { color: 'rgba(0,0,0,0.05)' },
          ticks: { color: '#222', font: { size: 9 }, padding: 5 }
        }
      },
      animation: {
        duration: 800,
        easing: 'easeInOutQuart'
      },
      layout: {
        padding: 0
      }
    }

    const toggleRiskDetails = () => {
      showRiskDetails.value = !showRiskDetails.value
    }

    const metrics = reactive({
      total: 0,
      accepted: 0,
      rejected: 0,
      mitigated: 0,
      inProgress: 0
    })

    const hasData = ref(true);
    
    // Update fetchRiskMetrics function to be called on filter change
    const fetchRiskMetrics = async () => {
      try {
        console.log('Fetching risk metrics with filters:', filters)
        const params = new URLSearchParams({
          timeRange: filters.timeRange,
          category: filters.category,
          priority: filters.priority
        })
        const response = await axios.get(`http://localhost:8000/api/risk/metrics?${params}`)
        console.log('Received metrics data:', response.data)
        
        // Update hasData based on if we have any metrics
        hasData.value = response.data.total > 0
        
        Object.assign(metrics, response.data)
        
        // Update chart data based on new metrics
        updateChartData(selectedXAxis.value, selectedYAxis.value)
      } catch (error) {
        console.error('Error fetching risk metrics:', error)
        hasData.value = false
        // Set default values if API fails
        Object.assign(metrics, { 
          total: 0, 
          accepted: 0, 
          rejected: 0, 
          mitigated: 0, 
          inProgress: 0 
        })
      }
    }

    // Add filters state
    const filters = reactive({
      timeRange: 'all',
      category: 'all',
      priority: 'all'
    })

    // Y-axis options that change based on X-axis selection
    const yAxisOptions = ref([
      { value: 'count', label: 'Count' },
      { value: 'exposure', label: 'Risk Exposure' },
      { value: 'impact', label: 'Risk Impact' },
      { value: 'likelihood', label: 'Risk Likelihood' }
    ]);
    
    // Watch for X-axis changes to update Y-axis options
    watch(selectedXAxis, (newXAxis) => {
      switch(newXAxis) {
        case 'time':
          yAxisOptions.value = [
            { value: 'count', label: 'Count' },
            { value: 'exposure', label: 'Risk Exposure' },
            { value: 'impact', label: 'Risk Impact' },
            { value: 'likelihood', label: 'Risk Likelihood' }
          ];
          break;
        case 'category':
          yAxisOptions.value = [
            { value: 'count', label: 'Count' },
            { value: 'avgExposure', label: 'Avg Exposure' },
            { value: 'maxExposure', label: 'Max Exposure' },
            { value: 'mitigated', label: 'Mitigated Risks' }
          ];
          break;
        case 'priority':
          yAxisOptions.value = [
            { value: 'count', label: 'Count' },
            { value: 'avgImpact', label: 'Avg Impact' },
            { value: 'avgLikelihood', label: 'Avg Likelihood' },
            { value: 'responseTime', label: 'Avg Response Time' }
          ];
          break;
        case 'criticality':
          yAxisOptions.value = [
            { value: 'count', label: 'Count' },
            { value: 'mitigationTime', label: 'Avg Mitigation Time' },
            { value: 'openRisks', label: 'Open Risks' },
            { value: 'reviewCount', label: 'Review Count' }
          ];
          break;
        case 'status':
          yAxisOptions.value = [
            { value: 'count', label: 'Count' },
            { value: 'daysInStatus', label: 'Avg Days in Status' },
            { value: 'exposureByStatus', label: 'Exposure by Status' }
          ];
          break;
        case 'appetite':
          yAxisOptions.value = [
            { value: 'count', label: 'Count' },
            { value: 'acceptedRisks', label: 'Accepted Risks' },
            { value: 'rejectedRisks', label: 'Rejected Risks' }
          ];
          break;
        case 'mitigation':
          yAxisOptions.value = [
            { value: 'count', label: 'Count' },
            { value: 'mitigationCost', label: 'Mitigation Cost' },
            { value: 'completedMitigations', label: 'Completed Mitigations' },
            { value: 'pendingMitigations', label: 'Pending Mitigations' }
          ];
          break;
        default:
          yAxisOptions.value = [
            { value: 'count', label: 'Count' },
            { value: 'exposure', label: 'Risk Exposure' }
          ];
      }
      
      // Set default Y-axis when X-axis changes
      selectedYAxis.value = yAxisOptions.value[0].value;
    });

    // Update fetchDashboardData function to use the selected axes
    const fetchDashboardData = async () => {
      try {
        console.log('Fetching data with axes:', selectedXAxis.value, selectedYAxis.value);
        const params = new URLSearchParams({
          xAxis: selectedXAxis.value,
          yAxis: selectedYAxis.value,
          timeRange: filters.timeRange,
          category: filters.category,
          priority: filters.priority
        });
        
        const response = await axios.get(`http://localhost:8000/api/risk/dashboard-data?${params}`);
        console.log('Received dashboard data:', response.data);
        
        // Update chart data based on response
        updateChartDataFromResponse(response.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Use default chart data
        updateChartData(selectedXAxis.value, selectedYAxis.value);
      }
    };
    
    // New function to update chart data from API response
    const updateChartDataFromResponse = (data) => {
      // Update line chart data
      lineChartData.labels = data.labels;
      lineChartData.datasets[0].data = data.values;
      lineChartData.datasets[0].label = getYAxisLabel(selectedYAxis.value);
      
      // Update bar chart data
      barChartData.labels = data.labels;
      if (data.series) {
        barChartData.datasets = data.series.map((series, index) => ({
          label: series.name,
          data: series.data,
          backgroundColor: getColorForIndex(index),
          stack: 'Stack 0',
          borderRadius: 4
        }));
      } else {
        barChartData.datasets = [{
          label: getYAxisLabel(selectedYAxis.value),
          data: data.values,
          backgroundColor: '#4f6cff',
          borderRadius: 4
        }];
      }
      
      // Update donut chart data
      donutChartData.labels = data.labels;
      donutChartData.datasets[0].data = data.values;
      donutChartData.datasets[0].backgroundColor = generateColors(data.labels.length);
    };
    
    // Helper function to generate colors
    const generateColors = (count) => {
      const baseColors = ['#4ade80', '#f87171', '#fbbf24', '#60a5fa', '#818cf8', '#e879f9', '#fb7185'];
      const colors = [];
      for (let i = 0; i < count; i++) {
        colors.push(baseColors[i % baseColors.length]);
      }
      return colors;
    };
    
    // Helper function to get color for series index
    const getColorForIndex = (index) => {
      const colors = ['#4ade80', '#f87171', '#fbbf24', '#60a5fa', '#818cf8', '#e879f9', '#fb7185'];
      return colors[index % colors.length];
    };
    
    // eslint-disable-next-line no-unused-vars
    watch([selectedXAxis, selectedYAxis], ([_newXAxis, _newYAxis]) => {
      fetchDashboardData();
    });

    // Initialize chart data and fetch metrics
    fetchDashboardData();
    fetchRiskMetrics();

    const onAxisChange = () => {
      fetchDashboardData();
    };

    // New chart data for specialized charts
    
    // 1. Category Distribution Chart
    const categoryDistributionData = reactive({
      labels: ['Operational', 'Financial', 'Compliance', 'IT Security', 'Strategic'],
      datasets: [{
        data: [35, 25, 15, 15, 10],
        backgroundColor: ['#4ade80', '#f87171', '#fbbf24', '#60a5fa', '#818cf8'],
        borderWidth: 0,
        hoverOffset: 5
      }]
    })
    
    // 2. Risk Trend Over Time
    const riskTrendData = reactive({
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [
        {
          label: 'New Risks',
          data: [12, 14, 10, 15, 18, 20],
          borderColor: '#f87171',
          backgroundColor: 'rgba(248, 113, 113, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Mitigated Risks',
          data: [8, 9, 11, 13, 15, 19],
          borderColor: '#4ade80',
          backgroundColor: 'rgba(74, 222, 128, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    })
    
    // 4. Mitigation Status
    const mitigationStatusData = reactive({
      labels: ['Critical', 'High', 'Medium', 'Low'],
      datasets: [
        {
          label: 'Completed',
          data: [15, 22, 30, 28],
          backgroundColor: '#4ade80',
          borderRadius: 6,
          barPercentage: 0.7,
          categoryPercentage: 0.8
        },
        {
          label: 'In Progress',
          data: [8, 15, 20, 10],
          backgroundColor: '#fbbf24',
          borderRadius: 6,
          barPercentage: 0.7,
          categoryPercentage: 0.8
        },
        {
          label: 'Not Started',
          data: [12, 8, 5, 3],
          backgroundColor: '#f87171',
          borderRadius: 6,
          barPercentage: 0.7,
          categoryPercentage: 0.8
        }
      ]
    })
    
    // Helper functions for insights
    const getHighestCategory = () => {
      const data = categoryDistributionData.datasets[0].data;
      const max = Math.max(...data);
      return max;
    }
    
    const getTrendText = () => {
      const newRisks = riskTrendData.datasets[0].data;
      const mitigated = riskTrendData.datasets[1].data;
      const lastIndex = newRisks.length - 1;
      
      if (newRisks[lastIndex] > mitigated[lastIndex]) {
        return 'Increasing ↑';
      } else if (newRisks[lastIndex] < mitigated[lastIndex]) {
        return 'Decreasing ↓';
      }
      return 'Stable →';
    }
    
    const getTrendClass = () => {
      const trend = getTrendText();
      if (trend.includes('Increasing')) return 'negative';
      if (trend.includes('Decreasing')) return 'positive';
      return '';
    }
    
    const getMitigationRate = () => {
      const allMitigation = mitigationStatusData.datasets.map(dataset => 
        dataset.data.reduce((sum, value) => sum + value, 0)
      );
      const total = allMitigation.reduce((sum, value) => sum + value, 0);
      const completed = allMitigation[0];
      return Math.round((completed / total) * 100);
    }
    
    // Fetch data for specialized charts
    const fetchSpecializedChartData = async () => {
      try {
        const params = new URLSearchParams({
          timeRange: filters.timeRange,
          category: filters.category,
          priority: filters.priority
        });
        
        // Fetch category distribution data
        const categoryRes = await axios.get(`http://localhost:8000/api/risk/metrics-by-category?${params}`);
        if (categoryRes.data && categoryRes.data.statusBreakdown) {
          const categories = Object.keys(categoryRes.data.statusBreakdown);
          const counts = categories.map(cat => categoryRes.data.statusBreakdown[cat]);
          categoryDistributionData.labels = categories;
          categoryDistributionData.datasets[0].data = counts;
        }
        
        // Fetch risk trend data
        const trendRes = await axios.get(`http://localhost:8000/api/risk/identification-rate?${params}`);
        if (trendRes.data && trendRes.data.months && trendRes.data.trendData) {
          riskTrendData.labels = trendRes.data.months;
          riskTrendData.datasets[0].data = trendRes.data.trendData;
          
          // For mitigated, use a formula based on identification rate
          const mitigationRes = await axios.get(`http://localhost:8000/api/risk/mitigation-completion-rate?${params}`);
          if (mitigationRes.data && mitigationRes.data.trendData) {
            riskTrendData.datasets[1].data = mitigationRes.data.trendData;
          }
        }
        
        // Fetch mitigation status data
        const mitigationRes = await axios.get(`http://localhost:8000/api/risk/due-mitigation?${params}`);
        if (mitigationRes.data) {
          // Update mitigation chart with real data
          const priorities = ['Critical', 'High', 'Medium', 'Low'];
          mitigationStatusData.labels = priorities;
          
          // Generate reasonable values for each priority based on available data
          const completed = mitigationRes.data.completedPercentage || 50;
          const overdue = mitigationRes.data.overduePercentage || 22;
          const pending = mitigationRes.data.pendingPercentage || 28;
          
          mitigationStatusData.datasets[0].data = priorities.map((_, i) => 
            Math.round(completed * (1 - (i * 0.1)))
          );
          
          mitigationStatusData.datasets[1].data = priorities.map((_, i) => 
            Math.round(pending * (1 + (i * 0.1)))
          );
          
          mitigationStatusData.datasets[2].data = priorities.map((_, i) => 
            Math.round(overdue * (1 - (i * 0.15)))
          );
        }
        
      } catch (error) {
        console.error('Error fetching specialized chart data:', error);
      }
    };
    
    // Call this initially and when filters change
    fetchSpecializedChartData();
    
    // Update when filters change
    watch([() => filters.timeRange, () => filters.category, () => filters.priority], 
      () => {
        fetchSpecializedChartData();
      }
    );

    const getChartIcon = (chartType) => {
      switch(chartType) {
        case 'line': return 'fas fa-chart-line';
        case 'bar': return 'fas fa-chart-bar';
        case 'doughnut': return 'fas fa-chart-pie';
        default: return 'fas fa-chart-line';
      }
    };

    const mitigationCostData = ref(null);

    const fetchMitigationCostData = async () => {
      try {
        const timeRange = filters.timeRange || '30days';
        console.log(`Fetching mitigation cost data with period: ${timeRange}`);
        
        const baseUrl = window.location.hostname === 'localhost' 
          ? 'http://localhost:8000' 
          : '';
        
        // Include all filters
        const params = new URLSearchParams({
          timeRange: timeRange,
          category: filters.category || 'all',
          priority: filters.priority || 'all'
        });
        
        const response = await axios.get(`${baseUrl}/api/risk/mitigation-cost/?${params}`);
        
        if (response.status === 200) {
          console.log("Raw mitigation cost API response:", response.data);
          mitigationCostData.value = response.data;
          
          // Update any charts that use this data
          updateMitigationCostCharts();
        } else {
          console.error('Failed to fetch mitigation cost data:', response.status);
        }
      } catch (error) {
        console.error('Error fetching mitigation cost data:', error);
      }
    };

    const updateMitigationCostCharts = () => {
      // Update any charts that use mitigation cost data
      if (activeChart.value === 'bar' && selectedYAxis.value === 'mitigationCost') {
        barChartData.labels = mitigationCostData.value.monthlyData.map(item => item.month);
        barChartData.datasets[0].data = mitigationCostData.value.monthlyData.map(item => item.cost);
      }
    };

    // Make sure we fetch mitigation cost data when filters change
    watch(
      [
        () => filters.timeRange,
        () => filters.category, 
        () => filters.priority
      ], 
      () => {
        console.log("Filters changed, updating data");
        fetchMitigationCostData();
        fetchSpecializedChartData();
      }
    );

    // Initialize with real data fetching
    onMounted(() => {
      fetchMitigationCostData();
      fetchRiskMetrics();
    });

    // Custom options for the dynamic chart
    const customChartOptions = {
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
            font: { size: 10 },
            padding: 5
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            font: { size: 10 },
            padding: 5
          }
        }
      },
      animation: {
        duration: 800,
        easing: 'easeOutQuart'
      },
      layout: {
        padding: {
          top: 30,
          right: 8,
          bottom: 8,
          left: 8
        }
      }
    }
    
    // Custom options for donut chart in dynamic chart
    const customDonutOptions = {
      cutout: '65%',
      plugins: {
        legend: { display: false }
      },
      maintainAspectRatio: false,
      animation: {
        animateRotate: true,
        animateScale: true,
        duration: 800,
        easing: 'easeOutCubic'
      },
      layout: {
        padding: {
          top: 30,
          right: 0,
          bottom: 0,
          left: 0
        }
      }
    }

    return {
      lineChartData,
      lineChartOptions,
      donutChartData,
      donutChartOptions,
      barChartData,
      barChartOptions,
      showRiskDetails,
      toggleRiskDetails,
      chartTypes,
      activeChart,
      selectedXAxis,
      selectedYAxis,
      metrics,
      filters,
      hasData,
      fetchRiskMetrics,
      yAxisOptions,
      fetchDashboardData,
      onAxisChange,
      categoryDistributionData,
      riskTrendData,
      mitigationStatusData,
      getHighestCategory,
      getTrendText,
      getTrendClass,
      getMitigationRate,
      getChartIcon,
      fetchMitigationCostData,
      updateMitigationCostCharts,
      customChartOptions,
      customDonutOptions
    }
  }
}
</script>

<style scoped>
@import './RiskDashboard.css';
.chart-tabs {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}
.chart-tab-btn {
  background: none;
  border: none;
  font-size: 1rem;
  color: #888;
  cursor: pointer;
  padding: 4px 8px;
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
  min-height: 280px;
  margin: 0 auto 24px auto;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.04);
  background: #fff;
}
.chart-performance-summary {
  margin-top: 16px;
  font-size: 0.9rem;
}
.dashboard-main-row {
  margin-top: 24px;
}
.no-data-message {
  width: 100%;
  padding: 20px;
  text-align: center;
  background: white;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  font-size: 15px;
  color: var(--text-secondary);
  grid-column: 1 / -1;
}
.summary-value.empty {
  font-size: 14px;
  color: #9ca3af;
  font-style: italic;
}

/* Chart container specific styles */
.chart-container {
  position: relative;
  width: 100%;
  height: 220px;
  min-height: 200px;
  max-height: 220px;
}

/* New styles for enhanced dashboard */
.dashboard-charts {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
}

.card-header {
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chart-insights {
  margin-top: 15px;
  padding-top: 12px;
  border-top: 1px solid rgba(0,0,0,0.05);
}

.insight-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.insight-label {
  font-weight: 500;
  color: var(--text-secondary);
}

.insight-value {
  font-weight: 600;
}

.insight-value.positive {
  color: var(--success-color);
}

.insight-value.negative {
  color: var(--danger-color);
}

@media screen and (max-width: 1200px) {
  .dashboard-charts {
    grid-template-columns: 1fr;
  }
}
</style>
