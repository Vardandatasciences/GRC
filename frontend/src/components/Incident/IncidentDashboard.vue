<template>
  <div class="incident-dashboard-wrapper">
    <!-- First row of KPI cards -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Number of Active Incidents</h3>
        <div class="kpi-value">48</div>
        <div class="kpi-chart">
          <div class="trend-line"></div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Incident Exposure</h3>
        <div class="kpi-value">872</div>
        <div class="kpi-chart">
          <div class="trend-line"></div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Incident Recurrence Rate</h3>
        <div class="kpi-value">6.5<span class="unit">%</span></div>
        <div class="kpi-chart">
          <div class="trend-line"></div>
        </div>
        <div class="source">SIA</div>
      </div>
    </div>

    <!-- Second row of KPI cards -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Incident Reduction Trend</h3>
        <div class="kpi-chart">
          <div class="bar-chart">
            <div class="bar" style="height: 70%"></div>
            <div class="bar" style="height: 60%"></div>
            <div class="bar" style="height: 75%"></div>
            <div class="bar" style="height: 80%"></div>
            <div class="bar" style="height: 70%"></div>
            <div class="bar" style="height: 60%"></div>
          </div>
        </div>
        <div class="chart-labels">
          <span>Start</span>
          <span>New</span>
          <span>End</span>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Incident Mitigation Completion Rate</h3>
        <div class="kpi-value">76<span class="unit">%</span></div>
      </div>
      
      <div class="kpi-card">
        <h3>Average Time to Remediate Critical Incidents</h3>
        <div class="kpi-value">35<span class="unit">days</span></div>
        <div class="kpi-chart">
          <div class="trend-line"></div>
        </div>
      </div>
    </div>

    <!-- Third row of KPI cards -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Mean Time to Respond (MTTR)</h3>
        <div class="kpi-value">6<span class="unit">hours</span></div>
        <div class="kpi-chart">
          <div class="trend-line"></div>
        </div>
        <div class="chart-labels">
          <span>Start</span>
          <span>End</span>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Average Time to Improvement Initiatives</h3>
        <div class="kpi-value">41<span class="unit">%</span></div>
        <div class="kpi-chart">
          <div class="bar-chart mini">
            <div class="bar" style="height: 20%"></div>
            <div class="bar" style="height: 25%"></div>
            <div class="bar" style="height: 30%"></div>
            <div class="bar" style="height: 35%"></div>
            <div class="bar" style="height: 40%"></div>
            <div class="bar" style="height: 45%"></div>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Incident Identification Rate</h3>
        <div class="kpi-value">6.5</div>
        <div class="kpi-chart">
          <div class="gauge-chart"></div>
        </div>
      </div>
    </div>

    <!-- Fourth row of KPI cards -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Mean Time to Incident Response</h3>
        <div class="kpi-value">6<span class="unit">hours</span></div>
        <div class="kpi-chart">
          <div class="trend-line"></div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Cost of Mitigation</h3>
        <div class="kpi-value">₹184K</div>
      </div>
      
      <div class="kpi-card">
        <h3>Completion of Improvement Initiatives</h3>
        <div class="kpi-chart">
          <div class="progress-bar">
            <div class="progress" style="width: 75%"></div>
          </div>
        </div>
        <div class="chart-values">
          <span>11</span>
          <div class="value-ticks">
            <span>0</span>
            <span>1</span>
            <span>2</span>
            <span>3</span>
            <span>5</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Fifth row of KPI cards -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Due Mitigation Actions</h3>
        <div class="kpi-value">22<span class="unit">%</span></div>
        <div class="kpi-chart">
          <div class="progress-bar">
            <div class="progress" style="width: 22%"></div>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Percentage of Due Mitigation Actions</h3>
        <div class="kpi-value">22<span class="unit">%</span></div>
        <div class="kpi-chart">
          <div class="trend-line"></div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Incident Identification Rate</h3>
        <div class="kpi-value">88<span class="unit">%</span></div>
        <div class="kpi-chart">
          <div class="bar-chart mini vertical">
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
          <span>J</span>
          <span>F</span>
          <span>M</span>
          <span>A</span>
          <span>M</span>
          <span>J</span>
          <span>J</span>
        </div>
      </div>
    </div>

    <!-- Sixth row of KPI cards -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Incident Classification Accuracy</h3>
        <div class="kpi-value">88<span class="unit">%</span></div>
        <div class="kpi-chart">
          <div class="progress-bar">
            <div class="progress" style="width: 88%"></div>
          </div>
        </div>
        <div class="kpi-chart mt-10">
          <div class="progress-bar">
            <div class="progress" style="width: 88%"></div>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Completion of Improvement Initiatives</h3>
        <div class="kpi-chart">
          <div class="bar-chart horizontal">
            <div class="bar" style="height: 60%"></div>
            <div class="bar" style="height: 90%"></div>
            <div class="bar" style="height: 70%"></div>
            <div class="bar" style="height: 80%"></div>
          </div>
        </div>
        <div class="chart-values">
          <div class="value-ticks">
            <span>3</span>
            <span>2</span>
            <span>5</span>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Frequency of Risk Assessment Review</h3>
        <div class="label">Aparant</div>
        <div class="kpi-chart">
          <div class="progress-bar horizontal">
            <div class="progress" style="width: 70%"></div>
          </div>
        </div>
        <div class="chart-values">
          <div class="value-ticks">
            <span>1</span>
            <span>0</span>
            <span>5</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Seventh row of KPI cards -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Impact on Operations and Finances</h3>
        <div class="kpi-value-circle">17<span class="unit">%</span></div>
        <div class="kpi-chart">
          <div class="progress-bar">
            <div class="progress" style="width: 17%"></div>
          </div>
        </div>
        <div class="chart-values">
          <div class="value-ticks">
            <span>3</span>
            <span>2</span>
            <span>6</span>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Incident Severity Based on Potential</h3>
        <div class="kpi-chart">
          <div class="progress-bar">
            <div class="progress orange" style="width: 70%"></div>
          </div>
        </div>
        <div class="chart-values">
          <div class="value-ticks">
            <span>9</span>
            <span>3</span>
            <span>4</span>
            <span>10</span>
          </div>
        </div>
        <div class="chart-labels">
          <span>AV</span>
          <span>I</span>
          <span>I</span>
          <span>I</span>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Incident Impact on Operations & Financial</h3>
        <div class="kpi-chart">
          <div class="progress-bars">
            <div class="progress-bar">
              <div class="progress blue" style="width: 40%"></div>
            </div>
            <div class="progress-bar">
              <div class="progress orange" style="width: 60%"></div>
            </div>
            <div class="progress-bar">
              <div class="progress green" style="width: 30%"></div>
            </div>
          </div>
        </div>
        <div class="chart-values">
          <div class="value-ticks">
            <span>0</span>
            <span>10</span>
          </div>
        </div>
        <div class="chart-footer">
          <span>1d lose</span>
          <span>5.Acceptable</span>
        </div>
      </div>
    </div>

    <!-- Eighth row of KPI cards -->
    <div class="kpi-row">
      <div class="kpi-card">
        <h3>Incident Tolerance Thresholds</h3>
        <div class="kpi-chart">
          <div class="progress-bar">
            <div class="progress blue" style="width: 50%"></div>
          </div>
        </div>
        <div class="chart-values">
          <div class="value-ticks">
            <span>5</span>
          </div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Incident Exposure Score</h3>
        <div class="kpi-chart">
          <div class="scatter-plot">
            <div class="dot" style="top: 30%; left: 20%"></div>
            <div class="dot" style="top: 40%; left: 70%"></div>
            <div class="dot" style="top: 60%; left: 50%"></div>
            <div class="dot" style="top: 70%; left: 80%"></div>
            <div class="dot" style="top: 50%; left: 30%"></div>
            <div class="dot orange" style="top: 30%; left: 40%"></div>
            <div class="dot orange" style="top: 40%; left: 60%"></div>
            <div class="dot orange" style="top: 20%; left: 90%"></div>
            <div class="dot orange" style="top: 60%; left: 20%"></div>
            <div class="dot orange" style="top: 50%; left: 50%"></div>
          </div>
        </div>
        <div class="chart-axes">
          <div class="y-axis">Influence</div>
          <div class="x-axis">
            <span>0</span>
            <span>5</span>
            <span>4</span>
            <span>9</span>
            <span>8</span>
            <span>10</span>
          </div>
          <div class="x-label">Export</div>
        </div>
      </div>
      
      <div class="kpi-card">
        <h3>Incident Resilience to Absorb Shocks</h3>
        <div class="kpi-chart">
          <div class="slider-chart">
            <div class="slider-track"></div>
            <div class="slider-thumb" style="left: 30%"></div>
          </div>
        </div>
        <div class="slider-labels">
          <span>5 hrs</span>
          <span>64 hrs</span>
        </div>
        <h3 class="mt-10">Incident Reliance to Absorb Shocks</h3>
        <div class="kpi-chart">
          <div class="slider-chart">
            <div class="slider-track"></div>
            <div class="slider-thumb" style="left: 40%"></div>
          </div>
        </div>
        <div class="slider-labels">
          <span>5 hrs</span>
          <span>64 hrs</span>
        </div>
      </div>
    </div>

    <div v-if="showPopup" class="incident-popup-overlay">
      <div class="incident-popup-modal">
        <button class="incident-popup-close" @click="closePopup">&times;</button>
        <div class="incident-popup-message">{{ popupMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import '../Incident/IncidentDashboard.css';

export default {
  name: 'IncidentDashboard',
  data() {
    return {
      showPopup: false,
      popupMessage: '',
      kpiData: {
        activeIncidents: 48,
        incidentExposure: 872,
        recurrenceRate: 6.5,
        mitigationRate: 76,
        remediationTime: 35,
        responseTime: 6,
        improvementTime: 41,
        identificationRate: 6.5,
        mitigationCost: '₹184K',
        dueMitigationActions: 22,
        classificationAccuracy: 88
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
    }
  }
}
</script>

<style scoped>
/* Base styles are moved to IncidentDashboard.css */
</style> 