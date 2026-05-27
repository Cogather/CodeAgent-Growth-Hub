<template>
  <div class="table-row-count" role="status">
    <template v-if="isFiltered">
      共 <span class="count-num">{{ display }}</span> {{ unit }}
      <span class="count-sub">（已筛选，总计 {{ total }} {{ unit }}）</span>
    </template>
    <template v-else>
      共 <span class="count-num">{{ total }}</span> {{ unit }}
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    total: number
    display: number
    unit?: string
  }>(),
  { unit: '人' }
)

const isFiltered = computed(() => props.display !== props.total)
</script>

<style scoped>
.table-row-count {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
  text-align: right;
}

.count-num {
  font-weight: 600;
  color: #374151;
  font-variant-numeric: tabular-nums;
}

.count-sub {
  color: #9ca3af;
  margin-left: 2px;
}
</style>
