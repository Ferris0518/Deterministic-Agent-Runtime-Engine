# Transport Domain 设计规范

> 版本: Draft v2  
> 状态: 待评审

---

## 1. 概述

Transport Domain 负责 **Client（用户端）与 Agent（编排端）之间的双向异步通信**。

### 设计原则

- **双向异步**：非请求-响应模式，双方可随时发送消息
- **关注点分离**：Client 和 Agent 各自只关心自己的收发逻辑
- **可扩展**：新增 Client 类型只需实现 MessageHandler

---

## 2. 接口定义 (Kernel)

```python
# === 基础接口 ===
class IOutputTransport(Protocol):
    """发送消息"""
    async def send(self, msg: Message) -> None: ...

class IInputTransport(Protocol):
    """接收消息"""
    async def on_message(self, msg: Message) -> None: ...

class ITransport(IInputTransport, IOutputTransport, Protocol):
    """完整的双向 Transport"""
    pass

# === 消息处理 ===
class IMessageHandler(Protocol):
    """消息处理器（用户/Agent 实现）"""
    async def handle(self, context: ITransportContext, msg: Message) -> None: ...

# === Transport Context ===
class ITransportContext(Protocol):
    """Transport 上下文（双方共用）"""
    async def put(self, msg: Message) -> None: ...
    def poll(self, msg_type: str | None = None) -> Message | None: ...

class IAgentTransportContext(ITransportContext, Protocol):
    """Agent 侧扩展上下文"""
    async def get(self, msg_type: str | None = None) -> Message: ...
    def register_task(self, task: asyncio.Task) -> None: ...
    def cancel_all_tasks(self) -> None: ...

# === Channel（传输通道）===
class IInputOutputChannel(Protocol):
    """双向通道：管理 Client 和 Agent 的连接"""
    def register_client(self, client: IInputTransport) -> IOutputTransport: ...
    def register_agent(self, agent: IInputTransport) -> IOutputTransport: ...

# === 角色专用接口 ===
class IClientTransport(ITransport, Protocol):
    """Client 侧 Transport 接口"""
    @property
    def context(self) -> ITransportContext: ...

class IAgentTransport(ITransport, Protocol):
    """Agent 侧 Transport 接口"""
    @property
    def context(self) -> IAgentTransportContext: ...
    async def recv(self, msg_type: str | None = None) -> Message: ...
    def run_interruptible(self, coro) -> asyncio.Task: ...
```

---

## 3. 消息协议

```python
@dataclass
class Message:
    type: str       # 消息类型
    payload: Any    # 消息内容
    timestamp: float = field(default_factory=time.time)
```

### 消息类型

| 方向 | type | payload | 说明 |
|------|------|---------|------|
| Client→Agent | `task` | `{text}` | 任务请求 |
| Client→Agent | `message` | `{text}` | 运行时补充 |
| Client→Agent | `authorize.response` | `{approved}` | 授权响应 |
| Client→Agent | `interrupt` | `{}` | 中断信号 |
| Agent→Client | `thinking` | `{content}` | LLM 思考 |
| Agent→Client | `response` | `{content}` | LLM 响应 |
| Agent→Client | `tool.start` | `{id, params}` | 工具开始 |
| Agent→Client | `tool.result` | `{id, result}` | 工具结果 |
| Agent→Client | `authorize.request` | `{id, summary}` | 请求授权 |
| Agent→Client | `complete` | `{success}` | 任务完成 |

> **注：** Tool 事件可通过 `ToolHookTransport` 从 Hook 系统桥接发送。

---

## 4. 架构

### 4.1 角色

```
┌─────────────────┐                           ┌─────────────────┐
│ ClientTransport │                           │ AgentTransport  │
├─────────────────┤                           ├─────────────────┤
│ context         │                           │ context         │
│ handler         │                           │ handler         │
│ _output ────────┼───┐                   ┌───┼──────── _output │
│ on_message() ◄──┼─┐ │                   │ ┌─┼─► on_message()  │
└─────────────────┘ │ │                   │ │ │ recv()          │
                    │ │ ┌───────────────┐ │ │ └─────────────────┘
                    │ └►│IInputOutput   │◄┘ │
                    │   │   Channel     │   │
                    │   ├───────────────┤   │
                    │   │_client ───────┼───┘
                    └───┼─────── _agent │
                        │register_client│
                        │register_agent │
                        └───────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                   ▼
    ┌─────────────────┐                 ┌─────────────────┐
    │ProcessorChannel │                 │WebSocketChannel │
    │  (同进程直连)    │                 │  (远程连接)      │
    └─────────────────┘                 └─────────────────┘
```

