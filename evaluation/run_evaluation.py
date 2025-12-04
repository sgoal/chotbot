#!/usr/bin/env python3
"""
Chatbot 自动化测评脚本

使用方法:
    python evaluation/run_evaluation.py [--api-url API_URL] [--output OUTPUT_FILE]

参数:
    --api-url: API 地址 (默认: http://localhost:5001)
    --output: 输出结果文件 (默认: evaluation_results.json)
    --categories: 指定测试类别 (逗号分隔, 默认: 全部)
"""

import json
import time
import argparse
import requests
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import sys


@dataclass
class TestResult:
    """单个测试结果"""
    test_id: str
    query: str
    response: str
    response_time: float
    success: bool
    relevance_score: float
    accuracy_score: float
    clarity_score: float
    expected_keywords_found: List[str]
    missing_keywords: List[str]
    error_message: str = ""


@dataclass
class CategoryResult:
    """类别测试结果"""
    category: str
    description: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    average_response_time: float
    average_relevance_score: float
    test_results: List[TestResult]


@dataclass
class EvaluationReport:
    """完整测评报告"""
    timestamp: str
    api_url: str
    total_tests: int
    total_passed: int
    total_failed: int
    overall_success_rate: float
    average_response_time: float
    category_results: List[CategoryResult]


