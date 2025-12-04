# Chatbot 测评框架使用说明

## 概述

本测评框架提供了一套完整的工具，用于评估 Chatbot 的各项能力，包括基础对话、知识问答、RAG 功能、工具使用等。

## 快速开始

### 1. 确保服务正在运行

```bash
# 启动 chatbot 服务
bash start.sh
```

等待服务完全启动（约 15-20 秒），确保后端运行在 http://localhost:5001

### 2. 运行完整测评

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行完整测评
cd evaluation
python run_evaluation.py
```

### 3. 查看测评结果

测评完成后，会生成以下文件：
- `evaluation_results.json` - 详细的测评结果（JSON 格式）
- `analysis_report.md` - 分析报告（Markdown 格式）

## 进阶使用

### 运行指定类别的测评

```bash
# 只测试基础对话和知识问答
python run_evaluation.py --categories basic_conversation,knowledge_qa

# 可用的类别:
# - basic_conversation: 基础对话能力
# - knowledge_qa: 知识问答能力
# - rag_functionality: RAG 功能
# - tool_usage: 工具使用能力
# - conversation_context: 对话上下文理解
# - edge_cases: 边界情况
# - multilingual: 多语言支持
```

### 指定 API 地址

```bash
# 如果服务运行在其他地址
python run_evaluation.py --api-url http://localhost:5001
```

### 自定义输出文件

```bash
# 指定输出文件名
python run_evaluation.py --output my_test_results.json
```

### 生成分析报告

```bash
# 基于测评结果生成详细的分析报告
python analyze_results.py

# 指定输入和输出文件
python analyze_results.py \
    --input my_test_results.json \
    --output my_analysis_report.md

# 生成 JSON 格式的报告
python analyze_results.py --format json
```

## 测评指标说明

### 1. 响应质量指标

- **相关性 (Relevance)**: 回答是否与问题相关（0-1 分）
- **准确性 (Accuracy)**: 信息是否准确（0-1 分）
- **清晰度 (Clarity)**: 表达是否清晰（0-1 分）

### 2. 功能性能指标

- **响应时间**: 系统响应速度（秒）
- **RAG 有效性**: 检索增强生成的准确率
- **工具成功率**: 外部工具调用成功率

### 3. 综合评分

综合评分 = (相关性 × 0.3) + (准确性 × 0.25) + (清晰度 × 0.2) + (响应时间 × 0.15) + (完整性 × 0.1)

**等级划分**:
- **优秀 (0.9-1.0)**: 表现卓越
- **良好 (0.8-0.89)**: 表现良好
- **中等 (0.7-0.79)**: 表现一般
- **及格 (0.6-0.69)**: 基本满足需求
- **不及格 (< 0.6)**: 需要大幅改进

## 测评用例结构

测评用例定义在 `test_cases.json` 文件中，包含以下类别：

### 1. 基础对话能力 (basic_conversation)
- 问候和告别
- 简单问答
- 礼貌用语

### 2. 知识问答能力 (knowledge_qa)
- 事实性问题
- 技术概念解释
- 比较和对比

### 3. RAG 功能 (rag_functionality)
- 文档内容检索
- 基于文档的问答
- 文档摘要生成

### 4. 工具使用能力 (tool_usage)
- 天气查询
- 网络搜索
- 其他工具调用

### 5. 对话上下文理解 (conversation_context)
- 指代消解
- 上下文保持
- 多轮对话

### 6. 边界情况 (edge_cases)
- 空输入
- 特殊字符
- 超长输入

### 7. 多语言支持 (multilingual)
- 英文对话
- 其他语言识别

## 添加新的测试用例

编辑 `test_cases.json` 文件，按照以下格式添加：

```json
{
  "id": "your_test_id",
  "query": "你的测试问题",
  "expected_keywords": ["期望的关键词1", "关键词2"],
  "expected_behavior": "期望的行为描述",
  "difficulty": "easy|medium|hard",
  "requires_search": false,
  "requires_rag": false,
  "requires_tools": false
}
```

## 解读测评报告

### 总体表现

查看 `analysis_report.md` 中的总体评分：

```markdown
| 指标 | 数值 | 评价 |
|------|------|------|
| 总体成功率 | 85% | 良好 |
| 平均响应时间 | 2.3秒 | 优秀 |
```

### 分类别表现

分析报告会显示每个类别的详细表现：

```markdown
### 基础对话能力

- **成功率**: 92% (优秀)
- **平均响应时间**: 1.2秒
- **平均相关性分数**: 0.95
```

### 改进建议

报告会提供具体的改进建议：

```markdown
### 1. RAG 功能 - RAG检索准确率较低

- **优先级**: 高
- **建议**: 优化向量嵌入模型，调整检索参数
- **预期改进**: 提升RAG准确率至0.8以上
```

## 常见问题

### Q1: 测评运行很慢怎么办？

A: 完整测评包含50+个测试用例，可能需要5-10分钟。可以：
- 只运行特定类别：`--categories basic_conversation`
- 减少测试用例数量（编辑 test_cases.json）

### Q2: 为什么有些测试总是失败？

A: 可能原因：
- API 服务未正确启动
- 网络连接问题
- 缺少必要的工具或依赖
- 测试用例的期望关键词设置不合理

### Q3: 如何提高测评分数？

A: 根据分析报告中的建议：
1. 优先解决高优先级问题
2. 优化RAG检索准确率
3. 提升响应速度
4. 改进错误处理机制

### Q4: 可以自定义评分标准吗？

A: 可以修改 `run_evaluation.py` 中的评分函数：
- `_calculate_relevance_score()`
- `_calculate_accuracy_score()`
- `_calculate_clarity_score()`

## 技术支持

如有问题或建议，请：
1. 检查日志文件（backend.log, frontend.log）
2. 查看 API 文档（http://localhost:5001/docs）
3. 提交 Issue 到项目仓库

## 版本信息

- 测评框架版本: 1.0
- 最后更新: 2024-12-03
- 兼容性: Python 3.11+
