<!--
  软件名称：基于多光束干涉校正的半导体外延层厚度光谱反演系统 V1.0
  组件功能：测量报告模板
  描述：生成可打印的测量分析报告，包含数据可视化图表
-->
<template>
  <div class="report-print-container" v-if="record">
    <!-- 报告头部 -->
    <div class="report-header">
      <div class="logo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>
          <path d="M2 12h20"/>
        </svg>
      </div>
      <div class="title">
        <h1>半导体薄膜厚度测量分析报告</h1>
        <p>Semi-conductor Thin Film Thickness Measurement Report</p>
      </div>
      <div class="report-version">V1.0</div>
    </div>

    <!-- 基础信息 -->
    <div class="report-section">
      <h2 class="section-title">
        <svg class="section-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
        基础信息
      </h2>
      <table class="info-table">
        <tbody>
          <tr>
            <td class="label">记录编号</td>
            <td class="value">{{ record.id }}</td>
            <td class="label">创建时间</td>
            <td class="value">{{ formatTime(record.created_at || record.calc_time) }}</td>
          </tr>
          <tr>
            <td class="label">薄膜编号</td>
            <td class="value film-code">{{ record.film_code }}</td>
            <td class="label">基底材料</td>
            <td class="value">
              <span class="material-badge" :class="getMaterialClass(record.material_type)">
                {{ getMaterialName(record.material_type) }}
              </span>
            </td>
          </tr>
          <tr>
            <td class="label">入射角</td>
            <td class="value">{{ record.theta_deg || 10 }}°</td>
            <td class="label">测量波长范围</td>
            <td class="value">{{ getWavelengthRange() }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 测量结果 -->
    <div class="report-section">
      <h2 class="section-title">
        <svg class="section-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
        测量结果
      </h2>
      <div class="results-grid">
        <div class="result-card primary">
          <div class="res-label">拟合厚度</div>
          <div class="res-value">{{ record.thickness_um ? record.thickness_um.toFixed(4) : '-' }}</div>
          <div class="res-unit">μm</div>
        </div>
        <div class="result-card">
          <div class="res-label">拟合优度 R²</div>
          <div class="res-value" :class="getR2Class(record.r_squared)">
            {{ record.r_squared ? record.r_squared.toFixed(4) : '-' }}
          </div>
          <div class="res-indicator" :class="getR2Class(record.r_squared)">
            {{ getR2Level(record.r_squared) }}
          </div>
        </div>
        <div class="result-card">
          <div class="res-label">干涉等级</div>
          <div class="res-value level">{{ getInterferenceLabel(record.multi_beam_level) }}</div>
          <div class="res-badge">{{ getInterferenceBadge(record.multi_beam_level) }}</div>
        </div>
        <div class="result-card" v-if="record.init_thickness_um">
          <div class="res-label">初估厚度</div>
          <div class="res-value">{{ record.init_thickness_um.toFixed(4) }}</div>
          <div class="res-unit">μm</div>
        </div>
      </div>
    </div>

    <!-- 数据质量指标 -->
    <div class="report-section" v-if="getDataQuality()">
      <h2 class="section-title">
        <svg class="section-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
        数据质量
      </h2>
      <div class="quality-grid">
        <div class="quality-item">
          <span class="quality-label">数据点数</span>
          <span class="quality-value">{{ getDataCount() }}</span>
        </div>
        <div class="quality-item">
          <span class="quality-label">信噪比估计</span>
          <span class="quality-value">{{ getDataQuality().snr }}</span>
        </div>
        <div class="quality-item">
          <span class="quality-label">波峰数量</span>
          <span class="quality-value">{{ getDataQuality().peaks }}</span>
        </div>
        <div class="quality-item">
          <span class="quality-label">波谷数量</span>
          <span class="quality-value">{{ getDataQuality().valleys }}</span>
        </div>
      </div>
    </div>

    <!-- 光谱拟合图表 -->
    <div class="report-section page-break">
      <h2 class="section-title">
        <svg class="section-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99z"/></svg>
        光谱拟合分析
      </h2>
      <div class="chart-wrapper">
        <div ref="chartRef" class="print-chart"></div>
      </div>
      <div class="chart-legend">
        <div class="legend-item">
          <span class="legend-dot exp"></span>
          <span>实测数据 (Experimental Data)</span>
        </div>
        <div class="legend-item">
          <span class="legend-line fit"></span>
          <span>拟合曲线 (Fitted Curve)</span>
        </div>
      </div>
    </div>

    <!--测量方法说明 -->
    <div class="report-section">
      <h2 class="section-title">
        <svg class="section-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
        测量方法说明
      </h2>
      <div class="method-box">
        <p>本测量基于<strong>多光束干涉原理</strong>，通过分析反射光谱的干涉条纹特征，实现薄膜厚度的非接触式精确测量。</p>
        <ul>
          <li>采用双光束干涉模型进行正演计算</li>
          <li>使用非线性最小二乘法拟合优化厚度参数</li>
          <li>通过反射率对比度判定多光束干涉等级</li>
          <li>支持 8 种主流半导体材料的折射率计算</li>
        </ul>
      </div>
    </div>

    <!-- 报告页脚 -->
    <div class="report-footer">
      <div class="footer-info">
        <span>报告生成时间: {{ new Date().toLocaleString() }}</span>
        <span>|</span>
        <span>SI Thickness Analysis System V1.0</span>
      </div>
      <p class="disclaimer">声明：本报告由系统自动生成，仅供科研与生产参考，不作为法律效力依据。</p>
    </div>
  </div>
  <div v-else class="no-record">暂无记录数据</div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from "vue";
import * as echarts from "echarts";

const props = defineProps({
  record: { type: Object, default: null }
});

const chartRef = ref(null);
let myChart = null;
let resizeObserver = null;

// 材料名称映射
const materialNames = {
  'SIC': '碳化硅 (4H-SiC)',
  'SI': '硅 (Si)',
  'GAN': '氮化镓 (GaN)',
  'ALN': '氮化铝 (AlN)',
  'INP': '磷化铟 (InP)',
  'GAAS': '砷化镓 (GaAs)',
  'ZNO': '氧化锌 (ZnO)',
  'C': '金刚石 (C)'
};

const formatTime = (timeStr) => {
  if (!timeStr) return "-";
  return new Date(timeStr).toLocaleString();
};

const getMaterialName = (type) => {
  if (!type) return '-';
  return materialNames[type.toUpperCase()] || type;
};

const getMaterialClass = (type) => {
  if (!type) return '';
  return 'material-' + type.toLowerCase().replace(' ', '-');
};

const getWavelengthRange = () => {
  if (!props.record?.data?.wavelength?.length) return '-';
  const wl = props.record.data.wavelength;
  const min = Math.min(...wl).toFixed(2);
  const max = Math.max(...wl).toFixed(2);
  return `${min} - ${max} μm`;
};

const getDataCount = () => {
  if (!props.record?.data?.wavelength) return 0;
  return props.record.data.wavelength.length;
};

const getR2Class = (r2) => {
  if (!r2) return '';
  if (r2 >= 0.99) return 'excellent';
  if (r2 >= 0.95) return 'good';
  if (r2 >= 0.8) return 'fair';
  return 'poor';
};

const getR2Level = (r2) => {
  if (!r2) return '-';
  if (r2 >= 0.99) return '优秀';
  if (r2 >= 0.95) return '良好';
  if (r2 >= 0.8) return '一般';
  return '较差';
};

const getInterferenceLabel = (level) => {
  if (!level) return '-';
  return level;
};

const getInterferenceBadge = (level) => {
  if (!level) return '';
  if (level.includes('强')) return '强';
  if (level.includes('中')) return '中';
  return '弱';
};

const getDataQuality = () => {
  if (!props.record?.data) return null;
  const wl = props.record.data.wavelength || [];
  const ref = props.record.data.reflectance || [];
  if (wl.length === 0) return null;
  
  // 简单估计波峰波谷
  let peaks = 0, valleys = 0;
  for (let i = 1; i < ref.length - 1; i++) {
    if (ref[i] > ref[i-1] && ref[i] > ref[i+1]) peaks++;
    if (ref[i] < ref[i-1] && ref[i] < ref[i+1]) valleys++;
  }
  
  // 估计信噪比
  const mean = ref.reduce((a, b) => a + b, 0) / ref.length;
  const variance = ref.reduce((a, b) => a + (b - mean) ** 2, 0) / ref.length;
  const snr = variance > 0 ? (20 * Math.log10(Math.sqrt(variance))).toFixed(1) + ' dB' : '-';
  
  return { peaks, valleys, snr };
};

const handleResize = () => {
  if (myChart) myChart.resize();
};

const initChart = () => {
  if (!props.record || !chartRef.value) return;
  if (myChart) myChart.dispose();
  
  myChart = echarts.init(chartRef.value, null, { renderer: "svg" });
  const data = props.record.data || {};
  const wavelengths = data.wavelength || [];
  const reflectances = data.reflectance || [];
  const refFit = data.ref_fit || [];
  
  // 过滤有效数据
  const validIndices = reflectances
    .map((r, i) => (typeof r === "number" && !isNaN(r) && isFinite(r) ? i : -1))
    .filter(i => i >= 0);
  
  const expData = validIndices.map(i => [wavelengths[i], reflectances[i]]);
  const fitData = validIndices.map(i => [wavelengths[i], refFit[i] || reflectances[i]]);
  
  const option = {
    animation: false,
    backgroundColor: '#fff',
    title: { 
      text: "反射光谱拟合曲线",
      subtext: "Reflectance Spectrum Analysis",
      left: "center", 
      top: 5,
      textStyle: { fontSize: 16, color: "#1D2129", fontWeight: 600 },
      subtextStyle: { fontSize: 12, color: "#86909C" }
    },
    tooltip: { 
      trigger: "axis",
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#E5E6EB',
      textStyle: { color: '#4E5969' }
    },
    legend: { 
      bottom: 10, 
      padding: [0, 0, 0, 0],
      textStyle: { color: '#4E5969' }
    },
    grid: { top: 80, left: 60, right: 40, bottom: 60 },
    xAxis: { 
      name: "波长 (μm)", 
      type: "value",
      nameTextStyle: { fontSize: 12, color: "#86909C", padding: [5, 0, 0, 0] },
      axisLine: { lineStyle: { color: "#E5E6EB" } },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: "#F2F3F5" } },
      axisLabel: { color: '#86909C' }
    },
    yAxis: { 
      name: "反射率", 
      type: "value",
      nameTextStyle: { fontSize: 12, color: "#86909C", padding: [0, 0, 5, 0] },
      axisLine: { lineStyle: { color: "#E5E6EB" } },
      splitLine: { lineStyle: { color: "#F2F3F5" } },
      axisLabel: { color: '#86909C' }
    },
    series: [
      {
        name: "实测数据",
        type: "scatter",
        data: expData,
        symbolSize: 4,
        itemStyle: { color: "#165DFF", opacity: 0.6 }
      },
      {
        name: "拟合曲线",
        type: "line",
        data: fitData,
        symbol: "none",
        lineStyle: { color: "#F53F3F", width: 2 },
        smooth: 0.3
      }
    ]
  };
  myChart.setOption(option);
};

