import sys
import re
import os
import socket
import json
import asyncio
import websockets
import requests
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QStackedWidget
from PyQt6.QtGui import QFont, QFontDatabase, QPixmap, QColor, QPainter
from PyQt6.QtCore import Qt, QTimer, QSize, QByteArray
from PyQt6.QtSvg import QSvgRenderer

# --- داده‌های SVG برای آیکون‌ها ---
GOLD_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="gold-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#FFE5A0;stop-opacity:1"/>
        <stop offset="50%" style="stop-color:#FFC107;stop-opacity:1"/>
        <stop offset="100%" style="stop-color:#FFB300;stop-opacity:1"/>
    </linearGradient>
</defs>
<!-- Gold ingot shape -->
<rect x="4" y="8" width="16" height="8" rx="1" ry="1" fill="url(#gold-gradient)" stroke="#B48834" stroke-width="1"/>
<rect x="6" y="10" width="12" height="4" rx="0.5" ry="0.5" fill="#FFD700" opacity="0.6"/>
<!-- Highlight lines -->
<line x1="6" y1="12" x2="18" y2="12" stroke="#B48834" stroke-width="0.5" opacity="0.8"/>
<line x1="6" y1="14" x2="18" y2="14" stroke="#B48834" stroke-width="0.5" opacity="0.8"/>
</svg>
""".encode('utf-8')

COIN_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs><radialGradient id="coin-gradient" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
<stop offset="0%" style="stop-color:#FDE08D;stop-opacity:1"/>
<stop offset="100%" style="stop-color:#D9A443;stop-opacity:1"/>
</radialGradient></defs>
<circle cx="12" cy="12" r="10" fill="url(#coin-gradient)" stroke="#B48834" stroke-width="1.5"/>
<circle cx="12" cy="12" r="7" fill="none" stroke="#B48834" stroke-width="1"/>
</svg>
""".encode('utf-8')

SYSTEM_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="system-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#64B5F6;stop-opacity:1"/>
<stop offset="100%" style="stop-color:#1976D2;stop-opacity:1"/>
</linearGradient></defs>
<path d="M12 2L2 7v10l10 5 10-5V7L12 2zm0 2.7L19.5 8 12 11.3 4.5 8 12 4.7zM4 16.2V9l8 3.3v7.5l-8-3.6zm16 0l-8 3.6v-7.5l8-3.3v7.2z" 
fill="url(#system-gradient)"/>
</svg>
""".encode('utf-8')

IP_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="ip-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#4CAF50;stop-opacity:1"/>
<stop offset="100%" style="stop-color:#2E7D32;stop-opacity:1"/>
</linearGradient></defs>
<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"
fill="url(#ip-gradient)"/>
</svg>
""".encode('utf-8')

# Weather Icons based on conditions
SUN_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs><radialGradient id="sun-gradient" cx="50%" cy="50%" r="50%">
<stop offset="0%" style="stop-color:#FFF176;stop-opacity:1"/>
<stop offset="100%" style="stop-color:#FF9800;stop-opacity:1"/>
</radialGradient></defs>
<circle cx="12" cy="12" r="5" fill="url(#sun-gradient)"/>
<path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" 
stroke="url(#sun-gradient)" stroke-width="2" fill="none"/>
</svg>
""".encode('utf-8')

CLOUD_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="cloud-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#B0BEC5;stop-opacity:1"/>
<stop offset="100%" style="stop-color:#607D8B;stop-opacity:1"/>
</linearGradient></defs>
<path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"
fill="url(#cloud-gradient)"/>
</svg>
""".encode('utf-8')

RAIN_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="rain-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#4FC3F7;stop-opacity:1"/>
<stop offset="100%" style="stop-color:#0277BD;stop-opacity:1"/>
</linearGradient></defs>
<path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"
fill="url(#rain-gradient)"/>
<path d="M8 18l2 2m4-2l2 2m-4-4l2 2" stroke="url(#rain-gradient)" stroke-width="2" fill="none"/>
</svg>
""".encode('utf-8')

MOON_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs><radialGradient id="moon-gradient" cx="30%" cy="30%" r="70%">
<stop offset="0%" style="stop-color:#FFF9C4;stop-opacity:1"/>
<stop offset="100%" style="stop-color:#F57C00;stop-opacity:1"/>
</radialGradient></defs>
<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" fill="url(#moon-gradient)"/>
</svg>
""".encode('utf-8')

# Default weather icon (sun)
WEATHER_ICON_SVG = SUN_ICON_SVG

