<template>
  <div class="chart-container">
    <div v-if="!rawData" class="chart-empty">
      <el-icon :size="48"><Picture /></el-icon>
      <p class="empty-title">暂无数据</p>
      <p class="empty-desc">请先导入光谱数据文件</p>
    </div>

    <template v-else>
      <div class="chart-toolbar">
        <div class="toolbar-tabs">
          <span
            v-for="tab in tabs"
            :key="tab.key"
            :class="['tab-item', { active: activeTab === tab.key, disabled: tab.disabled }]"
            @click="switchTab(tab)"
          >
            {{ tab.label }}
          </span>
        </div>
        <div class="toolbar-actions">
          <el-button
            v-if="activeTab === 'raw'"
            size="small"
            :type="brushMode ? 'primary' : 'default'"
            @click="toggleBrushMode"
          >
            {{ brushMode ? "框选中" : "框选范围" }}
          </el-button>
          <el-button v-if="activeTab === 'raw'" size="small" @click="showRangeSelector = true">
            精确输入
          </el-button>
        </div>
      </div>

      <div class="toolbar-hint-row">
        <el-icon><InfoFilled /></el-icon>
        <span v-if="brushMode">在图表上按住拖拽框选波长范围，完成后请在左侧预处理面板执行预处理</span>
        <span v-else>滚轮缩放 / 底部滑块平移；框选请点「框选范围」</span>
      </div>

      <div v-if="selectedRange" class="range-indicator">
        <span class="range-label">已选范围:</span>
        <span class="range-value">{{ selectedRange.start.toFixed(2) }} - {{ selectedRange.end.toFixed(2) }} μm</span>
        <span class="range-points">({{ selectedRange.count }} 点)</span>
        <el-button size="small" text @click="clearRange">清除</el-button>
      </div>

      <div class="chart-body">
        <div ref="chartDom" class="chart-box"></div>
      </div>

      <el-dialog v-model="showRangeSelector" title="数据范围选择" width="500px" append-to-body>
        <div class="range-selector-modal">
          <div class="range-inputs">
            <div class="input-group">
              <label>起始波长 (μm)</label>
              <el-input-number
                v-model="rangeStart"
                :min="rawData ? parseFloat(rawData.wl_min) : 0"
                :max="rangeEndInput"
                :step="0.1"
                :precision="2"
                size="default"
              />
            </div>
            <div class="input-separator">—</div>
            <div class="input-group">
              <label>结束波长 (μm)</label>
              <el-input-number
                v-model="rangeEndInput"
                :min="rangeStart"
                :max="rawData ? parseFloat(rawData.wl_max) : 20"
                :step="0.1"
                :precision="2"
                size="default"
              />
            </div>
          </div>
          <div class="range-info">
            <span>全谱: {{ rawData ? rawData.wl_min : "-" }} - {{ rawData ? rawData.wl_max : "-" }} μm</span>
            <span>约 {{ getRangePointCount() }} 个点</span>
          </div>
          <div class="range-presets">
            <span class="presets-label">快速:</span>
            <el-button size="small" @click="setRange('center')">中间1/3</el-button>
            <el-button size="small" @click="setRange('start')">前1/3</el-button>
            <el-button size="small" @click="setRange('end')">后1/3</el-button>
            <el-button size="small" @click="setRange('full')">全部</el-button>
          </div>
          <div class="quick-chart" ref="quickChartDom"></div>
        </div>
        <template #footer>
          <el-button @click="showRangeSelector = false">取消</el-button>
          <el-button type="primary" @click="applyRange">应用</el-button>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<script>
import * as echarts from "echarts";
import { Picture, InfoFilled } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";

const COLORS = { blue: "#165DFF", orange: "#FF7D00", green: "#00B42A", red: "#F53F3F" };

