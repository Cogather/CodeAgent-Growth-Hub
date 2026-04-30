<template>
  <div class="summary-view">
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-label">总人数</div>
            <div class="stat-value">{{ summary.totalPersonnel }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-label">有权限人数</div>
            <div class="stat-value">{{ summary.hasPermissionCount }}</div>
            <div class="stat-rate">{{ permissionRate }}%</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-label">使用过人数</div>
            <div class="stat-value">{{ summary.usedCount }}</div>
            <div class="stat-rate">{{ usedRate }}%</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-label">TOP用户</div>
            <div class="stat-value">{{ summary.topUserCount }}</div>
            <div class="stat-rate">{{ topUserRate }}%</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-tabs v-model="activeTab" style="margin-top: 20px">
      <el-tab-pane label="按PDU统计" name="pdu">
        <el-table :data="summary.byPdu" border>
          <el-table-column prop="pduName" label="PDU" />
          <el-table-column prop="total" label="总人数" />
          <el-table-column prop="hasPermission" label="有权限" />
          <el-table-column label="权限占比">
            <template #default="{ row }">
              {{ row.total > 0 ? ((row.hasPermission / row.total) * 100).toFixed(1) : 0 }}%
            </template>
          </el-table-column>
          <el-table-column prop="used" label="使用过" />
          <el-table-column label="使用占比">
            <template #default="{ row }">
              {{ row.total > 0 ? ((row.used / row.total) * 100).toFixed(1) : 0 }}%
            </template>
          </el-table-column>
          <el-table-column prop="top" label="TOP用户" />
          <el-table-column prop="senior" label="资深用户" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="按开发部统计" name="devDept">
        <el-table :data="summary.byDevDept" border>
          <el-table-column prop="devDeptName" label="开发部" />
          <el-table-column prop="total" label="总人数" />
          <el-table-column prop="hasPermission" label="有权限" />
          <el-table-column label="权限占比">
            <template #default="{ row }">
              {{ row.total > 0 ? ((row.hasPermission / row.total) * 100).toFixed(1) : 0 }}%
            </template>
          </el-table-column>
          <el-table-column prop="used" label="使用过" />
          <el-table-column label="使用占比">
            <template #default="{ row }">
              {{ row.total > 0 ? ((row.used / row.total) * 100).toFixed(1) : 0 }}%
            </template>
          </el-table-column>
          <el-table-column prop="top" label="TOP用户" />
          <el-table-column prop="senior" label="资深用户" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="按试验田统计" name="testField">
        <el-table :data="summary.byTestField" border>
          <el-table-column prop="testFieldName" label="试验田" />
          <el-table-column prop="total" label="总人数" />
          <el-table-column prop="hasPermission" label="有权限" />
          <el-table-column label="权限占比">
            <template #default="{ row }">
              {{ row.total > 0 ? ((row.hasPermission / row.total) * 100).toFixed(1) : 0 }}%
            </template>
          </el-table-column>
          <el-table-column prop="used" label="使用过" />
          <el-table-column label="使用占比">
            <template #default="{ row }">
              {{ row.total > 0 ? ((row.used / row.total) * 100).toFixed(1) : 0 }}%
            </template>
          </el-table-column>
          <el-table-column prop="top" label="TOP用户" />
          <el-table-column prop="senior" label="资深用户" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { usePersonnelStore } from '@/stores/personnel'

const store = usePersonnelStore()
const activeTab = ref('pdu')

const summary = computed(() => store.getUsageSummary())

const permissionRate = computed(() => {
  if (summary.value.totalPersonnel === 0) return 0
  return ((summary.value.hasPermissionCount / summary.value.totalPersonnel) * 100).toFixed(1)
})

const usedRate = computed(() => {
  if (summary.value.totalPersonnel === 0) return 0
  return ((summary.value.usedCount / summary.value.totalPersonnel) * 100).toFixed(1)
})

const topUserRate = computed(() => {
  if (summary.value.totalPersonnel === 0) return 0
  return ((summary.value.topUserCount / summary.value.totalPersonnel) * 100).toFixed(1)
})
</script>

<style scoped>
.summary-view {
  padding: 20px;
}
.stats-cards {
  margin-bottom: 20px;
}
.stat-item {
  text-align: center;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}
.stat-rate {
  font-size: 12px;
  color: #67c23a;
  margin-top: 4px;
}
</style>