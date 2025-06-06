<template>
  <div class="create-framework-container">
    <h2>Create Framework</h2>
    
    <!-- Framework Form -->
    <div v-if="!showExtractionScreens" class="framework-form-container">
      <form class="form-section" @submit.prevent="handleFrameworkFormSubmit">
        <!-- Framework ID and Name in one row -->
        <div class="form-row">
          <div class="form-group">
            <label>Framework ID</label>
            <div class="input-wrapper">
              <input type="text" v-model="formData.frameworkId" placeholder="Enter framework id" />
            </div>
          </div>
          
          <div class="form-group">
            <label>Framework Name</label>
            <div class="input-wrapper">
              <input type="text" v-model="formData.frameworkName" placeholder="Enter framework name" />
            </div>
          </div>
        </div>
        
        <!-- Version and Upload Document in one row -->
        <div class="form-row">
          <div class="form-group">
            <label>Version</label>
            <div class="input-wrapper">
              <input type="text" v-model="formData.version" placeholder="Enter version" />
            </div>
          </div>
          
          <div class="form-group">
            <label>Upload Document</label>
            <div class="upload-input-container">
              <input type="file" id="framework-doc" class="file-input" @change="handleFileUpload" />
              <label for="framework-doc" class="upload-label">
                <span class="upload-text">Choose File</span>
              </label>
            </div>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>Effective Start Date</label>
            <div class="input-wrapper">
              <input type="date" v-model="formData.effectiveStartDate" />
            </div>
          </div>
          
          <div class="form-group">
            <label>Effective End Date</label>
            <div class="input-wrapper">
              <input type="date" v-model="formData.effectiveEndDate" />
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <label>Created By</label>
          <div class="input-wrapper">
            <input type="text" v-model="formData.createdBy" placeholder="Enter creator name" />
          </div>
        </div>
        
        <button class="create-btn" type="submit">Submit</button>
      </form>
    </div>

    <!-- Extraction Content (Now Inline) -->
    <div v-if="showExtractionScreens && extractionSlides.length > 0" class="extraction-inline-container">
      <div class="extraction-content">
        <div class="extraction-header">
          <!-- Stepper Navigation Bar as Tabs -->
          <div class="extraction-stepper">
            <div
              v-for="(slide, idx) in extractionSlides"
              :key="idx"
              :class="['extraction-step', { active: extractionStep === idx }]"
              @click="extractionStep = idx"
              :style="{ cursor: extractionStep !== idx ? 'pointer' : 'default' }"
            >
              {{ slide.type === 'framework' ? 'Framework' : 
                 slide.type === 'policy' ? `Policy ${slide.index !== undefined ? slide.index + 1 : ''}` : 
                 'Authorizer' }}
              <span
                class="tab-close"
                v-if="extractionStep === idx"
                @click.stop="showExtractionScreens = false"
              >
                X
              </span>
            </div>
          </div>
        </div>
        <div class="extraction-body">
          <!-- Render slide content based on type -->
          <div v-if="extractionSlides[extractionStep].type === 'framework'">
            <label>Title:</label>
            <input :value="extractionSlides[extractionStep].data.title" readonly />
            <label>Description:</label>
            <textarea :value="extractionSlides[extractionStep].data.description" readonly></textarea>
          </div>
          <div v-else-if="extractionSlides[extractionStep].type === 'policy'">
            <div class="policy-main">
              <b>Policy</b>
              <label>Title:</label>
              <input :value="extractionSlides[extractionStep].data.title" readonly />
              <label>Description:</label>
              <textarea :value="extractionSlides[extractionStep].data.description" readonly></textarea>
              <label v-if="extractionSlides[extractionStep].data.objective">Objective:</label>
              <textarea v-if="extractionSlides[extractionStep].data.objective" :value="extractionSlides[extractionStep].data.objective" readonly></textarea>
              <label v-if="extractionSlides[extractionStep].data.scope">Scope:</label>
              <textarea v-if="extractionSlides[extractionStep].data.scope" :value="extractionSlides[extractionStep].data.scope" readonly></textarea>
            </div>
            <div v-if="extractionSlides[extractionStep].data.subPolicies && extractionSlides[extractionStep].data.subPolicies.length" class="subpolicies-group">
              <div v-for="(sub, i) in extractionSlides[extractionStep].data.subPolicies" :key="i" class="subpolicy-card extraction-subpolicy">
                <b>Sub Policy {{ i + 1 }}</b>
                <label>Title:</label>
                <input :value="sub.title" readonly />
                <label>Description:</label>
                <textarea :value="sub.description" readonly></textarea>
              </div>
            </div>
          </div>
          <div v-else-if="extractionSlides[extractionStep].type === 'authorizer'">
            <label>Title:</label>
            <input :value="extractionSlides[extractionStep].data.title" readonly />
            <label>Description:</label>
            <textarea :value="extractionSlides[extractionStep].data.description" readonly></textarea>
            <label>Created By:</label>
            <input :value="extractionSlides[extractionStep].data.createdBy" readonly />
            <label>Created date:</label>
            <input :value="extractionSlides[extractionStep].data.createdDate" readonly />
            <label>Authorized By:</label>
            <input :value="extractionSlides[extractionStep].data.authorizedBy" readonly />
            <label>Assign task for authorization:</label>
            <input :value="extractionSlides[extractionStep].data.assignTask" readonly />
          </div>
          <div style="text-align: right; margin-top: 24px">
            <button
              v-if="extractionStep < extractionSlides.length - 1"
              class="create-btn"
              style="min-width: 100px"
              @click="extractionStep = extractionStep + 1"
            >
              Next &gt;
            </button>
            <button
              v-else
              class="create-btn"
              style="min-width: 100px"
              @click="showExtractionScreens = false"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import frameworkSample from '../../data/frameworkSample.json'
