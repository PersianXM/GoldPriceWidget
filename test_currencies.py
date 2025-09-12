#!/usr/bin/env python3
"""
Test script for navigation changes and API testing
"""
import requests
import json
import sys
import os
import socket
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, QSize, QByteArray, Qt
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QStackedWidget
from PyQt6.QtGui import QFont, QFontDatabase, QPixmap, QColor, QPainter
from PyQt6.QtSvg import QSvgRenderer

def test_brs_currencies():
    """Test BRS API for all currency options"""
    url = "https://BrsApi.ir/Api/Market/Gold_Currency.php?key=B9PS4EgxiEgrngmuNdKa1xdgJybsp8Zi"

    try:
        print("Testing BRS Currency API...")
        print(f"URL: {url}")
        print("=" * 60)

        response = requests.get(url, timeout=10, verify=False)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Parse currency section
            if "currency" in data and isinstance(data["currency"], list):
                print("\n📊 تمام گزینه‌های ارزی موجود:")
                print("=" * 60)

                usd_to_irr_rate = None

                for item in data["currency"]:
                    if isinstance(item, dict):
                        symbol = item.get("symbol", "")
                        name = item.get("name", "")
                        price = item.get("price", "")

                        # Store USD rate for conversions
                        if symbol == "USD":
                            usd_to_irr_rate = float(price) if price else None

                        print(f"💵 {symbol} ({name}): {price} تومان")

                print("\n" + "=" * 60)
                print("🔄 نرخ تبدیل USD به تومان:")
                print(f"1 USD = {usd_to_irr_rate:,.0f} تومان" if usd_to_irr_rate else "N/A")

                # Show Tether related options
                print("\n💰 گزینه‌های مرتبط با تتر:")
                print("-" * 40)

                tether_options = []
                for item in data["currency"]:
                    if isinstance(item, dict):
                        symbol = item.get("symbol", "")
                        name = item.get("name", "")
                        price = item.get("price", "")

                        if "USDT" in symbol or "تتر" in name or "TETHER" in name.upper():
                            tether_options.append((symbol, name, price))

                if tether_options:
                    for symbol, name, price in tether_options:
                        usd_price = float(price) if price else 0
                        irr_price = usd_price * usd_to_irr_rate if usd_to_irr_rate else 0
                        print(f"💎 {symbol} ({name}): ${price}")
                        print(f"   💵 قیمت در تومان: {irr_price:,.0f}")
                else:
                    print("❌ گزینه تتر در ارزها یافت نشد")
            else:
                print("❌ ساختار داده ارزی نامعتبر")
        else:
            print(f"❌ API Error: {response.status_code}")

    except Exception as e:
        print(f"❌ Request Error: {str(e)}")

def test_brs_cryptocurrencies():
    """Test BRS API for cryptocurrency options"""
    url = "https://BrsApi.ir/Api/Market/Cryptocurrency.php?key=B9PS4EgxiEgrngmuNdKa1xdgJybsp8Zi"

    try:
        print("\n🪙 Testing BRS Cryptocurrency API...")
        print(f"URL: {url}")
        print("=" * 60)

        response = requests.get(url, timeout=10, verify=False)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Parse cryptocurrency section
            if "cryptocurrency" in data and isinstance(data["cryptocurrency"], list):
                print("\n🪙 تمام گزینه‌های رمز ارزی موجود:")
                print("=" * 60)

                tether_found = False
                for item in data["cryptocurrency"]:
                    if isinstance(item, dict):
                        symbol = item.get("symbol", "")
                        name = item.get("name", "")
                        price = item.get("price", "")

                        # Highlight Tether
                        if symbol == "USDT" or name == "تتر":
                            tether_found = True
                            print(f"💎 {symbol} ({name}): ${price}")
                            print(f"   💰 قیمت: ${price}")
                        else:
                            print(f"🪙 {symbol} ({name}): ${price}")

                if not tether_found:
                    print("❌ تتر در رمز ارزها یافت نشد")
            else:
                print("❌ ساختار داده رمز ارزی نامعتبر")
        else:
            print(f"❌ API Error: {response.status_code}")

    except Exception as e:
        print(f"❌ Request Error: {str(e)}")

