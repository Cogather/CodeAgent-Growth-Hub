<template>
  <div class="permission-manage">
    <el-card>
      <el-alert type="info" :closable="false" style="margin-bottom: 16px">
        输入工号后设置权限，将覆盖该人员已有的同区域权限
      </el-alert>
      <el-form :model="batchForm" label-width="120px">
        <el-form-item label="人员工号">
          <el-input v-model="batchForm.employeeNos" type="textarea" :rows="4" placeholder="请输入工号，多个用逗号或换行分隔" />
        </el-form-item>
        <el-form-item label="权限区域">
          <el-select v-model="batchForm.zone" placeholder="选择区域">
            <el-option label="蓝区" value="blue" />
            <el-option label="黄区" value="yellow" />
            <el-option label="绿区" value="green" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型权限">
          <el-input v-model="batchForm.modelPermission" placeholder="如: GPT-4, Claude-3" />
        </el-form-item>
        <el-form-item label="工具权限">
          <el-input v-model="batchForm.toolPermission" placeholder="如: CodeAgent, CodeReview" />
        </el-form-item>
        <el-form-item label="开通日期批次">
          <el-date-picker v-model="batchForm.batchDate" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitBatchConfig">批量配置</el-button>
          <el-button @click="resetBatchForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { usePersonnelStore } from '@/stores/personnel'
import type { ZoneType, PersonnelZone } from '@/types'
import { ElMessage } from 'element-plus'

const store = usePersonnelStore()

const batchForm = ref({
  employeeNos: '',
  zone: '' as ZoneType | '',
  modelPermission: '',
  toolPermission: '',
  batchDate: ''
})

const zoneLabel: Record<string, string> = {
  blue: '蓝区',
  yellow: '黄区',
  green: '绿区'
}

function submitBatchConfig() {
  if (!batchForm.value.employeeNos || !batchForm.value.zone || !batchForm.value.batchDate) {
    ElMessage.warning('请填写完整信息')
    return
  }

  const empNos = batchForm.value.employeeNos.split(/[,，\n]/).map(s => s.trim()).filter(s => s)
  if (empNos.length === 0) {
    ElMessage.warning('请输入至少一个工号')
    return
  }

  const zones: PersonnelZone[] = [{
    zone: batchForm.value.zone as ZoneType,
    modelPermission: batchForm.value.modelPermission,
    toolPermission: batchForm.value.toolPermission,
    batchDate: batchForm.value.batchDate
  }]

  const count = store.batchUpdatePermissions(empNos, zones)
  ElMessage.success(`成功配置 ${count} 人的${zoneLabel[batchForm.value.zone]}权限`)
  resetBatchForm()
}

function resetBatchForm() {
  batchForm.value = {
    employeeNos: '',
    zone: '',
    modelPermission: '',
    toolPermission: '',
    batchDate: ''
  }
}
</script>

<style scoped>
.permission-manage {
  padding: 20px;
}
</style>