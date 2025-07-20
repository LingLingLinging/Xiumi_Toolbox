"""
简洁网页访问工具
只包含基础的网页访问功能
"""

import requests
from typing import Optional, Dict


class WebAccess:
    """简洁网页访问类"""
    
    def __init__(self):
        self.session = requests.Session()
        # 设置用户代理
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.timeout = 30
    
    def get(self, url: str, params: Dict = None) -> Optional[requests.Response]:
        """
        GET请求获取网页
        
        Args:
            url: 网页URL
            params: URL参数
            
        Returns:
            Response对象，失败返回None
        """
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            return response if response.status_code == 200 else None
        except:
            return None
    
    def post(self, url: str, data: Dict = None, json: Dict = None) -> Optional[requests.Response]:
        """
        POST请求发送数据
        
        Args:
            url: 网页URL
            data: 表单数据
            json: JSON数据
            
        Returns:
            Response对象，失败返回None
        """
        try:
            if json:
                response = self.session.post(url, json=json, timeout=self.timeout)
            else:
                response = self.session.post(url, data=data, timeout=self.timeout)
            return response if response.status_code in [200, 201] else None
        except:
            return None
    
    def get_text(self, url: str) -> str:
        """获取网页文本内容"""
        response = self.get(url)
        return response.text if response else ""
    
    def get_json(self, url: str) -> Dict:
        """获取JSON数据"""
        response = self.get(url)
        try:
            return response.json() if response else {}
        except:
            return {}


def main():
    """演示用法"""
    web = WebAccess()
    
    # 测试GET请求
    print("测试GET请求...")
    response = web.get("https://httpbin.org/get")
    if response:
        print(f"状态码: {response.status_code}")
        print(f"内容: {response.text[:200]}...")
    
    # 测试获取文本
    print("\n测试获取文本...")
    text = web.get_text("https://www.baidu.com")
    print(f"页面文本长度: {len(text)}")
    
    # 测试JSON API
    print("\n测试JSON API...")
    json_data = web.get_json("https://httpbin.org/json")
    print(f"JSON数据: {json_data}")


if __name__ == "__main__":
    main()
