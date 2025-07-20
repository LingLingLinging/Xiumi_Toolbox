"""
极简网页访问工具
获取整个页面源码保存到列表，支持Cookie
"""

import requests
import json
import os
import time
from datetime import datetime


def get_xiumi_cookies():
    """
    获取秀米Cookie的便捷方式
    """
    print("请选择Cookie输入方式:")
    print("1. 使用已知的秀米Cookie")
    print("2. 手动输入完整Cookie字符串")
    print("3. 不使用Cookie")
    
    choice = input("请选择 (1/2/3): ").strip()
    
    if choice == '1':
        # 使用您提供的最新Cookie信息
        xiumi_cookies = {
            '_ga': 'GA1.1.138683111.1741960991',
            '_ga_082SS7M4WJ': 'GS1.1.1742122869.2.1.1742127827.0.0.0',
            '_ga_MPF5T5D71D': 'GS2.1.s1753021340$o30$g1$t1753021341$j59$l0$h0',
            'sid': 's%3A9z_-F6Q4Z2hubkFfEXsC5JRHsqtL02Qc.DgmCQxcq5gEV3oIkcKp0xs3Rx0viEgGR4deSuNZf11Y'
        }
        print("✓ 使用最新的秀米Cookie")
        return xiumi_cookies
    
    elif choice == '2':
        cookie_str = input("请粘贴Cookie字符串: ").strip()
        if cookie_str:
            return cookie_str
        return None
    
    else:
        return None


def get_full_page_lines_with_cookies(url: str, cookies=None, wait_seconds=5) -> tuple:
    """
    获取整个页面的所有行，支持Cookie和等待时间
    
    Args:
        url: 网页URL
        cookies: Cookie字典或字符串
        wait_seconds: 等待秒数，让页面加载完成
        
    Returns:
        包含所有HTML行的列表和完整HTML内容
    """
    try:
        # 创建session
        session = requests.Session()
        
        # 设置headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edge/120.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Referer': 'https://xiumi.us/',
        })
        
        # 设置Cookie
        if cookies:
            if isinstance(cookies, dict):
                for name, value in cookies.items():
                    session.cookies.set(name, value, domain='xiumi.us')
            elif isinstance(cookies, str):
                # 解析Cookie字符串
                for cookie in cookies.split(';'):
                    if '=' in cookie:
                        name, value = cookie.strip().split('=', 1)
                        session.cookies.set(name, value, domain='xiumi.us')
        
        print(f"正在请求: {url}")
        if cookies:
            print("✓ 使用最新Cookie访问")
            print(f"✓ Cookie数量: {len(session.cookies)}")
        
        # 发起请求
        response = session.get(url, timeout=30)
        
        # 等待页面加载（对于动态内容）
        if wait_seconds > 0:
            print(f"等待 {wait_seconds} 秒让页面动态内容加载完成...")
            time.sleep(wait_seconds)
            
            # 可能需要再次请求获取动态加载的内容
            response = session.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"✓ 访问成功，状态码: {response.status_code}")
            print(f"✓ 响应大小: {len(response.text)} 字符")
            
            # 检查是否有登录状态
            if 'login' in response.text.lower() or '登录' in response.text:
                print("⚠️  页面可能包含登录相关内容")
            if 'user' in response.text.lower() or '用户' in response.text:
                print("✓ 页面可能包含用户相关内容")
                
            # 获取整个页面，按行分割成列表
            all_lines = response.text.splitlines()
            return all_lines, response.text  # 返回行列表和完整HTML
        else:
            return [f"错误：状态码 {response.status_code}"], None
            
    except Exception as e:
        return [f"错误：{e}"], None


def save_html_file(html_content: str, url: str, save_dir: str = "saved_pages"):
    """
    保存HTML内容到文件（原样保存）
    
    Args:
        html_content: HTML内容
        url: 原始URL
        save_dir: 保存目录
        
    Returns:
        保存的文件路径
    """
    try:
        # 创建保存目录
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_url = url.replace('://', '_').replace('/', '_').replace('?', '_').replace('#', '_')[:30]
        filename = f"xiumi_page_{timestamp}_{safe_url}.html"
        filepath = os.path.join(save_dir, filename)
        
        # 原样保存HTML文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ HTML文件已保存: {filepath}")
        print(f"✓ 文件大小: {len(html_content)} 字符")
        return filepath
        
    except Exception as e:
        print(f"保存HTML文件失败: {e}")
        return None


