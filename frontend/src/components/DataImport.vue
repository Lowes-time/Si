<!-- 数据导入：文件上传、示例数据、手动粘贴 -->
<template>
  <div class="data-import">
    <!-- 标签页：上传/示例/手动输入 -->
    <el-tabs v-model="activeTab" class="import-tabs">
      <el-tab-pane label="文件上传" name="upload">
        <!-- 上传区域 -->
        <div
          class="upload-zone"
          :class="{ 'is-dragover': dragover, 'has-file': pendingFile }"
          @dragover.prevent="dragover = true"
          @dragleave.prevent="dragover = false"
          @drop.prevent="onDrop"
          @click="$refs.fileInput.click()"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".csv,.txt,.xlsx,.xls"
            style="display: none"
            @change="onFileSelect"
          />
          <div v-if="!pendingFile" class="upload-placeholder">
            <div class="upload-icon">
              <el-icon :size="36"><FolderOpened /></el-icon>
            </div>
            <div class="upload-text">
              <span>拖拽光谱文件到此处，或</span>
              <span class="upload-link">点击选择文件</span>
            </div>
            <div class="upload-hint">支持 CSV / TXT / XLSX 格式</div>
          </div>
          <div v-else class="upload-file-info">
            <div class="file-icon-box">
              <el-icon :size="24"><Document /></el-icon>
            </div>
            <div class="file-detail">
              <div class="file-name">{{ pendingFile.name }}</div>
              <div class="file-size">{{ formatSize(pendingFile.size) }}</div>
            </div>
            <el-button
              type="primary"
              :loading="uploading"
              @click.stop="doUpload"
              size="small"
              round
            >
              {{ uploading ? "解析中..." : "开始解析" }}
            </el-button>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="示例数据" name="sample">
        <div class="sample-section">
          <p class="sample-desc">加载内置示例数据进行演示</p>
          <div class="sample-buttons">
            <el-button
              v-for="sample in sampleDataList"
              :key="sample.key"
              @click="loadSampleData(sample.key)"
              class="sample-btn"
              size="default"
            >
              <span class="sample-name">{{ sample.name }}</span>
              <span class="sample-info">{{ sample.info }}</span>
            </el-button>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="手动输入" name="manual">
        <div class="manual-section">
          <p class="manual-desc">粘贴或输入波长和反射率数据</p>
          <el-input
            v-model="manualData"
            type="textarea"
            :rows="6"
            placeholder="格式：波长,反射率&#10;例如：&#10;8.5,0.45&#10;9.0,0.52&#10;9.5,0.48"
          />
          <el-button type="primary" @click="parseManualData" :disabled="!manualData.trim()" class="manual-btn">
            解析数据
          </el-button>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 数据摘要 -->
    <transition name="el-fade-in">
      <div v-if="dataSummary" class="data-stats">
        <div class="stat-item">
          <el-icon :size="18"><Grid /></el-icon>
          <div>
            <div class="stat-value">{{ dataSummary.row_count }}</div>
            <div class="stat-label">数据行数</div>
          </div>
        </div>
        <div class="stat-item">
          <el-icon :size="18"><TrendCharts /></el-icon>
          <div>
            <div class="stat-value">{{ dataSummary.wl_min }}</div>
            <div class="stat-label">最小波长 (μm)</div>
          </div>
        </div>
        <div class="stat-item">
          <el-icon :size="18"><TrendCharts /></el-icon>
          <div>
            <div class="stat-value">{{ dataSummary.wl_max }}</div>
            <div class="stat-label">最大波长 (μm)</div>
          </div>
        </div>
        <div class="stat-item action" @click="clearData">
          <el-icon :size="18"><Delete /></el-icon>
          <div>
            <div class="stat-value">清除</div>
            <div class="stat-label">重新选择</div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { FolderOpened, Document, Grid, TrendCharts, Delete } from "@element-plus/icons-vue";
import { uploadFile } from "../api/index.js";

