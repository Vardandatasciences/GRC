<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h2 class="dashboard-heading">Auditor Dashboard</h2>
      <div class="dashboard-actions">
        <button class="action-btn"><i class="fas fa-sync-alt"></i></button>
        <button class="action-btn"><i class="fas fa-download"></i></button>
        <!-- <button class="action-btn primary"><i class="fas fa-plus"></i> New Policy</button> -->
      </div>
    </div>
    
    <!-- Performance Summary Cards -->
    <div class="performance-summary">
      <div class="summary-card growth">
        <div class="summary-icon"><i class="fas fa-clipboard-check"></i></div>
        <div class="summary-content">
          <div class="summary-label">Audit Completion Rate</div>
          <div class="summary-value">+8.2% <span class="period">this month</span></div>
          <div class="summary-trend positive">+18.67% vs last month</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-tasks"></i></div>
        <div class="summary-content">
          <div class="summary-label">Total Audits</div>
          <div class="summary-value">42</div>
          <div class="summary-trend positive">+5 this month</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-hourglass-half"></i></div>
        <div class="summary-content">
          <div class="summary-label">Pending Reviews</div>
          <div class="summary-value">8</div>
          <div class="summary-trend negative">+2 since last week</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon"><i class="fas fa-exclamation-triangle"></i></div>
        <div class="summary-content">
          <div class="summary-label">Critical Findings</div>
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
            <span class="chart-title">Asset performance</span>
            
            <div class="chart-controls">
              <div class="axis-selectors">
                <select v-model="selectedXAxis" class="axis-select">
                  <option value="time">Time</option>
                  <option value="frameworks">Frameworks</option>
                  <option value="categories">Categories</option>
                  <option value="status">Status</option>
                </select>
                <select v-model="selectedYAxis" class="axis-select">
                  <option value="completion">Performance</option>
                  <option value="compliance">Compliance Rate</option>
                  <option value="findings">Finding Count</option>
                </select>
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
            <h3>Recent Audit Activity</h3>
            <button class="card-action"><i class="fas fa-ellipsis-v"></i></button>
          </div>
          <div class="activity-list">
            <div class="activity-item">
              <div class="activity-icon"><i class="fas fa-check-circle"></i></div>
              <div class="activity-content">
                <div class="activity-title">Audit Completed</div>
                <div class="activity-desc">ISO 27001 - Information Security</div>
                <div class="activity-time">2 hours ago</div>
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-icon update"><i class="fas fa-sync-alt"></i></div>
              <div class="activity-content">
                <div class="activity-title">Review Received</div>
                <div class="activity-desc">NIST 800-53 Compliance Audit</div>
                <div class="activity-time">Yesterday</div>
              </div>
            </div>
            <div class="activity-item">
              <div class="activity-icon alert"><i class="fas fa-exclamation-circle"></i></div>
              <div class="activity-content">
                <div class="activity-title">Due Date Approaching</div>
                <div class="activity-desc">GDPR Data Protection Assessment</div>
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
import '@fortawesome/fontawesome-free/css/all.min.css'

