<template>
  <div class="incident-form-page">
    <div class="incident-form-page-header">
      <h2 class="incident-form-page-title">Create Incident </h2>
    </div>
    <div class="incident-form-box">
      <div class="incident-form-box-title">
      </div>
      <form class="incident-create-form" @submit.prevent="submitIncident">
        <!-- Row 1: Basic Info (4 columns) -->
        <label>
          <span><i class="fas fa-heading"></i> Incident Title</span>
          <input type="text" v-model="form.title" placeholder="Enter incident title" required />
        </label>
        
        <label>
          <span><i class="fas fa-exclamation-circle"></i> Priority Level</span>
          <select v-model="form.priorityLevel" class="priority-select" required>
            <option value="">Select priority level</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </label>
        
        <label>
          <span><i class="fas fa-tag"></i> Risk Category</span>
          <select v-model="form.riskCategory" class="risk-select" required>
            <option value="">Select risk category</option>
            <option value="IT Security">IT Security</option>
            <option value="Compliance">Compliance</option>
            <option value="Operational">Operational</option>
            <option value="Financial">Financial</option>
            <option value="Strategic">Strategic</option>
          </select>
        </label>
        
        <label>
          <span><i class="fas fa-map-marker-alt"></i> Origin</span>
          <input type="text" value="Manual" disabled />
        </label>
        
        <!-- Row 2: Identified Dates (2 columns) -->
        <label>
          <span><i class="fas fa-calendar-check"></i> Identified Date</span>
          <input type="date" v-model="form.identifiedDate" required />
        </label>
        
        <label>
          <span><i class="fas fa-history"></i> Identified Time</span>
          <input type="time" v-model="form.identifiedTime" required />
        </label>
        
        <!-- Row 3: Description and Comments (2 columns each) -->
        <label class="field-half">
          <span><i class="fas fa-align-left"></i> Description</span>
          <textarea v-model="form.description" placeholder="Enter incident description" required></textarea>
        </label>
        
        <label class="field-half">
          <span><i class="fas fa-shield-alt"></i> Mitigation</span>
          <textarea v-model="form.mitigation" placeholder="Enter mitigation steps or plan"></textarea>
        </label>
        
        <!-- Row 4: Comments and Attachments -->
        <label class="field-half">
          <span><i class="fas fa-comments"></i> Comments</span>
          <textarea v-model="form.comments" placeholder="Enter any additional comments"></textarea>
        </label>
        
        <label class="field-half">
          <span><i class="fas fa-paperclip"></i> Attachments</span>
          <input type="text" v-model="form.attachments" placeholder="Enter attachment URL" />
        </label>

        <!-- Row 5: Action buttons -->
        <div class="incident-form-actions">
          <button type="reset" class="incident-cancel-btn">
            Clear
          </button>
          <button type="submit" class="incident-submit-btn">
            Create
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import './CreateIncident.css';

export default {
  name: 'CreateIncident',
  data() {
    return {
      form: {
        title: '',
        description: '',
        identifiedDate: '',
        identifiedTime: '',
        riskCategory: '',
        priorityLevel: '',
        comments: '',
        attachments: '',
        mitigation: ''
      }
    }
  },
  mounted() {
    this.setDefaultDates();
  },
  methods: {
    setDefaultDates() {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      const formattedDate = `${year}-${month}-${day}`;
      
      const hours = String(today.getHours()).padStart(2, '0');
      const minutes = String(today.getMinutes()).padStart(2, '0');
      const formattedTime = `${hours}:${minutes}`;
      
      this.form.identifiedDate = formattedDate;
      this.form.identifiedTime = formattedTime;
    },
    async submitIncident() {
      // Prevent double submissions
      const submitBtn = document.querySelector('.incident-submit-btn');
      if (submitBtn) submitBtn.disabled = true;
      
      try {
        // Get current date and time for the removed fields
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const currentDate = `${year}-${month}-${day}`;
        
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const currentTime = `${hours}:${minutes}`;
        
        // Map frontend fields to backend fields
        const payload = {
          IncidentTitle: this.form.title,
          Description: this.form.description,
          Mitigation: this.form.mitigation,
          Date: currentDate,
          Time: currentTime,
          IdentifiedAt: `${this.form.identifiedDate}T${this.form.identifiedTime}`,
          Origin: "Manual",
          Comments: this.form.comments,
          RiskCategory: this.form.riskCategory,
          RiskPriority: this.form.priorityLevel,
          Attachments: this.form.attachments
        };

        console.log("incident_data:", payload);

        await axios.post('http://localhost:8000/incidents/create/', payload);
        
        // Show success message with animation
        this.$nextTick(() => {
          const successMessage = document.createElement('div');
          successMessage.className = 'form-success-message';
          successMessage.textContent = 'Incident created successfully!';
          document.body.appendChild(successMessage);
          
          setTimeout(() => {
            successMessage.remove();
          }, 3000);
        });
        
        // Reset form
        this.form = {
          title: '',
          description: '',
          identifiedDate: '',
          identifiedTime: '',
          riskCategory: '',
          priorityLevel: '',
          comments: '',
          attachments: '',
          mitigation: ''
        };
        this.setDefaultDates();
      } catch (error) {
        alert('Failed to create incident: ' + (error.response?.data?.detail || error.message));
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    }
  }
}
</script>
  