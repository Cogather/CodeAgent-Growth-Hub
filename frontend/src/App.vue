<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>

<script setup lang="ts">
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  min-height: 100vh;
  background-color: #f8f9fc;
}

body {
  min-height: 100vh;
  background-color: #f8f9fc;
}

:root {
  --el-color-primary: #6366f1;
  --el-color-primary-light-3: #818cf8;
  --el-color-primary-light-5: #a5b4fc;
  --el-color-primary-light-7: #c7d2fe;
  --el-color-primary-light-9: #e0e7ff;
  --el-color-primary-dark-2: #4f46e5;
  --hub-sidebar-bg: #f5f7fa;
  --hub-header-bg: #ffffff;
  --hub-page-bg: #f8f9fc;
}

.el-button--primary {
  --el-button-bg-color: #6366f1;
  --el-button-border-color: #6366f1;
  --el-button-hover-bg-color: #818cf8;
  --el-button-hover-border-color: #818cf8;
  --el-button-active-bg-color: #4f46e5;
  --el-button-active-border-color: #4f46e5;
}

.el-card {
  border-radius: 12px;
  border: 1px solid #ebeef5;
}

.el-dialog {
  border-radius: 12px;
}
</style>
