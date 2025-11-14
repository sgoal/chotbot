#!/usr/bin/env python3
"""
MCP 工具管理器
"""

from typing import Dict, Any, List
from chotbot.mcp.tools.weather import WeatherTool
from chotbot.mcp.tools.fund import FundTool

class ToolManager:
    """
    工具管理器类，用于管理所有可调用的 MCP 工具
    """
    
    def __init__(self):
        self.tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """
        初始化所有工具
        """
        self.tools["查询天气"] = WeatherTool()
        self.tools["查询基金信息"] = FundTool()
    
    def get_tool_list(self) -> List[Dict[str, Any]]:
        """
        获取所有可用工具的列表
        
        Returns:
            List[Dict[str, Any]]: 工具列表
        """
        tool_list = []
        
        for tool_name, tool_instance in self.tools.items():
            # 获取工具的方法信息
            methods = []
            for method_name in dir(tool_instance):
                if not method_name.startswith('_'):
                    method = getattr(tool_instance, method_name)
                    if callable(method):
                        methods.append(method_name)
            
            tool_list.append({
                "name": tool_name,
                "type": tool_instance.__class__.__name__,
                "methods": methods
            })
        
        return tool_list
    
    def get_tool(self, tool_name: str):
        """
        根据工具名称获取工具实例
        
        Args:
            tool_name (str): 工具名称
            
        Returns:
            object: 工具实例
        """
        return self.tools.get(tool_name)
    
    def call_tool(self, tool_name: str, method: str, **kwargs) -> Any:
        """
        调用指定工具的指定方法
        
        Args:
            tool_name (str): 工具名称
            method (str): 方法名称
            **kwargs: 方法参数
            
        Returns:
            Any: 工具调用结果
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return {"error": f"工具 {tool_name} 不存在"}
        
        if not hasattr(tool, method):
            return {"error": f"工具 {tool_name} 没有方法 {method}"}
        
        tool_method = getattr(tool, method)
        
        try:
            result = tool_method(**kwargs)
            return result
        except Exception as e:
            return {"error": f"工具调用失败: {str(e)}", "message": "请检查参数是否正确"}
