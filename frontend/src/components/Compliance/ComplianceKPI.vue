<template>
  <div class="kpi-dashboard">
    <!-- Maturity Level KPI Card -->
    <div class="kpi-card">
      <div class="kpi-header">
        <h3 class="kpi-title">Maturity Level Distribution</h3>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
        <button @click="fetchMaturityData">Retry</button>
      </div>

      <div class="loading-overlay" v-else-if="loading">
        <div class="spinner"></div>
      </div>

      <div v-else>
        <div class="kpi-chart">
          <Bar
            v-if="chartData"
            :data="chartData"
            :options="chartOptions"
          />
        </div>

        <div class="maturity-grid">
          <div 
            v-for="level in maturityLevels" 
            :key="level"
            class="maturity-item"
          >
            <div class="maturity-color" :class="level.toLowerCase()"></div>
            <span class="maturity-label">{{ level }}</span>
            <span class="maturity-count">{{ getMaturityCount(level) }}</span>
          </div>
        </div>

        <div class="total-count">
          Total Active & Approved: {{ getTotalCompliances() }}
        </div>
      </div>
    </div>

    <!-- Non-Compliance KPI Card -->
    <div class="kpi-card non-compliance-card">
      <div class="kpi-header">
        <h3 class="kpi-title">Non-Compliance Count</h3>
      </div>

      <div v-if="nonComplianceError" class="error-message">
        {{ nonComplianceError }}
        <button @click="fetchNonComplianceCount">Retry</button>
        </div>

      <div class="loading-overlay" v-else-if="nonComplianceLoading">
        <div class="spinner"></div>
      </div>

      <div v-else>
        <div class="non-compliance-badge">
          {{ nonComplianceCount }}
        </div>
        <div class="non-compliance-label">
          Total Non-Compliant Items
        </div>
      </div>
    </div>

    <!-- Mitigated Risks KPI Card -->
    <div class="kpi-card mitigated-risks-card">
      <div class="kpi-header">
        <h3 class="kpi-title">Mitigated Risks</h3>
      </div>

      <div v-if="mitigatedError" class="error-message">
        {{ mitigatedError }}
        <button @click="fetchMitigatedCount">Retry</button>
      </div>

      <div class="loading-overlay" v-else-if="mitigatedLoading">
        <div class="spinner"></div>
      </div>

      <div v-else>
        <div class="mitigated-badge">
          {{ mitigatedCount }}
        </div>
        <div class="mitigated-label">
          Total Mitigated Risks
        </div>
      </div>
    </div>

    <!-- Automated Controls KPI Card -->
    <div class="kpi-card automated-controls-card">
      <div class="kpi-header">
        <h3 class="kpi-title">Controls Distribution</h3>
      </div>

      <div v-if="automatedError" class="error-message">
        {{ automatedError }}
        <button @click="fetchAutomatedCount">Retry</button>
      </div>

      <div class="loading-overlay" v-else-if="automatedLoading">
        <div class="spinner"></div>
      </div>

      <div v-else>
        <div class="automated-chart-container">
          <Pie
            v-if="automatedChartData"
            :data="automatedChartData"
            :options="automatedChartOptions"
          />
        </div>
        
        <div class="automated-stats">
          <div class="stat-item">
            <div class="stat-value automated-stat">
              {{ automatedData.automated_percentage }}%
            </div>
            <div class="stat-label">
              Automated
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-value manual-stat">
              {{ automatedData.manual_percentage }}%
            </div>
            <div class="stat-label">
              Manual
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Non-Compliance Repetitions KPI Card -->
    <div class="kpi-card repetitions-card">
      <div class="kpi-header">
        <h3 class="kpi-title">Non-Compliance Repetitions</h3>
      </div>

      <div v-if="repetitionsError" class="error-message">
        {{ repetitionsError }}
        <button @click="fetchRepetitionsData">Retry</button>
      </div>

      <div class="loading-overlay" v-else-if="repetitionsLoading">
        <div class="spinner"></div>
      </div>

      <div v-else>
        <div class="repetitions-chart-container">
          <Bar
            v-if="repetitionsChartData"
            :data="repetitionsChartData"
            :options="repetitionsChartOptions"
          />
        </div>
        
        <div class="repetitions-stats">
          <div class="repetition-stat-item">
            <div class="repetition-stat-value">
              {{ repetitionsData.total_items }}
            </div>
            <div class="repetition-stat-label">
              Total Items
            </div>
          </div>
          <div class="repetition-stat-item">
            <div class="repetition-stat-value">
              {{ repetitionsData.max_repetitions }}
            </div>
            <div class="repetition-stat-label">
              Max Repetitions
            </div>
          </div>
          <div class="repetition-stat-item">
            <div class="repetition-stat-value">
              {{ repetitionsData.avg_repetitions }}
            </div>
            <div class="repetition-stat-label">
              Avg Repetitions
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Bar, Pie } from 'vue-chartjs'
import { complianceService } from '@/services/api'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement
)

