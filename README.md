# 🎣 钓鱼游戏 MCP 服务器

基于 tutusagi/ai-fishing-game 的 MCP（Model Context Protocol）服务器实现。

## 项目说明

这是一个文字钓鱼游戏的 MCP 服务器，可以让 Claude 通过 MCP 协议远程玩钓鱼游戏。

## 功能特性

- ✅ 完整的钓鱼游戏引擎
- ✅ MCP 协议支持
- ✅ HTTP 接口（适合 Render 等平台部署）
- ✅ 持久化存档
- ✅ 确定性随机（相同种子产生相同结果）

## 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 HTTP 服务器
python app.py

# 测试健康检查
curl http://localhost:10000/health
```

## 部署到 Render

### 步骤 1: 准备 Git 仓库

```bash
# 在项目目录下初始化 Git
git init
git add .
git commit -m "Initial commit"

# 推送到 GitHub（需要先在 GitHub 创建仓库）
git remote add origin https://github.com/你的用户名/fishing-mcp-server.git
git push -u origin main
```

### 步骤 2: 在 Render 上部署

1. 访问 [Render.com](https://render.com)
2. 注册/登录账号
3. 点击 "New +" → "Web Service"
4. 连接你的 GitHub 仓库
5. 配置如下：
   - **Name**: `fishing-mcp-server`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: 选择 Free（免费套餐）
6. 点击 "Create Web Service"

### 步骤 3: 获取服务器地址

部署完成后，Render 会给你一个地址，例如：
```
https://fishing-mcp-server-xxxx.onrender.com
```

## 连接到 Claude Code

在 Claude Code 中添加 MCP 服务器配置：

1. 打开 `~/.claude/settings.json`（或使用 `/config` 命令）

2. 添加 MCP 服务器配置：

```json
{
  "mcpServers": {
    "fishing-game": {
      "url": "https://你的render地址.onrender.com/mcp",
      "transport": "http"
    }
  }
}
```

3. 重启 Claude Code

## 可用工具

### fishing_command
执行游戏指令，支持：
- `help` - 查看帮助
- `status` - 查看状态
- `shop` - 查看商店
- `buy <饵> <数量>` - 购买鱼饵
- `cast [次数]` - 抛竿钓鱼
- `goto [地点]` - 前往地点
- `inventory` - 查看背包
- `sell all` - 卖掉所有鱼
- `encyclopedia` - 查看图鉴

### fishing_new_game
重新开始新游戏，可选指定随机种子

## 游戏说明

- 初始：200 点，5 个普通蚯蚓
- 买饵 → 抛竿 → 钓鱼 → 卖鱼 → 赚点数 → 解锁新地点
- 集齐图鉴，探索不同稀有度的鱼
- 季节会随回合推进而变化

## License

MIT