class ChatbotEvaluator:
    """Chatbot 测评器"""

    def __init__(self, api_url: str = "http://localhost:5001"):
        self.api_url = api_url.rstrip("/")
        self.test_cases = self._load_test_cases()
        self.session = requests.Session()

    def _load_test_cases(self) -> Dict[str, Any]:
        """加载测试用例"""
        try:
            with open("evaluation/test_cases.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("错误: 找不到 test_cases.json 文件", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"错误: test_cases.json 格式错误: {e}", file=sys.stderr)
            sys.exit(1)

    def _send_query(self, query: str) -> tuple[str, float]:
        """发送查询到 chatbot"""
        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.api_url}/chat",
                json={"message": query},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            response_time = time.time() - start_time
            return result.get("response", ""), response_time
        except requests.RequestException as e:
            response_time = time.time() - start_time
            return f"错误: {str(e)}", response_time

    def _calculate_relevance_score(self, response: str, expected_keywords: List[str]) -> tuple[float, List[str], List[str]]:
        """计算相关性分数"""
        if not expected_keywords:
            return 1.0, [], []

        response_lower = response.lower()
        found_keywords = []
        missing_keywords = []

        for keyword in expected_keywords:
            if keyword.lower() in response_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        relevance_score = len(found_keywords) / len(expected_keywords)
        return relevance_score, found_keywords, missing_keywords

    def _calculate_accuracy_score(self, response: str, query: str) -> float:
        """计算准确性分数（简化版）"""
        # 这里可以实现更复杂的准确性检查
        # 例如：事实核查、逻辑一致性检查等
        if len(response.strip()) > 10:
            return 0.8
        return 0.3

    def _calculate_clarity_score(self, response: str) -> float:
        """计算清晰度分数"""
        if not response:
            return 0.0

        # 检查是否有清晰的结构
        has_structure = any(marker in response for marker in ["\n", "1.", "-", "•"])

        # 检查长度是否适中
        length_score = min(len(response) / 200, 1.0)

        clarity_score = 0.6 + (0.4 if has_structure else 0.0)
        clarity_score = min(clarity_score + length_score * 0.2, 1.0)

        return clarity_score

    def _run_single_test(self, test_case: Dict[str, Any]) -> TestResult:
        """运行单个测试"""
        test_id = test_case["id"]
        query = test_case["query"]
        expected_keywords = test_case.get("expected_keywords", [])

        print(f"  运行测试 {test_id}: {query[:50]}...")

        try:
            response, response_time = self._send_query(query)

            relevance_score, found_keywords, missing_keywords = self._calculate_relevance_score(
                response, expected_keywords
            )
            accuracy_score = self._calculate_accuracy_score(response, query)
            clarity_score = self._calculate_clarity_score(response)

            # 判断测试是否通过
            success = relevance_score >= 0.5 and accuracy_score >= 0.5

            return TestResult(
                test_id=test_id,
                query=query,
                response=response,
                response_time=response_time,
                success=success,
                relevance_score=relevance_score,
                accuracy_score=accuracy_score,
                clarity_score=clarity_score,
                expected_keywords_found=found_keywords,
                missing_keywords=missing_keywords
            )

        except Exception as e:
            return TestResult(
                test_id=test_id,
                query=query,
                response="",
                response_time=0.0,
                success=False,
                relevance_score=0.0,
                accuracy_score=0.0,
                clarity_score=0.0,
                expected_keywords_found=[],
                missing_keywords=expected_keywords,
                error_message=str(e)
            )

    def _run_category_tests(self, category_name: str, category_data: Dict[str, Any]) -> CategoryResult:
        """运行单个类别的测试"""
        print(f"\n📋 运行测试类别: {category_name} - {category_data['description']}")

        test_cases = category_data["test_cases"]
        test_results = []

        for test_case in test_cases:
            result = self._run_single_test(test_case)
            test_results.append(result)
            time.sleep(0.5)  # 避免请求过快

        # 计算类别统计
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.success)
        failed_tests = total_tests - passed_tests

        avg_response_time = sum(r.response_time for r in test_results) / total_tests
        avg_relevance_score = sum(r.relevance_score for r in test_results) / total_tests

        return CategoryResult(
            category=category_name,
            description=category_data["description"],
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            average_response_time=avg_response_time,
            average_relevance_score=avg_relevance_score,
            test_results=test_results
        )

    def run_evaluation(self, categories: List[str] = None) -> EvaluationReport:
        """运行完整测评"""
        print("🚀 开始 Chatbot 自动化测评")
        print(f"📡 API 地址: {self.api_url}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 检查 API 是否可用
        try:
            health_check = self.session.get(f"{self.api_url}/", timeout=5)
            if health_check.status_code != 200:
                print(f"⚠️  警告: API 健康检查返回状态码 {health_check.status_code}")
        except requests.RequestException:
            print("⚠️  警告: 无法连接到 API，测评可能失败")

        category_results = []
        test_categories = self.test_cases["test_categories"]

        # 如果指定了类别，只运行这些类别
        if categories:
            test_categories = {k: v for k, v in test_categories.items() if k in categories}

        total_start_time = time.time()

        for category_name, category_data in test_categories.items():
            if category_data.get("priority") == "low":
                print(f"\n⏭️  跳过低优先级类别: {category_name}")
                continue

            category_result = self._run_category_tests(category_name, category_data)
            category_results.append(category_result)

        total_time = time.time() - total_start_time

        # 计算总体统计
        total_tests = sum(cr.total_tests for cr in category_results)
        total_passed = sum(cr.passed_tests for cr in category_results)
        total_failed = sum(cr.failed_tests for cr in category_results)
        overall_success_rate = total_passed / total_tests if total_tests > 0 else 0

        avg_response_time = sum(
            cr.average_response_time * cr.total_tests for cr in category_results
        ) / total_tests if total_tests > 0 else 0
        print(f"\n✅ 测评完成！总用时: {total_time:.2f} 秒")

        return EvaluationReport(
            timestamp=datetime.now().isoformat(),
            api_url=self.api_url,
            total_tests=total_tests,
            total_passed=total_passed,
            total_failed=total_failed,
            overall_success_rate=overall_success_rate,
            average_response_time=avg_response_time,
            category_results=category_results
        )

    def save_report(self, report: EvaluationReport, output_file: str):
        """保存测评报告"""
        # 将 dataclass 转换为 dict
        report_dict = asdict(report)

        # 保存为 JSON
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        print(f"\n💾 测评报告已保存到: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Chatbot 自动化测评工具")
    parser.add_argument(
        "--api-url",
        default="http://localhost:5001",
        help="API 地址 (默认: http://localhost:5001)"
    )
    parser.add_argument(
        "--output",
        default="evaluation/evaluation_results.json",
        help="输出结果文件 (默认: evaluation/evaluation_results.json)"
    )
    parser.add_argument(
        "--categories",
        help="指定测试类别 (逗号分隔, 如: basic_conversation,knowledge_qa)"
    )

    args = parser.parse_args()

    # 解析类别列表
    categories = None
    if args.categories:
        categories = [cat.strip() for cat in args.categories.split(",")]

    # 运行测评
    evaluator = ChatbotEvaluator(api_url=args.api_url)
    report = evaluator.run_evaluation(categories=categories)

    # 保存报告
    evaluator.save_report(report, args.output)

    # 打印总结
    print("\n" + "=" * 60)
    print("📊 测评总结")
    print("=" * 60)
    print(f"总测试数: {report.total_tests}")
    print(f"通过数: {report.total_passed}")
    print(f"失败数: {report.total_failed}")
    print(f"成功率: {report.overall_success_rate:.2%}")
    print(f"平均响应时间: {report.average_response_time:.3f} 秒")
    print("=" * 60)

    # 按类别显示结果
    print("\n📋 按类别统计:")
    for cr in report.category_results:
        success_rate = cr.passed_tests / cr.total_tests if cr.total_tests > 0 else 0
        print(f"  {cr.category}: {cr.passed_tests}/{cr.total_tests} ({success_rate:.1%}) - 平均响应: {cr.average_response_time:.3f}s")


if __name__ == "__main__":
    main()
