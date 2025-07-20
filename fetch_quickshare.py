"""
Automatically Fetch the Quick Save Code of a Specific Post in Xiumi Editor

This script automates the process of obtaining the quick save code for a specific post in the Xiumi Editor. By entering the unique identifier or link of the post, the script will automatically access the Xiumi Editor, parse, and extract the corresponding quick save code, making it convenient for subsequent content backup and management. It is suitable for scenarios where batch or regular saving of Xiumi posts is required, improving work efficiency.
"""

import time
import json
import os
from datetime import datetime
from typing import Optional, Dict, List
from urllib.parse import urlparse, parse_qs

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    from bs4 import BeautifulSoup
    import requests
except ImportError as e:
    print(f"缺少必要的依赖包: {e}")
    print("请运行: pip install selenium webdriver-manager beautifulsoup4 requests")
    exit(1)


class XiumiQuickShareFetcher:
    """秀米编辑器另存码获取器"""
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.xiumi_base_url = "https://xiumi.us"
        self.login_url = f"{self.xiumi_base_url}/#/login"
        self.editor_url = f"{self.xiumi_base_url}/#/editor"
        self.browser_type = "chrome"  # 默认浏览器类型
    
    def detect_browser_paths(self) -> Dict[str, str]:
        """检测浏览器安装路径"""
        browser_paths = {}
        
        # Edge浏览器常见路径
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Users\{}\AppData\Local\Microsoft\Edge\Application\msedge.exe".format(os.environ.get('USERNAME', '')),
        ]
        
        for path in edge_paths:
            if os.path.exists(path):
                browser_paths['edge'] = path
                break
        
        # Chrome浏览器常见路径
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.environ.get('USERNAME', '')),
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                browser_paths['chrome'] = path
                break
        
        return browser_paths
    
    def start_browser_with_debug(self, browser: str = "edge", browser_path: str = None) -> bool:
        """启动带有调试端口的浏览器"""
        try:
            import subprocess
            
            if not browser_path:
                detected_paths = self.detect_browser_paths()
                browser_path = detected_paths.get(browser.lower())
                
                if not browser_path:
                    print(f"未找到{browser}浏览器路径")
                    return False
            
            # 启动命令
            cmd = [
                browser_path,
                "--remote-debugging-port=9222",
                "--user-data-dir=temp_profile",
                "--no-first-run",
                "--no-default-browser-check"
            ]
            
            print(f"正在启动{browser}浏览器(调试模式)...")
            print(f"命令: {' '.join(cmd)}")
            
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            # 等待浏览器启动
            time.sleep(3)
            print("浏览器已启动，可以进行手动操作")
            return True
            
        except Exception as e:
            print(f"启动浏览器失败: {e}")
            return False
        
    def setup_driver(self, headless: bool = False, browser: str = "chrome", use_existing: bool = False, browser_path: str = None) -> None:
        """
        设置浏览器驱动
        
        Args:
            headless: 是否使用无头模式（后台运行）
            browser: 浏览器类型 ("chrome" 或 "edge")
            use_existing: 是否连接到已运行的浏览器实例
            browser_path: 浏览器可执行文件路径
        """
        try:
            print(f"正在初始化{browser.upper()}浏览器驱动...")
            
            self.browser_type = browser.lower()
            
            if self.browser_type == "edge":
                # Edge选项配置
                edge_options = webdriver.EdgeOptions()
                
                # 基础选项
                edge_options.add_argument('--no-sandbox')
                edge_options.add_argument('--disable-dev-shm-usage')
                edge_options.add_argument('--disable-blink-features=AutomationControlled')
                edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                edge_options.add_experimental_option('useAutomationExtension', False)
                
                # 设置用户代理
                edge_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
                
                # 如果指定了浏览器路径
                if browser_path:
                    edge_options.binary_location = browser_path
                    print(f"使用指定的Edge路径: {browser_path}")
                
                if use_existing:
                    # 连接到已运行的Edge实例
                    edge_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
                    print("尝试连接到已运行的Edge浏览器实例...")
                    
                if headless:
                    edge_options.add_argument('--headless')
                
                # 设置驱动服务
                try:
                    service = EdgeService(EdgeChromiumDriverManager().install())
                except Exception as e:
                    print(f"自动下载Edge驱动失败: {e}")
                    print("尝试使用系统PATH中的Edge驱动...")
                    service = EdgeService()
                
                # 创建驱动实例
                self.driver = webdriver.Edge(service=service, options=edge_options)
                
            else:  # Chrome
                # Chrome选项配置
                chrome_options = webdriver.ChromeOptions()
                
                # 基础选项
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # 设置用户代理
                chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                
                # 如果指定了浏览器路径
                if browser_path:
                    chrome_options.binary_location = browser_path
                    print(f"使用指定的Chrome路径: {browser_path}")
                
                if use_existing:
                    # 连接到已运行的Chrome实例
                    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
                    print("尝试连接到已运行的Chrome浏览器实例...")
                
                if headless:
                    chrome_options.add_argument('--headless')
                
                # 设置驱动服务
                try:
                    service = ChromeService(ChromeDriverManager().install())
                except Exception as e:
                    print(f"自动下载Chrome驱动失败: {e}")
                    print("尝试使用系统PATH中的Chrome驱动...")
                    service = ChromeService()
                
                # 创建驱动实例
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 通用设置（仅在新实例时执行）
            if not use_existing:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                # 设置窗口大小
                self.driver.set_window_size(1920, 1080)
            
            # 设置等待
            self.wait = WebDriverWait(self.driver, 30)
            
            print(f"{browser.upper()}浏览器驱动初始化成功!")
            
        except Exception as e:
            print(f"浏览器驱动初始化失败: {e}")
            if use_existing:
                print("连接已运行实例失败，请确保:")
                print("1. 浏览器已启动并开启了远程调试端口")
                print("2. 启动命令包含: --remote-debugging-port=9222")
            raise
    
    def open_xiumi_login(self) -> None:
        """打开秀米登录页面"""
        try:
            print("正在打开秀米登录页面...")
            self.driver.get(self.login_url)
            
            # 等待页面加载
            time.sleep(3)
            print("秀米登录页面已打开，请手动完成登录操作...")
            
        except Exception as e:
            print(f"打开登录页面失败: {e}")
            raise
    
    def wait_for_login(self, timeout: int = 300) -> bool:
        """
        等待用户完成登录
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            bool: 登录是否成功
        """
        try:
            print(f"等待用户登录（超时时间: {timeout}秒）...")
            
            # 检查是否已经在编辑器页面或者登录成功的标志
            start_time = time.time()
            while time.time() - start_time < timeout:
                current_url = self.driver.current_url
                
                # 检查是否跳转到了编辑器或其他已登录页面
                if "editor" in current_url or "dashboard" in current_url or "home" in current_url:
                    print("检测到登录成功!")
                    return True
                
                # 检查是否有登录成功的DOM元素
                try:
                    # 这里可以根据秀米的实际页面结构调整选择器
                    login_success_elements = [
                        "//div[contains(@class, 'user')]",
                        "//div[contains(@class, 'avatar')]",
                        "//span[contains(text(), '用户')]",
                        "//div[contains(@class, 'header-user')]"
                    ]
                    
                    for selector in login_success_elements:
                        try:
                            element = self.driver.find_element(By.XPATH, selector)
                            if element.is_displayed():
                                print("检测到登录成功标志!")
                                return True
                        except NoSuchElementException:
                            continue
                            
                except Exception:
                    pass
                
                time.sleep(2)
                print(".", end="", flush=True)
            
            print(f"\n登录超时（{timeout}秒）")
            return False
            
        except Exception as e:
            print(f"等待登录过程中发生错误: {e}")
            return False
    
    def navigate_to_editor(self) -> None:
        """导航到编辑器页面"""
        try:
            print("正在导航到编辑器页面...")
            self.driver.get(self.editor_url)
            time.sleep(3)
            print("已进入编辑器页面")
            
        except Exception as e:
            print(f"导航到编辑器失败: {e}")
            raise
    
    def get_articles_list(self) -> List[Dict]:
        """
        获取文章列表
        
        Returns:
            List[Dict]: 文章信息列表
        """
        try:
            print("正在获取文章列表...")
            
            articles = []
            
            # 这里需要根据秀米的实际页面结构来定位文章列表
            # 以下是示例选择器，需要根据实际情况调整
            article_selectors = [
                "//div[contains(@class, 'article-item')]",
                "//div[contains(@class, 'post-item')]",
                "//li[contains(@class, 'article')]",
                "//div[contains(@class, 'content-item')]"
            ]
            
            for selector in article_selectors:
                try:
                    article_elements = self.driver.find_elements(By.XPATH, selector)
                    if article_elements:
                        print(f"找到 {len(article_elements)} 篇文章")
                        
                        for i, element in enumerate(article_elements[:10]):  # 限制前10篇
                            try:
                                # 提取文章信息
                                title = "未知标题"
                                article_id = f"article_{i}"
                                
                                # 尝试获取标题
                                title_selectors = [
                                    ".//h3", ".//h2", ".//h4",
                                    ".//*[contains(@class, 'title')]",
                                    ".//*[contains(@class, 'name')]"
                                ]
                                
                                for title_sel in title_selectors:
                                    try:
                                        title_elem = element.find_element(By.XPATH, title_sel)
                                        title = title_elem.text.strip()
                                        if title:
                                            break
                                    except:
                                        continue
                                
                                articles.append({
                                    'id': article_id,
                                    'title': title,
                                    'element': element
                                })
                                
                            except Exception as e:
                                print(f"处理文章 {i} 时出错: {e}")
                                continue
                        
                        break
                        
                except NoSuchElementException:
                    continue
            
            if not articles:
                print("未找到文章列表，可能需要调整选择器")
            
            return articles
            
        except Exception as e:
            print(f"获取文章列表失败: {e}")
            return []
    
    def get_quickshare_code(self, article_element) -> Optional[str]:
        """
        获取指定文章的另存码
        
        Args:
            article_element: 文章元素
            
        Returns:
            str: 另存码，如果获取失败返回None
        """
        try:
            print("正在获取另存码...")
            
            # 点击文章打开编辑页面
            self.driver.execute_script("arguments[0].click();", article_element)
            time.sleep(3)
            
            # 寻找另存码相关的按钮或链接
            quickshare_selectors = [
                "//button[contains(text(), '另存')]",
                "//a[contains(text(), '另存')]",
                "//div[contains(text(), '另存')]",
                "//span[contains(text(), '另存')]",
                "//button[contains(@class, 'share')]",
                "//button[contains(@class, 'save')]",
                "//div[contains(@class, 'quickshare')]"
            ]
            
            for selector in quickshare_selectors:
                try:
                    element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    self.driver.execute_script("arguments[0].click();", element)
                    time.sleep(2)
                    break
                except TimeoutException:
                    continue
            
            # 寻找另存码输入框或显示区域
            code_selectors = [
                "//input[contains(@placeholder, '另存码')]",
                "//textarea[contains(@placeholder, '另存码')]",
                "//div[contains(@class, 'code')]//input",
                "//div[contains(@class, 'share-code')]",
                "//span[contains(@class, 'code')]"
            ]
            
            for selector in code_selectors:
                try:
                    code_element = self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    
                    if code_element.tag_name.lower() in ['input', 'textarea']:
                        code = code_element.get_attribute('value')
                    else:
                        code = code_element.text
                    
                    if code and code.strip():
                        print(f"成功获取另存码: {code}")
                        return code.strip()
                        
                except TimeoutException:
                    continue
            
            print("未找到另存码")
            return None
            
        except Exception as e:
            print(f"获取另存码失败: {e}")
            return None
    
    def save_codes_to_file(self, codes: Dict[str, str], filename: str = None) -> str:
        """
        保存另存码到文件
        
        Args:
            codes: 另存码字典 {文章标题: 另存码}
            filename: 保存的文件名
            
        Returns:
            str: 保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xiumi_quickshare_codes_{timestamp}.json"
        
        filepath = os.path.join(os.getcwd(), filename)
        
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'total_count': len(codes),
                'codes': codes
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"另存码已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"保存文件失败: {e}")
            return None
    
    def run(self, headless: bool = False, browser: str = "chrome", use_existing: bool = False, browser_path: str = None) -> Dict[str, str]:
        """
        主运行函数
        
        Args:
            headless: 是否使用无头模式
            browser: 浏览器类型 ("chrome" 或 "edge")
            use_existing: 是否连接到已运行的浏览器实例
            browser_path: 浏览器可执行文件路径
            
        Returns:
            Dict[str, str]: 获取到的另存码字典
        """
        codes = {}
        
        try:
            # 1. 初始化浏览器
            self.setup_driver(headless=headless, browser=browser, use_existing=use_existing, browser_path=browser_path)
            
            # 2. 打开登录页面
            self.open_xiumi_login()
            
            # 3. 等待用户登录
            if not self.wait_for_login():
                print("登录超时或失败")
                return codes
            
            # 4. 导航到编辑器
            self.navigate_to_editor()
            
            # 5. 获取文章列表
            articles = self.get_articles_list()
            
            if not articles:
                print("未找到任何文章")
                return codes
            
            # 6. 逐个获取另存码
            print(f"开始获取 {len(articles)} 篇文章的另存码...")
            
            for i, article in enumerate(articles, 1):
                print(f"\n[{i}/{len(articles)}] 处理文章: {article['title']}")
                
                try:
                    code = self.get_quickshare_code(article['element'])
                    if code:
                        codes[article['title']] = code
                        print(f"✓ 成功获取另存码")
                    else:
                        print(f"✗ 未能获取另存码")
                        
                    # 返回到文章列表
                    self.driver.back()
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"✗ 处理文章失败: {e}")
                    continue
            
            # 7. 保存结果
            if codes:
                self.save_codes_to_file(codes)
                print(f"\n成功获取 {len(codes)} 个另存码")
            else:
                print("\n未获取到任何另存码")
            
            return codes
            
        except Exception as e:
            print(f"运行过程中发生错误: {e}")
            return codes
            
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """清理资源"""
        try:
            if self.driver:
                print("正在关闭浏览器...")
                self.driver.quit()
                print("浏览器已关闭")
        except Exception as e:
            print(f"清理资源时发生错误: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("秀米编辑器另存码获取工具")
    print("=" * 60)
    
    try:
        # 创建获取器实例
        fetcher = XiumiQuickShareFetcher()
        
        # 检测已安装的浏览器
        detected_browsers = fetcher.detect_browser_paths()
        print("\n检测到的浏览器:")
        for browser, path in detected_browsers.items():
            print(f"✓ {browser.upper()}: {path}")
        
        if not detected_browsers:
            print("❌ 未检测到浏览器，请手动指定路径")
        
        # 选择浏览器
        while True:
            print("\n请选择浏览器:")
            print("1. Chrome")
            print("2. Edge (推荐)")
            browser_choice = input("请输入选择 (1/2，默认2): ").strip()
            
            if browser_choice in ['', '2']:
                browser = "edge"
                break
            elif browser_choice == '1':
                browser = "chrome"
                break
            else:
                print("请输入 1 或 2")
        
        # 选择连接方式
        use_existing = False
        browser_path = None
        
        while True:
            print("\n请选择连接方式:")
            print("1. 启动新的浏览器实例")
            print("2. 连接到已运行的浏览器")
            print("3. 自动启动调试模式浏览器")
            print("4. 指定浏览器路径")
            
            connect_choice = input("请输入选择 (1/2/3/4，默认1): ").strip()
            
            if connect_choice in ['', '1']:
                # 使用新实例
                break
            elif connect_choice == '2':
                # 连接已运行实例
                use_existing = True
                print("\n📋 使用已运行浏览器的说明:")
                print("请确保浏览器是以调试模式启动的:")
                print(f"启动命令: {detected_browsers.get(browser, 'msedge.exe')} --remote-debugging-port=9222")
                print("或者选择选项3让程序自动启动")
                break
            elif connect_choice == '3':
                # 自动启动调试模式
                print(f"\n正在启动{browser.upper()}调试模式...")
                if fetcher.start_browser_with_debug(browser, detected_browsers.get(browser)):
                    use_existing = True
                    print("✅ 浏览器已启动，请在浏览器中进行必要操作后继续")
                    input("操作完成后按回车键继续...")
                else:
                    print("❌ 启动失败，将使用新实例模式")
                break
            elif connect_choice == '4':
                # 手动指定路径
                custom_path = input(f"请输入{browser.upper()}浏览器的完整路径: ").strip().strip('"')
                if os.path.exists(custom_path):
                    browser_path = custom_path
                    print(f"✅ 使用自定义路径: {custom_path}")
                    break
                else:
                    print("❌ 指定的路径不存在，请重新选择")
            else:
                print("请输入 1、2、3 或 4")
        
        # 询问是否使用无头模式
        headless = False
        if not use_existing:  # 已运行实例不支持无头模式
            while True:
                mode = input("是否使用无头模式？(y/n，默认n): ").strip().lower()
                if mode in ['', 'n', 'no']:
                    headless = False
                    break
                elif mode in ['y', 'yes']:
                    headless = True
                    break
                else:
                    print("请输入 y 或 n")
        
        # 显示配置信息
        print(f"\n" + "=" * 40)
        print("配置信息:")
        print(f"浏览器: {browser.upper()}")
        print(f"连接方式: {'连接已运行实例' if use_existing else '启动新实例'}")
        print(f"运行模式: {'无头模式' if headless else '有界面模式'}")
        if browser_path:
            print(f"浏览器路径: {browser_path}")
        print("=" * 40)
        
        print("注意: 脚本将打开/连接浏览器，请在浏览器中完成登录操作")
        input("按回车键开始...")
        
        # 运行获取程序
        codes = fetcher.run(
            headless=headless, 
            browser=browser, 
            use_existing=use_existing, 
            browser_path=browser_path
        )
        
        # 显示结果
        if codes:
            print(f"\n" + "=" * 60)
            print(f"获取完成! 共获取到 {len(codes)} 个另存码:")
            print("=" * 60)
            for title, code in codes.items():
                print(f"文章: {title}")
                print(f"另存码: {code}")
                print("-" * 40)
        else:
            print("\n未获取到任何另存码")
        
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序运行失败: {e}")
    finally:
        print("\n程序结束")


if __name__ == "__main__":
    main()
