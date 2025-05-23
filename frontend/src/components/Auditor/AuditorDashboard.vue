<template>
  <div class="auditor-dashboard-container">
    <div class="auditor-status-row">
      <div v-for="(s, i) in statusSummary" :key="i" class="auditor-status-box" :style="{ borderColor: s.color }">
        <span class="auditor-status-count" :style="{ color: s.color }">{{ s.count }}</span>
        <span class="auditor-status-label">{{ s.label }}</span>
      </div>
    </div>
    <div class="auditor-filters-row">
      <input class="auditor-search" placeholder="Search Policy" />
      <select class="auditor-filter"><option>All Framework</option></select>
      <select class="auditor-filter"><option>All Status</option></select>
      <select class="auditor-filter"><option>All created by</option></select>
      <select class="auditor-filter"><option>Sort by status</option></select>
      <div class="auditor-view-toggle">
        <button :class="{ active: view === 'grid' }" @click="view = 'grid'">Grid</button>
        <button :class="{ active: view === 'list' }" @click="view = 'list'">List</button>
      </div>
    </div>
    <div :class="view === 'grid' ? 'auditor-cards-grid' : 'auditor-cards-list'">
      <div v-for="(audit, idx) in audits" :key="idx" class="auditor-card">
        <div class="auditor-card-framework" :style="{ background: audit.framework.startsWith('ISO') ? '#ff5c5c' : '#ff5c5c' }">
          {{ audit.framework }}
        </div>
        <div class="auditor-card-policy">{{ audit.policy }}</div>
        <div class="auditor-card-user">{{ audit.user }}</div>
        <div class="auditor-card-status-row">
          <button v-if="audit.statusType === 'start'" class="auditor-card-status start" @click="openPopup(idx)">Start</button>
          <button v-else-if="auditStatuses[idx] === 'Completed'" class="auditor-card-status complete">Completed</button>
          <select
            v-else
            class="auditor-card-status review"
            :value="auditStatuses[idx]"
            @change="handleStatusChange(idx, $event.target.value)"
          >
            <option value="Work In Progress">Work In Progress</option>
            <option value="Under review">Under review</option>
          </select>
        </div>
        <div class="auditor-card-donut-row">
          <div class="auditor-card-donut">
            <CircleProgress
              :percent="audit.progress"
              :size="80"
              :border-width="10"
              :border-bg-width="10"
              fill-color="#4f7cff"
              empty-color="#e0e0e0"
            >
              <template #default="{ percent }">
                <span class="progress-text">{{ percent }}%</span>
              </template>
            </CircleProgress>
          </div>
        </div>
        <div class="auditor-card-date-row">
          <i class="fas fa-calendar-alt auditor-card-date-icon"></i>
          <span class="auditor-card-date">{{ audit.date }}</span>
        </div>
      </div>
    </div>

    <!-- Popup Modal -->
    <div v-if="showPopup" class="audit-popup-overlay">
      <div class="audit-popup-modal">
        <button class="popup-close" @click="closePopup">&times;</button>
        <div class="popup-header">
          <select v-model="popupData.framework" class="popup-select">
            <option disabled value="">Frame work</option>
            <option v-for="fw in frameworks" :key="fw">{{ fw }}</option>
          </select>
          <select v-model="popupData.policy" class="popup-select">
            <option disabled value="">Policy</option>
            <option v-for="p in policies" :key="p">{{ p }}</option>
          </select>
        </div>
        <div v-for="(sub, sIdx) in popupData.subpolicies" :key="sIdx" class="popup-subpolicy-block">
          <div class="popup-subpolicy-header">
            <span>Subpolicy</span>
            <input type="checkbox" v-model="sub.checked" class="popup-subpolicy-checkbox" />
          </div>
          <div class="popup-compliance-list">
            <div v-for="(compliance, cIdx) in sub.compliances" :key="cIdx" class="popup-compliance-row">
              <span class="popup-compliance-label">Compliance {{ cIdx + 1 }}</span>
              <input type="checkbox" v-model="compliance.checked" />
              <input class="popup-comment-input" v-model="compliance.comment" placeholder="Comment" />
              <input type="checkbox" v-model="compliance.commentChecked" />
            </div>
            <button class="popup-add-btn" @click="addCompliance(sIdx)">Add</button>
          </div>
        </div>
        <button class="popup-submit-btn" @click="submitPopup">Submit</button>
      </div>
    </div>
  </div>
</template>

<script>
import CircleProgress from 'vue3-circle-progress'
import 'vue3-circle-progress/dist/circle-progress.css'
import './AuditorDashboard.css'

