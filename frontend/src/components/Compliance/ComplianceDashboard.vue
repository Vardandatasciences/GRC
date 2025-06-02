<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>Compliance Dashboard</h1>
      <div class="header-actions">
        <button class="refresh-btn" @click="refreshData"><i class="fas fa-sync"></i></button>
        <button class="download-btn"><i class="fas fa-download"></i></button>
      </div>
    </div>

    <div class="metrics-grid">
      <!-- Approval Rate Card -->
      <div class="metric-card">
        <div class="metric-icon compliance-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="metric-content">
          <h3>Approval Rate</h3>
          <div class="metric-value">
            <span class="percentage">{{ dashboardData.approval_rate }}%</span>
          </div>
          <div class="metric-change">
            Based on {{ dashboardData.total_count }} compliances
          </div>
        </div>
      </div>

      <!-- Active Compliances Card -->
      <div class="metric-card">
        <div class="metric-icon policies-icon">
          <i class="fas fa-file-alt"></i>
        </div>
        <div class="metric-content">
          <h3>Active Compliances</h3>
          <div class="metric-value">
            <span class="number">{{ dashboardData.status_counts.active || 0 }}</span>
          </div>
          <div class="metric-change">
            Active and Approved
          </div>
        </div>
      </div>

      <!-- Total Findings Card -->
      <div class="metric-card">
        <div class="metric-icon risk-icon">
          <i class="fas fa-list"></i>
        </div>
        <div class="metric-content">
          <h3>Total Findings</h3>
          <div class="metric-value">
            <span class="number">{{ dashboardData.total_findings }}</span>
          </div>
          <div class="metric-change">
            Across all compliances
          </div>
        </div>
      </div>

      <!-- Under Review Card -->
      <div class="metric-card">
        <div class="metric-icon review-icon">
          <i class="fas fa-clock"></i>
        </div>
        <div class="metric-content">
          <h3>Under Review</h3>
          <div class="metric-value">
            <span class="number">{{ dashboardData.status_counts.under_review }}</span>
          </div>
          <div class="metric-change">
            Pending review
          </div>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <div class="performance-chart">
        <div class="chart-header">
          <h2>Compliance Analytics</h2>
          <div class="chart-controls">
            <div class="chart-type-icons">
              <button 
                class="chart-type-btn" 
                :class="{ active: selectedChartType === 'bar' }"
                @click="changeChartType('bar')"
                title="Bar Chart"
              >
                <i class="fas fa-chart-bar"></i>
              </button>
              <button 
                class="chart-type-btn" 
                :class="{ active: selectedChartType === 'line' }"
                @click="changeChartType('line')"
                title="Line Chart"
              >
                <i class="fas fa-chart-line"></i>
              </button>
              <button 
                class="chart-type-btn" 
                :class="{ active: selectedChartType === 'pie' }"
                @click="changeChartType('pie')"
                title="Pie Chart"
              >
                <i class="fas fa-chart-pie"></i>
              </button>
              <button 
                class="chart-type-btn" 
                :class="{ active: selectedChartType === 'doughnut' }"
                @click="changeChartType('doughnut')"
                title="Doughnut Chart"
              >
                <i class="fas fa-circle-notch"></i>
              </button>
            </div>
            <div class="axis-controls">
              <div class="axis-select">
                <label>X Axis:</label>
                <select v-model="selectedXAxis" @change="fetchDashboardData">
                  <option value="Compliance">Compliance</option>
                </select>
              </div>
              <div class="axis-select">
                <label>Y Axis:</label>
                <select v-model="selectedYAxis" @change="fetchDashboardData">
                  <option value="Criticality">By Criticality</option>
                  <option value="Status">By Status</option>
                  <option value="ActiveInactive">By Active/Inactive</option>
                  <option value="ManualAutomatic">By Manual/Automatic</option>
                  <option value="MandatoryOptional">By Mandatory/Optional</option>
                  <option value="MaturityLevel">By Maturity Level</option>
                </select>
              </div>
            </div>
          </div>
        </div>
        <div class="chart-container">
          <canvas id="myChart"></canvas>
        </div>
      </div>

      <div class="recent-activity">
        <div class="activity-header">
          <h2>Recent Activity</h2>
          <button class="more-options"><i class="fas fa-ellipsis-v"></i></button>
        </div>
        <div class="activity-list">
          <div v-for="(activity, index) in recentActivities" :key="index" class="activity-item">
            <div class="activity-icon" :class="activity.type">
              <i :class="activity.icon"></i>
            </div>
            <div class="activity-details">
              <h4>{{ activity.title }}</h4>
              <p>{{ activity.description }}</p>
              <span class="activity-time">{{ activity.time }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import '@fortawesome/fontawesome-free/css/all.min.css'
import { complianceService } from '@/services/api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend
)

