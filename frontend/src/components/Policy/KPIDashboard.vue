<template>
  <div class="kpi-dashboard">
    <div class="dashboard-header">
      <h1>Policy KPI Dashboard</h1>
      <button class="refresh-button" @click="fetchKPIData" :class="{ 'loading': loading }">
        <i class="fas fa-sync-alt"></i>
        Refresh
      </button>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loader"></div>
      <p>Loading KPI data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
      <button @click="fetchKPIData" class="retry-button">
        <i class="fas fa-redo"></i> Retry
      </button>
    </div>

    <!-- Content -->
    <div v-else class="dashboard-content">
      <div class="kpi-section">
        <div class="kpi-row">
          <!-- Active Policies KPI Card -->
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon">
                <i class="fas fa-file-alt"></i>
              </div>
              <h3>Active Policies</h3>
            </div>
            <div class="kpi-body">
              <div class="kpi-visualization">
                <div class="circular-progress"
                  :style="{
                    '--progress-color': getProgressColor,
                    '--progress-value': progressPercentage * 3.6 + 'deg'
                  }"
                >
                  <div class="circular-progress-inner">
                    <div class="kpi-value">{{ kpiData.active_policies || 0 }}</div>
                    <div class="kpi-label">Active</div>
                  </div>
                </div>
                <div class="kpi-details">
                  <div class="detail-item">
                    <div class="detail-info">
                      <span class="detail-label">Total Policies</span>
                      <i class="fas fa-info-circle info-icon" title="Total number of policies in the system"></i>
                    </div>
                    <span class="detail-value">{{ kpiData.total_policies || 0 }}</span>
                  </div>
                  <div class="detail-item">
                    <div class="detail-info">
                      <span class="detail-label">Active Rate</span>
                      <i class="fas fa-info-circle info-icon" title="Percentage of total policies that are currently active"></i>
                    </div>
                    <span class="detail-value">{{ getUtilizationRate }}%</span>
                  </div>
                  <div class="trend-section">
                    <div class="trend-header">
                      <span class="trend-label">12 Month Trend</span>
                      <span class="trend-indicator" :class="trendDirection">
                        <i :class="[
                          'fas',
                          trendDirection === 'up' ? 'fa-arrow-up' : 
                          trendDirection === 'down' ? 'fa-arrow-down' : 
                          'fa-minus'
                        ]"></i>
                      </span>
                    </div>
                    <div class="sparkline-container">
                      <canvas id="trendChart"></canvas>
                    </div>
                  </div>
                  <div class="detail-item status-breakdown">
                    <div class="status-title">Status Breakdown</div>
                    <div class="status-row">
                      <span class="status-label">
                        <span class="status-dot active"></span>
                        Active
                      </span>
                      <span class="status-value">{{ kpiData.active_policies || 0 }}</span>
                    </div>
                    <div class="status-row">
                      <span class="status-label">
                        <span class="status-dot inactive"></span>
                        Inactive
                      </span>
                      <span class="status-value">{{ getInactivePolicies }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Policy Acknowledgement Rate KPI Card -->
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon">
                <i class="fas fa-check-circle"></i>
              </div>
              <h3>Policy Acknowledgement Rate</h3>
            </div>
            <div class="kpi-body">
              <div class="acknowledgement-table">
                <div class="table-header">
                  <span>Policy Name</span>
                  <span>Acknowledgement Rate</span>
                </div>
                <div class="table-body">
                  <template v-if="kpiData.top_acknowledged_policies">
                    <div v-for="policy in kpiData.top_acknowledged_policies" 
                         :key="policy.policy_id" 
                         class="table-row">
                      <div class="policy-info">
                        <span class="policy-name">{{ policy.policy_name }}</span>
                        <div class="policy-stats">
                          <span class="acknowledged-count">{{ policy.acknowledged_count }}</span>
                          <span class="total-users">/ {{ policy.total_users }}</span>
                        </div>
                      </div>
                      <div class="progress-container">
                        <div class="progress-bar">
                          <div class="progress-fill" 
                               :style="{ width: policy.acknowledgement_rate + '%' }"
                               :class="getAcknowledgementClass(policy.acknowledgement_rate)">
                          </div>
                        </div>
                        <span class="progress-text">{{ policy.acknowledgement_rate }}%</span>
                      </div>
                    </div>
                  </template>
                  <div v-else class="no-data">
                    No acknowledgement data available
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Policy Coverage Rate KPI Card -->
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon">
                <i class="fas fa-chart-bar"></i>
              </div>
              <h3>Policy Coverage Rate</h3>
            </div>
            <div class="kpi-body">
              <div class="coverage-container">
                <div class="coverage-overview">
                  <div class="overall-coverage">
                    <div class="overall-label">Average Coverage</div>
                    <div class="overall-value">{{ kpiData.coverage_metrics?.overall_coverage_rate || 0 }}%</div>
                  </div>
                </div>
                <div class="coverage-bars">
                  <div v-for="dept in kpiData.coverage_metrics?.department_coverage || []" 
                       :key="dept.department" 
                       class="coverage-bar-row">
                    <div class="bar-header">
                      <span class="department-name">{{ dept.department }}</span>
                      <span class="department-value">{{ dept.coverage_rate }}%</span>
                    </div>
                    <div class="bar-container">
                      <div class="bar-background"></div>
                      <div class="bar-fill" 
                           :style="{ 
                             width: dept.coverage_rate + '%',
                             backgroundColor: getCoverageColor(dept.coverage_rate)
                           }">
                      </div>
                    </div>
                    <div class="department-policies">{{ dept.total_policies }} policies</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Policy Revision Rate KPI Card -->
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon">
                <i class="fas fa-sync"></i>
              </div>
              <h3>Policy Revision Rate</h3>
            </div>
            <div class="kpi-body">
              <div class="kpi-visualization">
                <div class="donut-chart-container">
                  <canvas ref="revisionDonutChart"></canvas>
                  <div class="donut-center-text">
                    <div class="kpi-value">{{ (kpiData.revision_rate || 0).toFixed(2) }}%</div>
                    <div class="kpi-label">Revised</div>
                  </div>
                </div>
                <div class="kpi-details">
                  <div class="detail-item">
                    <div class="detail-info">
                      <span class="detail-label">Revised Policies</span>
                      <i class="fas fa-info-circle info-icon" title="Number of policies that have been revised"></i>
                    </div>
                    <span class="detail-value">{{ kpiData.revised_policies || 0 }}</span>
                  </div>
                  <div class="detail-item">
                    <div class="detail-info">
                      <span class="detail-label">Unchanged Policies</span>
                      <i class="fas fa-info-circle info-icon" title="Number of policies that have not been revised"></i>
                    </div>
                    <span class="detail-value">{{ unchangedPolicies }}</span>
                  </div>
                  <div class="detail-item">
                    <div class="detail-info">
                      <span class="detail-label">Time Period</span>
                      <i class="fas fa-info-circle info-icon" title="Time period for revision rate calculation"></i>
                    </div>
                    <span class="detail-value">{{ kpiData.measurement_period || 'Last Quarter' }}</span>
                  </div>
                  <button 
                    @click="showRevisedPolicies = true" 
                    class="drill-down-button"
                    v-if="kpiData.revised_policies > 0"
                  >
                    <i class="fas fa-list"></i>
                    View Revised Policies
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Revised Policies Modal -->
    <div v-if="showRevisedPolicies" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Revised Policies</h2>
          <button @click="showRevisedPolicies = false" class="close-button">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="revised-policies-stats">
            <div class="stat-item">
              <span class="stat-label">Total Revisions:</span>
              <span class="stat-value">{{ kpiData.total_revisions }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Policies with Multiple Revisions:</span>
              <span class="stat-value">{{ kpiData.policies_with_multiple_revisions }}</span>
            </div>
          </div>
          <!-- We'll add the actual list of revised policies in a future update -->
          <p class="info-text">Detailed policy list will be added in the next iteration.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'

export default {
  name: 'KPIDashboard',
  setup() {
    const kpiData = ref({})
    const loading = ref(true)
    const error = ref(null)
    const revisionChart = ref(null)
    const revisionDonutChart = ref(null)
    const trendChart = ref(null)
    const showRevisedPolicies = ref(false)

    const progressPercentage = computed(() => {
      if (!kpiData.value.total_policies) return 0
      return Math.min((kpiData.value.active_policies / kpiData.value.total_policies) * 100, 100)
    })

    const getUtilizationRate = computed(() => {
      if (!kpiData.value.total_policies) return 0
      return Math.round((kpiData.value.active_policies / kpiData.value.total_policies) * 100)
    })

    const getInactivePolicies = computed(() => {
      if (!kpiData.value.total_policies) return 0
      return kpiData.value.total_policies - (kpiData.value.active_policies || 0)
    })

    const getProgressColor = computed(() => {
      const rate = kpiData.value.revision_rate || 0
      if (rate > 66) return '#66BB6A'  // Green for high revision rate
      if (rate > 33) return '#FFA726'   // Orange for medium revision rate
      return '#2196F3'                  // Blue for low revision rate
    })

    const getAcknowledgementClass = (rate) => {
      if (rate >= 80) return 'high'
      if (rate >= 50) return 'medium'
      return 'low'
    }

    const unchangedPolicies = computed(() => {
      if (!kpiData.value.total_policies || !kpiData.value.revised_policies) return 0
      return kpiData.value.total_policies - kpiData.value.revised_policies
    })

    const getCoverageColor = (rate) => {
      if (rate >= 90) return '#66BB6A'  // Green for high coverage
      if (rate >= 70) return '#FFA726'   // Orange for medium coverage
      return '#EF5350'                   // Red for low coverage
    }

    const updateRevisionChart = async () => {
      // Wait for the next DOM update
      await nextTick()
      
      // Check if the canvas element exists
      if (!revisionDonutChart.value) {
        console.warn('Canvas element not found')
        return
      }

      // Destroy existing chart if it exists
      if (revisionChart.value) {
        revisionChart.value.destroy()
      }

      try {
        const ctx = revisionDonutChart.value.getContext('2d')
        revisionChart.value = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['Revised', 'Unchanged'],
            datasets: [{
              data: [
                kpiData.value.revised_policies || 0,
                unchangedPolicies.value
              ],
              backgroundColor: ['#2196F3', '#e9ecef'],
              borderWidth: 0,
              borderRadius: 3
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const label = context.label || ''
                    const value = context.raw || 0
                    const total = kpiData.value.total_policies || 0
                    const percentage = ((value / total) * 100).toFixed(1)
                    return `${label}: ${value} (${percentage}%)`
                  }
                }
              }
            }
          }
        })
      } catch (err) {
        console.error('Error creating chart:', err)
      }
    }

    // Watch for changes in kpiData and loading state
    watch([() => kpiData.value, loading], async ([newKpiData, isLoading]) => {
      if (!isLoading && !error.value && newKpiData) {
        await updateRevisionChart()
      }
    }, { deep: true })

    const fetchKPIData = async () => {
      loading.value = true
      error.value = null

      try {
        console.log('Fetching KPI data...')
        const response = await axios.get('/api/policy-kpis/', {
          baseURL: 'http://localhost:8000',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        
        console.log('KPI data received:', response.data)
        
        if (!response.data || typeof response.data !== 'object') {
          throw new Error('Invalid response format')
        }
        
        kpiData.value = response.data
        
        // Update chart after data is loaded
        await updateRevisionChart()
      } catch (err) {
        console.error('Detailed error:', err.response?.data || err.message)
        error.value = `Failed to load KPI data: ${err.response?.data?.error || err.message}`
      } finally {
        loading.value = false
      }
    }

    const sparklineData = computed(() => {
      if (!kpiData.value?.active_policies_trend) return []
      return kpiData.value.active_policies_trend.map(item => item.count).reverse()
    })

    const sparklineLabels = computed(() => {
      if (!kpiData.value?.active_policies_trend) return []
      return kpiData.value.active_policies_trend.map(item => item.month).reverse()
    })

    const trendDirection = computed(() => {
      if (!sparklineData.value.length) return 'neutral'
      const first = sparklineData.value[0]
      const last = sparklineData.value[sparklineData.value.length - 1]
      return last > first ? 'up' : last < first ? 'down' : 'neutral'
    })

    const updateTrendChart = async () => {
      await nextTick()
      
      if (trendChart.value) {
        trendChart.value.destroy()
      }

      const ctx = document.getElementById('trendChart')
      if (!ctx) return

      trendChart.value = new Chart(ctx, {
        type: 'line',
        data: {
          labels: sparklineLabels.value,
          datasets: [{
            data: sparklineData.value,
            borderColor: getProgressColor.value,
            borderWidth: 2,
            tension: 0.4,
            fill: false,
            pointRadius: 0,
            pointHoverRadius: 4,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              callbacks: {
                title: (context) => {
                  return context[0].label
                },
                label: (context) => {
                  return `Active Policies: ${context.raw}`
                }
              }
            }
          },
          scales: {
            x: {
              display: false
            },
            y: {
              display: false,
              beginAtZero: true
            }
          }
        }
      })
    }

    watch(() => kpiData.value, () => {
      updateTrendChart()
    })

    onMounted(async () => {
      await fetchKPIData()
    })

    return {
      kpiData,
      loading,
      error,
      fetchKPIData,
      progressPercentage,
      getProgressColor,
      getUtilizationRate,
      getInactivePolicies,
      unchangedPolicies,
      revisionDonutChart,
      showRevisedPolicies,
      getCoverageColor,
      sparklineData,
      sparklineLabels,
      trendDirection,
      getAcknowledgementClass
    }
  }
}
</script>

