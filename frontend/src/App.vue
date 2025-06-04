<template>
  <div id="app">
    <div class="app-container">
      <Sidebar />
      <div class="main-content">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script>
import Sidebar from './components/Policy/Sidebar.vue'

export default {
  name: 'App',
  components: {
    Sidebar
  }
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow-x: hidden;
  font-family: Arial, Helvetica, sans-serif;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100%;
}

.app-container {
  display: flex;
  min-height: 100vh;
  overflow-y: auto; /* Single scrollbar for the entire app */
  overflow-x: hidden;
}

.main-content {
  flex: 1;
  padding: 20px;
  background-color: #f5f5f5;
  overflow: hidden; /* Prevent additional scrollbars */
}
</style>
