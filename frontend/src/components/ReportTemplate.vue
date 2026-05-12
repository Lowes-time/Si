<template>
  <div class="report-print-container" v-if="record">
    <div class="report-header">
      <div class="logo">SI</div>
      <div class="title">
        <h1>半导体薄膜厚度测量分析报告</h1>
        <p>Semi-conductor Thin Film Thickness Measurement Report</p>
      </div>
    </div>

    <div class="report-section">
      <h2 class="section-title">1. 基础信息 / Basic Information</h2>
      <table class="info-table">
        <tr>
          <td class="label">记录编号 (ID):</td>
          <td class="value">{{ record.id }}</td>
          <td class="label">测量时间 (Time):</td>
          <td class="value">{{ formatTime(record.calc_time) }}</td>
        </tr>
        <tr>
          <td class="label">源文件名 (File):</td>
          <td class="value">{{ record.filename }}</td>
          <td class="label">基底材料 (Material):</td>
          <td class="value">{{ record.material }}</td>
        </tr>
      </table>
    </div>

    <div class="report-section">
      <h2 class="section-title">2. 测量结果 / Measurement Results</h2>
      <div class="results-grid">
        <div class="result-card">
          <div class="res-label">拟合厚度 (Thickness)</div>
          <div class="res-value highlight">{{ record.thickness_um.toFixed(4) }} <span>μm</span></div>
        </div>
        <div class="result-card">
          <div class="res-label">拟合优度 (R²)</div>
          <div class="res-value">{{ record.r_squared.toFixed(4) }}</div>
        </div>
        <div class="result-card">
          <div class="res-label">干涉判定 (Level)</div>
          <div class="res-value">{{ record.multi_beam_level }}</div>
        </div>
      </div>
    </div>

    <div class="report-section page-break">
      <h2 class="section-title">3. 光谱拟合分析 / Spectral Fitting Analysis</h2>
      <div class="chart-wrapper">
        <div ref="chartRef" class="print-chart"></div>
      </div>
    </div>

    <div class="report-footer">
      <p>报告生成时间: {{ new Date().toLocaleString() }} | SI Thickness Analysis System V1.0</p>
      <p class="disclaimer">注：本报告由系统自动生成，仅供科研与生产参考。</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  record: { type: Object, default: null }
});

const chartRef = ref(null);
let myChart = null;
let resizeObserver = null;

const formatTime = (timeStr) => {
  return new Date(timeStr).toLocaleString();
};

const handleResize = () => {
  if (myChart) {
    myChart.resize();
  }
};

const initChart = () => {
  if (!props.record || !chartRef.value) return;
  if (myChart) myChart.dispose();
  
  myChart = echarts.init(chartRef.value, null, { renderer: 'svg' });
  const data = props.record.data;
  
  const option = {
    animation: false, // 打印不需要动画
    title: { 
      text: '反射光谱拟合曲线 (Reflectance Spectrum Analysis)', 
      left: 'center', 
      top: 0,
      textStyle: { fontSize: 16, color: '#1D2129' },
      padding: [10, 0, 20, 0]
    },
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, padding: [20, 0, 0, 0] },
    grid: { top: 70, left: 60, right: 40, bottom: 70 },
    xAxis: { 
      name: '波长 (μm)', 
      type: 'value',
      nameTextStyle: { fontSize: 12, color: '#86909C' },
      axisLine: { lineStyle: { color: '#E5E6EB' } },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#F2F3F5' } }
    },
    yAxis: { 
      name: '反射率', 
      type: 'value',
      nameTextStyle: { fontSize: 12, color: '#86909C' },
      axisLine: { lineStyle: { color: '#E5E6EB' } },
      splitLine: { lineStyle: { color: '#F2F3F5' } }
    },
    series: [
      {
        name: '实测数据 (Exp)',
        type: 'scatter',
        data: data.wavelength.map((w, i) => [w, data.reflectance[i]]),
        symbolSize: 3,
        itemStyle: { color: '#165DFF', opacity: 0.5 }
      },
      {
        name: '拟合曲线 (Fit)',
        type: 'line',
        data: data.wavelength.map((w, i) => [w, data.ref_fit[i]]),
        symbol: 'none',
        lineStyle: { color: '#F53F3F', width: 2 },
        smooth: true
      }
    ]
  };
  myChart.setOption(option);
};

onMounted(() => {
  if (props.record) initChart();
  window.addEventListener('beforeprint', handleResize);
  
  if (chartRef.value) {
    resizeObserver = new ResizeObserver(() => {
      handleResize();
    });
    resizeObserver.observe(chartRef.value);
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('beforeprint', handleResize);
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
  if (myChart) {
    myChart.dispose();
  }
});

watch(() => props.record, () => {
  nextTick(initChart);
}, { deep: true });
</script>

<style scoped>
.report-print-container {
  width: 210mm;
  min-height: 297mm;
  padding: 20mm;
  margin: 0 auto;
  background: white;
  color: #1D2129;
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
}

.report-header {
  display: flex;
  align-items: center;
  gap: 20px;
  border-bottom: 2px solid #165DFF;
  padding-bottom: 15px;
  margin-bottom: 30px;
}

.logo {
  width: 50px; height: 50px; background: #165DFF; color: white;
  display: flex; align-items: center; justify-content: center;
  font-weight: bold; font-size: 24px; border-radius: 8px;
}

.title h1 { font-size: 22px; margin: 0; color: #1D2129; }
.title p { font-size: 12px; margin: 5px 0 0; color: #86909C; }

.report-section { margin-bottom: 40px; clear: both; }
.section-title {
  font-size: 18px; font-weight: 600; padding-left: 12px;
  border-left: 5px solid #165DFF; margin-bottom: 20px;
  color: #1D2129;
}

.info-table { width: 100%; border-collapse: collapse; margin-bottom: 10px; table-layout: fixed; }
.info-table td { padding: 12px; border: 1px solid #E5E6EB; font-size: 14px; word-wrap: break-word; }
.info-table td.label { width: 160px; background: #F7F8FA; color: #4E5969; font-weight: 500; }

.results-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-bottom: 10px; }
.result-card {
  background: #F7F8FA; padding: 20px; border-radius: 8px; border: 1px solid #E5E6EB;
  text-align: center;
}
.res-label { font-size: 13px; color: #86909C; margin-bottom: 10px; }
.res-value { font-size: 20px; font-weight: 700; color: #1D2129; }
.res-value span { font-size: 14px; font-weight: normal; margin-left: 4px; }
.res-value.highlight { color: #165DFF; }

.chart-wrapper { 
  width: 100%; 
  height: 550px; 
  margin-top: 40px; 
  margin-bottom: 20px;
  background: #fff;
  padding: 20px;
  box-sizing: border-box;
  page-break-inside: avoid;
}
.print-chart { width: 100%; height: 100%; min-height: 500px; }

.report-footer {
  margin-top: 60px; padding-top: 20px; border-top: 1px solid #E5E6EB;
  text-align: center; font-size: 12px; color: #86909C;
}
.disclaimer { margin-top: 8px; font-style: italic; }

@media print {
  .page-break { page-break-before: always; }
  .report-print-container { padding: 0; margin: 0; width: 100%; }
}
</style>
