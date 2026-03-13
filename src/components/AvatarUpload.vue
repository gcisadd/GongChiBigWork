<template>
  <div class="avatar-upload">
    <div class="avatar-wrapper" @click="triggerUpload">
      <el-avatar
        :size="size"
        :src="avatarSrc"
        class="avatar-img"
      >
        {{ defaultText }}
      </el-avatar>
      <div class="avatar-overlay" v-if="showOverlay">
        <el-icon><Camera /></el-icon>
        <span>更换头像</span>
      </div>
    </div>
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileChange"
    />
  </div>
</template>

<script setup lang="ts">
import { Camera } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, ref } from 'vue'
import { profileApi } from '../services/api'

/**
 * 头像上传组件
 */

interface Props {
  modelValue?: string  // v-model，支持双向绑定
  size?: number
  username?: string
  showOverlay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  size: 80,
  username: '',
  showOverlay: true
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'change': [value: string]
}>()

const fileInput = ref<HTMLInputElement>()

// 计算显示的头像源
const avatarSrc = computed(() => {
  if (props.modelValue) {
    // 如果是完整的 data URL，直接返回
    if (props.modelValue.startsWith('data:')) {
      return props.modelValue
    }
    // 否则添加 data URL 前缀
    return `data:image/jpeg;base64,${props.modelValue}`
  }
  return ''
})

// 默认显示用户名首字母
const defaultText = computed(() => {
  if (props.username) {
    return props.username.charAt(0).toUpperCase()
  }
  return ''
})

// 触发文件选择
const triggerUpload = () => {
  fileInput.value?.click()
}

// 处理文件选择
const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  // 验证文件大小（最大 2MB）
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 2MB')
    return
  }

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }

  try {
    // 转换为 Base64
    const base64 = await fileToBase64(file)

    // 上传到服务器
    await profileApi.uploadAvatar(base64)

    // 触发更新
    emit('update:modelValue', base64)
    emit('change', base64)

    ElMessage.success('头像更新成功')
  } catch (error: any) {
    console.error('头像上传失败:', error)
    ElMessage.error(error.response?.data?.detail || '头像上传失败')
  }

  // 清空 input，允许重复选择同一文件
  target.value = ''
}

// 文件转 Base64
const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      // 去掉 data:image/xxx;base64, 前缀，只保留 Base64 数据
      const result = reader.result as string
      const base64 = result.split(',')[1]
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}
</script>

<style scoped>
.avatar-upload {
  display: inline-block;
}

.avatar-wrapper {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-overlay .el-icon {
  font-size: 20px;
  margin-bottom: 4px;
}

.avatar-img {
  display: block;
}
</style>
