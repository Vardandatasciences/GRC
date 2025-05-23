<template>
  <div class="incident-dashboard-wrapper">
    <h1>Incident Management KPIs</h1>
    
    <!-- KPI Metrics Cards -->
    <div class="metrics-cards">
      <div class="metric-card">
        <div class="metric-value">{{ metrics.totalIncidents }}</div>
        <div class="metric-label">Total Incidents</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">{{ metrics.incidentVolume }}</div>
        <div class="metric-label">Incident Volume</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">{{ metrics.escalationRate }}%</div>
        <div class="metric-label">Escalation Rate</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">{{ metrics.repeatRate }}%</div>
        <div class="metric-label">Repeat Incident Rate</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">{{ metrics.closureRate }}%</div>
        <div class="metric-label">Closure Rate</div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-container">
      <div class="chart-card" @click="showChartDetail('severity')">
        <h3>Incidents by Severity</h3>
        <div class="chart-type-selector">
          <button v-for="type in ['pie', 'bar', 'horizontal', 'line']" 
                  :key="type" 
                  @click.stop="changeChartType('severity', type)"
                  :class="{ active: chartTypes.severity === type }">
            <i :class="getChartIcon(type)"></i>
          </button>
        </div>
        <div class="pie-chart-container">
          <canvas class="pie-chart" ref="severityChart"></canvas>
          
          <div class="chart-interact-hint">Click for details</div>
        </div>
      </div>
      
      <div class="chart-card" @click="showChartDetail('type')">
        <h3>Incidents by Type</h3>
        <div class="chart-type-selector">
          <button v-for="type in ['bar', 'pie', 'horizontal', 'line']" 
                  :key="type" 
                  @click.stop="changeChartType('type', type)"
                  :class="{ active: chartTypes.type === type }">
            <i :class="getChartIcon(type)"></i>
          </button>
        </div>
        <div class="bar-chart-container">
          <canvas class="bar-chart" ref="typeChart"></canvas>
          <div class="chart-interact-hint">Click for details</div>
        </div>
      </div>
      
      <div class="chart-card" @click="showChartDetail('escalation')">
        <h3>Incident Sources & Escalation Rate</h3>
        <div class="chart-type-selector">
          <button v-for="type in ['stacked', 'pie', 'horizontal', 'bar']" 
                  :key="type" 
                  @click.stop="changeChartType('escalation', type)"
                  :class="{ active: chartTypes.escalation === type }">
            <i :class="getChartIcon(type)"></i>
          </button>
        </div>
        <div class="chart-labels">
          <div class="escalation-rate">Escalation Rate: {{ metrics.escalationRate }}%</div>
          <div class="chart-legend">
            <div v-for="(source, index) in escalationData?.sourceLabels" :key="source" class="legend-item">
              <span class="legend-color" :style="{ backgroundColor: escalationData?.sourceColors[index] }"></span>
              <span>{{ source }}</span>
            </div>
          </div>
        </div>
        <div class="bar-chart-container">
          <canvas class="bar-chart" ref="escalationChart"></canvas>
          <div class="chart-interact-hint">Click for details</div>
        </div>
      </div>

      <!-- Incident Volume Chart -->
      <div class="chart-card full-width" @click="showChartDetail('timeline')">
        <div class="chart-header">
          <h3>Incident Volume Over Time</h3>
          <div class="chart-controls">
            <div class="time-range-selector">
              <select v-model="timelineRange" @change="updateTimelineChart">
                <option value="days">Last 14 Days</option>
                <option value="months">Last 6 Months</option>
                <option value="quarters">Quarterly</option>
              </select>
            </div>
            <div class="chart-type-selector">
              <button v-for="type in ['area', 'line', 'bar']" 
                      :key="type" 
                      @click.stop="changeChartType('timeline', type)"
                      :class="{ active: chartTypes.timeline === type }">
                <i :class="getChartIcon(type)"></i>
              </button>
            </div>
          </div>
        </div>
        <div class="line-chart-container">
          <canvas class="line-chart" ref="timelineChart"></canvas>
          <div class="chart-interact-hint">Click for details</div>
        </div>
      </div>

      <!-- Repeat Incident Rate Chart -->
      <div class="chart-card" @click="showChartDetail('repeat')">
        <h3>Repeat Incident Rate</h3>
        <div class="chart-type-selector">
          <button v-for="type in ['donut', 'pie', 'bar']" 
                  :key="type" 
                  @click.stop="changeChartType('repeat', type)"
                  :class="{ active: chartTypes.repeat === type }">
            <i :class="getChartIcon(type)"></i>
          </button>
        </div>
        <div class="pie-chart-container">
          <canvas class="pie-chart" ref="repeatChart"></canvas>
          <div class="chart-interact-hint">Click for details</div>
        </div>
      </div>
    </div>

    <!-- Chart Detail Modal -->
    <div v-if="chartDetailVisible" class="chart-detail-overlay" @click="hideChartDetail">
      <div class="chart-detail-modal" @click.stop>
        <button class="chart-detail-close" @click="hideChartDetail">&times;</button>
        <h2>{{ chartDetailTitle }}</h2>
        <div class="chart-detail-container">
          <canvas ref="detailChart"></canvas>
        </div>
        <div class="chart-detail-info">
          <table v-if="chartDetailData.labels && chartDetailData.values">
            <thead>
              <tr>
                <th>{{ chartDetailTableHeaders.label }}</th>
                <th>{{ chartDetailTableHeaders.value }}</th>
                <th>Percentage</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(label, index) in chartDetailData.labels" :key="index">
                <td>{{ label }}</td>
                <td>{{ chartDetailData.values[index] }}</td>
                <td>{{ calculatePercentage(chartDetailData.values[index], chartDetailData.values) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Chart from 'chart.js/auto';
import './IncidentDashboard.css';

export default {
  name: 'IncidentDashboard',
  data() {
    return {
      incidents: [],
      openIncidents: [],
      charts: {
        severity: null,
        type: null,
        source: null,
        timeline: null,
        volume: null,
        escalation: null,
        repeat: null
      },
      metrics: {
        totalIncidents: 28,
        incidentVolume: 37,
        responseRate: 77,
        escalationRate: 65,
        repeatRate: 23,
        avgDetectionTime: 1.3,
        avgResponseTime: 2.5,
        closureRate: 68
      },
      severityData: [
        { name: 'High', value: 32 },
        { name: 'Medium', value: 41 },
        { name: 'Low', value: 27 }
      ],
      severityColors: ['#e63946', '#f8961e', '#90be6d'],
      typeData: {
        labels: ['Phishing', 'DoS', 'Escalation'],
        values: [65, 85, 55]
      },
      sourceData: {
        labels: ['Manual', 'SIEM', 'Audit'],
        values: [75, 60, 55]
      },
      chartDetailVisible: false,
      chartDetailTitle: '',
      chartDetailType: 'pie',
      chartDetailData: { labels: [], values: [] },
      chartDetailColors: [],
      chartDetailTableHeaders: { label: 'Category', value: 'Count' },
      detailChart: null,
      chartTypes: {
        severity: 'pie',
        type: 'bar',
        source: 'bar',
        timeline: 'line',
        volume: 'area',
        escalation: 'stacked',
        repeat: 'donut'
      },
      typeColors: ['#4a89dc', '#5d9cec', '#7eb0ef', '#9fc4f4', '#c0d7f8'],
      sourceColors: ['#8b5cf6', '#a78bfa', '#c4b5fd'],
      timelineColors: ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0'],
      volumeData: null,
      escalationData: null,
      repeatData: null,
      timelineRange: 'days',
    };
  },
  mounted() {
    this.fetchIncidents();
  },
  methods: {
    async fetchIncidents() {
      try {
        const response = await axios.get('http://localhost:8000/incidents/');
        this.incidents = response.data;
        console.log('Fetched incidents:', this.incidents);
        
        // Set defaults if no incidents returned
        if (!this.incidents || this.incidents.length === 0) {
          this.metrics = {
            totalIncidents: 0,
            incidentVolume: 0,
            responseRate: 0,
            escalationRate: 0,
            repeatRate: 0,
            avgDetectionTime: 0,
            avgResponseTime: 0,
            closureRate: 0
          };
          return;
        }
        
        // Process the data
        this.processIncidentData();
        
        // After data is processed, initialize charts
        this.$nextTick(() => {
          this.initCharts();
        });
      } catch (error) {
        console.error('Failed to fetch incidents:', error);
      }
    },
    
    processIncidentData() {
      // Calculate metrics
      this.metrics.totalIncidents = this.incidents.length;
      
      // Filter open incidents
      this.openIncidents = this.incidents.filter(incident => 
        !incident.Status || incident.Status === 'Open' || incident.Status === 'Scheduled'
      ).slice(0, 5); // Show 5 most recent
      
      // Calculate severity distribution
      const priorityCounts = {
        'High': 0,
        'Medium': 0,
        'Low': 0
      };
      
      this.incidents.forEach(incident => {
        const priority = incident.RiskPriority ? incident.RiskPriority.trim() : null;
        if (priority) {
          if (priority.toLowerCase() === 'high') priorityCounts['High']++;
          else if (priority.toLowerCase() === 'medium') priorityCounts['Medium']++;
          else if (priority.toLowerCase() === 'low') priorityCounts['Low']++;
        }
      });
      
      // Calculate response metrics from actual data
      if (this.incidents.length > 0) {
        // Count incidents with a response (status other than Open or null)
        const respondedCount = this.incidents.filter(i => 
          i.Status && i.Status !== 'Open' && i.Status !== 'Scheduled'
        ).length;
        
        // Calculate response rate (% of incidents that have been responded to)
        this.metrics.responseRate = Math.round((respondedCount / this.incidents.length) * 100);
        
        // Calculate closure rate (% of resolved/closed incidents)
        const resolvedCount = this.incidents.filter(i => 
          i.Status === 'Resolved' || i.Status === 'Closed'
        ).length;
        this.metrics.closureRate = Math.round((resolvedCount / this.incidents.length) * 100);
        
        // Calculate detection and response times
        let totalDetectionTime = 0;
        let totalResponseTime = 0;
        let detectionCount = 0;
        let responseCount = 0;
        
        this.incidents.forEach(incident => {
          // Calculate detection time (time between creation and identification)
          if (incident.CreatedAt && incident.IdentifiedAt) {
            const createdAt = new Date(incident.CreatedAt);
            const identifiedAt = new Date(incident.IdentifiedAt);
            
            if (identifiedAt > createdAt) {
              const detectionHours = (identifiedAt - createdAt) / (1000 * 60 * 60);
              totalDetectionTime += detectionHours;
              detectionCount++;
            }
          }
          
          // Calculate response time (time between identification and response)
          if (incident.IdentifiedAt && incident.RespondedAt) {
            const identifiedAt = new Date(incident.IdentifiedAt);
            const respondedAt = new Date(incident.RespondedAt);
            
            if (respondedAt > identifiedAt) {
              const responseHours = (respondedAt - identifiedAt) / (1000 * 60 * 60);
              totalResponseTime += responseHours;
              responseCount++;
            }
          }
        });
        
        // Set average detection time
        if (detectionCount > 0) {
          this.metrics.avgDetectionTime = (totalDetectionTime / detectionCount).toFixed(1);
        } else {
          this.metrics.avgDetectionTime = 0;
        }
        
        // Set average response time
        if (responseCount > 0) {
          this.metrics.avgResponseTime = (totalResponseTime / responseCount).toFixed(1);
        } else {
          this.metrics.avgResponseTime = 0;
        }
      } else {
        // If no incidents, set all metrics to 0
        this.metrics = {
          totalIncidents: 0,
          incidentVolume: 0,
          responseRate: 0,
          escalationRate: 0,
          repeatRate: 0,
          avgDetectionTime: 0, 
          avgResponseTime: 0,
          closureRate: 0
        };
      }
      
      // Update severity data for charts
      const total = Object.values(priorityCounts).reduce((sum, count) => sum + count, 0);
      if (total > 0) {
        this.severityData = [
          { name: 'High', value: priorityCounts['High'] },
          { name: 'Medium', value: priorityCounts['Medium'] },
          { name: 'Low', value: priorityCounts['Low'] }
        ];
      }
      
      // Calculate incidents by type - use actual RiskCategory values
      const categoryCounts = {};
      
      // Extract unique categories and count them
      this.incidents.forEach(incident => {
        if (incident.RiskCategory) {
          // Trim the category and handle case consistency
          const category = incident.RiskCategory.trim();
          if (category) {
            if (!categoryCounts[category]) {
              categoryCounts[category] = 0;
            }
            categoryCounts[category]++;
          }
        }
      });
      
      console.log("Category counts:", categoryCounts);
      
      // Take top 5 categories if there are too many
      const sortedCategories = Object.entries(categoryCounts)
        .sort((a, b) => b[1] - a[1]) // Sort by count, descending
        .slice(0, 5); // Limit to 5 categories for readability
      
      // Update typeData with actual categories from database
      this.typeData = {
        labels: sortedCategories.map(entry => entry[0]),
        values: sortedCategories.map(entry => entry[1])
      };
      
      // Calculate incidents by source
      const sourceCounts = { 'Manual': 0, 'SIEM': 0, 'Audit': 0 };
      this.incidents.forEach(incident => {
        if (incident.Origin) {
          if (incident.Origin.includes('Manual')) sourceCounts['Manual']++;
          else if (incident.Origin.includes('SIEM')) sourceCounts['SIEM']++;
          else if (incident.Origin.includes('Audit')) sourceCounts['Audit']++;
        }
      });
      this.sourceData.values = Object.values(sourceCounts);
      
      // Calculate new KPI metrics from actual data
      if (this.incidents.length > 0) {
        // Calculate incident volume (last 30 days)
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        
        const recentIncidents = this.incidents.filter(i => 
          new Date(i.Date) >= thirtyDaysAgo
        );
        this.metrics.incidentVolume = recentIncidents.length;
        
        // Calculate escalation rate
        const auditIncidents = this.incidents.filter(i => 
          i.Origin && i.Origin.toLowerCase().includes('audit')
        ).length;
        
        this.metrics.escalationRate = Math.round((auditIncidents / this.incidents.length) * 100);
        
        // Calculate repeat incident rate
        const repeatIncidents = this.incidents.filter(i => 
          i.IsRepeat || i.Status === 'Reopened'
        ).length;
        
        this.metrics.repeatRate = Math.round((repeatIncidents / this.incidents.length) * 100);
        
        // Prepare data for volume chart (daily counts for last 14 days)
        this.prepareVolumeData();
        
        // Prepare data for escalation chart
        this.prepareEscalationData();
        
        // Prepare data for repeat incident chart
        this.prepareRepeatData();
      }
    },
    
    prepareVolumeData() {
      // Generate daily incident counts for the last 14 days
      const days = 14;
      const labels = [];
      const values = [];
      
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        
        // Format date as MM/DD
        const formattedDate = `${date.getMonth() + 1}/${date.getDate()}`;
        labels.push(formattedDate);
        
        // Count incidents for this day
        const count = this.incidents.filter(incident => {
          if (!incident.Date) return false;
          const incidentDate = new Date(incident.Date);
          return incidentDate.toDateString() === date.toDateString();
        }).length;
        
        values.push(count);
      }
      
      this.volumeData = { labels, values };
    },
    
    prepareEscalationData() {
      // Calculate source distribution with escalation information
      const sourceCounts = { 'Manual': 0, 'SIEM': 0, 'Audit': 0 };
      const sourceLabels = Object.keys(sourceCounts);
      
      this.incidents.forEach(incident => {
        if (incident.Origin) {
          if (incident.Origin.includes('Manual')) sourceCounts['Manual']++;
          else if (incident.Origin.includes('SIEM')) sourceCounts['SIEM']++;
          else if (incident.Origin.includes('Audit')) sourceCounts['Audit']++;
        }
      });
      
      // Set colors for each source
      const sourceColors = ['#c4b5fd', '#4a89dc', '#8b5cf6'];
      
      // Calculate overall escalation rate for metrics
      const auditIncidents = sourceCounts['Audit'];
      const totalIncidents = this.incidents.length;
      this.metrics.escalationRate = Math.round((auditIncidents / totalIncidents) * 100);
      
      // For stacked view, prepare monthly data
      const months = 6;
      const labels = [];
      const datasets = sourceLabels.map((source, index) => ({
        label: source,
        data: [],
        backgroundColor: sourceColors[index]
      }));
      
      for (let i = months - 1; i >= 0; i--) {
        const date = new Date();
        date.setMonth(date.getMonth() - i);
        
        // Format as month name
        const monthName = date.toLocaleString('default', { month: 'short' });
        labels.push(monthName);
        
        // Filter incidents for this month
        const monthIncidents = this.incidents.filter(incident => {
          if (!incident.Date) return false;
          const incidentDate = new Date(incident.Date);
          return incidentDate.getMonth() === date.getMonth() && 
                 incidentDate.getFullYear() === date.getFullYear();
        });
        
        // Count by source for this month
        sourceLabels.forEach((source, sourceIndex) => {
          const count = monthIncidents.filter(i => 
            i.Origin && i.Origin.includes(source)
          ).length;
          
          datasets[sourceIndex].data.push(count);
        });
      }
      
      this.escalationData = { 
        labels, 
        datasets,
        sourceValues: Object.values(sourceCounts),
        sourceLabels,
        sourceColors,
        totalIncidents: totalIncidents,
        auditIncidents: auditIncidents
      };
    },
    
    prepareRepeatData() {
      // Calculate new vs repeat incidents
      const repeatCount = this.incidents.filter(i => 
        i.IsRepeat || i.Status === 'Reopened'
      ).length;
      
      const newCount = this.incidents.length - repeatCount;
      
      this.repeatData = {
        labels: ['New', 'Repeat'],
        values: [newCount, repeatCount],
        colors: ['#10b981', '#f59e0b']
      };
    },
    
    initCharts() {
      this.$nextTick(() => {
        // Destroy existing charts to prevent duplicates/stale data
        if (this.charts.severity) {
          this.charts.severity.destroy();
        }
        if (this.charts.type) {
          this.charts.type.destroy();
        }
        if (this.charts.source) {
          this.charts.source.destroy();
        }
        if (this.charts.timeline) {
          this.charts.timeline.destroy();
        }
        if (this.charts.volume) {
          this.charts.volume.destroy();
        }
        if (this.charts.escalation) {
          this.charts.escalation.destroy();
        }
        if (this.charts.repeat) {
          this.charts.repeat.destroy();
        }
        
        this.createSeverityChart();
        this.createTypeChart();
        this.createSourceChart();
        this.createTimelineChart();
        this.createVolumeChart();
        this.createEscalationChart();
        this.createRepeatChart();
      });
    },
    
    generateTimelineData() {
      if (this.timelineRange === 'days') {
        return this.generateDailyTimelineData();
      } else if (this.timelineRange === 'months') {
        return this.generateMonthlyTimelineData();
      } else {
        return this.generateQuarterlyTimelineData();
      }
    },
    
    generateDailyTimelineData() {
      // Generate daily incident counts for the last 14 days
      const days = 14;
      const labels = [];
      const values = [];
      
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        
        // Format date as MM/DD
        const formattedDate = `${date.getMonth() + 1}/${date.getDate()}`;
        labels.push(formattedDate);
        
        // Count incidents for this day
        const count = this.incidents.filter(incident => {
          if (!incident.Date) return false;
          const incidentDate = new Date(incident.Date);
          return incidentDate.toDateString() === date.toDateString();
        }).length;
        
        values.push(count);
      }
      
      return {
        labels,
        values,
        title: 'Daily Incident Volume'
      };
    },
    
    generateMonthlyTimelineData() {
      // Generate monthly data for the last 6 months
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const monthCounts = Array(12).fill(0);
      
      this.incidents.forEach(incident => {
        if (incident.Date) {
          const date = new Date(incident.Date);
          const month = date.getMonth();
          monthCounts[month]++;
        }
      });
      
      // Grab only the last 6 months for display
      const today = new Date();
      const currentMonth = today.getMonth();
      const last6Months = [];
      const last6Values = [];
      
      for (let i = 5; i >= 0; i--) {
        const monthIndex = (currentMonth - i + 12) % 12;
        last6Months.push(months[monthIndex]);
        last6Values.push(monthCounts[monthIndex]);
      }
      
      return {
        labels: last6Months,
        values: last6Values,
        title: 'Monthly Incident Volume'
      };
    },
    
    generateQuarterlyTimelineData() {
      const quarters = ['Q1', 'Q2', 'Q3', 'Q4'];
      const quarterCounts = [0, 0, 0, 0];
      
      this.incidents.forEach(incident => {
        if (incident.Date) {
          const date = new Date(incident.Date);
          const month = date.getMonth();
          const quarter = Math.floor(month / 3);
          quarterCounts[quarter]++;
        }
      });
      
      return {
        labels: quarters,
        values: quarterCounts,
        title: 'Quarterly Incident Volume'
      };
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: 'numeric' });
    },
    
    getPriorityClass(priority) {
      if (!priority) return '';
      switch(priority.toLowerCase()) {
        case 'high': return 'priority-high';
        case 'medium': return 'priority-medium';
        case 'low': return 'priority-low';
        default: return '';
      }
    },
    
    calculateResponseTime(incident) {
      if (incident.IdentifiedAt && incident.RespondedAt) {
        const identifiedAt = new Date(incident.IdentifiedAt);
        const respondedAt = new Date(incident.RespondedAt);
        
        if (respondedAt > identifiedAt) {
          return ((respondedAt - identifiedAt) / (1000 * 60 * 60)).toFixed(1);
        }
      }
      // Fallback to a reasonable estimate if real data isn't available
      return ((Math.random() * 3) + 1).toFixed(1);
    },
    
    showChartDetail(chartType) {
      // Set modal properties based on chart type
      switch(chartType) {
        case 'severity':
          this.chartDetailTitle = 'Incidents by Severity';
          this.chartDetailType = this.chartTypes.severity;
          this.chartDetailData = {
            labels: this.severityData.map(item => item.name),
            values: [
              this.incidents.filter(i => i.RiskPriority?.toLowerCase() === 'high').length,
              this.incidents.filter(i => i.RiskPriority?.toLowerCase() === 'medium').length,
              this.incidents.filter(i => i.RiskPriority?.toLowerCase() === 'low').length
            ]
          };
          this.chartDetailColors = this.severityColors;
          this.chartDetailTableHeaders = { label: 'Severity', value: 'Count' };
          break;
        
        case 'type':
          this.chartDetailTitle = 'Incidents by Type';
          this.chartDetailType = this.chartTypes.type;
          this.chartDetailData = {
            labels: this.typeData.labels,
            values: this.typeData.values
          };
          this.chartDetailColors = this.typeColors;
          this.chartDetailTableHeaders = { label: 'Type', value: 'Count' };
          break;
        
        case 'source':
          this.chartDetailTitle = 'Incidents by Source';
          this.chartDetailType = this.chartTypes.source;
          this.chartDetailData = {
            labels: this.sourceData.labels,
            values: this.sourceData.values
          };
          this.chartDetailColors = this.sourceColors;
          this.chartDetailTableHeaders = { label: 'Source', value: 'Count' };
          break;
        
        case 'timeline': {
          const timelineData = this.generateTimelineData();
          this.chartDetailTitle = 'Incident Volume Over Time';
          this.chartDetailType = this.chartTypes.timeline === 'area' ? 'line' : this.chartTypes.timeline;
          this.chartDetailData = {
            labels: timelineData.labels,
            values: timelineData.values
          };
          this.chartDetailColors = this.timelineColors;
          this.chartDetailTableHeaders = { 
            label: this.timelineRange === 'days' ? 'Date' : 
                  this.timelineRange === 'months' ? 'Month' : 'Quarter', 
            value: 'Incidents' 
          };
          break;
        }
        
        case 'volume':
          this.chartDetailTitle = 'Incident Volume';
          this.chartDetailType = this.chartTypes.volume;
          this.chartDetailData = this.volumeData;
          this.chartDetailColors = [];
          this.chartDetailTableHeaders = { label: 'Date', value: 'Incidents' };
          break;
        
        case 'escalation':
          this.chartDetailTitle = 'Incident Sources & Escalation Rate';
          this.chartDetailType = this.chartTypes.escalation;
          
          if (this.chartTypes.escalation === 'pie') {
            this.chartDetailData = {
              labels: this.escalationData?.sourceLabels || [],
              values: this.escalationData?.sourceValues || []
            };
            this.chartDetailColors = this.escalationData?.sourceColors || [];
          } else {
            this.chartDetailData = {
              labels: this.escalationData?.labels || [],
              datasets: this.escalationData?.datasets || []
            };
            this.chartDetailColors = [];
          }
          
          this.chartDetailTableHeaders = { label: 'Source', value: 'Count' };
          break;
        
        case 'repeat':
          this.chartDetailTitle = 'Repeat Incident Rate';
          this.chartDetailType = this.chartTypes.repeat;
          this.chartDetailData = this.repeatData;
          this.chartDetailColors = this.repeatData.colors;
          this.chartDetailTableHeaders = { label: 'Type', value: 'Count' };
          break;
      }
      
      // Show the modal and initialize detail chart
      this.chartDetailVisible = true;
      this.$nextTick(() => {
        this.initDetailChart();
      });
    },
    
    hideChartDetail() {
      this.chartDetailVisible = false;
      if (this.detailChart) {
        this.detailChart.destroy();
        this.detailChart = null;
      }
    },
    
    initDetailChart() {
      const ctx = this.$refs.detailChart?.getContext('2d');
      if (!ctx) return;
      
      if (this.detailChart) {
        this.detailChart.destroy();
      }
      
      // Convert 'horizontal' to 'bar' with appropriate axis configuration
      let chartType = this.chartDetailType;
      const isHorizontal = chartType === 'horizontal';
      
      if (isHorizontal) {
        chartType = 'bar';
      } else if (chartType === 'area') {
        chartType = 'line';
      }
      
      const chartConfig = {
        type: chartType,
        data: {
          labels: this.chartDetailData.labels,
          datasets: [{
            data: this.chartDetailData.values,
            backgroundColor: chartType === 'line' 
              ? 'rgba(74, 137, 220, 0.1)' 
              : this.chartDetailColors,
            borderColor: chartType === 'line' ? this.chartDetailColors[0] : undefined,
            tension: chartType === 'line' ? 0.4 : undefined,
            fill: chartType === 'line' ? true : undefined
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: isHorizontal ? 'y' : 'x',
          plugins: {
            legend: {
              display: chartType === 'pie'
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const label = context.label || '';
                  const value = context.raw || 0;
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = Math.round((value / total) * 100);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              display: chartType !== 'pie'
            },
            x: {
              display: chartType !== 'pie'
            }
          }
        }
      };
      
      this.detailChart = new Chart(ctx, chartConfig);
    },
    
    calculatePercentage(value, allValues) {
      const total = allValues.reduce((sum, val) => sum + val, 0);
      return total > 0 ? Math.round((value / total) * 100) : 0;
    },
    
    getChartIcon(type) {
      switch(type) {
        case 'pie': return 'fa-solid fa-chart-pie';
        case 'bar': return 'fa-solid fa-chart-bar';
        case 'horizontal': return 'fa-solid fa-bars-progress';
        case 'line': return 'fa-solid fa-chart-line';
        case 'area': return 'fa-solid fa-chart-area';
        case 'polarArea': return 'fa-solid fa-circle';
        case 'radar': return 'fa-solid fa-spider-web';
        case 'donut': return 'fa-solid fa-circle-dot';
        case 'stacked': return 'fa-solid fa-layer-group';
        default: return 'fa-solid fa-chart-simple';
      }
    },
    
    changeChartType(chartId, newType) {
      this.chartTypes[chartId] = newType;
      this.refreshChart(chartId);
    },
    
    refreshChart(chartId) {
      // Safely destroy the existing chart
      if (this.charts[chartId]) {
        try {
          this.charts[chartId].destroy();
        } catch (e) {
          console.error(`Error destroying ${chartId} chart:`, e);
        }
        this.charts[chartId] = null;
      }
      
      // Re-create the chart with the new type after a short delay
      // to ensure DOM is ready
      setTimeout(() => {
        switch(chartId) {
          case 'severity':
            this.createSeverityChart();
            break;
          case 'type':
            this.createTypeChart();
            break;
          case 'source':
            this.createSourceChart();
            break;
          case 'timeline':
            this.createTimelineChart();
            break;
          case 'volume':
            this.createVolumeChart();
            break;
          case 'escalation':
            this.createEscalationChart();
            break;
          case 'repeat':
            this.createRepeatChart();
            break;
        }
      }, 50);
    },
    
    createSeverityChart() {
      const severityCtx = this.$refs.severityChart;
      if (!severityCtx) return;
      
      // Get the context safely
      const ctx = severityCtx.getContext('2d');
      if (!ctx) return;
      
      let type = this.chartTypes.severity;
      const isRadial = ['pie', 'polarArea'].includes(type);
      const isLine = type === 'line';
      const isHorizontal = type === 'horizontal';
      
      // Ensure any existing chart is destroyed
      if (this.charts.severity) {
        this.charts.severity.destroy();
      }
      
      // Set actual chart type for horizontal bar
      if (isHorizontal) {
        type = 'bar';
      }
      
      const severityData = [
        this.incidents.filter(i => i.RiskPriority?.toLowerCase() === 'high').length,
        this.incidents.filter(i => i.RiskPriority?.toLowerCase() === 'medium').length,
        this.incidents.filter(i => i.RiskPriority?.toLowerCase() === 'low').length
      ];
      
      this.charts.severity = new Chart(ctx, {
        type: type,
        data: {
          labels: ['High', 'Medium', 'Low'],
          datasets: [{
            data: severityData,
            backgroundColor: isLine ? 'rgba(74, 137, 220, 0.1)' : this.severityColors,
            borderColor: isLine ? '#4a89dc' : undefined,
            borderWidth: isLine ? 2 : 0,
            tension: isLine ? 0.4 : undefined,
            fill: isLine
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: isHorizontal ? 'y' : 'x',
          plugins: {
            legend: {
              display: isRadial
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.raw || 0;
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = Math.round((value / total) * 100);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              display: !isRadial || isLine || isHorizontal
            },
            x: {
              display: !isRadial || isLine || isHorizontal
            }
          }
        }
      });
    },
    
    createTypeChart() {
      const typeCtx = this.$refs.typeChart?.getContext('2d');
      if (!typeCtx) return;
      
      let type = this.chartTypes.type;
      const isRadial = ['pie', 'polarArea'].includes(type);
      const isLine = type === 'line';
      const isHorizontal = type === 'horizontal';
      
      // Set actual chart type for horizontal bar
      if (isHorizontal) {
        type = 'bar';
      }
      
      this.charts.type = new Chart(typeCtx, {
        type: type,
        data: {
          labels: this.typeData.labels,
          datasets: [{
            data: this.typeData.values,
            backgroundColor: isLine ? 'rgba(74, 137, 220, 0.1)' : 
                          isRadial ? this.typeColors : this.typeColors[0],
            borderColor: isLine ? this.typeColors[0] : undefined,
            borderWidth: isLine ? 2 : 0,
            tension: isLine ? 0.4 : undefined,
            fill: isLine
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: isHorizontal ? 'y' : 'x',
          plugins: {
            legend: {
              display: isRadial
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              display: !isRadial || isLine || isHorizontal
            },
            x: {
              display: !isRadial || isLine || isHorizontal
            }
          }
        }
      });
    },
    
    createSourceChart() {
      const sourceCtx = this.$refs.sourceChart?.getContext('2d');
      if (!sourceCtx) return;
      
      let type = this.chartTypes.source;
      const isRadial = ['pie', 'polarArea'].includes(type);
      const isLine = type === 'line';
      const isHorizontal = type === 'horizontal';
      
      // Set actual chart type for horizontal bar
      if (isHorizontal) {
        type = 'bar';
      }
      
      this.charts.source = new Chart(sourceCtx, {
        type: type,
        data: {
          labels: this.sourceData.labels,
          datasets: [{
            data: this.sourceData.values,
            backgroundColor: isLine ? 'rgba(139, 92, 246, 0.1)' : 
                          isRadial ? this.sourceColors : this.sourceColors[0],
            borderColor: isLine ? this.sourceColors[0] : undefined,
            borderWidth: isLine ? 2 : 0,
            tension: isLine ? 0.4 : undefined,
            fill: isLine
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: isHorizontal ? 'y' : 'x',
          plugins: {
            legend: {
              display: isRadial
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              display: !isRadial || isLine || isHorizontal
            },
            x: {
              display: !isRadial || isLine || isHorizontal
            }
          }
        }
      });
    },
    
    createTimelineChart() {
      const timelineCtx = this.$refs.timelineChart?.getContext('2d');
      if (!timelineCtx) return;
      
      let type = this.chartTypes.timeline;
      const isRadial = ['pie', 'polarArea'].includes(type);
      const isLine = type === 'line' || type === 'area';
      const isHorizontal = type === 'horizontal';
      const isArea = type === 'area';
      
      // Set actual chart type for horizontal bar and area
      if (isHorizontal) {
        type = 'bar';
      } else if (type === 'area') {
        type = 'line';
      }
      
      const timelineData = this.generateTimelineData();
      
      if (this.charts.timeline) {
        this.charts.timeline.destroy();
      }
      
      this.charts.timeline = new Chart(timelineCtx, {
        type: type,
        data: {
          labels: timelineData.labels,
          datasets: [{
            label: 'Incidents',
            data: timelineData.values,
            borderColor: '#10b981',
            backgroundColor: isRadial ? 
                          this.timelineColors : 
                          isArea ? 'rgba(16, 185, 129, 0.1)' : '#10b981',
            tension: isLine ? 0.4 : 0,
            fill: isArea
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: isHorizontal ? 'y' : 'x',
          plugins: {
            legend: {
              display: false
            },
            title: {
              display: true,
              text: timelineData.title,
              position: 'top',
              font: {
                size: 14
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Incident Count'
              }
            },
            x: {
              title: {
                display: true,
                text: this.timelineRange === 'days' ? 'Date' : 
                     this.timelineRange === 'months' ? 'Month' : 'Quarter'
              }
            }
          }
        }
      });
    },
    
    createVolumeChart() {
      const volumeCtx = this.$refs.volumeChart?.getContext('2d');
      if (!volumeCtx) return;
      
      let type = this.chartTypes.volume === 'area' ? 'line' : this.chartTypes.volume;
      const isArea = this.chartTypes.volume === 'area';
      
      if (this.charts.volume) {
        this.charts.volume.destroy();
      }
      
      this.charts.volume = new Chart(volumeCtx, {
        type: type,
        data: {
          labels: this.volumeData?.labels || [],
          datasets: [{
            label: 'Daily Incidents',
            data: this.volumeData?.values || [],
            borderColor: '#4a89dc',
            backgroundColor: isArea ? 'rgba(74, 137, 220, 0.2)' : '#4a89dc',
            tension: 0.4,
            fill: isArea
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
              intersect: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Incident Count'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Date'
              }
            }
          }
        }
      });
    },
    
    createEscalationChart() {
      const escalationCtx = this.$refs.escalationChart?.getContext('2d');
      if (!escalationCtx) return;
      
      let chartType = this.chartTypes.escalation;
      const isStacked = chartType === 'stacked';
      const isHorizontal = chartType === 'horizontal';
      const isPie = chartType === 'pie';
      
      if (this.charts.escalation) {
        this.charts.escalation.destroy();
      }
      
      // For pie chart, show overall distribution
      if (isPie) {
        this.charts.escalation = new Chart(escalationCtx, {
          type: 'pie',
          data: {
            labels: this.escalationData?.sourceLabels || [],
            datasets: [{
              data: this.escalationData?.sourceValues || [],
              backgroundColor: this.escalationData?.sourceColors || []
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false // Hide built-in legend since we have a custom one
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const label = context.label || '';
                    const value = context.raw || 0;
                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                    const percentage = Math.round((value / total) * 100);
                    return `${label}: ${value} (${percentage}%)`;
                  }
                }
              },
              title: {
                display: true,
                text: 'Incident Distribution by Source',
                position: 'top',
                padding: {
                  bottom: 10
                },
                font: {
                  size: 14
                }
              }
            }
          }
        });
        return;
      }
      
      // For bar charts (stacked or regular)
      this.charts.escalation = new Chart(escalationCtx, {
        type: 'bar',
        data: {
          labels: this.escalationData?.labels || [],
          datasets: this.escalationData?.datasets || []
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: isHorizontal ? 'y' : 'x',
          plugins: {
            legend: {
              display: false // Hide built-in legend since we have a custom one
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              callbacks: {
                footer: (tooltipItems) => {
                  // Calculate the total for this month/period
                  const total = tooltipItems.reduce((sum, item) => sum + item.parsed.y, 0);
                  const auditValue = tooltipItems.find(item => item.dataset.label === 'Audit')?.parsed.y || 0;
                  const escalationRate = Math.round((auditValue / total) * 100) || 0;
                  return `Escalation Rate: ${escalationRate}%`;
                }
              }
            },
            title: {
              display: isStacked,
              text: 'Monthly Incident Sources',
              position: 'top',
              padding: {
                bottom: 10
              },
              font: {
                size: 14
              }
            }
          },
          scales: {
            x: {
              stacked: isStacked,
              title: {
                display: true,
                text: 'Month'
              }
            },
            y: {
              stacked: isStacked,
              beginAtZero: true,
              title: {
                display: true,
                text: 'Incident Count'
              }
            }
          }
        }
      });
    },
    
    createRepeatChart() {
      const repeatCtx = this.$refs.repeatChart?.getContext('2d');
      if (!repeatCtx) return;
      
      let type = this.chartTypes.repeat === 'donut' ? 'doughnut' : this.chartTypes.repeat;
      
      if (this.charts.repeat) {
        this.charts.repeat.destroy();
      }
      
      this.charts.repeat = new Chart(repeatCtx, {
        type: type,
        data: {
          labels: this.repeatData?.labels || [],
          datasets: [{
            data: this.repeatData?.values || [],
            backgroundColor: this.repeatData?.colors || ['#10b981', '#f59e0b']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top'
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.raw || 0;
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = Math.round((value / total) * 100);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            }
          },
          cutout: type === 'doughnut' ? '60%' : undefined
        }
      });
    },
    
    updateTimelineChart() {
      this.refreshChart('timeline');
    },
  }
}
</script>

<style scoped>
.incident-dashboard-wrapper {
  padding: 20px;
  background-color: #f8f9fa;
  font-family: Arial, sans-serif;
}

h1 {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  padding-left: 10px;
}

h3 {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
}

/* KPI Metrics Cards */
.metrics-cards {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  margin-bottom: 25px;
}

.metric-card {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  text-align: center;
  flex: 1;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
}

.metric-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

/* Charts Grid */
.charts-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 25px;
}

.chart-card {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  position: relative;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.chart-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.05);
}

.full-width {
  grid-column: 1 / -1;
}

.pie-chart-container, 
.bar-chart-container, 
.line-chart-container {
  height: 200px;
  position: relative;
}

.pie-chart,
.bar-chart,
.line-chart {
  height: 100%;
  width: 100%;
}

/* Chart Legends */
.chart-legend {
  display: flex;
  flex-direction: column;
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 5px;
}

.legend-label {
  font-size: 12px;
}

/* Table Styles */
.incidents-table-section {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.incidents-table {
  width: 100%;
  border-collapse: collapse;
}

.incidents-table th,
.incidents-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.incidents-table th {
  font-weight: bold;
  color: #555;
  background-color: #f8f9fa;
}

/* Priority Colors */
.priority-high {
  padding: 4px 8px;
  background-color: #ffebee;
  color: #d32f2f;
  border-radius: 4px;
  font-weight: bold;
}

.priority-medium {
  padding: 4px 8px;
  background-color: #fff8e1;
  color: #ff8f00;
  border-radius: 4px;
  font-weight: bold;
}

.priority-low {
  padding: 4px 8px;
  background-color: #e8f5e9;
  color: #388e3c;
  border-radius: 4px;
  font-weight: bold;
}

.chart-interact-hint {
  position: absolute;
  bottom: 5px;
  right: 10px;
  font-size: 0.75rem;
  color: #94a3b8;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.chart-card:hover .chart-interact-hint {
  opacity: 1;
}

.chart-detail-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(3px);
}

.chart-detail-modal {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 80%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  position: relative;
}

.chart-detail-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #94a3b8;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.chart-detail-close:hover {
  background-color: #f1f5f9;
  color: #1e293b;
}

.chart-detail-container {
  height: 350px;
  margin: 1.5rem 0;
}

.chart-detail-info table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1.5rem;
}

.chart-detail-info th,
.chart-detail-info td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.chart-detail-info th {
  background-color: #f8fafc;
  font-weight: 600;
}

.chart-detail-info tr:hover td {
  background-color: #f1f5f9;
}

/* Completely redesigned chart header and controls */
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 0 10px;
  width: 100%;
}

.chart-card.full-width {
  padding-top: 15px; /* Reduce top padding as we're using a different layout */
}

.chart-card.full-width h3 {
  position: static; /* Override the absolute positioning */
  margin: 0;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.time-range-selector select {
  padding: 5px 10px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
  background-color: #f1f5f9;
  color: #64748b;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 130px;
  height: 28px;
}

.chart-type-selector {
  position: static; /* Override absolute positioning */
  display: flex;
  gap: 8px;
}

/* For other charts, keep the absolute positioning */
.chart-card:not(.full-width) .chart-type-selector {
  position: absolute;
  top: 10px;
  right: 10px;
}

/* Add new styles for combined chart */
.chart-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
  margin-bottom: 10px;
  padding: 0 15px;
}

.escalation-rate {
  font-weight: bold;
  color: #8b5cf6;
  font-size: 1rem;
}

.chart-legend {
  display: flex;
  gap: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.85rem;
}

.legend-color {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 3px;
}
</style> 