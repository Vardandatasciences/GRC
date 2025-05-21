<template>
  <div class="dashboard-container">
    <h2 class="dashboard-heading">Dashboard</h2>
    <div class="dashboard-main-row">
      <div class="dashboard-main-left">
        <div class="policy-card">
          <div class="policy-card-header">
            <img :src="loanLogo" alt="Loan Policy" class="policy-card-icon" />
            <div class="policy-card-title">Loan Policy</div>
            <div class="policy-card-upload">
              <i class="fas fa-upload"></i>
            </div>
          </div>
          <div class="policy-card-progressbar">
            <div class="progress-bar-main">
              <div class="progress-bar-fill" style="width: 48%"></div>
            </div>
            <span class="policy-card-progress-label">48% Latest results</span>
          </div>
          <div class="policy-card-analytics">
            <span>Analytics</span>
            <span class="policy-card-analytics-arrow">▼</span>
          </div>
          <div class="policy-card-list">
            <div class="policy-card-list-header">
              <span>Performance</span>
            </div>
            <div v-for="(item, idx) in policyProgress" :key="idx" class="policy-card-list-row">
              <span class="policy-card-list-label">{{ item.name }}</span>
              <div class="policy-card-list-progress">
                <div class="progress-bar-sub">
                  <div class="progress-bar-fill-sub" :style="{ width: `${item.percent}%` }"></div>
                </div>
                <span :class="['policy-card-list-status', item.status === 'Completed' ? 'completed' : 'inprogress']">
                  {{ item.status }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="dashboard-main-right">
        <div class="dashboard-summary-cards">
          <div class="summary-card">
            <div class="summary-title">Total Policies</div>
            <div class="summary-value">134</div>
          </div>
          <div class="summary-card">
            <div class="summary-title">Total SubPolicies</div>
            <div class="summary-value">240</div>
          </div>
        </div>
        <div class="dashboard-charts-row">
          <div class="dashboard-chart-card donut">
            <div class="donut-title">Policy status</div>
            <div style="width: 100%; max-width: 160px; height: 140px; margin: 0 auto">
              <Doughnut :data="donutData" :options="donutOptions" :height="140" />
            </div>
            <div class="donut-legend">
              <span><span class="legend-dot active"></span>Active</span>
              <span><span class="legend-dot inactive"></span>Inactive</span>
              <span><span class="legend-dot onhold"></span>Onhold</span>
            </div>
          </div>
          <div class="dashboard-chart-card bar">
            <div class="bar-title">Policy List</div>
            <div style="width: 100%; max-width: 160px; height: 140px; margin: 0 auto">
              <Bar :data="barData" :options="barOptions" :height="140" />
            </div>
            <div class="bar-legend">
              <span><span class="legend-dot active"></span>Active</span>
              <span><span class="legend-dot inactive"></span>Inactive</span>
              <span><span class="legend-dot onhold"></span>Onhold</span>
            </div>
          </div>
        </div>
        <div class="dashboard-chart-card horizontal-bar">
          <div class="horizontal-bar-title">Policy list</div>
          <div style="width: 100%; max-width: 600px; height: 60px; margin: 0 auto">
            <Bar :data="horizontalBarData" :options="horizontalBarOptions" :height="60" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { Chart, ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { Doughnut, Bar } from 'vue-chartjs'
import loanLogo from '../../assets/loan_logo1.svg'
import '@fortawesome/fontawesome-free/css/all.min.css'

Chart.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

export default {
  name: 'PolicyDashboard',
  components: {
    Doughnut,
    Bar
  },
  setup() {
    const currentIndex = ref(0)
    const isHovering = ref(null)
    const policyListRef = ref(null)

    const policyProgress = [
      { name: 'Loan Processing', percent: 48, status: 'Completed' },
      { name: 'Credit Assessment', percent: 68, status: 'Completed' },
      { name: 'Risk Evaluation', percent: 78, status: 'Completed' },
      { name: 'Documentation', percent: 90, status: 'Completed' },
      { name: 'Compliance Check', percent: 0, status: 'Work in progress' }
    ]

    const donutData = {
      labels: ['Active', 'Inactive', 'Onhold'],
      datasets: [
        {
          data: [60, 25, 15],
          backgroundColor: ['#b6f7b0', '#ffb3b3', '#fff7b0'],
          borderWidth: 0
        }
      ]
    }

    const donutOptions = {
      cutout: '70%',
      plugins: {
        legend: { display: false, labels: { font: { size: 10 } } }
      },
      maintainAspectRatio: true
    }

    const barData = {
      labels: ['ISO 27001', 'NIST 8000'],
      datasets: [
        {
          label: 'Active',
          data: [8, 5],
          backgroundColor: '#b6f7b0',
          stack: 'Stack 0'
        },
        {
          label: 'Inactive',
          data: [6, 7],
          backgroundColor: '#ffb3b3',
          stack: 'Stack 0'
        },
        {
          label: 'Onhold',
          data: [3, 0],
          backgroundColor: '#fff7b0',
          stack: 'Stack 0'
        }
      ]
    }

    const barOptions = {
      plugins: { legend: { display: false, labels: { font: { size: 10 } } } },
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        x: { stacked: true, grid: { display: false }, ticks: { color: '#222', font: { size: 10 } } },
        y: { stacked: true, grid: { display: false }, ticks: { color: '#222', font: { size: 10 } } }
      }
    }

    const horizontalBarData = {
      labels: [
        'Financial policy',
        'Loan policy',
        'Service policy',
        'Credit policy',
        'Risk policy'
      ],
      datasets: [
        {
          label: 'Active',
          data: [8, 8, 9, 5, 6],
          backgroundColor: '#b6f7b0',
          borderRadius: 6,
          barPercentage: 0.5,
          categoryPercentage: 0.7
        }
      ]
    }

    const horizontalBarOptions = {
      indexAxis: 'x',
      plugins: {
        legend: { display: false, labels: { font: { size: 10 } } }
      },
      scales: {
        x: {
          ticks: {
            color: '#222',
            font: { size: 10 },
            callback: function(value, index) {
              return horizontalBarData.labels[index]
            },
            maxRotation: 45,
            minRotation: 45
          },
          grid: { display: false }
        },
        y: {
          beginAtZero: true,
          grid: { display: false },
          ticks: { color: '#222', font: { size: 10 } }
        }
      },
      maintainAspectRatio: true
    }

    return {
      currentIndex,
      isHovering,
      policyListRef,
      policyProgress,
      donutData,
      donutOptions,
      barData,
      barOptions,
      horizontalBarData,
      horizontalBarOptions,
      loanLogo
    }
  }
}
</script>

<style scoped>
/* Import the existing CSS file */
@import './PolicyDashboard.css';
</style> 