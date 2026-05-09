<template>
  <div class="data-import">
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
      </div>
    </transition>
  </div>
</template>

<script>
import { FolderOpened, Document, Grid, TrendCharts } from "@element-plus/icons-vue";
import { uploadFile } from "../api/index.js";

export default {
  name: "DataImport",
  components: { FolderOpened, Document, Grid, TrendCharts },
  emits: ["data-loaded"],
  data() {
    return {
      pendingFile: null,
      uploading: false,
      dragover: false,
      dataSummary: null,
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
  },
};
</script>

<style scoped>
.data-import { display: flex; flex-direction: column; gap: 16px; }

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

/* 数据统计 */
.data-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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
.stat-item .el-icon { color: var(--color-primary, #165DFF); flex-shrink: 0; }
.stat-value { font-size: 15px; font-weight: 600; color: #1D2129; }
.stat-label { font-size: 11px; color: #86909C; margin-top: 1px; }
</style>
