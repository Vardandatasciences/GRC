<template>
  <div class="incident-dashboard-wrapper">
    <!-- First row of KPI cards - Detection and Response Times -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Mean Time to Detect (MTTD)</h3>
        <div class="kpi-value">
          {{ kpiData.mttd.value }}<span class="unit">{{ kpiData.mttd.unit }}</span>
          <span :class="['value-change', kpiData.mttd.change_percentage > 0 ? 'positive' : 'negative']">
            <i :class="kpiData.mttd.change_percentage > 0 ? 'fas fa-caret-up' : 'fas fa-caret-down'"></i>
            {{ Math.abs(kpiData.mttd.change_percentage) }}%
          </span>
        </div>
        <div class="kpi-chart">
          <div class="line-chart">
            <svg viewBox="0 0 300 60" preserveAspectRatio="none">
              <!-- Create dynamic path based on trend data -->
              <path v-if="kpiData.mttd.trend && kpiData.mttd.trend.length > 0"
                    :d="generateTrendPath(kpiData.mttd.trend.map(t => t.minutes || t.hours))"
                    fill="none" stroke="#3498db" stroke-width="2"></path>
              
              <!-- Create dynamic data points -->
              <template v-if="kpiData.mttd.trend && kpiData.mttd.trend.length > 0">
                <circle v-for="(point, index) in getTrendPoints(kpiData.mttd.trend.map(t => t.minutes || t.hours))" 
                        :key="'mttd-point-'+index"
                        :cx="point.x" 
                        :cy="point.y" 
                        r="3" 
                        fill="#3498db"/>
              </template>
            </svg>
          </div>
          <div class="chart-months">
            <span v-for="(item, index) in kpiData.mttd.trend" :key="'mttd-month-'+index">
              {{ item.month }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Mean Time to Respond (MTTR)</h3>
        <div class="kpi-value">
          6<span class="unit">hours</span>
          <span class="value-change negative"><i class="fas fa-caret-down"></i>2.1%</span>
        </div>
        <div class="kpi-chart">
          <div class="line-chart">
            <svg viewBox="0 0 300 60" preserveAspectRatio="none">
              <path d="M0,35 C25,40 50,30 75,35 C100,40 125,25 150,30 C175,35 200,30 225,20 C250,10 275,15 300,20" 
                fill="none" stroke="#3498db" stroke-width="2"></path>
              <circle cx="0" cy="35" r="3" fill="#3498db"/>
              <circle cx="50" cy="30" r="3" fill="#3498db"/>
              <circle cx="100" cy="40" r="3" fill="#3498db"/>
              <circle cx="150" cy="30" r="3" fill="#3498db"/>
              <circle cx="200" cy="30" r="3" fill="#3498db"/>
              <circle cx="250" cy="10" r="3" fill="#3498db"/>
              <circle cx="300" cy="20" r="3" fill="#3498db"/>
            </svg>
          </div>
          <div class="chart-months">
            <span>Jan</span>
            <span>Feb</span>
            <span>Mar</span>
            <span>Apr</span>
            <span>May</span>
            <span>Jun</span>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Mean Time to Contain (MTTC)</h3>
        <div class="kpi-value">
          12<span class="unit">hours</span>
          <span class="value-change positive"><i class="fas fa-caret-up"></i>0.8%</span>
      </div>
        <div class="kpi-chart">
          <div class="line-chart">
            <svg viewBox="0 0 300 60" preserveAspectRatio="none">
              <path d="M0,25 C25,30 50,35 75,25 C100,15 125,20 150,30 C175,40 200,35 225,30 C250,25 275,20 300,25" 
                fill="none" stroke="#3498db" stroke-width="2"></path>
              <circle cx="0" cy="25" r="3" fill="#3498db"/>
              <circle cx="50" cy="35" r="3" fill="#3498db"/>
              <circle cx="100" cy="15" r="3" fill="#3498db"/>
              <circle cx="150" cy="30" r="3" fill="#3498db"/>
              <circle cx="200" cy="35" r="3" fill="#3498db"/>
              <circle cx="250" cy="20" r="3" fill="#3498db"/>
              <circle cx="300" cy="25" r="3" fill="#3498db"/>
            </svg>
          </div>
          <div class="chart-months">
            <span>Jan</span>
            <span>Feb</span>
            <span>Mar</span>
            <span>Apr</span>
            <span>May</span>
            <span>Jun</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Second row of KPI cards - Resolution Metrics -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Mean Time to Resolve (MTTRv)</h3>
        <div class="kpi-value">
          35<span class="unit">hours</span>
          <span class="value-change negative"><i class="fas fa-caret-down"></i>2.0%</span>
        </div>
        <div class="kpi-chart">
          <div class="line-chart">
            <svg viewBox="0 0 300 60" preserveAspectRatio="none">
              <path d="M0,20 C25,25 50,20 75,15 C100,10 125,15 150,20 C175,25 200,20 225,15 C250,10 275,15 300,20" 
                fill="none" stroke="#3498db" stroke-width="2"></path>
              <circle cx="0" cy="20" r="3" fill="#3498db"/>
              <circle cx="50" cy="20" r="3" fill="#3498db"/>
              <circle cx="100" cy="10" r="3" fill="#3498db"/>
              <circle cx="150" cy="20" r="3" fill="#3498db"/>
              <circle cx="200" cy="20" r="3" fill="#3498db"/>
              <circle cx="250" cy="10" r="3" fill="#3498db"/>
              <circle cx="300" cy="20" r="3" fill="#3498db"/>
            </svg>
          </div>
          <div class="chart-months">
            <span>Jan</span>
            <span>Feb</span>
            <span>Mar</span>
            <span>Apr</span>
            <span>May</span>
            <span>Jun</span>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>First Response Time</h3>
        <div class="kpi-value">
          3.5<span class="unit">hours</span>
          <span class="value-change positive"><i class="fas fa-caret-up"></i>1.5%</span>
        </div>
        <div class="kpi-chart">
          <div class="line-chart">
            <svg viewBox="0 0 300 60" preserveAspectRatio="none">
              <path d="M0,30 C25,25 50,30 75,35 C100,40 125,35 150,30 C175,25 200,20 225,25 C250,30 275,25 300,20" 
                fill="none" stroke="#3498db" stroke-width="2"></path>
              <circle cx="0" cy="30" r="3" fill="#3498db"/>
              <circle cx="50" cy="30" r="3" fill="#3498db"/>
              <circle cx="100" cy="40" r="3" fill="#3498db"/>
              <circle cx="150" cy="30" r="3" fill="#3498db"/>
              <circle cx="200" cy="20" r="3" fill="#3498db"/>
              <circle cx="250" cy="30" r="3" fill="#3498db"/>
              <circle cx="300" cy="20" r="3" fill="#3498db"/>
            </svg>
          </div>
          <div class="chart-months">
            <span>Jan</span>
            <span>Feb</span>
            <span>Mar</span>
            <span>Apr</span>
            <span>May</span>
            <span>Jun</span>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Time to Escalation</h3>
        <div class="kpi-value">
          5.2<span class="unit">hours</span>
          <span class="value-change negative"><i class="fas fa-caret-down"></i>3.5%</span>
      </div>
        <div class="kpi-chart">
          <div class="line-chart">
            <svg viewBox="0 0 300 60" preserveAspectRatio="none">
              <path d="M0,20 C25,25 50,20 75,15 C100,20 125,25 150,30 C175,35 200,30 225,25 C250,20 275,15 300,20" 
                fill="none" stroke="#3498db" stroke-width="2"></path>
              <circle cx="0" cy="20" r="3" fill="#3498db"/>
              <circle cx="50" cy="20" r="3" fill="#3498db"/>
              <circle cx="100" cy="15" r="3" fill="#3498db"/>
              <circle cx="150" cy="30" r="3" fill="#3498db"/>
              <circle cx="200" cy="30" r="3" fill="#3498db"/>
              <circle cx="250" cy="15" r="3" fill="#3498db"/>
              <circle cx="300" cy="20" r="3" fill="#3498db"/>
            </svg>
          </div>
          <div class="chart-months">
            <span>Jan</span>
            <span>Feb</span>
            <span>Mar</span>
            <span>Apr</span>
            <span>May</span>
            <span>Jun</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Third row of KPI cards - Incident Volume Metrics -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Number of Incidents Detected</h3>
        <div class="kpi-value">48</div>
        <div class="kpi-chart">
          <div class="bar-chart vertical">
            <div class="bar" style="height: 30%"></div>
            <div class="bar" style="height: 40%"></div>
            <div class="bar" style="height: 35%"></div>
            <div class="bar" style="height: 60%"></div>
            <div class="bar" style="height: 85%"></div>
            <div class="bar" style="height: 50%"></div>
            <div class="bar" style="height: 35%"></div>
          </div>
        </div>
        <div class="chart-labels">
          <span>M</span>
          <span>T</span>
          <span>W</span>
          <span>T</span>
          <span>F</span>
          <span>S</span>
          <span>S</span>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Number of Reopened Incidents</h3>
        <div class="kpi-value">7</div>
        <div class="kpi-chart">
          <div class="progress-bar">
            <div class="progress" style="width: 15%"></div>
          </div>
        </div>
        <div class="chart-values">
          <span>15% of total incidents</span>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Incident Closure Rate</h3>
        <div class="kpi-value">76<span class="unit">%</span></div>
        <div class="kpi-chart">
          <div class="progress-bar">
            <div class="progress" style="width: 76%"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Fourth row of KPI cards - Quality Metrics -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>False Positive Rate</h3>
        <div class="kpi-value">12<span class="unit">%</span></div>
        <div class="kpi-chart">
          <div class="donut-chart">
            <div class="donut-hole"></div>
            <div class="donut-segment" style="--start-angle: 0deg; --end-angle: 43.2deg;"></div>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Detection Accuracy</h3>
        <div class="kpi-value">88<span class="unit">%</span></div>
        <div class="kpi-chart">
          <div class="progress-bar">
            <div class="progress" style="width: 88%"></div>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>SLA Compliance Rate</h3>
        <div class="kpi-value">82<span class="unit">%</span></div>
        <div class="kpi-chart">
          <div class="progress-bar">
            <div class="progress" style="width: 82%"></div>
          </div>
          </div>
        </div>
      </div>
      
    <!-- Fifth row of KPI cards - Categorization Metrics -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Percentage of Incidents by Severity</h3>
        <div class="kpi-chart pie-chart-container">
          <div class="pie-chart">
            <div class="pie-segment critical" style="--segment-size: 25%;"></div>
            <div class="pie-segment high" style="--segment-size: 35%;"></div>
            <div class="pie-segment medium" style="--segment-size: 30%;"></div>
            <div class="pie-segment low" style="--segment-size: 10%;"></div>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item"><span class="legend-color critical"></span>Critical (25%)</div>
          <div class="legend-item"><span class="legend-color high"></span>High (35%)</div>
          <div class="legend-item"><span class="legend-color medium"></span>Medium (30%)</div>
          <div class="legend-item"><span class="legend-color low"></span>Low (10%)</div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>User-Reported vs System-Detected</h3>
        <div class="kpi-chart pie-chart-container">
          <div class="pie-chart">
            <div class="pie-segment user" style="--segment-size: 65%;"></div>
            <div class="pie-segment system" style="--segment-size: 35%;"></div>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item"><span class="legend-color user"></span>User (65%)</div>
          <div class="legend-item"><span class="legend-color system"></span>System (35%)</div>
        </div>
      </div>
      
      <!-- <div class="kpi-card">
        <h3>Incident Recurrence Rate</h3>
        <div class="kpi-value">6.5<span class="unit">%</span></div>
        <div class="kpi-chart">
          <div class="trend-line"></div>
        </div>
      </div> -->
    </div>

    <!-- Sixth row of KPI cards - Cost and Impact -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Cost per Incident</h3>
        <div class="kpi-value">₹184K</div>
        <div class="kpi-chart">
          <div class="bar-chart horizontal">
            <div class="bar critical" style="width: 80%">₹325K - Critical</div>
            <div class="bar high" style="width: 60%">₹210K - High</div>
            <div class="bar medium" style="width: 40%">₹125K - Medium</div>
            <div class="bar low" style="width: 20%">₹75K - Low</div>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Automated vs Manual Responses</h3>
        <div class="kpi-chart pie-chart-container">
          <div class="pie-chart">
            <div class="pie-segment automated" style="--segment-size: 40%;"></div>
            <div class="pie-segment manual" style="--segment-size: 60%;"></div>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item"><span class="legend-color automated"></span>Automated (40%)</div>
          <div class="legend-item"><span class="legend-color manual"></span>Manual (60%)</div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Resolution SLA Breach Rate</h3>
        <div class="kpi-value">18<span class="unit">%</span></div>
        <div class="kpi-chart">
            <div class="progress-bar">
            <div class="progress red" style="width: 18%"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Seventh row of KPI cards - Root Cause Analysis -->
    <div class="kpi-row">
      <div class="kpi-card root-cause-card">
        <h3>Incident Root Cause Categories</h3>
        <div class="kpi-chart bar-chart-container">
          <div class="horizontal-bar-chart">
            <div class="h-bar-item">
              <div class="h-bar-label">Human Error</div>
              <div class="h-bar-track">
                <div class="h-bar-progress" style="width: 35%"></div>
              </div>
              <div class="h-bar-value">35%</div>
            </div>
            <div class="h-bar-item">
              <div class="h-bar-label">System Failure</div>
              <div class="h-bar-track">
                <div class="h-bar-progress" style="width: 25%"></div>
              </div>
              <div class="h-bar-value">25%</div>
            </div>
            <div class="h-bar-item">
              <div class="h-bar-label">Process Deficiency</div>
              <div class="h-bar-track">
                <div class="h-bar-progress" style="width: 20%"></div>
              </div>
              <div class="h-bar-value">20%</div>
            </div>
            <div class="h-bar-item">
              <div class="h-bar-label">External Threat</div>
              <div class="h-bar-track">
                <div class="h-bar-progress" style="width: 15%"></div>
              </div>
              <div class="h-bar-value">15%</div>
            </div>
            <div class="h-bar-item">
              <div class="h-bar-label">Other</div>
              <div class="h-bar-track">
                <div class="h-bar-progress" style="width: 5%"></div>
              </div>
              <div class="h-bar-value">5%</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="kpi-card threat-types-card">
        <h3>Volume of Incident Types</h3>
        <div class="kpi-chart bar-chart-container">
          <div class="vertical-bar-chart">
            <div class="v-bar-item">
              <div class="v-bar-progress" style="height: 75%"></div>
              <div class="v-bar-label">Phishing</div>
              <div class="v-bar-value">32</div>
            </div>
            <div class="v-bar-item">
              <div class="v-bar-progress" style="height: 55%"></div>
              <div class="v-bar-label">Malware</div>
              <div class="v-bar-value">23</div>
            </div>
            <div class="v-bar-item">
              <div class="v-bar-progress" style="height: 30%"></div>
              <div class="v-bar-label">DDoS</div>
              <div class="v-bar-value">13</div>
            </div>
            <div class="v-bar-item">
              <div class="v-bar-progress" style="height: 20%"></div>
              <div class="v-bar-label">Insider</div>
              <div class="v-bar-value">8</div>
            </div>
            <div class="v-bar-item">
              <div class="v-bar-progress" style="height: 15%"></div>
              <div class="v-bar-label">Other</div>
              <div class="v-bar-value">6</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- After the Seventh row of KPI cards, add new Eighth row -->
    <div class="kpi-row">
      <div class="kpi-card incident-volume-card">
        <h3>Incident Volume</h3>
        <div class="kpi-value">157</div>
        <div class="kpi-chart volume-chart">
          <div class="area-chart">
            <svg viewBox="0 0 300 60" preserveAspectRatio="none">
              <path d="M0,60 L0,40 C10,35 20,45 30,42 C40,39 50,28 60,25 C70,22 80,30 90,35 C100,40 110,45 120,30 C130,15 140,10 150,15 C160,20 170,35 180,30 C190,25 200,15 210,10 C220,5 230,15 240,25 C250,35 260,30 270,20 C280,10 290,15 300,20 L300,60 Z" 
                fill="rgba(52, 152, 219, 0.2)" stroke="#3498db" stroke-width="1"></path>
              <path d="M0,40 C10,35 20,45 30,42 C40,39 50,28 60,25 C70,22 80,30 90,35 C100,40 110,45 120,30 C130,15 140,10 150,15 C160,20 170,35 180,30 C190,25 200,15 210,10 C220,5 230,15 240,25 C250,35 260,30 270,20 C280,10 290,15 300,20" 
                fill="none" stroke="#3498db" stroke-width="2"></path>
            </svg>
          </div>
        </div>
        <div class="chart-labels">
          <span>Mon</span>
          <span>Wed</span>
          <span>Fri</span>
          <span>Sun</span>
        </div>
      </div>
      
      <div class="kpi-card escalation-rate-card">
        <h3>Incident Escalation Rate</h3>
        <div class="kpi-value">38<span class="unit">%</span></div>
        <div class="kpi-chart stacked-bar-container">
          <div class="stacked-bar">
            <div class="stacked-segment audit" style="width: 38%">Audit</div>
            <div class="stacked-segment manual" style="width: 62%">Manual</div>
          </div>
        </div>
        <div class="chart-values">
          <div class="chart-legend">
            <div class="legend-item"><span class="legend-color audit"></span>Audit (38%)</div>
            <div class="legend-item"><span class="legend-color manual"></span>Manual (62%)</div>
          </div>
        </div>
      </div>
      
      <div class="kpi-card repeat-rate-card">
        <h3>Repeat Incident Rate</h3>
        <div class="kpi-value">21<span class="unit">%</span></div>
        <div class="kpi-chart donut-chart-container">
          <div class="donut-chart repeat-donut">
            <div class="donut-segment new" style="--start-angle: 0deg; --end-angle: 284.4deg;"></div>
            <div class="donut-segment repeat" style="--start-angle: 284.4deg; --end-angle: 360deg;"></div>
            <div class="donut-hole">
              <div class="donut-hole-text">21%</div>
        </div>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item"><span class="legend-color new"></span>New (79%)</div>
          <div class="legend-item"><span class="legend-color repeat"></span>Repeat (21%)</div>
        </div>
      </div>
    </div>

    <div v-if="showPopup" class="incident-popup-overlay">
      <div class="incident-popup-modal">
        <button class="incident-popup-close" @click="closePopup">&times;</button>
        <div class="incident-popup-message">{{ popupMessage }}</div>
      </div>
    </div>

    <div class="incident-count-card">
      <h3>Total Incidents</h3>
      <h2>{{ incidentCounts.total }}</h2>
    </div>
    
    <div class="incident-count-card">
      <h3>Pending Incidents</h3>
      <h2>{{ incidentCounts.pending }}</h2>
    </div>
    
    <div class="incident-count-card">
      <h3>Accepted Incidents</h3>
      <h2>{{ incidentCounts.accepted }}</h2>
    </div>
    
    <div class="incident-count-card">
      <h3>Rejected Incidents</h3>
      <h2>{{ incidentCounts.rejected }}</h2>
    </div>
    
    <div class="incident-count-card">
      <h3>Resolved Incidents</h3>
      <h2>{{ incidentCounts.resolved }}</h2>
    </div>
  </div>
</template>

<script>
import '../Incident/IncidentDashboard.css';
import axios from 'axios';

export default {
  name: 'IncidentDashboard',
  data() {
    return {
      showPopup: false,
      popupMessage: '',
      loading: true,
      kpiData: {
        mttd: { value: 0, unit: 'hours', trend: [], change_percentage: 0 },
        mttr: { value: 6, unit: 'hours', trend: [] },
        mttc: { value: 12, unit: 'hours', trend: [] },
        mttrv: { value: 35, unit: 'hours', trend: [] },
        firstResponseTime: { value: 3.5, unit: 'hours', trend: [] },
        escalationTime: { value: 5.2, unit: 'hours', trend: [] },
        incidentsDetected: { value: 48, byDay: [12, 15, 13, 22, 32, 18, 13] },
        reopenedIncidents: { value: 7, percentage: 15 },
        closureRate: { value: 76, unit: '%' },
        falsePositiveRate: { value: 12, unit: '%' },
        detectionAccuracy: { value: 88, unit: '%' },
        slaComplianceRate: { value: 82, unit: '%' },
        incidentsBySeverity: {
          critical: 25,
          high: 35, 
          medium: 30,
          low: 10
        },
        incidentsByOrigin: {
          user: 65,
          system: 35
        },
        recurrenceRate: { value: 6.5, unit: '%', trend: [] },
        costPerIncident: { 
          average: 184000, 
          bySeverity: {
            critical: 325000,
            high: 210000,
            medium: 125000,
            low: 75000
          }
        },
        responseTypes: {
          automated: 40,
          manual: 60
        },
        slaBreachRate: { value: 18, unit: '%' },
        rootCauseCategories: {
          'Human Error': 35,
          'System Failure': 25,
          'Process Deficiency': 20,
          'External Threat': 15,
          'Other': 5
        },
        incidentTypes: {
          'Phishing': 32,
          'Malware': 23,
          'DDoS': 13,
          'Insider': 8,
          'Other': 6
        },
        incidentVolume: {
          value: 157,
          byDay: [40, 42, 25, 35, 30, 15, 10, 20, 30, 25, 20, 15, 25]
        },
        escalationRate: {
          value: 38,
          audit: 38,
          manual: 62
        },
        repeatRate: {
          value: 21,
          new: 79,
          repeat: 21
        }
      },
      incidentCounts: {
        total: 0,
        pending: 0,
        accepted: 0,
        rejected: 0,
        resolved: 0
      }
    }
  },
  methods: {
    openPopup(message) {
      this.popupMessage = message;
      this.showPopup = true;
    },
    closePopup() {
      this.showPopup = false;
      this.popupMessage = '';
    },
    async fetchKPIData() {
      try {
        this.loading = true;
        
        // First, try to get all metrics at once
        try {
          const response = await axios.get('/api/incident/metrics/', {
            params: {
              timeRange: 'all'
            }
          });
          
          if (response.data && response.data.mttd) {
            this.kpiData.mttd = {
              value: response.data.mttd.value,
              unit: response.data.mttd.unit,
              trend: response.data.mttd.trend,
              change_percentage: response.data.mttd.change_percentage
            };
          }
          
          // Process other metrics if available
          
          this.loading = false;
          return;
        } catch (error) {
          console.warn('Metrics endpoint not available, falling back to individual endpoints');
        }
        
        // If all-in-one endpoint fails, fall back to individual requests
        // Rest of the existing code with individual endpoints...
      } catch (error) {
        console.error('Error fetching KPI data:', error);
        this.openPopup('Error loading dashboard data. Please try again later.');
        this.loading = false;
      }
    },
    // Helper method to generate SVG path for trend line
    generateTrendPath(dataPoints) {
      if (!dataPoints || dataPoints.length === 0) return '';
      
      // Normalize data points to fit in the SVG viewport
      const maxValue = Math.max(...dataPoints) || 1;
      const minValue = Math.min(...dataPoints) || 0;
      const range = maxValue - minValue || 1;
      
      // Calculate x-step based on number of points
      const xStep = 300 / (dataPoints.length - 1 || 1);
      
      // Start the path
      let path = `M0,${60 - ((dataPoints[0] - minValue) / range * 40 + 10)}`;
      
      // Add points to the path
      for (let i = 1; i < dataPoints.length; i++) {
        const x = i * xStep;
        const y = 60 - ((dataPoints[i] - minValue) / range * 40 + 10);
        path += ` L${x},${y}`;
      }
      
      return path;
    },
    
    // Helper method to get points for trend circles
    getTrendPoints(dataPoints) {
      if (!dataPoints || dataPoints.length === 0) return [];
      
      // Normalize data points to fit in the SVG viewport
      const maxValue = Math.max(...dataPoints) || 1;
      const minValue = Math.min(...dataPoints) || 0;
      const range = maxValue - minValue || 1;
      
      // Calculate x-step based on number of points
      const xStep = 300 / (dataPoints.length - 1 || 1);
      
      // Generate points
      return dataPoints.map((value, index) => {
        return {
          x: index * xStep,
          y: 60 - ((value - minValue) / range * 40 + 10)
        };
      });
    },
    fetchIncidentCounts() {
      console.log("Fetching incident counts");
      fetch('/api/incidents/counts/')
        .then(response => response.json())
        .then(data => {
          console.log("Received incident counts:", data);
          this.incidentCounts = data;
        })
        .catch(error => {
          console.error('Error fetching incident counts:', error);
        });
    }
  },
  mounted() {
    this.fetchKPIData();
    this.fetchIncidentCounts();
  }
}
</script>

<style scoped>
/* Additional styles needed for new charts */
.pie-chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 120px;
}

