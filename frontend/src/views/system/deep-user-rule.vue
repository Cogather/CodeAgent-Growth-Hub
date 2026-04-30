<template>
  <div class="system-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>深度用户规则配置</span>
        </div>
      </template>
      
      <el-form :model="rule" label-width="180px" style="max-width: 500px">
        <el-form-item label="统计周期（天）">
          <el-input-number v-model="rule.daysWindow" :min="1" :max="90" />
          <span class="form-tip">最近N天的统计数据</span>
        </el-form-item>
        <el-form-item label="调用量阈值">
          <el-input-number v-model="rule.callCountThreshold" :min="0" :step="100" />
          <span class="form-tip">达到此调用量才可能被判定为深度用户</span>
        </el-form-item>
        <el-form-item label="活跃天数阈值">
          <el-input-number v-model="rule.activeDaysThreshold" :min="1" :max="30" />
          <span class="form-tip">达到此活跃天数才可能被判定为深度用户</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveRule">保存配置</el-button>
        </el-form-item>
      </el-form>
      
      <el-divider />
      
      <div class="rule-preview">
        <h4>规则预览</h4>
        <p>用户满足以下条件时，将被标记为深度用户：</p>
        <ul>
          <li>最近 {{ rule.daysWindow }} 天调用量 ≥ {{ rule.callCountThreshold }}</li>
          <li>最近 {{ rule.daysWindow }} 天活跃天数 ≥ {{ rule.activeDaysThreshold }}</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useMockDataStore } from '@/stores/mockData'

const mockDataStore = useMockDataStore()

const rule = reactive({
  daysWindow: mockDataStore.deepUserRule.daysWindow,
  callCountThreshold: mockDataStore.deepUserRule.callCountThreshold,
  activeDaysThreshold: mockDataStore.deepUserRule.activeDaysThreshold
})

const saveRule = () => {
  Object.assign(mockDataStore.deepUserRule, rule)
  ElMessage.success('配置保存成功')
}
</script>

<style scoped>
.system-page {
  width: 100%;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}

.form-tip {
  margin-left: 12px;
  color: #909399;
  font-size: 12px;
}

.rule-preview {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.rule-preview h4 {
  margin-bottom: 12px;
}

.rule-preview ul {
  margin: 12px 0 0 20px;
}

.rule-preview li {
  margin: 8px 0;
  color: #606266;
}
</style>
