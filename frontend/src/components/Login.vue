<template>
  <div class="login-page">
    <div class="login-box">
      <h1 class="login-title">半导体薄膜厚度光学测量分析系统</h1>
      <p class="login-version">V1.0</p>
      <el-form class="login-form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input
            v-model="username"
            placeholder="用户名，默认 user"
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="password"
            type="password"
            placeholder="密码，默认 123456"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <p v-if="errorMsg" class="login-error">{{ errorMsg }}</p>
        <el-button
          type="primary"
          size="large"
          class="login-btn"
          :loading="submitting"
          @click="handleLogin"
        >
          登录
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script>
import { validateLogin, setLoggedIn } from "../utils/auth.js";

export default {
  name: "Login",
  emits: ["login-success"],
  data() {
    return {
      username: "",
      password: "",
      errorMsg: "",
      submitting: false,
    };
  },
  methods: {
    handleLogin() {
      this.errorMsg = "";
      const name = this.username.trim();
      const pwd = this.password;
      if (!name) {
        this.errorMsg = "请输入用户名";
        return;
      }
      if (!pwd) {
        this.errorMsg = "请输入密码";
        return;
      }
      this.submitting = true;
      if (validateLogin(name, pwd)) {
        setLoggedIn();
        this.$emit("login-success", name);
      } else {
        this.errorMsg = "用户名或密码错误";
      }
      this.submitting = false;
    },
  },
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #4a6fa5;
}

.login-box {
  width: 380px;
  padding: 40px 36px 36px;
  background: #fff;
  border-radius: 8px;
}

.login-title {
  font-size: 20px;
  font-weight: 600;
  text-align: center;
  color: #1d2129;
  line-height: 1.4;
  margin-bottom: 8px;
}

.login-version {
  text-align: center;
  font-size: 13px;
  color: #86909c;
  margin-bottom: 28px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.login-error {
  color: #f53f3f;
  font-size: 13px;
  margin: -6px 0 12px;
}

.login-btn {
  width: 100%;
  margin-top: 4px;
}
</style>
