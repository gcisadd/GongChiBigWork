<template>
  <div class="comment-item" :class="{ 'is-reply': isReply }">
    <div class="comment-main">
      <el-avatar :size="isReply ? 28 : 36" :src="avatarSrc" class="comment-avatar">
        {{ comment.username.charAt(0).toUpperCase() }}
      </el-avatar>

      <div class="comment-content-wrapper">
        <div class="comment-meta">
          <span class="comment-username">{{ comment.username }}</span>
          <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
          <el-tag v-if="isOwner" type="danger" size="small" class="owner-tag">作者</el-tag>
        </div>

        <div class="comment-content">
          {{ comment.content }}
        </div>

        <!-- 操作按钮：仅文档作者显示删除 -->
        <div class="comment-actions">
          <el-button
            type="primary"
            size="small"
            text
            @click="toggleReplyInput"
          >
            回复
          </el-button>
          <el-button
            v-if="canDelete"
            type="danger"
            size="small"
            text
            @click="$emit('delete', comment)"
          >
            删除
          </el-button>
        </div>

        <!-- 本条评论下的内联回复输入框 -->
        <div v-if="showReplyInput" class="inline-reply">
          <el-input
            v-model="inlineReplyContent"
            type="textarea"
            :rows="2"
            placeholder="写下回复..."
            class="inline-reply-input"
          />
          <div class="inline-reply-actions">
            <el-button size="small" text @click="cancelInlineReply">取消</el-button>
            <el-button
              type="primary"
              size="small"
              :loading="inlineSubmitting"
              :disabled="!inlineReplyContent.trim()"
              @click="submitInlineReply"
            >
              回复
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 嵌套回复 -->
    <div v-if="comment.replies && comment.replies.length > 0" class="comment-replies">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :current-user-id="currentUserId"
        :current-username="currentUsername"
        :document-owner-id="documentOwnerId"
        :is-reply="true"
        @delete="$emit('delete', $event)"
        @submit-reply="$emit('submit-reply', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

/**
 * 评论项组件
 *
 * 显示单个评论，支持嵌套回复
 */

interface CommentData {
  id: number
  document_id: number
  user_id: number
  username: string
  avatar?: string
  content: string
  parent_id: number | null
  created_at: string
  updated_at: string
  replies: CommentData[]
}

interface Props {
  comment: CommentData
  currentUserId: number
  currentUsername: string
  documentOwnerId?: number
  isReply?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  documentOwnerId: 0,
  isReply: false
})

const emit = defineEmits<{
  delete: [comment: CommentData]
  'submit-reply': [{ parentId: number; content: string }]
}>()

// 内联回复
const showReplyInput = ref(false)
const inlineReplyContent = ref('')
const inlineSubmitting = ref(false)

// 当前登录用户是否为文档作者
const isCurrentUserDocumentOwner = computed(() => {
  return props.currentUserId === props.documentOwnerId && props.documentOwnerId !== 0
})

// 当前登录用户是否为该评论的发布者
const isCommentAuthor = computed(() => {
  return props.comment.user_id === props.currentUserId
})

// 是否显示删除按钮（文档作者 或 评论发布者）
const canDelete = computed(() => {
  return isCurrentUserDocumentOwner.value || isCommentAuthor.value
})

// 该条评论的发布者是否为文档作者
const isOwner = computed(() => {
  return props.comment.user_id === props.documentOwnerId
})

// 格式化头像URL
const avatarSrc = computed(() => {
  if (props.comment.avatar) {
    if (props.comment.avatar.startsWith('data:')) {
      return props.comment.avatar
    }
    return `data:image/jpeg;base64,${props.comment.avatar}`
  }
  return ''
})

// 格式化时间
const formatTime = (time: string): string => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return date.toLocaleDateString('zh-CN')
}

const toggleReplyInput = () => {
  showReplyInput.value = !showReplyInput.value
  if (!showReplyInput.value) inlineReplyContent.value = ''
}

const cancelInlineReply = () => {
  showReplyInput.value = false
  inlineReplyContent.value = ''
}

const submitInlineReply = async () => {
  if (!inlineReplyContent.value.trim()) return
  inlineSubmitting.value = true
  emit('submit-reply', { parentId: props.comment.id, content: inlineReplyContent.value.trim() })
  inlineReplyContent.value = ''
  showReplyInput.value = false
  inlineSubmitting.value = false
}
</script>

<style scoped>
.comment-item {
  padding: 12px;
  background-color: #fafafa;
  border-radius: 8px;
}

.comment-item.is-reply {
  margin-left: 20px;
  background-color: #f5f7fa;
}

.comment-main {
  display: flex;
  gap: 12px;
}

.comment-avatar {
  flex-shrink: 0;
  background-color: #409eff;
  color: #fff;
  font-weight: 600;
}

.comment-content-wrapper {
  flex: 1;
  min-width: 0;
}

.comment-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.comment-username {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.comment-time {
  color: #909399;
  font-size: 12px;
}

.owner-tag {
  margin-left: 4px;
}

.comment-content {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 8px 0;
  word-break: break-word;
}

.comment-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.inline-reply {
  margin-top: 12px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 6px;
}

.inline-reply-input {
  margin-bottom: 8px;
}

.inline-reply-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.comment-replies {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