### 4.2 职责划分

| 角色 | 职责 |
|------|------|
| **IInputOutputChannel** | 双向通道接口：`register_client()`/`register_agent()` 注册两端 |
| **ProcessorChannel** | 同进程实现：直接转发消息 |
| **WebSocketChannel** | 远程实现：通过 WebSocket 传输消息 |
| **ClientTransport** | 组合 Channel，调用 `handler` 处理消息，管理 `context` |
| **AgentTransport** | 组合 Channel，提供 `recv()` 阻塞等待，可中断任务管理 |
| **TransportContext** | 基础：消息缓冲 (`put`/`poll`) |
| **AgentTransportContext** | 扩展：阻塞等待 (`get`) + 任务管理 |

---

## 5. 实现

### 5.1 ProcessorChannel（同进程直连）

```python
class ProcessorChannel(IInputOutputChannel):
    """同进程直连通道：直接调用对端的 on_message()"""
    
    def __init__(self):
        self._client: IInputTransport | None = None
        self._agent: IInputTransport | None = None
    
    def register_client(self, client: IInputTransport) -> IOutputTransport:
        self._client = client
        return _ChannelSender(target=lambda: self._agent)
    
    def register_agent(self, agent: IInputTransport) -> IOutputTransport:
        self._agent = agent
        return _ChannelSender(target=lambda: self._client)


class _ChannelSender(IOutputTransport):
    def __init__(self, target: Callable[[], IInputTransport | None]):
        self._get_target = target
    
    async def send(self, msg: Message) -> None:
        target = self._get_target()
        if target:
            await target.on_message(msg)
```

### 5.2 StdioChannel（标准输入输出）

```python
class StdioChannel(IInputOutputChannel):
    """Stdio 通道：映射到 stdin/stdout"""
    
    def __init__(self):
        self._client: IInputTransport | None = None
        self._agent: IInputTransport | None = None
    
    def register_client(self, client: IInputTransport) -> IOutputTransport:
        self._client = client
        return _StdioClientSender()
    
    def register_agent(self, agent: IInputTransport) -> IOutputTransport:
        self._agent = agent
        return _StdioAgentSender()


class _StdioClientSender(IOutputTransport):
    """Client 发送消息到 stdout (Agent 会从 stdin 读)"""
    async def send(self, msg: Message) -> None:
        print(serialize(msg), flush=True)

class _StdioAgentSender(IOutputTransport):
    """Agent 发送消息到 stdout (Client 会从 stdin 读)"""
    async def send(self, msg: Message) -> None:
        print(serialize(msg), flush=True)
```

### 5.3 ClientTransport

```python
class ClientTransport(IClientTransport):
    """Client 侧：组合 Channel，管理 context 和 handler"""
    
    def __init__(self, channel: IInputOutputChannel, handler: IMessageHandler):
        self._handler = handler
        self._context = TransportContext()
        self._output = channel.register_client(self)
    
    @property
    def context(self) -> TransportContext:
        return self._context
    
    async def send(self, msg: Message) -> None:
        await self._output.send(msg)
    
    async def on_message(self, msg: Message) -> None:
        await self._handler.handle(self._context, msg)
```

### 5.4 AgentTransport

```python
class AgentTransport(IAgentTransport):
    """Agent 侧：组合 Channel，提供 recv() 和可中断任务"""
    
    def __init__(self, channel: IInputOutputChannel, handler: IMessageHandler | None = None):
        self._context = AgentTransportContext()
        self._handler = handler or AgentMessageHandler()
        self._output = channel.register_agent(self)
    
    @property
    def context(self) -> AgentTransportContext:
        return self._context
    
    async def send(self, msg: Message) -> None:
        await self._output.send(msg)
    
    async def on_message(self, msg: Message) -> None:
        await self._handler.handle(self._context, msg)
    
    async def recv(self, msg_type: str | None = None) -> Message:
        return await self._context.get(msg_type)
    
    def run_interruptible(self, coro) -> asyncio.Task:
        task = asyncio.create_task(coro)
        self._context.register_task(task)
        return task


class AgentMessageHandler(IMessageHandler):
    async def handle(self, context: IAgentTransportContext, msg: Message) -> None:
        if msg.type == "interrupt":
            context.cancel_all_tasks()
        else:
            await context.put(msg)
```

### 5.5 TransportContext（基础）

