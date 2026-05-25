<!--
  预处理：波长区间、滤波、ALS 与 SiC 带剔除
-->
<template>
  <div class="preprocess-panel">
    <!-- 数据范围选择 -->
    <div class="form-group">
      <label class="form-label">
        <el-icon><FullScreen /></el-icon>
        数据范围选择
        <el-tag size="small" type="info">可选</el-tag>
      </label>
      <div class="range-selector">
        <div class="range-mode-tabs">
          <el-radio-group v-model="rangeMode" size="small">
            <el-radio-button label="manual">手动输入</el-radio-button>
            <el-radio-button label="auto">自动最优</el-radio-button>
            <el-radio-button label="full">使用全部</el-radio-button>
          </el-radio-group>
        </div>
        
        <div v-if="rangeMode === 'manual'" class="range-inputs">
          <div class="range-input-group">
            <label>起始波长 (μm)</label>
            <el-input-number
              v-model="rangeStart"
              :min="rawData ? rawData.wl_min : 0"
              :max="rangeEnd || 20"
              :step="0.1"
              :precision="2"
              size="small"
              controls-position="right"
            />
          </div>
          <div class="range-separator">—</div>
          <div class="range-input-group">
            <label>结束波长 (μm)</label>
            <el-input-number
              v-model="rangeEnd"
              :min="rangeStart || 0"
              :max="rawData ? rawData.wl_max : 20"
              :step="0.1"
              :precision="2"
              size="small"
              controls-position="right"
            />
          </div>
        </div>
        
        <div v-if="rangeMode === 'manual'" class="range-hint">
          <span class="data-info">数据范围: {{ rawData ? rawData.wl_min : '-' }} - {{ rawData ? rawData.wl_max : '-' }} μm</span>
          <span class="point-count">将使用约 {{ getSelectedPointCount() }} 个数据点</span>
        </div>
        
        <div v-if="rangeMode === 'auto'" class="auto-range-options">
          <div class="option-item">
            <span class="option-label">最小数据点数</span>
            <el-input-number v-model="minPoints" :min="30" :max="200" :step="10" size="small" controls-position="right" />
          </div>
          <div class="option-item">
            <span class="option-label">扫描窗口</span>
            <el-input-number v-model="scanWindow" :min="50" :max="500" :step="50" size="small" controls-position="right" />
          </div>
          <div class="option-hint">
            系统将自动寻找干涉条纹最清晰、数据质量最好的区间进行分析
          </div>
        </div>
        
        <div v-if="rangeMode === 'full'" class="full-range-info">
          <el-icon><InfoFilled /></el-icon>
          <span>将使用全部 {{ rawData ? rawData.row_count : 0 }} 个数据点进行拟合</span>
        </div>
      </div>
    </div>

    <!-- 滤波方法选择 -->
    <div class="form-group">
      <label class="form-label">滤波方法</label>
      <div class="method-toggle">
        <button
          :class="['method-btn', { active: method === 'sg' }]"
          @click="method = 'sg'"
        >
          <el-icon :size="16"><Filter /></el-icon>
          <span>Savitzky-Golay</span>
        </button>
        <button
          :class="['method-btn', { active: method === 'ma' }]"
          @click="method = 'ma'"
        >
          <el-icon :size="16"><TrendCharts /></el-icon>
          <span>滑动平均 (MA)</span>
        </button>
      </div>
    </div>

    <!-- 窗口大小 -->
    <div class="form-group">
      <div class="form-label-row">
        <label class="form-label">窗口大小</label>
        <span class="form-value-tag">{{ window === 0 ? '自动' : window }}</span>
      </div>
      <el-slider
        v-model="window"
        :min="0"
        :max="51"
        :step="2"
        :marks="{ 0: '自动', 5: '5', 15: '15', 31: '31', 51: '51' }"
      />
    </div>

    <!-- 归一化 -->
    <div class="form-group inline-group">
      <label class="form-label">归一化</label>
      <el-switch v-model="normalize" size="small" />
      <span class="inline-hint">{{ normalize ? '映射到 [0, 1]' : '原始量纲' }}</span>
    </div>

    <div class="form-group inline-group">
      <label class="form-label">ALS 基线</label>
      <el-switch v-model="useAls" size="small" />
    </div>

    <div class="form-group inline-group">
      <label class="form-label">SiC 剩余射线剔除</label>
      <el-switch v-model="maskReststrahlen" size="small" />
    </div>

    <!-- 操作按钮 -->
    <el-button
      type="primary"
      :disabled="!rawData"
      :loading="processing"
      @click="doPreprocess"
      class="action-btn"
      size="large"
    >
      <el-icon v-if="!processing"><VideoPlay /></el-icon>
      {{ processing ? "处理中..." : "执行预处理与分析" }}
    </el-button>
  </div>
