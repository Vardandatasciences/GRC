import axios from 'axios'

// Create axios instance with base URL pointing to Django backend
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Add response interceptor for debugging
api.interceptors.response.use(
  response => {
    console.log(`API Response from ${response.config.url}:`, response.status);
    return response;
  },
  error => {
    console.error('API Error:', error.response ? error.response.status : error.message);
    return Promise.reject(error);
  }
);

export default api 