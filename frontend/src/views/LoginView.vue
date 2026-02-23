<template>
  <div class="login-page">
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <h2>Cisco 交換器管理介面</h2>
          <p class="subtitle">WS-C2960X-48TS-L</p>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="交換器 IP / 主機名稱" prop="host">
          <el-input
            v-model="form.host"
            placeholder="192.168.1.1"
            :prefix-icon="Connection"
            clearable
          />
        </el-form-item>

        <el-form-item label="帳號" prop="username">
          <el-input
            v-model="form.username"
            placeholder="admin"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item label="密碼" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="請輸入密碼"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item label="Enable 密碼（選填）">
          <el-input
            v-model="form.secret"
            type="password"
            placeholder="若有設定 Enable 密碼請填寫"
            :prefix-icon="Key"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="isLoading"
            class="login-btn"
          >
            {{ isLoading ? '連線中...' : '登入' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Connection, User, Lock, Key } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useSessionStore } from '@/stores/session'

const router = useRouter()
const sessionStore = useSessionStore()

const formRef = ref<FormInstance>()
const isLoading = ref(false)

const form = reactive({
  host: '',
  username: '',
  password: '',
  secret: '',
})

const rules: FormRules = {
  host: [{ required: true, message: '請輸入交換器 IP 或主機名稱', trigger: 'blur' }],
  username: [{ required: true, message: '請輸入帳號', trigger: 'blur' }],
  password: [{ required: true, message: '請輸入密碼', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  isLoading.value = true
  try {
    const result = await sessionStore.login(form)
    if (result.success) {
      ElMessage.success('連線成功')
      router.push({ name: 'dashboard' })
    } else {
      ElMessage.error(result.message)
    }
  } catch {
    ElMessage.error('連線失敗，請確認網路連通性')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}

.login-card {
  width: 420px;
}

.login-header {
  text-align: center;
}

.login-header h2 {
  margin: 0 0 4px;
  font-size: 20px;
  color: #303133;
}

.subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.login-btn {
  width: 100%;
}
</style>
