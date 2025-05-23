<template>
  <div class="assign-audit-container">
    <div class="assign-audit-header">
      <h1>Assign Audit</h1>
      <button class="assign-audit-btn" @click="showForm = true">
        <i class="fas fa-plus" style="margin-right: 8px"></i> Assign Audit
      </button>
    </div>
    <div class="assign-audit-search">
      <input type="text" placeholder="Search..." />
      <i class="fas fa-search search-icon"></i>
    </div>
    <div class="assign-audit-table-wrapper">
      <table class="assign-audit-table">
        <thead>
          <tr>
            <th>Frame work</th>
            <th>Policy</th>
            <th>Subpolicy</th>
            <th>Auditor</th>
            <th>Duedate</th>
            <th>frequency</th>
            <th>Review</th>
            <th>Audit Type</th>
            <th>Status</th>
            <th>Report</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in auditData" :key="idx">
            <td :title="row.framework">{{ row.framework }}</td>
            <td :title="row.policy">{{ row.policy }}</td>
            <td :title="row.subpolicy">{{ row.subpolicy }}</td>
            <td :title="row.auditor">{{ row.auditor }}</td>
            <td :title="row.duedate">{{ row.duedate }}</td>
            <td :title="row.frequency">{{ row.frequency }}</td>
            <td :title="row.review">{{ row.review }}</td>
            <td :title="row.auditType">{{ row.auditType }}</td>
            <td :title="row.status">{{ row.status }}</td>
            <td :title="row.report">{{ row.report }}</td>
          </tr>
          <!-- Empty rows for visual match -->
          <tr v-for="i in 6" :key="'empty-' + i">
            <td v-for="j in 10" :key="j"></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="showForm" class="assign-audit-modal">
      <div class="assign-audit-modal-content">
        <h2>Assign Audit</h2>
        <form @submit.prevent="handleSubmit" class="assign-audit-form">
          <label>Framework<input name="framework" v-model="form.framework" required /></label>
          <label>Policy<input name="policy" v-model="form.policy" required /></label>
          <label>Subpolicy<input name="subpolicy" v-model="form.subpolicy" required /></label>
          <label>Auditor<input name="auditor" v-model="form.auditor" required /></label>
          <label>Duedate<input name="duedate" type="date" v-model="form.duedate" required /></label>
          <label>Frequency<input name="frequency" v-model="form.frequency" required /></label>
          <label>Audit Type<input name="auditType" v-model="form.auditType" required /></label>
          <label>Reviewer<input name="reviewer" v-model="form.reviewer" required /></label>
          <div class="assign-audit-form-actions">
            <button type="submit">Submit</button>
            <button type="button" @click="showForm = false">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import './AssignAudit.css'

export default {
  name: 'AssignAudit',
  data() {
    return {
      showForm: false,
      form: {
        framework: '',
        policy: '',
        subpolicy: '',
        auditor: '',
        duedate: '',
        frequency: '',
        auditType: '',
        reviewer: ''
      },
      auditData: [
        {
          framework: 'ISO 27001',
          policy: 'Security',
          subpolicy: 'Visit',
          auditor: 'Akhil',
          duedate: '24/12/2024',
          frequency: 'Daily',
          review: 'Susheel',
          auditType: 'Internal',
          status: 'Completed',
          report: 'Download'
        },
        {
          framework: 'NIST 8000',
          policy: 'HR',
          subpolicy: 'Leave',
          auditor: 'Mani',
          duedate: '24/12/2024',
          frequency: 'Monthly',
          review: 'Ramana',
          auditType: 'Internal',
          status: 'Work In progress',
          report: 'Pending'
        }
      ]
    }
  },
  methods: {
    handleSubmit() {
      // Here you would handle form submission (e.g., add to auditData or send to backend)
      this.showForm = false
      this.form = {
        framework: '',
        policy: '',
        subpolicy: '',
        auditor: '',
        duedate: '',
        frequency: '',
        auditType: '',
        reviewer: ''
      }
    }
  }
}
</script>
<style scoped>
/* Import the existing CSS file */
@import './AssignAudit.css';
</style>  