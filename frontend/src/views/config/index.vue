<template>
  <div class="config-page">
    <div class="page-header">
      <div>
        <h1>配置中心</h1>
        <p>管理 CodeAgent 运营元数据、人员与网络区域权限</p>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="config-tabs">
      <el-tab-pane label="组织架构" name="departments">
        <DepartmentTree />
      </el-tab-pane>
      <el-tab-pane label="人员名单" name="personnel">
        <PersonnelList />
      </el-tab-pane>
      <el-tab-pane label="黄区白名单" name="zone-yellow">
        <ZonePermissionPanel zone="yellow" />
      </el-tab-pane>
      <el-tab-pane label="蓝区白名单" name="zone-blue">
        <ZonePermissionPanel zone="blue" />
      </el-tab-pane>
      <el-tab-pane label="绿区白名单" name="zone-green">
        <ZonePermissionPanel zone="green" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DepartmentTree from './components/DepartmentTree.vue'
import PersonnelList from './components/PersonnelList.vue'
import ZonePermissionPanel from './components/ZonePermissionPanel.vue'

const activeTab = ref('departments')
</script>

<style scoped>
.config-page {
  max-width: 100%;
}

.page-header {
  margin-bottom: 8px;
}

.page-header h1 {
  font-size: 22px;
  color: #1f2937;
  margin-bottom: 4px;
}

.page-header p {
  font-size: 14px;
  color: #9ca3af;
}

.config-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}
</style>
