<template>
  <div class="create-compliance-container">
    <div class="compliance-form-row">
      <select v-model="selectedFramework" class="compliance-select">
        <option disabled value="">Framework</option>
        <option v-for="fw in frameworks" :key="fw">{{ fw }}</option>
      </select>
      <select v-model="selectedPolicy" class="compliance-select">
        <option disabled value="">Policies</option>
        <option v-for="p in policies" :key="p">{{ p }}</option>
      </select>
      <select v-model="selectedSubPolicy" class="compliance-select">
        <option disabled value="">Sub Policies</option>
        <option v-for="sp in subPolicies" :key="sp">{{ sp }}</option>
      </select>
    </div>
    <div class="compliance-list">
      <div v-for="(compliance, idx) in complianceList" :key="idx" class="compliance-item-row">
        <input v-model="compliance.value" class="compliance-input" :placeholder="`Compliance ${idx+1}`" />
        <button class="compliance-remove-btn" @click="removeCompliance(idx)">-</button>
        <button v-if="idx === complianceList.length - 1" class="compliance-add-btn" @click="addCompliance">+</button>
      </div>
    </div>
    <button class="compliance-submit-btn" @click="submitCompliance">Submit</button>
  </div>
</template>

<script>
export default {
  name: 'CreateCompliance',
  data() {
    return {
      selectedFramework: '',
      selectedPolicy: '',
      selectedSubPolicy: '',
      frameworks: ['Framework 1', 'Framework 2'],
      policies: ['Policy 1', 'Policy 2'],
      subPolicies: ['Sub Policy 1', 'Sub Policy 2'],
      complianceList: [
        { value: '' },
        { value: '' }
      ]
    }
  },
  methods: {
    addCompliance() {
      this.complianceList.push({ value: '' });
    },
    removeCompliance(idx) {
      if (this.complianceList.length > 1) {
        this.complianceList.splice(idx, 1);
      }
    },
    submitCompliance() {
      // Handle submit logic here
      alert('Compliance submitted!');
    }
  }
}
</script>

<style scoped>
.create-compliance-container {
  padding: 32px 0 0 180px;
  min-height: 100vh;
  background: #fafafa;
  font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
}
.compliance-form-row {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
  justify-content: center;
}
.compliance-select {
  font-size: 1rem;
  padding: 4px 16px 4px 10px;
  border-radius: 0;
  border: 2px solid #111;
  background: #fff;
  min-width: 140px;
  text-align: left;
}
.compliance-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
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
.compliance-remove-btn, .compliance-add-btn {
  font-size: 1.3rem;
  width: 28px;
  height: 28px;
  border-radius: 50%;
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
}
.compliance-remove-btn:hover, .compliance-add-btn:hover {
  background: #f0f0f0;
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