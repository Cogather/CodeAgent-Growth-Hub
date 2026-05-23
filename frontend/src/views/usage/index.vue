<template>
  <ModulePlaceholder
    title="使用统计"
    description="晾晒 CodeAgent 用户使用数据，包括活跃度、功能使用分布、部门对比等统计视图。"
    icon="DataLine"
    status="planned"
    hint="请在 src/views/usage/index.vue 中实现。建议引入 ECharts 做图表展示，数据从 CodeAgent 使用数据 API 拉取。"
  />
</template>

<script setup lang="ts">
import ModulePlaceholder from '@/components/ModulePlaceholder.vue'
</script>