.pie-chart {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: #e0e0e0;
  overflow: hidden;
}

.pie-segment {
  position: absolute;
  width: 100%;
  height: 100%;
  transform-origin: 50% 50%;
  clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%, 50% 0%);
}

.pie-segment.critical {
  background-color: #ef4444;
  transform: rotate(0deg);
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + var(--segment-size) * 100%) 0%, calc(50% + var(--segment-size) * 100%) 100%, 50% 100%);
}

.pie-segment.high {
  background-color: #f97316;
  transform: rotate(calc(var(--segment-size-critical, 25%) * 3.6deg));
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + var(--segment-size) * 100%) 0%, calc(50% + var(--segment-size) * 100%) 100%, 50% 100%);
}

.pie-segment.medium {
  background-color: #facc15;
  transform: rotate(calc((var(--segment-size-critical, 25%) + var(--segment-size-high, 35%)) * 3.6deg));
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + var(--segment-size) * 100%) 0%, calc(50% + var(--segment-size) * 100%) 100%, 50% 100%);
}

.pie-segment.low {
  background-color: #84cc16;
  transform: rotate(calc((var(--segment-size-critical, 25%) + var(--segment-size-high, 35%) + var(--segment-size-medium, 30%)) * 3.6deg));
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + var(--segment-size) * 100%) 0%, calc(50% + var(--segment-size) * 100%) 100%, 50% 100%);
}

