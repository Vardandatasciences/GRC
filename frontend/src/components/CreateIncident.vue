<template>
  <div class="create-incident-container">
    <h2>Create New Incident</h2>
    <form @submit.prevent="submitIncident" class="incident-form">
      <div class="form-group">
        <label for="title">Incident Title</label>
        <input 
          type="text" 
          id="title" 
          v-model="incident.incidenttitle" 
          required
          placeholder="Enter incident title"
        />
      </div>

      <div class="form-group">
        <label for="description">Description</label>
        <textarea 
          id="description" 
          v-model="incident.description" 
          required
          placeholder="Enter incident description"
        ></textarea>
      </div>

      <div class="form-group">
        <label for="Date">Date</label>
        <input 
          type="date" 
          id="Date" 
          v-model="incident.Date" 
          required
        />
      </div>

      <div class="form-group">
        <label for="Time">Time</label>
        <input 
          type="time" 
          id="Time" 
          v-model="incident.Time" 
          required
        />
      </div>

      <div class="form-group">
        <label for="risk_category">Risk Category</label>
        <input 
          type="text" 
          id="risk_category" 
          v-model="incident.risk_category" 
          required
          placeholder="Enter risk category"
        />
      </div>

      <div class="form-group">
        <label for="priority_level">Priority Level</label>
        <select id="priority_level" v-model="incident.priority_level" required>
          <option value="">Select priority level</option>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
          <option value="Critical">Critical</option>
        </select>
      </div>

      <div class="form-group">
        <label for="comments">Comments</label>
        <textarea 
          id="comments" 
          v-model="incident.Comments" 
          placeholder="Enter any additional comments"
        ></textarea>
      </div>

      <div class="form-group">
        <label for="attachments">Attachments (text or URL)</label>
        <input 
          type="text" 
          id="attachments" 
          v-model="incident.attachments" 
          placeholder="Enter attachment info or URL"
        />
      </div>

      <div class="form-group">
        <label for="mitigation">Mitigation</label>
        <textarea
          id="mitigation"
          v-model="incident.mitigation"
          placeholder="Enter mitigation steps or plan"
          rows="3"
        ></textarea>
      </div>

      <div class="form-actions">
        <button type="submit" class="submit-btn">Create Incident</button>
        <button type="button" @click="goBack" class="cancel-btn">Cancel</button>
      </div>

      <div v-if="error" class="error-message">{{ error }}</div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'CreateIncident',
  data() {
    return {
      incident: {
        incidenttitle: '',
        description: '',
        Date: new Date().toISOString().split('T')[0],
        Time: new Date().toTimeString().split(' ')[0].slice(0,5),
        risk_category: '',
        priority_level: '',
        Comments: '',
        Origin: 'Web',
        attachments: '',
        mitigation: ''
      },
      error: ''
    }
  },
  methods: {
    async submitIncident() {
      try {
        const payload = {
          incidenttitle: this.incident.incidenttitle,
          description: this.incident.description,
          Date: this.incident.Date,
          Time: this.incident.Time,
          risk_category: this.incident.risk_category,
          priority_level: this.incident.priority_level,
          Comments: this.incident.Comments,
          attachments: this.incident.attachments,
          mitigation: this.incident.mitigation,
          Origin: 'Web'
        };
        const response = await axios.post('http://localhost:8000/incidents/create/', payload);
        if (response.status === 201) {
          this.$router.push('/incidents');
        }
      } catch (err) {
        this.error = err.response?.data || 'Failed to create incident';
      }
    },
    goBack() {
      this.$router.push('/incidents');
    }
  }
}
</script>

<style scoped>
.create-incident-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.incident-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: 600;
  color: #333;
}

input, textarea, select {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

textarea {
  min-height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.submit-btn, .cancel-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-btn {
  background-color: #4CAF50;
  color: white;
}

.submit-btn:hover {
  background-color: #45a049;
}

.cancel-btn {
  background-color: #f44336;
  color: white;
}

.cancel-btn:hover {
  background-color: #da190b;
}

.error-message {
  color: #f44336;
  margin-top: 1rem;
  padding: 0.5rem;
  background-color: #ffebee;
  border-radius: 4px;
}
</style> 