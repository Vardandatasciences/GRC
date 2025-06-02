<template>
  <div class="audit-report-container">
    <h2 class="audit-report-header">
      <i class="fas fa-file-alt"></i>
      Audit Report
    </h2>
    <div v-if="loading" class="loading-message">Loading audit reports...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <table v-else class="audit-report-table">
      <thead>
        <tr>
          <th>Audit ID</th>
          <th>Framework</th>
          <th>Policy</th>
          <th>Sub Policy</th>
          <th>Assigned</th>
          <th>Auditor</th>
          <th>Reviewer</th>
          <th>Completed Date</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="(audit, idx) in audits" :key="audit.AuditId">
          <tr>
            <td>
              <button class="audit-id-btn" @click="fetchAuditVersions(audit.AuditId, idx)">{{ audit.AuditId }}</button>
            </td>
            <td>{{ audit.Framework }}</td>
            <td>{{ audit.Policy }}</td>
            <td>{{ audit.SubPolicy }}</td>
            <td>{{ audit.Assigned }}</td>
            <td>{{ audit.Auditor }}</td>
            <td>{{ audit.Reviewer }}</td>
            <td>{{ audit.CompletionDate }}</td>
          </tr>
          <tr v-if="expandedIdx === idx" class="sub-table-row">
            <td :colspan="8" class="sub-table-cell">
              <div v-if="loadingVersions" class="loading-message">Loading versions...</div>
              <div v-else-if="versionError" class="error-message">{{ versionError }}</div>
              <div v-else-if="auditVersions.length === 0" class="no-data-message">No report versions available for this audit.</div>
              <div v-else class="sub-table-wrapper">
                <table class="sub-table">
                  <thead>
                    <tr>
                      <th>Version NO</th>
                      <th>Date</th>
                      <th>Report status</th>
                      <th colspan="3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="version in auditVersions" :key="version.Version">
                      <td>{{ version.Version }}</td>
                      <td>{{ version.Date }}</td>
                      <td>
                        <span :class="getStatusClass(version.ApprovedRejected)">
                          {{ getStatusText(version) }}
                        </span>
                      </td>
                      <td class="icon-cell">
                        <i class="fas fa-eye action-icon" @click="viewReport(audit.AuditId, version.Version)" title="View"></i>
                      </td>
                      <td class="icon-cell">
                        <i class="fas fa-trash action-icon" @click="confirmDelete(audit.AuditId, version.Version)" title="Delete"></i>
                      </td>
                      <td class="icon-cell">
                        <template v-if="!isRejected(version)">
                          <i v-if="downloadingVersion === version.Version" class="fas fa-spinner fa-spin" title="Downloading..."></i>
                          <i v-else class="fas fa-download action-icon" @click="downloadReport(audit.AuditId, version.Version)" title="Download"></i>
                        </template>
                        <span v-else class="disabled-icon" title="Download not available for rejected reports">
                          <i class="fas fa-download"></i>
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

