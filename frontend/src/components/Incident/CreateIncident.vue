<template>
    <div class="incident-container">
      <div class="incident-header">
        <button class="create-incident-btn" @click="showModal = true">
          <i class="fas fa-plus"></i> Create Incident
        </button>
      </div>
      <div class="incident-table-wrapper">
        <table class="incident-table">
          <thead>
            <tr>
              <th>Incident ID</th>
              <th>Title</th>
              <th>Description</th>
              <th>Date</th>
              <th>Time</th>
              <th>Risk Category</th>
              <th>Priority Level</th>
              <th>Attachments</th>
              <th>Comments</th>
              <th>Mitigation</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>1</td>
              <td>Manual</td>
              <td>Work in features</td>
              <td>24/7/25</td>
              <td>23:59</td>
              <td>Hr details</td>
              <td>High</td>
              <td><a href="https://www.cyberlink.com" target="_blank">www.cyberlink.com</a></td>
              <td>Need to be done</td>
              <td>Work</td>
            </tr>
            <tr v-for="i in 4" :key="i">
              <td v-for="j in 10" :key="j"></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="showModal" class="incident-modal-overlay">
        <div class="incident-modal">
          <div class="incident-modal-title">Create New Incident</div>
          <form class="incident-form" @submit.prevent="submitIncident">
            <label>Incident Title
              <input type="text" v-model="form.title" placeholder="Enter incident title" required />
            </label>
            <label>Description
              <textarea v-model="form.description" placeholder="Enter incident description" required></textarea>
            </label>
            <div class="incident-form-row">
              <label>Date
                <input type="date" v-model="form.date" required />
              </label>
              <label>Time
                <input type="time" v-model="form.time" required />
              </label>
            </div>
            <label>Risk Category
              <input type="text" v-model="form.riskCategory" placeholder="Enter risk category" required />
            </label>
            <label>Priority Level
              <select v-model="form.priorityLevel" required>
                <option value="">Select priority level</option>
                <option>High</option>
                <option>Medium</option>
                <option>Low</option>
              </select>
            </label>
            <label>Comments
              <textarea v-model="form.comments" placeholder="Enter any additional comments"></textarea>
            </label>
            <label>Attachments (text or URL)
              <input type="text" v-model="form.attachments" placeholder="Enter attachment info or URL" />
            </label>
            <label>Mitigation
              <textarea v-model="form.mitigation" placeholder="Enter mitigation steps or plan"></textarea>
            </label>
            <div class="incident-form-actions">
              <button type="submit" class="incident-submit-btn">Create Incident</button>
              <button type="button" class="incident-cancel-btn" @click="showModal = false">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'CreateIncident',
    data() {
      return {
        showModal: false,
        form: {
          title: '',
          description: '',
          date: '',
          time: '',
          riskCategory: '',
          priorityLevel: '',
          comments: '',
          attachments: '',
          mitigation: ''
        }
      }
    },
    methods: {
      submitIncident() {
        alert('Incident created!');
        this.showModal = false;
        this.form = {
          title: '',
          description: '',
          date: '',
          time: '',
          riskCategory: '',
          priorityLevel: '',
          comments: '',
          attachments: '',
          mitigation: ''
        };
      }
    }
  }
  </script>
  
  <style scoped>
  .incident-container {
    padding: 32px 32px 32px 220px;
    background: #f5f5f5;
    min-height: 100vh;
    font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
  }
  .incident-header {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 18px;
  }
  .create-incident-btn {
    background: #4f7cff;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 12px 32px;
    font-size: 1.2rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(79,124,255,0.08);
    transition: background 0.2s;
  }
  .create-incident-btn i {
    font-size: 1.2rem;
  }
  .create-incident-btn:hover {
    background: #365bb3;
  }
  .incident-table-wrapper {
    overflow-x: auto;
  }
  .incident-table {
    width: 100%;
    border-collapse: collapse;
    background: #fff;
    font-size: 1.1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  }
  .incident-table th, .incident-table td {
    border: 2px solid #222;
    padding: 10px 8px;
    text-align: left;
    min-width: 90px;
  }
  .incident-table th {
    background: #f5f5f5;
    font-weight: bold;
    font-size: 1.15rem;
  }
  .incident-table td {
    background: #fff;
  }
  .incident-table a {
    color: #4f7cff;
    text-decoration: underline;
  }
  .incident-modal-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.18);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 3000;
  }
  .incident-modal {
    background: #fff;
    border: 3px solid #222;
    border-radius: 12px;
    padding: 36px 38px 28px 38px;
    min-width: 420px;
    max-width: 98vw;
    width: 500px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  }
  .incident-modal-title {
    font-size: 1.35rem;
    font-weight: bold;
    margin-bottom: 18px;
    color: #222;
  }
  .incident-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .incident-form label {
    font-size: 1rem;
    font-weight: 600;
    color: #222;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .incident-form input[type="text"],
  .incident-form input[type="date"],
  .incident-form input[type="time"],
  .incident-form select,
  .incident-form textarea {
    padding: 8px 12px;
    border: 1.5px solid #bbb;
    border-radius: 6px;
    font-size: 1rem;
    font-family: inherit;
    resize: none;
  }
  .incident-form textarea {
    min-height: 48px;
    max-height: 120px;
  }
  .incident-form-row {
    display: flex;
    gap: 18px;
  }
  .incident-form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 18px;
    margin-top: 10px;
  }
  .incident-submit-btn {
    background: #4caf50;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 10px 32px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }
  .incident-submit-btn:hover {
    background: #388e3c;
  }
  .incident-cancel-btn {
    background: #e53935;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 10px 32px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }
  .incident-cancel-btn:hover {
    background: #b71c1c;
  }
  </style>
  