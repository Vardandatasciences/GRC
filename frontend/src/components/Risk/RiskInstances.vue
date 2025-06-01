<template>
  <div class="risk-container">
    <div class="risk-content">
      <div class="risk-header">
        <div class="risk-title">
          <i class="fas fa-exclamation-triangle risk-icon"></i> Risk Instances
        </div>
        <button class="add-instance-btn">
          <i class="fas fa-plus"></i> Add Instance
        </button>
      </div>
      
      <!-- Cards View -->
      <div class="risk-cards-container">
        <div v-for="(instance, index) in instances" :key="instance.RiskInstanceId" class="risk-instance-card">
          <div class="risk-card-header">
            <div class="risk-id">Risk #{{ index + 1 }}</div>
            <div class="risk-status" :class="getStatusClass(instance.RiskStatus)">
              {{ instance.RiskStatus }}
            </div>
          </div>
          
          <div class="risk-card-title">{{ instance.RiskDescription }}</div>
          
          <div class="risk-card-details">
            <div class="detail-row">
              <div class="detail-item">
                <div class="detail-label">Category:</div>
                <div class="detail-value">{{ instance.Category }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">Criticality:</div>
                <div class="detail-value">{{ instance.Criticality }}</div>
              </div>
            </div>
            
            <div class="detail-row">
              <div class="detail-item">
                <div class="detail-label">Priority:</div>
                <div class="detail-value">{{ instance.RiskPriority }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">Owner:</div>
                <div class="detail-value">{{ instance.RiskOwner }}</div>
              </div>
            </div>
            
            <div class="detail-row">
              <div class="detail-item">
                <div class="detail-label">Likelihood:</div>
                <div class="detail-value">{{ instance.RiskLikelihood }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">Impact:</div>
                <div class="detail-value">{{ instance.RiskImpact }}</div>
              </div>
            </div>
            
            <div class="detail-row">
              <div class="detail-item">
                <div class="detail-label">Exposure Rating:</div>
                <div class="detail-value">{{ instance.RiskExposureRating }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">Response Type:</div>
                <div class="detail-value">{{ instance.RiskResponseType }}</div>
              </div>
            </div>
            
            <!-- Add due date information -->
            <div class="detail-row">
              <div class="detail-item">
                <div class="detail-label">Due Date:</div>
                <div class="detail-value">
                  <template v-if="instance.MitigationDueDate">
                    {{ formatDate(instance.MitigationDueDate) }}
                    <span class="due-status" :class="getDueStatusClass(instance.MitigationDueDate)">
                      {{ getDueStatusText(instance.MitigationDueDate) }}
                    </span>
                  </template>
                  <template v-else>Not set</template>
                </div>
              </div>
              <div class="detail-item">
                <div class="detail-label">Status:</div>
                <div class="detail-value">{{ instance.MitigationStatus || 'Not Started' }}</div>
              </div>
            </div>
          </div>
          
          <div class="risk-card-footer">
            <button class="view-details-btn">View Details</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RiskInstances',
  data() {
    return {
      instances: [],
      newInstance: {
        RiskId: null,
        Criticality: '',
        PossibleDamage: '',
        Category: '',
        Appetite: '',
        RiskDescription: '',
        RiskLikelihood: '',
        RiskImpact: '',
        RiskExposureRating: '',
        RiskPriority: '',
        RiskResponseType: '',
        RiskResponseDescription: '',
        RiskMitigation: '',
        RiskOwner: '',
        RiskStatus: 'Open',
        UserId: 1,
        Date: new Date().toISOString().split('T')[0]
      }
    }
  },
  mounted() {
    this.fetchInstances()
  },
  methods: {
    fetchInstances() {
      axios.get('http://localhost:8000/api/risk-instances/')
        .then(response => {
          this.instances = response.data
        })
        .catch(error => {
          console.error('Error fetching risk instances:', error)
        })
    },
    getStatusClass(status) {
      if (!status) return '';
      
      if (status.includes('Revision')) {
        return 'status-revision';
      } else if (status === 'Approved') {
        return 'status-approved';
      } else if (status === 'In Progress') {
        return 'status-in-progress';
      } else if (status === 'Open') {
        return 'status-open';
      }
      
      return '';
    },
    submitInstance() {
      // Convert numeric string values to actual numbers
      const formData = {
        ...this.newInstance,
        RiskId: parseInt(this.newInstance.RiskId) || null,
        RiskLikelihood: parseFloat(this.newInstance.RiskLikelihood) || 0,
        RiskImpact: parseFloat(this.newInstance.RiskImpact) || 0,
        RiskExposureRating: this.newInstance.RiskExposureRating ? 
          parseFloat(this.newInstance.RiskExposureRating) : null,
        UserId: parseInt(this.newInstance.UserId) || null
      }
      
      axios.post('http://localhost:8000/api/risk-instances/', formData)
        .then(response => {
          this.instances.push(response.data)
          this.newInstance = {
            RiskId: null,
            Criticality: '',
            PossibleDamage: '',
            Category: '',
            Appetite: '',
            RiskDescription: '',
            RiskLikelihood: '',
            RiskImpact: '',
            RiskExposureRating: '',
            RiskPriority: '',
            RiskResponseType: '',
            RiskResponseDescription: '',
            RiskMitigation: '',
            RiskOwner: '',
            RiskStatus: 'Open',
            UserId: 1,
            Date: new Date().toISOString().split('T')[0]
          }
          alert('Risk instance added successfully!')
        })
        .catch(error => {
          console.error('Error adding risk instance:', error.response?.data || error.message)
          alert('Error adding risk instance. Please check your data and try again.')
        })
    },
    formatDate(dateString) {
      if (!dateString) return 'Not set';
      
      try {
        // Handle ISO format and other string formats
        const date = new Date(dateString);
        
        // Check if date is valid
        if (isNaN(date.getTime())) {
          console.warn(`Invalid date format: ${dateString}`);
          return dateString; // Return as is if can't parse
        }
        
        return date.toLocaleDateString();
      } catch (e) {
        console.error(`Error formatting date: ${e}`);
        return dateString; // Return original string if there's an error
      }
    },
    getDueStatusClass(dateString) {
      if (!dateString) return '';
      
      try {
        const dueDate = new Date(dateString);
        
        // Check if date is valid
        if (isNaN(dueDate.getTime())) {
          console.warn(`Invalid date for status class: ${dateString}`);
          return '';
        }
        
        const today = new Date();
        
        // Reset the time part for accurate day comparison
        dueDate.setHours(0, 0, 0, 0);
        today.setHours(0, 0, 0, 0);
        
        const daysLeft = Math.floor((dueDate - today) / (1000 * 60 * 60 * 24));
        
        if (daysLeft < 0) return 'overdue';
        if (daysLeft <= 3) return 'urgent';
        if (daysLeft <= 7) return 'warning';
        return 'on-track';
      } catch (e) {
        console.error(`Error calculating due status class: ${e}`);
        return '';
      }
    },
    getDueStatusText(dateString) {
      if (!dateString) return '';
      
      try {
        const dueDate = new Date(dateString);
        
        // Check if date is valid
        if (isNaN(dueDate.getTime())) {
          console.warn(`Invalid date for status text: ${dateString}`);
          return '';
        }
        
        const today = new Date();
        
        // Reset the time part for accurate day comparison
        dueDate.setHours(0, 0, 0, 0);
        today.setHours(0, 0, 0, 0);
        
        const daysLeft = Math.floor((dueDate - today) / (1000 * 60 * 60 * 24));
        
        if (daysLeft < 0) return `(Delayed by ${Math.abs(daysLeft)} days)`;
        if (daysLeft === 0) return '(Due today)';
        if (daysLeft === 1) return '(Due tomorrow)';
        return `(${daysLeft} days left)`;
      } catch (e) {
        console.error(`Error calculating due status text: ${e}`);
        return '';
      }
    }
  }
}
</script>

<style>
.risk-container {
  padding: 20px;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.risk-content {
  max-width: 1200px;
  margin: 0 auto;
}

.risk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.risk-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
}

.risk-icon {
  color: #f0ad4e;
  font-size: 24px;
  margin-right: 10px;
}

.add-instance-btn {
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.add-instance-btn i {
  margin-right: 6px;
}

.risk-cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(530px, 1fr));
  gap: 20px;
}

.risk-instance-card {
  background: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border: 1px solid #e9ecef;
}

.risk-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.risk-id {
  font-weight: 600;
  color: #495057;
}

.risk-status {
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 600;
}

.status-revision {
  background: #ffebee;
  color: #d32f2f;
}

.status-approved {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-in-progress {
  background: #fff8e1;
  color: #f57c00;
}

.status-open {
  background: #e3f2fd;
  color: #1976d2;
}

.risk-card-title {
  padding: 15px 15px 5px;
  font-size: 16px;
  font-weight: 500;
  color: #212529;
  min-height: 60px;
}

.risk-card-details {
  padding: 0 15px 15px;
}

.detail-row {
  display: flex;
  margin-bottom: 5px;
}

.detail-item {
  flex: 1;
  display: flex;
  margin-bottom: 5px;
}

.detail-label {
  font-weight: 600;
  color: #6c757d;
  width: 110px;
  font-size: 13px;
}

.detail-value {
  color: #212529;
  font-size: 13px;
}

.risk-card-footer {
  padding: 10px 15px;
  border-top: 1px solid #e9ecef;
  text-align: right;
}

.view-details-btn {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 13px;
}

.view-details-btn:hover {
  background: #0069d9;
}

.due-status {
  margin-left: 5px;
  font-size: 12px;
  font-weight: 500;
}

.due-status.overdue {
  color: #f5222d;
}

.due-status.urgent {
  color: #fa8c16;
}

.due-status.warning {
  color: #faad14;
}

.due-status.on-track {
  color: #52c41a;
}
</style>