</template>

<script>
import { Filter, TrendCharts, VideoPlay, FullScreen, InfoFilled } from "@element-plus/icons-vue";
import { preprocess } from "../api/index.js";

export default {
  name: "PreprocessPanel",
  components: { Filter, TrendCharts, VideoPlay, FullScreen, InfoFilled },
  props: {
    rawData: { type: Object, default: null },
    chartRange: { type: Object, default: null },
  },
  emits: ["preprocessed"],
  data() {
    return {
      rangeMode: "full",
      rangeStart: null,
      rangeEnd: null,
      minPoints: 50,
      scanWindow: 100,
      method: "sg",
      window: 0,
      normalize: false,
      useAls: false,
      maskReststrahlen: false,
      processing: false
    };
  },
  watch: {
    rawData: {
      handler(newData) {
        if (newData) {
          this.rangeStart = parseFloat(newData.wl_min) || null;
          this.rangeEnd = parseFloat(newData.wl_max) || null;
        }
      },
      immediate: true
    },
    chartRange(val) {
      if (val && val.start != null && val.end != null) {
        this.rangeMode = "manual";
        this.rangeStart = val.start;
        this.rangeEnd = val.end;
      }
    }
  },
  methods: {
    getSelectedPointCount() {
      if (!this.rawData || !this.rawData.wavelength) return 0;
      if (this.rangeMode === 'full') return this.rawData.wavelength.length;
      
      const start = this.rangeStart;
      const end = this.rangeEnd;
      if (!start || !end) return this.rawData.wavelength.length;
      
      return this.rawData.wavelength.filter(wl => wl >= start && wl <= end).length;
    },
    async doPreprocess() {
      if (!this.rawData) return;
      this.processing = true;
      
      try {
        let wavelength = [...this.rawData.wavelength];
        let reflectance = [...this.rawData.reflectance];
        
        // 根据范围模式处理数据
        if (this.rangeMode === 'manual') {
          const start = this.rangeStart;
          const end = this.rangeEnd;
          if (start !== null && end !== null) {
            const indices = [];
            for (let i = 0; i < wavelength.length; i++) {
              if (wavelength[i] >= start && wavelength[i] <= end) {
                indices.push(i);
              }
            }
            wavelength = indices.map(i => wavelength[i]);
            reflectance = indices.map(i => reflectance[i]);
          }
        } else if (this.rangeMode === 'auto') {
          // 自动最优区间选择
          const result = this.findOptimalRange(wavelength, reflectance, this.minPoints, this.scanWindow);
          wavelength = result.wavelength;
          reflectance = result.reflectance;
          this.$message.info(`自动选择区间: ${result.start.toFixed(2)} - ${result.end.toFixed(2)} μm (${wavelength.length} 个点)`);
        }
        
        const res = await preprocess({
          wavelength: wavelength,
          reflectance: reflectance,
          material: this.rawData.suggested_material || "SIC",
          method: this.method,
          window: this.window,
          normalize: this.normalize,
          use_als: this.useAls,
          mask_reststrahlen: this.maskReststrahlen,
        });
        
        if (res.data.success) {
          if (res.data.used_window) {
            this.$message.info(`平滑窗口: ${res.data.used_window}`);
          }
          // 确定实际使用的数据范围
          let actualStart, actualEnd;
          if (this.rangeMode === 'full') {
            actualStart = this.rawData.wl_min;
            actualEnd = this.rawData.wl_max;
          } else if (this.rangeMode === 'manual') {
            actualStart = this.rangeStart;
            actualEnd = this.rangeEnd;
          } else {
            // auto模式，从findOptimalRange结果获取
            actualStart = wavelength[0];
            actualEnd = wavelength[wavelength.length - 1];
          }
          
          // 将选择的数据范围信息传递给父组件
          const rangeInfo = {
            ...res.data.data,
            // 传递原始数据范围（完整数据）
            wl_min: this.rawData.wl_min,
            wl_max: this.rawData.wl_max,
            // 传递实际拟合范围（选择后的数据）
            wl_range_start: actualStart,
            wl_range_end: actualEnd,
            rangeMode: this.rangeMode,
            // 传递完整数据供图表展示
            full_wavelength: [...this.rawData.wavelength],
            full_reflectance: [...this.rawData.reflectance]
          };
          this.$emit("preprocessed", rangeInfo);
          this.$message.success("预处理完成");
        } else {
          this.$message.error(res.data.error || "预处理失败");
        }
      } catch (e) {
        this.$message.error("请求失败: " + e.message);
      } finally {
        this.processing = false;
      }
    },
    findOptimalRange(wavelength, reflectance, minPoints, scanWindow) {
      // 自动寻找最优拟合区间
      // 算法：计算每段数据的干涉对比度，选择对比度最高的区间
      
      const n = wavelength.length;
      if (n <= minPoints) {
        return { wavelength, reflectance, start: wavelength[0], end: wavelength[n-1] };
      }
      
      let bestStart = 0;
      let bestEnd = n - 1;
      let bestContrast = 0;
      
      // 滑动窗口扫描
      for (let i = 0; i <= n - minPoints; i += Math.floor(scanWindow / 4)) {
        for (let j = i + minPoints; j < n; j += Math.floor(scanWindow / 4)) {
          const segment = reflectance.slice(i, j);
          const refMax = Math.max(...segment);
          const refMin = Math.min(...segment);
          const contrast = (refMax - refMin) / (refMax + refMin + 1e-6);
          
          if (contrast > bestContrast) {
            bestContrast = contrast;
            bestStart = i;
            bestEnd = j;
          }
        }
      }
      
      // 精细调整边界
      let left = bestStart;
      let right = bestEnd;
      
      // 向左微调
      while (left < bestStart + 20 && left < n - minPoints) {
        const segment = reflectance.slice(left, bestEnd);
        const contrast = (Math.max(...segment) - Math.min(...segment)) / (Math.max(...segment) + Math.min(...segment) + 1e-6);
        if (contrast > bestContrast * 0.95) {
          bestStart = left;
        }
        left++;
      }
      
      // 向右微调
      while (right > bestEnd - 20 && right > bestStart + minPoints) {
        const segment = reflectance.slice(bestStart, right);
        const contrast = (Math.max(...segment) - Math.min(...segment)) / (Math.max(...segment) + Math.min(...segment) + 1e-6);
        if (contrast > bestContrast * 0.95) {
          bestEnd = right;
        }
        right--;
      }
      
      return {
        wavelength: wavelength.slice(bestStart, bestEnd),
        reflectance: reflectance.slice(bestStart, bestEnd),
        start: wavelength[bestStart],
        end: wavelength[bestEnd - 1]
      };
    }
  },
};
</script>

