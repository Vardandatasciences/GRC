<template>
  <div class="reviewer-container">
    <h1 class="reviewer-title">Reviewer Task</h1>
    <div class="reviewer-search-row">
      <input class="reviewer-search" placeholder="" />
      <i class="fas fa-search reviewer-search-icon"></i>
    </div>
    <div class="reviewer-table-wrapper">
      <table class="reviewer-table">
        <thead>
          <tr>
            <th>Frame work</th>
            <th>Policy</th>
            <th>Subpolicy</th>
            <th>Reviewer</th>
            <th>Duedate</th>
            <th>Audit Type</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in reviewerData" :key="idx">
            <td>{{ row.framework }}</td>
            <td>{{ row.policy }}</td>
            <td>{{ row.subpolicy }}</td>
            <td>{{ row.reviewer }}</td>
            <td>{{ row.duedate }}</td>
            <td>{{ row.auditType }}</td>
            <td><a href="#" class="reviewer-status-link" @click.prevent="openFormModal">{{ row.status }}</a></td>
          </tr>
          <!-- Empty rows for visual match -->
          <tr v-for="i in 5" :key="'empty-' + i">
            <td v-for="j in 7" :key="j"></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="showFormModal" class="reviewer-modal-overlay">
      <div class="reviewer-modal" style="min-width: 950px; max-width: 98vw; font-size: 1rem;">
        <button class="reviewer-modal-close" @click="closeFormModal">&times;</button>
        <div style="display: flex; justify-content: space-between; margin-bottom: 24px;">
          <select class="reviewer-modal-select" style="font-size:1rem;"><option>Frame work</option></select>
          <select class="reviewer-modal-select" style="font-size:1rem;"><option>Policy</option></select>
        </div>
        <div v-for="i in 2" :key="i" style="border:2px solid #000; margin-bottom:20px; padding:10px; background:#fff;">
          <div style="margin-bottom:10px; display:flex; align-items:center;">
            <label style="font-size:1rem;">Subpolicy</label>
            <input type="checkbox" style="margin-left:10px; width:20px; height:20px;">
          </div>
          <div v-for="j in 3" :key="j" style="display:flex; align-items:center; margin-bottom:10px;">
            <div style="width:150px; font-size:1.2rem; border-bottom:2px solid #000;">Compliancece {{ j }}</div>
            <input type="checkbox" style="margin-left:10px; width:20px; height:20px;">
            <input type="text" placeholder="Comment" style="margin-left:10px; font-size:1rem; border-radius:12px; border:2px solid #000; padding:4px 16px; width:170px;">
          </div>
          <button style="float:right; background:#6c2bd7; color:#fff; border-radius:12px; font-size:1.1rem; padding:6px 24px; border:none;">Add</button>
        </div>
        <div class="reviewer-modal-actions">
          <button class="approve-btn" @click="closeFormModal">Approve</button>
          <button class="reject-btn" @click="closeFormModal">Reject</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import './Reviewer.css'

export default {
  name: 'AuditorReviewer',
  data() {
    return {
      reviewerData: [
        {
          framework: 'ISO 27001',
          policy: 'Security',
          subpolicy: 'Visit',
          reviewer: 'Akhil',
          duedate: '24/12/2024',
          auditType: 'Internal',
          status: 'Under review'
        },
        {
          framework: 'NIST 8000',
          policy: 'HR',
          subpolicy: 'Leave',
          reviewer: 'Mani',
          duedate: '24/12/2024',
          auditType: 'Internal',
          status: 'Under review'
        }
      ],
      showFormModal: false
    }
  },
  methods: {
    openFormModal() {
      this.showFormModal = true;
    },
    closeFormModal() {
      this.showFormModal = false;
    }
  }
}
</script>

<style scoped>
@import './Reviewer.css';
.reviewer-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.reviewer-modal {
  background: #fff;
  border: 2px solid #222;
  border-radius: 8px;
  padding: 32px 24px 24px 24px;
  min-width: 350px;
  max-width: 90vw;
  position: relative;
}
.reviewer-modal-close {
  position: absolute;
  top: 10px;
  right: 18px;
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
}
.reviewer-modal-actions {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 24px;
}
.approve-btn {
  background: #4caf50;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 32px;
  font-size: 1.1rem;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}
.approve-btn:hover {
  background: #388e3c;
}
.reject-btn {
  background: #e53935;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 32px;
  font-size: 1.1rem;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}
.reject-btn:hover {
  background: #b71c1c;
}
</style> 