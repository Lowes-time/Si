<!--
  软件名称：基于多光束干涉校正的半导体外延层厚度光谱反演系统 V1.0
  组件功能：光谱数据可视化图表
  描述：使用ECharts展示原始数据、预处理结果和拟合曲线，支持数据范围选择
-->
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
        <div class="toolbar-hint">
          <el-icon><InfoFilled /></el-icon>
          <span>拖拽下方滑块可缩放查看 | 数据范围请在左侧预处理面板设置</span>
        </div>
      </div>
      
      <!-- 数据范围指示 -->
      <div v-if="selectedRange" class="range-indicator">
        <span class="range-label">已选择范围:</span>
        <span class="range-value">{{ selectedRange.start.toFixed(2) }} - {{ selectedRange.end.toFixed(2) }} μm</span>
        <span class="range-points">({{ selectedRange.count }} 个点)</span>
        <el-button size="small" text @click="clearRange">清除</el-button>
      </div>
      
      <div class="chart-body">
        <div ref="chartDom" class="chart-box" @mouseup="onChartMouseUp"></div>
      </div>
      
      <!-- 数据范围选择器弹窗 -->
      <el-dialog v-model="showRangeSelector" title="数据范围选择" width="500px" append-to-body>
        <div class="range-selector-modal">
          <p class="selector-desc">在下方图表中拖拽选择数据范围，或手动输入起止波长</p>
          
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
            <span>数据范围: {{ rawData ? rawData.wl_min : '-' }} - {{ rawData ? rawData.wl_max : '-' }} μm</span>
            <span>将使用约 {{ getRangePointCount() }} 个数据点</span>
          </div>
          
          <div class="range-presets">
            <span class="presets-label">快速选择:</span>
            <el-button size="small" @click="setRange('center')">中间1/3</el-button>
            <el-button size="small" @click="setRange('start')">前1/3</el-button>
            <el-button size="small" @click="setRange('end')">后1/3</el-button>
            <el-button size="small" @click="setRange('full')">全部</el-button>
          </div>
          
          <div class="quick-chart" ref="quickChartDom"></div>
        </div>
        
        <template #footer>
          <el-button @click="showRangeSelector = false">取消</el-button>
          <el-button type="primary" @click="applyRange">应用范围</el-button>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<script>
import * as echarts from "echarts";
import { Picture, FullScreen, InfoFilled } from "@element-plus/icons-vue";

const COLORS = {
  blue: "#165DFF",
  orange: "#FF7D00",
  green: "#00B42A",
  red: "#F53F3F",
};

