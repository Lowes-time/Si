<template>
  <Login v-if="!loggedIn" @login-success="onLoginSuccess" />
  <div v-else class="app-container">
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
      <div class="header-actions">
        <span class="user-label">{{ currentUser }}</span>
        <el-button link type="primary" @click="handleLogout">退出</el-button>
      </div>
    </header>
    <div class="app-body">
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
                <PreprocessPanel :raw-data="rawData" :chart-range="chartRange" @preprocessed="onPreprocessed" />
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
                <CalculationPanel :raw-data="rawData" :processed-data="processedData" @calculated="onCalculated" @export="onExport" @save="onSaveRecord" />
              </el-collapse-item>
              <el-collapse-item name="results" :disabled="!calcResult">
                <template #title>
                  <div class="step-title">
                    <span class="step-num">4</span>
                    <span class="step-label">分析结果</span>
                  </div>
                </template>
                <ResultsLog
                  :log="resultLog"
                  :result="calcResult"
                  @save="onSaveRecord"
                  @export="onExport"
                  @history="activeView = 'history'"
                />
              </el-collapse-item>
            </el-collapse>
          </div>
        </aside>
        <main class="chart-area">
          <SpectrumChart
            :raw-data="rawData"
            :processed-data="processedData"
            :calc-result="calcResult"
            @range-selected="onChartRangeSelected"
          />
        </main>
      </template>
      <template v-else>
        <main class="database-view">
          <DatabasePanel @retest="onRetest" />
        </main>
      </template>
    </div>

    <footer class="app-footer">
      <div class="footer-links">
        <a href="javascript:void(0)" @click="showHelp = true" class="footer-link">使用帮助</a>
        <span class="divider">|</span>
        <a href="javascript:void(0)" @click="showAbout = true" class="footer-link">关于系统</a>
      </div>
      <div class="footer-copyright">
        &copy; 2026 半导体薄膜厚度光学测量分析系统
      </div>
    </footer>

    <!-- 关于对话框 -->
    <el-dialog v-model="showAbout" title="关于系统" width="550px" append-to-body>
      <div class="about-content">
        <div class="about-logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>
            <path d="M2 12h20"/>
          </svg>
        </div>
        <h2>半导体薄膜厚度光学测量分析系统</h2>
        <p class="version">Version 1.0</p>
        <div class="about-info">
          <p>基于多光束干涉校正的半导体外延层厚度光谱反演系统</p>
          <ul>
            <li>支持 13 种半导体材料</li>
            <li>高精度光学薄膜厚度测量</li>
            <li>实时数据可视化分析</li>
            <li>历史记录管理</li>
          </ul>
        </div>
        <div class="about-tech">
          <span>技术栈: FastAPI + Vue3 + SQLAlchemy</span>
        </div>
      </div>
    </el-dialog>

    <!-- 帮助对话框 -->
    <el-dialog v-model="showHelp" title="使用帮助" width="700px" append-to-body class="help-dialog" @closed="helpActivePage = 1">
      <div class="help-content">
        <div v-show="helpActivePage === 1" class="help-page">
          <div class="help-section">
            <h3>一、数据导入</h3>
            <p>系统支持三种数据导入方式：</p>
            <ul>
              <li><strong>文件上传</strong>：拖拽或点击上传 CSV/TXT/XLSX 格式的光谱数据文件</li>
              <li><strong>示例数据</strong>：内置 SiC/Si/GaAs/Ge 等演示样例，可直接加载验证拟合效果</li>
              <li><strong>手动输入</strong>：直接粘贴或输入波长和反射率数据（格式：波长,反射率）</li>
            </ul>
          </div>
          
          <div class="help-section">
            <h3>二、数据范围选择</h3>
            <p>导入数据后，可以在预处理面板中选择感兴趣的数据区间：</p>
            <ul>
              <li><strong>手动输入</strong>：在"波长范围"输入框中指定起止波长</li>
              <li><strong>自动选择</strong>：系统可自动分析并选择最优拟合区间</li>
              <li><strong>数据限制</strong>：最小需保留 30 个数据点以保证拟合精度</li>
            </ul>
          </div>
        </div>

        <div v-show="helpActivePage === 2" class="help-page">
          <div class="help-section">
            <h3>三、材料选择与计算</h3>
            <p>在膜厚反演面板中：</p>
            <ul>
              <li>选择对应的半导体基底材料（支持 13 种材料）</li>
              <li>设置入射角（0-89°）</li>
              <li>点击"执行厚度拟合与反演"进行计算</li>
            </ul>
          </div>

          <div class="help-section">
            <h3>四、结果保存与报告</h3>
            <ul>
              <li>计算完成后可点击"保存入库"将结果保存到数据库</li>
              <li>点击"Excel"导出计算结果</li>
              <li>在历史记录中可查看历史数据、重测和打印报告</li>
            </ul>
          </div>
        </div>

        <div v-show="helpActivePage === 3" class="help-page">
          <div class="help-section">
            <h3>五、支持的材料</h3>
            <div class="material-list">
              <div class="material-item"><span class="mat-name">SiC</span><span class="mat-desc">碳化硅 - 功率器件、射频</span></div>
              <div class="material-item"><span class="mat-name">Si</span><span class="mat-desc">硅 - IC衬底、太阳能</span></div>
              <div class="material-item"><span class="mat-name">GaN</span><span class="mat-desc">氮化镓 - 蓝光LED、功率</span></div>
              <div class="material-item"><span class="mat-name">AlN</span><span class="mat-desc">氮化铝 - UVC LED</span></div>
              <div class="material-item"><span class="mat-name">InP</span><span class="mat-desc">磷化铟 - 光通信</span></div>
              <div class="material-item"><span class="mat-name">GaAs</span><span class="mat-desc">砷化镓 - 射频、激光</span></div>
              <div class="material-item"><span class="mat-name">ZnO</span><span class="mat-desc">氧化锌 - UV、压电</span></div>
              <div class="material-item"><span class="mat-name">C</span><span class="mat-desc">金刚石 - 高功率探测</span></div>
              <div class="material-item"><span class="mat-name">Ge</span><span class="mat-desc">锗 - 红外光学</span></div>
              <div class="material-item"><span class="mat-name">GaSb</span><span class="mat-desc">砷化镓锑 - 红外激光</span></div>
              <div class="material-item"><span class="mat-name">InAs</span><span class="mat-desc">砷化铟 - 中红外器件</span></div>
              <div class="material-item"><span class="mat-name">SiO2</span><span class="mat-desc">二氧化硅 - 栅氧、钝化</span></div>
              <div class="material-item"><span class="mat-name">Si3N4</span><span class="mat-desc">氮化硅 - 应力缓冲</span></div>
            </div>
          </div>
        </div>

        <div v-show="helpActivePage === 4" class="help-page">
          <div class="help-section">
            <h3>六、数据来源与算法说明</h3>
            <div class="algorithm-info">
              <div class="algo-item">
                <h4>材料光学常数</h4>
                <p>所有半导体材料的折射率数据均来源于：</p>
                <ul>
                  <li>公开发表的学术论文（如Peter Yu, "Fundamentals of Semiconductors"）</li>
                  <li>美国NIST（国家标准与技术研究院）光学常数数据库</li>
                  <li>Sellmeier方程经验公式（业界标准方法）</li>
                </ul>
              </div>
              <div class="algo-item">
                <h4>核心算法</h4>
                <p>薄膜厚度反演采用以下成熟算法：</p>
                <ul>
                  <li><strong>双光束干涉模型</strong>：基于薄膜光学原理的反射率计算</li>
                  <li><strong>Savitzky-Golay滤波</strong>：数据平滑去噪</li>
                  <li><strong>Levenberg-Marquardt优化</strong>：非线性最小二乘拟合</li>
                  <li><strong>干涉条纹对比度分析</strong>：多光束干涉等级判定</li>
                </ul>
              </div>
              <div class="algo-item">
                <h4>准确性保证</h4>
                <ul>
                  <li>折射率公式经过实验验证</li>
                  <li>拟合算法采用工业级scipy优化库</li>
                  <li>R²指标评估拟合质量</li>
                  <li>支持置信区间估算</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        
        <div class="help-pagination">
          <el-pagination 
            v-model:current-page="helpActivePage" 
            :page-size="1" 
            :total="4" 
            layout="prev, pager, next"
            background
            style="justify-content: center; margin-top: 20px;"
          />
        </div>
      </div>
    </el-dialog>
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
import Login from "./components/Login.vue";
import { exportResult, saveRecord } from "./api/index.js";
import { isLoggedIn, clearLogin } from "./utils/auth.js";
import { ElMessage, ElMessageBox } from "element-plus";

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
    Login,
  },
  data() {
    return {
      loggedIn: isLoggedIn(),
      currentUser: "user",
      showAbout: false,
      showHelp: false,
      helpActivePage: 1,
      activeView: "analysis",
      rawData: null,
      processedData: null,
      calcResult: null,
      resultLog: [],
      activePanels: ["import"],
      selectedMaterial: "SIC",
      chartRange: null,
    };
  },
  watch: {
    activeView(val) {
      if (val === "analysis" && !this.rawData) {
        this.activePanels = ["import"];
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
        if (!this.activePanels.includes("calculate")) {
          this.activePanels.push("calculate");
        }
        if (!this.activePanels.includes("results")) {
          this.activePanels.push("results");
        }
      }
    },
  },
  methods: {
    onLoginSuccess(name) {
      this.loggedIn = true;
      this.currentUser = name || "user";
    },
    handleLogout() {
      clearLogin();
      this.loggedIn = false;
      this.currentUser = "user";
      this.rawData = null;
      this.processedData = null;
      this.calcResult = null;
      this.resultLog = [];
      this.activeView = "analysis";
      this.activePanels = ["import"];
    },
    onChartRangeSelected(range) {
      this.chartRange = range;
      if (range) {
        this.addLog(`图表框选范围: ${range.start.toFixed(2)} - ${range.end.toFixed(2)} μm`);
        if (!this.activePanels.includes("preprocess")) {
          this.activePanels.push("preprocess");
        }
      }
    },
    onDataLoaded(data) {
      this.rawData = data;
      this.processedData = null;
      this.calcResult = null;
      const fileName = data.filename || data.film_code || "数据文件";
      this.addLog("数据加载完成: " + fileName + "，共 " + data.row_count + " 行");
      this.$nextTick(() => { this.activePanels = ["preprocess"]; });
    },
    onRetest(data) {
      this.rawData = data;
      this.processedData = null;
      this.calcResult = null;
      this.activeView = "analysis";
      const fileName = data.film_code || data.filename || "历史记录";
      this.addLog("已从历史记录加载复测数据: " + fileName);
      this.$nextTick(() => { this.activePanels = ["preprocess"]; });
    },
    onPreprocessed(data) {
      this.processedData = data;
      this.calcResult = null;
      const peaks = data.peaks_wl ? data.peaks_wl.length : 0;
      const valleys = data.valleys_wl ? data.valleys_wl.length : 0;
      this.addLog("预处理完成: 检测到 " + peaks + " 个波峰, " + valleys + " 个波谷");
    },
    onCalculated(result) {
      this.calcResult = result;
      if (result.material_type) {
        this.selectedMaterial = result.material_type;
      }
      this.addLog("初估厚度: " + result.init_thickness_um + " μm");
      this.addLog("干涉判定: " + result.multi_beam_level);
      this.addLog("拟合厚度: " + result.thickness_um + " μm");
      this.addLog("拟合优度 R²: " + result.r_squared);
      if (result.fit_model) {
        this.addLog("拟合模型: " + result.fit_model);
      }
      this.$nextTick(() => {
        this.activePanels = ["calculate", "results"];
      });
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
      const mat = material || this.calcResult.material_type || this.selectedMaterial;
      const filmCode = await this.promptFilmCode();
      if (!filmCode) {
        ElMessage.warning("已取消保存");
        return;
      }
      try {
        const opticalData = this.calcResult.wavelength.map((wl, i) => ({
          wavelength: wl,
          reflectance: this.calcResult.reflectance[i],
          fitted_reflectance: this.calcResult.ref_fit ? this.calcResult.ref_fit[i] : null,
          seq_order: i
        }));
        await saveRecord({
          film_code: filmCode,
          material_type: mat,
          thickness_um: this.calcResult.thickness_um,
          r_squared: this.calcResult.r_squared,
          multi_beam_level: this.calcResult.multi_beam_level,
          theta_deg: this.calcResult.theta_deg || 10.0,
          notes: "",
          optical_data: opticalData
        });
        this.addLog("分析结果已存入本地数据库: " + filmCode);
        ElMessageBox.confirm("记录已保存，是否前往历史记录查看？", "保存成功", {
          confirmButtonText: "查看历史",
          cancelButtonText: "继续分析",
          type: "success",
        }).then(() => {
          this.activeView = "history";
        }).catch(() => {});
      } catch (e) {
        ElMessage.error("保存失败: " + e.message);
      }
    },
    promptFilmCode() {
      return new Promise((resolve) => {
        this.$prompt("请输入薄膜编号（如 SiC-15um-A）", "保存记录", {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          inputPattern: /\S+/,
          inputErrorMessage: "薄膜编号不能为空",
          inputValue: this.generateDefaultFilmCode()
        }).then(({ value }) => {
          resolve(value);
        }).catch(() => {
          resolve(null);
        });
      });
    },
    generateDefaultFilmCode() {
      const now = new Date();
      const y = now.getFullYear();
      const m = String(now.getMonth() + 1).padStart(2, "0");
      const d = String(now.getDate()).padStart(2, "0");
      const rand = Math.floor(Math.random() * 1000).toString().padStart(3, "0");
      return "FILM-" + y + m + d + "-" + rand;
    },
    addLog(msg) {
      const time = new Date().toLocaleTimeString();
      this.resultLog.push("[" + time + "] " + msg);
    },
  },
};
</script>

