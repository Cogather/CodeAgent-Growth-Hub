<template>
  <div class="usage-data">
    <div class="toolbar">
      <el-button type="primary" @click="showImportDialog = true">导入使用数据</el-button>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        :max-date="new Date()"
        :clearable="false"
        style="margin-left: 20px"
      />
      <el-select v-model="filterPduId" placeholder="筛选PDU" clearable style="margin-left: 20px; width: 150px">
        <el-option v-for="p in store.pdus" :key="p.id" :label="p.name" :value="p.id" />
      </el-select>
      <el-select v-model="filterDevDeptId" placeholder="筛选开发部" clearable style="margin-left: 10px; width: 150px">
        <el-option v-for="d in availableDevDepts" :key="d.id" :label="d.name" :value="d.id" />
      </el-select>
      <el-select v-model="filterTestFieldId" placeholder="筛选试验田" clearable style="margin-left: 10px; width: 150px">
        <el-option v-for="t in store.testFields" :key="t.id" :label="t.name" :value="t.id" />
      </el-select>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>人员使用明细 ({{ displayDates.length }}天)</span>
          <span class="date-range">{{ dateRangeText }}</span>
        </div>
      </template>
      <div v-if="filteredPersonnel.length > 0" class="usage-table-wrapper">
        <table class="usage-matrix">
          <thead>
            <tr>
              <th class="sticky-col">工号</th>
              <th class="sticky-col">姓名</th>
              <th class="sticky-col">PDU</th>
              <th class="sticky-col">开发部</th>
              <th class="sticky-col">试验田</th>
              <th class="sticky-col">PDU接口人</th>
              <th class="sticky-col">FSE</th>
              <th class="sticky-col">开通权限日期</th>
              <th v-for="date in displayDates" :key="date" class="date-col">{{ date }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="person in usageMatrix" :key="person.id">
              <td class="sticky-col">{{ person.employeeNo }}</td>
              <td class="sticky-col">{{ person.name }}</td>
              <td class="sticky-col">{{ person.pduName || '-' }}</td>
              <td class="sticky-col">{{ person.devDeptName || '-' }}</td>
              <td class="sticky-col">{{ person.testFieldName || '-' }}</td>
              <td class="sticky-col">{{ person.pduContact || '-' }}</td>
              <td class="sticky-col">{{ person.fse || '-' }}</td>
              <td class="sticky-col">{{ getFirstBatchDate(person) }}</td>
              <td v-for="date in displayDates" :key="date" class="date-col" :class="getCellClass(person, date)">
                {{ getCellValue(person, date) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <el-empty v-else description="暂无人员数据，请先在人员名单中添加" />
    </el-card>

    <el-dialog v-model="showImportDialog" title="导入使用数据" width="600px">
      <el-alert type="info" :closable="false" style="margin-bottom: 16px">
        请上传CSV文件，格式：工号,日期,调用次数,是否使用codeagent(是/否)
      </el-alert>
      <el-upload ref="uploadRef" :auto-upload="false" :limit="1" accept=".csv" :on-change="handleFileChange">
        <el-button type="primary">选择文件</el-button>
      </el-upload>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleImport">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { usePersonnelStore } from '@/stores/personnel'
import type { DailyUsage, Personnel } from '@/types'
import { ElMessage } from 'element-plus'

const store = usePersonnelStore()
const showImportDialog = ref(false)
const importData = ref<any[]>([])

const filterPduId = ref<number | undefined>()
const filterDevDeptId = ref<number | undefined>()
const filterTestFieldId = ref<number | undefined>()

const today = new Date()
const defaultStart = new Date(today.getTime() - 14 * 24 * 60 * 60 * 1000)
const dateRange = ref<[Date, Date]>([defaultStart, today])

const dateRangeText = computed(() => {
  const start = dateRange.value[0]
  const end = dateRange.value[1]
  return `${start.toLocaleDateString()} ~ ${end.toLocaleDateString()}`
})

const displayDates = computed(() => {
  const start = dateRange.value[0]
  const end = dateRange.value[1]
  const days = Math.min(15, Math.ceil((end.getTime() - start.getTime()) / (24 * 60 * 60 * 1000)) + 1)
  const dates: string[] = []
  for (let i = 0; i < days; i++) {
    const d = new Date(start.getTime() + i * 24 * 60 * 60 * 1000)
    dates.push(d.toISOString().split('T')[0])
  }
  return dates
})

const availableDevDepts = computed(() => {
  if (!filterPduId.value) return store.devDepts
  return store.getDevDeptsByPdu(filterPduId.value)
})

watch(filterPduId, () => {
  filterDevDeptId.value = undefined
})

const filteredPersonnel = computed(() => {
  return store.personnelList.filter(person => {
    if (filterPduId.value && person.pduId !== filterPduId.value) return false
    if (filterDevDeptId.value && person.devDeptId !== filterDevDeptId.value) return false
    if (filterTestFieldId.value && person.testFieldId !== filterTestFieldId.value) return false
    return true
  })
})

const usageMatrix = computed(() => {
  return filteredPersonnel.value.map(person => {
    const usages = store.dailyUsage.filter(u => u.personnelId === person.id)
    return {
      ...person,
      usageMap: new Map(usages.map(u => [u.date, u]))
    }
  })
})

function getFirstBatchDate(person: Personnel): string {
  if (!person.zones || person.zones.length === 0) return '-'
  const sorted = [...person.zones].sort((a, b) => a.batchDate.localeCompare(b.batchDate))
  return sorted[0]?.batchDate || '-'
}

function getCellValue(person: any, date: string) {
  const usage = person.usageMap.get(date)
  return usage ? usage.callCount : '-'
}

function getCellClass(person: any, date: string) {
  const usage = person.usageMap.get(date)
  if (!usage) return ''
  if (usage.callCount >= 100) return 'high-usage'
  if (usage.callCount > 0) return 'has-usage'
  return ''
}

function handleFileChange(file: any) {
  const reader = new FileReader()
  reader.onload = (e) => {
    const text = e.target?.result as string
    const lines = text.split('\n').filter(l => l.trim())
    const headers = lines[0].split(',').map(h => h.trim())
    importData.value = lines.slice(1).map(line => {
      const values = line.split(',').map(v => v.trim())
      const obj: any = {}
      headers.forEach((h, i) => {
        obj[h] = values[i]
      })
      return obj
    })
  }
  reader.readAsText(file.raw)
}

function handleImport() {
  if (importData.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }

  const usageList: Omit<DailyUsage, 'id'>[] = []
  importData.value.forEach(item => {
    const person = store.personnelList.find(p => p.employeeNo === item['工号'])
    if (person) {
      usageList.push({
        personnelId: person.id,
        employeeNo: item['工号'],
        name: person.name,
        date: item['日期'],
        callCount: parseInt(item['调用次数']) || 0,
        usedCodeAgent: item['是否使用codeagent'] === '是'
      })
    }
  })

  store.addDailyUsage(usageList)
  showImportDialog.value = false
  importData.value = []
  ElMessage.success('导入成功')
}
</script>

<style scoped>
.usage-data {
  padding: 20px;
}
.toolbar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.date-range {
  font-size: 12px;
  color: #909399;
}
.usage-table-wrapper {
  overflow-x: auto;
  max-height: 600px;
  overflow-y: auto;
}
.usage-matrix {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.usage-matrix th,
.usage-matrix td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
  white-space: nowrap;
}
.usage-matrix th {
  background: #f5f7fa;
  position: sticky;
  top: 0;
  z-index: 2;
}
.sticky-col {
  position: sticky;
  left: 0;
  background: #fff;
  z-index: 1;
  min-width: 80px;
}
.usage-matrix thead th.sticky-col {
  z-index: 3;
}
.date-col {
  min-width: 60px;
}
.high-usage {
  background: #f56c6c;
  color: #fff;
}
.has-usage {
  background: #e6a23c;
  color: #fff;
}
</style>