def save_search_results(search_results: list, search_term: str, save_dir: str = "saved_pages"):
    """
    保存搜索结果到HTML文件
    
    Args:
        search_results: 搜索结果列表 [(行号, 内容), ...]
        search_term: 搜索关键词
        save_dir: 保存目录
    """
    try:
        if not search_results:
            return
            
        # 创建保存目录
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_term = search_term.replace(' ', '_').replace('/', '_')[:20]
        filename = f"search_results_{safe_term}_{timestamp}.html"
        filepath = os.path.join(save_dir, filename)
        
        # 生成HTML内容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>搜索结果 - {search_term}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #007acc; color: white; padding: 20px; margin-bottom: 20px; border-radius: 5px; }}
        .result {{ margin: 10px 0; padding: 15px; border-left: 4px solid #007acc; background: white; border-radius: 3px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .line-num {{ color: #666; font-weight: bold; font-size: 12px; }}
        .highlight {{ background: #ffeb3b; padding: 2px 4px; border-radius: 2px; }}
        .content {{ margin-top: 8px; font-family: monospace; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🔍 搜索结果</h2>
        <p><strong>搜索关键词:</strong> {search_term}</p>
        <p><strong>找到结果:</strong> {len(search_results)} 个</p>
        <p><strong>生成时间:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
"""
        
        for line_num, content in search_results:
            # 高亮显示搜索关键词（大小写不敏感）
            import re
            highlighted_content = re.sub(
                f'({re.escape(search_term)})', 
                r'<span class="highlight">\1</span>', 
                content, 
                flags=re.IGNORECASE
            )
            html_content += f"""
    <div class="result">
        <div class="line-num">第 {line_num} 行</div>
        <div class="content">{highlighted_content}</div>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ 搜索结果已保存: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"保存搜索结果失败: {e}")
        return None


def search_in_page(page_lines: list, search_term: str):
    """在页面中搜索关键词"""
    matches = []
    for line_num, line in enumerate(page_lines, 1):
        if search_term.lower() in line.lower():
            matches.append((line_num, line.strip()))
    
    if matches:
        print(f"\n🎯 找到 {len(matches)} 个匹配结果:")
        for line_num, content in matches[:10]:  # 只显示前10个
            # 截断过长的内容
            display_content = content[:200] + "..." if len(content) > 200 else content
            print(f"第{line_num}行: {display_content}")
        if len(matches) > 10:
            print(f"... 还有 {len(matches) - 10} 个结果")
            
        # 询问是否保存搜索结果
        save_choice = input("\n是否保存搜索结果到HTML文件? (y/n): ").strip().lower()
        if save_choice == 'y':
            save_search_results(matches, search_term)
            
    else:
        print(f"❌ 没有找到包含'{search_term}'的行")
    
    return matches


def main():
    """主函数"""
    print("=" * 60)
    print("🌟 秀米网页访问工具 (已更新Cookie)")
    print("=" * 60)
    
    # 获取Cookie
    cookies = get_xiumi_cookies()
    
    # 输入URL
    url = input("\n请输入秀米网页URL: ").strip()
    if not url:
        return
    
    # 设置等待时间
    wait_time = input("\n请输入等待时间(秒，默认5秒): ").strip()
    try:
        wait_seconds = int(wait_time) if wait_time else 5
    except ValueError:
        wait_seconds = 5
        
    print(f"\n🚀 正在获取整个页面: {url}")
    print(f"⏱️  将等待 {wait_seconds} 秒让页面完全加载")
    
    # 获取整个页面保存到 page_lines 列表中
    result = get_full_page_lines_with_cookies(url, cookies, wait_seconds)
    if len(result) == 2:
        page_lines, full_html = result
    else:
        page_lines, full_html = result, None
    
    if page_lines and page_lines[0].startswith("错误："):
        print(f"❌ {page_lines[0]}")
        return
    
    print(f"✅ 页面获取完成，共 {len(page_lines)} 行")
    
    # 询问是否保存完整HTML
    if full_html:
        save_choice = input("\n💾 是否保存完整页面到HTML文件? (y/n): ").strip().lower()
        if save_choice == 'y':
            saved_file = save_html_file(full_html, url)
            if saved_file:
                print(f"📂 可以用浏览器打开查看: {os.path.abspath(saved_file)}")
    
    # 显示前3行内容预览
    print("\n📄 前3行内容预览:")
    for i, line in enumerate(page_lines[:3], 1):
        display_line = line[:100] + "..." if len(line) > 100 else line
        print(f"第{i}行: {display_line}")
    
    # 循环搜索
    print("\n🔍 开始搜索模式 (输入关键词进行搜索)")
    while True:
        search_term = input("\n请输入搜索关键词 (输入'quit'退出): ").strip()
        if search_term.lower() == 'quit':
            print("👋 程序结束")
            break
        if search_term:
            search_in_page(page_lines, search_term)


if __name__ == "__main__":
    main()