export default {
  name: 'ComplianceDashboard',
  data() {
    return {
      selectedChartType: 'bar',
      selectedXAxis: 'Compliance',
      selectedYAxis: 'Criticality',
      chart: null,
      chartId: 'myChart',
      api: {
        complianceService
      },
      dashboardData: {
        status_counts: {
          approved: 0,
          active: 0,
          under_review: 0
        },
        total_count: 0,
        total_findings: 0,
        approval_rate: 0
      },
      chartData: null,
      recentActivities: [
        {
          type: 'updated',
          icon: 'fas fa-sync',
          title: 'Compliance Activity',
          description: 'New compliance item added',
          time: '2 hours ago'
        },
        {
          type: 'review',
          icon: 'fas fa-clipboard-check',
          title: 'Compliance Activity',
          description: 'Compliance review completed',
          time: '5 hours ago'
        },
        {
          type: 'risk',
          icon: 'fas fa-exclamation-triangle',
          title: 'Compliance Activity',
          description: 'New compliance version created',
          time: '1 day ago'
        }
      ]
    }
  },
  mounted() {
    this.fetchDashboardData()
  },
  beforeUnmount() {
    this.destroyChart()
  },
  beforeRouteLeave(to, from, next) {
    this.destroyChart()
    next()
  },
  methods: {
    destroyChart() {
      if (this.chart) {
        this.chart.destroy()
        this.chart = null
      }
    },
    async fetchDashboardData() {
      try {
        console.log('Starting fetchDashboardData...')
        console.log('Request payload:', {
          xAxis: this.selectedXAxis,
          yAxis: this.selectedYAxis
        })

        // First fetch the dashboard data
        const [dashboardResponse, analyticsResponse] = await Promise.all([
          this.api.complianceService.getComplianceDashboard(),
          this.api.complianceService.getComplianceAnalytics({
            xAxis: this.selectedXAxis,
            yAxis: this.selectedYAxis
          })
        ])

        console.log('Dashboard API Response:', dashboardResponse.data)
        console.log('Analytics API Response:', analyticsResponse.data)

        if (dashboardResponse.data.success && analyticsResponse.data.success) {
          // Update dashboard metrics
          this.dashboardData = {
            status_counts: dashboardResponse.data.data.summary.status_counts || {},
            total_count: dashboardResponse.data.data.summary.total_count || 0,
            total_findings: dashboardResponse.data.data.summary.total_findings || 0,
            approval_rate: analyticsResponse.data.dashboardData.approval_rate || 0
          }
          
          // Update chart data
          this.chartData = analyticsResponse.data.chartData
          
          // Wait for the next tick to ensure DOM is updated
          await this.$nextTick()
          this.updateChart()
        } else {
          throw new Error(dashboardResponse.data.message || analyticsResponse.data.message || 'API request failed')
        }
      } catch (error) {
        console.error('Error in fetchDashboardData:', error)
        // Set default values on error
        this.dashboardData = {
          status_counts: {
            approved: 0,
            active: 0,
            under_review: 0
          },
          total_count: 0,
          total_findings: 0,
          approval_rate: 0
        }
        this.chartData = {
          labels: [],
          datasets: [{
            label: 'Error Loading Data',
            data: [],
            backgroundColor: 'rgba(244, 67, 54, 0.6)',
            borderColor: '#F44336',
            borderWidth: 1
          }]
        }
        await this.$nextTick()
        this.updateChart()
      }
    },
    updateChart() {
      try {
        // Destroy existing chart
        this.destroyChart()

        // Get the canvas element
        const canvas = document.getElementById(this.chartId)
        if (!canvas) {
          console.error('Chart canvas not found')
          return
        }

        // Create the chart configuration
        const config = this.createChartConfig()

        // Create new chart instance
        this.chart = new ChartJS(canvas, config)
      } catch (error) {
        console.error('Error in updateChart:', error)
        this.chart = null
      }
    },
    createChartConfig() {
      if (!this.chartData) {
        return {
          type: this.selectedChartType,
          data: {
            labels: [],
            datasets: [{
              label: 'No Data',
              data: [],
              backgroundColor: 'rgba(200, 200, 200, 0.5)',
              borderColor: '#ccc',
              borderWidth: 1
            }]
          },
          options: this.getChartOptions()
        }
      }

      const dataset = {
        ...this.chartData.datasets[0],
        backgroundColor: this.getBackgroundColors(),
        borderColor: this.getBorderColors(),
        borderWidth: 1
      }

      if (this.selectedChartType === 'line') {
        dataset.tension = 0.1
        dataset.fill = false
      }

      return {
        type: this.selectedChartType,
        data: {
          labels: this.chartData.labels,
          datasets: [dataset]
        },
        options: this.getChartOptions()
      }
    },
    getChartOptions() {
      const options = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 500,
          easing: 'easeInOutQuad'
        },
        plugins: {
          legend: {
            display: ['pie', 'doughnut'].includes(this.selectedChartType),
            position: 'top'
          },
          tooltip: {
            enabled: true,
            callbacks: {
              label: (context) => {
                if (['pie', 'doughnut'].includes(this.selectedChartType)) {
                  const label = context.label || ''
                  const value = context.raw || 0
                  const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0)
                  const percentage = ((value / total) * 100).toFixed(1)
                  return `${label}: ${value} (${percentage}%)`
                }
                return `Count: ${context.raw}`
              }
            }
          }
        }
      }

      if (['bar', 'line'].includes(this.selectedChartType)) {
        options.scales = {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              precision: 0
            }
          }
        }
      }

      return options
    },
    changeChartType(newType) {
      if (this.selectedChartType === newType) {
        return
      }
      
      this.selectedChartType = newType
      this.$nextTick(() => {
        this.updateChart()
      })
    },
    getBackgroundColors() {
      const colorMaps = {
        Criticality: {
          'High': 'rgba(244, 67, 54, 0.6)',
          'Medium': 'rgba(255, 152, 0, 0.6)',
          'Low': 'rgba(76, 175, 80, 0.6)'
        },
        Status: {
          'Approved': 'rgba(76, 175, 80, 0.6)',
          'Under Review': 'rgba(255, 152, 0, 0.6)',
          'Rejected': 'rgba(244, 67, 54, 0.6)',
          'Active': 'rgba(33, 150, 243, 0.6)'
        },
        ActiveInactive: {
          'Active': 'rgba(76, 175, 80, 0.6)',
          'Inactive': 'rgba(158, 158, 158, 0.6)'
        },
        ManualAutomatic: {
          'Manual': 'rgba(33, 150, 243, 0.6)',
          'Automatic': 'rgba(156, 39, 176, 0.6)'
        },
        MandatoryOptional: {
          'Mandatory': 'rgba(244, 67, 54, 0.6)',
          'Optional': 'rgba(255, 152, 0, 0.6)'
        },
        MaturityLevel: {
          'Initial': 'rgba(244, 67, 54, 0.6)',
          'Developing': 'rgba(255, 152, 0, 0.6)',
          'Defined': 'rgba(255, 235, 59, 0.6)',
          'Managed': 'rgba(76, 175, 80, 0.6)',
          'Optimizing': 'rgba(33, 150, 243, 0.6)'
        }
      }

      return this.chartData?.labels?.map(label => 
        colorMaps[this.selectedYAxis.replace('By ', '')][label] || 'rgba(158, 158, 158, 0.6)'
      ) || []
    },
    getBorderColors() {
      const colorMaps = {
        Criticality: {
          'High': '#F44336',
          'Medium': '#FF9800',
          'Low': '#4CAF50'
        },
        Status: {
          'Approved': '#4CAF50',
          'Under Review': '#FF9800',
          'Rejected': '#F44336',
          'Active': '#2196F3'
        },
        ActiveInactive: {
          'Active': '#4CAF50',
          'Inactive': '#9E9E9E'
        },
        ManualAutomatic: {
          'Manual': '#2196F3',
          'Automatic': '#9C27B0'
        },
        MandatoryOptional: {
          'Mandatory': '#F44336',
          'Optional': '#FF9800'
        },
        MaturityLevel: {
          'Initial': '#F44336',
          'Developing': '#FF9800',
          'Defined': '#FFEB3B',
          'Managed': '#4CAF50',
          'Optimizing': '#2196F3'
        }
      }

      return this.chartData?.labels?.map(label => 
        colorMaps[this.selectedYAxis.replace('By ', '')][label] || '#9E9E9E'
      ) || []
    },
    refreshData() {
      this.fetchDashboardData()
    }
  }
}
</script>

<style>
@import './ComplianceDashboard.css';

.chart-controls {
  display: flex;
  align-items: center;
  gap: 24px;
}

.chart-type-icons {
  display: flex;
  gap: 8px;
  padding: 4px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.chart-type-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chart-type-btn:hover {
  background-color: #e2e8f0;
  color: #1e293b;
}

.chart-type-btn.active {
  background-color: #4CAF50;
  color: white;
}

.chart-type-btn i {
  font-size: 1.1rem;
}

.axis-controls {
  display: flex;
  gap: 16px;
}

.axis-select {
  display: flex;
  align-items: center;
  gap: 8px;
}

.axis-select label {
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
}

.axis-select select {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #1e293b;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.axis-select select:hover {
  border-color: #94a3b8;
}

.axis-select select:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.chart-type-select {
  display: none;
}
</style> 