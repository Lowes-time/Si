<template>
  <div class="results-log">
    <!-- 空状态 -->
    <div v-if="!result" class="empty-state">
      <el-icon :size="40"><Timer /></el-icon>
      <p class="empty-text">等待厚度反演计算完成</p>
      <p class="empty-hint">在"膜厚反演"面板中点击计算按钮</p>
    </div>

    <!-- 结果卡片 -->
    <template v-else>
      <div class="result-cards">
        <div class="result-card primary">
          <div class="rc-label">拟合厚度</div>
          <div class="rc-value">{{ result.thickness_um }} <span class="rc-unit">μm</span></div>
        </div>
        <div class="result-card">
          <div class="rc-label">R² 拟合优度</div>
          <div class="rc-value" :class="{ good: result.r_squared > 0.8, warn: result.r_squared <= 0.8 }">
            {{ result.r_squared }}
          </div>
        </div>
        <div class="result-card">
          <div class="rc-label">初估厚度</div>
          <div class="rc-value sub">{{ result.init_thickness_um }} <span class="rc-unit">μm</span></div>
        </div>
        <div class="result-card">
          <div class="rc-label">干涉判定</div>
          <div class="rc-value beam">
            <span class="beam-dot" :class="beamLevel"></span>
            {{ result.multi_beam_level }}
          </div>
        </div>
      </div>

      <!-- 操作日志 -->
      <div class="log-section">
        <div class="log-header">
          <el-icon :size="14"><List /></el-icon>
          <span>操作日志</span>
        </div>
        <div class="log-lines">
          <div
            v-for="(line, i) in log"
            :key="i"
            class="log-line"
          >
            <span class="log-dot"></span>
            {{ line }}
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { Timer, List } from "@element-plus/icons-vue";

export default {
  name: "ResultsLog",
  components: { Timer, List },
  props: {
    log: { type: Array, default: () => [] },
    result: { type: Object, default: null },
  },
  computed: {
    beamLevel() {
      if (!this.result) return "";
      if (this.result.multi_beam_level?.includes("强")) return "danger";
      if (this.result.multi_beam_level?.includes("中等")) return "warning";
      return "info";
    },
  },
};
</script>

<style scoped>
.results-log { display: flex; flex-direction: column; gap: 16px; }

/* 空状态 */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  padding: 32px 16px; color: #86909C;
}
.empty-state .el-icon { margin-bottom: 12px; color: #C9CDD4; }
.empty-text { font-size: 14px; font-weight: 500; color: #4E5969; }
.empty-hint { font-size: 12px; color: #86909C; margin-top: 4px; }

/* 结果卡片 */
.result-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.result-card {
  padding: 14px 12px; border-radius: 8px; background: #F7F8FA;
  transition: background 0.2s;
}
.result-card:hover { background: #EEF0F4; }
.result-card.primary {
  grid-column: 1 / -1;
  background: linear-gradient(135deg, #E8F3FF, #F0F5FF);
  border: 1px solid #B8D4FF;
}
.rc-label { font-size: 12px; color: #86909C; margin-bottom: 4px; }
.rc-value { font-size: 15px; font-weight: 600; color: #1D2129; }
.result-card.primary .rc-value { font-size: 22px; color: var(--color-primary, #165DFF); }
.rc-value.sub { font-size: 14px; }
.rc-value.good { color: #00B42A; }
.rc-value.warn { color: #F53F3F; }
.rc-unit { font-size: 12px; font-weight: 400; color: #86909C; }

.rc-value.beam { display: flex; align-items: center; gap: 6px; font-size: 13px; }
.beam-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.beam-dot.danger { background: #F53F3F; }
.beam-dot.warning { background: #FF7D00; }
.beam-dot.info { background: #165DFF; }

/* 操作日志 */
.log-section {
  background: #F7F8FA; border-radius: 8px; padding: 12px;
}
.log-header {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; font-weight: 500; color: #4E5969;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #E5E6EB;
}
.log-lines { max-height: 160px; overflow-y: auto; }
.log-line {
  font-size: 12px; color: #86909C; padding: 3px 0;
  display: flex; align-items: baseline; gap: 6px;
  line-height: 1.5;
}
.log-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: #C9CDD4; flex-shrink: 0; margin-top: 4px;
}
</style>
