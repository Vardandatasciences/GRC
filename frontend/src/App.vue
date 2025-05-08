<template>
  <div id="app">
    <Login v-if="!isLoggedIn" @login-success="handleLoginSuccess" />
    <LoginSuccess v-else @logout="handleLogout" />
  </div>
</template>

<script>
import Login from './components/Login.vue'
import LoginSuccess from './components/LoginSuccess.vue'

export default {
  name: 'App',
  components: {
    Login,
    LoginSuccess
  },
  data() {
    return {
      isLoggedIn: false
    }
  },
  created() {
    // Check if user is already logged in
    const user = localStorage.getItem('user');
    if (user) {
      this.isLoggedIn = true;
    }
  },
  methods: {
    handleLoginSuccess() {
      this.isLoggedIn = true;
    },
    handleLogout() {
      this.isLoggedIn = false;
    }
  }
}
</script>

<style>
body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
