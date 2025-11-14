#!/usr/bin/env python3
"""
天气查询 MCP 工具
"""

import requests
from typing import Dict, Any
from chotbot.utils.config import Config

class WeatherTool:
    """
    天气查询工具类，用于获取实时天气信息
    """
    
    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.base_url = Config.WEATHER_API_BASE_URL
        self.language = Config.WEATHER_API_LANGUAGE
        
        # 城市代码映射（部分常见城市）
        self.city_code_map = {
            "北京": "1792947",
            "上海": "1793045",
            "广州": "1807846",
            "深圳": "1809858",
            "成都": "1784559",
            "杭州": "1791247",
            "重庆": "1791330",
            "西安": "1787559",
            "武汉": "1789558",
            "天津": "1792438"
        }
    
    def get_weather_by_city(self, city: str) -> Dict[str, Any]:
        """
        根据城市名称查询天气
        
        Args:
            city (str): 城市名称
            
        Returns:
            Dict[str, Any]: 天气信息
        """
        if not self.api_key:
            return {
                "error": "请先在配置文件中设置WEATHER_API_KEY",
                "message": "需要注册OpenWeatherMap账号获取免费API Key"
            }
            
        # 获取城市代码
        city_code = self.city_code_map.get(city)
        if not city_code:
            # 如果没有预定义的城市代码，使用城市名称查询
            params = {
                "q": city,
                "appid": self.api_key,
                "lang": self.language,
                "units": "metric"  # 使用摄氏度
            }
        else:
            # 使用城市代码查询
            params = {
                "id": city_code,
                "appid": self.api_key,
                "lang": self.language,
                "units": "metric"  # 使用摄氏度
            }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # 检查请求是否成功
            
            data = response.json()
            
            # 解析天气信息
            weather_info = {
                "城市": data.get("name", ""),
                "温度": f"{data['main']['temp']}°C",
                "湿度": f"{data['main']['humidity']}%",
                "天气状况": data["weather"][0]["description"],
                "风速": f"{data['wind']['speed']} m/s",
                "气压": f"{data['main']['pressure']} hPa"
            }
            
            return weather_info
            
        except requests.RequestException as e:
            return {
                "error": f"天气查询失败: {str(e)}",
                "message": "请检查网络连接或城市名称是否正确"
            }
        except KeyError as e:
            return {
                "error": f"天气数据解析失败: {str(e)}",
                "message": "API响应格式可能已更改"
            }
