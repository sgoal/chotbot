#!/usr/bin/env python3
"""
Chatbot 测评结果分析工具

使用方法:
    python evaluation/analyze_results.py [--input INPUT_FILE] [--output OUTPUT_FILE]

参数:
    --input: 输入的测评结果文件 (默认: evaluation/evaluation_results.json)
    --output: 输出的分析报告文件 (默认: evaluation/analysis_report.md)
    --format: 输出格式 (markdown/json, 默认: markdown)
"""

import json
import argparse
from typing import Dict, List, Any
from datetime import datetime


class ResultsAnalyzer:
    """测评结果分析器"""

    def __init__(self, results_file: str):
        self.results_file = results_file
        self.data = self._load_results()

    def _load_results(self) -> Dict[str, Any]:
        """加载测评结果"""
        try:
            with open(self.results_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"错误: 找不到结果文件 {self.results_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"错误: JSON 格式错误: {e}")
            return {}

    def generate_summary(self) -> Dict[str, Any]:
        """生成总体摘要"""
        if not self.data:
            return {}

        summary = {
            "timestamp": self.data.get("timestamp", ""),
            "api_url": self.data.get("api_url", ""),
            "total_tests": self.data.get("total_tests", 0),
            "total_passed": self.data.get("total_passed", 0),
            "total_failed": self.data.get("total_failed", 0),
            "overall_success_rate": self.data.get("overall_success_rate", 0),
            "average_response_time": self.data.get("average_response_time", 0),
        }

        # 计算等级
        success_rate = summary["overall_success_rate"]
        if success_rate >= 0.9:
            summary["grade"] = "优秀"
        elif success_rate >= 0.8:
            summary["grade"] = "良好"
        elif success_rate >= 0.7:
            summary["grade"] = "中等"
        elif success_rate >= 0.6:
            summary["grade"] = "及格"
        else:
            summary["grade"] = "不及格"

        return summary

    def analyze_categories(self) -> List[Dict[str, Any]]:
        """分析各个类别的表现"""
        category_results = self.data.get("category_results", [])
        category_analysis = []

        for category in category_results:
            success_rate = (
                category["passed_tests"] / category["total_tests"]
                if category["total_tests"] > 0
                else 0
            )

            # 计算等级
            if success_rate >= 0.9:
                grade = "优秀"
            elif success_rate >= 0.8:
                grade = "良好"
            elif success_rate >= 0.7:
                grade = "中等"
            elif success_rate >= 0.6:
                grade = "及格"
            else:
                grade = "不及格"

            category_analysis.append({
                "category": category["category"],
                "description": category["description"],
                "total_tests": category["total_tests"],
                "passed_tests": category["passed_tests"],
                "failed_tests": category["failed_tests"],
                "success_rate": success_rate,
                "grade": grade,
                "average_response_time": category["average_response_time"],
                "average_relevance_score": category["average_relevance_score"],
            })

        # 按成功率排序
        category_analysis.sort(key=lambda x: x["success_rate"], reverse=True)

        return category_analysis

    def identify_weak_areas(self) -> List[Dict[str, Any]]:
        """识别薄弱环节"""
        weak_areas = []
        category_analysis = self.analyze_categories()

        for category in category_analysis:
            success_rate = category["success_rate"]

            if success_rate < 0.6:
                priority = "高"
                issue = "表现较差，需要大幅改进"
            elif success_rate < 0.7:
                priority = "中"
                issue = "表现一般，有明显改进空间"
            elif success_rate < 0.8:
                priority = "低"
                issue = "表现良好，有小瑕疵"
            else:
                continue

            weak_areas.append({
                "category": category["category"],
                "success_rate": success_rate,
                "priority": priority,
                "issue": issue,
                "average_response_time": category["average_response_time"],
            })

        return weak_areas

    def analyze_test_cases(self) -> Dict[str, Any]:
        """分析测试用例详情"""
        category_results = self.data.get("category_results", [])

        failed_cases = []
        slow_cases = []

        for category in category_results:
            for test_result in category["test_results"]:
                if not test_result["success"]:
                    failed_cases.append({
                        "category": category["category"],
                        "test_id": test_result["test_id"],
                        "query": test_result["query"],
                        "response": test_result["response"][:200] + "..." if len(test_result["response"]) > 200 else test_result["response"],
                        "missing_keywords": test_result["missing_keywords"],
                        "response_time": test_result["response_time"],
                    })

                if test_result["response_time"] > 5.0:
                    slow_cases.append({
                        "category": category["category"],
                        "test_id": test_result["test_id"],
                        "query": test_result["query"],
                        "response_time": test_result["response_time"],
                    })

        return {
            "failed_cases": failed_cases,
            "slow_cases": slow_cases,
            "total_failed": len(failed_cases),
            "total_slow": len(slow_cases),
        }

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """生成改进建议"""
        recommendations = []
        weak_areas = self.identify_weak_areas()

        for area in weak_areas:
            category = area["category"]
            success_rate = area["success_rate"]

            if "rag" in category.lower():
                recommendations.append({
                    "priority": area["priority"],
                    "category": category,
                    "issue": "RAG检索准确率较低",
                    "suggestion": "优化向量嵌入模型，调整检索参数，增加文档预处理",
                    "expected_improvement": "提升RAG准确率至0.8以上",
                })
            elif "tool" in category.lower():
                recommendations.append({
                    "priority": area["priority"],
                    "category": category,
                    "issue": "工具调用成功率较低",
                    "suggestion": "检查工具接口稳定性，增加错误重试机制，优化工具选择逻辑",
                    "expected_improvement": "提升工具调用成功率至0.85以上",
                })
            elif "conversation" in category.lower():
                recommendations.append({
                    "priority": area["priority"],
                    "category": category,
                    "issue": "上下文理解能力较弱",
                    "suggestion": "增强对话状态管理，改进上下文编码机制，增加对话历史权重",
                    "expected_improvement": "提升上下文保持能力至0.8以上",
                })
            else:
                recommendations.append({
                    "priority": area["priority"],
                    "category": category,
                    "issue": f"{category}表现不佳",
                    "suggestion": "增加训练数据，优化模型参数，改进提示词工程",
                    "expected_improvement": f"提升{category}成功率至0.8以上",
                })

        # 响应时间优化建议
        avg_response_time = self.data.get("average_response_time", 0)
        if avg_response_time > 3.0:
            recommendations.append({
                "priority": "中",
                "category": "性能优化",
                "issue": f"响应时间较慢 (平均{avg_response_time:.2f}秒)",
                "suggestion": "实现响应缓存机制，优化模型加载，考虑使用更快的推理引擎",
                "expected_improvement": "将平均响应时间降低至2秒以内",
            })

        # 按优先级排序
        priority_order = {"高": 0, "中": 1, "低": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return recommendations

    def generate_markdown_report(self, output_file: str):
        """生成 Markdown 格式的分析报告"""
        summary = self.generate_summary()
        category_analysis = self.analyze_categories()
        weak_areas = self.identify_weak_areas()
        test_case_analysis = self.analyze_test_cases()
        recommendations = self.generate_recommendations()

        report = f"""# Chatbot 测评分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**API 地址**: {summary.get('api_url', 'N/A')}  
**测评结果文件**: {self.results_file}

---

## 📊 总体表现

| 指标 | 数值 | 评价 |
|------|------|------|
| 总体成功率 | {summary.get('overall_success_rate', 0):.2%} | {summary.get('grade', 'N/A')} |
| 总测试数 | {summary.get('total_tests', 0)} | - |
| 通过数 | {summary.get('total_passed', 0)} | - |
| 失败数 | {summary.get('total_failed', 0)} | - |
| 平均响应时间 | {summary.get('average_response_time', 0):.3f}秒 | {'优秀' if summary.get('average_response_time', 0) < 2 else '良好' if summary.get('average_response_time', 0) < 5 else '需要改进'} |

**综合评级**: {summary.get('grade', 'N/A')}

---

## 📋 分类别表现

"""

        for category in category_analysis:
            report += f"""### {category['category'].replace('_', ' ').title()}

- **描述**: {category['description']}
- **测试数**: {category['total_tests']} (通过: {category['passed_tests']}, 失败: {category['failed_tests']})
- **成功率**: {category['success_rate']:.2%} ({category['grade']})
- **平均响应时间**: {category['average_response_time']:.3f}秒
- **平均相关性分数**: {category['average_relevance_score']:.3f}

"""

        if weak_areas:
            report += f"""---

## ⚠️ 薄弱环节

"""
            for area in weak_areas:
                report += f"""### {area['category'].replace('_', ' ').title()}

- **问题**: {area['issue']}
- **成功率**: {area['success_rate']:.2%}
- **优先级**: {area['priority']}
- **平均响应时间**: {area['average_response_time']:.3f}秒

"""

        if test_case_analysis['failed_cases']:
            report += f"""---

## ❌ 失败测试用例详情

共 {test_case_analysis['total_failed']} 个测试用例失败：

"""
            for i, case in enumerate(test_case_analysis['failed_cases'][:10], 1):  # 只显示前10个
                report += f"""### {i}. {case['test_id']} ({case['category']})

- **查询**: {case['query']}
- **缺失关键词**: {', '.join(case['missing_keywords'])}
- **响应时间**: {case['response_time']:.3f}秒
- **响应预览**: {case['response'][:100]}...

"""

            if test_case_analysis['total_failed'] > 10:
                report += f"*... 还有 {test_case_analysis['total_failed'] - 10} 个失败用例未显示*\n\n"

        if test_case_analysis['slow_cases']:
            report += f"""---

## 🐌 响应时间较慢的测试

共 {test_case_analysis['total_slow']} 个测试用例响应时间超过5秒：

"""
            for i, case in enumerate(test_case_analysis['slow_cases'][:10], 1):
                report += f"""### {i}. {case['test_id']} ({case['category']})

- **查询**: {case['query']}
- **响应时间**: {case['response_time']:.3f}秒

"""

            if test_case_analysis['total_slow'] > 10:
                report += f"*... 还有 {test_case_analysis['total_slow'] - 10} 个慢响应用例未显示*\n\n"

        if recommendations:
            report += f"""---

## 💡 改进建议

"""
            for i, rec in enumerate(recommendations, 1):
                report += f"""### {i}. {rec['category']} - {rec['issue']}

- **优先级**: {rec['priority']}
- **建议**: {rec['suggestion']}
- **预期改进**: {rec['expected_improvement']}

"""

        report += f"""---

## 📈 下一步行动

1. **立即行动** (高优先级):
   - 解决成功率低于60%的类别问题
   - 优化响应时间超过8秒的测试用例

2. **短期改进** (1-2周内):
   - 实施上述高优先级改进建议
   - 重新运行测评验证改进效果

3. **长期优化** (1个月内):
   - 持续监控关键指标
   - 根据用户反馈调整测试用例
   - 定期运行完整测评套件

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**分析工具版本**: 1.0
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ 分析报告已保存到: {output_file}")

    def generate_json_report(self, output_file: str):
        """生成 JSON 格式的分析报告"""
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "input_file": self.results_file,
                "analyzer_version": "1.0",
            },
            "summary": self.generate_summary(),
            "category_analysis": self.analyze_categories(),
            "weak_areas": self.identify_weak_areas(),
            "test_case_analysis": self.analyze_test_cases(),
            "recommendations": self.generate_recommendations(),
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"✅ JSON 分析报告已保存到: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Chatbot 测评结果分析工具")
    parser.add_argument(
        "--input",
        default="evaluation/evaluation_results.json",
        help="输入的测评结果文件 (默认: evaluation/evaluation_results.json)",
    )
    parser.add_argument(
        "--output",
        default="evaluation/analysis_report.md",
        help="输出的分析报告文件 (默认: evaluation/analysis_report.md)",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="输出格式 (默认: markdown)",
    )

    args = parser.parse_args()

    analyzer = ResultsAnalyzer(args.input)

    if args.format == "markdown":
        analyzer.generate_markdown_report(args.output)
    else:
        analyzer.generate_json_report(args.output)

    # 打印总结
    summary = analyzer.generate_summary()
    if summary:
        print("\n" + "=" * 60)
        print("📊 分析总结")
        print("=" * 60)
        print(f"总体成功率: {summary.get('overall_success_rate', 0):.2%}")
        print(f"综合评级: {summary.get('grade', 'N/A')}")
        print(f"平均响应时间: {summary.get('average_response_time', 0):.3f}秒")
        print("=" * 60)


if __name__ == "__main__":
    main()
