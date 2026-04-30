<template>
  <div class="organization-manage">
    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="PDU管理" name="pdu">
        <div class="toolbar">
          <el-button type="primary" @click="openPduDialog()">新增PDU</el-button>
        </div>
        <el-table :data="store.pdus" border row-key="id" :tree-props="{ children: 'children' }">
          <el-table-column prop="name" label="PDU名称" />
          <el-table-column prop="pduContact" label="接口人" />
          <el-table-column prop="fseName" label="负责FSE">
            <template #default="{ row }">
              {{ getFseByPdu(row.id)?.name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" />
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="primary" link @click="openPduDialog(row)">编辑</el-button>
              <el-button type="success" link @click="openDevDeptDialog(row.id)">添加开发部</el-button>
              <el-button type="danger" link @click="store.deletePdu(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="开发部管理" name="devDept">
        <div class="toolbar">
          <el-select v-model="filterPduId" placeholder="选择PDU" clearable style="width: 200px; margin-right: 10px">
            <el-option v-for="p in store.pdus" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </div>
        <el-table :data="filteredDevDepts" border>
          <el-table-column prop="name" label="开发部名称" />
          <el-table-column prop="pduName" label="所属PDU">
            <template #default="{ row }">
              {{ getPduName(row.parentId) }}
            </template>
          </el-table-column>
          <el-table-column prop="devContact" label="接口人" />
          <el-table-column prop="createdAt" label="创建时间" />
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button type="primary" link @click="openDevDeptDialog(row.parentId, row)">编辑</el-button>
              <el-button type="danger" link @click="store.deleteDevDept(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="FSE管理" name="fse">
        <div class="toolbar">
          <el-button type="primary" @click="openFseDialog()">新增FSE</el-button>
        </div>
        <el-table :data="store.fses" border>
          <el-table-column prop="name" label="FSE名称" />
          <el-table-column prop="pduName" label="负责PDU" />
          <el-table-column prop="createdAt" label="创建时间" />
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button type="primary" link @click="openFseDialog(row)">编辑</el-button>
              <el-button type="danger" link @click="store.deleteFse(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="试验田管理" name="testField">
        <div class="toolbar">
          <el-button type="primary" @click="openTestFieldDialog()">新增试验田</el-button>
        </div>
        <el-table :data="store.testFields" border>
          <el-table-column prop="name" label="试验田名称" />
          <el-table-column prop="owner" label="Owner" />
          <el-table-column prop="responsible" label="责任人" />
          <el-table-column prop="createdAt" label="创建时间" />
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button type="primary" link @click="openTestFieldDialog(row)">编辑</el-button>
              <el-button type="danger" link @click="store.deleteTestField(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="pduDialogVisible" title="PDU" width="500px">
      <el-form :model="pduForm" label-width="100px">
        <el-form-item label="PDU名称">
          <el-input v-model="pduForm.name" />
        </el-form-item>
        <el-form-item label="接口人">
          <el-input v-model="pduForm.pduContact" />
        </el-form-item>
        <el-form-item label="负责FSE">
          <el-select v-model="pduForm.fseId" placeholder="选择FSE" clearable>
            <el-option v-for="f in store.fses" :key="f.id" :label="f.name" :value="f.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pduDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPdu">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="devDeptDialogVisible" title="开发部" width="500px">
      <el-form :model="devDeptForm" label-width="100px">
        <el-form-item label="所属PDU">
          <el-select v-model="devDeptForm.parentId" :disabled="!!currentPduId">
            <el-option v-for="p in store.pdus" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开发部名称">
          <el-input v-model="devDeptForm.name" />
        </el-form-item>
        <el-form-item label="接口人">
          <el-input v-model="devDeptForm.devContact" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="devDeptDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitDevDept">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="fseDialogVisible" title="FSE" width="500px">
      <el-form :model="fseForm" label-width="100px">
        <el-form-item label="FSE名称">
          <el-input v-model="fseForm.name" />
        </el-form-item>
        <el-form-item label="负责PDU">
          <el-select v-model="fseForm.pduId">
            <el-option v-for="p in store.pdus" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="fseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitFse">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="testFieldDialogVisible" title="试验田" width="500px">
      <el-form :model="testFieldForm" label-width="100px">
        <el-form-item label="试验田名称">
          <el-input v-model="testFieldForm.name" />
        </el-form-item>
        <el-form-item label="Owner">
          <el-input v-model="testFieldForm.owner" placeholder="负责人" />
        </el-form-item>
        <el-form-item label="责任人">
          <el-input v-model="testFieldForm.responsible" placeholder="责任人" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="testFieldDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTestField">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { usePersonnelStore } from '@/stores/personnel'
import type { OrganizationUnit, FSE } from '@/types'

const store = usePersonnelStore()
const activeTab = ref('pdu')
const filterPduId = ref<number | undefined>()

const pduDialogVisible = ref(false)
const pduForm = ref({ id: 0, name: '', pduContact: '', fseId: undefined as number | undefined })
const currentPduId = ref<number | undefined>()

const devDeptDialogVisible = ref(false)
const devDeptForm = ref({ id: 0, parentId: 0, name: '', devContact: '' })

const fseDialogVisible = ref(false)
const fseForm = ref({ id: 0, name: '', pduId: 0, pduName: '' })

const testFieldDialogVisible = ref(false)
const testFieldForm = ref({ id: 0, name: '', owner: '', responsible: '' })

const filteredDevDepts = computed(() => {
  if (!filterPduId.value) return store.devDepts
  return store.devDepts.filter(d => d.parentId === filterPduId.value)
})

function getPduName(pduId: number | null) {
  if (!pduId) return '-'
  return store.getPduById(pduId)?.name || '-'
}

function getFseByPdu(pduId: number) {
  return store.getFseByPduId(pduId)
}

function openPduDialog(row?: OrganizationUnit) {
  if (row) {
    const fse = store.getFseByPduId(row.id)
    pduForm.value = { id: row.id, name: row.name, pduContact: row.pduContact || '', fseId: fse?.id }
  } else {
    pduForm.value = { id: 0, name: '', pduContact: '', fseId: undefined }
  }
  pduDialogVisible.value = true
}

function submitPdu() {
  if (pduForm.value.id) {
    store.updatePdu(pduForm.value.id, { name: pduForm.value.name, pduContact: pduForm.value.pduContact })
    if (pduForm.value.fseId) {
      const fse = store.fses.find(f => f.id === pduForm.value.fseId)
      if (fse && fse.pduId !== pduForm.value.id) {
        store.updateFse(fse.id, { pduId: pduForm.value.id, pduName: pduForm.value.name })
      }
    }
  } else {
    store.addPdu({ name: pduForm.value.name, type: 'pdu', parentId: null, pduContact: pduForm.value.pduContact })
    if (pduForm.value.fseId) {
      const fse = store.fses.find(f => f.id === pduForm.value.fseId)
      if (fse) {
        const newPdu = store.pdus[store.pdus.length - 1]
        store.updateFse(fse.id, { pduId: newPdu.id, pduName: newPdu.name })
      }
    }
  }
  pduDialogVisible.value = false
}

function openDevDeptDialog(pduId: number, row?: OrganizationUnit) {
  currentPduId.value = row ? undefined : pduId
  if (row) {
    devDeptForm.value = { id: row.id, parentId: row.parentId || 0, name: row.name, devContact: row.devContact || '' }
  } else {
    devDeptForm.value = { id: 0, parentId: pduId, name: '', devContact: '' }
  }
  devDeptDialogVisible.value = true
}

function submitDevDept() {
  if (devDeptForm.value.id) {
    store.updateDevDept(devDeptForm.value.id, devDeptForm.value)
  } else {
    store.addDevDept({ name: devDeptForm.value.name, type: 'devDept', parentId: devDeptForm.value.parentId, devContact: devDeptForm.value.devContact })
  }
  devDeptDialogVisible.value = false
}

function openFseDialog(row?: FSE) {
  if (row) {
    fseForm.value = { ...row }
  } else {
    fseForm.value = { id: 0, name: '', pduId: 0, pduName: '' }
  }
  fseDialogVisible.value = true
}

function submitFse() {
  const pdu = store.pdus.find(p => p.id === fseForm.value.pduId)
  fseForm.value.pduName = pdu?.name || ''
  
  if (fseForm.value.id) {
    store.updateFse(fseForm.value.id, fseForm.value)
  } else {
    store.addFse(fseForm.value)
  }
  fseDialogVisible.value = false
}

function openTestFieldDialog(row?: OrganizationUnit) {
  if (row) {
    testFieldForm.value = { id: row.id, name: row.name, owner: row.owner || '', responsible: row.responsible || '' }
  } else {
    testFieldForm.value = { id: 0, name: '', owner: '', responsible: '' }
  }
  testFieldDialogVisible.value = true
}

function submitTestField() {
  if (testFieldForm.value.id) {
    store.updateTestField(testFieldForm.value.id, { 
      name: testFieldForm.value.name,
      owner: testFieldForm.value.owner,
      responsible: testFieldForm.value.responsible
    })
  } else {
    store.addTestField({ 
      name: testFieldForm.value.name, 
      type: 'testField', 
      parentId: null,
      owner: testFieldForm.value.owner,
      responsible: testFieldForm.value.responsible
    })
  }
  testFieldDialogVisible.value = false
}
</script>

<style scoped>
.organization-manage {
  padding: 20px;
}
.toolbar {
  margin-bottom: 16px;
}
</style>