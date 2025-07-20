"""
测试脚本 - 验证依赖包和基础功能
"""

def test_imports():
    """测试依赖包导入"""
    try:
        print("测试导入依赖包...")
        
        import selenium
        print(f"✓ Selenium 版本: {selenium.__version__}")
        
        from selenium import webdriver
        print("✓ WebDriver 模块导入成功")
        
        from webdriver_manager.chrome import ChromeDriverManager
        print("✓ WebDriver Manager 导入成功")
        
        import requests
        print(f"✓ Requests 版本: {requests.__version__}")
        
        from bs4 import BeautifulSoup
        print("✓ BeautifulSoup 导入成功")
        
        print("\n所有依赖包测试通过! ✅")
        return True
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        print("\n请运行以下命令安装缺失的依赖:")
        print("pip install selenium webdriver-manager beautifulsoup4 requests lxml")
        return False

def test_chrome_driver():
    """测试Chrome驱动"""
    try:
        print("\n测试Chrome驱动...")
        
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        
        # 配置Chrome选项
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # 创建驱动
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 简单测试
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✓ Chrome驱动测试成功! 页面标题: {title}")
        return True
        
    except Exception as e:
        print(f"✗ Chrome驱动测试失败: {e}")
        return False

def test_edge_driver():
    """测试Edge驱动"""
    try:
        print("\n测试Edge驱动...")
        
        from selenium import webdriver
        from selenium.webdriver.edge.service import Service as EdgeService
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        
        # 配置Edge选项
        edge_options = webdriver.EdgeOptions()
        edge_options.add_argument('--headless')  # 无头模式
        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-dev-shm-usage')
        
        # 创建驱动
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=edge_options)
        
        # 简单测试
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✓ Edge驱动测试成功! 页面标题: {title}")
        return True
        
    except Exception as e:
        print(f"✗ Edge驱动测试失败: {e}")
        return False

def test_basic_functionality():
    """测试基础功能"""
    try:
        print("\n测试基础功能...")
        
        # 测试XiumiQuickShareFetcher类的导入
        import sys
        import os
        
        # 添加当前目录到路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        from fetch_quickshare import XiumiQuickShareFetcher
        
        # 创建实例
        fetcher = XiumiQuickShareFetcher()
        print("✓ XiumiQuickShareFetcher 类创建成功")
        
        # 测试URL配置
        assert fetcher.xiumi_base_url == "https://xiumi.us"
        assert fetcher.login_url == "https://xiumi.us/#/login"
        assert fetcher.editor_url == "https://xiumi.us/#/editor"
        print("✓ URL配置正确")
        
        print("\n基础功能测试通过! ✅")
        return True
        
    except Exception as e:
        print(f"✗ 基础功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("秀米另存码获取工具 - 环境测试")
    print("=" * 50)
    
    all_passed = True
    
    # 测试导入
    if not test_imports():
        all_passed = False
    
    # 测试Chrome驱动
    if not test_chrome_driver():
        all_passed = False
    
    # 测试Edge驱动
    if not test_edge_driver():
        all_passed = False
    
    # 测试基础功能
    if not test_basic_functionality():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过! 环境配置正确，可以运行主程序")
        print("运行命令: python fetch_quickshare.py")
        print("推荐使用Edge浏览器，兼容性更好")
    else:
        print("❌ 存在测试失败，请检查环境配置")
        print("请确保已安装所有依赖包和Chrome/Edge浏览器")
    print("=" * 50)

if __name__ == "__main__":
    main()
