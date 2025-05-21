<template>
  <div class="dashboard-container">
    <h1>Risk Dashboard</h1>
    
    <!-- Filter Section -->
    <div class="filters">
      
      <div class="filter">
        <label>Category</label>
        <select v-model="selectedCategory" @change="fetchRiskMetrics()">
          <option value="">All</option>
          <option>Operational</option>
          <option>Compliance</option>
          <option>IT Security</option>
        </select>
      </div>
      <div class="filter">
        <label>Priority</label>
        <select>
          <option value="">All</option>
          <option>Critical</option>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>
      </div>
    </div>
    
    <!-- Metrics Cards -->
    <div class="metrics">
      <div class="metric-card">
        <h3>Total Risks</h3>
        <div class="metric-value">{{ metrics.total }}</div>
      </div>
      <div class="metric-card">
        <h3>Open Risks</h3>
        <div class="metric-value">{{ metrics.open }}</div>
      </div>
      <div class="metric-card">
        <h3>In Progress Risks</h3>
        <div class="metric-value">{{ metrics.inProgress }}</div>
      </div>
      <div class="metric-card">
        <h3>Closed Risks</h3>
        <div class="metric-value">{{ metrics.closed }}</div>
      </div>
    </div>
    
    <!-- Charts Section -->
    <div class="charts">
      <div class="chart-container">
        <div class="chart-toggle-row">
          <button :class="['chart-toggle-btn', statusChartType==='line' ? 'active' : '']" @click="statusChartType='line'">
            <i class="fas fa-chart-line"></i>
          </button>
          <button :class="['chart-toggle-btn', statusChartType==='bar' ? 'active' : '']" @click="statusChartType='bar'">
            <i class="fas fa-chart-bar"></i>
          </button>
          <button :class="['chart-toggle-btn', statusChartType==='doughnut' ? 'active' : '']" @click="statusChartType='doughnut'">
            <i class="fas fa-dot-circle"></i>
          </button>
        </div>
        <h3>Risk by Status</h3>
        <canvas ref="statusChart"></canvas>
        <div class="chart-legend">
          <div class="legend-item"><span class="legend-color open"></span> Open</div>
          <div class="legend-item"><span class="legend-color in-progress"></span> In Progress</div>
          <div class="legend-item"><span class="legend-color closed"></span> Closed</div>
        </div>
      </div>
      
      <div class="chart-container">
        <div class="chart-toggle-row">
          <button :class="['chart-toggle-btn', categoryChartType==='bar' ? 'active' : '']" @click="categoryChartType='bar'">
            <i class="fas fa-chart-bar"></i>
          </button>
          <button :class="['chart-toggle-btn', categoryChartType==='doughnut' ? 'active' : '']" @click="categoryChartType='doughnut'">
            <i class="fas fa-dot-circle"></i>
          </button>
          <button :class="['chart-toggle-btn', categoryChartType==='pie' ? 'active' : '']" @click="categoryChartType='pie'">
            <i class="fas fa-chart-pie"></i>
          </button>
        </div>
        <h3>Risk by Category</h3>
        <canvas ref="categoryChart"></canvas>
      </div>
      
      <div class="chart-container">
        <h3>Risk Heat Map</h3>
        <canvas ref="heatmapChart"></canvas>
      </div>
    </div>
    
    <!-- New Charts Row -->
    <div class="charts charts-extra">
      <div class="chart-container">
        <div class="chart-toggle-row">
          <button :class="['chart-toggle-btn', categoryPieChartType==='pie' ? 'active' : '']" @click="categoryPieChartType='pie'">
            <i class="fas fa-chart-pie"></i>
          </button>
          <button :class="['chart-toggle-btn', categoryPieChartType==='doughnut' ? 'active' : '']" @click="categoryPieChartType='doughnut'">
            <i class="fas fa-dot-circle"></i>
          </button>
        </div>
        <h3>Risk Category by Total Risk Rating</h3>
        <canvas ref="categoryPieChart"></canvas>
      </div>
      <div class="chart-container">
        <div class="chart-toggle-row">
          <button :class="['chart-toggle-btn', ratingDonutChartType==='doughnut' ? 'active' : '']" @click="ratingDonutChartType='doughnut'">
            <i class="fas fa-dot-circle"></i>
          </button>
          <button :class="['chart-toggle-btn', ratingDonutChartType==='pie' ? 'active' : '']" @click="ratingDonutChartType='pie'">
            <i class="fas fa-chart-pie"></i>
          </button>
        </div>
        <h3>Risk Rating Breakdown</h3>
        <canvas ref="ratingDonutChart"></canvas>
      </div>
    </div>
    
    <!-- Risk Instances Table -->
    <div class="risk-table-container">
      <h3>Risk Instances</h3>
      <table class="risk-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Risk Instances</th>
            <th>Priority</th>
            <th>Score</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>1</td>
            <td>Data Breach</td>
            <td>Critical</td>
            <td>6</td>
            <td>Open</td>
            <td><button class="view-btn">View</button></td>
          </tr>
          <tr>
            <td>2</td>
            <td>Regulatory Non-Compliancee</td>
            <td>High</td>
            <td>6</td>
            <td>Open</td>
            <td><button class="view-btn">View</button></td>
          </tr>
          <tr>
            <td>3</td>
            <td>Constrainteriote Elitroning</td>
            <td>Score</td>
            <td>5</td>
            <td>In Progresss</td>
            <td><button class="open-btn">Open</button></td>
          </tr>
          <tr>
            <td>4</td>
            <td>Intrinsic Disk Interntory</td>
            <td>Score</td>
            <td>5</td>
            <td>Open</td>
            <td><button class="in-prog-btn">In Prog</button></td>
          </tr>
          <tr>
            <td>5</td>
            <td>Regitatory Abovce Recallationn</td>
            <td>Score</td>
            <td>4</td>
            <td>In Progress</td>
            <td><button class="closed-btn">Closed</button></td>
          </tr>
          <tr>
            <td>6</td>
            <td>Recordary Overaction</td>
            <td>Closed</td>
            <td>3</td>
            <td>Open</td>
            <td><button class="open-btn">Open</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto'
