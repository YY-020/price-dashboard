# -*- coding: utf-8 -*-
"""
LLM 客户端模块
统一 DeepSeek API 调用，被 organizer 和 translator 共用
"""

import requests
import json
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """DeepSeek API 统一客户端"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    def call(self, prompt, temperature=0.1):
        """调用 DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"LLM API 调用失败: {e}")
            return None
    
    def call_json(self, prompt, temperature=0.1):
        """调用 API 并解析 JSON 结果"""
        result = self.call(prompt, temperature)
        if not result:
            return None
        
        try:
            result = result.strip()
            if result.startswith('```'):
                result = result.split('\n', 1)[1]
                if result.endswith('```'):
                    result = result[:-3]
            
            return json.loads(result)
        except Exception as e:
            logger.error(f"JSON 解析失败: {e}")
            return None