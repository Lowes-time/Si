<template>
  <div class="calculation-panel">
    <!-- 材料选择 -->
    <div class="form-group">
      <label class="form-label">基底材料</label>
      <div class="material-cards">
        <div
          :class="['material-card', { active: material === 'SiC' }]"
          @click="material = 'SiC'"
        >
          <div class="mc-icon">SiC</div>
          <div class="mc-info">
            <div class="mc-name">碳化硅</div>
            <div class="mc-desc">SiC 基底</div>
          </div>
          <el-icon v-if="material === 'SiC'" class="mc-check" :size="18"><CircleCheckFilled /></el-icon>
        </div>
        <div
          :class="['material-card', { active: material === 'Si' }]"
          @click="material = 'Si'"
        >
          <div class="mc-icon">Si</div>
          <div class="mc-info">
            <div class="mc-name">硅</div>
            <div class="mc-desc">Si 基底</div>
          </div>
          <el-icon v-if="material === 'Si'" class="mc-check" :size="18"><CircleCheckFilled /></el-icon>
        </div>
      </div>
    </div>

    <!-- 入射角 -->
    <div class="form-group">
      <label class="form-label">入射角</label>
      <div class="angle-input-wrap">
        <el-input-number
          v-model="thetaDeg"
          :min="0"
          :max="89"
          :step="1"
          :precision="1"
          controls-position="right"
          size="large"
          class="angle-input"
        />
        <span class="angle-unit">°</span>
      </div>
    </div>

    <!-- 操作按钮 -->
    <el-button
      type="primary"
      :disabled="!rawData"
      :loading="calculating"
      @click="doCalculate"
      class="action-btn"
      size="large"
    >
      <el-icon v-if="!calculating"><Cpu /></el-icon>
      {{ calculating ? "拟合计算中..." : "执行厚度拟合与反演" }}
    </el-button>

    <transition name="el-fade-in">
      <div v-if="hasResult" class="export-row">
        <el-button
          type="default"
          @click="$emit('export')"
          class="export-btn"
        >
          <el-icon><Download /></el-icon>
          Excel
        </el-button>
        <el-button
          type="primary"
          @click="$emit('save', material)"
          class="save-btn"
          plain
        >
          <el-icon><FolderAdd /></el-icon>
          保存入库
        </el-button>
      </div>
    </transition>
  </div>
</template>

<script>
import { CircleCheckFilled, Cpu, Download, FolderAdd } from "@element-plus/icons-vue";
import { calculate } from "../api/index.js";

export default {
  name: "CalculationPanel",
  components: { CircleCheckFilled, Cpu, Download, FolderAdd },
  props: { rawData: { type: Object, default: null } },
  emits: ["calculated", "export", "save"],
  data() {
    return { material: "SiC", thetaDeg: 10.0, calculating: false, hasResult: false };
  },
  methods: {
    async doCalculate() {
      if (!this.rawData) return;
      this.calculating = true;
      this.hasResult = false;
      try {
        const res = await calculate({
          wavelength: this.rawData.wavelength,
          reflectance: this.rawData.reflectance,
          material: this.material, theta_deg: this.thetaDeg,
        });
        if (res.data.success) {
          this.hasResult = true;
          this.$emit("calculated", res.data.result);
          this.$message.success("厚度反演完成");
        } else {
          this.$message.error(res.data.error || "计算失败");
        }
      } catch (e) {
        this.$message.error("计算请求失败: " + e.message);
      } finally {
        this.calculating = false;
      }
    },
  },
};
</script>

<style scoped>
.calculation-panel { display: flex; flex-direction: column; gap: 20px; }

.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-label { font-size: 13px; font-weight: 500; color: #4E5969; }

/* 材料卡片 */
.material-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.material-card {
  display: flex; align-items: center; gap: 10px;
  padding: 12px; border: 1px solid #E5E6EB; border-radius: 8px;
  cursor: pointer; transition: all 0.2s; position: relative;
}
.material-card:hover { border-color: #B8D4FF; background: #F7FAFF; }
.material-card.active {
  border-color: var(--color-primary, #165DFF);
  background: #E8F3FF;
  box-shadow: 0 0 0 2px rgba(22,93,255,0.1);
}
.mc-icon {
  width: 38px; height: 38px; border-radius: 8px;
  background: #F0F5FF; color: var(--color-primary, #165DFF);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; flex-shrink: 0;
}
.material-card.active .mc-icon { background: var(--color-primary, #165DFF); color: #fff; }
.mc-info { flex: 1; }
.mc-name { font-size: 14px; font-weight: 500; color: #1D2129; }
.mc-desc { font-size: 11px; color: #86909C; margin-top: 1px; }
.mc-check { color: var(--color-primary, #165DFF); flex-shrink: 0; }

/* 入射角 */
.angle-input-wrap { display: flex; align-items: center; gap: 8px; }
.angle-input { flex: 1; }
.angle-unit { font-size: 16px; font-weight: 500; color: #4E5969; }

.action-btn {
  width: 100%; border-radius: 8px; font-weight: 500;
  height: 40px; letter-spacing: 0.5px;
}
.export-row { display: flex; gap: 8px; }
.export-btn, .save-btn {
  flex: 1; border-radius: 8px; font-weight: 500;
}
.export-btn {
  border: 1px dashed #B8D4FF; color: var(--color-primary, #165DFF);
}
.export-btn:hover { border-color: var(--color-primary, #165DFF); background: #E8F3FF; }
</style>