import { MatrixController, MatrixElement } from 'chartjs-chart-matrix'
Chart.register(MatrixController, MatrixElement)
import axios from 'axios'

export default {
  name: 'RiskDashboard',
  data() {
    return {
      statusChartType: 'line',
      categoryChartType: 'bar',
      categoryPieChartType: 'pie',
      ratingDonutChartType: 'doughnut',
      statusChartInstance: null,
      categoryChartInstance: null,
      categoryPieChartInstance: null,
      ratingDonutChartInstance: null,
      heatmapChartInstance: null,
      selectedCategory: "",
      // Unified chart data for all chart types
      statusChartData: {
        labels: ['Open', 'In Progress', 'Closed'],
        datasets: [{
          label: 'Risks',
          data: [5, 4, 3],
          backgroundColor: ['#4285f4', '#fbbc05', '#ea4335'],
          borderColor: '#4285f4',
          fill: false,
          tension: 0.3,
          pointRadius: 5
        }]
      },
      categoryChartData: {
        labels: ['Operational', 'Compliance', 'IT Security'],
        datasets: [{
          label: 'Count',
          data: [4, 3, 5],
          backgroundColor: ['#ea4335', '#fbbc05', '#4285f4', '#34a853'],
          borderWidth: 0
        }]
      },
      categoryPieChartData: {
        labels: [
          'Competitive Risk',
          'Financial Risk',
          'Governance Risk',
          'Legal and Regulatory Risk',
          'People Risk',
          'System and Technology Risk'
        ],
        datasets: [{
          data: [2, 2, 21, 5, 29, 41],
          backgroundColor: [
            '#3366cc', '#dc3912', '#109618', '#990099', '#0099c6', '#ff9900'
          ],
          borderWidth: 0
        }]
      },
      ratingDonutChartData: {
        labels: ['Low risk', 'Medium Risk', 'High Risk', 'Critical Risk'],
        datasets: [{
          data: [46, 39, 12, 3],
          backgroundColor: ['#43a047', '#fbbc05', '#ea4335', '#d32f2f'],
          borderWidth: 0
        }]
      },
      // Matrix heatmap data
      heatmapMatrixData: [
        [25, 1, 0, 0, 1],
        [5, 0, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 2, 0, 0],
        [1, 0, 2, 0, 0]
      ],
      heatmapLabelsX: ['VERY LOW', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
      heatmapLabelsY: ['VERY LOW', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
      metrics: {
        total: 0,
        open: 0,
        inProgress: 0,
        closed: 0
      }
    }
  },
  mounted() {
    console.log('Dashboard component mounted')
    // Check if Chart is available
    console.log('Chart available:', typeof Chart !== 'undefined')
    
    try {
      this.renderStatusChart()
      this.renderCategoryChart()
      this.renderCategoryPieChart()
      this.renderRatingDonutChart()
      this.renderHeatmapScatterChart()
    } catch (error) {
      console.error('Error creating charts:', error)
    }
    this.fetchRiskMetrics()
  },
  watch: {
    statusChartType() { this.renderStatusChart() },
    categoryChartType() { this.renderCategoryChart() },
    categoryPieChartType() { this.renderCategoryPieChart() },
    ratingDonutChartType() { this.renderRatingDonutChart() }
  },
  methods: {
    renderStatusChart() {
      if (this.statusChartInstance) this.statusChartInstance.destroy()
      const ctx = this.$refs.statusChart.getContext('2d')
      let type = this.statusChartType
      if (type === 'doughnut') type = 'doughnut'
      this.statusChartInstance = new Chart(ctx, {
        type,
        data: this.statusChartData,
        options: {
          cutout: type === 'doughnut' ? '70%' : undefined,
          responsive: true,
          plugins: {
            legend: {
              display: type === 'doughnut',
              position: 'right',
              labels: { boxWidth: 18, font: { size: 14 } }
            }
          },
          scales: type === 'bar' || type === 'line' ? {
            x: { beginAtZero: true, grid: { display: false } },
            y: { beginAtZero: true, grid: { display: false } }
          } : {}
        }
      })
    },
    renderCategoryChart() {
      if (this.categoryChartInstance) this.categoryChartInstance.destroy()
      const ctx = this.$refs.categoryChart.getContext('2d')
      let type = this.categoryChartType
      if (type === 'pie' || type === 'doughnut') type = this.categoryChartType
      this.categoryChartInstance = new Chart(ctx, {
        type,
        data: this.categoryChartData,
        options: {
          cutout: type === 'doughnut' ? '70%' : undefined,
          indexAxis: type === 'bar' ? 'y' : undefined,
          responsive: true,
          plugins: {
            legend: {
              display: type === 'pie' || type === 'doughnut',
              position: 'right',
              labels: { boxWidth: 18, font: { size: 14 } }
            }
          },
          scales: type === 'bar' ? {
            x: { beginAtZero: true, grid: { display: false } },
            y: { grid: { display: false } }
          } : {}
        }
      })
    },
    renderCategoryPieChart() {
      if (this.categoryPieChartInstance) this.categoryPieChartInstance.destroy()
      const ctx = this.$refs.categoryPieChart.getContext('2d')
      let type = this.categoryPieChartType
      if (type === 'pie' || type === 'doughnut') type = this.categoryPieChartType
      this.categoryPieChartInstance = new Chart(ctx, {
        type,
        data: this.categoryPieChartData,
        options: {
          cutout: type === 'doughnut' ? '70%' : undefined,
          responsive: true,
          plugins: {
            legend: {
              display: true,
              position: 'right',
              labels: { boxWidth: 18, font: { size: 14 } }
            }
          }
        }
      })
    },
    renderRatingDonutChart() {
      if (this.ratingDonutChartInstance) this.ratingDonutChartInstance.destroy()
      const ctx = this.$refs.ratingDonutChart.getContext('2d')
      let type = this.ratingDonutChartType
      if (type === 'pie' || type === 'doughnut') type = this.ratingDonutChartType
      this.ratingDonutChartInstance = new Chart(ctx, {
        type,
        data: this.ratingDonutChartData,
        options: {
          cutout: type === 'doughnut' ? '70%' : undefined,
          responsive: true,
          plugins: {
            legend: {
              display: true,
              position: 'right',
              labels: { boxWidth: 18, font: { size: 14 } }
            }
          }
        }
      })
    },
    renderHeatmapScatterChart() {
      if (this.heatmapChartInstance) this.heatmapChartInstance.destroy()
      const ctx = this.$refs.heatmapChart.getContext('2d')
      // Example risk data: each dot is a risk (x: Likelihood, y: Impact, v: count/severity)
      const risks = [
        { x: 1, y: 5, v: 25 }, { x: 2, y: 5, v: 1 }, { x: 5, y: 5, v: 1 },
        { x: 1, y: 4, v: 5 },
        { x: 2, y: 3, v: 1 }, { x: 4, y: 3, v: 1 },
        { x: 2, y: 2, v: 1 }, { x: 3, y: 2, v: 1 },
        { x: 3, y: 1, v: 2 }, { x: 1, y: 1, v: 1 }, { x: 3, y: 5, v: 0 },
        // ... add more as needed
      ]
      function getColor(val) {
        if (val >= 20) return '#388e3c'; // deep green
        if (val >= 5) return '#43a047'; // green
        if (val === 2) return '#fbc02d'; // yellow
        if (val === 1) return '#f57c00'; // orange
        if (val === 0) return '#d32f2f'; // red
        return '#222';
      }
      this.heatmapChartInstance = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [{
            label: 'Risk Heatmap',
            data: risks,
            pointBackgroundColor: risks.map(r => getColor(r.v)),
            pointRadius: risks.map(r => Math.max(6, r.v * 1.5)),
            pointHoverRadius: risks.map(r => Math.max(8, r.v * 2)),
            showLine: false
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                title: ctx => `Likelihood: ${ctx[0].raw.x}, Impact: ${ctx[0].raw.y}`,
                label: ctx => `Count: ${ctx.raw.v}`
              }
            }
          },
          scales: {
            x: {
              min: 1, max: 5,
              title: { display: true, text: 'Likelihood', font: { size: 14 } },
              ticks: { stepSize: 1, font: { size: 13 } },
              grid: { color: '#e6e6e6' }
            },
            y: {
              min: 1, max: 5,
              title: { display: true, text: 'Impact', font: { size: 14 } },
              ticks: { stepSize: 1, font: { size: 13 } },
              grid: { color: '#e6e6e6' }
            }
          }
        }
      })
    },
    async fetchRiskMetrics() {
      try {
        console.log('Fetching risk metrics...', this.selectedCategory)
        
        // Add category parameter to URL if selected
        const url = this.selectedCategory 
          ? `http://localhost:8000/api/risk/metrics?category=${encodeURIComponent(this.selectedCategory)}`
          : 'http://localhost:8000/api/risk/metrics'
        
        const response = await axios.get(url)
        console.log('Received metrics data:', response.data)
        this.metrics = response.data
        
        // Update the statusChartData properly
        if (this.statusChartInstance) {
          this.statusChartData.datasets[0].data = [
            this.metrics.open || 0,
            this.metrics.inProgress || 0, 
            this.metrics.closed || 0
          ]
          this.statusChartInstance.update()
        }
      } catch (error) {
        console.error('Error fetching risk metrics:', error)
      }
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 0 20px 20px 20px;
  max-width: 1300px;
  margin: 0 auto;
}

