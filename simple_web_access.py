"""
简单网页访问工具
使用requests库进行基础的网页访问和内容获取
"""

import requests
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class SimpleWebAccess:
    """简单网页访问类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """设置会话参数"""
        # 设置用户代理
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 设置超时
        self.timeout = 30
    
    def get_page(self, url: str, params: Dict = None) -> Optional[requests.Response]:
        """
        获取网页内容
        
        Args:
            url: 网页URL
            params: URL参数
            
        Returns:
            Response对象，如果失败返回None
        """
        try:
            print(f"正在访问: {url}")
            
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # 检查响应状态
            if response.status_code == 200:
                print(f"✓ 访问成功 (状态码: {response.status_code})")
                return response
            else:
                print(f"✗ 访问失败 (状态码: {response.status_code})")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"✗ 请求异常: {e}")
            return None
    
    def post_data(self, url: str, data: Dict = None, json_data: Dict = None) -> Optional[requests.Response]:
        """
        POST数据到网页
        
        Args:
            url: 网页URL
            data: 表单数据
            json_data: JSON数据
            
        Returns:
            Response对象，如果失败返回None
        """
        try:
            print(f"正在POST到: {url}")
            
            if json_data:
                response = self.session.post(
                    url, 
                    json=json_data, 
                    timeout=self.timeout
                )
            else:
                response = self.session.post(
                    url, 
                    data=data, 
                    timeout=self.timeout
                )
            
            if response.status_code in [200, 201]:
                print(f"✓ POST成功 (状态码: {response.status_code})")
                return response
            else:
                print(f"✗ POST失败 (状态码: {response.status_code})")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"✗ POST异常: {e}")
            return None
    
    def parse_html(self, response: requests.Response) -> Optional[BeautifulSoup]:
        """
        解析HTML内容
        
        Args:
            response: requests响应对象
            
        Returns:
            BeautifulSoup对象，如果失败返回None
        """
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except Exception as e:
            print(f"✗ HTML解析失败: {e}")
            return None
    
    def extract_links(self, soup: BeautifulSoup, base_url: str = None) -> list:
        """
        提取页面中的所有链接
        
        Args:
            soup: BeautifulSoup对象
            base_url: 基础URL，用于处理相对链接
            
        Returns:
            链接列表
        """
        links = []
        try:
            for link in soup.find_all('a', href=True):
                href = link['href']
                if base_url:
                    href = urljoin(base_url, href)
                
                links.append({
                    'text': link.text.strip(),
                    'url': href,
                    'title': link.get('title', '')
                })
            
            print(f"✓ 找到 {len(links)} 个链接")
            return links
            
        except Exception as e:
            print(f"✗ 提取链接失败: {e}")
            return []
    
    def extract_text(self, soup: BeautifulSoup) -> str:
        """
        提取页面中的纯文本
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            纯文本内容
        """
        try:
            # 移除script和style标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 获取文本
            text = soup.get_text()
            
            # 清理文本
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            print(f"✗ 提取文本失败: {e}")
            return ""
    
    def save_to_file(self, content: Any, filename: str, content_type: str = "text") -> bool:
        """
        保存内容到文件
        
        Args:
            content: 要保存的内容
            filename: 文件名
            content_type: 内容类型 ("text", "json", "html")
            
        Returns:
            是否保存成功
        """
        try:
            if content_type == "json":
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(content, f, ensure_ascii=False, indent=2)
            elif content_type == "html":
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(str(content))
            else:  # text
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(str(content))
            
            print(f"✓ 内容已保存到: {filename}")
            return True
            
        except Exception as e:
            print(f"✗ 保存文件失败: {e}")
            return False
    
    def download_file(self, url: str, filename: str = None) -> bool:
        """
        下载文件
        
        Args:
            url: 文件URL
            filename: 保存的文件名，如果为None则从URL自动生成
            
        Returns:
            是否下载成功
        """
        try:
            if not filename:
                filename = url.split('/')[-1] or 'downloaded_file'
            
            print(f"正在下载: {url}")
            
            response = self.session.get(url, stream=True, timeout=self.timeout)
            
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✓ 文件下载成功: {filename}")
                return True
            else:
                print(f"✗ 下载失败 (状态码: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"✗ 下载异常: {e}")
            return False
    
    def get_page_info(self, url: str) -> Dict[str, Any]:
        """
        获取页面基本信息
        
        Args:
            url: 网页URL
            
        Returns:
            页面信息字典
        """
        info = {
            'url': url,
            'title': '',
            'description': '',
            'keywords': '',
            'links_count': 0,
            'images_count': 0,
            'text_length': 0,
            'status_code': None,
            'content_type': '',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            response = self.get_page(url)
            if not response:
                return info
            
            info['status_code'] = response.status_code
            info['content_type'] = response.headers.get('content-type', '')
            
            soup = self.parse_html(response)
            if not soup:
                return info
            
            # 提取标题
            title_tag = soup.find('title')
            if title_tag:
                info['title'] = title_tag.text.strip()
            
            # 提取描述
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag:
                info['description'] = desc_tag.get('content', '')
            
            # 提取关键词
            keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            if keywords_tag:
                info['keywords'] = keywords_tag.get('content', '')
            
            # 统计链接数量
            links = soup.find_all('a', href=True)
            info['links_count'] = len(links)
            
            # 统计图片数量
            images = soup.find_all('img')
            info['images_count'] = len(images)
            
            # 提取文本长度
            text = self.extract_text(soup)
            info['text_length'] = len(text)
            
            return info
            
        except Exception as e:
            print(f"✗ 获取页面信息失败: {e}")
            return info


def demo_usage():
    """演示用法"""
    print("=" * 60)
    print("简单网页访问工具演示")
    print("=" * 60)
    
    # 创建访问器实例
    web_access = SimpleWebAccess()
    
    # 示例网站
    test_urls = [
        "https://httpbin.org/get",  # 测试GET请求
        "https://www.baidu.com",    # 百度首页
        "https://httpbin.org/headers",  # 查看请求头
    ]
    
    for url in test_urls:
        print(f"\n{'='*40}")
        print(f"测试URL: {url}")
        print('='*40)
        
        # 获取页面信息
        info = web_access.get_page_info(url)
        print(f"页面标题: {info['title']}")
        print(f"状态码: {info['status_code']}")
        print(f"内容类型: {info['content_type']}")
        print(f"链接数量: {info['links_count']}")
        print(f"图片数量: {info['images_count']}")
        print(f"文本长度: {info['text_length']}")
        
        # 保存页面信息
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"page_info_{timestamp}.json"
        web_access.save_to_file(info, filename, "json")
        
        time.sleep(1)  # 避免请求过于频繁


def interactive_mode():
    """交互模式"""
    print("=" * 60)
    print("交互式网页访问模式")
    print("=" * 60)
    
    web_access = SimpleWebAccess()
    
    while True:
        print("\n请选择操作:")
        print("1. 访问网页")
        print("2. 下载文件")
        print("3. 获取页面信息")
        print("4. 提取链接")
        print("5. 退出")
        
        choice = input("请输入选择 (1-5): ").strip()
        
        if choice == '1':
            url = input("请输入网页URL: ").strip()
            if url:
                response = web_access.get_page(url)
                if response:
                    print(f"页面内容长度: {len(response.text)} 字符")
                    
                    save = input("是否保存页面内容？(y/n): ").strip().lower()
                    if save in ['y', 'yes']:
                        filename = input("请输入文件名 (默认: page.html): ").strip()
                        if not filename:
                            filename = "page.html"
                        web_access.save_to_file(response.text, filename, "html")
        
        elif choice == '2':
            url = input("请输入文件URL: ").strip()
            if url:
                filename = input("请输入保存文件名 (留空自动生成): ").strip()
                filename = filename if filename else None
                web_access.download_file(url, filename)
        
        elif choice == '3':
            url = input("请输入网页URL: ").strip()
            if url:
                info = web_access.get_page_info(url)
                print(f"\n页面信息:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
        
        elif choice == '4':
            url = input("请输入网页URL: ").strip()
            if url:
                response = web_access.get_page(url)
                if response:
                    soup = web_access.parse_html(response)
                    if soup:
                        links = web_access.extract_links(soup, url)
                        print(f"\n找到 {len(links)} 个链接:")
                        for i, link in enumerate(links[:10], 1):  # 只显示前10个
                            print(f"  {i}. {link['text']} -> {link['url']}")
                        
                        if len(links) > 10:
                            print(f"  ... 还有 {len(links) - 10} 个链接")
        
        elif choice == '5':
            print("退出程序")
            break
        
        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    print("=" * 60)
    print("简单网页访问工具")
    print("=" * 60)
    
    while True:
        print("\n请选择模式:")
        print("1. 演示模式")
        print("2. 交互模式")
        print("3. 退出")
        
        mode = input("请输入选择 (1-3): ").strip()
        
        if mode == '1':
            demo_usage()
        elif mode == '2':
            interactive_mode()
        elif mode == '3':
            print("程序结束")
            break
        else:
            print("无效选择，请重新输入")
