<template>
  <div class="audit-logs">
    <el-table :data="store.auditLogs" border>
      <el-table-column prop="createdAt" label="时间" width="180" />
      <el-table-column prop="action" label="操作" width="100" />
      <el-table-column prop="operatorName" label="操作人" width="100" />
      <el-table-column prop="target" label="对象" />
      <el-table-column prop="detail" label="详情" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { usePersonnelStore } from '@/stores/personnel'

const store = usePersonnelStore()
</script>

<style scoped>
.audit-logs {
  padding: 20px;
}
</style>