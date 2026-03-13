<template>
  <el-menu :default-active="activeMenu" class="aside-menu" router @select="handleMenuSelect">
    <el-menu-item index="/table">
      <el-icon><Document /></el-icon>
      <span>文档列表</span>
    </el-menu-item>
    <el-menu-item index="/friends">
      <el-icon><User /></el-icon>
      <span>好友管理</span>
    </el-menu-item>
    <!-- 协作编辑页面显示"协作编辑"，其他页面显示"新建文档" -->
    <el-menu-item v-if="isCollabRoute" index="/collab-editor">
      <el-icon><Connection /></el-icon>
      <span>协作编辑</span>
    </el-menu-item>
    <el-menu-item v-else index="/editor">
      <el-icon><Edit /></el-icon>
      <span>新建文档</span>
    </el-menu-item>
    <el-menu-item index="/profile">
      <el-icon><UserFilled /></el-icon>
      <span>关于</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const activeMenu = computed(() => route.path);

// 判断当前是否在协作编辑路由
const isCollabRoute = computed(() => route.path === "/collab-editor");

const handleMenuSelect = (index: string) => {
  router.push(index);
};
</script>

<style scoped>
.aside-menu {
  height: 100%;
  border-right: none;
}
</style>
