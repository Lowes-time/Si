<!--
  膜厚反演：材料、入射角、计算与快捷导出
-->
<template>
  <div class="calculation-panel">
    <!-- 数据范围信息 -->
    <div v-if="effectiveData" class="data-range-info">
      <el-icon><InfoFilled /></el-icon>
      <span>拟合范围: {{ getRangeStart() }} - {{ getRangeEnd() }} μm</span>
      <span class="point-count">({{ effectiveData.wavelength?.length || 0 }} 个点)</span>
    </div>

    <!-- 材料选择 -->
    <div class="form-group">
      <label class="form-label">基底材料</label>
      <div class="material-grid">
        <div
          v-for="mat in materialOptions"
          :key="mat.key"
          :class="['material-card', { active: material === mat.key }]"
          @click="material = mat.key"
        >
          <div class="mc-icon">{{ mat.formula }}</div>
          <div class="mc-info">
            <div class="mc-name">{{ mat.name_cn }}</div>
            <div class="mc-desc">{{ mat.desc }}</div>
          </div>
          <el-icon v-if="material === mat.key" class="mc-check" :size="16"><CircleCheckFilled /></el-icon>
        </div>
      </div>
    </div>

    <!-- 入射角 -->
    <div class="form-group">
      <label class="form-label">入射角 (°)</label>
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
      </div>
    </div>

    <!-- 操作按钮 -->
    <el-button
      type="primary"
      :disabled="!effectiveData"
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
          @click="handleSave"
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
import { CircleCheckFilled, Cpu, Download, FolderAdd, InfoFilled } from "@element-plus/icons-vue";
import { calculate, fetchMaterials } from "../api/index.js";
import { ElMessage } from "element-plus";

export default {
  name: "CalculationPanel",
  components: { CircleCheckFilled, Cpu, Download, FolderAdd, InfoFilled },
  props: { 
    rawData: { type: Object, default: null },
    processedData: { type: Object, default: null }
  },
  emits: ["calculated", "export", "save"],
  data() {
    return {
      material: "SIC",
      thetaDeg: 10.0,
      calculating: false,
      hasResult: false,
      lastResult: null,
      materialOptions: [],
    };
  },
  mounted() {
    this.loadMaterials();
  },
  watch: {
    rawData(val) {
      if (val?.suggested_material) {
        this.material = val.suggested_material;
      }
    },
  },
  computed: {
    // 优先使用经过预处理/范围选择后的数据
    effectiveData() {
      if (this.processedData && this.processedData.wavelength) {
        return this.processedData;
      }
      if (this.rawData && this.rawData.wavelength) {
        return this.rawData;
      }
      return null;
    }
  },
  methods: {
    async loadMaterials() {
      try {
        const res = await fetchMaterials();
        const list = res.data?.data || [];
        this.materialOptions = list.map((m) => ({
          key: m.key,
          formula: m.formula || m.key,
          name_cn: (m.name || "").split("(")[0].trim() || m.key,
          desc: m.desc || "",
        }));
      } catch (e) {
        this.materialOptions = [
          { key: "SIC", formula: "SiC", name_cn: "碳化硅", desc: "功率器件" },
          { key: "SI", formula: "Si", name_cn: "硅", desc: "IC衬底" },
        ];
      }
    },
    async doCalculate() {
      if (!this.effectiveData) {
        ElMessage.warning("请先导入数据并执行预处理");
        return;
      }
      
      this.calculating = true;
      this.hasResult = false;
      try {
        // 优先使用预处理后的平滑数据(ref_smooth)，否则使用原始数据
        const wlData = this.effectiveData.wavelength;
        const refData = this.effectiveData.ref_smooth || this.effectiveData.reflectance;
        
        const res = await calculate({
          wavelength: wlData,
          reflectance: refData,
          material: this.material, 
          theta_deg: this.thetaDeg,
        });
        if (res.data.success) {
          this.hasResult = true;
          this.lastResult = res.data.result;
          this.lastResult.theta_deg = this.thetaDeg;
          this.lastResult.material_type = this.material;
          // 传递拟合数据范围信息
          this.lastResult.fit_range = {
            start: this.effectiveData.wl_range_start || this.effectiveData.wl_min || 0,
            end: this.effectiveData.wl_range_end || this.effectiveData.wl_max || 0,
            count: this.effectiveData.wavelength.length
          };
          this.$emit("calculated", this.lastResult);
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
    async handleSave() {
      if (!this.lastResult) {
        ElMessage.warning("请先执行计算");
        return;
      }
      this.$emit("save", this.material, this.thetaDeg);
    },
    // 获取起始波长（确保 start <= end）
    getRangeStart() {
      if (!this.effectiveData) return '全部';
      const start = this.effectiveData.wl_range_start ?? this.effectiveData.wl_min;
      const end = this.effectiveData.wl_range_end ?? this.effectiveData.wl_max;
      if (start == null) return '全部';
      // 确保起始值 <= 结束值
      return Math.min(start, end).toFixed(2);
    },
    // 获取结束波长（确保 start <= end）
    getRangeEnd() {
      if (!this.effectiveData) return '全部';
      const start = this.effectiveData.wl_range_start ?? this.effectiveData.wl_min;
      const end = this.effectiveData.wl_range_end ?? this.effectiveData.wl_max;
      if (end == null) return '全部';
      // 确保结束值 >= 起始值
      return Math.max(start, end).toFixed(2);
    }
  },
};
</script>

<style scoped>
.calculation-panel { display: flex; flex-direction: column; gap: 20px; }

.data-range-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #E8F3FF;
  border: 1px solid #B8D4FF;
  border-radius: 8px;
  font-size: 12px;
  color: #165DFF;
}
.data-range-info .el-icon { flex-shrink: 0; }
.point-count { color: #86909C; margin-left: 4px; }

.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-label { font-size: 13px; font-weight: 500; color: #4E5969; }

.material-grid { 
  display: grid; 
  grid-template-columns: repeat(3, 1fr); 
  gap: 8px;
  max-height: 220px;
  overflow-y: auto;
  padding-right: 4px;
}

.material-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 10px 6px;
  border: 1px solid #E5E6EB;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  text-align: center;
}
.material-card:hover { border-color: #B8D4FF; background: #F7FAFF; }
.material-card.active {
  border-color: var(--color-primary, #165DFF);
  background: #E8F3FF;
  box-shadow: 0 0 0 2px rgba(22,93,255,0.1);
}
.mc-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #F0F5FF;
  color: var(--color-primary, #165DFF);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}
.material-card.active .mc-icon { 
  background: var(--color-primary, #165DFF); 
  color: #fff; 
}
.mc-info { width: 100%; }
.mc-name { font-size: 12px; font-weight: 600; color: #1D2129; }
.mc-desc { font-size: 10px; color: #86909C;margin-top: 2px; }
.mc-check { 
  position: absolute; 
  top: 4px; 
  right: 4px; 
  color: var(--color-primary, #165DFF); 
}

.angle-input-wrap { display: flex; align-items: center; gap: 8px; }
.angle-input { flex: 1; }

.action-btn {
  width: 100%; 
  border-radius: 8px; 
  font-weight: 500;
  height: 40px; 
  letter-spacing: 0.5px;
}
.export-row { display: flex; gap: 8px; }
.export-btn, .save-btn { flex: 1; border-radius: 8px; font-weight: 500; }
.export-btn {
  border: 1px dashed #B8D4FF; 
  color: var(--color-primary, #165DFF);
}
.export-btn:hover { 
  border-color: var(--color-primary, #165DFF); 
  background: #E8F3FF; 
}
</style>