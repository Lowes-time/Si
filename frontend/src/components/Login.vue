<template>
  <div class="login-page">
    <div class="login-box">
      <h1 class="login-title">半导体薄膜厚度光学测量分析系统</h1>
      <p class="login-version">V1.0</p>
      <el-form
        v-if="mode === 'login'"
        class="login-form"
        @submit.prevent="handleLogin"
      >
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
        <p v-if="successMsg" class="login-success">{{ successMsg }}</p>
        <el-button
          type="primary"
          size="large"
          class="login-btn"
          :loading="submitting"
          @click="handleLogin"
        >
          登录
        </el-button>
        <p class="login-switch">
          还没有账户？
          <a href="javascript:void(0)" @click="switchToRegister">注册账户</a>
        </p>
      </el-form>
      <el-form
        v-else
        class="login-form"
        @submit.prevent="handleRegister"
      >
        <el-form-item>
          <el-input
            v-model="regUsername"
            placeholder="用户名，3～20 个字符"
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="regPassword"
            type="password"
            placeholder="密码，6～32 个字符"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="regConfirm"
            type="password"
            placeholder="确认密码"
            size="large"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        <p v-if="errorMsg" class="login-error">{{ errorMsg }}</p>
        <el-button
          type="primary"
          size="large"
          class="login-btn"
          :loading="submitting"
          @click="handleRegister"
        >
          注册
        </el-button>
        <p class="login-switch">
          已有账户？
          <a href="javascript:void(0)" @click="switchToLogin">返回登录</a>
        </p>
      </el-form>
    </div>
  </div>
</template>

<script>
import {
  validateLogin,
  setLoggedIn,
  registerUser,
  isUsernameTaken,
  USERNAME_MIN,
  USERNAME_MAX,
  PASSWORD_MIN,
  PASSWORD_MAX,
} from "../utils/auth.js";

export default {
  name: "Login",
  emits: ["login-success"],
  data() {
    return {
      mode: "login",
      username: "",
      password: "",
      regUsername: "",
      regPassword: "",
      regConfirm: "",
      errorMsg: "",
      successMsg: "",
      submitting: false,
    };
  },
  methods: {
    switchToRegister() {
      this.mode = "register";
      this.errorMsg = "";
      this.successMsg = "";
    },
    switchToLogin() {
      this.mode = "login";
      this.errorMsg = "";
      this.regPassword = "";
      this.regConfirm = "";
    },
    handleLogin() {
      this.errorMsg = "";
      this.successMsg = "";
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
    handleRegister() {
      this.errorMsg = "";
      const name = this.regUsername.trim();
      const pwd = this.regPassword;
      const confirm = this.regConfirm;
      if (!name) {
        this.errorMsg = "请输入用户名";
        return;
      }
      if (name.length < USERNAME_MIN || name.length > USERNAME_MAX) {
        this.errorMsg = `用户名长度应为 ${USERNAME_MIN}～${USERNAME_MAX} 个字符`;
        return;
      }
      if (!pwd) {
        this.errorMsg = "请输入密码";
        return;
      }
      if (pwd.length < PASSWORD_MIN || pwd.length > PASSWORD_MAX) {
        this.errorMsg = `密码长度应为 ${PASSWORD_MIN}～${PASSWORD_MAX} 个字符`;
        return;
      }
      if (!confirm) {
        this.errorMsg = "请确认密码";
        return;
      }
      if (pwd !== confirm) {
        this.errorMsg = "两次输入的密码不一致";
        return;
      }
      if (isUsernameTaken(name)) {
        this.errorMsg = "该用户名已被占用";
        return;
      }
      this.submitting = true;
      registerUser(name, pwd);
      setLoggedIn();
      this.$emit("login-success", name);
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

.login-success {
  color: #00b42a;
  font-size: 13px;
  margin: -6px 0 12px;
}

.login-btn {
  width: 100%;
  margin-top: 4px;
}

.login-switch {
  margin-top: 16px;
  text-align: center;
  font-size: 13px;
  color: #86909c;
}

.login-switch a {
  color: #165dff;
  text-decoration: none;
}

.login-switch a:hover {
  text-decoration: underline;
}
</style>
