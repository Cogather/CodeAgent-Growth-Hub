<template>
  <div class="personnel-view">
    <el-card>
      <div class="toolbar">
        <el-button type="primary" @click="openPersonDialog()">新增人员</el-button>
        <el-button type="success" @click="showImportDialog = true">批量导入</el-button>
        <el-button type="info" @click="handleExport">导出</el-button>
        
        <el-select v-model="filterPduId" placeholder="筛选PDU" clearable style="margin-left: 20px; width: 150px">
          <el-option v-for="p in store.pdus" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        
        <el-select v-model="filterDevDeptId" placeholder="筛选开发部" clearable style="margin-left: 10px; width: 150px">
          <el-option v-for="d in availableDevDepts" :key="d.id" :label="d.name" :value="d.id" />
        </el-select>
        
        <el-select v-model="filterTestFieldId" placeholder="筛选试验田" clearable style="margin-left: 10px; width: 150px">
          <el-option v-for="t in store.testFields" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>

        <el-checkbox-group v-model="permissionFilters" style="margin-left: 10px">
          <el-checkbox-button label="hasPermission">有权限</el-checkbox-button>
          <el-checkbox-button label="noPermission">无权限</el-checkbox-button>
        </el-checkbox-group>
      </div>

      <el-table :data="filteredPersonnel" border>
        <el-table-column prop="employeeNo" label="工号" width="100" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="isTestField" label="试验田" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.testFieldId" type="success" size="small">是</el-tag>
            <el-tag v-else type="info" size="small" effect="plain">否</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pduName" label="PDU" />
        <el-table-column prop="devDeptName" label="开发部" />
        <el-table-column prop="testFieldName" label="试验田" />
        <el-table-column prop="pduContact" label="PDU接口人" />
        <el-table-column prop="devContact" label="开发部接口人" />
        <el-table-column prop="fse" label="FSE" />
        <el-table-column label="权限区域" min-width="180">
          <template #default="{ row }">
            <div v-if="row.zones && row.zones.length > 0">
              <el-tag v-for="zone in row.zones" :key="zone.zone" size="small" :type="zoneType[zone.zone as ZoneType]" style="margin-right: 4px; margin-bottom: 2px">
                {{ zoneLabel[zone.zone as ZoneType] }}
              </el-tag>
            </div>
            <span v-else class="no-permission">未开通</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" link @click="openPersonDialog(row)">编辑</el-button>
            <el-button type="danger" link @click="store.deletePersonnel(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="personDialogVisible" :title="personDialogTitle" width="650px">
      <el-form :model="personForm" label-width="100px">
        <el-form-item label="工号">
          <el-input v-model="personForm.employeeNo" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="personForm.name" />
        </el-form-item>
        
        <el-form-item label="PDU">
          <el-select v-model="personForm.pduId" @change="onPduChange">
            <el-option v-for="p in store.pdus" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开发部">
          <el-select v-model="personForm.devDeptId">
            <el-option v-for="d in availableDevDeptsForm" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="PDU接口人">
          <el-input v-model="personForm.pduContact" />
        </el-form-item>
        <el-form-item label="开发部接口人">
          <el-input v-model="personForm.devContact" />
        </el-form-item>
        
        <el-form-item label="试验田">
          <el-select v-model="personForm.testFieldId" placeholder="可选，不选则为普通先锋人员" clearable>
            <el-option v-for="t in store.testFields" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="personForm.testFieldId" label="FSE">
          <el-input v-model="personForm.fse" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="personDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPerson">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showImportDialog" title="批量导入" width="600px">
      <el-alert type="info" :closable="false" style="margin-bottom: 16px">
        格式：工号,姓名,PDU,开发部,PDU接口人,开发部接口人,试验田(可选),FSE(可选)
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
import type { Personnel, ZoneType, PersonnelZone } from '@/types'
import { ElMessage } from 'element-plus'

const store = usePersonnelStore()

const filterPduId = ref<number | undefined>()
const filterDevDeptId = ref<number | undefined>()
const filterTestFieldId = ref<number | undefined>()
const permissionFilters = ref<string[]>([])

const personDialogVisible = ref(false)
const personForm = ref({
  id: 0,
  employeeNo: '',
  name: '',
  pduId: undefined as number | undefined,
  pduName: '',
  devDeptId: undefined as number | undefined,
  devDeptName: '',
  testFieldId: undefined as number | undefined,
  testFieldName: '',
  pduContact: '',
  devContact: '',
  fse: '',
  zones: [] as PersonnelZone[]
})

const showImportDialog = ref(false)
const importData = ref<any[]>([])

const zoneType: Record<ZoneType, string> = {
  blue: 'info',
  yellow: 'warning',
  green: 'success'
}

const zoneLabel: Record<ZoneType, string> = {
  blue: '蓝区',
  yellow: '黄区',
  green: '绿区'
}

const availableDevDepts = computed(() => {
  if (!filterPduId.value) return store.devDepts
  return store.getDevDeptsByPdu(filterPduId.value)
})

const availableDevDeptsForm = computed(() => {
  if (!personForm.value.pduId) return store.devDepts
  return store.getDevDeptsByPdu(personForm.value.pduId)
})

watch(filterPduId, () => {
  filterDevDeptId.value = undefined
})

