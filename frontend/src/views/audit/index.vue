<template>
  <ModulePlaceholder
    title="变更记录"
    description="查看各模块的历史修改记录与操作审计，支持按模块、操作人、时间范围筛选。"
    icon="Document"
    status="planned"
    hint="请在 src/views/audit/index.vue 中实现。建议对接后端 audit_log 表，或与各模块统一的变更事件总线。"
  />
</template>

<script setup lang="ts">
import ModulePlaceholder from '@/components/ModulePlaceholder.vue'
</script>
