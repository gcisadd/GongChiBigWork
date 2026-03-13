<template>
  <div class="friend-select">
    <div class="selected-friends">
      <span class="label">已选好友：</span>
      <el-tag
        v-for="friend in selectedFriends"
        :key="friend.friend_id"
        closable
        @close="handleRemoveFriend(friend)"
        class="friend-tag"
      >
        {{ friend.friend_username }}
      </el-tag>
      <span v-if="selectedFriends.length === 0" class="no-friends">未选择好友</span>
    </div>
    <el-button type="primary" @click="showDialog = true" class="select-btn"> 选择好友 </el-button>

    <el-dialog v-model="showDialog" title="选择好友" width="500px">
      <div class="dialog-content">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索好友"
          clearable
          @input="handleSearch"
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-checkbox-group v-model="checkedFriends" class="friend-list">
          <el-checkbox
            v-for="friend in filteredFriends"
            :key="friend.friend_id"
            :value="friend.friend_id"
            class="friend-checkbox"
          >
            <div class="friend-info">
              <span class="friend-name">{{ friend.friend_username }}</span>
              <span class="friend-email">{{ friend.friend_email }}</span>
            </div>
          </el-checkbox>
        </el-checkbox-group>

        <el-empty v-if="friends.length === 0" description="暂无好友" />
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-select v-model="defaultPermission" placeholder="默认权限" class="permission-select">
            <el-option label="仅查看" value="view" />
            <el-option label="可编辑" value="edit" />
          </el-select>
          <el-button @click="showDialog = false">取消</el-button>
          <el-button type="primary" @click="handleConfirm">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { Search } from "@element-plus/icons-vue";
import { computed, onMounted, ref } from "vue";
import { friendApi } from "../services/api";

interface Friend {
  id: number;
  friend_id: number;
  friend_username: string;
  friend_email: string;
  created_at: string;
}

interface SelectedFriend extends Friend {
  permission_level: string;
}

const props = defineProps<{
  modelValue: SelectedFriend[];
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: SelectedFriend[]): void;
}>();

const showDialog = ref(false);
const searchKeyword = ref("");
const friends = ref<Friend[]>([]);
const checkedFriends = ref<number[]>([]);
const defaultPermission = ref("view");

let searchTimer: ReturnType<typeof setTimeout> | null = null;

const filteredFriends = computed(() => {
  if (!searchKeyword.value.trim()) {
    return friends.value;
  }
  const keyword = searchKeyword.value.toLowerCase();
  return friends.value.filter(
    (f) =>
      f.friend_username.toLowerCase().includes(keyword) ||
      f.friend_email.toLowerCase().includes(keyword),
  );
});

const selectedFriends = computed(() => props.modelValue);

const loadFriends = async () => {
  try {
    const res = await friendApi.getFriends();
    friends.value = res.items || [];
  } catch (error) {
    console.error("获取好友列表失败:", error);
  }
};

const handleSearch = () => {
  if (searchTimer) {
    clearTimeout(searchTimer);
  }
  // 搜索功能可以扩展
};

const handleRemoveFriend = (friend: SelectedFriend) => {
  const newList = selectedFriends.value.filter((f) => f.friend_id !== friend.friend_id);
  emit("update:modelValue", newList);
};

const handleConfirm = () => {
  const selected: SelectedFriend[] = friends.value
    .filter((f) => checkedFriends.value.includes(f.friend_id))
    .map((f) => ({
      ...f,
      permission_level: defaultPermission.value,
    }));

  emit("update:modelValue", selected);
  showDialog.value = false;
  checkedFriends.value = [];
  searchKeyword.value = "";
};

onMounted(() => {
  loadFriends();
});
</script>

<style scoped>
.friend-select {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
}

.selected-friends {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.select-btn {
  flex-shrink: 0;
}

.label {
  font-size: 14px;
  color: #606266;
}

.friend-tag {
  margin-right: 5px;
}

.no-friends {
  font-size: 14px;
  color: #909399;
}

.dialog-content {
  max-height: 400px;
  overflow-y: auto;
}

.search-input {
  margin-bottom: 15px;
}

.friend-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.friend-checkbox {
  display: flex;
  width: 100%;
  margin-right: 0;
}

.friend-checkbox :deep(.el-checkbox__label) {
  flex: 1;
}

.friend-info {
  display: flex;
  flex-direction: column;
}

.friend-name {
  font-weight: 500;
  color: #303133;
}

.friend-email {
  font-size: 12px;
  color: #909399;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  align-items: center;
}

.permission-select {
  margin-right: auto;
}
</style>