<style>
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
body { font-family: var(--font-family); background: var(--color-bg-1); color: var(--color-text-1); -webkit-font-smoothing: antialiased; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #C9CDD4; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #A8ADB5; }

.app-container { height: 100vh; display: flex; flex-direction: column; }
.app-header { display: flex; align-items: center; justify-content: space-between; padding: 0 24px; height: 56px; flex-shrink: 0; background: var(--color-bg-2); border-bottom: 1px solid var(--color-border); box-shadow: var(--shadow-sm); z-index: 10; }
.header-left { display: flex; align-items: center; gap: 12px; }
.logo-icon { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background: var(--color-primary); border-radius: var(--radius-md); color: #fff; }
.logo-icon svg { width: 22px; height: 22px; }
.header-text { display: flex; align-items: center; gap: 10px; }
.header-text h1 { font-size: 16px; font-weight: 600; letter-spacing: 0.5px; }
.version-badge { font-size: 11px; font-weight: 500; color: var(--color-primary); background: var(--color-primary-light); padding: 2px 8px; border-radius: 10px; }
.header-nav { margin-left: 48px; flex: 1; }
.nav-tabs :deep(.el-tabs__header) { margin: 0; border-bottom: none; }
.nav-tabs :deep(.el-tabs__nav-wrap::after) { display: none; }
.nav-tabs :deep(.el-tabs__item) { height: 56px; line-height: 56px; font-size: 15px; font-weight: 500; }

.app-body { flex: 1; display: flex; overflow: hidden; }

.app-footer {
  text-align: center;
  padding: 12px 0;
  background: var(--color-bg-2);
  border-top: 1px solid var(--color-border);
  font-size: 12px;
  color: var(--color-text-3);
  flex-shrink: 0;
}
.footer-links { margin-bottom: 6px; }
.footer-link {
  color: var(--color-text-2);
  text-decoration: none;
  cursor: pointer;
  transition: color 0.2s;
}
.footer-link:hover { color: var(--color-primary); }
.footer-links .divider { margin: 0 12px; color: var(--color-border); }
.footer-copyright { font-size: 11px; }

.database-view { flex: 1; background: var(--color-bg-2); overflow: hidden; }
.control-panel { width: 400px; flex-shrink: 0; background: var(--color-bg-2); border-right: 1px solid var(--color-border); display: flex; flex-direction: column; }
.panel-scroll { flex: 1; overflow-y: auto; padding: 16px; }

.control-collapse { --el-collapse-header-height: 44px; --el-collapse-header-bg-color: transparent; --el-collapse-content-bg-color: transparent; border: none; }
.control-collapse .el-collapse-item { margin-bottom: 8px; border: 1px solid var(--color-border) !important; border-radius: var(--radius-md) !important; overflow: hidden; transition: box-shadow 0.2s; }
.control-collapse .el-collapse-item:hover { box-shadow: var(--shadow-sm); }
.control-collapse .el-collapse-item__header { padding: 0 16px; font-size: 14px; border-bottom: 1px solid transparent; transition: background 0.2s; }
.control-collapse .el-collapse-item__header:hover { background: var(--color-bg-1); }
.control-collapse .el-collapse-item.is-active > .el-collapse-item__header { border-bottom-color: var(--color-border); }
.control-collapse .el-collapse-item__wrap { border-top: none; }
.control-collapse .el-collapse-item__content { padding: 16px; }

.step-title { display: flex; align-items: center; gap: 10px; width: 100%; }
.step-num { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; background: var(--color-bg-1); color: var(--color-text-3); flex-shrink: 0; }
.step-num.done { background: var(--color-success); color: #fff; }
.step-label { font-weight: 500; flex: 1; text-align: left; }

.chart-area { flex: 1; min-width: 0; padding: 16px; overflow: hidden; background: var(--color-bg-1); }

.header-actions { display: flex; align-items: center; gap: 8px; margin-left: auto; flex-shrink: 0; }
.user-label { font-size: 13px; color: var(--color-text-2); }

.about-content { text-align: center; padding: 20px; }
.about-logo { width: 64px; height: 64px; background: linear-gradient(135deg, #165DFF 0%, #4080FF 100%); border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; color: white; }
.about-logo svg { width: 40px; height: 40px; }
.about-content h2 { font-size: 18px; font-weight: 600; margin: 0 0 8px; }
.about-content .version { font-size: 13px; color: #86909C; margin-bottom: 20px; }
.about-info { background: #F7F8FA; padding: 16px; border-radius: 8px; text-align: left; margin-bottom: 16px; }
.about-info p { font-size: 13px; color: #4E5969; margin: 0 0 12px; }
.about-info ul { margin: 0; padding-left: 20px; }
.about-info li { font-size: 12px; color: #86909C; margin-bottom: 4px; }
.about-tech { font-size: 11px; color: #C9CDD4; }

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
}
.action-btn .el-icon { margin-right: 4px; }

.help-dialog .help-content { padding: 10px 0; }
.help-section { margin-bottom: 20px; }
.help-section h3 { font-size: 15px; font-weight: 600; color: #1D2129; margin: 0 0 10px; padding-left: 10px; border-left: 3px solid #165DFF; }
.help-section p { font-size: 13px; color: #4E5969; margin: 0 0 8px; }
.help-section ul { margin: 0; padding-left: 20px; }
.help-section li { font-size: 13px; color: #4E5969; line-height: 1.8; }
.help-section li strong { color: #1D2129; }

.material-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.material-item { 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  padding: 10px 12px; 
  background: #F7F8FA; 
  border-radius: 6px; 
}
.mat-name { 
  font-weight: 600; 
  color: #165DFF; 
  background: #E8F3FF; 
  padding: 2px 8px; 
  border-radius: 4px; 
  font-size: 12px; 
}
.mat-desc { font-size: 12px; color: #86909C; }

.algorithm-info { display: flex; flex-direction: column; gap: 16px; }
.algo-item {
  background: #F7F8FA;
  padding: 14px 16px;
  border-radius: 8px;
  border-left: 3px solid #165DFF;
}
.algo-item h4 { font-size: 14px; font-weight: 600; color: #1D2129; margin: 0 0 8px; }
.algo-item p { font-size: 12px; color: #4E5969; margin: 0 0 8px; }
.algo-item ul { margin: 0; padding-left: 18px; }
.algo-item li { font-size: 12px; color: #4E5969; line-height: 1.7; }

@media (max-width: 900px) {
  .app-body { flex-direction: column; }
  .control-panel { width: 100%; max-height: 45%; border-right: none; border-bottom: 1px solid var(--color-border); }
  .chart-area { flex: 1; min-height: 400px; padding: 12px; }
}
</style>