Chart.register(ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

export default {
  name: 'AuditorDashboard',
  components: {
    Doughnut,
    Bar,
    Line
  },
  setup() {
    const selectedXAxis = ref('time')
    const selectedYAxis = ref('completion')
    
    // Watch for axis changes and update chart data accordingly
    watch([selectedXAxis, selectedYAxis], ([newXAxis, newYAxis]) => {
      // Update chart data based on selected axes
      updateChartData(newXAxis, newYAxis)
    })

    // --- AUDIT STATUS DATA BY CATEGORY ---
    const auditStatusData = {
      'ISO 27001': { completed: 12, inProgress: 3, yetToStart: 2 },
      'NIST 800-53': { completed: 10, inProgress: 4, yetToStart: 1 },
      'GDPR': { completed: 8, inProgress: 6, yetToStart: 2 },
      'PCI DSS': { completed: 14, inProgress: 2, yetToStart: 1 },
      'HIPAA': { completed: 9, inProgress: 5, yetToStart: 3 }
    }

    const updateChartData = (xAxis, yAxis) => {
      const labels = getLabelsForXAxis(xAxis)
      let data = getDataForYAxis(yAxis)
      
      // If frameworks, use status split
      if (xAxis === 'frameworks') {
        // For donut: sum all completed/inProgress/yetToStart
        const completed = Object.values(auditStatusData).reduce((a, c) => a + c.completed, 0)
        const inProgress = Object.values(auditStatusData).reduce((a, c) => a + c.inProgress, 0)
        const yetToStart = Object.values(auditStatusData).reduce((a, c) => a + c.yetToStart, 0)
        donutChartData.labels = ['Completed', 'In Progress', 'Yet To Start']
        donutChartData.datasets[0].data = [completed, inProgress, yetToStart]
        donutChartData.datasets[0].backgroundColor = ['#4ade80', '#fbbf24', '#f87171']

        // For bar/horizontal bar: show each framework split
        barChartData.labels = labels
        barChartData.datasets = [
          {
            label: 'Completed',
            data: labels.map(l => auditStatusData[l]?.completed || 0),
            backgroundColor: '#4ade80',
            stack: 'Stack 0',
            borderRadius: 4
          },
          {
            label: 'In Progress',
            data: labels.map(l => auditStatusData[l]?.inProgress || 0),
            backgroundColor: '#fbbf24',
            stack: 'Stack 0',
            borderRadius: 4
          },
          {
            label: 'Yet To Start',
            data: labels.map(l => auditStatusData[l]?.yetToStart || 0),
            backgroundColor: '#f87171',
            stack: 'Stack 0',
            borderRadius: 4
          }
        ]
        horizontalBarChartData.labels = labels
        horizontalBarChartData.datasets = [
          {
            label: 'Completed',
            data: labels.map(l => auditStatusData[l]?.completed || 0),
            backgroundColor: '#4ade80',
            borderRadius: 6,
            barPercentage: 0.5,
            categoryPercentage: 0.7
          },
          {
            label: 'In Progress',
            data: labels.map(l => auditStatusData[l]?.inProgress || 0),
            backgroundColor: '#fbbf24',
            borderRadius: 6,
            barPercentage: 0.5,
            categoryPercentage: 0.7
          },
          {
            label: 'Yet To Start',
            data: labels.map(l => auditStatusData[l]?.yetToStart || 0),
            backgroundColor: '#f87171',
            borderRadius: 6,
            barPercentage: 0.5,
            categoryPercentage: 0.7
          }
        ]
        // For line: show only completed for demo
        lineChartData.labels = labels
        lineChartData.datasets[0].data = labels.map(l => auditStatusData[l]?.completed || 0)
        lineChartData.datasets[0].label = 'Completed'
        return
      }
      // If status, show Completed/InProgress/YetToStart as X axis
      if (xAxis === 'status') {
        const statusLabels = ['Completed', 'In Progress', 'Yet To Start']
        // Sum for each status across all frameworks
        const completed = Object.values(auditStatusData).reduce((a, c) => a + c.completed, 0)
        const inProgress = Object.values(auditStatusData).reduce((a, c) => a + c.inProgress, 0)
        const yetToStart = Object.values(auditStatusData).reduce((a, c) => a + c.yetToStart, 0)
        const statusData = [completed, inProgress, yetToStart]
        // Donut
        donutChartData.labels = statusLabels
        donutChartData.datasets[0].data = statusData
        donutChartData.datasets[0].backgroundColor = ['#4ade80', '#fbbf24', '#f87171']
        // Bar
        barChartData.labels = statusLabels
        barChartData.datasets = [
          {
            label: getYAxisLabel(yAxis),
            data: statusData,
            backgroundColor: ['#4ade80', '#fbbf24', '#f87171'],
            borderRadius: 4
          }
        ]
        // Horizontal Bar
        horizontalBarChartData.labels = statusLabels
        horizontalBarChartData.datasets = [
          {
            label: getYAxisLabel(yAxis),
            data: statusData,
            backgroundColor: ['#4ade80', '#fbbf24', '#f87171'],
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
        case 'completion': return 'Completion Rate'
        case 'compliance': return 'Compliance Rate'
        case 'findings': return 'Finding Count'
        default: return 'Value'
      }
    }

    const getBarChartDatasets = (yAxis) => {
      const baseData = getDataForYAxis(yAxis)
      return [
        {
          label: 'Major Findings',
          data: baseData.map(val => Math.round(val * 0.35)),
          backgroundColor: '#f87171',
          stack: 'Stack 0',
          borderRadius: 4
        },
        {
          label: 'Minor Findings',
          data: baseData.map(val => Math.round(val * 0.65)),
          backgroundColor: '#fbbf24',
          stack: 'Stack 0',
          borderRadius: 4
        }
      ]
    }

    const getLabelsForXAxis = (xAxis) => {
      switch(xAxis) {
        case 'time':
          return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
        case 'frameworks':
          return ['ISO 27001', 'NIST 800-53', 'GDPR', 'PCI DSS', 'HIPAA']
        case 'categories':
          return ['Information Security', 'Data Protection', 'Risk Assessment', 'Access Control', 'Change Management']
        case 'status':
          return ['Completed', 'In Progress', 'Yet To Start']
        default:
          return []
      }
    }

    const getDataForYAxis = (yAxis) => {
      switch(yAxis) {
        case 'completion':
          return [65, 70, 75, 78, 82, 85, 88]
        case 'compliance':
          return [92, 90, 88, 86, 89, 91, 93]
        case 'findings':
          return [15, 12, 18, 22, 16, 14, 17]
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
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
      datasets: [{
        label: 'Audit Completion Rate',
        data: [65, 70, 75, 78, 82, 85, 88],
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
      labels: ['Completed', 'In Progress', 'Yet To Start'],
      datasets: [{
        data: [53, 32, 15],
        backgroundColor: ['#4ade80', '#fbbf24', '#f87171'],
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
      labels: ['ISO 27001', 'NIST 800-53'],
      datasets: [
        {
          label: 'Completed',
          data: [12, 10],
          backgroundColor: '#4ade80',
          stack: 'Stack 0',
          borderRadius: 4
        },
        {
          label: 'In Progress',
          data: [3, 4],
          backgroundColor: '#fbbf24',
          stack: 'Stack 0',
          borderRadius: 4
        },
        {
          label: 'Yet To Start',
          data: [2, 1],
          backgroundColor: '#f87171',
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
        'Information Security',
        'Data Protection',
        'Risk Assessment',
        'Access Control',
        'Change Management'
      ],
      datasets: [{
        label: 'Completion Rate (%)',
        data: [86, 92, 78, 84, 73],
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

    // Initialize chart data
    updateChartData(selectedXAxis.value, selectedYAxis.value)

    return {
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
      selectedYAxis
    }
  }
}
</script>

<style scoped>
@import './AuditorDashboard.css';
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