#!/usr/bin/env python3
"""
测试意图识别模块
"""

import sys
import os
import json

# 添加项目路径
sys.path.insert(0, 'src')

from chotbot.intent.intent_recognizer import IntentRecognizer

# 创建一个简单的意图配置
config = {
    "intents": [
        {
            "name": "查询天气",
            "examples": [
                "今天北京的天气怎么样？",
                "上海明天会下雨吗？",
                "广州未来三天的温度是多少？"
            ],
            "slots": [
                {
                    "name": "城市",
                    "type": "string",
                    "examples": ["北京", "上海", "广州"]
                },
                {
                    "name": "日期",
                    "type": "date",
                    "examples": ["今天", "明天", "未来三天"]
                }
            ]
        },
        {
            "name": "查询股票",
            "examples": [
                "茅台的股价是多少？",
                "腾讯今天的行情如何？",
                "阿里巴巴的股票代码是什么？"
            ],
            "slots": [
                {
                    "name": "股票代码",
                    "type": "string",
                    "examples": ["茅台", "腾讯", "阿里巴巴"]
                }
            ]
        }
    ]
}

# 保存配置文件
config_path = 'intent_config.json'
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

# 初始化意图识别器
recognizer = IntentRecognizer(config_path)

# 测试意图识别
test_inputs = [
    "今天北京的天气怎么样？",
    "腾讯今天的行情如何？",
    "广州未来三天的温度是多少？",
    "阿里巴巴的股票代码是什么？",
    "你好啊，今天天气真不错！",
    "明天上海会下雨吗？"
]

for input_text in test_inputs:
    result = recognizer.recognize(input_text)
    print(f"输入: {input_text}")
    print(f"意图: {result['intent']}")
    print(f"槽位: {result['slots']}")
    print(f"置信度: {result['confidence']:.2f}")
    print("-" * 50)

# 测试添加新意图
print("测试添加新意图：")
recognizer.add_intent(
    "设置提醒",
    ["明天早上8点提醒我开会", "下午3点提醒我买咖啡"],
    [
        {
            "name": "时间",
            "type": "time",
            "examples": ["明天早上8点", "下午3点"]
        },
        {
            "name": "内容",
            "type": "string",
            "examples": ["开会", "买咖啡"]
        }
    ]
)

# 测试新添加的意图
new_test_inputs = [
    "明天早上8点提醒我开会",
    "下午3点提醒我买咖啡"
]

for input_text in new_test_inputs:
    result = recognizer.recognize(input_text)
    print(f"输入: {input_text}")
    print(f"意图: {result['intent']}")
    print(f"槽位: {result['slots']}")
    print(f"置信度: {result['confidence']:.2f}")
    print("-" * 50)

# 清理配置文件
os.remove(config_path)
print("✅ 意图识别模块测试完成！")
