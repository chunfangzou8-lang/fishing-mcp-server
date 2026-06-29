#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文字钓鱼游戏 MCP 服务器
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

# 确保使用 UTF-8 编码
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# 导入游戏引擎
import engine


class MCPServer:
    """MCP 协议服务器"""

    def __init__(self):
        self.tools = [
            {
                "name": "fishing_command",
                "description": "执行钓鱼游戏指令。支持所有游戏命令：help, status, shop, buy, cast, goto, inventory, sell, encyclopedia, look 等",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "游戏指令，例如：'cast'（抛竿）、'buy basic_worm 5'（买饵）、'status'（查看状态）、'cast 10'（连钓10竿）"
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "fishing_new_game",
                "description": "重新开始新游戏，可选择指定随机种子（相同种子会产生相同的游戏结果）",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "seed": {
                            "type": "integer",
                            "description": "随机种子（可选，默认为 2619879833）"
                        }
                    }
                }
            }
        ]

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理 MCP 请求"""
        method = request.get("method")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "fishing-game",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "tools": self.tools
                }
            }

        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            try:
                if tool_name == "fishing_command":
                    command = arguments.get("command", "")
                    result = engine.cmd(command)

                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result
                                }
                            ]
                        }
                    }

                elif tool_name == "fishing_new_game":
                    seed = arguments.get("seed", 0x9e3779b9)
                    result = engine.new_game(seed)

                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result
                                }
                            ]
                        }
                    }

                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }

            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }

        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    def run(self):
        """运行 MCP 服务器（stdio 模式）"""
        while True:
            try:
                # 读取一行输入
                line = sys.stdin.readline()
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                # 解析 JSON-RPC 请求
                request = json.loads(line)

                # 处理请求
                response = self.handle_request(request)

                # 发送响应
                print(json.dumps(response, ensure_ascii=False), flush=True)

            except KeyboardInterrupt:
                break
            except Exception as e:
                # 错误响应
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    server = MCPServer()
    server.run()
