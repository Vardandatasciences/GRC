<template>
  <div class="success-container">
    <div class="success-card">
      <div class="success-icon">✓</div>
      <h2>Login Successful!</h2>
      <p>Welcome back, {{ user.name }}</p>
      <button @click="logout" class="logout-btn">Logout</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginSuccess',
  data() {
    return {
      user: {
        name: 'User',
        email: ''
      }
    }
  },
  created() {
    // Get user data from localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      this.user = JSON.parse(storedUser);
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('user');
      this.$emit('logout');
    }
  }
}
</script>

<style scoped>
.success-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.success-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 100%;
  max-width: 400px;
}

.success-icon {
  font-size: 3rem;
  color: #4caf50;
  background-color: rgba(76, 175, 80, 0.1);
  height: 80px;
  width: 80px;
  line-height: 80px;
  border-radius: 50%;
  margin: 0 auto 1.5rem;
}

h2 {
  margin-bottom: 1rem;
  color: #333;
}

p {
  margin-bottom: 1.5rem;
  color: #666;
}

.logout-btn {
  padding: 0.75rem 1.5rem;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.logout-btn:hover {
  background-color: #d32f2f;
}
</style> 