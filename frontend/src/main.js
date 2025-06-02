import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import '@fortawesome/fontawesome-free/css/all.min.css'
import Toast from "vue-toastification"
import "vue-toastification/dist/index.css"

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:8000'  // Django backend URL
axios.defaults.headers.common['Content-Type'] = 'application/json'

const app = createApp(App)

// Toast plugin options
const toastOptions = {
    position: "top-right",
    timeout: 3000,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: "button",
    icon: true,
    rtl: false
}

app.use(router)
app.use(Toast, toastOptions)
app.mount('#app')