import './CreateFramework.css'

export default {
  name: 'CreateFramework',
  setup() {
    const showExtractionScreens = ref(false)
    const extractionStep = ref(0)
    const extractionSlides = ref([])
    const formData = ref({
      frameworkId: '',
      frameworkName: '',
      version: '',
      document: null,
      effectiveStartDate: '',
      effectiveEndDate: '',
      createdBy: ''
    })

    const handleFileUpload = (event) => {
      formData.value.document = event.target.files[0]
    }

    const handleFrameworkFormSubmit = () => {
      // Build slides dynamically based on JSON structure
      const slides = []
      if (frameworkSample.framework) {
        slides.push({
          type: 'framework',
          data: frameworkSample.framework
        })
      }
      if (frameworkSample.policies && Array.isArray(frameworkSample.policies)) {
        frameworkSample.policies.forEach((policy, idx) => {
          slides.push({
            type: 'policy',
            data: policy,
            index: idx
          })
        })
      }
      if (frameworkSample.authorizer) {
        slides.push({
          type: 'authorizer',
          data: frameworkSample.authorizer
        })
      }
      extractionSlides.value = slides
      showExtractionScreens.value = true
      extractionStep.value = 0
    }

    return {
      showExtractionScreens,
      extractionStep,
      extractionSlides,
      formData,
      handleFileUpload,
      handleFrameworkFormSubmit
    }
  }
}
</script>

<style scoped>
.create-framework-container {
  margin-left: 230px;
  padding: 30px;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.framework-form-container {
  max-width: 600px;
  margin: 0 auto;
  background: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
}

h2 {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 32px;
  font-weight: 600;
  position: relative;
  padding-bottom: 12px;
}

h2:after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #3498db, #5165ff);
  border-radius: 3px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.form-group input, 
.form-group textarea {
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
  background-color: #f9f9f9;
  color: #333;
}

.form-group input:focus, 
.form-group textarea:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
  outline: none;
  background-color: #fff;
}

.form-group input[type="date"] {
  cursor: pointer;
  color: #333;
}

.upload-input-container {
  position: relative;
}

.file-input {
  position: absolute;
  width: 0.1px;
  height: 0.1px;
  opacity: 0;
  overflow: hidden;
  z-index: -1;
}

.upload-label {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  background: #f0f7ff;
  border: 1px dashed #3498db;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #3498db;
  font-weight: 500;
}

.upload-label:hover {
  background: #e1f0fe;
  border-color: #2980b9;
}

.upload-text::before {
  content: '';
  font-size: 16px;
  margin-right: 8px;
}

.create-btn {
  background: linear-gradient(90deg, #3498db, #5165ff);
  color: white;
  padding: 14px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  margin-top: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.2);
  width: auto;
  min-width: 120px;
  margin-left: auto;
  margin-right: auto;
  display: block;
}

.create-btn:hover {
  background: linear-gradient(90deg, #2980b9, #3f51b5);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(52, 152, 219, 0.3);
}

.create-btn:active {
  transform: translateY(1px);
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.2);
}

/* Extraction Content (Now Inline) */
.extraction-inline-container {
  margin: 24px auto;
  max-width: 1200px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  overflow: hidden;
}

.extraction-content {
  display: flex;
  flex-direction: column;
  min-height: 600px;
  max-height: 800px;
}

/* Update existing styles */
.extraction-header {
  position: sticky;
  top: 0;
  z-index: 10;
}