export default {
  name: "SpectrumChart",
  components: { Picture, InfoFilled },
  props: {
    rawData: { type: Object, default: null },
    processedData: { type: Object, default: null },
    calcResult: { type: Object, default: null },
  },
  emits: ["range-selected"],
  data() {
    return {
      activeTab: "raw",
      chartInst: null,
      quickChartInst: null,
      showRangeSelector: false,
      rangeStart: null,
      rangeEndInput: null,
      selectedRange: null,
      brushMode: false,
      isSelecting: false,
      startX: null,
      endX: null,
      rangeRect: null,
    };
  },
  computed: {
    tabs() {
      return [
        { key: "raw", label: "原始光谱", disabled: false },
        { key: "fit", label: "拟合对比", disabled: !this.calcResult },
        { key: "residual", label: "残差分析", disabled: !this.calcResult },
      ];
    },
    data() {
      return this.processedData || this.rawData;
    },
  },
  watch: {
    rawData() {
      this.activeTab = "raw";
      this.selectedRange = null;
      this.brushMode = false;
      this.$nextTick(() => {
        this.initChart();
        this.drawRaw();
      });
    },
    calcResult(val) {
      if (val) {
        this.$nextTick(() => {
          if (!this.chartInst) this.initChart();
          this.drawCurrent();
        });
      }
    },
    showRangeSelector(val) {
      if (val && this.rawData) {
        this.$nextTick(() => {
          this.rangeStart = parseFloat(this.rawData.wl_min);
          this.rangeEndInput = parseFloat(this.rawData.wl_max);
          this.initQuickChart();
        });
      }
    },
    brushMode() {
      this.drawCurrent();
    },
  },
  mounted() {
    window.addEventListener("resize", this.onResize);
    window.addEventListener("mouseup", this.onWindowMouseUp);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.onResize);
    window.removeEventListener("mouseup", this.onWindowMouseUp);
    this.detachBrushHandlers();
    this.chartInst?.dispose();
    this.quickChartInst?.dispose();
  },
  methods: {
    toggleBrushMode() {
      this.brushMode = !this.brushMode;
      if (!this.brushMode) this.cancelSelection();
    },
    attachBrushHandlers() {
      if (!this.chartInst) return;
      const zr = this.chartInst.getZr();
      zr.on("mousedown", this.onChartMouseDown);
      zr.on("mousemove", this.onChartMouseMove);
    },
    detachBrushHandlers() {
      if (!this.chartInst) return;
      const zr = this.chartInst.getZr();
      zr.off("mousedown", this.onChartMouseDown);
      zr.off("mousemove", this.onChartMouseMove);
    },
    initChart() {
      const dom = this.$refs.chartDom;
      if (!dom || dom.clientWidth === 0) return;
      this.detachBrushHandlers();
      if (this.chartInst) this.chartInst.dispose();
      this.chartInst = echarts.init(dom);
      this.attachBrushHandlers();
    },
    initQuickChart() {
      const dom = this.$refs.quickChartDom;
      if (!dom || !this.rawData) return;
      if (this.quickChartInst) this.quickChartInst.dispose();
      this.quickChartInst = echarts.init(dom);
      const wl = this.rawData.wavelength || [];
      const ref = this.rawData.reflectance || [];
      const markArea = this.buildMarkArea();
      this.quickChartInst.setOption({
        tooltip: { trigger: "axis" },
        grid: { left: 40, right: 20, top: 20, bottom: 40 },
        xAxis: { type: "value", name: "波长 (μm)" },
        yAxis: { type: "value", name: "反射率" },
        series: [{
          type: "line",
          data: wl.map((x, i) => [x, ref[i]]),
          lineStyle: { width: 1, color: COLORS.blue },
          symbol: "none",
          markArea: { silent: true, data: markArea },
        }],
      });
    },
    buildMarkArea() {
      if (!this.rangeStart && !this.selectedRange) return [];
      const s = this.rangeStart ?? this.selectedRange?.start;
      const e = this.rangeEndInput ?? this.selectedRange?.end;
      if (s == null || e == null) return [];
      return [[
        { xAxis: Math.min(s, e), itemStyle: { color: "rgba(22,93,255,0.12)" } },
        { xAxis: Math.max(s, e) },
      ]];
    },
    onResize() {
      this.chartInst?.resize();
      this.quickChartInst?.resize();
    },
    switchTab(tab) {
      if (tab.disabled) return;
      if (this.brushMode) this.brushMode = false;
      this.activeTab = tab.key;
      this.$nextTick(() => this.drawCurrent());
    },
    onChartMouseDown(params) {
      if (!this.brushMode || this.activeTab !== "raw") return;
      this.isSelecting = true;
      this.startX = params.offsetX;
      this.endX = params.offsetX;
      this.rangeRect = document.createElement("div");
      this.rangeRect.style.cssText =
        "position:absolute;border:2px dashed #165DFF;background:rgba(22,93,255,0.1);pointer-events:none;z-index:1000;top:0;height:100%;";
      this.$refs.chartDom.style.position = "relative";
      this.$refs.chartDom.appendChild(this.rangeRect);
    },
    onChartMouseMove(params) {
      if (!this.isSelecting || !this.rangeRect) return;
      this.endX = params.offsetX;
      const left = Math.min(this.startX, this.endX);
      const width = Math.abs(this.endX - this.startX);
      this.rangeRect.style.left = left + "px";
      this.rangeRect.style.width = width + "px";
    },
    onWindowMouseUp() {
      if (!this.isSelecting) return;
      this.isSelecting = false;
      this.removeRangeRect();
      if (!this.chartInst || !this.rawData || this.startX == null || this.endX == null) return;
      if (Math.abs(this.endX - this.startX) < 5) return;

      const p1 = this.chartInst.convertFromPixel("grid", [this.startX, 0]);
      const p2 = this.chartInst.convertFromPixel("grid", [this.endX, 0]);
      if (!p1 || !p2) return;

      const wlMin = Math.min(p1[0], p2[0]);
      const wlMax = Math.max(p1[0], p2[0]);
      const wl = this.rawData.wavelength || [];
      const count = wl.filter((w) => w >= wlMin && w <= wlMax).length;
      if (count < 10) {
        ElMessage.warning("选取范围过小，请重新框选");
        return;
      }
      this.selectedRange = { start: wlMin, end: wlMax, count };
      this.$emit("range-selected", this.selectedRange);
      ElMessage.success(`已框选 ${wlMin.toFixed(2)} - ${wlMax.toFixed(2)} μm，请在预处理面板确认`);
      this.drawRaw();
    },
    removeRangeRect() {
      if (this.rangeRect && this.$refs.chartDom?.contains(this.rangeRect)) {
        this.$refs.chartDom.removeChild(this.rangeRect);
      }
      this.rangeRect = null;
    },
    cancelSelection() {
      this.isSelecting = false;
      this.removeRangeRect();
    },
    getRangePointCount() {
      if (!this.rawData || this.rangeStart === null || this.rangeEndInput === null) return 0;
      const wl = this.rawData.wavelength || [];
      const lo = Math.min(this.rangeStart, this.rangeEndInput);
      const hi = Math.max(this.rangeStart, this.rangeEndInput);
      return wl.filter((w) => w >= lo && w <= hi).length;
    },
    setRange(mode) {
      if (!this.rawData) return;
      const min = parseFloat(this.rawData.wl_min);
      const max = parseFloat(this.rawData.wl_max);
      const span = max - min;
      const map = {
        center: [min + span * 0.33, min + span * 0.67],
        start: [min, min + span * 0.33],
        end: [min + span * 0.67, max],
        full: [min, max],
      };
      [this.rangeStart, this.rangeEndInput] = map[mode];
      this.initQuickChart();
    },
    applyRange() {
      if (this.rangeStart == null || this.rangeEndInput == null) return;
      const lo = Math.min(this.rangeStart, this.rangeEndInput);
      const hi = Math.max(this.rangeStart, this.rangeEndInput);
      this.selectedRange = { start: lo, end: hi, count: this.getRangePointCount() };
      this.$emit("range-selected", this.selectedRange);
      ElMessage.success(`已选择 ${lo.toFixed(2)} - ${hi.toFixed(2)} μm`);
      this.showRangeSelector = false;
      this.drawRaw();
    },
    clearRange() {
      this.selectedRange = null;
      this.$emit("range-selected", null);
      this.drawRaw();
    },
    drawCurrent() {
      if (!this.chartInst) this.initChart();
      if (!this.chartInst) return;
      if (this.activeTab === "raw") this.drawRaw();
      else if (this.activeTab === "fit") this.drawFit();
      else if (this.activeTab === "residual") this.drawResidual();
    },
    baseGrid() {
      return { left: 64, right: 28, top: 22, bottom: 88 };
    },
    legendOption(names) {
      return {
        data: names,
        bottom: 38,
        left: "center",
        orient: "horizontal",
        itemWidth: 16,
        itemHeight: 8,
        itemGap: 20,
        textStyle: { fontSize: 11, color: "#4E5969" },
      };
    },
    baseXAxis() {
      return {
        type: "value",
        name: "波长 (μm)",
        nameTextStyle: { fontSize: 12, color: "#86909C" },
        axisLine: { lineStyle: { color: "#E5E6EB" } },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: "#F2F3F5" } },
        axisLabel: {
          fontSize: 11,
          color: "#86909C",
          formatter(v) {
            return v.toFixed(v < 10 ? 2 : v < 100 ? 1 : 0);
          },
        },
      };
    },
    baseDataZoom() {
      const pan = !this.brushMode;
      return [
        {
          type: "slider",
          xAxisIndex: 0,
          filterMode: "none",
          height: 22,
          bottom: 10,
          brushSelect: false,
        },
        {
          type: "inside",
          xAxisIndex: 0,
          zoomOnMouseWheel: !this.brushMode,
          moveOnMouseMove: pan,
          moveOnMouseWheel: false,
        },
      ];
    },
    drawRaw() {
      if (!this.rawData) return;
      const wl = this.rawData.wavelength || [];
      const ref = this.rawData.reflectance || [];
      const markArea = this.selectedRange
        ? [[
            { xAxis: this.selectedRange.start, itemStyle: { color: "rgba(22,93,255,0.08)" } },
            { xAxis: this.selectedRange.end },
          ]]
        : [];
      const series = [{
        name: "原始光谱",
        type: "line",
        data: wl.map((x, i) => [x, ref[i]]),
        lineStyle: { width: 1, color: COLORS.blue },
        symbol: "none",
        markArea: { silent: true, data: markArea },
      }];
      if (this.data?.ref_smooth) {
        series.push({
          name: "平滑光谱",
          type: "line",
          data: this.data.wavelength.map((x, i) => [x, this.data.ref_smooth[i]]),
          lineStyle: { width: 1.5, color: COLORS.orange },
          symbol: "none",
          smooth: true,
        });
      }
      this.chartInst.setOption({
        tooltip: { trigger: "axis" },
        legend: this.legendOption(series.map((s) => s.name)),
        xAxis: { ...this.baseXAxis(), nameGap: 22 },
        yAxis: { type: "value", name: "反射率", nameGap: 12 },
        grid: this.baseGrid(),
        dataZoom: this.baseDataZoom(),
        series,
      }, true);
    },
    drawFit() {
      const res = this.calcResult;
      if (!res) return;
      this.chartInst.setOption({
        tooltip: { trigger: "axis" },
        legend: this.legendOption(["实验数据", "模型拟合"]),
        xAxis: { ...this.baseXAxis(), nameGap: 22 },
        yAxis: { type: "value", name: "反射率", nameGap: 12 },
        grid: this.baseGrid(),
        dataZoom: this.baseDataZoom(),
        series: [
          {
            name: "实验数据",
            type: "scatter",
            data: res.wavelength.map((x, i) => [x, res.reflectance[i]]),
            symbolSize: 3,
            itemStyle: { color: COLORS.blue, opacity: 0.5 },
          },
          {
            name: "模型拟合",
            type: "line",
            data: res.wavelength.map((x, i) => [x, res.ref_fit[i]]),
            lineStyle: { width: 2, color: COLORS.red },
            symbol: "none",
            smooth: true,
          },
        ],
      }, true);
    },
    drawResidual() {
      const res = this.calcResult;
      if (!res) return;
      const residuals = res.wavelength.map((x, i) => [x, res.reflectance[i] - res.ref_fit[i]]);
      this.chartInst.setOption({
        tooltip: { trigger: "axis" },
        xAxis: { ...this.baseXAxis(), nameGap: 22 },
        yAxis: { type: "value", name: "残差", nameGap: 12 },
        grid: { ...this.baseGrid(), bottom: 88 },
        dataZoom: this.baseDataZoom(),
        series: [{
          type: "line",
          data: residuals,
          lineStyle: { width: 1, color: COLORS.green },
          symbol: "circle",
          symbolSize: 4,
          markLine: { silent: true, symbol: "none", data: [{ yAxis: 0 }] },
        }],
      }, true);
    },
  },
};
</script>