def test_navigation_logic():
    """Test the new navigation logic for mouse clicks"""
    print("\n🖱️ Testing Navigation Logic...")
    print("=" * 60)

    # Simulate the display modes
    display_modes = ['ip', 'system', 'weather', 'usd', 'tether', 'btc', 'eth', 'coin', 'gold']
    total_modes = len(display_modes)

    print(f"Total display modes: {total_modes}")
    print(f"Modes: {display_modes}")
    print()

    # Test scenarios
    test_cases = [
        ("Current: 0 (IP)", 0, "Left Click (Next)", "next"),
        ("Current: 0 (IP)", 0, "Right Click (Previous)", "previous"),
        ("Current: 4 (Tether)", 4, "Left Click (Next)", "next"),
        ("Current: 4 (Tether)", 4, "Right Click (Previous)", "previous"),
        ("Current: 8 (Gold)", 8, "Left Click (Next)", "next"),
        ("Current: 8 (Gold)", 8, "Right Click (Previous)", "previous"),
    ]

    for description, current_index, action, direction in test_cases:
        if direction == "next":
            next_index = (current_index + 1) % total_modes
        else:  # previous
            next_index = (current_index - 1) % total_modes

        current_mode = display_modes[current_index]
        next_mode = display_modes[next_index]

        print(f"{description}")
        print(f"  {action}")
        print(f"  Result: {current_mode} → {next_mode} (Index: {current_index} → {next_index})")
        print()

    print("✅ Navigation logic test completed!")

class TestGlassWindow(QWidget):
    """Test version of GlassWindow with new navigation"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test - نرخ طلا و سکه")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.display_mode = 'gold'

        # Simple test container
        container_widget = QWidget(self)
        container_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        container_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 50);
                border-radius: 15px;
            }
            QLabel {
                color: white;
                background-color: transparent;
            }
        """)

        container_widget.setFixedWidth(300)
        container_widget.setFixedHeight(60)

        # Test label
        self.test_label = QLabel("🖱️ Test Navigation: Left=Next, Right=Previous")
        self.test_label.setStyleSheet("color: white; background-color: transparent; font-size: 12px;")

        # Layout
        layout = QHBoxLayout(container_widget)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.addWidget(self.test_label)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container_widget)

        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        container_widget.setGraphicsEffect(shadow)

        self.show()
        self.raise_()
        self.move(100, 100)  # Position away from main app

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.test_label.setText("🖱️ Left Click: Next → (Navigation would advance)")
        elif event.button() == Qt.MouseButton.RightButton:
            self.test_label.setText("🖱️ Right Click: Previous ← (Navigation would go back)")
        else:
            self.test_label.setText("🖱️ Test Navigation: Left=Next, Right=Previous")

def run_navigation_test():
    """Run the navigation test GUI"""
    print("\n🖱️ Running Navigation Test GUI...")
    print("Instructions:")
    print("- Left click: Should advance to next display")
    print("- Right click: Should go back to previous display")
    print("- Close window when done testing")
    print("=" * 60)

    app = QApplication(sys.argv)
    test_window = TestGlassWindow()
    test_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    print("🔍 بررسی گزینه‌های ارزی و رمز ارزی BRS API + Navigation Test")
    print("=" * 80)

    # Test currencies
    test_brs_currencies()

    # Test cryptocurrencies
    test_brs_cryptocurrencies()

    # Test navigation logic
    test_navigation_logic()

    print("\n" + "=" * 80)
    print("✅ بررسی کامل شد!")
    print("=" * 80)

    # Ask user if they want to run GUI test
    try:
        response = input("\n🖱️ Do you want to run the navigation GUI test? (y/n): ").strip().lower()
        if response == 'y' or response == 'yes':
            run_navigation_test()
        else:
            print("GUI test skipped.")
    except KeyboardInterrupt:
        print("\nGUI test skipped.")