.pie-segment.user {
  background-color: #3498db;
}

.pie-segment.system {
  background-color: #1abc9c;
  transform: rotate(calc(var(--segment-size-user, 65%) * 3.6deg));
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + var(--segment-size) * 100%) 0%, calc(50% + var(--segment-size) * 100%) 100%, 50% 100%);
}

.pie-segment.automated {
  background-color: #9b59b6;
}

.pie-segment.manual {
  background-color: #e74c3c;
  transform: rotate(calc(var(--segment-size-automated, 40%) * 3.6deg));
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + var(--segment-size) * 100%) 0%, calc(50% + var(--segment-size) * 100%) 100%, 50% 100%);
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
  font-size: 0.7rem;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-right: 8px;
}

.legend-color {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 4px;
  border-radius: 2px;
}

.legend-color.critical { background-color: #ef4444; }
.legend-color.high { background-color: #f97316; }
.legend-color.medium { background-color: #facc15; }
.legend-color.low { background-color: #84cc16; }
.legend-color.user { background-color: #3498db; }
.legend-color.system { background-color: #1abc9c; }
.legend-color.automated { background-color: #9b59b6; }
.legend-color.manual { background-color: #e74c3c; }

.donut-chart {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: #e0e0e0;
  margin: 0 auto;
}

.donut-hole {
  position: absolute;
  width: 60px;
  height: 60px;
  background: white;
  border-radius: 50%;
  top: 20px;
  left: 20px;
}

.donut-segment {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  clip: rect(0px, 100px, 100px, 50px);
  background: #ef4444;
}

.root-cause-card, .threat-types-card {
  flex: 2;
}

.bar-chart-container {
  height: 200px;
  margin-top: 10px;
}

.horizontal-bar-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.h-bar-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.h-bar-label {
  width: 110px;
  font-size: 0.8rem;
  text-align: right;
}

.h-bar-track {
  flex: 1;
  height: 12px;
  background: #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
}

.h-bar-progress {
  height: 100%;
  background: #3498db;
  border-radius: 6px;
}

.h-bar-value {
  width: 40px;
  font-size: 0.8rem;
  text-align: left;
}

.vertical-bar-chart {
  display: flex;
  height: 100%;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 30px;
}

.v-bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 18%;
  position: relative;
}

.v-bar-progress {
  width: 100%;
  background: #3498db;
  border-radius: 6px 6px 0 0;
}

.v-bar-label {
  position: absolute;
  bottom: -25px;
  font-size: 0.8rem;
}

.v-bar-value {
  margin-bottom: 5px;
  font-size: 0.8rem;
  font-weight: bold;
}

.bar.critical { background-color: #ef4444; }
.bar.high { background-color: #f97316; }
.bar.medium { background-color: #facc15; }
.bar.low { background-color: #84cc16; }

.bar-chart.horizontal {
  flex-direction: column;
  height: auto;
}

.bar-chart.horizontal .bar {
  display: flex;
  align-items: center;
  padding-left: 8px;
  height: 20px !important;
  margin: 5px 0;
  color: white;
  font-size: 0.8rem;
  border-radius: 4px;
}

.progress.red {
  background-color: #ef4444;
}

/* Incident Volume Area Chart */
.volume-chart {
  height: 80px;
}

.area-chart {
  width: 100%;
  height: 100%;
}

.area-chart svg {
  width: 100%;
  height: 100%;
}

/* Escalation Rate Stacked Bar */
.stacked-bar-container {
  height: 40px;
  margin: 15px 0;
}

.stacked-bar {
  display: flex;
  width: 100%;
  height: 25px;
  background: #ecf0f1;
  border-radius: 5px;
  overflow: hidden;
}

.stacked-segment {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  white-space: nowrap;
}

.stacked-segment.audit {
  background-color: #3498db;
}

.stacked-segment.manual {
  background-color: #9b59b6;
}

.legend-color.audit {
  background-color: #3498db;
}

.legend-color.manual {
  background-color: #9b59b6;
}

/* Repeat Incident Rate Donut */
.donut-chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
}

.repeat-donut {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #ecf0f1;
}

.donut-segment.new {
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: #2ecc71;
  border-radius: 50%;
  clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%, 50% 0%);
  transform-origin: center;
  transform: rotate(var(--start-angle));
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + 100% * cos(var(--end-angle))) calc(50% - 100% * sin(var(--end-angle))), calc(50% + 100% * cos(var(--start-angle))) calc(50% - 100% * sin(var(--start-angle))));
}

.donut-segment.repeat {
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: #e74c3c;
  border-radius: 50%;
  transform-origin: center;
  transform: rotate(var(--start-angle));
  clip-path: polygon(50% 50%, 50% 0%, calc(50% + 100% * cos(var(--end-angle))) calc(50% - 100% * sin(var(--end-angle))), calc(50% + 100% * cos(var(--start-angle))) calc(50% - 100% * sin(var(--start-angle))));
}

.donut-hole {
  position: absolute;
  width: 50px;
  height: 50px;
  background: white;
  border-radius: 50%;
  top: 15px;
  left: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.donut-hole-text {
  font-size: 1rem;
  font-weight: bold;
  color: #2c3e50;
}

.legend-color.new {
  background-color: #2ecc71;
}

.legend-color.repeat {
  background-color: #e74c3c;
}

/* Line Chart Styles */
.line-chart {
  width: 100%;
  height: 40px;
  margin-bottom: 5px;
}

.line-chart svg {
  width: 100%;
  height: 100%;
}

.chart-months {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #7f8c8d;
  margin-top: 5px;
  padding: 0 5px;
}

/* Style for value change indicators */
.value-change {
  display: inline-flex;
  align-items: center;
  font-size: 0.75rem;
  margin-left: 10px;
  vertical-align: middle;
}

.value-change.positive {
  color: #4ade80;
}

.value-change.negative {
  color: #f87171;
}

.value-change i {
  margin-right: 2px;
}

/* Update existing kpi-chart for line charts */
.kpi-chart {
  height: auto;
  position: relative;
  margin-bottom: 10px;
}
</style> 