export default {
  name: 'AuditorDashboard',
  components: {
    CircleProgress
  },
  data() {
    return {
      view: 'grid',
      auditStatuses: [],
      statusSummary: [
        { label: 'Yet to start', count: 1, color: '#1aaf5d' },
        { label: 'Work In Progress', count: 2, color: '#2d7be5' },
        { label: 'Under review', count: 3, color: '#e5a12d' },
        { label: 'Completed', count: 1, color: '#1aaf5d' }
      ],
      audits: [
        {
          framework: 'ISO 27001',
          policy: 'Employee Code of Conduct',
          user: 'Susheel CTO',
          status: 'Yet to start',
          statusType: 'start',
          date: '24/02/2025',
          progress: 0
        },
        {
          framework: 'NIST 8000',
          policy: 'Loan Policy recovery',
          user: 'Khairu shaik',
          status: 'Active',
          statusType: 'active',
          date: '24/02/2025',
          progress: 60
        },
        {
          framework: 'ISO 27001',
          policy: 'Data Security Policy',
          user: 'Kkhairu',
          status: 'work in progress',
          statusType: 'progress',
          date: '24/02/2025',
          progress: 40
        },
        {
          framework: 'NIST 8000',
          policy: 'Loan Policy recovery',
          user: 'Praharshitha',
          status: 'Review',
          statusType: 'review',
          date: '24/02/2025',
          progress: 80
        }
      ],
      showPopup: false,
      popupData: {
        framework: '',
        policy: '',
        subpolicies: [
          {
            name: '',
            compliances: [
              { checked: false, comment: '', commentChecked: false },
              { checked: false, comment: '', commentChecked: false },
              { checked: false, comment: '', commentChecked: false }
            ]
          },
          {
            name: '',
            compliances: [
              { checked: false, comment: '', commentChecked: false },
              { checked: false, comment: '', commentChecked: false },
              { checked: false, comment: '', commentChecked: false }
            ]
          }
        ]
      },
      frameworks: ['ISO 27001', 'NIST 8000'],
      policies: ['Employee Code of Conduct', 'Loan Policy recovery', 'Data Security Policy']
    }
  },
  created() {
    // Initialize auditStatuses with the initial statuses from audits
    this.auditStatuses = this.audits.map(a => a.status)
  },
  methods: {
    handleStatusChange(idx, newStatus) {
      this.auditStatuses[idx] = newStatus
    },
    openPopup(idx) {
      // Optionally, you can prefill popupData based on the audit card
      const audit = this.audits[idx]
      this.popupData.framework = audit.framework
      this.popupData.policy = audit.policy
      // Reset subpolicies and compliances
      this.popupData.subpolicies = [
        {
          name: '',
          compliances: [
            { checked: false, comment: '', commentChecked: false },
            { checked: false, comment: '', commentChecked: false },
            { checked: false, comment: '', commentChecked: false }
          ]
        },
        {
          name: '',
          compliances: [
            { checked: false, comment: '', commentChecked: false },
            { checked: false, comment: '', commentChecked: false },
            { checked: false, comment: '', commentChecked: false }
          ]
        }
      ]
      this.showPopup = true
    },
    closePopup() {
      this.showPopup = false
    },
    addCompliance(subIdx) {
      this.popupData.subpolicies[subIdx].compliances.push({ checked: false, comment: '', commentChecked: false })
    },
    submitPopup() {
      // You can handle the popupData here (send to backend, etc.)
      this.closePopup()
    }
  }
}
</script>

<style scoped>
@import './AuditorDashboard.css';

.progress-text {
  font-size: 1.1rem;
  color: #4f7cff;
}

.audit-popup-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.audit-popup-modal {
  background: #f5f5f5;
  border: 3px solid #222;
  border-radius: 8px;
  padding: 32px 24px 24px 24px;
  min-width: 700px;
  max-width: 90vw;
  position: relative;
}
.popup-close {
  position: absolute;
  top: 10px;
  right: 18px;
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
}
.popup-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 18px;
}
.popup-select {
  font-size: 1.3rem;
  padding: 8px 24px 8px 12px;
  border-radius: 16px;
  border: 2px solid #222;
  margin: 0 12px;
}
.popup-subpolicy-block {
  border: 2px solid #222;
  margin-bottom: 18px;
  padding: 12px 18px 18px 18px;
  background: #fff;
}
.popup-subpolicy-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}
.popup-subpolicy-checkbox {
  margin-left: 8px;
  font-size: 1.1rem;
  border-radius: 4px;
  border: 1.5px solid #222;
  padding: 2px 8px;
  width: 120px;
}
.popup-compliance-list {
  margin-left: 12px;
}
.popup-compliance-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}
.popup-compliance-label {
  font-size: 1.2rem;
  margin-right: 8px;
  min-width: 120px;
}
.popup-comment-input {
  margin: 0 8px;
  border-radius: 8px;
  border: 2px solid #222;
  padding: 4px 12px;
  font-size: 1.1rem;
  width: 140px;
}
.popup-add-btn {
  background: #5a1aff;
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 8px 32px;
  font-size: 1.1rem;
  margin-top: 8px;
  cursor: pointer;
  float: right;
}
.popup-submit-btn {
  background: #4f7cff;
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 10px 40px;
  font-size: 1.2rem;
  margin-top: 18px;
  cursor: pointer;
  display: block;
  margin-left: auto;
  margin-right: auto;
}
</style> 