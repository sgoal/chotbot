#!/usr/bin/env python3
"""
意图识别模块 - 支持意图识别与槽位提取
"""

import os
import json
import re
from typing import Dict, List, Tuple
import nltk

# 确保nltk资源已下载
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class IntentRecognizer:
    """
    意图识别类，支持意图识别和槽位提取
    """

    def __init__(self, config_path: str = None):
        """
        初始化意图识别模块
        Args:
            config_path: 意图配置文件路径
        """
        self.config = self._load_config(config_path)
        self.intents = self.config.get('intents', [])

        # 预编译正则表达式
        self._precompile_patterns()

        # 初始化NLTK分词器
        self.tokenizer = nltk.RegexpTokenizer(r'\w+')

    def _load_config(self, config_path: str = None) -> Dict:
        """
        加载意图配置文件
        Args:
            config_path: 配置文件路径
        Returns:
            配置字典
        """
        default_config = {
            "intents": []
        }

        if not config_path:
            return default_config

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件 {config_path} 不存在")

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _precompile_patterns(self) -> None:
        """
        预编译意图识别的正则表达式
        """
        self.patterns = []
        for intent in self.intents:
            for example in intent.get('examples', []):
                # 直接使用原始示例进行关键词匹配
                # 对于槽位提取，我们将在匹配后单独处理
                self.patterns.append({
                    'intent': intent['name'],
                    'example': example,
                    'pattern': example,
                    'slots': intent.get('slots', [])
                })

    def recognize(self, user_input: str) -> Dict:
        """
        识别用户输入的意图和槽位
        Args:
            user_input: 用户输入文本
        Returns:
            识别结果，包含intent和slots
        """
        # 预处理用户输入
        input_clean = user_input.strip()

        # 首先尝试基于关键词的意图识别
        intent_scores = []
        for intent in self.intents:
            score = self._calculate_keyword_score(input_clean, intent)
            if score > 0:
                intent_scores.append((intent['name'], score))

        if intent_scores:
            # 选择得分最高的意图
            best_intent_info = sorted(intent_scores, key=lambda x: x[1], reverse=True)[0]
            best_intent_name = best_intent_info[0]
            best_intent = [intent for intent in self.intents if intent['name'] == best_intent_name][0]
            
            # 提取槽位信息
            slots = self._extract_slots(input_clean, best_intent)
            
            return {
                'intent': best_intent_name,
                'slots': slots,
                'confidence': best_intent_info[1] / 100.0
            }

        # 如果没有识别到任何意图，返回默认结果
        return {
            'intent': '闲聊',
            'slots': {},
            'confidence': 0.5
        }

    def _calculate_keyword_score(self, input_text: str, intent: Dict) -> int:
        """
        基于关键词计算意图得分
        Args:
            input_text: 用户输入文本
            intent: 意图信息
        Returns:
            得分
        """
        # 简单的关键词匹配得分
        keywords = []
        # 从示例中提取关键词
        for example in intent.get('examples', []):
            keywords.extend(self.tokenizer.tokenize(example))
        # 从槽位示例中提取关键词
        for slot in intent.get('slots', []):
            keywords.extend(slot.get('examples', []))

        # 去重
        keywords = list(set(keywords))
        # 计算匹配的关键词数量
        match_count = 0
        for keyword in keywords:
            if keyword in input_text:
                match_count += 1

        return (match_count / len(keywords)) * 100 if keywords else 0

    def _extract_slots(self, input_text: str, intent: Dict) -> Dict:
        """
        提取槽位信息
        Args:
            input_text: 用户输入文本
            intent: 意图信息
        Returns:
            槽位信息
        """
        slots = {}
        for slot in intent.get('slots', []):
            slot_name = slot['name']
            slot_type = slot['type']

            # 根据槽位类型使用不同的提取方法
            if slot_type == 'date':
                # 日期正则表达式
                date_patterns = r'(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|今天|明天|后天|大后天|本周|下周|本月|下月|今年|明年|未来[1-3]天)'
                match = re.search(date_patterns, input_text)
                if match:
                    slots[slot_name] = match.group()

            elif slot_type == 'city':
                # 城市提取，使用内置的城市列表
                cities = ['北京', '上海', '广州', '深圳', '成都', '杭州', '重庆', '西安', '武汉', '天津']
                for city in cities:
                    if city in input_text:
                        slots[slot_name] = city
                        break

            elif slot_type == 'stock_symbol':
                # 股票代码提取
                stock_symbols = ['茅台', '腾讯', '阿里巴巴', '百度', '京东', '美团']
                for symbol in stock_symbols:
                    if symbol in input_text:
                        slots[slot_name] = symbol
                        break

            elif slot_type == 'time':
                # 时间提取
                time_patterns = r'((上午|下午|晚上)?\d{1,2}:\d{2}|明天上午|明天下午|后天下午)'
                match = re.search(time_patterns, input_text)
                if match:
                    slots[slot_name] = match.group()

            elif slot_type == 'string':
                # 通用字符串提取，使用槽位示例
                examples = slot.get('examples', [])
                for example in examples:
                    if example in input_text:
                        slots[slot_name] = example
                        break

            elif slot_type == 'number':
                # 数字提取
                number_patterns = r'(\d+(\.\d+)?)'
                match = re.search(number_patterns, input_text)
                if match:
                    slots[slot_name] = match.group()

        return slots

    def add_intent(self, intent_name: str, examples: List[str], slots: List[Dict] = None) -> None:
        """
        添加新意图
        Args:
            intent_name: 意图名称
            examples: 意图示例
            slots: 槽位信息
        """
        new_intent = {
            'name': intent_name,
            'examples': examples,
            'slots': slots or []
        }
        self.intents.append(new_intent)
        self._precompile_patterns()  # 重新编译模式

    def save_config(self, config_path: str) -> None:
        """
        保存配置文件
        Args:
            config_path: 配置文件路径
        """
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