onMounted(() => {
  if (props.record) initChart();
  window.addEventListener("beforeprint", handleResize);
  if (chartRef.value) {
    resizeObserver = new ResizeObserver(() => handleResize());
    resizeObserver.observe(chartRef.value);
  }
});

onBeforeUnmount(() => {
  window.removeEventListener("beforeprint", handleResize);
  if (resizeObserver) resizeObserver.disconnect();
  if (myChart) myChart.dispose();
});

watch(() => props.record, () => {
  nextTick(initChart);
}, { deep: true });
</script>

<style scoped>
.report-print-container {
  width: 210mm;
  min-height: 297mm;
  padding: 15mm 20mm;
  margin: 0 auto;
  background: white;
  color: #1D2129;
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
}

.report-header {
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 3px solid #165DFF;
  padding-bottom: 12px;
  margin-bottom: 24px;
}

.logo {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #165DFF 0%, #4080FF 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
.logo svg { width: 28px; height: 28px; }

.title h1 { font-size: 20px; margin: 0; font-weight: 600; }
.title p { font-size: 11px; margin: 4px 0 0; color: #86909C; }

.report-version {
  margin-left: auto;
  padding: 4px 12px;
  background: #E8F3FF;
  color: #165DFF;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.report-section { margin-bottom: 28px; clear: both; }
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  padding-left: 10px;
  border-left: 4px solid #165DFF;
  margin-bottom: 16px;
  color: #1D2129;
}
.section-icon { width: 18px; height: 18px; color: #165DFF; }

.info-table { width: 100%; border-collapse: collapse; }
.info-table td { padding: 10px 12px; border: 1px solid #E5E6EB; font-size: 13px; }
.info-table td.label { width: 120px; background: #F7F8FA; color: #4E5969; font-weight: 500; }
.film-code { font-family: "Consolas", monospace; color: #165DFF; font-weight: 500; }

.material-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: #F0F5FF;
  color: #165DFF;
}

.results-grid { 
  display: grid; 
  grid-template-columns: repeat(4, 1fr); 
  gap: 12px;
}
.result-card {
  background: #F7F8FA;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #E5E6EB;
  text-align: center;
}
.result-card.primary { background: linear-gradient(135deg, #E8F3FF 0%, #F0F5FF 100%); border-color: #B8D4FF; }
.res-label { font-size: 12px; color: #86909C; margin-bottom: 6px; }
.res-value { font-size: 18px; font-weight: 700; color: #1D2129; }
.res-value.excellent { color: #00B42A; }
.res-value.good { color: #4080FF; }
.res-value.fair { color: #FF7D00; }
.res-value.poor { color: #F53F3F; }
.res-value.level { font-size: 14px; }
.res-unit { font-size: 12px; color: #86909C; margin-top: 2px; }
.res-indicator { font-size: 11px; color: #86909C; margin-top: 4px; }
.res-indicator.excellent { color: #00B42A; }
.res-indicator.good { color: #4080FF; }
.res-indicator.fair { color: #FF7D00; }
.res-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  margin-top: 4px;
  background: #F0F5FF;
  color: #165DFF;
}

.quality-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.quality-item {
  background: #fff;
  padding: 12px;
  border: 1px solid #E5E6EB;
  border-radius: 6px;
  text-align: center;
}
.quality-label { display: block; font-size: 11px; color: #86909C; margin-bottom: 4px; }
.quality-value { font-size: 16px; font-weight: 600; color: #1D2129; }

.chart-wrapper {
  width: 100%; 
  height: 420px;
  background: #fff;
  border: 1px solid #E5E6EB;
  border-radius: 8px;
  padding: 12px;
  box-sizing: border-box;
  page-break-inside: avoid;
}
.print-chart { width: 100%; height: 100%; }

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 12px;
  padding: 8px;
  background: #F7F8FA;
  border-radius: 6px;
}
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #4E5969; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }
.legend-dot.exp { background: #165DFF; }
.legend-line { width: 20px; height: 2px; }
.legend-line.fit { background: #F53F3F; }

.method-box {
  background: #F7F8FA;
  padding: 16px 20px;
  border-radius: 8px;
  border: 1px solid #E5E6EB;
  font-size: 13px;
  line-height: 1.8;
}
.method-box p { margin: 0 0 12px; }
.method-box ul { margin: 0; padding-left: 20px; }
.method-box li { margin-bottom: 4px; }

.report-footer {
  margin-top: 40px;
  padding-top: 16px;
  border-top: 1px solid #E5E6EB;
  text-align: center;
}
.footer-info {
  display: flex;
  justify-content: center;
  gap: 12px;
  font-size: 11px;
  color: #86909C;
  margin-bottom: 8px;
}
.disclaimer { font-size: 10px; color: #C9CDD4; font-style: italic; }

.no-record {
  padding: 40px;
  text-align: center;
  color: #86909C;
  font-size: 14px;
}

@media print {
  .page-break { page-break-before: always; }
  .report-print-container { padding: 0; margin: 0; width: 100%; }
  .chart-wrapper { page-break-inside: avoid; }
}
</style>