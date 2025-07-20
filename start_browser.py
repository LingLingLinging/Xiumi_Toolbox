"""
浏览器调试模式启动工具

这个脚本可以帮助启动带有远程调试端口的浏览器，
便于后续的自动化脚本连接。
"""

import os
import subprocess
import time
from typing import Dict, Optional

def detect_browser_paths() -> Dict[str, str]:
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

def start_browser_debug_mode(browser: str, browser_path: str = None, port: int = 9222) -> bool:
    """启动浏览器调试模式"""
    try:
        if not browser_path:
            detected_paths = detect_browser_paths()
            browser_path = detected_paths.get(browser.lower())
            
            if not browser_path:
                print(f"❌ 未找到{browser}浏览器路径")
                return False
        
        # 创建临时用户数据目录
        temp_dir = os.path.join(os.getcwd(), f"temp_browser_profile_{browser}")
        
        # 启动命令
        cmd = [
            browser_path,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={temp_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows"
        ]
        
        print(f"正在启动{browser.upper()}浏览器(调试模式)...")
        print(f"调试端口: {port}")
        print(f"用户数据目录: {temp_dir}")
        print(f"执行命令: {' '.join(cmd)}")
        print("-" * 50)
        
        # 启动浏览器
        process = subprocess.Popen(
            cmd, 
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        print("✅ 浏览器已启动!")
        print(f"📋 现在你可以:")
        print("1. 在浏览器中打开秀米网站并登录")
        print("2. 进行任何必要的手动操作")
        print("3. 然后运行主脚本并选择'连接到已运行的浏览器'")
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 启动浏览器失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("浏览器调试模式启动工具")
    print("=" * 60)
    
    # 检测浏览器
    detected_browsers = detect_browser_paths()
    
    if not detected_browsers:
        print("❌ 未检测到任何浏览器")
        print("请确保已安装Chrome或Edge浏览器")
        return
    
    print("检测到的浏览器:")
    for browser, path in detected_browsers.items():
        print(f"✓ {browser.upper()}: {path}")
    
    # 选择浏览器
    while True:
        print("\n请选择要启动的浏览器:")
        options = []
        for i, browser in enumerate(detected_browsers.keys(), 1):
            print(f"{i}. {browser.upper()}")
            options.append(browser)
        
        if 'edge' in detected_browsers:
            default_choice = str(options.index('edge') + 1)
            print(f"(默认选择: {default_choice} - Edge)")
        else:
            default_choice = "1"
        
        choice = input(f"请输入选择 (1-{len(options)}，默认{default_choice}): ").strip()
        
        if choice == '':
            choice = default_choice
        
        try:
            browser_index = int(choice) - 1
            if 0 <= browser_index < len(options):
                selected_browser = options[browser_index]
                browser_path = detected_browsers[selected_browser]
                break
            else:
                print("选择超出范围，请重新选择")
        except ValueError:
            print("请输入有效的数字")
    
    # 自定义端口
    while True:
        port_input = input("请输入调试端口 (默认9222): ").strip()
        if port_input == '':
            port = 9222
            break
        try:
            port = int(port_input)
            if 1024 <= port <= 65535:
                break
            else:
                print("端口范围应在1024-65535之间")
        except ValueError:
            print("请输入有效的端口号")
    
    # 启动浏览器
    print(f"\n即将启动 {selected_browser.upper()} 浏览器...")
    input("按回车键继续...")
    
    if start_browser_debug_mode(selected_browser, browser_path, port):
        print("\n🎉 浏览器启动成功!")
        print("现在可以运行主脚本并选择连接模式了")
        print(f"主脚本: python fetch_quickshare.py")
    else:
        print("\n❌ 启动失败")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
