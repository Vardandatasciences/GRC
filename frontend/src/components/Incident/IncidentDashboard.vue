<template>
  <div class="incident-dashboard-wrapper">
    <div class="incident-status-summary">
      <div class="status-card" v-for="(item, idx) in statusSummary" :key="idx">
        <div class="status-count">{{ item.count }}</div>
        <div class="status-label">{{ item.label }}</div>
      </div>
    </div>

    
    <div class="incident-filters">
      <select class="incident-filter"><option>Incident Id</option></select>
      <select class="incident-filter"><option>From</option></select>
      <input class="incident-filter" type="date" />
      <select class="incident-filter"><option>Priority Level</option></select>
      <select class="incident-filter"><option>Sort by status</option></select>
      <div class="incident-view-toggle">
        <button :class="{ active: view === 'grid' }" @click="view = 'grid'">Grid</button>
        <button :class="{ active: view === 'list' }" @click="view = 'list'">List</button>
      </div>
    </div>
    <div class="incident-cards-grid">
      <div class="incident-card" v-for="(incident, idx) in incidents" :key="idx">
        <div class="incident-card-header" :class="incident.headerClass">{{ incident.header }}</div>
        <div class="incident-card-title">{{ incident.title }}</div>
        <div class="incident-card-desc">{{ incident.desc }}</div>
        <div v-if="incident.statusTag" class="incident-card-status-tag" :style="{background: incident.statusTagColor, color: '#222'}">{{ incident.statusTag }}</div>
        <div v-if="!incident.statusTag" class="incident-card-actions">
          <button class="incident-card-btn solve" @click="openPopup('You will be direct to the Risk module')">{{ incident.solveBtn }}</button>
          <button class="incident-card-btn no" @click="openPopup('Rejected')">No</button>
        </div>
        <div class="incident-card-date-row">
          <i class="fas fa-calendar-alt incident-card-date-icon"></i>
          <span class="incident-card-date">{{ incident.date }}</span>
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
export default {
  name: 'IncidentDashboard',
  data() {
    return {
      view: 'grid',
      statusSummary: [
        { count: 1, label: 'Accept' },
        { count: 2, label: 'Reject' },
        { count: 3, label: 'From SIEM' },
        { count: 1, label: 'Frrom Auditor' },
        { count: 1, label: 'Manual Incident' }
      ],
      incidents: [
        {
          header: 'ISO 27001',
          headerClass: 'iso-header',
          title: 'Work Flow diagram',
          desc: 'Make the flow in the diagramitic format',
          solveBtn: 'Solve',
          date: '24/02/2025'
        },
        {
          header: 'From SIEM',
          headerClass: 'siem-header',
          title: 'Policy mapping issues',
          desc: 'Should map the issue with the approval',
          solveBtn: 'Solve',
          date: '24/02/2025'
        },
        {
          header: 'From Auditor',
          headerClass: 'auditor-header',
          title: 'Mapping compliance table',
          desc: 'Should map the sp1 to sp2',
          solveBtn: 'Solve',
          date: '24/02/2025'
        },
        {
          header: 'ISO 27001',
          headerClass: 'iso-header',
          title: 'Loan policy approval issue',
          desc: 'Map the approval to the loukya',
          solveBtn: '',
          statusTag: 'Forwarded to Risk',
          statusTagColor: '#b6ffb6',
          date: '24/02/2025'
        }
      ],
      showPopup: false,
      popupMessage: ''
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
.incident-dashboard-wrapper {
  padding: 24px 16px 24px 200px;
  background: #f5f5f5;
  min-height: 100vh;
  font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
}
.incident-status-summary {
  display: flex;
  gap: 18px;
  margin-bottom: 16px;
}
.status-card {
  background: #ededed;
  border-radius: 18px;
  padding: 10px 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 90px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.status-count {
  font-size: 1.2rem;
  font-weight: bold;
  color: #3a3a3a;
}
.status-label {
  font-size: 0.95rem;
  color: #444;
  margin-top: 4px;
}
.incident-filters {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}
.incident-filter {
  font-size: 0.95rem;
  padding: 6px 10px;
  border-radius: 6px;
  border: 2px solid #222;
  background: #fff;
  min-width: 90px;
}
.incident-view-toggle {
  background: #ededed;
  border-radius: 18px;
  padding: 2px 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 10px;
}
.incident-view-toggle button {
  background: #d6f5d6;
  border: none;
  border-radius: 6px;
  padding: 4px 12px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #222;
  cursor: pointer;
  transition: background 0.2s;
}
.incident-view-toggle button.active {
  background: #4caf50;
  color: #fff;
}
.incident-cards-grid {
  display: flex;
  gap: 14px;
  margin-top: 10px;
  flex-wrap: wrap;
}
.incident-card {
  background: #ededed;
  border-radius: 12px;
  padding: 10px 12px 10px 12px;
  min-width: 180px;
  max-width: 210px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  position: relative;
}
.incident-card-header {
  font-size: 0.95rem;
  font-weight: 600;
  color: #fff;
  background: #ff5c5c;
  border-radius: 12px 12px 12px 12px;
  padding: 2px 10px;
  margin-bottom: 6px;
  align-self: flex-start;
}
.incident-card-header.siem-header {
  background: #ff5c5c;
}
.incident-card-header.auditor-header {
  background: #ff5c5c;
}
.incident-card-title {
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 1px;
  color: #222;
}
.incident-card-desc {
  font-size: 0.92rem;
  color: #222;
  margin-bottom: 6px;
}
.incident-card-status-tag {
  background: #b6ffb6;
  color: #222;
  font-weight: 600;
  border-radius: 6px;
  padding: 2px 10px;
  margin-bottom: 6px;
  font-size: 0.95rem;
}
.incident-card-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
}
.incident-card-btn {
  background: #fff;
  border: none;
  border-radius: 10px;
  padding: 4px 12px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #222;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: background 0.2s;
}
.incident-card-btn.solve {
  background: #fff;
}
.incident-card-btn.no {
  background: #fff;
}
.incident-card-date-row {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 2px;
}
.incident-card-date-icon {
  color: #222;
  font-size: 0.95rem;
}
.incident-card-date {
  color: #ff5c5c;
  font-size: 0.95rem;
  font-weight: 600;
}
.incident-popup-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 4000;
}
.incident-popup-modal {
  background: #fff;
  border: 2px solid #222;
  border-radius: 12px;
  padding: 32px 38px 24px 38px;
  min-width: 320px;
  max-width: 90vw;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.incident-popup-close {
  position: absolute;
  top: 10px;
  right: 18px;
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #222;
}
.incident-popup-message {
  font-size: 1.15rem;
  color: #222;
  font-weight: 600;
  text-align: center;
  margin-top: 10px;
  margin-bottom: 10px;
}
</style> 