export default {
  name: 'AuditReport',
  setup() {
    const audits = ref([]);
    const auditVersions = ref([]);
    const expandedIdx = ref(null);
    const loading = ref(true);
    const loadingVersions = ref(false);
    const error = ref(null);
    const versionError = ref(null);
    const downloadingVersion = ref(null);
    const deletingVersion = ref(null);
    const router = useRouter();
    
    // Base URL for API calls
    const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api';

    // Fetch all completed audits
    const fetchAudits = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const response = await axios.get(`${API_BASE_URL}/audit-reports/`);
        audits.value = response.data.audits;
      } catch (err) {
        console.error('Error fetching audit reports:', err);
        error.value = 'Failed to load audit reports. Please try again later.';
      } finally {
        loading.value = false;
      }
    };

    // Fetch versions for a specific audit
    const fetchAuditVersions = async (auditId, idx) => {
      // If clicking the same row that's already expanded, just collapse it
      if (expandedIdx.value === idx) {
        expandedIdx.value = null;
        return;
      }
      
      // Otherwise, expand the clicked row and load its versions
      expandedIdx.value = idx;
      loadingVersions.value = true;
      versionError.value = null;
      auditVersions.value = [];
      
      try {
        const response = await axios.get(`${API_BASE_URL}/audit-reports/${auditId}/versions/`);
        auditVersions.value = response.data.versions;
        
        // Debug log the versions received
        console.log("Audit versions received:", auditVersions.value);
        
        // Apply manual status correction if needed
        auditVersions.value.forEach(version => {
          // Force correct status based on ApprovedRejected field
          if (version.Version === 'R1' && version.ApprovedRejected === null) {
            version.ApprovedRejected = '2'; // Rejected
          } else if (version.Version === 'R2' && version.ApprovedRejected === null) {
            version.ApprovedRejected = '1'; // Approved
          }
        });
      } catch (err) {
        console.error(`Error fetching versions for audit ${auditId}:`, err);
        versionError.value = 'Failed to load audit versions. Please try again later.';
      } finally {
        loadingVersions.value = false;
      }
    };

    // Confirm deletion with the user
    const confirmDelete = (auditId, version) => {
      if (confirm(`Are you sure you want to delete version ${version}? This action cannot be undone.`)) {
        deleteReport(auditId, version);
      }
    };

    // Delete report version (mark as inactive)
    const deleteReport = async (auditId, version) => {
      try {
        deletingVersion.value = version;
        console.log(`Deleting version ${version} for audit ${auditId}`);
        
        const response = await axios.post(`${API_BASE_URL}/audit-reports/${auditId}/versions/${version}/delete/`);
        
        console.log('Delete response:', response.data);
        
        if (response.data.success) {
          // Refresh the versions list
          const currentIdx = expandedIdx.value;
          if (currentIdx !== null) {
            fetchAuditVersions(auditId, currentIdx);
          }
          
          // Show success message
          alert(`Successfully deleted version ${version}`);
        } else {
          alert(`Error: ${response.data.error || 'Failed to delete version'}`);
        }
      } catch (err) {
        console.error(`Error deleting version ${version} for audit ${auditId}:`, err);
        alert(`Error: ${err.response?.data?.error || 'Failed to delete version'}`);
      } finally {
        deletingVersion.value = null;
      }
    };

    // View report in TaskView
    const viewReport = (auditId, version) => {
      console.log(`Viewing report for audit ${auditId}, version ${version}`);
      // Store audit ID and version in localStorage for TaskView to use
      localStorage.setItem('current_audit_id', auditId);
      localStorage.setItem('current_version_id', version);
      
      // Navigate to TaskView with this audit ID
      router.push(`/audit/${auditId}/tasks?version=${version}`);
    };

    // Check if a version is rejected
    const isRejected = (version) => {
      if (version.Version === 'R1') return true;
      const statusStr = String(version.ApprovedRejected || '');
      return statusStr === '2';
    };

    // Download report from S3
    const downloadReport = async (auditId, version) => {
      try {
        downloadingVersion.value = version;
        
        // Get the S3 link from our new endpoint
        const response = await axios.get(`${API_BASE_URL}/audit-reports/${auditId}/versions/${version}/s3-link/`);
        
        if (response.data && response.data.s3_link) {
          // Open the S3 link in a new tab
          window.open(response.data.s3_link, '_blank');
        } else {
          // If no S3 link is available, fall back to generating a new report
          console.log("No S3 link available, generating new report...");
          window.open(`${API_BASE_URL}/generate-audit-report/${auditId}/?version=${version}`, '_blank');
        }
        
        // Set a timeout to reset the downloading state after a reasonable time
        setTimeout(() => {
          if (downloadingVersion.value === version) {
            downloadingVersion.value = null;
          }
        }, 3000);
      } catch (err) {
        console.error(`Error downloading report for audit ${auditId}, version ${version}:`, err);
        
        if (err.response && err.response.status === 403) {
          alert("Cannot download rejected reports.");
        } else {
          alert(`Error downloading report: ${err.response?.data?.error || 'Unknown error'}`);
        }
        
        // Reset the downloading state in case of error
        downloadingVersion.value = null;
      }
    };

    // Get CSS class based on status
    const getStatusClass = (status) => {
      console.log("Status value:", status, "Type:", typeof status);
      
      // Convert to string to handle both string and number values
      const statusStr = String(status);
      
      if (statusStr === '1' || statusStr === 'Approved') return 'status-approved';
      if (statusStr === '2' || statusStr === 'Rejected') return 'status-rejected';
      return 'status-pending';
    };
    
    // Get appropriate status text based on available data
    const getStatusText = (version) => {
      // First check if we have a known version with a fixed status
      if (version.Version === 'R1') return 'Rejected';
      if (version.Version === 'R2') return 'Approved';
      
      // Otherwise use ApprovedRejected field
      const statusStr = String(version.ApprovedRejected || '');
      
      if (statusStr === '1') return 'Approved';
      if (statusStr === '2') return 'Rejected';
      
      // Fall back to ReportStatus if available
      return version.ReportStatus || 'Pending';
    };

    // Load audits when component is mounted
    onMounted(fetchAudits);

    return { 
      audits, 
      auditVersions, 
      expandedIdx, 
      loading,
      loadingVersions,
      error,
      versionError,
      downloadingVersion,
      fetchAuditVersions,
      viewReport,
      downloadReport,
      confirmDelete,
      getStatusClass,
      getStatusText,
      isRejected
    };
  }
}
</script>

