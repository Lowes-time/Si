<template>
  <div class="app-container">
    <header class="app-header">
      <div class="header-left">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>
            <path d="M2 12h20"/>
          </svg>
        </div>
        <div class="header-text">
          <h1>半导体薄膜厚度光学测量分析系统</h1>
          <span class="version-badge">V1.0</span>
        </div>
      </div>
      <div class="header-nav">
        <el-tabs v-model="activeView" class="nav-tabs">
          <el-tab-pane label="实时分析" name="analysis" />
          <el-tab-pane label="历史记录" name="history" />
        </el-tabs>
      </div>
    </header>
    <div class="app-body">
      <!-- Analysis View -->
      <template v-if="activeView === 'analysis'">
        <aside class="control-panel">
          <div class="panel-scroll">
            <el-collapse v-model="activePanels" class="control-collapse">
              <el-collapse-item name="import">
                <template #title>
                  <div class="step-title">
                    <span class="step-num" :class="{ done: rawData }">
                      <el-icon v-if="rawData"><CircleCheckFilled /></el-icon>
                      <span v-else>1</span>
                    </span>
                    <span class="step-label">数据导入</span>
                  </div>
                </template>
                <DataImport @data-loaded="onDataLoaded" />
              </el-collapse-item>
              <el-collapse-item name="preprocess" :disabled="!rawData">
                <template #title>
                  <div class="step-title">
                    <span class="step-num" :class="{ done: processedData }">
                      <el-icon v-if="processedData"><CircleCheckFilled /></el-icon>
                      <span v-else>2</span>
                    </span>
                    <span class="step-label">预处理设置</span>
                  </div>
                </template>
                <PreprocessPanel
                  :raw-data="rawData"
                  @preprocessed="onPreprocessed"
                />
              </el-collapse-item>
              <el-collapse-item name="calculate" :disabled="!rawData">
                <template #title>
                  <div class="step-title">
                    <span class="step-num" :class="{ done: calcResult }">
                      <el-icon v-if="calcResult"><CircleCheckFilled /></el-icon>
                      <span v-else>3</span>
                    </span>
                    <span class="step-label">膜厚反演</span>
                  </div>
                </template>
                <CalculationPanel
                  :raw-data="rawData"
                  @calculated="onCalculated"
                  @export="onExport"
                  @save="onSaveRecord"
                />
              </el-collapse-item>
              <el-collapse-item name="results" :disabled="!calcResult">
                <template #title>
                  <div class="step-title">
                    <span class="step-num">4</span>
                    <span class="step-label">分析结果</span>
                  </div>
                </template>
                <ResultsLog :log="resultLog" :result="calcResult" />
              </el-collapse-item>
            </el-collapse>
          </div>
        </aside>
        <main class="chart-area">
          <SpectrumChart
            :raw-data="rawData"
            :processed-data="processedData"
            :calc-result="calcResult"
          />
        </main>
      </template>

      <!-- History View -->
      <template v-else>
        <main class="database-view">
          <DatabasePanel @retest="onRetest" />
        </main>
      </template>
    </div>
  </div>
</template>

<script>
import { CircleCheckFilled } from "@element-plus/icons-vue";
import DataImport from "./components/DataImport.vue";
import PreprocessPanel from "./components/PreprocessPanel.vue";
import CalculationPanel from "./components/CalculationPanel.vue";
import ResultsLog from "./components/ResultsLog.vue";
import SpectrumChart from "./components/SpectrumChart.vue";
import DatabasePanel from "./components/DatabasePanel.vue";
import { exportResult, saveRecord } from "./api/index.js";
import { ElMessage } from "element-plus";

export default {
  name: "App",
  components: {
    CircleCheckFilled,
    DataImport,
    PreprocessPanel,
    CalculationPanel,
    ResultsLog,
    SpectrumChart,
    DatabasePanel,
  },
  data() {
    return {
      activeView: "analysis",
      rawData: null,
      processedData: null,
      calcResult: null,
      resultLog: [],
      activePanels: ["import"],
    };
  },
  watch: {
    activeView(val) {
      if (val === 'analysis' && !this.rawData) {
        this.activePanels = ['import'];
      }
    },
    rawData(val) {
      if (val) {
        const idx = this.activePanels.indexOf("import");
        if (idx !== -1) this.activePanels.splice(idx, 1);
        if (!this.activePanels.includes("preprocess")) {
          this.activePanels.push("preprocess");
        }
      }
    },
    calcResult(val) {
      if (val) {
        const idx = this.activePanels.indexOf("calculate");
        if (idx !== -1) this.activePanels.splice(idx, 1);
        if (!this.activePanels.includes("results")) {
          this.activePanels.push("results");
        }
      }
    },
  },
  methods: {
    onDataLoaded(data) {
      this.rawData = data;
      this.processedData = null;
      this.calcResult = null;
      this.addLog(`数据加载完成: ${data.filename}，共 ${data.row_count} 行`);
      this.$nextTick(() => { this.activePanels = ["preprocess"]; });
    },
    onRetest(data) {
      this.rawData = data;
      this.processedData = null;
      this.calcResult = null;
      this.activeView = 'analysis';
      this.addLog(`已从历史记录加载复测数据: ${data.filename}`);
      this.$nextTick(() => { this.activePanels = ["preprocess"]; });
    },
    onPreprocessed(data) {
      this.processedData = data;
      this.calcResult = null;
      this.addLog(`预处理完成: 检测到 ${data.peaks_wl?.length || 0} 个波峰, ${data.valleys_wl?.length || 0} 个波谷`);
    },
    onCalculated(result) {
      this.calcResult = result;
      this.addLog(`初估厚度: ${result.init_thickness_um} μm`);
      this.addLog(`干涉判定: ${result.multi_beam_level}`);
      this.addLog(`拟合厚度: ${result.thickness_um} μm`);
      this.addLog(`拟合优度 R²: ${result.r_squared}`);
      this.$nextTick(() => { this.activePanels = ["results"]; });
    },
    async onExport() {
      if (!this.calcResult) return;
      try {
        const res = await exportResult({
          result: this.calcResult,
          wavelength: this.calcResult.wavelength,
          reflectance: this.calcResult.reflectance,
          ref_fit: this.calcResult.ref_fit,
        });
        const url = URL.createObjectURL(new Blob([res.data]));
        const a = document.createElement("a");
        a.href = url;
        a.download = "thickness_result.xlsx";
        a.click();
        URL.revokeObjectURL(url);
        this.addLog("结果已导出为 thickness_result.xlsx");
      } catch (e) {
        this.addLog("导出失败: " + e.message);
      }
    },
    async onSaveRecord(material) {
      if (!this.calcResult || !this.rawData) return;
      try {
        await saveRecord({
          filename: this.rawData.filename,
          material: material,
          thickness_um: this.calcResult.thickness_um,
          r_squared: this.calcResult.r_squared,
          multi_beam_level: this.calcResult.multi_beam_level,
          data_json: {
            wavelength: this.calcResult.wavelength,
            reflectance: this.calcResult.reflectance,
            ref_fit: this.calcResult.ref_fit
          }
        });
        ElMessage.success("数据已成功保存至数据库");
        this.addLog("分析结果已存入本地数据库");
      } catch (e) {
        ElMessage.error("保存失败: " + e.message);
      }
    },
    addLog(msg) {
      const time = new Date().toLocaleTimeString();
      this.resultLog.push(`[${time}] ${msg}`);
    },
  },
};
</script>