<style scoped>
.preprocess-panel { display: flex; flex-direction: column; gap: 20px; }

.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group.inline-group { flex-direction: row; align-items: center; gap: 12px; }
.form-label { 
  font-size: 13px; 
  font-weight: 500; 
  color: #4E5969; 
  display: flex;
  align-items: center;
  gap: 6px;
}
.form-label-row { display: flex; justify-content: space-between; align-items: center; }
.form-value-tag {
  font-size: 12px; font-weight: 600; color: var(--color-primary, #165DFF);
  background: #E8F3FF; padding: 2px 8px; border-radius: 4px;
}
.inline-hint { font-size: 12px; color: #86909C; }

/* 数据范围选择器 */
.range-selector {
  background: #F7F8FA;
  border: 1px solid #E5E6EB;
  border-radius: 8px;
  padding: 12px;
}

.range-mode-tabs { margin-bottom: 12px; }

.range-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.range-input-group {
  flex: 1;
}
.range-input-group label {
  display: block;
  font-size: 11px;
  color: #86909C;
  margin-bottom: 4px;
}

.range-separator {
  color: #86909C;
  font-size: 14px;
  flex-shrink: 0;
}

.range-hint {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #86909C;
  padding-top: 8px;
  border-top: 1px dashed #E5E6EB;
}

.auto-range-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
}
.option-label { font-size: 12px; color: #4E5969; flex-shrink: 0; width: 80px; }

.option-hint {
  font-size: 11px;
  color: #86909C;
  padding: 8px 10px;
  background: #fff;
  border-radius: 6px;
  line-height: 1.5;
}

.full-range-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #4E5969;
}

.method-toggle {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
}
.method-btn {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 10px 8px; border: 1px solid #E5E6EB; border-radius: 8px;
  background: #fff; font-size: 13px; color: #4E5969; cursor: pointer;
  transition: all 0.2s; font-family: inherit;
}
.method-btn:hover { border-color: #B8D4FF; background: #F7FAFF; }
.method-btn.active {
  border-color: var(--color-primary, #165DFF);
  background: #E8F3FF; color: var(--color-primary, #165DFF); font-weight: 500;
  box-shadow: 0 0 0 2px rgba(22,93,255,0.1);
}
.method-btn .el-icon { flex-shrink: 0; }

.action-btn {
  width: 100%; border-radius: 8px; font-weight: 500;
  height: 40px; letter-spacing: 0.5px;
}
</style>