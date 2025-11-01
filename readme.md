# 🐺 狼人杀在线游戏系统

一个基于 Vue3 + FastAPI 的在线狼人杀游戏平台

## 技术栈

### 后端
- **FastAPI** - 现代、快速的 Web 框架
- **PostgreSQL/MySQL** - 关系型数据库
- **Redis** - 缓存和消息队列
- **WebSocket** - 实时通信
- **JWT** - 用户认证
- **SQLAlchemy** - ORM 框架
- **Alembic** - 数据库迁移工具

### 前端
- **Vue 3** - 渐进式前端框架
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP 客户端
- **Vite** - 构建工具

## 项目结构

```
Werewolf/
├── backend/              # 后端代码
│   ├── app/
│   │   ├── api/         # API路由
│   │   │   ├── auth.py  # 认证相关
│   │   │   ├── users.py # 用户相关
│   │   │   └── rooms.py # 房间相关
│   │   ├── core/        # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── database.py    # 数据库连接
│   │   │   ├── security.py    # 安全相关（JWT、密码）
│   │   │   └── redis_client.py # Redis客户端
│   │   ├── models/      # 数据模型
│   │   │   ├── user.py  # 用户模型
│   │   │   └── game.py  # 游戏模型
│   │   ├── services/    # 业务逻辑
│   │   │   └── game_engine.py # 游戏引擎
│   │   ├── websocket/   # WebSocket服务
│   │   │   ├── manager.py # 连接管理
│   │   │   └── router.py  # WebSocket路由
│   │   └── main.py     # 应用入口
│   ├── requirements.txt
│   └── .env.example    # 环境变量示例
│
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── views/       # 页面组件
│   │   │   ├── Login.vue    # 登录页
│   │   │   ├── Register.vue # 注册页
│   │   │   ├── Home.vue     # 大厅页
│   │   │   ├── Room.vue     # 房间页
│   │   │   ├── Game.vue     # 游戏页
│   │   │   └── Profile.vue  # 个人中心
│   │   ├── components/  # 公共组件
│   │   ├── stores/     # Pinia状态管理
│   │   │   ├── auth.js  # 认证状态
│   │   │   └── room.js  # 房间状态
│   │   ├── api/        # API调用
│   │   │   └── index.js # Axios配置
│   │   ├── router/     # 路由配置
│   │   │   └── index.js
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── 设计文档.md          # 项目设计文档
└── README.md
```

## 功能特性

- ✅ **用户系统** - 注册、登录、个人信息管理
- ✅ **房间管理** - 创建房间、加入房间、房间列表
- ✅ **实时通信** - WebSocket 实时聊天和游戏事件
- ✅ **游戏引擎** - 角色分配、状态机、回合控制
- ✅ **游戏逻辑** - 夜晚行动、白天投票、胜负判定
- ✅ **角色系统** - 村民、狼人、预言家、女巫、猎人、守卫
- ✅ **玩家发言** - 白天阶段玩家发言讨论，发言记录在游戏日志中
- ✅ **AI 助手接口** - 提供 API 接口获取游戏日志和玩家角色，支持 AI 辅助分析

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- PostgreSQL/MySQL
- Redis

### 后端启动

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库、Redis等信息
```

5. 初始化数据库：
```bash
# 使用 Alembic 创建数据库表
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

6. 启动服务：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

4. 访问应用：
打开浏览器访问 `http://localhost:5173`

## API 文档

后端启动后，可以访问以下地址查看 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### AI 助手接口

系统提供专门的 API 接口供 AI 助手获取游戏信息，帮助玩家进行游戏策略分析。

#### 1. 获取游戏日志（包含玩家发言）

```http
GET /api/ai/game/{room_code}/logs?limit=100
Authorization: Bearer {token}
```

**参数：**
- `room_code` (路径参数): 房间号
- `limit` (查询参数, 可选): 限制返回的日志数量，不传则返回全部

**响应：**
```json
{
  "logs": [
    {
      "type": "game_log",
      "round": 1,
      "phase": "day",
      "message": "💬 玩家A: 我认为玩家B是狼人",
      "timestamp": "2024-01-01T10:00:00",
      "player_id": 1,
      "player_name": "玩家A"
    },
    {
      "type": "game_log",
      "round": 1,
      "phase": "night",
      "message": "🌙 第 1 夜开始，请各位玩家进行行动",
      "timestamp": "2024-01-01T09:50:00"
    }
  ],
  "total_count": 50
}
```

#### 2. 获取玩家角色信息

```http
GET /api/ai/game/{room_code}/player-info
Authorization: Bearer {token}
```

**响应：**
```json
{
  "player_id": 1,
  "player_name": "玩家A",
  "role": "seer",
  "is_alive": true,
  "seat_number": 1
}
```

**角色说明：**
- `villager`: 村民
- `werewolf`: 狼人
- `seer`: 预言家
- `witch`: 女巫
- `hunter`: 猎人
- `guard`: 守卫

#### 3. 获取完整游戏上下文（推荐）

```http
GET /api/ai/game/{room_code}/context
Authorization: Bearer {token}
```

**响应：**
```json
{
  "game_id": 1,
  "room_code": "ABC123",
  "current_round": 2,
  "current_phase": "day",
  "player_info": {
    "player_id": 1,
    "player_name": "玩家A",
    "role": "seer",
    "is_alive": true,
    "seat_number": 1
  },
  "game_logs": [
    {
      "type": "game_log",
      "round": 1,
      "phase": "day",
      "message": "💬 玩家A: 我认为玩家B是狼人",
      "timestamp": "2024-01-01T10:00:00",
      "player_id": 1,
      "player_name": "玩家A"
    }
  ],
  "alive_players": [1, 2, 3, 4, 5, 6],
  "dead_players": [7, 8]
}
```

**使用场景：**

AI 助手可以通过此接口获取完整的游戏上下文，包括：
- 当前玩家的角色和身份
- 完整的游戏日志（包含所有玩家发言）
- 游戏当前状态（轮次、阶段）
- 存活和死亡玩家列表

**示例代码（Python）：**

```python
import requests

# 获取游戏上下文
def get_game_context(room_code: str, token: str):
    url = f"http://localhost:8000/api/ai/game/{room_code}/context"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"获取游戏上下文失败: {response.status_code}")

# 使用示例
context = get_game_context("ABC123", "your_jwt_token")
player_role = context["player_info"]["role"]
game_logs = context["game_logs"]

# 基于角色和日志进行分析
if player_role == "seer":
    # 预言家的策略分析
    pass
```

**注意事项：**
- 所有接口都需要 JWT 认证
- 接口会验证用户是否在对应的游戏中
- 游戏日志包含系统事件和玩家发言
- 玩家发言格式：`💬 [玩家名称]: [发言内容]`

## 开发计划

详细开发计划请参考 `设计文档.md`

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
