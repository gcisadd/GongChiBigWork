# GongChiBigWork

这是一个基于 Vue 3 + TypeScript + Vite 构建的现代化前端项目，集成了 Element Plus 组件库，提供了美观的用户界面和良好的开发体验。

## 项目简介

本项目是一个 Vue 3 单页应用（SPA），使用最新的前端技术栈开发，包含以下主要功能：

- **登录页面**：提供用户登录功能，包含表单验证、记住我等功能，登录成功后跳转到表格页面
- **表格页面**：提供数据表格展示和管理功能，包含数据列表、分页、新增、编辑、删除等操作
- **路由管理**：使用 Vue Router 进行页面路由管理
- **状态管理**：使用 Pinia 进行全局状态管理
- **UI 组件库**：集成 Element Plus，提供丰富的 UI 组件

## 技术栈

- **框架**：Vue 3 (Composition API)
- **语言**：TypeScript
- **构建工具**：Vite
- **路由**：Vue Router 4
- **状态管理**：Pinia
- **UI 组件库**：Element Plus
- **图标库**：@element-plus/icons-vue

## 项目结构

```
GongChiBigWork/
├── src/
│   ├── assets/          # 静态资源文件
│   ├── components/      # 公共组件
│   ├── router/          # 路由配置
│   ├── stores/          # Pinia 状态管理
│   ├── views/           # 页面组件
│   │   ├── AboutView.vue     # 登录页面
│   │   └── TableView.vue      # 表格页面
│   ├── App.vue          # 根组件
│   └── main.ts          # 应用入口文件
├── public/              # 公共静态资源
└── package.json         # 项目依赖配置
```

## 功能说明

### 登录页面 (`/about`)

登录页面位于 `src/views/AboutView.vue`，提供完整的用户登录功能。

#### 功能特性

1. **表单验证**
   - 用户名验证：必填，长度 3-20 个字符
   - 密码验证：必填，长度 6-20 个字符
   - 实时验证反馈

2. **用户体验**
   - 支持记住我功能
   - 密码显示/隐藏切换
   - 输入框清除功能
   - 支持回车键快速登录
   - 登录按钮加载状态提示

3. **界面设计**
   - 响应式设计，支持移动端和桌面端
   - 渐变背景，现代化 UI 设计
   - 卡片式布局，清晰的视觉层次

#### 使用方法

1. 访问登录页面：在浏览器中访问 `/about` 路由
2. 输入用户名：在用户名输入框中输入 3-20 个字符
3. 输入密码：在密码输入框中输入 6-20 个字符
4. 选择记住我（可选）：勾选"记住我"复选框以保存登录状态
5. 点击登录：点击"登录"按钮或按回车键提交登录

#### 参数说明

**登录表单数据 (loginForm)**
- `username` (string): 用户名，必填，长度 3-20 个字符
- `password` (string): 密码，必填，长度 6-20 个字符
- `remember` (boolean): 是否记住登录状态，可选

#### 返回值说明

- **登录成功**：显示成功消息提示，如果选择记住我，会将用户名保存到 localStorage
- **登录失败**：显示错误消息提示
- **表单验证失败**：显示警告消息，提示用户填写完整信息

#### 注意事项

- 当前登录功能为模拟实现，实际项目中需要替换为真实的 API 调用
- 登录成功后可以根据业务需求跳转到指定页面
- 记住我功能会将用户名保存到 localStorage，实际项目中应保存加密的 token

## 开发环境设置

### 推荐 IDE 设置

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (需要禁用 Vetur)

### 推荐浏览器设置

- Chromium 内核浏览器 (Chrome, Edge, Brave 等):
  - [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
  - [在 Chrome DevTools 中启用自定义对象格式化器](http://bit.ly/object-formatters)
- Firefox:
  - [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)
  - [在 Firefox DevTools 中启用自定义对象格式化器](https://fxdx.dev/firefox-devtools-custom-object-formatters/)

## TypeScript 类型支持

TypeScript 默认无法处理 `.vue` 导入的类型信息，因此我们使用 `vue-tsc` 替代 `tsc` CLI 进行类型检查。在编辑器中，需要 [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) 来让 TypeScript 语言服务识别 `.vue` 类型。

## 项目安装

```sh
npm install
```

## 开发命令

### 启动开发服务器（热重载）

```sh
npm run dev
```

启动后，访问 `http://localhost:5173` 查看应用。

### 类型检查、编译和生产构建

```sh
npm run build
```

### 预览生产构建

```sh
npm run preview
```

### 使用 ESLint 进行代码检查

```sh
npm run lint
```

## 自定义配置

查看 [Vite 配置参考](https://vite.dev/config/)。

## 项目改进计划

### 已完成功能
- ✅ 集成 Element Plus 组件库
- ✅ 创建登录页面
- ✅ 实现表单验证功能
- ✅ 响应式设计

### 待改进功能
- [ ] 集成真实的登录 API
- [ ] 添加路由守卫，保护需要登录的页面
- [ ] 实现 token 管理和自动刷新
- [ ] 添加忘记密码功能
- [ ] 优化登录页面的错误处理
- [ ] 添加更多页面和功能模块

## 开发规范

### 代码注释规范

所有组件和函数都应包含详细的中文注释，包括：
- 组件/函数的用途和功能描述
- 输入参数说明 (@input)
- 处理过程说明 (@process)
- 输出结果说明 (@output)

### 代码风格

- 使用 TypeScript 进行类型约束
- 遵循 Vue 3 Composition API 最佳实践
- 使用 Element Plus 组件保持 UI 一致性
- 保持代码简洁、可维护、可扩展

## 许可证

本项目为私有项目。