<style scoped>
.kpi-dashboard {
  padding: 2rem;
  background-color: #f8f9fa;
  min-height: calc(100vh - 4rem);
  max-width: 1200px;
  margin: 0 auto;
  margin-left: 260px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.dashboard-header h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0;
  font-weight: 600;
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  color: #2c3e50;
}

.refresh-button:hover {
  background-color: #f5f5f5;
  border-color: #d0d0d0;
}

.refresh-button.loading i {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.loader {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #2196F3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.error-state {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.error-state i {
  font-size: 2rem;
  color: #dc3545;
  margin-bottom: 1rem;
}

.retry-button {
  padding: 0.75rem 1.5rem;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 1rem auto 0;
  font-size: 0.9rem;
}

.retry-button:hover {
  background-color: #1976D2;
  transform: translateY(-1px);
}

.dashboard-content {
  display: grid;
  gap: 2rem;
}

.kpi-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  width: 100%;
}

.kpi-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 100%; /* Ensure all cards have the same height */
}

.full-width {
  grid-column: auto; /* Reset the grid-column property */
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.kpi-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(33, 150, 243, 0.1);
  border-radius: 12px;
}

.kpi-icon i {
  font-size: 1.5rem;
  color: #2196F3;
}

.kpi-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #2c3e50;
  font-weight: 600;
}

