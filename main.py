"""
WiFi Password Finder
======================
Finds and displays all saved WiFi passwords on your Windows/Linux/Mac machine.
No external dependencies required - uses built-in OS commands.
"""

import subprocess
import sys
import os
import re
import json
from datetime import datetime


def get_wifi_profiles_windows():
    """Get all saved WiFi profiles on Windows."""
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "profiles"],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        
        profiles = []
        for line in result.stdout.split("\n"):
            if "All User Profile" in line or "Tüm Kullanıcı Profili" in line:
                # Extract profile name
                profile = line.split(":")[1].strip()
                if profile:
                    profiles.append(profile)
        
        return profiles
    except Exception as e:
        print(f"Error: {e}")
        return []


def get_wifi_password_windows(profile):
    """Get password for a specific WiFi profile on Windows."""
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "profile", profile, "key=clear"],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        
        password = None
        security = "Unknown"
        
        for line in result.stdout.split("\n"):
            # English
            if "Key Content" in line:
                password = line.split(":")[1].strip()
            if "Authentication" in line:
                security = line.split(":")[1].strip()
            # Turkish
            if "Anahtar İçeriği" in line:
                password = line.split(":")[1].strip()
            if "Kimlik Doğrulama" in line:
                security = line.split(":")[1].strip()
        
        return {
            "profile": profile,
            "password": password or "(no password / open network)",
            "security": security,
        }
    except:
        return {
            "profile": profile,
            "password": "(error reading)",
            "security": "Unknown",
        }


def get_wifi_passwords_linux():
    """Get saved WiFi passwords on Linux."""
    results = []
    
    # Method 1: NetworkManager
    nm_path = "/etc/NetworkManager/system-connections/"
    if os.path.exists(nm_path):
        try:
            for filename in os.listdir(nm_path):
                filepath = os.path.join(nm_path, filename)
                with open(filepath, "r") as f:
                    content = f.read()
                
                ssid = filename.replace(".nmconnection", "")
                password = "(open network)"
                
                for line in content.split("\n"):
                    if "psk=" in line:
                        password = line.split("=")[1].strip()
                    elif "ssid=" in line:
                        ssid = line.split("=")[1].strip()
                
                results.append({
                    "profile": ssid,
                    "password": password,
                    "security": "WPA" if password != "(open network)" else "Open",
                })
        except PermissionError:
            print("⚠️  Run with sudo for full access: sudo python main.py")
    
    # Method 2: nmcli
    if not results:
        try:
            output = subprocess.run(
                ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
                capture_output=True, text=True
            )
            for line in output.stdout.strip().split("\n"):
                parts = line.split(":")
                if len(parts) >= 2 and "wireless" in parts[1].lower():
                    name = parts[0]
                    pwd_output = subprocess.run(
                        ["nmcli", "-s", "-g", "802-11-wireless-security.psk", "connection", "show", name],
                        capture_output=True, text=True
                    )
                    password = pwd_output.stdout.strip() or "(open network)"
                    results.append({
                        "profile": name,
                        "password": password,
                        "security": "WPA",
                    })
        except:
            pass
    
    return results


def get_wifi_passwords_mac():
    """Get saved WiFi passwords on macOS."""
    results = []
    
    try:
        # Get list of preferred networks
        output = subprocess.run(
            ["networksetup", "-listpreferredwirelessnetworks", "en0"],
            capture_output=True, text=True
        )
        
        networks = []
        for line in output.stdout.strip().split("\n")[1:]:
            network = line.strip()
            if network:
                networks.append(network)
        
        for network in networks:
            try:
                pwd_output = subprocess.run(
                    ["security", "find-generic-password", "-wa", network],
                    capture_output=True, text=True
                )
                password = pwd_output.stdout.strip() or "(access denied - run with sudo)"
            except:
                password = "(error)"
            
            results.append({
                "profile": network,
                "password": password,
                "security": "WPA",
            })
    except:
        pass
    
    return results


def display_results(results):
    """Display WiFi passwords in a nice table."""
    if not results:
        print("\n❌ No saved WiFi networks found.")
        return
    
    print(f"\n{'='*70}")
    print(f"{'WiFi Network':<30} {'Password':<25} {'Security':<15}")
    print(f"{'='*70}")
    
    found_passwords = 0
    
    for r in results:
        profile = r["profile"][:28]
        password = r["password"][:23]
        security = r["security"][:13]
        
        # Highlight if password found
        if r["password"] and r["password"] not in ["(no password / open network)", "(error reading)", "(open network)"]:
            found_passwords += 1
            icon = "🔑"
        else:
            icon = "🔓"
        
        print(f"{icon} {profile:<28} {password:<25} {security:<15}")
    
    print(f"{'='*70}")
    print(f"\n📊 Total networks: {len(results)} | With passwords: {found_passwords}")


def export_results(results, format="txt"):
    """Export results to file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == "json":
        filename = f"wifi_passwords_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    else:
        filename = f"wifi_passwords_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"WiFi Passwords - Exported {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            for r in results:
                f.write(f"Network:  {r['profile']}\n")
                f.write(f"Password: {r['password']}\n")
                f.write(f"Security: {r['security']}\n")
                f.write("-" * 40 + "\n")
    
    return filename


def main():
    print("""
    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║   🔑 WiFi Password Finder               ║
    ║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ║
    ║                                          ║
    ║   Find all saved WiFi passwords         ║
    ║   on your computer                       ║
    ║                                          ║
    ╚══════════════════════════════════════════╝
    """)
    
    # Detect OS
    platform = sys.platform
    
    if platform == "win32":
        print("  🖥️  OS: Windows")
        print("  ⏳ Scanning saved networks...\n")
        
        profiles = get_wifi_profiles_windows()
        results = []
        
        for profile in profiles:
            data = get_wifi_password_windows(profile)
            results.append(data)
    
    elif platform == "linux":
        print("  🐧 OS: Linux")
        print("  ⏳ Scanning saved networks...\n")
        results = get_wifi_passwords_linux()
    
    elif platform == "darwin":
        print("  🍎 OS: macOS")
        print("  ⏳ Scanning saved networks...\n")
        results = get_wifi_passwords_mac()
    
    else:
        print(f"  ❌ Unsupported OS: {platform}")
        return
    
    # Display
    display_results(results)
    
    # Export option
    if results:
        print("\n  📁 Export options:")
        print("  [1] Export to TXT")
        print("  [2] Export to JSON")
        print("  [3] Exit")
        
        choice = input("\n  Select [1/2/3]: ").strip()
        
        if choice == "1":
            filename = export_results(results, "txt")
            print(f"\n  ✅ Exported to {filename}")
        elif choice == "2":
            filename = export_results(results, "json")
            print(f"\n  ✅ Exported to {filename}")
        else:
            print("\n  👋 Done!")
    
    input("\n  Press Enter to exit...")


if __name__ == "__main__":
    main()
