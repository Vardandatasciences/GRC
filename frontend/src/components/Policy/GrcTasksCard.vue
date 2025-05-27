<template>
  <div class="grc-tasks-card">
    <div class="grc-tasks-header-row">
      <div>
        <div class="grc-tasks-title">My GRC Tasks</div>
        <div class="grc-tasks-subtitle">
          You have <a href="#" class="grc-tasks-link">4 assigned tasks</a> in GRC
        </div>
      </div>
      <button class="grc-tasks-menu-btn"><i class="fas fa-ellipsis-h"></i></button>
    </div>
    <div class="grc-tasks-table">
      <div class="grc-tasks-table-header">
        <span>Task</span>
        <span>Assigned By</span>
        <span>Status</span>
      </div>
      <div class="grc-tasks-table-row" v-for="task in tasks" :key="task.task">
        <span class="grc-task-name">{{ task.task }}</span>
        <span class="grc-task-assigned">
          <img v-if="task.avatar" :src="task.avatar" class="grc-task-avatar" alt="avatar" />
          <span>{{ task.assignedBy }}</span>
        </span>
        <span :class="['grc-task-status', task.statusClass]">{{ task.status }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GrcTasksCard',
  data() {
    return {
      tasks: [
        {
          task: 'CEO & CFO 302 Certification',
          assignedBy: 'Fatima',
          avatar: 'https://randomuser.me/api/portraits/women/44.jpg',
          status: 'Due Soon',
          statusClass: 'due-soon'
        },
        {
          task: 'Q4 Audit Committee Deck',
          assignedBy: 'Simon',
          avatar: 'https://randomuser.me/api/portraits/men/32.jpg',
          status: 'Overdue',
          statusClass: 'overdue'
        },
        {
          task: 'ERM Risk Assessments for SVPs',
          assignedBy: 'Olivia',
          avatar: 'https://randomuser.me/api/portraits/women/65.jpg',
          status: 'In Progress',
          statusClass: 'in-progress'
        },
        {
          task: 'ESG Report – Business Legal Review',
          assignedBy: 'Francesco',
          avatar: 'https://randomuser.me/api/portraits/men/41.jpg',
          status: 'Pending',
          statusClass: 'pending'
        }
      ]
    }
  }
}
</script>

<style scoped>
.grc-tasks-card {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  padding: 22px 20px 18px 20px;
  min-width: 0;
  width: 100%;
  max-width: 370px;
  font-size: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border: 1.5px solid #e0e7ef;
}
.grc-tasks-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 10px;
}
.grc-tasks-title {
  font-size: 18px;
  font-weight: 600;
  color: #222;
  margin-bottom: 2px;
}
.grc-tasks-subtitle {
  font-size: 13px;
  color: #6b7280;
}
.grc-tasks-link {
  color: #2d8cff;
  text-decoration: underline;
  font-weight: 500;
}
.grc-tasks-menu-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 18px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 6px;
  transition: background 0.2s;
}
.grc-tasks-menu-btn:hover {
  background: #f3f4f6;
}
.grc-tasks-table {
  width: 100%;
  margin-top: 6px;
}
.grc-tasks-table-header {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr;
  font-size: 13px;
  color: #888;
  font-weight: 500;
  margin-bottom: 6px;
  padding-bottom: 2px;
  border-bottom: 1px solid #f3f4f6;
}
.grc-tasks-table-row {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr;
  align-items: center;
  font-size: 14px;
  padding: 7px 0;
  border-bottom: 1px solid #f7f7fa;
  gap: 0 8px;
}
.grc-task-name {
  color: #222;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.grc-task-assigned {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 14px;
  color: #444;
}
.grc-task-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}
.grc-task-status {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  color: #fff;
  text-align: center;
  min-width: 80px;
}
.grc-task-status.due-soon {
  background: #fbbf24;
  color: #fff;
}
.grc-task-status.overdue {
  background: #ef4444;
  color: #fff;
}
.grc-task-status.in-progress {
  background: #22c55e;
  color: #fff;
}
.grc-task-status.pending {
  background: #d1d5db;
  color: #444;
}
</style> 