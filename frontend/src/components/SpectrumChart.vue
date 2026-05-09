<template>
  <div class="chart-container">
    <!-- 空状态 -->
    <div v-if="!rawData" class="chart-empty">
      <el-icon :size="48"><Picture /></el-icon>
      <p class="empty-title">暂无数据</p>
      <p class="empty-desc">请先导入光谱数据文件</p>
    </div>

    <!-- 图表视图 -->
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
      </div>
      <div class="chart-body">
        <div ref="chartDom" class="chart-box"></div>
      </div>
    </template>
  </div>
</template>

<script>
import * as echarts from "echarts";
import { Picture } from "@element-plus/icons-vue";

const COLORS = {
  blue: "#165DFF",
  orange: "#FF7D00",
  green: "#00B42A",
  red: "#F53F3F",
};

export default {
  name: "SpectrumChart",
  components: { Picture },
  props: {
    rawData: { type: Object, default: null },
    processedData: { type: Object, default: null },
    calcResult: { type: Object, default: null },
  },
  data() {
    return { activeTab: "raw", chartInst: null };
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
      this.$nextTick(() => { this.initChart(); this.drawRaw(); });
    },
    calcResult(val) {
      if (val) {
        this.$nextTick(() => {
          if (!this.chartInst) this.initChart();
          this.drawCurrent();
        });
      }
    },
  },
  mounted() {
    window.addEventListener("resize", this.onResize);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.onResize);
    this.chartInst?.dispose();
  },
  methods: {
    initChart() {
      const dom = this.$refs.chartDom;
      if (!dom || dom.clientWidth === 0) return;
      if (this.chartInst) this.chartInst.dispose();
      this.chartInst = echarts.init(dom);
    },
    onResize() {
      this.chartInst?.resize();
    },
    switchTab(tab) {
      if (tab.disabled) return;
      this.activeTab = tab.key;
      this.$nextTick(() => this.drawCurrent());
    },
    drawCurrent() {
      if (!this.chartInst) this.initChart();
      if (!this.chartInst) return;
      if (this.activeTab === "raw") this.drawRaw();
      else if (this.activeTab === "fit") this.drawFit();
      else if (this.activeTab === "residual") this.drawResidual();
    },
    baseGrid() {
      return { left: 56, right: 28, top: 24, bottom: 36 };
    },
    baseXAxis() {
      return {
        type: "value", name: "波长 (μm)",
        nameTextStyle: { fontSize: 12, color: "#86909C" },
        axisLine: { lineStyle: { color: "#E5E6EB" } },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: "#F2F3F5" } },
      };
    },
    drawRaw() {
      if (!this.rawData) return;
      const wl = this.rawData.wavelength || [];
      const ref = this.rawData.reflectance || [];
      const series = [{
        name: "原始光谱", type: "line",
        data: wl.map((x, i) => [x, ref[i]]),
        lineStyle: { width: 1, color: COLORS.blue },
        itemStyle: { color: COLORS.blue },
        symbol: "none",
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(22,93,255,0.10)" },
            { offset: 1, color: "rgba(22,93,255,0.01)" },
          ]),
        },
      }];
      if (this.data?.ref_smooth) {
        series.push({
          name: "平滑光谱", type: "line",
          data: this.data.wavelength.map((x, i) => [x, this.data.ref_smooth[i]]),
          lineStyle: { width: 1.5, color: COLORS.orange },
          symbol: "none", smooth: true,
        });
      }
      this.chartInst.setOption({
        tooltip: { trigger: "axis" },
        legend: { data: series.map((s) => s.name), bottom: 4, textStyle: { fontSize: 12, color: "#4E5969" } },
        xAxis: this.baseXAxis(),
        yAxis: { type: "value", name: "反射率", nameTextStyle: { fontSize: 12, color: "#86909C" }, axisLine: { lineStyle: { color: "#E5E6EB" } }, splitLine: { lineStyle: { color: "#F2F3F5" } } },
        grid: this.baseGrid(),
        series,
      }, true);
    },
    drawFit() {
      const res = this.calcResult;
      if (!res) return;
      this.chartInst.setOption({
        tooltip: { trigger: "axis" },
        legend: { data: ["实验数据", "模型拟合"], bottom: 4, textStyle: { fontSize: 12, color: "#4E5969" } },
        xAxis: this.baseXAxis(),
        yAxis: { type: "value", name: "反射率", nameTextStyle: { fontSize: 12, color: "#86909C" }, axisLine: { lineStyle: { color: "#E5E6EB" } }, splitLine: { lineStyle: { color: "#F2F3F5" } } },
        grid: this.baseGrid(),
        series: [
          { name: "实验数据", type: "scatter", data: res.wavelength.map((x, i) => [x, res.reflectance[i]]), symbolSize: 3, itemStyle: { color: COLORS.blue, opacity: 0.5 } },
          { name: "模型拟合", type: "line", data: res.wavelength.map((x, i) => [x, res.ref_fit[i]]), lineStyle: { width: 2, color: COLORS.red }, symbol: "none", smooth: true },
        ],
      }, true);
    },
    drawResidual() {
      const res = this.calcResult;
      if (!res) return;
      const residuals = res.wavelength.map((x, i) => [x, res.reflectance[i] - res.ref_fit[i]]);
      this.chartInst.setOption({
        tooltip: { trigger: "axis" },
        xAxis: this.baseXAxis(),
        yAxis: { type: "value", name: "残差", nameTextStyle: { fontSize: 12, color: "#86909C" }, axisLine: { lineStyle: { color: "#E5E6EB" } }, splitLine: { lineStyle: { color: "#F2F3F5" } } },
        grid: { ...this.baseGrid(), bottom: 28 },
        series: [{
          type: "line", data: residuals,
          lineStyle: { width: 1, color: COLORS.green },
          itemStyle: { color: COLORS.green },
          symbol: "circle", symbolSize: 4,
          markLine: { silent: true, symbol: "none", data: [{ yAxis: 0 }], lineStyle: { color: "#C9CDD4", type: "dashed", width: 1 } },
        }],
      }, true);
    },
  },
};
</script>

<style scoped>
.chart-container {
  height: 100%; display: flex; flex-direction: column;
  background: #fff; border-radius: 12px; overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* 空状态 */
.chart-empty {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  color: #C9CDD4; gap: 8px;
}
.empty-title { font-size: 15px; font-weight: 500; color: #86909C; }
.empty-desc { font-size: 13px; color: #A8ADB5; }

/* 工具栏 */
.chart-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px 0;
  flex-shrink: 0;
}
.toolbar-tabs {
  display: flex; gap: 4px; background: #F2F3F5;
  border-radius: 6px; padding: 3px;
}
.tab-item {
  padding: 5px 14px; font-size: 13px; color: #4E5969;
  border-radius: 4px; cursor: pointer; transition: all 0.2s;
  font-weight: 500; user-select: none;
}
.tab-item:hover:not(.disabled) { color: #1D2129; }
.tab-item.active {
  background: #fff; color: #1D2129;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}
.tab-item.disabled { color: #C9CDD4; cursor: not-allowed; }

/* 图表体 */
.chart-body { flex: 1; min-height: 0; padding: 8px; }
.chart-box { width: 100%; height: 100%; }
</style>
