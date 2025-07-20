"""
简化的环境测试脚本
"""

def test_basic_imports():
    """测试基本导入"""
    try:
        print("测试基本导入...")
        
        import selenium
        print(f"✓ Selenium 版本: {selenium.__version__}")
        
        from selenium import webdriver
        print("✓ WebDriver 模块导入成功")
        
        from selenium.webdriver.edge.service import Service as EdgeService
        from selenium.webdriver.chrome.service import Service as ChromeService
        print("✓ 浏览器服务导入成功")
        
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        from webdriver_manager.chrome import ChromeDriverManager
        print("✓ 驱动管理器导入成功")
        
        return True
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_edge_availability():
    """测试Edge浏览器可用性"""
    try:
        print("\n测试Edge浏览器...")
        
        import subprocess
        import os
        
        # 检查常见的Edge安装路径
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        
        for path in edge_paths:
            if os.path.exists(path):
                print(f"✓ 找到Edge浏览器: {path}")
                return True
        
        print("✗ 未找到Edge浏览器")
        return False
        
    except Exception as e:
        print(f"✗ 检查Edge失败: {e}")
        return False

def test_chrome_availability():
    """测试Chrome浏览器可用性"""
    try:
        print("\n测试Chrome浏览器...")
        
        import subprocess
        import os
        
        # 检查常见的Chrome安装路径
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                print(f"✓ 找到Chrome浏览器: {path}")
                return True
        
        print("✗ 未找到Chrome浏览器")
        return False
        
    except Exception as e:
        print(f"✗ 检查Chrome失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("秀米另存码获取工具 - 简化环境测试")
    print("=" * 50)
    
    results = []
    
    # 测试基本导入
    results.append(test_basic_imports())
    
    # 测试浏览器可用性
    edge_available = test_edge_availability()
    chrome_available = test_chrome_availability()
    
    results.append(edge_available or chrome_available)
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    if edge_available:
        print("✅ Edge浏览器可用 (推荐)")
    if chrome_available:
        print("✅ Chrome浏览器可用")
    
    if not edge_available and not chrome_available:
        print("❌ 没有找到可用的浏览器")
        print("请安装Chrome或Edge浏览器")
    
    if all(results):
        print("\n🎉 环境检查通过！")
        print("可以运行主程序: python fetch_quickshare.py")
        if edge_available:
            print("建议选择Edge浏览器，兼容性更好")
    else:
        print("\n❌ 环境检查失败")
        print("请检查依赖包安装和浏览器安装")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
