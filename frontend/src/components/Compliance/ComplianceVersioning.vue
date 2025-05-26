<template>
  <div class="versioning-container">
    <div class="versioning-form-row">
      <select v-model="selectedFramework" class="versioning-select">
        <option disabled value="">Framework</option>
        <option v-for="fw in frameworks" :key="fw">{{ fw }}</option>
      </select>
      <select v-model="selectedPolicy" class="versioning-select">
        <option disabled value="">Policies</option>
        <option v-for="p in policies" :key="p">{{ p }}</option>
      </select>
      <select v-model="selectedSubPolicy" class="versioning-select">
        <option disabled value="">Sub Policies</option>
        <option v-for="sp in subPolicies" :key="sp">{{ sp }}</option>
      </select>
      <button class="mapping-btn" @click="onMappingClick">Mapping</button>
    </div>
    <div class="versioning-mapping-row" v-if="showMapping">
      <div class="compliance-block">
        <div v-for="(compliance, idx) in complianceList1" :key="idx" class="compliance-item-row">
          <input v-model="compliance.value" class="compliance-input" :placeholder="`Compliance ${idx+1}`" :readonly="!compliance.editing" />
          <button class="compliance-remove-btn" @click="removeCompliance(1, idx)">-</button>
          <button class="compliance-edit-btn" @click="toggleEdit(1, idx)">Edit</button>
          <button v-if="idx === complianceList1.length - 1" class="compliance-add-btn" @click="addCompliance(1)">+</button>
        </div>
      </div>
      <div class="arrow-container">
        <svg width="80" height="40" viewBox="0 0 80 40">
          <line x1="0" y1="20" x2="70" y2="20" stroke="#111" stroke-width="3" marker-end="url(#arrowhead)" />
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#111" />
            </marker>
          </defs>
        </svg>
      </div>
      <div class="compliance-block">
        <div v-for="(compliance, idx) in complianceList2" :key="idx" class="compliance-item-row">
          <input v-model="compliance.value" class="compliance-input" :placeholder="`Compliance ${idx+1}`" :readonly="!compliance.editing" />
          <button class="compliance-remove-btn" @click="removeCompliance(2, idx)">-</button>
          <button class="compliance-edit-btn" @click="toggleEdit(2, idx)">Edit</button>
          <button v-if="idx === complianceList2.length - 1" class="compliance-add-btn" @click="addCompliance(2)">+</button>
        </div>
      </div>
    </div>
    <div v-else class="versioning-single-block">
      <div class="compliance-block">
        <div v-for="(compliance, idx) in complianceList1" :key="idx" class="compliance-item-row">
          <input v-model="compliance.value" class="compliance-input" :placeholder="`Compliance ${idx+1}`" :readonly="!compliance.editing" />
          <button class="compliance-remove-btn" @click="removeCompliance(1, idx)">-</button>
          <button class="compliance-edit-btn" @click="toggleEdit(1, idx)">Edit</button>
          <button v-if="idx === complianceList1.length - 1" class="compliance-add-btn" @click="addCompliance(1)">+</button>
        </div>
      </div>
    </div>
    <button class="compliance-submit-btn" @click="submitCompliance">Submit</button>
  </div>
</template>

<script>
export default {
  name: 'ComplianceVersioning',
  data() {
    return {
      selectedFramework: '',
      selectedPolicy: '',
      selectedSubPolicy: '',
      frameworks: ['Framework 1', 'Framework 2'],
      policies: ['Policy 1', 'Policy 2'],
      subPolicies: ['Sub Policy 1', 'Sub Policy 2'],
      complianceList1: [
        { value: 'Only take 5 leves a month', editing: false },
        { value: 'Leave should be intimated before', editing: false }
      ],
      complianceList2: [
        { value: '', editing: true }
      ],
      showMapping: false
    }
  },
  methods: {
    addCompliance(listNum) {
      if (listNum === 1) {
        this.complianceList1.push({ value: '', editing: true });
      } else {
        this.complianceList2.push({ value: '', editing: true });
      }
    },
    removeCompliance(listNum, idx) {
      if (listNum === 1 && this.complianceList1.length > 1) {
        this.complianceList1.splice(idx, 1);
      } else if (listNum === 2 && this.complianceList2.length > 1) {
        this.complianceList2.splice(idx, 1);
      }
    },
    toggleEdit(listNum, idx) {
      if (listNum === 1) {
        this.complianceList1[idx].editing = !this.complianceList1[idx].editing;
      } else {
        this.complianceList2[idx].editing = !this.complianceList2[idx].editing;
      }
    },
    onMappingClick() {
      this.complianceList2 = this.complianceList1.map(item => ({ value: item.value, editing: false }));
      this.showMapping = true;
    },
    submitCompliance() {
      alert('Compliance versioning submitted!');
    }
  }
}
</script>

<style scoped>
.versioning-container {
  padding: 32px 0 0 180px;
  min-height: 100vh;
  background: #fafafa;
  font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
}
.versioning-form-row {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
  justify-content: center;
}
.versioning-select {
  font-size: 1rem;
  padding: 4px 16px 4px 10px;
  border-radius: 0;
  border: 2px solid #111;
  background: #fff;
  min-width: 140px;
  text-align: left;
}
.mapping-btn {
  font-size: 1.1rem;
  padding: 4px 32px;
  border: 2px solid #111;
  background: #fff;
  color: #111;
  border-radius: 0;
  cursor: pointer;
  margin-left: 24px;
  transition: background 0.2s;
}
.mapping-btn:hover {
  background: #f0f0f0;
}
.versioning-mapping-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32px;
  margin-bottom: 32px;
}
.versioning-single-block {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
}
.compliance-block {
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: #fff;
  padding: 18px 24px;
  border: 2px solid #111;
  border-radius: 8px;
  min-width: 350px;
}
.compliance-item-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.compliance-input {
  font-size: 1.1rem;
  border: 2px solid #111;
  border-radius: 0;
  padding: 4px 12px;
  min-width: 220px;
  background: #fff;
}
.compliance-remove-btn, .compliance-add-btn, .compliance-edit-btn {
  font-size: 1.1rem;
  min-width: 44px;
  min-height: 32px;
  border-radius: 0;
  border: 2px solid #111;
  background: #fff;
  color: #111;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-left: 6px;
  transition: background 0.2s;
}
.compliance-add-btn {
  font-size: 1.3rem;
  margin-left: 8px;
  border-radius: 50%;
  width: 32px;
  height: 32px;
}
.compliance-remove-btn {
  font-size: 1.3rem;
  border-radius: 50%;
  width: 32px;
  height: 32px;
}
.compliance-edit-btn {
  font-size: 1.1rem;
  min-width: 60px;
  border-radius: 0;
}
.compliance-remove-btn:hover, .compliance-add-btn:hover, .compliance-edit-btn:hover {
  background: #f0f0f0;
}
.arrow-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 80px;
}
.compliance-submit-btn {
  display: block;
  margin: 24px auto 0 auto;
  background: #caffb6;
  color: #222;
  border: 2px solid #222;
  border-radius: 4px;
  font-size: 1.2rem;
  font-weight: 500;
  padding: 6px 32px;
  cursor: pointer;
  transition: background 0.2s;
}
.compliance-submit-btn:hover {
  background: #b6ffb6;
}
</style> 