h1 {
  font-size: 32px;
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
}

.filters {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
}

.filter {
  flex: 1;
}

.filter label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.filter select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
}

.metrics {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  flex: 1;
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.metric-card h3 {
  font-size: 16px;
  margin-top: 0;
  margin-bottom: 10px;
  color: #555;
}

.metric-value {
  font-size: 32px;
  font-weight: bold;
  color: #2c3e50;
}

.charts {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.chart-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  min-height: 380px;
  height: 380px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  min-width: 370px;
  width: 100%;
  max-width: 500px;
}

.chart-container canvas {
  height: 260px !important;
  max-height: 260px;
  width: 100% !important;
  min-width: 320px;
  max-width: 460px;
  display: block;
  margin: 0 auto;
}

.chart-container h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #2c3e50;
  font-size: 18px;
}

.chart-legend {
  display: flex;
  justify-content: center;
  margin-top: 15px;
  gap: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 5px;
}

.legend-color.open {
  background-color: #4285f4;
}

.legend-color.in-progress {
  background-color: #fbbc05;
}

.legend-color.closed {
  background-color: #ea4335;
}

.risk-table-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.risk-table-container h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #2c3e50;
  font-size: 18px;
}

.risk-table {
  width: 100%;
  border-collapse: collapse;
}

.risk-table th, .risk-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e6e6e6;
}

.risk-table thead th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.risk-table tbody tr:hover {
  background-color: #f8f9fa;
}

button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
}

.view-btn {
  background-color: #4285f4;
}

.open-btn {
  background-color: #34a853;
}

.in-prog-btn {
  background-color: #fbbc05;
}

.closed-btn {
  background-color: #ea4335;
}

.charts-extra {
  margin-top: 30px;
  grid-template-columns: 1fr 1fr;
}

.chart-toggle-row {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
}
.chart-toggle-btn {
  background: #f4f7fb;
  border: 1.5px solid #e0e7ef;
  border-radius: 8px;
  padding: 6px 14px;
  font-size: 1.2rem;
  color: #4285f4;
  cursor: pointer;
  transition: background 0.15s, border 0.15s;
}
.chart-toggle-btn.active, .chart-toggle-btn:hover {
  background: #eaf1fb;
  border: 1.5px solid #4285f4;
  color: #0056b3;
}
.heatmap-img {
  width: 100%;
  max-width: 420px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-top: 12px;
}
</style>
