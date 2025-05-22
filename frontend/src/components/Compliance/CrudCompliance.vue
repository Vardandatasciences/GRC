<template>
  <div class="crud-compliance-container">
    <div class="crud-form-row">
      <select v-model="selectedFramework" class="crud-select">
        <option disabled value="">Framework</option>
        <option v-for="fw in frameworks" :key="fw">{{ fw }}</option>
      </select>
      <select v-model="selectedPolicy" class="crud-select">
        <option disabled value="">Policies</option>
        <option v-for="p in policies" :key="p">{{ p }}</option>
      </select>
      <select v-model="selectedSubPolicy" class="crud-select">
        <option disabled value="">Sub Policies</option>
        <option v-for="sp in subPolicies" :key="sp">{{ sp }}</option>
      </select>
    </div>
    <div class="crud-list">
      <div v-for="(compliance, idx) in complianceList" :key="idx" class="crud-item-row">
        <input type="checkbox" v-model="compliance.checked" class="crud-checkbox" />
        <input
          v-model="compliance.value"
          class="crud-input"
          :readonly="!compliance.editing"
          :placeholder="`Compliance ${idx+1}`"
        />
        <button class="crud-remove-btn" @click="removeCompliance(idx)">-</button>
        <button class="crud-edit-btn" @click="toggleEdit(idx)">Edit</button>
        <button v-if="idx === complianceList.length - 1" class="crud-add-btn" @click="addCompliance">+</button>
      </div>
    </div>
    <button class="crud-submit-btn" @click="submitCompliance">Submit</button>
  </div>
</template>

<script>
export default {
  name: 'CrudCompliance',
  data() {
    return {
      selectedFramework: '',
      selectedPolicy: '',
      selectedSubPolicy: '',
      frameworks: ['Framework 1', 'Framework 2'],
      policies: ['Policy 1', 'Policy 2'],
      subPolicies: ['Sub Policy 1', 'Sub Policy 2'],
      complianceList: [
        { value: 'Only take 5 leves a month', checked: false, editing: false },
        { value: 'Leave should be intimated before', checked: false, editing: false }
      ]
    }
  },
  methods: {
    addCompliance() {
      this.complianceList.push({ value: '', checked: false, editing: true });
    },
    removeCompliance(idx) {
      if (this.complianceList.length > 1) {
        this.complianceList.splice(idx, 1);
      }
    },
    toggleEdit(idx) {
      this.complianceList[idx].editing = !this.complianceList[idx].editing;
    },
    submitCompliance() {
      // Handle submit logic here
      alert('CRUD Compliance submitted!');
    }
  }
}
</script>

<style scoped>
.crud-compliance-container {
  padding: 32px 0 0 180px;
  min-height: 100vh;
  background: #fafafa;
  font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
}
.crud-form-row {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
  justify-content: center;
}
.crud-select {
  font-size: 1rem;
  padding: 4px 16px 4px 10px;
  border-radius: 0;
  border: 2px solid #111;
  background: #fff;
  min-width: 140px;
  text-align: left;
}
.crud-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}
.crud-item-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.crud-checkbox {
  width: 28px;
  height: 28px;
  margin-right: 8px;
}
.crud-input {
  font-size: 1.1rem;
  border: 2px solid #111;
  border-radius: 0;
  padding: 4px 12px;
  min-width: 320px;
  background: #fff;
}
.crud-remove-btn, .crud-add-btn, .crud-edit-btn {
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
.crud-add-btn {
  font-size: 1.3rem;
  margin-left: 8px;
  border-radius: 50%;
  width: 32px;
  height: 32px;
}
.crud-remove-btn {
  font-size: 1.3rem;
  border-radius: 50%;
  width: 32px;
  height: 32px;
}
.crud-edit-btn {
  font-size: 1.1rem;
  min-width: 60px;
  border-radius: 0;
}
.crud-remove-btn:hover, .crud-add-btn:hover, .crud-edit-btn:hover {
  background: #f0f0f0;
}
.crud-submit-btn {
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
.crud-submit-btn:hover {
  background: #b6ffb6;
}
</style> 