export default {
  name: 'ComplianceKPI',
  components: {
    Bar,
    Pie
  },
  data() {
    return {
      loading: true,
      error: null,
      maturityLevels: ['Initial', 'Developing', 'Defined', 'Managed', 'Optimizing'],
      maturityData: null,
      chartData: null,
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            titleColor: '#1e293b',
            bodyColor: '#475569',
            borderColor: '#e2e8f0',
            borderWidth: 1,
            padding: 8,
            titleFont: {
              size: 13
            },
            bodyFont: {
              size: 12
            },
            callbacks: {
              label: function(context) {
                return `Count: ${context.raw}`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              display: true,
              color: '#f1f5f9',
              drawBorder: false
            },
            ticks: {
              precision: 0,
              color: '#64748b',
              font: {
                size: 11
              }
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              color: '#64748b',
              font: {
                size: 10
              }
            }
          }
        }
      },
      nonComplianceLoading: true,
      nonComplianceError: null,
      nonComplianceCount: 0,
      mitigatedLoading: true,
      mitigatedError: null,
      mitigatedCount: 0,
      automatedLoading: true,
      automatedError: null,
      automatedData: null,
      automatedChartData: null,
      automatedChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            titleColor: '#1e293b',
            bodyColor: '#475569',
            borderColor: '#e2e8f0',
            borderWidth: 1,
            padding: 8,
            callbacks: {
              label: function(context) {
                return `${context.label}: ${context.raw}%`;
              }
            }
          }
        }
      },
      repetitionsLoading: true,
      repetitionsError: null,
      repetitionsData: null,
      repetitionsChartData: null,
      repetitionsChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            titleColor: '#1e293b',
            bodyColor: '#475569',
            borderColor: '#e2e8f0',
            borderWidth: 1,
            padding: 8,
            callbacks: {
              label: function(context) {
                return `Occurrences: ${context.raw}`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Number of Items',
              color: '#64748b'
            },
            ticks: {
              precision: 0,
              color: '#64748b'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Number of Repetitions',
              color: '#64748b'
            },
            ticks: {
              color: '#64748b'
            }
          }
        }
      }
    }
  },
  methods: {
    async fetchMaturityData() {
      this.loading = true;
      this.error = null;
      try {
        const response = await complianceService.getMaturityLevelKPI();
        console.log('Maturity Level Response:', response);
        if (response.data && response.data.success) {
          this.maturityData = response.data.data;
          this.updateChartData();
        } else {
          throw new Error(response.data?.message || 'Failed to fetch data');
        }
      } catch (error) {
        console.error('Error fetching maturity data:', error);
        this.error = error.response?.data?.message || error.message || 'Failed to load data';
      } finally {
        this.loading = false;
      }
    },
    
    updateChartData() {
      if (!this.maturityData) return;
      
      const totals = this.maturityData.summary.total_by_maturity;
      
      this.chartData = {
        labels: this.maturityLevels,
        datasets: [{
          data: this.maturityLevels.map(level => totals[level] || 0),
          backgroundColor: [
            '#f43f5e', // Initial
            '#3b82f6', // Developing
            '#f59e0b', // Defined
            '#10b981', // Managed
            '#8b5cf6'  // Optimizing
          ],
          borderRadius: 4,
          maxBarThickness: 32,
          borderSkipped: false
        }]
      };
    },
    
    getMaturityCount(level) {
      if (!this.maturityData) return 0;
      return this.maturityData.summary.total_by_maturity[level] || 0;
    },

    getTotalCompliances() {
      if (!this.maturityData) return 0;
      return this.maturityData.summary.total_compliances || 0;
    },

    async fetchNonComplianceCount() {
      this.nonComplianceLoading = true;
      this.nonComplianceError = null;
      try {
        const response = await complianceService.getNonComplianceCount();
        console.log('Non-Compliance Response:', response);
        if (response.data && response.data.success) {
          this.nonComplianceCount = response.data.data.non_compliance_count;
        } else {
          throw new Error(response.data?.message || 'Failed to fetch non-compliance count');
        }
      } catch (error) {
        console.error('Error fetching non-compliance count:', error);
        this.nonComplianceError = error.response?.data?.message || error.message || 'Failed to load non-compliance data';
      } finally {
        this.nonComplianceLoading = false;
      }
    },

    async fetchMitigatedCount() {
      this.mitigatedLoading = true;
      this.mitigatedError = null;
      try {
        const response = await complianceService.getMitigatedRisksCount();
        console.log('Mitigated Risks Response:', response);
        if (response.data && response.data.success) {
          this.mitigatedCount = response.data.data.mitigated_count;
        } else {
          throw new Error(response.data?.message || 'Failed to fetch mitigated risks count');
        }
      } catch (error) {
        console.error('Error fetching mitigated risks count:', error);
        this.mitigatedError = error.response?.data?.message || error.message || 'Failed to load mitigated risks data';
      } finally {
        this.mitigatedLoading = false;
      }
    },

    async fetchAutomatedCount() {
      this.automatedLoading = true;
      this.automatedError = null;
      try {
        const response = await complianceService.getAutomatedControlsCount();
        console.log('Automated Controls Response:', response);
        if (response.data && response.data.success) {
          this.automatedData = response.data.data;
          this.updateAutomatedChartData();
        } else {
          throw new Error(response.data?.message || 'Failed to fetch automated controls data');
        }
      } catch (error) {
        console.error('Error fetching automated controls data:', error);
        this.automatedError = error.response?.data?.message || error.message || 'Failed to load automated controls data';
      } finally {
        this.automatedLoading = false;
      }
    },

    updateAutomatedChartData() {
      if (!this.automatedData) return;
      
      this.automatedChartData = {
        labels: ['Automated', 'Manual'],
        datasets: [{
          data: [
            this.automatedData.automated_percentage,
            this.automatedData.manual_percentage
          ],
          backgroundColor: [
            '#3b82f6',  // Blue for automated
            '#94a3b8'   // Gray for manual
          ],
          borderWidth: 0
        }]
      };
    },

    async fetchRepetitionsData() {
      this.repetitionsLoading = true;
      this.repetitionsError = null;
      try {
        const response = await complianceService.getNonComplianceRepetitions();
        console.log('Repetitions Response:', response);
        if (response.data && response.data.success) {
          this.repetitionsData = response.data.data;
          this.updateRepetitionsChartData();
        } else {
          throw new Error(response.data?.message || 'Failed to fetch repetitions data');
        }
      } catch (error) {
        console.error('Error fetching repetitions data:', error);
        this.repetitionsError = error.response?.data?.message || error.message || 'Failed to load repetitions data';
      } finally {
        this.repetitionsLoading = false;
      }
    },

    updateRepetitionsChartData() {
      if (!this.repetitionsData) return;
      
      const distribution = this.repetitionsData.distribution;
      
      this.repetitionsChartData = {
        labels: distribution.map(item => item.repetitions),
        datasets: [{
          data: distribution.map(item => item.occurrences),
          backgroundColor: '#dc2626',  // Red color
          borderRadius: 4,
          maxBarThickness: 32
        }]
      };
    }
  },
  mounted() {
    this.fetchMaturityData();
    this.fetchNonComplianceCount();
    this.fetchMitigatedCount();
    this.fetchAutomatedCount();
    this.fetchRepetitionsData();
  }
}
</script>

<style>
@import './ComplianceKPI.css';
</style> 