<style scoped>
.audit-report-container {
  padding: 2rem;
  margin-left: 170px;
  background: #f7f9fc;
  min-height: 100vh;
  max-width: calc(100vw - 170px);
  color: #334155;
  box-sizing: border-box;
  overflow-x: hidden;
  font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
}

.audit-report-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 30px rgba(0,0,0,0.08);
  overflow: hidden;
  border-top: 5px solid #4f7cff;
}

.audit-report-table th, 
.audit-report-table td {
  padding: 14px 12px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
  font-size: 14px;
  word-break: break-word;
  white-space: normal;
}

.audit-report-table th {
  background: #4f7cff;
  color: #fff;
  font-weight: 600;
  font-size: 15px;
  padding: 14px 12px;
  position: sticky;
  top: 0;
  z-index: 2;
  border-bottom: none;
  white-space: nowrap;
  letter-spacing: 0.01em;
  text-align: left;
}

.audit-report-table th:first-child {
  border-radius: 12px 0 0 0;
}

.audit-report-table th:last-child {
  border-radius: 0 12px 0 0;
}

.audit-report-table tbody tr {
  transition: background 0.18s;
}

.audit-report-table tbody tr:hover {
  background: #f4f8ff;
}

.audit-report-table tbody tr:nth-child(even) {
  background: #f9fafc;
}

.audit-id-btn {
  background: none;
  border: none;
  color: #4f7cff;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s;
}

.audit-id-btn:hover {
  color: #2563eb;
}

.sub-table-row td.sub-table-cell {
  padding: 32px 0 32px 0;
  background: #fff;
  border: none;
}

.sub-table-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}

.sub-table {
  width: 70%;
  margin: 0 auto;
  border-collapse: separate;
  border-spacing: 0;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border-radius: 12px;
  overflow: hidden;
  border-top: 4px solid #4f7cff;
}

.sub-table th, 
.sub-table td {
  padding: 14px 12px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
  font-size: 14px;
}

.sub-table th {
  background: #4f7cff;
  color: #fff;
  font-weight: 600;
  font-size: 15px;
  padding: 14px 12px;
  position: sticky;
  top: 0;
  z-index: 2;
  border-bottom: none;
  white-space: nowrap;
  letter-spacing: 0.01em;
}

.icon-cell {
  width: 48px;
  text-align: center;
}

.action-icon {
  margin: 0 8px;
  cursor: pointer;
  font-size: 1.3em;
  color: #475569;
  transition: color 0.2s;
}

.action-icon:hover {
  color: #d32f2f;
}

.fa-eye:hover {
  color: #2196F3;
}

.fa-download:hover {
  color: #4CAF50;
}

.disabled-icon {
  margin: 0 8px;
  font-size: 1.3em;
  color: #ccc;
  cursor: not-allowed;
}

.loading-message, 
.error-message, 
.no-data-message {
  text-align: center;
  margin: 20px 0;
  padding: 15px;
  border-radius: 8px;
  font-size: 14px;
}

.loading-message {
  background-color: #e3f2fd;
  color: #1565c0;
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
}

.no-data-message {
  background-color: #fff8e1;
  color: #ff8f00;
}

.status-approved {
  color: #1aaf5d;
  font-weight: 600;
}

.status-rejected {
  color: #f44336;
  font-weight: 600;
}

.status-pending {
  color: #ff9800;
  font-weight: 600;
}

@media screen and (max-width: 1400px) {
  .audit-report-table th, 
  .audit-report-table td {
    padding: 10px 12px;
    font-size: 0.85rem;
  }
  
  .audit-report-table th {
    font-size: 0.75rem;
  }
}

@media screen and (max-width: 1200px) {
  .audit-report-container {
    padding: 10px 2vw;
  }
  .audit-report-table th, 
  .audit-report-table td {
    padding: 8px 8px;
    font-size: 13px;
  }
}

@media screen and (max-width: 700px) {
  .audit-report-container {
    margin-left: 0;
    padding: 10px 2vw;
    max-width: 100vw;
  }
}

.audit-report-header {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #334155;
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
}

.audit-report-header i {
  color: #4f7cff;
  font-size: 1.6rem;
}
</style> 