.extraction-body {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  background-color: #fcfcfc;
  background-image: linear-gradient(to bottom, #f7f9fc, #ffffff);
}

.extraction-stepper {
  display: flex;
  align-items: flex-end;
  border-bottom: 2px solid rgba(255, 255, 255, 0.3);
  background: none;
  margin: 0;
  padding: 0;
  position: relative;
  z-index: 2;
}

.extraction-step {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-bottom: none;
  border-radius: 8px 8px 0 0;
  font-size: 15px;
  font-weight: 500;
  color: white;
  padding: 12px 24px 10px 18px;
  margin-right: -2px;
  position: relative;
  z-index: 2;
  min-width: 120px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.extraction-step:hover {
  background: rgba(255, 255, 255, 0.3);
}

.extraction-step.active {
  background: white;
  color: #6a11cb;
  font-weight: 700;
  z-index: 3;
  border-bottom: 2px solid white;
}

.extraction-step .tab-close {
  font-size: 18px;
  font-weight: 400;
  margin-left: 10px;
  color: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.extraction-step .tab-close:hover {
  color: #ff4757;
  background-color: rgba(255, 255, 255, 0.2);
}

.policy-main {
  margin-bottom: 28px;
  padding: 24px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.04);
  border-left: 4px solid #2575fc;
}

.policy-main b {
  display: block;
  font-size: 20px;
  color: #2c3e50;
  margin-bottom: 20px;
  position: relative;
}

.subpolicies-group {
  display: flex;
  flex-direction: row;
  gap: 20px;
  align-items: flex-start;
  overflow-x: auto;
  padding: 12px 4px;
  justify-content: space-between;
  flex-wrap: wrap;
}

.extraction-subpolicy {
  background: linear-gradient(145deg, #ffffff, #f5f9ff);
  border: 1px solid rgba(214, 233, 255, 0.6);
  border-radius: 16px;
  padding: 24px 20px;
  min-width: 220px;
  max-width: 280px;
  width: 32%;
  font-size: 14px;
  box-shadow: 0 8px 16px rgba(42, 112, 219, 0.08);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.extraction-subpolicy:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(42, 112, 219, 0.12);
  border-color: #a9d2ff;
}

.extraction-subpolicy b {
  color: #2575fc;
  font-size: 18px;
  margin-bottom: 8px;
  display: block;
  text-align: center;
  position: relative;
  font-weight: 600;
}

.extraction-subpolicy b:after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, #6a11cb, #2575fc);
  border-radius: 3px;
}

.extraction-subpolicy label {
  color: #6a11cb;
  font-size: 13px;
  font-weight: 600;
  margin-top: 8px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
}

.extraction-subpolicy label:before {
  content: "•";
  color: #6a11cb;
  margin-right: 6px;
  font-size: 18px;
}

.extraction-subpolicy input,
.extraction-subpolicy textarea {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #d1e3fa;
  border-radius: 10px;
  font-size: 13px;
  padding: 10px 14px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(42, 112, 219, 0.04);
  margin-bottom: 8px;
  width: 100%;
  box-sizing: border-box;
}

.extraction-subpolicy input:focus,
.extraction-subpolicy textarea:focus {
  border-color: #6a11cb;
  box-shadow: 0 0 0 3px rgba(106, 17, 203, 0.08);
  background: #ffffff;
}

.extraction-subpolicy textarea {
  min-height: 100px;
  resize: none;
  width: 100%;
}

.extraction-body label {
  font-size: 13px;
  font-weight: 600;
  color: #6a11cb;
  margin-bottom: 4px;
  display: block;
}

.extraction-body input,
.extraction-body textarea {
  width: 100%;
  border: 1px solid #d6e9ff;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 14px;
  background: #fff;
  outline: none;
  margin-bottom: 16px;
  color: #333;
  transition: all 0.2s ease;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
}

.extraction-body input:focus,
.extraction-body textarea:focus {
  border-color: #6a11cb;
  box-shadow: 0 0 0 3px rgba(106, 17, 203, 0.1), inset 0 1px 3px rgba(0,0,0,0.03);
}

.extraction-body textarea {
  min-height: 70px;
  resize: vertical;
}

.extraction-body .create-btn {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  min-width: 120px;
  padding: 12px 24px;
  border-radius: 50px;
  margin-left: auto;
  font-size: 14px;
  width: auto;
  max-width: 150px;
}

.extraction-body .create-btn:hover {
  background: linear-gradient(135deg, #5e0fb5 0%, #1c68e3 100%);
  box-shadow: 0 8px 16px rgba(106, 17, 203, 0.2);
}

/* Custom scrollbar for better UX */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: #c1d9f0;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a9d2ff;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.form-group .input-icon {
  position: absolute;
  left: 12px;
  bottom: 8px;
  color: #3498db;
  font-size: 18px;
  z-index: 1;
  transition: color 0.2s ease;
}

.form-group input:focus + .input-icon,
.form-group textarea:focus + .input-icon {
  color: #2575fc;
}
</style> 