<style scoped>
.chart-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.chart-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #c9cdd4;
  gap: 8px;
}
.empty-title { font-size: 15px; font-weight: 500; color: #86909c; }
.empty-desc { font-size: 13px; color: #a8adb5; }
.chart-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px 0;
  flex-shrink: 0;
}
.toolbar-tabs {
  display: flex;
  gap: 4px;
  background: #f2f3f5;
  border-radius: 6px;
  padding: 3px;
}
.toolbar-actions { display: flex; gap: 8px; }
.toolbar-hint-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  font-size: 11px;
  color: #86909c;
}
.tab-item {
  padding: 5px 14px;
  font-size: 13px;
  color: #4e5969;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}
.tab-item.active { background: #fff; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06); }
.tab-item.disabled { color: #c9cdd4; cursor: not-allowed; }
.range-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #e8f3ff;
  font-size: 12px;
}
.range-value { color: #165dff; font-weight: 600; }
.chart-body { flex: 1; min-height: 0; padding: 8px; }
.chart-box { width: 100%; height: 100%; }
.range-selector-modal { padding: 10px 0; }
.range-inputs { display: flex; align-items: center; gap: 16px; margin-bottom: 12px; }
.input-group { flex: 1; }
.input-group label { display: block; font-size: 12px; margin-bottom: 6px; }
.range-info {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  padding: 8px 12px;
  background: #f7f8fa;
  margin-bottom: 12px;
}
.range-presets { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.quick-chart { width: 100%; height: 200px; border: 1px solid #e5e6eb; border-radius: 8px; }
</style>
