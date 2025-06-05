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

    <!-- Add this new card after the maturity level card -->
    <div class="kpi-card status-overview-card">
      <div class="kpi-header">
        <h3 class="kpi-title">Compliance Status Overview</h3>
      </div>

      <div v-if="statusOverviewError" class="error-message">
        {{ statusOverviewError }}
        <button @click="fetchStatusOverview">Retry</button>
      </div>

      <div class="loading-overlay" v-else-if="statusOverviewLoading">
        <div class="spinner"></div>
      </div>

      <div v-else class="status-overview-content">
        <div class="status-chart-container">
          <Doughnut
            v-if="statusOverviewChartData"
            :data="statusOverviewChartData"
            :options="statusOverviewChartOptions"
          />
        </div>
        
        <div class="status-stats">
          <div 
            v-for="(count, status) in statusOverviewData.counts" 
            :key="status"
            class="status-stat-item"
            :class="status.toLowerCase().replace(' ', '-')"
          >
            <div class="status-stat-value">{{ count }}</div>
            <div class="status-stat-label">{{ status }}</div>
            <div class="status-stat-percentage">{{ statusOverviewData.percentages[status] }}%</div>
          </div>
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

    <!-- On-Time Mitigation KPI Card -->
    <div class="kpi-card ontime-mitigation-card">
      <div class="kpi-header">
        <h3 class="kpi-title">On-Time Mitigation Rate</h3>
      </div>

      <div v-if="ontimeMitigationError" class="error-message">
        {{ ontimeMitigationError }}
        <button @click="fetchOntimeMitigationData">Retry</button>
      </div>

      <div class="loading-overlay" v-else-if="ontimeMitigationLoading">
        <div class="spinner"></div>
      </div>

      <div v-else class="ontime-mitigation-content">
        <div class="ontime-percentage-circle" :class="{ 'high-rate': ontimeMitigationData.on_time_percentage >= 70 }">
          <div class="percentage-value">{{ Math.round(ontimeMitigationData.on_time_percentage) }}%</div>
          <div class="percentage-label">On Time</div>
        </div>
        
        <div class="ontime-stats">
          <div class="ontime-stat-item">
            <div class="stat-value">{{ ontimeMitigationData.completed_on_time }}</div>
            <div class="stat-label">On Time</div>
          </div>
          <div class="ontime-stat-item">
            <div class="stat-value">{{ ontimeMitigationData.completed_late }}</div>
            <div class="stat-label">Late</div>
          </div>
          <div class="ontime-stat-item">
            <div class="stat-value">{{ ontimeMitigationData.total_completed }}</div>
            <div class="stat-label">Total</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add this new card -->
    <div class="kpi-card reputational-impact-card">
      <div class="kpi-header">
        <h3 class="kpi-title">Reputational Impact Assessment</h3>
      </div>

      <div v-if="reputationalError" class="error-message">
        {{ reputationalError }}
        <button @click="fetchReputationalData">Retry</button>
      </div>

      <div class="loading-overlay" v-else-if="reputationalLoading">
        <div class="spinner"></div>
      </div>

      <div v-else class="reputational-impact-content">
        <div class="reputational-chart-container">
          <Line
            v-if="reputationalChartData"
            :data="reputationalChartData"
            :options="reputationalChartOptions"
          />
        </div>
        
        <div class="impact-stats">
          <div 
            v-for="(count, level) in reputationalData.impact_counts" 
            :key="level"
            class="impact-stat-item"
            :class="level"
          >
            <div class="impact-stat-value">{{ count }}</div>
            <div class="impact-stat-label">{{ level.charAt(0).toUpperCase() + level.slice(1) }}</div>
            <div class="impact-stat-percentage">{{ Math.round(reputationalData.impact_percentages[level]) }}%</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Bar, Pie, Doughnut, Line } from 'vue-chartjs'