.kpi-body {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.kpi-visualization {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  position: relative;
}

.circular-progress {
  position: relative;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: conic-gradient(
    var(--progress-color, #2196F3) var(--progress-value),
    #e9ecef var(--progress-value)
  );
}

.circular-progress-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 144px;
  height: 144px;
  background: white;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
}

.circular-progress .kpi-value {
  font-size: 2.2rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1;
  margin-bottom: 0.25rem;
  text-align: center;
  white-space: nowrap;
}

.circular-progress .kpi-label {
  font-size: 0.9rem;
  color: #6c757d;
  text-align: center;
}

.kpi-details {
  flex: 1;
  margin-left: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.detail-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-icon {
  color: #6c757d;
  font-size: 0.9rem;
  cursor: help;
}

.status-breakdown {
  flex-direction: column;
  gap: 0.75rem;
}

.status-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.active {
  background-color: #2196F3;
}

.status-dot.inactive {
  background-color: #9e9e9e;
}

.status-value {
  font-weight: 600;
  color: #2c3e50;
}

.progress-bar {
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background-color: #2196F3;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress.medium {
  background-color: #FFA726;
}

.progress.high {
  background-color: #66BB6A;
}

.donut-chart-container {
  position: relative;
  width: 180px;
  height: 180px;
}

.donut-center-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.drill-down-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  width: 100%;
  justify-content: center;
  margin-top: 0.5rem;
}

.drill-down-button:hover {
  background-color: #1976D2;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #6c757d;
  cursor: pointer;
  padding: 0.5rem;
}

.close-button:hover {
  color: #2c3e50;
}

.modal-body {
  padding: 1.5rem;
}

.revised-policies-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-item {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-label {
  color: #6c757d;
  font-size: 0.9rem;
}

.stat-value {
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 600;
}

.info-text {
  color: #6c757d;
  text-align: center;
  font-style: italic;
}

.coverage-container {
  padding: 1.5rem;
}

.coverage-overview {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.overall-coverage {
  text-align: center;
}

.overall-label {
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.overall-value {
  font-size: 2rem;
  font-weight: 600;
  color: #2c3e50;
}

.coverage-bars {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.coverage-bar-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.department-name {
  font-size: 0.9rem;
  color: #2c3e50;
  font-weight: 500;
}

.department-value {
  font-size: 0.9rem;
  color: #6c757d;
}

.bar-container {
  position: relative;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
}

.bar-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #f5f5f5;
}

.bar-fill {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  transition: width 0.5s ease;
  min-width: 4px;
}

.department-policies {
  font-size: 0.8rem;
  color: #6c757d;
  text-align: right;
}

/* Custom scrollbar for coverage bars */
.coverage-bars::-webkit-scrollbar {
  width: 4px;
}

.coverage-bars::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.coverage-bars::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.coverage-bars::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.trend-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.trend-label {
  font-size: 0.9rem;
  color: #6c757d;
}

.trend-indicator {
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.trend-indicator.up {
  color: #28a745;
  background-color: rgba(40, 167, 69, 0.1);
}

.trend-indicator.down {
  color: #dc3545;
  background-color: rgba(220, 53, 69, 0.1);
}

.trend-indicator.neutral {
  color: #6c757d;
  background-color: rgba(108, 117, 125, 0.1);
}

.sparkline-container {
  height: 40px;
  width: 100%;
  margin-top: 0.5rem;
  position: relative;
}

/* Make sure the sparkline is responsive */
.sparkline-container :deep(svg) {
  width: 100%;
  height: 100%;
}

/* Acknowledgement KPI Card Styles */
.acknowledgement-table {
  width: 100%;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 1fr auto;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  font-weight: 600;
  color: #2c3e50;
}

.table-body {
  max-height: 300px;
  overflow-y: auto;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr auto;
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
  align-items: center;
  transition: background-color 0.2s;
}

.table-row:hover {
  background-color: #f8f9fa;
}

.policy-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.policy-name {
  font-weight: 500;
  color: #2c3e50;
}

.policy-stats {
  display: flex;
  gap: 4px;
  font-size: 0.9em;
  color: #6c757d;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 150px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.progress-fill.low {
  background-color: #dc3545;
}

.progress-fill.medium {
  background-color: #ffc107;
}

.progress-fill.high {
  background-color: #28a745;
}

.progress-text {
  min-width: 48px;
  text-align: right;
  font-weight: 500;
  color: #2c3e50;
}

.no-data {
  padding: 24px;
  text-align: center;
  color: #6c757d;
  font-style: italic;
}

@media (max-width: 768px) {
  .table-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .progress-container {
    width: 100%;
  }

  .kpi-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .kpi-dashboard {
    padding: 1rem;
  }
}

@media (max-width: 768px) {
  .kpi-visualization {
    flex-direction: column;
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .kpi-details {
    margin-left: 0;
    width: 100%;
  }

  .circular-progress {
    width: 150px;
    height: 150px;
  }

  .circular-progress-inner {
    width: 120px;
    height: 120px;
  }

  .circular-progress .kpi-value {
    font-size: 1.8rem;
  }

  .status-breakdown {
    padding: 1rem;
  }

  .coverage-container {
    padding: 1rem;
  }

  .overall-value {
    font-size: 1.5rem;
  }
}

@media (max-width: 900px) {
  .kpi-dashboard {
    margin-left: 0;
    padding: 1rem;
  }
}
</style> 