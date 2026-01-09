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

### 表格页面 (`/table`)

表格页面位于 `src/views/TableView.vue`，提供完整的数据表格展示和管理功能。

#### 功能特性

1. **布局结构**
   - 使用 Element Plus Container 组件构建左右布局
   - 左侧导航栏：固定宽度 200px，包含页面导航菜单
   - 右侧主内容区：自适应宽度，包含表格和操作功能
   - 全屏显示，响应式设计

2. **导航功能**
   - 左侧导航栏提供页面快速切换
   - 支持路由跳转，自动高亮当前页面
   - 菜单项包含图标和文字说明

3. **表格功能**
   - 数据列表展示：支持多列数据显示
   - 行选择：支持单选和多选
   - 分页功能：支持自定义每页显示数量
   - 数据操作：新增、编辑、删除（单行和批量）

4. **用户体验**
   - 表格边框和斑马纹样式
   - 操作按钮图标提示
   - 删除操作二次确认
   - 操作成功/失败消息提示

#### 使用方法

1. **访问表格页面**：在浏览器中访问 `/table` 路由，或通过左侧导航栏点击"数据表格"
2. **查看数据**：表格自动加载并显示数据列表
3. **选择数据**：点击表格左侧复选框选择单行或多行数据
4. **新增数据**：点击"新增"按钮（功能待实现）
5. **编辑数据**：点击表格操作列的"编辑"按钮（功能待实现）
6. **删除数据**：
   - 单行删除：点击表格操作列的"删除"按钮
   - 批量删除：先选择多行数据，再点击工具栏的"删除"按钮
7. **刷新数据**：点击"刷新"按钮重新加载数据
8. **分页操作**：使用底部分页组件切换页码或修改每页显示数量

#### 布局结构说明

**Container 组件结构：**
- `<el-container>`：主容器，全屏布局
- `<el-aside>`：左侧导航栏，固定宽度 200px
- `<el-main>`：右侧主内容区，自适应宽度

**导航菜单配置：**
- 使用 `el-menu` 组件实现导航菜单
- 通过 `router` 属性启用路由跳转
- 菜单项通过 `index` 属性指定路由路径

#### 参数说明

**表格数据 (tableData)**
- `id` (number): 数据唯一标识
- `name` (string): 姓名
- `age` (number): 年龄
- `email` (string): 邮箱地址
- `address` (string): 地址

**分页参数**
- `currentPage` (number): 当前页码，默认 1
- `pageSize` (number): 每页显示数量，默认 10，可选值：[10, 20, 50, 100]
- `total` (number): 数据总数

#### 返回值说明

- **删除成功**：显示成功消息，更新表格数据
- **删除取消**：无操作，保持原数据不变
- **刷新成功**：显示成功消息，重新加载数据

#### 注意事项

- 当前数据为模拟数据，实际项目中需要替换为真实的 API 调用
- 新增和编辑功能目前仅显示提示信息，需要后续实现对话框和表单
- 分页功能目前仅更新显示，实际项目中需要调用 API 获取对应页数据
- 左侧导航栏宽度固定为 200px，可根据需求调整

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
- ✅ 表格页面使用 Container 布局（左侧导航栏 + 右侧表格区域）

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