import { complianceService } from '@/services/api'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
  PointElement,
  LineElement
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
  PointElement,
  LineElement
)

export default {
  name: 'ComplianceKPI',
  components: {
    Bar,
    Pie,
    Doughnut,
    Line
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
      },
      ontimeMitigationLoading: true,
      ontimeMitigationError: null,
      ontimeMitigationData: {
        on_time_percentage: 0,
        total_completed: 0,
        completed_on_time: 0,
        completed_late: 0
      },
      statusOverviewLoading: true,
      statusOverviewError: null,
      statusOverviewData: {
        counts: {},
        percentages: {},
        total: 0
      },
      statusOverviewChartData: null,
      statusOverviewChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '75%',
        radius: '90%',
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
            padding: 12,
            boxPadding: 6,
            usePointStyle: true,
            callbacks: {
              label: function(context) {
                const value = context.raw;
                const dataset = context.dataset;
                const label = context.label;
                return [
                  `${label}: ${value.toFixed(1)}%`,
                  `Count: ${dataset.data[context.dataIndex]}`
                ];
              }
            }
          }
        },
        animation: {
          animateRotate: true,
          animateScale: true,
          duration: 1000,
          easing: 'easeOutQuart'
        }
      },
      reputationalLoading: true,
      reputationalError: null,
      reputationalData: {
        impact_counts: {},
        impact_percentages: {},
        timeline_data: {
          dates: [],
          low: [],
          medium: [],
          high: []
        },
        total_risks: 0
      },
      reputationalChartData: null,
      reputationalChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 20,
              font: {
                size: 12
              }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            titleColor: '#1e293b',
            bodyColor: '#475569',
            borderColor: '#e2e8f0',
            borderWidth: 1,
            padding: 12,
            usePointStyle: true,
            callbacks: {
              label: function(context) {
                return `${context.dataset.label}: ${context.raw}`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            ticks: {
              font: {
                size: 12
              },
              color: '#64748b'
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: '#f1f5f9'
            },
            ticks: {
              precision: 0,
              stepSize: 1,
              font: {
                size: 12
              },
              color: '#64748b'
            },
            title: {
              display: true,
              text: 'Number of Risks',
              color: '#64748b',
              font: {
                size: 12,
                weight: 'normal'
              }
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
    },

    async fetchOntimeMitigationData() {
      this.ontimeMitigationLoading = true;
      this.ontimeMitigationError = null;
      try {
        const response = await complianceService.getOntimeMitigationPercentage();
        console.log('On-time Mitigation Response:', response);
        if (response.data && response.data.success) {
          // Ensure we have all required data with defaults
          this.ontimeMitigationData = {
            on_time_percentage: response.data.data.on_time_percentage || 0,
            total_completed: response.data.data.total_completed || 0,
            completed_on_time: response.data.data.completed_on_time || 0,
            completed_late: response.data.data.completed_late || 0
          };
        } else {
          throw new Error(response.data?.message || 'Failed to fetch on-time mitigation data');
        }
      } catch (error) {
        console.error('Error fetching on-time mitigation data:', error);
        this.ontimeMitigationError = error.response?.data?.message || error.message || 'Failed to load on-time mitigation data';
      } finally {
        this.ontimeMitigationLoading = false;
      }
    },

    async fetchStatusOverview() {
      this.statusOverviewLoading = true;
      this.statusOverviewError = null;
      try {
        const response = await complianceService.getComplianceStatusOverview();
        if (response.data && response.data.success) {
          this.statusOverviewData = response.data.data;
          this.updateStatusOverviewChart();
        } else {
          throw new Error(response.data?.message || 'Failed to fetch status overview data');
        }
      } catch (error) {
        console.error('Error fetching status overview:', error);
        this.statusOverviewError = error.response?.data?.message || error.message || 'Failed to load status overview';
      } finally {
        this.statusOverviewLoading = false;
      }
    },

    updateStatusOverviewChart() {
      if (!this.statusOverviewData) return;

      // Define colors for each status
      const statusColors = {
        'Approved': '#10B981',
        'Under Review': '#3B82F6',
        'Active': '#F59E0B',
        'Rejected': '#EF4444'
      };

      const hoverColors = {
        'Approved': '#059669',
        'Under Review': '#2563EB',
        'Active': '#D97706',
        'Rejected': '#DC2626'
      };

      const labels = Object.keys(this.statusOverviewData.percentages);
      
      this.statusOverviewChartData = {
        labels,
        datasets: [{
          data: Object.values(this.statusOverviewData.percentages),
          backgroundColor: labels.map(status => statusColors[status]),
          hoverBackgroundColor: labels.map(status => hoverColors[status]),
          borderWidth: 0,
          borderRadius: 4
        }]
      };
    },

    async fetchReputationalData() {
      this.reputationalLoading = true;
      this.reputationalError = null;
      try {
        const response = await complianceService.getReputationalImpact();
        console.log('Reputational Impact Response:', response);
        if (response.data && response.data.success) {
          this.reputationalData = response.data.data;
          this.updateReputationalChart();
        } else {
          throw new Error(response.data?.message || 'Failed to fetch reputational impact data');
        }
      } catch (error) {
        console.error('Error fetching reputational impact:', error);
        this.reputationalError = error.response?.data?.message || error.message || 'Failed to load reputational impact data';
        
        // Set default empty data structure to prevent chart errors
        this.reputationalData = {
          impact_counts: { low: 0, medium: 0, high: 0 },
          impact_percentages: { low: 0, medium: 0, high: 0 },
          timeline_data: {
            dates: [],
            low: [],
            medium: [],
            high: []
          },
          total_risks: 0
        };
      } finally {
        this.reputationalLoading = false;
      }
    },

    updateReputationalChart() {
      if (!this.reputationalData?.impact_counts) {
        // Set default empty chart data
        this.reputationalChartData = {
          labels: ['Low', 'Medium', 'High'],
          datasets: [{
            label: 'Impact Count',
            data: [0, 0, 0],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4,
            fill: true,
            pointBackgroundColor: '#3b82f6',
            pointBorderColor: '#fff',
            pointRadius: 5,
            pointHoverRadius: 7
          }]
        };
        return;
      }

      // Get impact counts directly
      const { low, medium, high } = this.reputationalData.impact_counts;

      // Create line chart data
      this.reputationalChartData = {
        labels: ['Low', 'Medium', 'High'],
        datasets: [{
          label: 'Impact Count',
          data: [low, medium, high],
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true,
          pointBackgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
          pointBorderColor: '#fff',
          pointRadius: 6,
          pointHoverRadius: 8
        }]
      };
    },
  },
  mounted() {
    this.fetchMaturityData();
    this.fetchNonComplianceCount();
    this.fetchMitigatedCount();
    this.fetchAutomatedCount();
    this.fetchRepetitionsData();
    this.fetchOntimeMitigationData();
    this.fetchStatusOverview();
    this.fetchReputationalData();
  }
}
</script>

<style>
@import './ComplianceKPI.css';

.reputational-impact-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.reputational-chart-container {
  height: 300px;
  margin-bottom: 20px;
}

.impact-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}

.impact-stat-item {
  text-align: center;
  padding: 10px;
  border-radius: 6px;
}

.impact-stat-item.high {
  background-color: rgba(239, 68, 68, 0.1);
}

.impact-stat-item.medium {
  background-color: rgba(245, 158, 11, 0.1);
}

.impact-stat-item.low {
  background-color: rgba(16, 185, 129, 0.1);
}

.impact-stat-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 4px;
}

.impact-stat-label {
  font-size: 14px;
  color: #64748b;
}

.impact-stat-percentage {
  font-size: 16px;
  color: #475569;
  margin-top: 4px;
}
</style> 