export default {
  name: "SpectrumChart",
  components: { Picture, FullScreen, InfoFilled },
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
      isSelecting: false,
      startX: null,
      rangeRect: null
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
    showRangeSelector(val) {
      if (val) {
        this.$nextTick(() => {
          if (this.rawData) {
            this.rangeStart = parseFloat(this.rawData.wl_min);
            this.rangeEndInput = parseFloat(this.rawData.wl_max);
            this.initQuickChart();
}
        });
      }
    }
  },
  mounted() {
    window.addEventListener("resize", this.onResize);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.onResize);
    this.chartInst?.dispose();
    this.quickChartInst?.dispose();
  },
  methods: {
    initChart() {
      const dom = this.$refs.chartDom;
      if (!dom || dom.clientWidth === 0) return;
      if (this.chartInst) this.chartInst.dispose();
      this.chartInst = echarts.init(dom);
      
      // 绑定图表拖拽事件
      this.chartInst.getZr().on('mousedown', this.onChartMouseDown);
      this.chartInst.getZr().on('mousemove', this.onChartMouseMove);
    },
    initQuickChart() {
      const dom = this.$refs.quickChartDom;
      if (!dom || !this.rawData) return;
      if (this.quickChartInst) this.quickChartInst.dispose();
      this.quickChartInst = echarts.init(dom);
      
      const wl = this.rawData.wavelength || [];
      const ref = this.rawData.reflectance || [];
      
      this.quickChartInst.setOption({
        tooltip: { trigger: "axis" },
        grid: { left: 40, right: 20, top: 20, bottom: 40 },
        xAxis: { 
          type: "value", 
          name: "波长 (μm)",
          nameTextStyle: { fontSize: 11 },
          axisLine: { lineStyle: { color: "#E5E6EB" } },
          splitLine: { lineStyle: { color: "#F2F3F5" } }
        },
        yAxis: { 
          type: "value", 
          name: "反射率",
          nameTextStyle: { fontSize: 11 },
          axisLine: { lineStyle: { color: "#E5E6EB" } },
          splitLine: { lineStyle: { color: "#F2F3F5" } }
        },
        series: [{
          type: "line",
          data: wl.map((x, i) => [x, ref[i]]),
          lineStyle: { width: 1, color: COLORS.blue },
          symbol: "none",
          markArea: {
            silent: true,
            data: []
          }
        }]
      });
    },
    onResize() {
      this.chartInst?.resize();
      this.quickChartInst?.resize();
    },
    switchTab(tab) {
      if (tab.disabled) return;
      this.activeTab = tab.key;
      this.$nextTick(() => this.drawCurrent());
    },
    onChartMouseDown(params) {
      if (this.activeTab !== "raw") return;
      this.isSelecting = true;
      this.startX = params.offsetX;
      this.rangeRect = document.createElement("div");
      this.rangeRect.style.cssText = `
        position: absolute; 
        border: 2px dashed #165DFF; 
        background: rgba(22,93,255,0.1);
        pointer-events: none;
        z-index: 1000;
      `;
      this.$refs.chartDom.style.position = "relative";
      this.$refs.chartDom.appendChild(this.rangeRect);
    },
    onChartMouseMove(params) {
      if (!this.isSelecting || !this.rangeRect) return;
      
      const currentX = params.offsetX;
      const left = Math.min(this.startX, currentX);
      const width = Math.abs(currentX - this.startX);
      
      this.rangeRect.style.left = left + "px";
      this.rangeRect.style.top = "0";
      this.rangeRect.style.width = width + "px";
      this.rangeRect.style.height = "100%";
    },
    onChartMouseUp(params) {
      if (!this.isSelecting) return;
      this.isSelecting = false;
      
      if (this.rangeRect) {
        this.$refs.chartDom.removeChild(this.rangeRect);
        this.rangeRect = null;
      }
      
      if (!this.chartInst || !this.rawData) return;
      
      // 将像素位置转换为波长值
      const pixelX = params.offsetX;
      const point = this.chartInst.convertFromPixel('grid', [pixelX, 0]);
      
      if (point && point[0]) {
        const clickedWl = point[0];
        // 选择以点击位置为中心的一段数据
        const wl = this.rawData.wavelength || [];
        const windowSize = Math.floor(wl.length * 0.3); // 选择30%的数据
        
        let startIdx = 0;
        let endIdx = wl.length;
        
        for (let i = 0; i < wl.length; i++) {
          if (wl[i] >= clickedWl) {
            startIdx = Math.max(0, i - windowSize / 2);
            endIdx = Math.min(wl.length, i + windowSize / 2);
            break;
          }
        }
        
        this.selectedRange = {
          start: wl[startIdx],
          end: wl[endIdx - 1],
          count: endIdx - startIdx
        };
        
        this.$emit("range-selected", this.selectedRange);
      }
    },
    getRangePointCount() {
      if (!this.rawData || this.rangeStart === null || this.rangeEndInput === null) return 0;
      const wl = this.rawData.wavelength || [];
      return wl.filter(w => w >= this.rangeStart && w <= this.rangeEndInput).length;
    },
    setRange(mode) {
      if (!this.rawData) return;
      const wl = this.rawData.wavelength || [];
      const min = parseFloat(this.rawData.wl_min);
      const max = parseFloat(this.rawData.wl_max);
      const range = max - min;
      
      switch(mode) {
        case 'center':
          this.rangeStart = min + range * 0.33;
          this.rangeEndInput = min + range * 0.67;
          break;
        case 'start':
          this.rangeStart = min;
          this.rangeEndInput = min + range * 0.33;
          break;
        case 'end':
          this.rangeStart = min + range * 0.67;
          this.rangeEndInput = max;
          break;
        case 'full':
          this.rangeStart = min;
          this.rangeEndInput = max;
          break;
      }
    },
    applyRange() {
      if (this.rangeStart !== null && this.rangeEndInput !== null) {
        this.selectedRange = {
          start: this.rangeStart,
          end: this.rangeEndInput,
          count: this.getRangePointCount()
        };
        this.$emit("range-selected", this.selectedRange);
        this.$message.success(`已选择范围: ${this.rangeStart.toFixed(2)} - ${this.rangeEndInput.toFixed(2)} μm`);
      }
      this.showRangeSelector = false;
    },
    clearRange() {
      this.selectedRange = null;
      this.$emit("range-selected", null);
    },
    drawCurrent() {
      if (!this.chartInst) this.initChart();
      if (!this.chartInst) return;
      if (this.activeTab === "raw") this.drawRaw();
      else if (this.activeTab === "fit") this.drawFit();
      else if (this.activeTab === "residual") this.drawResidual();
    },
    baseGrid() {
      return { left: 60, right: 28, top: 24, bottom: 56 };
    },
    baseXAxis() {
      return {
        type: "value", name: "波长 (μm)",
        nameTextStyle: { fontSize: 12, color: "#86909C" },
        axisLine: { lineStyle: { color: "#E5E6EB" } },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: "#F2F3F5" } },
        axisLabel: {
          fontSize: 11,
          color: "#86909C",
          formatter: function(value) {
            // 优化标签显示，小数点后最多2位
            return value.toFixed(value < 10 ? 2 : value < 100 ? 1 : 0);
          }
        }
      };
    },
    // 生成dataZoom配置，支持缩放和拖拽
    baseDataZoom() {
      return [
        {
          type: 'slider',  // 滑块式缩放
          xAxisIndex: 0,
          filterMode: 'none',
          height: 24,
          bottom: 4,
          borderColor: '#E5E6EB',
          backgroundColor: '#F7F8FA',
          fillerColor: 'rgba(22,93,255,0.08)',
          handleStyle: {
            color: '#165DFF',
            borderColor: '#165DFF'
          },
          moveHandleStyle: {
            color: '#165DFF',
            backgroundColor: '#E8F3FF'
          },
          textStyle: {
            color: '#86909C',
            fontSize: 10
          },
          dataBackground: {
            lineStyle: { color: '#C9CDD4' },
            areaStyle: { color: '#F2F3F5' }
          },
          selectedDataBackground: {
            lineStyle: { color: '#165DFF' },
            areaStyle: { color: 'rgba(22,93,255,0.05)' }
          },
          brushSelect: false
        },
        {
          type: 'inside',  // 内置缩放（鼠标滚轮/双指）
          xAxisIndex: 0,
          zoomOnMouseWheel: true,
          moveOnMouseMove: true,
          moveOnMouseWheel: false
        }
      ];
    },
    drawRaw() {
      if (!this.rawData) return;
      const wl = this.rawData.wavelength || [];
      const ref = this.rawData.reflectance || [];
      
      // 高亮显示已选择的范围
      let markArea = [];
      if (this.selectedRange) {
        markArea = [
          [
            { xAxis: this.selectedRange.start, itemStyle: { color: 'rgba(22,93,255,0.08)' } },
            { xAxis: this.selectedRange.end }
          ]
        ];
      }
      
      const series = [{
        name: "原始光谱", type: "line",
        data: wl.map((x, i) => [x, ref[i]]),
        lineStyle: { width: 1, color: COLORS.blue },
        itemStyle: { color: COLORS.blue },
        symbol: "none",
        markArea: { silent: true, data: markArea },
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
        legend: { data: series.map((s) => s.name), bottom: 28, textStyle: { fontSize: 12, color: "#4E5969" } },
        xAxis: this.baseXAxis(),
        yAxis: { 
          type: "value", name: "反射率", nameTextStyle: { fontSize: 12, color: "#86909C" }, 
          axisLine: { lineStyle: { color: "#E5E6EB" } }, 
          splitLine: { lineStyle: { color: "#F2F3F5" } },
          axisLabel: { fontSize: 11, color: "#86909C" }
        },
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
        legend: { data: ["实验数据", "模型拟合"], bottom: 28, textStyle: { fontSize: 12, color: "#4E5969" } },
        xAxis: this.baseXAxis(),
        yAxis: { 
          type: "value", name: "反射率", nameTextStyle: { fontSize: 12, color: "#86909C" }, 
          axisLine: { lineStyle: { color: "#E5E6EB" } }, 
          splitLine: { lineStyle: { color: "#F2F3F5" } },
          axisLabel: { fontSize: 11, color: "#86909C" }
        },
        grid: this.baseGrid(),
        dataZoom: this.baseDataZoom(),
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
        yAxis: { 
          type: "value", name: "残差", nameTextStyle: { fontSize: 12, color: "#86909C" }, 
          axisLine: { lineStyle: { color: "#E5E6EB" } }, 
          splitLine: { lineStyle: { color: "#F2F3F5" } },
          axisLabel: { fontSize: 11, color: "#86909C" }
        },
        grid: { ...this.baseGrid(), bottom: 28 },
        dataZoom: this.baseDataZoom(),
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

.chart-empty {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  color: #C9CDD4; gap: 8px;
}
.empty-title { font-size: 15px; font-weight: 500; color: #86909C; }
.empty-desc { font-size: 13px; color: #A8ADB5; }

.chart-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px 0;
  flex-shrink: 0;
}
.toolbar-tabs {
  display: flex; gap: 4px; background: #F2F3F5;
  border-radius: 6px; padding: 3px;
}
.toolbar-actions { display: flex; gap: 8px; }
.toolbar-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #86909C;
  background: #F7F8FA;
  padding: 4px 10px;
  border-radius: 4px;
}
.toolbar-hint .el-icon { color: #165DFF; }
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

.range-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #E8F3FF;
  border-bottom: 1px solid #B8D4FF;
  font-size: 12px;
}
.range-label { color: #4E5969; }
.range-value { color: #165DFF; font-weight: 600; }
.range-points { color: #86909C; }

.chart-body { flex: 1; min-height: 0; padding: 8px; }
.chart-box { width: 100%; height: 100%; }

/* 范围选择器弹窗 */
.range-selector-modal { padding: 10px 0; }
.selector-desc { font-size: 13px; color: #86909C; margin-bottom: 16px; }

.range-inputs {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}
.input-group { flex: 1; }
.input-group label {
  display: block;
  font-size: 12px;
  color: #4E5969;
  margin-bottom: 6px;
}
.input-separator { font-size: 18px; color: #86909C; }

.range-info {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #86909C;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #F7F8FA;
  border-radius: 6px;
}

.range-presets {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.presets-label { font-size: 12px; color: #4E5969; }

.quick-chart {
  width: 100%;
  height: 200px;
  background: #FAFBFC;
  border-radius: 8px;
  border: 1px solid #E5E6EB;
}
</style>