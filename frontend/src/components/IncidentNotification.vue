<template>
  <div class="incident-notification">
    <h2>New Incident Alert</h2>
    <p><strong>Incident ID:</strong> {{ incident.IncidentId || incident.id }}</p>
    <p><strong>Title:</strong> {{ incident.incidenttitle || incident.title }}</p>
    <p><strong>Description:</strong> {{ incident.description }}</p>
    <div v-if="!showAssignDropdown" class="notification-actions">
      <button class="solve-btn" @click="$emit('solve')">Want to Solve</button>
      <button class="no-btn" @click="$emit('reject')">No</button>
    </div>
    <div v-else class="assign-dropdown">
      <label>Assignee:
        <select v-model="selectedAssignee">
          <option v-for="user in users" :key="user.UserId" :value="user.UserId">
            {{ user.UserName }}
          </option>
        </select>
      </label>
      <label>Reviewer:
        <select v-model="selectedReviewer">
          <option v-for="user in users" :key="user.UserId" :value="user.UserId">
            {{ user.UserName }}
          </option>
        </select>
      </label>
      <button @click="assign">Done</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IncidentNotification',
  props: {
    incident: { type: Object, required: true },
    showAssignDropdown: { type: Boolean, default: false },
    users: { type: Array, default: () => [] }
  },
  data() {
    return {
      selectedAssignee: null,
      selectedReviewer: null
    }
  },
  methods: {
    assign() {
      if (!this.selectedAssignee || !this.selectedReviewer) {
        alert('Please select both assignee and reviewer.');
        return;
      }
      this.$emit('assign', {
        incidentId: this.incident.IncidentId || this.incident.id,
        assigneeId: this.selectedAssignee,
        reviewerId: this.selectedReviewer
      });
      // Reset dropdowns for next use
      this.selectedAssignee = null;
      this.selectedReviewer = null;
    }
  }
}
</script>

<style scoped>
.incident-notification {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 2rem;
  max-width: 400px;
  margin: 2rem auto;
  text-align: left;
}
.notification-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}
.solve-btn {
  background: #4CAF50;
  color: #fff;
  border: none;
  padding: 0.7rem 1.5rem;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}
.no-btn {
  background: #dc3545;
  color: #fff;
  border: none;
  padding: 0.7rem 1.5rem;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}
.assign-dropdown {
  background: #f8f9fa;
  border: 1px solid #ccc;
  padding: 1rem;
  border-radius: 6px;
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>