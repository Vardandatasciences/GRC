<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Policy Dashboard</h2>
      <div class="dashboard-actions">
        <button class="action-btn"><i class="fas fa-sync-alt"></i></button>
        <button class="action-btn"><i class="fas fa-download"></i></button>
        <!-- <button class="action-btn primary"><i class="fas fa-plus"></i> New Policy</button> -->
      </div>
    </div>
    
    <!-- Performance Summary Cards -->
    <div class="performance-summary">
      <div class="summary-card growth">
        <div class="summary-icon"><i class="fas fa-chart-line"></i></div>
        <div class="summary-content">
          <div class="summary-label">Policy Performance</div>
          <div class="summary-value">+2.46% <span class="period">today</span></div>
          <div class="summary-trend positive">+18.67% in 1W</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-file-alt"></i></div>
        <div class="summary-content">
          <div class="summary-label">Total Policies</div>
          <div class="summary-value">134</div>
          <div class="summary-trend positive">+12 this month</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-clipboard-list"></i></div>
        <div class="summary-content">
          <div class="summary-label">Total SubPolicies</div>
          <div class="summary-value">240</div>
          <div class="summary-trend positive">+18 this month</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-exclamation-triangle"></i></div>
        <div class="summary-content">
          <div class="summary-label">Critical Issues</div>
          <div class="summary-value">7</div>
          <div class="summary-trend negative">+2 this week</div>
        </div>
      </div>
    </div>

    <!-- Main Row: Asset Performance and Recent Activity -->
    <div class="dashboard-main-row dashboard-main-row-3col" style="display: flex; width: 100%;">
      <!-- Left: Asset Performance Card -->
      <div class="dashboard-main-col asset-performance-col" style="width: 70%;">
        <div class="chart-card tabbed-chart-card">
          <div class="card-header">
            <div class="header-left">
              <span>Asset performance</span>
              <div class="axis-selectors">
                <select v-model="selectedXAxis" class="axis-select">
                  <option disabled value="">Select X Axis</option>
                  <option value="time">Time</option>
                  <option value="policies">Policies</option>
                  <option value="categories">Categories</option>
                  <option value="status">Status</option>
                </select>
                <select v-model="selectedYAxis" class="axis-select">
                  <option disabled value="">Select Y Axis</option>
                  <option value="performance">Performance</option>
                  <option value="compliance">Compliance</option>
                  <option value="risk">Risk Score</option>
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
          <div class="chart-container">
            <Line v-if="activeChart === 'line'" :data="lineChartData" :options="lineChartOptions" />
            <Bar v-if="activeChart === 'bar'" :data="barChartData" :options="barChartOptions" />
            <Doughnut v-if="activeChart === 'doughnut'" :data="donutChartData" :options="donutChartOptions" />
            <Bar v-if="activeChart === 'horizontalBar'" :data="horizontalBarChartData" :options="horizontalBarChartOptions" />
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
                <div class="activity-title">New Policy Added</div>
                <div class="activity-desc">Credit Risk Assessment Policy</div>
                <div class="activity-time">2 hours ago</div>
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-icon update"><i class="fas fa-edit"></i></div>
              <div class="activity-content">
                <div class="activity-title">Policy Updated</div>
                <div class="activity-desc">Loan Processing Policy</div>
                <div class="activity-time">Yesterday</div>
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-icon alert"><i class="fas fa-exclamation-circle"></i></div>
              <div class="activity-content">
                <div class="activity-title">Compliance Alert</div>
                <div class="activity-desc">Documentation Policy needs review</div>
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
import { ref, reactive, watch } from 'vue'
import { Chart, ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js'
import { Doughnut, Bar, Line } from 'vue-chartjs'
import loanLogo from '../../assets/loan_logo1.svg'
import '@fortawesome/fontawesome-free/css/all.min.css'

Chart.register(ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

export default {
  name: 'PolicyDashboard',
  components: {
    Doughnut,
    Bar,
    Line
  },
  setup() {
    const showPolicyDetails = ref(true)
    const selectedXAxis = ref('time')
    const selectedYAxis = ref('performance')
    
    // Watch for axis changes and update chart data accordingly
    watch([selectedXAxis, selectedYAxis], ([newXAxis, newYAxis]) => {
      // Update chart data based on selected axes
      updateChartData(newXAxis, newYAxis)
    })

    // --- CATEGORY DATA FOR ACTIVE/INACTIVE/ON HOLD ---
    const categoryStatusData = {
      Security: { active: 12, inactive: 3, onhold: 2 },
      Compliance: { active: 10, inactive: 4, onhold: 1 },
      Risk: { active: 8, inactive: 6, onhold: 2 },
      Operations: { active: 14, inactive: 2, onhold: 1 },
      Governance: { active: 9, inactive: 5, onhold: 3 }
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
        horizontalBarChartData.labels = labels
        horizontalBarChartData.datasets = [
          {
            label: 'Active',
            data: labels.map(l => categoryStatusData[l]?.active || 0),
            backgroundColor: '#4ade80',
            borderRadius: 6,
            barPercentage: 0.5,
            categoryPercentage: 0.7
          },
          {
            label: 'Inactive',
            data: labels.map(l => categoryStatusData[l]?.inactive || 0),
            backgroundColor: '#f87171',
            borderRadius: 6,
            barPercentage: 0.5,
            categoryPercentage: 0.7
          },
          {
            label: 'On Hold',
            data: labels.map(l => categoryStatusData[l]?.onhold || 0),
            backgroundColor: '#fbbf24',
            borderRadius: 6,
            barPercentage: 0.5,
            categoryPercentage: 0.7
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
        // Horizontal Bar
        horizontalBarChartData.labels = statusLabels
        horizontalBarChartData.datasets = [
          {
            label: getYAxisLabel(yAxis),
            data: statusData,
            backgroundColor: ['#4ade80', '#f87171', '#fbbf24'],
            borderRadius: 6,
            barPercentage: 0.5,
            categoryPercentage: 0.7
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

      // Update Horizontal Bar Chart
      horizontalBarChartData.labels = labels
      horizontalBarChartData.datasets[0].data = data
      horizontalBarChartData.datasets[0].label = getYAxisLabel(yAxis)
    }

    const getYAxisLabel = (yAxis) => {
      switch(yAxis) {
        case 'performance': return 'Performance Score'
        case 'compliance': return 'Compliance Rate'
        case 'risk': return 'Risk Score'
        default: return 'Value'
      }
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
        case 'policies':
          return ['ISO 27001', 'NIST 8000', 'GDPR', 'PCI DSS', 'HIPAA']
        case 'categories':
          return ['Security', 'Compliance', 'Risk', 'Operations', 'Governance']
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
      { type: 'horizontalBar', icon: 'fas fa-align-left', label: 'Horizontal Bar' }
    ];
    const activeChart = ref('line');
    
    // Line Chart Data
    const lineChartData = reactive({
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Policy Performance',
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
    
    // Bar Chart Data
    const barChartData = reactive({
      labels: ['ISO 27001', 'NIST 8000'],
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
      }
    }
    
    // Horizontal Bar Chart Data
    const horizontalBarChartData = reactive({
      labels: [
        'Financial policy',
        'Loan policy',
        'Service policy',
        'Credit policy',
        'Risk policy'
      ],
      datasets: [{
        label: 'Active',
        data: [8, 8, 9, 5, 6],
        backgroundColor: '#4ade80',
        borderRadius: 6,
        barPercentage: 0.5,
        categoryPercentage: 0.7
      }]
    })
    
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

    const togglePolicyDetails = () => {
      showPolicyDetails.value = !showPolicyDetails.value
    }

    const policyProgress = [
      { name: 'Loan Processing', percent: 48, status: 'Completed' },
      { name: 'Credit Assessment', percent: 68, status: 'Completed' },
      { name: 'Risk Evaluation', percent: 78, status: 'Completed' },
      { name: 'Documentation', percent: 90, status: 'Completed' },
      { name: 'Compliance Check', percent: 0, status: 'Work in progress' }
    ]

    // Initialize chart data
    updateChartData(selectedXAxis.value, selectedYAxis.value)

    return {
      policyProgress,
      lineChartData,
      lineChartOptions,
      donutChartData,
      donutChartOptions,
      barChartData,
      barChartOptions,
      horizontalBarChartData,
      horizontalBarChartOptions,
      loanLogo,
      showPolicyDetails,
      togglePolicyDetails,
      chartTypes,
      activeChart,
      selectedXAxis,
      selectedYAxis
    }
  }
}
</script>

<style scoped>
@import './PolicyDashboard.css';
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