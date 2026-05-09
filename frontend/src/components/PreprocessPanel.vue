<template>
  <div class="preprocess-panel">
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
        <span class="form-value-tag">{{ window }}</span>
      </div>
      <el-slider
        v-model="window"
        :min="5"
        :max="51"
        :step="2"
        :marks="{ 5: '5', 15: '15', 31: '31', 51: '51' }"
      />
    </div>

    <!-- 归一化 -->
    <div class="form-group inline-group">
      <label class="form-label">归一化</label>
      <el-switch v-model="normalize" size="small" />
      <span class="inline-hint">{{ normalize ? '映射到 [0, 1] 区间' : '保持原始量纲' }}</span>
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
      {{ processing ? "处理中..." : "执行平滑与极值提取" }}
    </el-button>
  </div>
</template>

<script>
import { Filter, TrendCharts, VideoPlay } from "@element-plus/icons-vue";
import { preprocess } from "../api/index.js";

export default {
  name: "PreprocessPanel",
  components: { Filter, TrendCharts, VideoPlay },
  props: { rawData: { type: Object, default: null } },
  emits: ["preprocessed"],
  data() {
    return { method: "sg", window: 15, normalize: false, processing: false };
  },
  methods: {
    async doPreprocess() {
      if (!this.rawData) return;
      this.processing = true;
      try {
        const res = await preprocess({
          wavelength: this.rawData.wavelength,
          reflectance: this.rawData.reflectance,
          method: this.method, window: this.window, normalize: this.normalize,
        });
        if (res.data.success) {
          this.$emit("preprocessed", res.data.data);
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
  },
};
</script>

<style scoped>
.preprocess-panel { display: flex; flex-direction: column; gap: 20px; }

.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group.inline-group { flex-direction: row; align-items: center; gap: 12px; }
.form-label { font-size: 13px; font-weight: 500; color: #4E5969; }
.form-label-row { display: flex; justify-content: space-between; align-items: center; }
.form-value-tag {
  font-size: 12px; font-weight: 600; color: var(--color-primary, #165DFF);
  background: #E8F3FF; padding: 2px 8px; border-radius: 4px;
}
.inline-hint { font-size: 12px; color: #86909C; }

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