const SAMPLE_FILES = {
  sic_15: { file: "/samples/test_sic_15um.csv", name: "SiC-15μm", material: "SIC", thick: "15 μm" },
  sic_30: { file: "/samples/test_sic_30um.csv", name: "SiC-30μm", material: "SIC", thick: "30 μm" },
  si_2: { file: "/samples/test_si_2um.csv", name: "Si-2μm", material: "SI", thick: "2 μm" },
  gaas_5: { file: "/samples/test_gaas_5um.csv", name: "GaAs-5μm", material: "GAAS", thick: "5 μm" },
  ge_8: { file: "/samples/test_ge_8um.csv", name: "Ge-8μm", material: "GE", thick: "8 μm" },
};

const SAMPLE_LIST = Object.entries(SAMPLE_FILES).map(([key, m]) => ({
  key,
  name: m.name,
  info: `理论厚度 ${m.thick}`,
}));

export default {
  name: "DataImport",
  components: { FolderOpened, Document, Grid, TrendCharts, Delete },
  emits: ["data-loaded"],
  data() {
    return {
      activeTab: "upload",
      pendingFile: null,
      uploading: false,
      dragover: false,
      dataSummary: null,
      manualData: "",
      sampleDataList: SAMPLE_LIST,
    };
  },
  methods: {
    formatSize(bytes) {
      if (!bytes) return "0 B";
      const units = ["B", "KB", "MB"];
      const i = Math.floor(Math.log(bytes) / Math.log(1024));
      return (bytes / Math.pow(1024, i)).toFixed(1) + " " + units[i];
    },
    onDrop(e) {
      this.dragover = false;
      const files = e.dataTransfer.files;
      if (files.length) { this.pendingFile = files[0]; this.dataSummary = null; }
    },
    onFileSelect(e) {
      const files = e.target.files;
      if (files.length) { this.pendingFile = files[0]; this.dataSummary = null; }
    },
    async doUpload() {
      if (!this.pendingFile) return;
      this.uploading = true;
      try {
        const formData = new FormData();
        formData.append("file", this.pendingFile);
        const res = await uploadFile(formData);
        if (res.data.success) {
          this.dataSummary = res.data.data;
          this.$emit("data-loaded", res.data.data);
          this.$message.success("数据加载成功");
        } else {
          this.$message.error(res.data.error || "上传失败");
        }
      } catch (e) {
        this.$message.error("上传请求失败: " + e.message);
      } finally {
        this.uploading = false;
      }
    },
    async loadSampleData(key) {
      const meta = SAMPLE_FILES[key];
      if (!meta) return;
      try {
        const resp = await fetch(meta.file);
        const text = await resp.text();
        const lines = text.trim().split("\n");
        const wavelength = [];
        const reflectance = [];
        for (let i = 1; i < lines.length; i++) {
          const parts = lines[i].split(",");
          if (parts.length < 2) continue;
          const wn = parseFloat(parts[0]);
          let ref = parseFloat(parts[1]);
          if (ref > 2) ref /= 100;
          wavelength.push(10000 / wn);
          reflectance.push(ref);
        }
        this.dataSummary = {
          filename: meta.file.split("/").pop(),
          film_code: meta.name,
          suggested_material: meta.material,
          row_count: wavelength.length,
          wavelength,
          reflectance,
          wl_min: Math.min(...wavelength).toFixed(2),
          wl_max: Math.max(...wavelength).toFixed(2),
        };
        this.$emit("data-loaded", this.dataSummary);
        this.$message.success(`${meta.name} 已加载（${meta.thick}）`);
      } catch (e) {
        this.$message.error("示例加载失败: " + e.message);
      }
    },
    generateSampleData(key) {
      // 保留作离线兜底，正常走 loadSampleData
      return this.loadSampleData(key);
    },
    parseManualData() {
      try {
        const lines = this.manualData.trim().split("\n");
        const wavelength = [];
        const reflectance = [];
        
        for (const line of lines) {
          const parts = line.split(/[,\s\t]+/).filter(p => p);
          if (parts.length >= 2) {
            const wl = parseFloat(parts[0]);
            const ref = parseFloat(parts[1]);
            if (!isNaN(wl) && !isNaN(ref)) {
              wavelength.push(wl);
              reflectance.push(ref);
            }
          }
        }
        
        if (wavelength.length < 10) {
          this.$message.warning("有效数据点不足，至少需要10个数据点");
          return;
        }
        
        this.dataSummary = {
          film_code: "MANUAL-" + Date.now(),
          row_count: wavelength.length,
          wavelength: wavelength,
          reflectance: reflectance,
          wl_min: Math.min(...wavelength).toFixed(2),
          wl_max: Math.max(...wavelength).toFixed(2)
        };
        this.$emit("data-loaded", this.dataSummary);
        this.$message.success("手动数据解析成功");
      } catch (e) {
        this.$message.error("数据解析失败: " + e.message);
      }
    },
    clearData() {
      this.pendingFile = null;
      this.dataSummary = null;
      this.manualData = "";
      this.$emit("data-loaded", null);
    }
  },
};
</script>