```python
class TransportContext(ITransportContext):
    """基础上下文：消息缓冲（Client/Agent 共用）"""
    
    def __init__(self):
        self._queue: deque[Message] = deque()
    
    async def put(self, msg: Message) -> None:
        self._queue.append(msg)
    
    def poll(self, msg_type: str | None = None) -> Message | None:
        """非阻塞获取消息，无匹配返回 None"""
        for i, msg in enumerate(self._queue):
            if msg_type is None or msg.type == msg_type:
                del self._queue[i]
                return msg
        return None
```

### 5.6 AgentTransportContext（扩展）

```python
class AgentTransportContext(TransportContext, IAgentTransportContext):
    """Agent 侧扩展：阻塞等待 + 任务管理"""
    
    def __init__(self):
        super().__init__()
        self._event = asyncio.Event()
        self._tasks: dict[str, asyncio.Task] = {}
    
    async def put(self, msg: Message) -> None:
        await super().put(msg)
        self._event.set()  # 通知有新消息
    
    async def get(self, msg_type: str | None = None) -> Message:
        """阻塞等待匹配消息"""
        while True:
            msg = self.poll(msg_type)
            if msg:
                return msg
            self._event.clear()
            await self._event.wait()
    
    def register_task(self, task: asyncio.Task) -> None:
        key = str(id(task))
        self._tasks[key] = task
        task.add_done_callback(lambda _: self._tasks.pop(key, None))
    
    def cancel_all_tasks(self) -> None:
        for t in self._tasks.values():
            t.cancel()
        self._tasks.clear()
```



## 6. Client 扩展指南

### 用户需要做什么

1. **实现 `IMessageHandler`**：处理从 Agent 收到的消息
2. **通过 `transport.send()` 发送消息**：向 Agent 发送任务/授权/中断等

### 示例：Stdio Client

```python
class StdioClient(ClientTransport):
    def __init__(self, channel: IInputOutputChannel):
        handler = CLIHandler(lambda: self)
        super().__init__(channel, handler)
    
    async def run(self):
        """主循环：从 stdin 持续读取并分发到 on_message"""
        while True:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line: break
            msg = deserialize(line)
            await self.on_message(msg)

class CLIHandler(IMessageHandler):
    def __init__(self, get_client: Callable[[], StdioClient]):
        self._get_client = get_client
    
    async def handle(self, context: TransportContext, msg: Message) -> None:
        match msg.type:
            case "response":
                print(f"Agent: {msg.payload['content']}")
            case "authorize.request":
                # ... 处理授权 ...
                pass

# 初始化
channel = StdioChannel()
client = StdioClient(channel)
await client.run()
```

---

## 7. Agent 集成

### 编排中使用

```python
class FiveLayerAgent:
    def __init__(self, endpoint: IAgentTransport):
        self.client_endpoint = endpoint  # 编排层通过此端点与外部通信
    
    async def run(self):
        # 模拟：等待初始任务
        task_msg = await self.client_endpoint.recv(msg_type="task")
        
        # 发送思考中
        await self.client_endpoint.send(Message(type="thinking", ...))
        
        # 可中断的模型调用
        task = self.client_endpoint.run_interruptible(
            self._model.generate(task_msg.payload["text"])
        )
        response = await task
        
        # 发送最终响应
        await self.client_endpoint.send(Message(type="response", ...))
```

## 8. 启动与初始化 (Bootstrap)

无论是同进程还是 Stdio 模式，最终都需要一个启动入口。

### 示例：Stdio 模式启动

```python
async def main():
    # 1. 创建通道
    channel = StdioChannel()
    
    # 2. 创建端点
    # Client 包装 channel
    client = StdioClient(channel)
    
    # Agent 包装 channel 并注入到业务类
    agent_endpoint = AgentTransport(channel)
    agent = FiveLayerAgent(agent_endpoint)
    
    # 3. 并发运行
    await asyncio.gather(
        agent.run(),
        client.run()
    )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 9. Hook 桥接（可选）

```python
class ToolHookTransport:
    """将 Hook 事件桥接到 Transport"""
    
    def __init__(self, endpoint: IAgentTransport):
        self._endpoint = endpoint
    
    async def on_tool_start(self, tool_id: str, params: dict):
        await self._endpoint.send(Message(type="tool.start", payload={...}))
    
    async def on_tool_result(self, tool_id: str, result: Any):
        await self._endpoint.send(Message(type="tool.result", payload={...}))
```

---

## 10. 未来扩展

| 场景 | 替换组件 |
|------|----------|
| 跨进程通信 | 实现 `WebSocketChannel` 替代 `ProcessorChannel` |
| 多 Client | Channel 内部支持多个 Client/Agent 注册 |
| 消息持久化 | 在 `IInputOutputChannel.send()` 链条中添加日志层 |
