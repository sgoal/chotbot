#!/usr/bin/env python3
"""
基金信息查询 MCP 工具
"""

import requests
from typing import Dict, Any, List
from chotbot.utils.config import Config

class FundTool:
    """
    基金信息查询工具类，用于获取基金基本信息和净值数据
    """
    
    def __init__(self):
        self.base_url = Config.FUND_API_BASE_URL
    
    def get_fund_basic_info(self, fund_code: str) -> Dict[str, Any]:
        """
        根据基金代码查询基金基本信息
        
        Args:
            fund_code (str): 基金代码
            
        Returns:
            Dict[str, Any]: 基金基本信息
        """
        try:
            # 查询基金基本信息
            url = f"{self.base_url}v1/fund/detail?fundCode={fund_code}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != 0:
                return {
                    "error": "基金信息查询失败",
                    "message": data.get("message", "未知错误")
                }
            
            fund_data = data.get("data", {})
            
            # 解析基金信息
            fund_info = {
                "基金代码": fund_data.get("fundCode", ""),
                "基金名称": fund_data.get("name", ""),
                "基金类型": fund_data.get("type", ""),
                "成立日期": fund_data.get("establishDate", ""),
                "最新净值日期": fund_data.get("netWorthDate", ""),
                "最新单位净值": fund_data.get("netWorth", ""),
                "日涨跌幅": fund_data.get("dayGrowth", ""),
                "近1月涨幅": fund_data.get("monthGrowth", ""),
                "近3月涨幅": fund_data.get("quarterGrowth", ""),
                "近6月涨幅": fund_data.get("halfYearGrowth", ""),
                "近1年涨幅": fund_data.get("yearGrowth", ""),
                "基金经理": fund_data.get("manager", ""),
                "基金公司": fund_data.get("company", "")
            }
            
            return fund_info
            
        except requests.RequestException as e:
            return {
                "error": f"基金信息查询失败: {str(e)}",
                "message": "请检查网络连接或基金代码是否正确"
            }
        except KeyError as e:
            return {
                "error": f"基金数据解析失败: {str(e)}",
                "message": "API响应格式可能已更改"
            }
    
    def get_fund_net_worth_history(self, fund_code: str, limit: int = 10) -> Dict[str, Any]:
        """
        查询基金净值历史数据
        
        Args:
            fund_code (str): 基金代码
            limit (int): 返回数据条数
            
        Returns:
            Dict[str, Any]: 基金净值历史数据
        """
        try:
            # 查询基金净值历史
            url = f"{self.base_url}v1/fund/nav?fundCode={fund_code}&pageIndex=1&pageSize={limit}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != 0:
                return {
                    "error": "基金净值查询失败",
                    "message": data.get("message", "未知错误")
                }
            
            net_worth_data = data.get("data", {})
            history_list = net_worth_data.get("list", [])
            
            # 解析历史数据
            history = []
            for item in history_list:
                history.append({
                    "日期": item.get("date", ""),
                    "单位净值": item.get("netWorth", ""),
                    "日涨跌幅": item.get("dayGrowth", "")
                })
            
            return {
                "基金代码": fund_code,
                "历史净值数据": history,
                "数据条数": len(history)
            }
            
        except requests.RequestException as e:
            return {
                "error": f"基金净值查询失败: {str(e)}",
                "message": "请检查网络连接或基金代码是否正确"
            }
        except KeyError as e:
            return {
                "error": f"基金净值数据解析失败: {str(e)}",
                "message": "API响应格式可能已更改"
            }