<style scoped>
.data-import { display: flex; flex-direction: column; gap: 16px; }

.import-tabs :deep(.el-tabs__header) { margin-bottom: 16px; }
.import-tabs :deep(.el-tabs__nav-wrap::after) { display: none; }
.import-tabs :deep(.el-tabs__item) { font-size: 13px; }

/* 上传区域 */
.upload-zone {
  border: 2px dashed #D0D5DD;
  border-radius: 12px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  background: #FAFBFC;
}
.upload-zone:hover,
.upload-zone.is-dragover {
  border-color: var(--color-primary, #165DFF);
  background: #F0F5FF;
  box-shadow: 0 0 0 3px rgba(22,93,255,0.08);
}
.upload-zone.has-file {
  border-style: solid;
  border-color: #E5E6EB;
  background: #fff;
  cursor: default;
  padding: 20px 24px;
}

.upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.upload-icon { color: #86909C; margin-bottom: 4px; }
.upload-text { font-size: 14px; color: #4E5969; }
.upload-link { color: var(--color-primary, #165DFF); margin-left: 4px; cursor: pointer; }
.upload-hint { font-size: 12px; color: #86909C; }

.upload-file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: left;
}
.file-icon-box {
  width: 44px; height: 44px;
  border-radius: 10px;
  background: #F0F5FF;
  color: var(--color-primary, #165DFF);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.file-detail { flex: 1; min-width: 0; }
.file-name { font-size: 14px; font-weight: 500; color: #1D2129; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-size { font-size: 12px; color: #86909C; margin-top: 2px; }

/* 示例数据 */
.sample-section { padding: 8px 0; }
.sample-desc { font-size: 13px; color: #86909C; margin-bottom: 16px; }
.sample-buttons { display: flex; flex-direction: column; gap: 10px; }
.sample-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #E5E6EB;
  border-radius: 8px;
  transition: all 0.2s;
}
.sample-btn:hover { border-color: #B8D4FF; background: #F0F5FF; }
.sample-name { font-size: 14px; font-weight: 500; color: #1D2129; }
.sample-info { font-size: 12px; color: #86909C; }

/* 手动输入 */
.manual-section { padding: 8px 0; }
.manual-desc { font-size: 13px; color: #86909C; margin-bottom: 12px; }
.manual-btn { margin-top: 12px; width: 100%; }

/* 数据统计 */
.data-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}
.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 12px;
  background: #F7F8FA;
  border-radius: 8px;
  transition: background 0.2s;
}
.stat-item:hover { background: #F0F5FF; }
.stat-item.action { cursor: pointer; }
.stat-item.action:hover { background: #FFF0F0; }
.stat-item .el-icon { color: var(--color-primary, #165DFF); flex-shrink: 0; }
.stat-item.action .el-icon { color: #F53F3F; }
.stat-value { font-size: 15px; font-weight: 600; color: #1D2129; }
.stat-label { font-size: 11px; color: #86909C; margin-top: 1px; }
</style>