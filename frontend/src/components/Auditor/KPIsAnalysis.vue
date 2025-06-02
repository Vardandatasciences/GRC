<template>
  <div class="kpis-analysis-container">
    <h2>KPIs Analysis</h2>
    
    <div class="time-period-filter">
      <div class="filter-label">Time Period:</div>
      <div class="filter-options">
        <button 
          v-for="period in timePeriods" 
          :key="period.value" 
          :class="['period-button', { active: selectedTimePeriod === period.value }]"
          @click="changeTimePeriod(period.value)"
        >
          {{ period.label }}
        </button>
      </div>
      
      <div class="custom-date-range" v-if="selectedTimePeriod === 'custom'">
        <div class="date-range-picker">
          <div class="date-input">
            <label>From:</label>
            <input type="date" v-model="startDate" @change="fetchData" />
          </div>
          <div class="date-input">
            <label>To:</label>
            <input type="date" v-model="endDate" @change="fetchData" />
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading KPI data...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <p class="error-message">{{ error }}</p>
      <button @click="fetchData" class="retry-button">Retry</button>
    </div>
    
    <div v-else class="kpi-card">
      <h3>Audits Completed vs. Planned</h3>
      <div class="kpi-visualizations">
        <div class="gauge-container">
          <div class="gauge">
            <div class="gauge-fill" :style="{ transform: `rotate(${gaugeRotation}deg)` }"></div>
            <div class="gauge-center">
              <span class="gauge-value">{{ auditStats.completion_percentage }}%</span>
            </div>
          </div>
          <div class="gauge-label">Completion Rate</div>
        </div>
        
        <div class="bar-chart-container">
          <div class="bar-chart">
            <div class="bar-group">
              <div class="bar-label">Planned</div>
              <div class="bar planned" :style="{ height: `${(auditStats.planned / maxBarValue) * 100}%` }">
                <div class="bar-value">{{ auditStats.planned }}</div>
              </div>
            </div>
            <div class="bar-group">
              <div class="bar-label">Completed</div>
              <div class="bar completed" :style="{ height: `${(auditStats.completed / maxBarValue) * 100}%` }">
                <div class="bar-value">{{ auditStats.completed }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="kpi-details">
        <div class="detail-item">
          <span class="detail-label">Time Period:</span>
          <span class="detail-value">{{ auditStats.period_label }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Planned Audits:</span>
          <span class="detail-value">{{ auditStats.planned }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Completed Audits:</span>
          <span class="detail-value">{{ auditStats.completed }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Completion Rate:</span>
          <span class="detail-value">{{ auditStats.completion_percentage }}%</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Target:</span>
          <span class="detail-value">{{ auditStats.target }}%</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Status:</span>
          <span :class="['detail-value', 'status', auditStats.status_class]">{{ auditStats.status }}</span>
        </div>
      </div>
    </div>
    
    <!-- Trend Chart Section -->
    <div v-if="!loading && !error" class="kpi-card">
      <h3>Audit Completion Trend</h3>
      <div class="trend-chart-container">
        <div v-if="loadingTrend" class="loading-spinner small"></div>
        <div v-else-if="trendError" class="error-message small">
          {{ trendError }}
          <button @click="fetchTrendData" class="retry-button small">Retry</button>
        </div>
        <div v-else-if="trendData.length === 0" class="no-data-message">
          No trend data available for the selected time period.
        </div>
        <div v-else class="trend-chart">
          <!-- Placeholder for trend chart (would use a charting library in production) -->
          <div class="trend-chart-bars">
            <div 
              v-for="(item, index) in trendData" 
              :key="index" 
              class="trend-bar-group"
            >
              <div class="trend-bar-container">
                <div class="trend-bar planned" 
                  :style="{ height: `${(item.planned / maxTrendValue) * 100}%` }"
                  :title="`Planned: ${item.planned}`"
                ></div>
                <div class="trend-bar completed" 
                  :style="{ height: `${(item.completed / maxTrendValue) * 100}%` }"
                  :title="`Completed: ${item.completed}`"
                ></div>
              </div>
              <div class="trend-bar-label">{{ item.time_period }}</div>
              <div class="trend-bar-percentage">{{ item.percentage }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { 
  fetchKpiData, 
  calculateGaugeRotation,
  formatDateForApi
} from '../PerformanceAnalysis/KpiFunctions.js';

export default {
  name: 'KPIsAnalysis',
  data() {
    return {
      auditStats: {
        period_label: '',
        planned: 0,
        completed: 0,
        completion_percentage: 0,
        target: 85,
        status: '',
        status_class: ''
      },
      trendData: [],
      loading: false,
      error: null,
      loadingTrend: false,
      trendError: null,
      selectedTimePeriod: 'month',
      startDate: null,
      endDate: null,
      timePeriods: [
        { value: 'week', label: 'Week' },
        { value: 'month', label: 'Month' },
        { value: 'quarter', label: 'Quarter' },
        { value: 'year', label: 'Year' },
        { value: 'custom', label: 'Custom' }
      ]
    }
  },
  computed: {
    gaugeRotation() {
      return calculateGaugeRotation(this.auditStats.completion_percentage);
    },
    maxBarValue() {
      return Math.max(this.auditStats.planned, this.auditStats.completed, 1); // Minimum of 1 to avoid division by zero
    },
    maxTrendValue() {
      if (this.trendData.length === 0) return 1;
      return Math.max(
        ...this.trendData.map(item => Math.max(item.planned, item.completed)),
        1 // Minimum of 1 to avoid division by zero
      );
    },
    apiParams() {
      const params = {
        period: this.selectedTimePeriod
      };
      
      if (this.selectedTimePeriod === 'custom' && this.startDate && this.endDate) {
        params.start_date = formatDateForApi(this.startDate);
        params.end_date = formatDateForApi(this.endDate);
      }
      
      return params;
    }
  },
  methods: {
    async fetchData() {
      try {
        this.loading = true;
        this.error = null;
        
        const data = await fetchKpiData('auditCompletion', this.apiParams);
        this.auditStats = data;
        
        // Also fetch the trend data
        this.fetchTrendData();
        
        this.loading = false;
      } catch (error) {
        this.error = 'Failed to load KPI data';
        this.loading = false;
        console.error('Error fetching KPI data:', error);
      }
    },
    
    async fetchTrendData() {
      try {
        this.loadingTrend = true;
        this.trendError = null;
        
        // Calculate appropriate period breakdown based on time span
        let periodBreakdown = 'day';
        if (this.selectedTimePeriod === 'year') {
          periodBreakdown = 'month';
        } else if (this.selectedTimePeriod === 'quarter') {
          periodBreakdown = 'week';
        } else if (this.selectedTimePeriod === 'month') {
          periodBreakdown = 'week';
        } else if (this.selectedTimePeriod === 'week') {
          periodBreakdown = 'day';
        }
        
        const params = {
          ...this.apiParams,
          period: periodBreakdown,
          time_span: this.selectedTimePeriod
        };
        
        const response = await fetchKpiData('auditCompletionTrend', params);
        this.trendData = response.trend_data || [];
        
        this.loadingTrend = false;
      } catch (error) {
        this.trendError = 'Failed to load trend data';
        this.loadingTrend = false;
        console.error('Error fetching trend data:', error);
      }
    },
    
    changeTimePeriod(period) {
      this.selectedTimePeriod = period;
      
      // If switching to custom and dates aren't set, initialize with last month
      if (period === 'custom' && (!this.startDate || !this.endDate)) {
        const end = new Date();
        const start = new Date();
        start.setMonth(start.getMonth() - 1);
        
        this.endDate = formatDateForApi(end);
        this.startDate = formatDateForApi(start);
      }
      
      this.fetchData();
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    }
  },
  mounted() {
    // Initialize with the current month as default
    const now = new Date();
    const firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    this.startDate = formatDateForApi(firstDayOfMonth);
    this.endDate = formatDateForApi(now);
    
    this.fetchData();
  }
}
</script>

<style scoped>
.kpis-analysis-container {
  margin-left: 180px;
  padding: 32px 24px 24px 24px;
  background: #f8f9fb;
  min-height: 100vh;
  font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
}

h2 {
  margin-bottom: 24px;
  color: #333;
  font-size: 1.8rem;
}

h3 {
  margin-bottom: 16px;
  color: #444;
  font-size: 1.3rem;
}

.time-period-filter {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

.filter-label {
  font-weight: 500;
  margin-bottom: 10px;
  color: #555;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.period-button {
  background-color: #f0f0f0;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.period-button.active {
  background-color: #4f7cff;
  color: white;
}

.custom-date-range {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.date-range-picker {
  display: flex;
  gap: 16px;
}

.date-input {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.date-input label {
  font-size: 0.9rem;
  color: #666;
}

.date-input input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.kpi-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

.kpi-visualizations {
  display: flex;
  flex-wrap: wrap;
  gap: 40px;
  margin-bottom: 24px;
}

/* Gauge styling */
.gauge-container {
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.gauge {
  position: relative;
  width: 150px;
  height: 75px;
  overflow: hidden;
  margin-bottom: 10px;
}

.gauge:before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: #f0f0f0;
}

.gauge-fill {
  position: absolute;
  top: 0;
  left: 0;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: conic-gradient(#4f7cff 0%, transparent 50%);
  transform-origin: center bottom;
  transform: rotate(-90deg);
  transition: transform 0.5s ease-out;
}

.gauge-center {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 150px;
  height: 75px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.gauge-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #333;
}

.gauge-label {
  font-size: 1rem;
  color: #666;
}

/* Bar chart styling */
.bar-chart-container {
  flex: 1;
  min-width: 200px;
}

.bar-chart {
  display: flex;
  height: 180px;
  align-items: flex-end;
  gap: 40px;
  padding-bottom: 24px;
  border-bottom: 1px solid #eee;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.bar {
  width: 60px;
  position: relative;
  border-radius: 4px 4px 0 0;
  transition: height 0.5s ease;
}

.bar.planned {
  background-color: #e2e8f0;
}

.bar.completed {
  background-color: #4f7cff;
}

.bar-value {
  position: absolute;
  top: -24px;
  width: 100%;
  text-align: center;
  font-weight: bold;
}

.bar-label {
  margin-top: 8px;
  font-size: 0.9rem;
  color: #666;
}

/* KPI details styling */
.kpi-details {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #eee;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 4px;
}

.detail-value {
  font-size: 1.1rem;
  font-weight: 500;
  color: #333;
}

.status {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.9rem;
}

.status.success {
  background-color: #e9f7ef;
  color: #1aaf5d;
}

.status.warning {
  background-color: #fff8e6;
  color: #e5a12d;
}

.status.danger {
  background-color: #fdedeb;
  color: #e5534b;
}

/* Trend Chart Styling */
.trend-chart-container {
  height: 300px;
  position: relative;
}

.trend-chart {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.trend-chart-bars {
  display: flex;
  height: 100%;
  align-items: flex-end;
  gap: 30px;
  overflow-x: auto;
  padding: 0 10px 40px 10px;
}

.trend-bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 0 0 80px;
}

.trend-bar-container {
  display: flex;
  align-items: flex-end;
  height: 200px;
  width: 80px;
  position: relative;
}

.trend-bar {
  width: 30px;
  position: relative;
  border-radius: 4px 4px 0 0;
  transition: height 0.5s ease;
}

.trend-bar.planned {
  background-color: #e2e8f0;
  margin-right: 5px;
}

.trend-bar.completed {
  background-color: #4f7cff;
  margin-left: 5px;
}

.trend-bar-label {
  font-size: 0.85rem;
  color: #666;
  margin-top: 8px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 80px;
}

.trend-bar-percentage {
  font-size: 0.85rem;
  font-weight: 500;
  color: #333;
  margin-top: 4px;
}

.no-data-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-style: italic;
}

/* Loading and Error Styling */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4f7cff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.loading-spinner.small {
  width: 24px;
  height: 24px;
  border-width: 3px;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.error-message {
  color: #e5534b;
  margin-bottom: 16px;
}

.error-message.small {
  font-size: 0.9rem;
  margin: 16px 0;
  text-align: center;
}

.retry-button {
  background: #4f7cff;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 500;
  cursor: pointer;
}

.retry-button.small {
  padding: 4px 8px;
  font-size: 0.85rem;
  margin-top: 8px;
}

@media (max-width: 768px) {
  .kpis-analysis-container {
    margin-left: 0;
    padding: 16px;
  }
  
  .kpi-visualizations {
    flex-direction: column;
    gap: 24px;
  }
  
  .date-range-picker {
    flex-direction: column;
  }
  
  .trend-chart-bars {
    padding-bottom: 60px;
  }
}
</style> 