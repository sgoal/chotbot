#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json

# 将src目录添加到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from unittest.mock import Mock, MagicMock
except ImportError:
    from mock import Mock, MagicMock  # Python 2.7 compatibility
from chotbot.core.react_agent import ReActAgent
from chotbot.mcp.tools.search import SearchTool

# 测试ReActAgent的引用功能
def test_citation_feature():
    # 创建模拟的LLM客户端
    mock_llm = Mock()
    
    # 配置LLM的响应
    # 第一次响应生成搜索行动
    mock_llm.generate = MagicMock(side_effect=[
        "search[What is AI]",  # 第一次调用：生成搜索行动
        "Final Answer: Artificial Intelligence (AI) is the simulation of human intelligence in machines."  # 第二次调用：生成最终答案
    ])
    
    # 创建工具管理器并添加搜索工具
    mock_tool_manager = Mock()
    
    # 创建搜索工具实例
    search_tool = SearchTool()
    
    # 模拟搜索结果
    mock_tool_manager.get_tool_list = Mock(return_value="search")
    mock_tool_manager.get_tool = Mock(return_value=search_tool)
    
    # 创建ReActAgent
    agent = ReActAgent(mock_llm, mock_tool_manager)
    
    # 运行代理
    user_input = "What is AI?"
    final_answer, thinking_steps = agent.run(user_input, max_steps=10)
    
    # 打印结果
    print("Final Answer:")
    print(final_answer)
    print("\nThinking Steps:")
    for step in thinking_steps:
        print(json.dumps(step, indent=2, ensure_ascii=False))
    
    # 检查是否包含引用
    assert "引用来源" in final_answer, "Final answer should include citations"
    
    return True

if __name__ == "__main__":
    try:
        if test_citation_feature():
            print("\n✅ Citation feature test passed!")
    except Exception as e:
        print("\n❌ Citation feature test failed: %s" % e)
        import traceback
        traceback.print_exc()
