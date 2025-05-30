import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import '@fortawesome/fontawesome-free/css/all.css'
import axios from 'axios'
 
// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:8000'
 
const app = createApp(App)
 
// Configure Vue app
app.config.compilerOptions.isCustomElement = tag => tag.includes('-')
app.config.performance = true
app.config.warnHandler = () => null // Suppress hydration mismatch warnings in production
 
app.use(router)
app.mount('#app')
 
 