def convert_to_persian_numbers(input_str):
    """اعداد انگلیسی را به فارسی تبدیل می‌کند."""
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    translation_table = str.maketrans(english_digits, persian_digits)
    return input_str.translate(translation_table)

def round_to_significant(num, n=6):
    """گرد کردن عدد به n رقم معنی‌دار"""
    if num == 0:
        return 0
    magnitude = 10 ** (len(str(int(num))) - n)
    if magnitude > 0:
        return round(num / magnitude) * magnitude
    return num

class WeatherUpdater(QThread):
    weather_updated = pyqtSignal(str, str)  # temperature, icon_type

    def __init__(self):
        super().__init__()
        # Using OpenWeatherMap API for weather data
        self.weather_api_url = "https://api.openweathermap.org/data/2.5/weather"
        self.api_key = "YOUR_OPENWEATHERMAP_API_KEY"  # Replace with actual API key
        self.city = "Mahshahr,IR"

    def run(self):
        while True:
            try:
                # Fetch weather data with condition
                result = self._fetch_weather_data()
                if result:
                    temperature, icon_type = result
                    print(f"Fetched temperature: {temperature}, icon: {icon_type}")
                    self.weather_updated.emit(temperature, icon_type)
                else:
                    # If API fails, try alternative method
                    print("API failed, trying alternative weather service...")
                    alt_result = self._fetch_weather_alternative()
                    if alt_result:
                        temperature, icon_type = alt_result
                        print(f"Fetched temperature from alternative: {temperature}, icon: {icon_type}")
                        self.weather_updated.emit(temperature, icon_type)
                    else:
                        print("All weather services failed")
                        self.weather_updated.emit("خطای اتصال", "sun")
            except Exception as e:
                print(f"Error fetching weather: {str(e)}")
                self.weather_updated.emit("خطای اتصال", "sun")

            self.msleep(600000)  # Update every 10 minutes

    def _get_weather_icon(self, condition_id, is_night=False):
        """Determine weather icon based on condition"""
        # Weather condition codes from OpenWeatherMap
        if is_night:
            return "moon"
        elif condition_id >= 200 and condition_id < 300:  # Thunderstorm
            return "rain"
        elif condition_id >= 300 and condition_id < 600:  # Rain
            return "rain"
        elif condition_id >= 600 and condition_id < 700:  # Snow
            return "rain"  # Using rain icon for snow too
        elif condition_id >= 700 and condition_id < 800:  # Atmosphere (fog, mist, etc.)
            return "cloud"
        elif condition_id == 800:  # Clear sky
            return "sun" if not is_night else "moon"
        elif condition_id > 800:  # Clouds
            return "cloud"
        else:
            return "sun"

    def _is_night_time(self, sunrise, sunset, current_time=None):
        """Check if it's night time based on sunrise/sunset"""
        if current_time is None:
            current_time = datetime.now().timestamp()

        return current_time < sunrise or current_time > sunset

    def _fetch_weather_data(self):
        """Fetch weather data from OpenWeatherMap API"""
        try:
            params = {
                'q': self.city,
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            response = requests.get(self.weather_api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                condition_id = data['weather'][0]['id']

                # Check if it's night time
                sunrise = data['sys']['sunrise']
                sunset = data['sys']['sunset']
                is_night = self._is_night_time(sunrise, sunset)

                icon_type = self._get_weather_icon(condition_id, is_night)
                return f"{temp:.1f}°C", icon_type
            else:
                print(f"API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Weather API error: {str(e)}")
            return None

    def _fetch_weather_alternative(self):
        """Alternative weather service using wttr.in (no API key required)"""
        try:
            # Get temperature
            temp_url = "https://wttr.in/Mahshahr?format=%t"
            temp_response = requests.get(temp_url, timeout=10)

            # Get weather condition
            condition_url = "https://wttr.in/Mahshahr?format=%C"
            condition_response = requests.get(condition_url, timeout=10)

            if temp_response.status_code == 200 and condition_response.status_code == 200:
                temp = temp_response.text.strip()
                condition = condition_response.text.strip().lower()

                # Clean up temperature
                temp = temp.replace('+', '')
                temp = temp.replace('°C', '').replace('°c', '').replace('C', '').replace('c', '')

                # Determine icon based on condition text
                if 'rain' in condition or 'shower' in condition or 'drizzle' in condition:
                    icon_type = "rain"
                elif 'cloud' in condition or 'overcast' in condition:
                    icon_type = "cloud"
                elif 'clear' in condition or 'sunny' in condition:
                    # Check if it's night time (rough estimation)
                    current_hour = datetime.now().hour
                    icon_type = "moon" if current_hour < 6 or current_hour > 18 else "sun"
                else:
                    icon_type = "sun"

                return f"{temp}°C", icon_type
        except Exception as e:
            print(f"Alternative weather API error: {str(e)}")
            return None

class PriceUpdater(QThread):
    price_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.brs_api_url = "https://BrsApi.ir/Api/Market/Gold_Currency.php?key=B9PS4EgxiEgrngmuNdKa1xdgJybsp8Zi"

    def run(self):
        while True:
            try:
                # Fetch prices from API
                prices = self._fetch_from_api()

                if prices:
                    print(f"Fetched prices: {prices}")
                    self.price_updated.emit(prices)

            except Exception as e:
                print(f"Error fetching prices: {str(e)}")

            self.msleep(15000)  # Update every 15 seconds

    def _load_json_data(self):
        """Load data from JSON file"""
        try:
            with open("FreeApi_Gold_Currency.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return self._parse_api_response(data)
        except Exception as e:
            print(f"Error loading JSON: {str(e)}")
            return None

    def _fetch_from_api(self):
        """Fetch prices from BRS API"""
        try:
            # Try with requests first
            import requests
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.brs_api_url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                return self._parse_api_response(response.json())
        except Exception as e:
            print(f"BRS API (requests) error: {str(e)}")

        # Fallback to urllib if requests fails
        try:
            import urllib.request
            import json
            import ssl

            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            req = urllib.request.Request(self.brs_api_url, headers=headers)
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return self._parse_api_response(data)
        except Exception as e:
            print(f"BRS API (urllib) error: {str(e)}")
            return None

    def _parse_api_response(self, data):
        """Parse the JSON data"""
        prices = {}

        print(f"JSON Data: {data}")  # Debug: print the full response

        if isinstance(data, dict):
            # Parse gold section
            if "gold" in data and isinstance(data["gold"], list):
                for item in data["gold"]:
                    if isinstance(item, dict):
                        symbol = item.get("symbol", "")
                        name = item.get("name", "")
                        price = item.get("price", "")
                        if symbol == "IR_GOLD_18K":
                            prices["طلای ۱۸ عیار"] = str(price)
                        elif symbol == "IR_COIN_EMAMI":
                            prices["سکه امامی"] = str(price)

        return prices if prices else None

class GlassWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نرخ طلا و سکه")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.display_mode = 'gold'  

        # --- ساخت ویجت‌های مجزا برای هر حالت نمایش ---
        
        container_widget = QWidget(self)
        container_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # تنظیم شفافیت و استایل
        container_style = """
            QWidget {
                background-color: rgba(0, 0, 0, 50);
                border-radius: 15px;
            }
            QLabel {
                color: white;
                background-color: transparent;
            }
        """
        container_widget.setStyleSheet(container_style)
        
        # تنظیم اندازه ثابت برای پنجره
        container_widget.setFixedWidth(220)
        container_widget.setFixedHeight(50)

        # --- فونت ---
        try:
            font_path = os.path.join(os.path.dirname(__file__), 'Vazirmatn-Regular.ttf')
            font_id = QFontDatabase.addApplicationFont(font_path)
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            custom_font = QFont(font_family, 14)
        except (IndexError, FileNotFoundError):
            custom_font = QFont("Arial", 14)

        # --- مجموعه ویجت‌های طلا ---
        self.gold_price_label = QLabel("...")
        self.gold_price_label.setFont(custom_font)
        self.gold_price_label.setStyleSheet("color: white; background-color: transparent;")
        
        self.gold_icon_label = QLabel()
        self.gold_icon_label.setPixmap(self._render_svg_to_pixmap(GOLD_ICON_SVG))
        self.gold_icon_label.setStyleSheet("background-color: transparent;")

        # --- مجموعه ویجت‌های سکه ---
        self.coin_price_label = QLabel("...")
        self.coin_price_label.setFont(custom_font)
        self.coin_price_label.setStyleSheet("color: white; background-color: transparent;")
        
        self.coin_icon_label = QLabel()
        self.coin_icon_label.setPixmap(self._render_svg_to_pixmap(COIN_ICON_SVG))
        self.coin_icon_label.setStyleSheet("background-color: transparent;")

        # --- مجموعه ویجت‌های system ---
        self.system_price_label = QLabel(self._get_system_name())
        self.system_price_label.setFont(custom_font)
        self.system_price_label.setStyleSheet("color: white; background-color: transparent;")
        
        self.system_icon_label = QLabel()
        self.system_icon_label.setPixmap(self._render_svg_to_pixmap(SYSTEM_ICON_SVG))
        self.system_icon_label.setStyleSheet("background-color: transparent;")

        # --- مجموعه ویجت‌های IP ---
        self.ip_label = QLabel(self._get_local_ip())
        self.ip_label.setFont(custom_font)
        self.ip_label.setStyleSheet("color: white; background-color: transparent;")

        self.ip_icon_label = QLabel()
        self.ip_icon_label.setPixmap(self._render_svg_to_pixmap(IP_ICON_SVG))
        self.ip_icon_label.setStyleSheet("background-color: transparent;")

        # --- مجموعه ویجت‌های Weather ---
        self.weather_label = QLabel("در حال بارگذاری...")
        self.weather_label.setFont(custom_font)
        self.weather_label.setStyleSheet("color: white; background-color: transparent;")

        self.weather_icon_label = QLabel()
        self.weather_icon_label.setPixmap(self._render_svg_to_pixmap(WEATHER_ICON_SVG))
        self.weather_icon_label.setStyleSheet("background-color: transparent;")

        # --- ساخت ویجت‌های مجزا برای طلا و سکه و system ---
        gold_container = QWidget()
        gold_layout = QHBoxLayout(gold_container)
        gold_layout.setContentsMargins(20, 8, 20, 8)  # حاشیه بیشتر
        gold_layout.setSpacing(10)  # فاصله بیشتر بین آیتم‌ها
        gold_layout.addStretch()
        gold_layout.addWidget(self.gold_icon_label)
        gold_layout.addWidget(self.gold_price_label)
        gold_layout.addStretch()

        coin_container = QWidget()
        coin_layout = QHBoxLayout(coin_container)
        coin_layout.setContentsMargins(20, 8, 20, 8)  # حاشیه بیشتر
        coin_layout.setSpacing(10)  # فاصله بیشتر بین آیتم‌ها
        coin_layout.addStretch()
        coin_layout.addWidget(self.coin_icon_label)
        coin_layout.addWidget(self.coin_price_label)
        coin_layout.addStretch()

        system_container = QWidget()
        system_layout = QHBoxLayout(system_container)
        system_layout.setContentsMargins(20, 8, 20, 8)  # حاشیه بیشتر
        system_layout.setSpacing(10)  # فاصله بیشتر بین آیتم‌ها
        system_layout.addStretch()
        system_layout.addWidget(self.system_icon_label)
        system_layout.addWidget(self.system_price_label)
        system_layout.addStretch()

        # --- کانتینر IP ---
        ip_container = QWidget()
        ip_layout = QHBoxLayout(ip_container)
        ip_layout.setContentsMargins(20, 8, 20, 8)
        ip_layout.setSpacing(10)
        ip_layout.addStretch()
        ip_layout.addWidget(self.ip_icon_label)
        ip_layout.addWidget(self.ip_label)
        ip_layout.addStretch()

        # --- کانتینر Weather ---
        weather_container = QWidget()
        weather_layout = QHBoxLayout(weather_container)
        weather_layout.setContentsMargins(20, 8, 20, 8)
        weather_layout.setSpacing(10)
        weather_layout.addStretch()
        weather_layout.addWidget(self.weather_icon_label)
        weather_layout.addWidget(self.weather_label)
        weather_layout.addStretch()

        # --- ساخت استک ویجت برای جابجایی بین حالت‌ها ---
        self.stack = QStackedWidget()
        self.stack.addWidget(coin_container)      # ایندکس 0
        self.stack.addWidget(gold_container)      # ایندکس 1
        self.stack.addWidget(system_container)    # ایندکس 2
        self.stack.addWidget(ip_container)        # ایندکس 3
        self.stack.addWidget(weather_container)   # ایندکس 4

        # --- چیدمان اصلی ---
        content_layout = QHBoxLayout(container_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.stack)

        # --- تنظیم حالت اولیه ---
        self.stack.setCurrentIndex(0)  # نمایش سکه
        self.display_mode = 'coin'

        # --- سایه و چیدمان اصلی ---
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 0)
        container_widget.setGraphicsEffect(shadow)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container_widget)

        # --- راه‌اندازی به‌روزرسانی قیمت‌ها در پس‌زمینه ---
        self.price_updater = PriceUpdater()
        self.price_updater.price_updated.connect(self._update_price_labels)
        self.price_updater.start()

        # --- راه‌اندازی به‌روزرسانی آب و هوا در پس‌زمینه ---
        self.weather_updater = WeatherUpdater()
        self.weather_updater.weather_updated.connect(self._update_weather_display)
        self.weather_updater.start()
        
        self.move_to_top_right()

    def _render_svg_to_pixmap(self, svg_data, size=QSize(22, 22)):
        renderer = QSvgRenderer(QByteArray(svg_data))
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap

    def move_to_top_right(self):
        QTimer.singleShot(100, self._do_move)

    def _do_move(self):
        self.adjustSize() 
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move(screen_geometry.width() - self.width() - 20, 20)

    def _get_system_name(self):
        """دریافت نام سیستم"""
        return os.environ.get('COMPUTERNAME', 'Unknown')

    def _get_local_ip(self):
        """دریافت IP محلی"""
        try:
            # ایجاد یک سوکت موقت برای دریافت IP محلی
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Unknown IP"

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            current_index = self.stack.currentIndex()
            # چرخش بین پنج حالت
            next_index = (current_index + 1) % 5
            self.stack.setCurrentIndex(next_index)
            self.display_mode = ['coin', 'gold', 'system', 'ip', 'weather'][next_index]
        elif event.button() == Qt.MouseButton.RightButton:
            self.close()

    def _format_price(self, price_str):
        """گرد کردن قیمت به 6 رقم معنی‌دار"""
        try:
            price = int(price_str)
            # گرد کردن به نزدیک‌ترین عدد با 6 رقم معنی‌دار
            magnitude = 10 ** (len(str(price)) - 6)
            if magnitude > 0:
                price = round(price / magnitude) * magnitude
            return convert_to_persian_numbers(f"{price:,}")
        except (ValueError, TypeError):
            return "خطا"

    def _update_price_labels(self, prices):
        """به‌روزرسانی برچسب‌های قیمت"""
        try:
            print("Available prices:", prices.keys())  # برای دیباگ

            # به‌روزرسانی قیمت‌ها
            for key in prices:
                # برای سکه امامی
                if key.strip() == 'سکه امامی':
                    self.coin_price_label.setText(self._format_price(prices[key]))
                    print(f"Updated coin price (Emami): {prices[key]}")

                # برای طلای 18 عیار - بررسی همه حالت‌های ممکن
                elif any(gold_type in key.strip() for gold_type in ['طلای ۱۸ عیار', 'طلای ۱۸عیار', 'طلا ۱۸ عیار']):
                    self.gold_price_label.setText(self._format_price(prices[key]))
                    print(f"Updated gold price: {prices[key]} from key: {key}")

        except (ValueError, TypeError) as e:
            print(f"Error updating labels: {str(e)}")
            self.gold_price_label.setText("خطای داده")
            self.coin_price_label.setText("خطای داده")

    def _update_weather_display(self, temperature, icon_type):
        """به‌روزرسانی نمایش دما و آیکون"""
        try:
            # Update temperature label
            if temperature and temperature != "خطای اتصال":
                # تبدیل اعداد انگلیسی به فارسی
                persian_temp = convert_to_persian_numbers(temperature)
                self.weather_label.setText(persian_temp)
                print(f"Updated weather temperature: {persian_temp}")
            else:
                self.weather_label.setText("خطای داده")

            # Update weather icon based on condition
            if icon_type == "sun":
                self.weather_icon_label.setPixmap(self._render_svg_to_pixmap(SUN_ICON_SVG))
            elif icon_type == "cloud":
                self.weather_icon_label.setPixmap(self._render_svg_to_pixmap(CLOUD_ICON_SVG))
            elif icon_type == "rain":
                self.weather_icon_label.setPixmap(self._render_svg_to_pixmap(RAIN_ICON_SVG))
            elif icon_type == "moon":
                self.weather_icon_label.setPixmap(self._render_svg_to_pixmap(MOON_ICON_SVG))
            else:
                # Default to sun icon
                self.weather_icon_label.setPixmap(self._render_svg_to_pixmap(SUN_ICON_SVG))

            print(f"Updated weather icon: {icon_type}")

        except Exception as e:
            print(f"Error updating weather display: {str(e)}")
            self.weather_label.setText("خطای داده")
            self.weather_icon_label.setPixmap(self._render_svg_to_pixmap(SUN_ICON_SVG))
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GlassWindow()
    window.show()
    sys.exit(app.exec())