const filteredPersonnel = computed(() => {
  return store.personnelList.filter(person => {
    if (filterPduId.value && person.pduId !== filterPduId.value) return false
    if (filterDevDeptId.value && person.devDeptId !== filterDevDeptId.value) return false
    if (filterTestFieldId.value && person.testFieldId !== filterTestFieldId.value) return false
    
    const hasPerm = person.zones && person.zones.length > 0
    if (permissionFilters.value.includes('hasPermission') && !hasPerm) return false
    if (permissionFilters.value.includes('noPermission') && hasPerm) return false
    
    return true
  })
})

const personDialogTitle = computed(() => {
  return personForm.value.id ? '编辑人员' : '新增人员'
})

function openPersonDialog(person?: Personnel) {
  if (person) {
    personForm.value = {
      id: person.id,
      employeeNo: person.employeeNo,
      name: person.name,
      pduId: person.pduId,
      pduName: person.pduName || '',
      devDeptId: person.devDeptId,
      devDeptName: person.devDeptName || '',
      testFieldId: person.testFieldId,
      testFieldName: person.testFieldName || '',
      pduContact: person.pduContact || '',
      devContact: person.devContact || '',
      fse: person.fse || '',
      zones: [...(person.zones || [])]
    }
  } else {
    personForm.value = {
      id: 0,
      employeeNo: '',
      name: '',
      pduId: undefined,
      pduName: '',
      devDeptId: undefined,
      devDeptName: '',
      testFieldId: undefined,
      testFieldName: '',
      pduContact: '',
      devContact: '',
      fse: '',
      zones: []
    }
  }
  personDialogVisible.value = true
}

function onPduChange() {
  const pdu = store.pdus.find(p => p.id === personForm.value.pduId)
  if (pdu) {
    personForm.value.pduName = pdu.name
    personForm.value.pduContact = pdu.pduContact || ''
    const fse = store.getFseByPduId(pdu.id)
    if (fse && !personForm.value.testFieldId) {
      personForm.value.fse = fse.name
    }
  }
  personForm.value.devDeptId = undefined
  personForm.value.devDeptName = ''
}

function submitPerson() {
  if (!personForm.value.employeeNo || !personForm.value.name) {
    ElMessage.warning('请填写工号和姓名')
    return
  }

  if (!personForm.value.pduId || !personForm.value.devDeptId) {
    ElMessage.warning('请选择PDU和开发部')
    return
  }

  const dept = store.getDevDeptById(personForm.value.devDeptId)
  personForm.value.devDeptName = dept?.name || ''

  if (personForm.value.testFieldId) {
    const tf = store.getTestFieldById(personForm.value.testFieldId)
    personForm.value.testFieldName = tf?.name || ''
  } else {
    personForm.value.testFieldName = ''
    personForm.value.fse = ''
  }

  const data = {
    employeeNo: personForm.value.employeeNo,
    name: personForm.value.name,
    pduId: personForm.value.pduId!,
    pduName: personForm.value.pduName,
    devDeptId: personForm.value.devDeptId!,
    devDeptName: personForm.value.devDeptName,
    testFieldId: personForm.value.testFieldId || undefined,
    testFieldName: personForm.value.testFieldName || undefined,
    pduContact: personForm.value.pduContact,
    devContact: personForm.value.devContact,
    fse: personForm.value.fse,
    zones: personForm.value.zones
  }

  if (personForm.value.id) {
    store.updatePersonnel(personForm.value.id, data)
    ElMessage.success('更新成功')
  } else {
    store.addPersonnel(data)
    ElMessage.success('添加成功')
  }
  personDialogVisible.value = false
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
      headers.forEach((h, i) => { obj[h] = values[i] })
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

  const persons = importData.value.map(item => {
    const pdu = store.pdus.find(p => p.name === item['PDU'])
    const dept = store.devDepts.find(d => d.name === item['开发部'] && d.parentId === pdu?.id)
    const tf = item['试验田'] ? store.testFields.find(t => t.name === item['试验田']) : null
    
    return {
      employeeNo: item['工号'],
      name: item['姓名'],
      pduId: pdu?.id,
      pduName: item['PDU'],
      devDeptId: dept?.id,
      devDeptName: item['开发部'],
      testFieldId: tf?.id,
      testFieldName: item['试验田'] || '',
      pduContact: item['PDU接口人'],
      devContact: item['开发部接口人'],
      fse: item['FSE'],
      zones: [] as PersonnelZone[]
    }
  })

  store.batchImportPersonnel(persons as any)
  showImportDialog.value = false
  importData.value = []
  ElMessage.success(`导入成功，共${persons.length}人`)
}

function handleExport() {
  const headers = ['工号', '姓名', '试验田', 'PDU', '开发部', '试验田', 'PDU接口人', '开发部接口人', 'FSE', '权限区域']
  const rows = filteredPersonnel.value.map(p => [
    p.employeeNo,
    p.name,
    p.testFieldId ? '是' : '否',
    p.pduName || '-',
    p.devDeptName || '-',
    p.testFieldName || '-',
    p.pduContact || '-',
    p.devContact || '-',
    p.fse || '-',
    p.zones?.map(z => zoneLabel[z.zone as ZoneType]).join(',') || '未开通'
  ])
  
  const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n')
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `人员名单_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
}
</script>

<style scoped>
.personnel-view {
  padding: 20px;
}
.toolbar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.no-permission {
  color: #909399;
  font-size: 12px;
}
</style>