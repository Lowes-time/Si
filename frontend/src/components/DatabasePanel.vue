<!--
  软件名称：基于多光束干涉校正的半导体外延层厚度光谱反演系统 V1.0
  组件功能：历史记录管理面板
  描述：历史记录查询、删除、重测、报告打印功能
-->
<template>
  <div class="database-container">
    <div class="table-toolbar">
      <div class="toolbar-left">
        <el-input v-model="searchQuery" placeholder="搜索薄膜编号..." prefix-icon="Search" clearable @clear="loadData" @keyup.enter="loadData" class="search-input" />
        <el-button type="primary" @click="loadData">查询</el-button>
      </div>
      <div class="toolbar-right">
        <el-button icon="Refresh" @click="loadData">刷新</el-button>
      </div>
    </div>

    <el-table v-loading="loading" :data="records" border stripe style="width: 100%" class="data-table" header-cell-class-name="table-header">
      <el-table-column prop="id" label="ID" width="80" align="center" />
      <el-table-column prop="film_code" label="薄膜编号" min-width="180" show-overflow-tooltip />
      <el-table-column prop="material_type" label="材质" width="100" align="center">
        <template #default="{ row }">
          <el-tag size="small">{{ row.material_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="厚度 (μm)" width="120" align="right">
        <template #default="{ row }">
          <span class="thickness-val">{{ row.thickness_um ? row.thickness_um.toFixed(4) : '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="拟合优度 R²" width="120" align="right">
        <template #default="{ row }">
          <span :class="getR2Class(row.r_squared)">{{ row.r_squared ? row.r_squared.toFixed(4) : '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="multi_beam_level" label="干涉等级" width="140" align="center">
        <template #default="{ row }">
          <span class="interference-level">{{ row.multi_beam_level || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="170" align="center">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right" align="center">
        <template #default="{ row }">
          <el-button link type="primary" icon="RefreshLeft" @click="handleRetest(row)">重测</el-button>
          <el-button link type="primary" icon="Printer" @click="openPrintPreview(row)">报告</el-button>
          <el-popconfirm title="确定要删除这条记录吗？" confirm-button-text="确定" cancel-button-text="取消" @confirm="handleDelete(row)">
            <template #reference>
              <el-button link type="danger" icon="Delete">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="loadData" @current-change="loadData" />
    </div>

    <el-dialog v-model="printVisible" title="报告打印预览" width="900px" class="print-dialog" append-to-body destroy-on-close>
      <div class="print-actions">
        <el-button type="primary" icon="Printer" @click="handlePrint">打印 / 另存为 PDF</el-button>
      </div>
      <div class="print-content" id="printable-report">
        <ReportTemplate :record="selectedRecord" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { Search, Refresh, Delete, RefreshLeft, Printer } from "@element-plus/icons-vue";
import { fetchRecords, deleteRecord, fetchRecordDetail } from "../api/index.js";
import { ElMessage } from "element-plus";
import ReportTemplate from "./ReportTemplate.vue";

const emit = defineEmits(["retest"]);

const records = ref([]);
const loading = ref(false);
const searchQuery = ref("");
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const printVisible = ref(false);
const selectedRecord = ref(null);

const loadData = async () => {
  loading.value = true;
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchQuery.value || undefined
    };
    const res = await fetchRecords(params);
    // 兼容两种响应格式：直接返回数组 或 {data: [], total: n}
    records.value = Array.isArray(res.data) ? res.data : (res.data.data || []);
    total.value = Array.isArray(res.data) ? res.data.length : (res.data.total || records.value.length);
  } catch (e) {
    ElMessage.error("获取记录失败: " + e.message);
  } finally {
    loading.value = false;
  }
};

const handleRetest = async (row) => {
  loading.value = true;
  try {
    const res = await fetchRecordDetail(row.id);
    const fullData = res.data;
    const rawDataProxy = {
      film_code: fullData.film_code,
      row_count: fullData.data.wavelength.length,
      wavelength: [...fullData.data.wavelength],
      reflectance: [...fullData.data.reflectance],
      wl_min: Math.min(...fullData.data.wavelength),
      wl_max: Math.max(...fullData.data.wavelength)
    };
    emit("retest", rawDataProxy);
    ElMessage.success("历史数据已加载至分析视图");
  } catch (e) {
    ElMessage.error("加载历史数据失败: " + e.message);
  } finally {
    loading.value = false;
  }
};

const openPrintPreview = async (row) => {
  try {
    const res = await fetchRecordDetail(row.id);
    selectedRecord.value = res.data;
    printVisible.value = true;
  } catch (e) {
    ElMessage.error("获取详情失败: " + e.message);
  }
};

const handlePrint = () => {
  const printContent = document.getElementById("printable-report");
  if (!printContent) return;
  const printWindow = window.open("", "_blank");
  printWindow.document.write("<html><head><title>Measurement Report</title>");
  const styles = document.querySelectorAll("style, link[rel='stylesheet']");
  styles.forEach(s => printWindow.document.write(s.outerHTML));
  printWindow.document.write("</head><body>");
  printWindow.document.write(printContent.innerHTML);
  printWindow.document.write("</body></html>");
  printWindow.document.close();
  setTimeout(() => {
    printWindow.print();
    printWindow.close();
  }, 500);
};

const handleDelete = async (row) => {
  try {
    await deleteRecord(row.id);
    ElMessage.success("删除成功");
    loadData();
  } catch (e) {
    ElMessage.error("删除失败: " + e.message);
  }
};

const formatTime = (timeStr) => {
  if (!timeStr) return "-";
  const date = new Date(timeStr);
  return date.toLocaleString();
};

const getR2Class = (val) => {
  if (!val) return "text-muted";
  if (val > 0.99) return "text-success";
  if (val > 0.9) return "text-warning";
  return "text-danger";
};

onMounted(loadData);
</script>

<style scoped>
.database-container { height: 100%; display: flex; flex-direction: column; padding: 24px; background: #fff; }
.table-toolbar { display: flex; justify-content: space-between; margin-bottom: 20px; }
.toolbar-left { display: flex; gap: 12px; }
.search-input { width: 260px; }
.data-table { flex: 1; border-radius: 8px; overflow: hidden; }
:deep(.table-header) { background-color: #f5f7fa !important; color: #1d2129; font-weight: 600; }
.thickness-val { font-family: "Monaco", "Menlo", monospace; font-weight: 500; color: var(--color-primary, #165DFF); }
.interference-level { font-size: 12px; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
.text-success { color: #00b42a; font-weight: 600; }
.text-warning { color: #ff7d00; font-weight: 600; }
.text-danger { color: #f53f3f; font-weight: 600; }
.text-muted { color: #86909c; }
.print-actions { display: flex; justify-content: flex-end; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px dashed #eee; }
.print-content { background: #f0f2f5; padding: 20px; display: flex; justify-content: center; max-height: 70vh; overflow-y: auto; }
:deep(.print-dialog .el-dialog__body) { padding: 10px 20px 20px; }
</style>