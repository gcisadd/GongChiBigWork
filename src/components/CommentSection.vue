<template>
  <div class="comment-section">
    <div class="comment-header">
      <h3>
        <el-icon><ChatDotRound /></el-icon>
        评论
        <el-badge :value="totalCount" :hidden="totalCount === 0" type="primary" />
      </h3>
    </div>

    <!-- 顶部：仅用于发表新评论 -->
    <div class="comment-input-section">
      <el-input
        v-model="newComment"
        type="textarea"
        placeholder="写下你的评论..."
        :rows="2"
        :disabled="loading"
      />
      <div class="comment-actions">
        <el-button
          type="primary"
          size="small"
          :loading="submitting"
          :disabled="!newComment.trim()"
          @click="submitComment"
        >
          发表评论
        </el-button>
      </div>
    </div>

    <!-- 评论列表 -->
    <div class="comment-list" v-loading="loading">
      <el-empty v-if="comments.length === 0 && !loading" description="暂无评论" />

      <div v-else class="comment-tree">
        <CommentItem
          v-for="comment in comments"
          :key="comment.id"
          :comment="comment"
          :current-user-id="currentUserId"
          :current-username="currentUsername"
          :document-owner-id="ownerId"
          @delete="handleDelete"
          @submit-reply="handleSubmitReply"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, ref, watch } from 'vue'
import { documentApi, profileApi, commentApi } from '../services/api'
import CommentItem from './CommentItem.vue'

/**
 * 评论组件
 *
 * 文档评论功能，支持评论、回复、删除（仅作者可见删除按钮），无编辑功能
 */

interface CommentData {
  id: number
  document_id: number
  user_id: number
  username: string
  content: string
  parent_id: number | null
  created_at: string
  updated_at: string
  replies: CommentData[]
}

// Props
interface Props {
  documentId: number
  documentOwnerId?: number
}

const props = withDefaults(defineProps<Props>(), {
  documentOwnerId: 0
})

// 当前用户信息
const currentUsername = ref(localStorage.getItem('username') || '')
const currentUserId = ref<number>(0)
const ownerId = ref<number>(props.documentOwnerId)

// 获取当前用户ID
const getCurrentUserId = async () => {
  try {
    const response = await profileApi.getProfile()
    currentUserId.value = response.id
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 获取文档所有者ID
const getDocumentOwnerId = async () => {
  if (!props.documentId) return

  try {
    const response = await documentApi.getDocument(props.documentId)
    ownerId.value = response.creator_id
  } catch (error) {
    console.error('获取文档信息失败:', error)
  }
}

// 评论数据
const comments = ref<CommentData[]>([])
const loading = ref(false)
const submitting = ref(false)
const newComment = ref('')
const totalCount = ref(0)


// 计算总评论数
const countComments = (commentList: CommentData[]): number => {
  let count = commentList.length
  for (const comment of commentList) {
    if (comment.replies && comment.replies.length > 0) {
      count += countComments(comment.replies)
    }
  }
  return count
}

watch(
  comments,
  () => {
    totalCount.value = countComments(comments.value)
  },
  { deep: true }
)

// 加载评论
const loadComments = async () => {
  if (!props.documentId) return

  loading.value = true
  try {
    const response = await commentApi.getComments(props.documentId)
    // commentApi.getComments 返回的已是 { total, items }，无需再取 .data
    comments.value = response.items || []
  } catch (error) {
    console.error('加载评论失败:', error)
    ElMessage.error('加载评论失败')
  } finally {
    loading.value = false
  }
}

// 提交评论（仅用于顶部发表新评论）
const submitComment = async () => {
  if (!newComment.value.trim() || !props.documentId) return

  submitting.value = true
  try {
    await commentApi.createComment(props.documentId, {
      content: newComment.value.trim()
    })
    ElMessage.success('评论成功')
    newComment.value = ''
    await loadComments()
  } catch (error: any) {
    console.error('提交评论失败:', error)
    ElMessage.error(error.response?.data?.detail || '提交评论失败')
  } finally {
    submitting.value = false
  }
}

// 处理在某条评论下的内联回复
const handleSubmitReply = async (payload: { parentId: number; content: string }) => {
  if (!props.documentId) return
  try {
    await commentApi.replyComment(props.documentId, {
      content: payload.content,
      parent_id: payload.parentId
    })
    ElMessage.success('回复成功')
    await loadComments()
  } catch (error: any) {
    console.error('回复失败:', error)
    ElMessage.error(error.response?.data?.detail || '回复失败')
  }
}

// 处理删除
const handleDelete = async (comment: CommentData) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条评论吗？删除后无法恢复。',
      '删除评论',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await commentApi.deleteComment(props.documentId, comment.id)
    ElMessage.success('删除成功')
    await loadComments()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除评论失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除评论失败')
    }
  }
}

// 监听文档ID变化
watch(
  () => props.documentId,
  (newId) => {
    if (newId) {
      loadComments()
    }
  },
  { immediate: true }
)

onMounted(() => {
  getCurrentUserId()
  if (props.documentId) {
    getDocumentOwnerId()
  }
})
</script>

<style scoped>
.comment-section {
  margin-top: 20px;
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.comment-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.comment-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.comment-input-section {
  margin-bottom: 20px;
}

.comment-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.comment-list {
  min-height: 100px;
}

.comment-tree {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