<style>
/* ===== Design Tokens ===== */
:root {
  --color-primary: #165DFF;
  --color-primary-light: #E8F3FF;
  --color-success: #00B42A;
  --color-warning: #FF7D00;
  --color-danger: #F53F3F;
  --color-text-1: #1D2129;
  --color-text-2: #4E5969;
  --color-text-3: #86909C;
  --color-bg-1: #F7F8FA;
  --color-bg-2: #FFFFFF;
  --color-border: #E5E6EB;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.06);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.08);
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: var(--font-family);
  background: var(--color-bg-1);
  color: var(--color-text-1);
  -webkit-font-smoothing: antialiased;
}

/* ===== Scrollbar ===== */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #C9CDD4; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #A8ADB5; }

.app-container { height: 100vh; display: flex; flex-direction: column; }

/* ===== Header ===== */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
  flex-shrink: 0;
  background: var(--color-bg-2);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  z-index: 10;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  border-radius: var(--radius-md);
  color: #fff;
}
.logo-icon svg { width: 22px; height: 22px; }
.header-text { display: flex; align-items: center; gap: 10px; }
.header-text h1 {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-1);
  letter-spacing: 0.5px;
}
.version-badge {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-primary);
  background: var(--color-primary-light);
  padding: 2px 8px;
  border-radius: 10px;
}

.header-nav {
  margin-left: 48px;
  flex: 1;
}

.nav-tabs :deep(.el-tabs__header) {
  margin: 0;
  border-bottom: none;
}
.nav-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}
.nav-tabs :deep(.el-tabs__item) {
  height: 56px;
  line-height: 56px;
  font-size: 15px;
  font-weight: 500;
}

/* ===== Body Layout ===== */
.app-body { flex: 1; display: flex; overflow: hidden; }

.database-view {
  flex: 1;
  background: var(--color-bg-2);
  overflow: hidden;
}

.control-panel {
  width: 400px;
  flex-shrink: 0;
  background: var(--color-bg-2);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}
.panel-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

/* ===== Collapse ===== */
.control-collapse {
  --el-collapse-header-height: 44px;
  --el-collapse-header-bg-color: transparent;
  --el-collapse-content-bg-color: transparent;
  border: none;
}
.control-collapse .el-collapse-item {
  margin-bottom: 8px;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  overflow: hidden;
  transition: box-shadow 0.2s;
}
.control-collapse .el-collapse-item:hover {
  box-shadow: var(--shadow-sm);
}
.control-collapse .el-collapse-item__header {
  padding: 0 16px;
  font-size: 14px;
  border-bottom: 1px solid transparent;
  transition: background 0.2s;
}
.control-collapse .el-collapse-item__header:hover {
  background: var(--color-bg-1);
}
.control-collapse .el-collapse-item.is-active > .el-collapse-item__header {
  border-bottom-color: var(--color-border);
}
.control-collapse .el-collapse-item__wrap {
  border-top: none;
}
.control-collapse .el-collapse-item__content {
  padding: 16px;
}

.step-title {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}
.step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  background: var(--color-bg-1);
  color: var(--color-text-3);
  flex-shrink: 0;
}
.step-num.done {
  background: var(--color-success);
  color: #fff;
}
.step-label {
  font-weight: 500;
  flex: 1;
  text-align: left;
}

/* ===== Chart Area ===== */
.chart-area {
  flex: 1;
  min-width: 0;
  padding: 16px;
  overflow: hidden;
  background: var(--color-bg-1);
}

@media (max-width: 900px) {
  .app-body { flex-direction: column; }
  .control-panel { width: 100%; max-height: 45%; border-right: none; border-bottom: 1px solid var(--color-border); }
  .chart-area { flex: 1; min-height: 400px; padding: 12px; }
}
</style>
