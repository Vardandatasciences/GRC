<template>
  <div class="performance-page-wrapper">
    <div class="performance-page">
      <h2 class="top-bar-heading">Policy 
        Performance</h2>
      
      <div class="search-framework-row">
        <div class="modern-search-bar-wrapper">
          <div class="modern-search-bar">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="Search Policy"
              class="modern-search-input"
            />
            <button class="modern-search-btn" tabindex="-1">
              <i class="fas fa-search"></i>
            </button>
          </div>
        </div>
        <div class="framework-dropdown-center">
          <select v-model="selectedFramework" @change="handleFrameworkChange">
            <option value="all">Select Framework</option>
            <option value="nist">NIST</option>
            <option value="iso">ISO 27001</option>
            <option value="pci">PCI DSS</option>
            <option value="gdpr">GDPR</option>
          </select>
        </div>
      </div>

      <!-- Policy Cards Grid -->
      <div class="policy-cards-grid">
        <div 
          v-for="(policy, index) in filteredPolicies" 
          :key="index"
          class="policy-card"
        >
          <div class="policy-card-header">
            <div class="policy-card-icon">
              {{ policy.category.charAt(0) }}
            </div>
            <div class="policy-card-title">{{ policy.name }}</div>
            <div class="policy-card-upload">
              <i class="fas fa-cloud-arrow-up"></i>
            </div>
          </div>
          <div class="policy-card-progressbar">
            <div class="progress-bar-main">
              <div class="progress-bar-fill" :style="{ width: policy.progress }"></div>
            </div>
            <span class="policy-card-progress-label">{{ policy.progress }} Latest results</span>
          </div>
          <div class="policy-card-analytics">
            <span>Analytics</span>
            <span class="policy-card-analytics-arrow">▼</span>
          </div>
          <div class="policy-card-list">
            <div class="policy-card-list-header">
              <span>Performance</span>
            </div>
            <div 
              v-for="(item, idx) in policy.subpolicies" 
              :key="idx"
              class="policy-card-list-row"
            >
              <span class="policy-card-list-label">{{ item.name }}</span>
              <div class="policy-card-list-progress">
                <template v-if="item.status === 'Completed'">
                  <div class="progress-bar-sub">
                    <div 
                      class="progress-bar-fill-sub" 
                      :style="{ width: `${item.percent}%` }"
                    ></div>
                  </div>
                </template>
                <span 
                  :class="[
                    'policy-card-list-status',
                    item.status === 'Completed' ? 'completed-modern' : 'inprogress-modern'
                  ]"
                >
                  {{ item.status }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'PerformancePage',
  setup() {
    const searchQuery = ref('')
    const selectedFramework = ref('all')

    // Sample data for policies
    const policies = [
      {
        id: '1.1',
        name: 'Financial Policy',
        category: 'Financial',
        progress: '40%',
        framework: 'nist',
        subpolicies: [
          { name: 'Budget Management', status: 'Completed', percent: 95 },
          { name: 'Expense Tracking', status: 'Completed', percent: 88 },
          { name: 'Financial Reporting', status: 'In Progress', percent: 65 },
          { name: 'Audit Compliance', status: 'In Progress', percent: 70 },
          { name: 'Risk Assessment', status: 'In Progress', percent: 45 }
        ]
      },
      {
        id: '1.2',
        name: 'Service Policy',
        category: 'Service',
        progress: '50%',
        framework: 'iso',
        subpolicies: [
          { name: 'Customer Support', status: 'Completed', percent: 92 },
          { name: 'Service Delivery', status: 'In Progress', percent: 75 }
        ]
      },
      {
        id: '2.1',
        name: 'Loan Policy',
        category: 'Loan',
        progress: '80%',
        framework: 'pci',
        subpolicies: [
          { name: 'Loan Processing', status: 'Completed', percent: 90 },
          { name: 'Credit Assessment', status: 'Completed', percent: 85 },
          { name: 'Risk Evaluation', status: 'Completed', percent: 88 },
          { name: 'Documentation', status: 'Completed', percent: 92 },
          { name: 'Compliance Check', status: 'In Progress', percent: 60 }
        ]
      }
    ]

    // Filter policies based on search query and selected framework
    const filteredPolicies = computed(() => {
      return policies.filter(policy => {
        const matchesSearch = policy.name.toLowerCase().includes(searchQuery.value.toLowerCase());
        const matchesFramework = selectedFramework.value === 'all' || policy.framework === selectedFramework.value;
        return matchesSearch && matchesFramework;
      });
    });
    
    const handleFrameworkChange = () => {
      // Framework change handler
    }

    return {
      searchQuery,
      selectedFramework,
      filteredPolicies,
      handleFrameworkChange
    }
  }
}
</script>

<style scoped>
@import './PerformancePage.css';

/* Top bar heading styles */
.top-bar-heading {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 700;
  color: #26324b;
  position: relative;
  display: inline-block;
  margin-bottom: 32px;
  transition: all 0.3s ease;
}

.top-bar-heading::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #6c2cff, #4f46e5);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.top-bar-heading:hover::after {
  width: 100%;
}

.performance-page-wrapper {
  padding-left: 20px; /* Additional left padding via wrapper */
  overflow-x: hidden; /* Prevent horizontal scrolling */
}
</style> 