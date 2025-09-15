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

# Tether (USDT) Icon - Official Symbol
TETHER_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="tether-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#50AF95;stop-opacity:1"/>
        <stop offset="100%" style="stop-color:#26A69A;stop-opacity:1"/>
    </linearGradient>
</defs>
<circle cx="12" cy="12" r="10" fill="url(#tether-gradient)" stroke="#1B5E20" stroke-width="1"/>
<text x="12" y="16" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="12" font-weight="bold">₮</text>
</svg>
""".encode('utf-8')

# Bitcoin Icon
BITCOIN_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="bitcoin-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#F7931A;stop-opacity:1"/>
        <stop offset="100%" style="stop-color:#E65100;stop-opacity:1"/>
    </linearGradient>
</defs>
<circle cx="12" cy="12" r="10" fill="url(#bitcoin-gradient)" stroke="#BF360C" stroke-width="1.5"/>
<text x="12" y="16" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="12" font-weight="bold">₿</text>
</svg>
""".encode('utf-8')

# Ethereum Icon
ETHEREUM_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="eth-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#627EEA;stop-opacity:1"/>
        <stop offset="100%" style="stop-color:#454A75;stop-opacity:1"/>
    </linearGradient>
</defs>
<!-- Ethereum diamond symbol -->
<path d="M12 2L18 8L18 16L12 22L6 16L6 8Z" fill="url(#eth-gradient)" stroke="#454A75" stroke-width="1"/>
<path d="M12 2L18 8L12 12L6 8Z" fill="#FFFFFF" opacity="0.8"/>
<path d="M12 22L18 16L12 12L6 16Z" fill="#FFFFFF" opacity="0.6"/>
</svg>
""".encode('utf-8')

# USD Icon (Dollar Bill)
USD_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs>
    <linearGradient id="usd-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#4CAF50;stop-opacity:1"/>
        <stop offset="100%" style="stop-color:#2E7D32;stop-opacity:1"/>
    </linearGradient>
</defs>
<!-- Dollar bill shape -->
<rect x="3" y="6" width="18" height="12" rx="1" ry="1" fill="url(#usd-gradient)" stroke="#1B5E20" stroke-width="1"/>
<!-- Dollar sign -->
<text x="12" y="15" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="10" font-weight="bold">$</text>
<!-- Bill lines -->
<line x1="5" y1="9" x2="19" y2="9" stroke="white" stroke-width="0.5" opacity="0.7"/>
<line x1="5" y1="11" x2="19" y2="11" stroke="white" stroke-width="0.5" opacity="0.7"/>
<line x1="5" y1="13" x2="19" y2="13" stroke="white" stroke-width="0.5" opacity="0.7"/>
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

def check_internet_connection():
    """بررسی وجود اتصال اینترنت"""
    try:
        # تلاش برای اتصال به سرور DNS گوگل
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        try:
            # تلاش برای اتصال به سرور DNS کلودفلر
            socket.create_connection(("1.1.1.1", 53), timeout=5)
            return True
        except OSError:
            return False

class WeatherUpdater(QThread):
    weather_updated = pyqtSignal(str, str)  # temperature, icon_type

    def __init__(self):
        super().__init__()
        # Using a free weather API service that doesn't require API key
        self.city = "Mahshahr"

    def run(self):
        while True:
            try:
                # بررسی اتصال اینترنت قبل از تلاش برای دریافت داده‌ها
                if not check_internet_connection():
                    print("No internet connection detected for weather")
                    self.weather_updated.emit("No Internet", "sun")
                    self.msleep(60000)  # چک کردن هر دقیقه در صورت عدم اتصال
                    continue

                # Try primary weather service
                result = self._fetch_weather_wttr()
                if result:
                    temperature, icon_type = result
                    print(f"Fetched temperature: {temperature}, icon: {icon_type}")
                    self.weather_updated.emit(temperature, icon_type)
                else:
                    # If primary fails, try alternative
                    print("Primary weather API failed, trying alternative...")
                    alt_result = self._fetch_weather_alternative()
                    if alt_result:
                        temperature, icon_type = alt_result
                        print(f"Fetched temperature from alternative: {temperature}, icon: {icon_type}")
                        self.weather_updated.emit(temperature, icon_type)
                    else:
                        print("All weather services failed")
                        self.weather_updated.emit("Connection Error", "sun")
            except Exception as e:
                print(f"Error fetching weather: {str(e)}")
                self.weather_updated.emit("Connection Error", "sun")

            self.msleep(600000)  # Update every 10 minutes

    def _fetch_weather_wttr(self):
        """Primary weather service using wttr.in (reliable and no API key required)"""
        try:
            # Get weather data in JSON format for better parsing
            url = f"https://wttr.in/{self.city}?format=j1"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Get current weather
                current = data['current_condition'][0]
                temp_c = current['temp_C']
                weather_desc = current['weatherDesc'][0]['value'].lower()
                
                # Determine icon based on weather description
                if any(keyword in weather_desc for keyword in ['rain', 'shower', 'drizzle', 'precipitation']):
                    icon_type = "rain"
                elif any(keyword in weather_desc for keyword in ['cloud', 'overcast', 'fog', 'mist']):
                    icon_type = "cloud"
                elif any(keyword in weather_desc for keyword in ['clear', 'sunny', 'bright']):
                    # Check if it's night time (rough estimation)
                    current_hour = datetime.now().hour
                    icon_type = "moon" if current_hour < 6 or current_hour > 19 else "sun"
                else:
                    icon_type = "sun"

                return f"{temp_c}°C", icon_type
                
        except Exception as e:
            print(f"wttr.in API error: {str(e)}")
            return None

    def _fetch_weather_alternative(self):
        """Alternative weather service using simple wttr.in format"""
        try:
            # Get temperature and weather in simple format
            temp_url = f"https://wttr.in/{self.city}?format=%t"
            condition_url = f"https://wttr.in/{self.city}?format=%C"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            temp_response = requests.get(temp_url, headers=headers, timeout=10)
            condition_response = requests.get(condition_url, headers=headers, timeout=10)

            if temp_response.status_code == 200 and condition_response.status_code == 200:
                temp = temp_response.text.strip()
                condition = condition_response.text.strip().lower()

                # Clean up temperature
                temp = temp.replace('+', '').replace('−', '-')
                if '°' not in temp:
                    temp += '°C'

                # Determine icon based on condition text
                if any(keyword in condition for keyword in ['rain', 'shower', 'drizzle']):
                    icon_type = "rain"
                elif any(keyword in condition for keyword in ['cloud', 'overcast', 'fog']):
                    icon_type = "cloud"
                elif any(keyword in condition for keyword in ['clear', 'sunny']):
                    # Check if it's night time
                    current_hour = datetime.now().hour
                    icon_type = "moon" if current_hour < 6 or current_hour > 19 else "sun"
                else:
                    icon_type = "sun"

                return temp, icon_type
                
        except Exception as e:
            print(f"Alternative weather API error: {str(e)}")
            return None

class PriceUpdater(QThread):
    price_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.brs_api_url = "https://BrsApi.ir/Api/Market/Gold_Currency.php?key=B9PS4EgxiEgrngmuNdKa1xdgJybsp8Zi"
        # Using BRS API for cryptocurrency data as requested
        self.crypto_api_url = "https://BrsApi.ir/Api/Market/Cryptocurrency.php?key=B9PS4EgxiEgrngmuNdKa1xdgJybsp8Zi"

    def run(self):
        while True:
            try:
                # بررسی اتصال اینترنت قبل از تلاش برای دریافت داده‌ها
                if not check_internet_connection():
                    print("No internet connection detected for prices")
                    # ارسال پیام خطا برای همه قیمت‌ها
                    error_prices = {
                        "طلای ۱۸ عیار": "No Internet",
                        "سکه امامی": "No Internet",
                        "دلار": "No Internet",
                        "تتر": "No Internet",
                        "بیت‌کوین": "No Internet",
                        "اتریوم": "No Internet"
                    }
                    self.price_updated.emit(error_prices)
                    self.msleep(60000)  # چک کردن هر دقیقه در صورت عدم اتصال
                    continue

                # Fetch prices from both APIs
                gold_prices = self._fetch_from_api()
                crypto_prices = self._fetch_crypto_from_api()

                # Combine prices
                prices = {}
                if gold_prices:
                    prices.update(gold_prices)
                if crypto_prices:
                    prices.update(crypto_prices)

                if prices:
                    print(f"Fetched prices: {prices}")
                    self.price_updated.emit(prices)
                else:
                    # اگر هیچ داده‌ای دریافت نشد، پیام خطای عمومی ارسال شود
                    error_prices = {
                        "طلای ۱۸ عیار": "Connection Error",
                        "سکه امامی": "Connection Error",
                        "دلار": "Connection Error",
                        "تتر": "Connection Error",
                        "بیت‌کوین": "Connection Error",
                        "اتریوم": "Connection Error"
                    }
                    self.price_updated.emit(error_prices)

            except Exception as e:
                print(f"Error fetching prices: {str(e)}")
                # ارسال پیام خطا در صورت بروز خطای غیرمنتظره
                error_prices = {
                    "طلای ۱۸ عیار": "System Error",
                    "سکه امامی": "System Error",
                    "دلار": "System Error",
                    "تتر": "System Error",
                    "بیت‌کوین": "System Error",
                    "اتریوم": "System Error"
                }
                self.price_updated.emit(error_prices)

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

    def _fetch_crypto_from_api(self):
        """Fetch cryptocurrency prices from BRS API"""
        try:
            # Try with requests first
            import requests
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.crypto_api_url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                return self._parse_crypto_api_response(response.json())
        except Exception as e:
            print(f"Crypto API (requests) error: {str(e)}")

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

            req = urllib.request.Request(self.crypto_api_url, headers=headers)
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return self._parse_crypto_api_response(data)
        except Exception as e:
            print(f"Crypto API (urllib) error: {str(e)}")
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

            # Parse currency section
            if "currency" in data and isinstance(data["currency"], list):
                for item in data["currency"]:
                    if isinstance(item, dict):
                        symbol = item.get("symbol", "")
                        name = item.get("name", "")
                        price = item.get("price", "")

                        # USD as base exchange rate
                        if symbol == "USD":
                            prices["دلار"] = str(price)
                            prices["usd_to_irr"] = str(price)
                            print(f"Found USD price: {price}")

                        # Tether in IRR (USDT_IRT)
                        elif symbol == "USDT_IRT":
                            prices["تتر"] = str(price)
                            print(f"Found Tether (IRR): {price}")

        return prices if prices else None

    def _parse_crypto_api_response(self, data):
        """Parse the cryptocurrency JSON data from BRS API"""
        prices = {}

        print(f"Crypto JSON Data: {data}")  # Debug: print the full response

        if isinstance(data, dict):
            # Handle BRS API response structure: {"cryptocurrency": [...]}
            if "cryptocurrency" in data and isinstance(data["cryptocurrency"], list):
                print("Found cryptocurrency data in BRS format")
                for item in data["cryptocurrency"]:
                    if isinstance(item, dict):
                        symbol = item.get("symbol", "")
                        name = item.get("name", "")
                        price = item.get("price", "")

                        print(f"Crypto item: symbol={symbol}, name={name}, price={price}")

                        # Check for different cryptocurrencies
                        if symbol == "USDT" or name == "تتر" or name == "Tether":
                            if price:
                                prices["تتر"] = str(price)
                                print(f"Found Tether price from BRS: {price}")
                        elif symbol == "BTC" or name == "بیت‌کوین" or name == "Bitcoin":
                            if price:
                                prices["بیت‌کوین"] = str(price)
                                print(f"Found Bitcoin price from BRS: {price}")
                        elif symbol == "ETH" or name == "اتریوم" or name == "Ethereum":
                            if price:
                                prices["اتریوم"] = str(price)
                                print(f"Found Ethereum price from BRS: {price}")

            # Fallback: Check for other possible structures
            else:
                possible_keys = ["crypto", "data", "result", "coins", "assets"]

                for key in possible_keys:
                    if key in data and isinstance(data[key], list):
                        print(f"Found crypto data in key: {key}")
                        for item in data[key]:
                            if isinstance(item, dict):
                                symbol = item.get("symbol", item.get("Symbol", ""))
                                name = item.get("name", item.get("Name", ""))
                                price = item.get("price", item.get("Price", ""))

                                print(f"Crypto item from {key}: symbol={symbol}, name={name}, price={price}")

                                if (symbol and ("USDT" in symbol.upper() or "TETHER" in symbol.upper())) or \
                                   (name and ("تتر" in name or "TETHER" in name.upper() or "USDT" in name.upper())):
                                    if price:
                                        prices["تتر"] = str(price)
                                        print(f"Found Tether price: {price}")
                                elif (symbol and "BTC" in symbol.upper()) or \
                                     (name and ("بیت‌کوین" in name or "BITCOIN" in name.upper())):
                                    if price:
                                        prices["بیت‌کوین"] = str(price)
                                        print(f"Found Bitcoin price: {price}")
                                elif (symbol and "ETH" in symbol.upper()) or \
                                     (name and ("اتریوم" in name or "ETHEREUM" in name.upper())):
                                    if price:
                                        prices["اتریوم"] = str(price)
                                        print(f"Found Ethereum price: {price}")
                                        break

        elif isinstance(data, list):
            # If the entire response is a list of cryptocurrencies
            print("Crypto data is a direct list")
            for item in data:
                if isinstance(item, dict):
                    symbol = item.get("symbol", item.get("Symbol", ""))
                    name = item.get("name", item.get("Name", ""))
                    price = item.get("price", item.get("Price", ""))

                    print(f"Direct list crypto item: symbol={symbol}, name={name}, price={price}")

                    if (symbol and ("USDT" in symbol.upper() or "TETHER" in symbol.upper())) or \
                       (name and ("تتر" in name or "TETHER" in name.upper() or "USDT" in name.upper())):
                        if price:
                            prices["تتر"] = str(price)
                            print(f"Found Tether price: {price}")
                    elif (symbol and "BTC" in symbol.upper()) or \
                         (name and ("بیت‌کوین" in name or "BITCOIN" in name.upper())):
                        if price:
                            prices["بیت‌کوین"] = str(price)
                            print(f"Found Bitcoin price: {price}")
                    elif (symbol and "ETH" in symbol.upper()) or \
                         (name and ("اتریوم" in name or "ETHEREUM" in name.upper())):
                        if price:
                            prices["اتریوم"] = str(price)
                            print(f"Found Ethereum price: {price}")
                            break

        print(f"Final crypto prices: {prices}")
        return prices if prices else None

class GlassWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نرخ طلا و سکه")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
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
        # استفاده از فونت‌های رسمی ویندوز
        try:
            # اولویت اول: Segoe UI (فونت مدرن ویندوز)
            custom_font = QFont("Segoe UI", 14)
            # بررسی در دسترس بودن فونت
            if not QFontDatabase.families().__contains__("Segoe UI"):
                # فونت جایگزین: Tahoma (برای ویندوزهای قدیمی‌تر)
                custom_font = QFont("Tahoma", 14)
        except Exception:
            # فونت پیش‌فرض در صورت بروز مشکل
            custom_font = QFont("Arial", 14)

        # --- مجموعه ویجت‌های طلا ---
        self.gold_price_label = QLabel("۲,۵۰۰,۰۰۰")
        self.gold_price_label.setFont(custom_font)
        self.gold_price_label.setStyleSheet("color: white; background-color: transparent;")

        self.gold_icon_label = QLabel()
        self.gold_icon_label.setPixmap(self._render_svg_to_pixmap(GOLD_ICON_SVG))
        self.gold_icon_label.setStyleSheet("background-color: transparent;")

        # --- مجموعه ویجت‌های سکه ---
        self.coin_price_label = QLabel("۱۴,۸۰۰,۰۰۰")
        self.coin_price_label.setFont(custom_font)
        self.coin_price_label.setStyleSheet("color: white; background-color: transparent;")

        self.coin_icon_label = QLabel()
        self.coin_icon_label.setPixmap(self._render_svg_to_pixmap(COIN_ICON_SVG))
        self.coin_icon_label.setStyleSheet("background-color: transparent;")

        # --- مجموعه ویجت‌های system ---
        self.system_price_label = QLabel(self._get_system_name())
        system_font = QFont(custom_font.family(), 12)
        self.system_price_label.setFont(system_font)
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
        self.weather_label = QLabel("۴۴°C")
        self.weather_label.setFont(custom_font)
        self.weather_label.setStyleSheet("color: white; background-color: transparent;")

        self.weather_icon_label = QLabel()
        self.weather_icon_label.setPixmap(self._render_svg_to_pixmap(SUN_ICON_SVG))
        self.weather_icon_label.setStyleSheet("background-color: transparent;")

        # --- مجموعه ویجت‌های Tether ---
        self.tether_price_label = QLabel("۵۰,۰۰۰")
        self.tether_price_label.setFont(custom_font)
        self.tether_price_label.setStyleSheet("color: white; background-color: transparent;")

        self.tether_icon_label = QLabel()
        self.tether_icon_label.setPixmap(self._render_svg_to_pixmap(TETHER_ICON_SVG))
        self.tether_icon_label.setStyleSheet("background-color: transparent;")

        # --- مجموعه ویجت‌های USD ---
        self.usd_price_label = QLabel("۴۹,۵۰۰")
        self.usd_price_label.setFont(custom_font)
        self.usd_price_label.setStyleSheet("color: white; background-color: transparent;")

        self.usd_icon_label = QLabel()
        self.usd_icon_label.setPixmap(self._render_svg_to_pixmap(USD_ICON_SVG))
        self.usd_icon_label.setStyleSheet("background-color: transparent;")

        # --- مجموعه ویجت‌های Bitcoin ---
        self.btc_price_label = QLabel("۱,۲۵۰,۰۰۰")
        self.btc_price_label.setFont(custom_font)
        self.btc_price_label.setStyleSheet("color: white; background-color: transparent;")

        self.btc_icon_label = QLabel()
        self.btc_icon_label.setPixmap(self._render_svg_to_pixmap(BITCOIN_ICON_SVG))
        self.btc_icon_label.setStyleSheet("background-color: transparent;")

        # --- مجموعه ویجت‌های Ethereum ---
        self.eth_price_label = QLabel("۲۵۰,۰۰۰")
        self.eth_price_label.setFont(custom_font)
        self.eth_price_label.setStyleSheet("color: white; background-color: transparent;")

        self.eth_icon_label = QLabel()
        self.eth_icon_label.setPixmap(self._render_svg_to_pixmap(ETHEREUM_ICON_SVG))
        self.eth_icon_label.setStyleSheet("background-color: transparent;")

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

        # --- کانتینر Tether ---
        tether_container = QWidget()
        tether_layout = QHBoxLayout(tether_container)
        tether_layout.setContentsMargins(20, 8, 20, 8)
        tether_layout.setSpacing(10)
        tether_layout.addStretch()
        tether_layout.addWidget(self.tether_icon_label)
        tether_layout.addWidget(self.tether_price_label)
        tether_layout.addStretch()

        # --- کانتینر USD ---
        usd_container = QWidget()
        usd_layout = QHBoxLayout(usd_container)
        usd_layout.setContentsMargins(20, 8, 20, 8)
        usd_layout.setSpacing(10)
        usd_layout.addStretch()
        usd_layout.addWidget(self.usd_icon_label)
        usd_layout.addWidget(self.usd_price_label)
        usd_layout.addStretch()

        # --- کانتینر Bitcoin ---
        btc_container = QWidget()
        btc_layout = QHBoxLayout(btc_container)
        btc_layout.setContentsMargins(20, 8, 20, 8)
        btc_layout.setSpacing(10)
        btc_layout.addStretch()
        btc_layout.addWidget(self.btc_icon_label)
        btc_layout.addWidget(self.btc_price_label)
        btc_layout.addStretch()

        # --- کانتینر Ethereum ---
        eth_container = QWidget()
        eth_layout = QHBoxLayout(eth_container)
        eth_layout.setContentsMargins(20, 8, 20, 8)
        eth_layout.setSpacing(10)
        eth_layout.addStretch()
        eth_layout.addWidget(self.eth_icon_label)
        eth_layout.addWidget(self.eth_price_label)
        eth_layout.addStretch()

        # --- ساخت استک ویجت برای جابجایی بین حالت‌ها ---
        self.stack = QStackedWidget()
        self.stack.addWidget(ip_container)         # ایندکس 0 - IP address
        self.stack.addWidget(system_container)     # ایندکس 1 - System name
        self.stack.addWidget(weather_container)    # ایندکس 2 - Weather
        self.stack.addWidget(coin_container)       # ایندکس 3 - سکه امامی
        self.stack.addWidget(gold_container)       # ایندکس 4 - طلای عیار 18
        self.stack.addWidget(usd_container)        # ایندکس 5 - USD
        self.stack.addWidget(tether_container)     # ایندکس 6 - تتر
        self.stack.addWidget(btc_container)        # ایندکس 7 - بیت کوین
        self.stack.addWidget(eth_container)        # ایندکس 8 - اتریوم

        # --- چیدمان اصلی ---
        content_layout = QHBoxLayout(container_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.stack)

        # --- تنظیم حالت اولیه ---
        self.stack.setCurrentIndex(0)  # نمایش IP
        self.display_mode = 'ip'

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
        
        # Ensure window is visible and on top
        self.show()
        self.raise_()
        self.activateWindow()
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
        if event.button() == Qt.MouseButton.RightButton:
            # کلیک راست: بستن برنامه
            self.close()
        elif event.button() == Qt.MouseButton.LeftButton:
            # تعیین محل کلیک بر اساس مختصات X
            click_x = event.position().x()
            widget_width = self.width()

            if click_x > widget_width / 2:
                # کلیک بر روی سمت راست (قیمت): نمایش اطلاعات بعدی (Next)
                current_index = self.stack.currentIndex()
                next_index = (current_index + 1) % 9
                self.stack.setCurrentIndex(next_index)
                self.display_mode = ['ip', 'system', 'weather', 'coin', 'gold', 'usd', 'tether', 'btc', 'eth'][next_index]
            else:
                # کلیک بر روی سمت چپ (آیکون): نمایش اطلاعات قبلی (Previous)
                current_index = self.stack.currentIndex()
                previous_index = (current_index - 1) % 9
                self.stack.setCurrentIndex(previous_index)
                self.display_mode = ['ip', 'system', 'weather', 'coin', 'gold', 'usd', 'tether', 'btc', 'eth'][previous_index]

    def _format_price(self, price_str):
        """گرد کردن قیمت به 6 رقم معنی‌دار"""
        try:
            # بررسی پیام‌های خطا و برگرداندن آنها بدون تغییر
            if isinstance(price_str, str):
                if "No Internet" in price_str or "Error" in price_str:
                    return price_str
                
                # Try to convert to float first (for decimal prices like 1.0)
                try:
                    price = float(price_str)
                except ValueError:
                    price = int(price_str)
            else:
                price = float(price_str)

            # For cryptocurrency prices close to 1, show more decimal places
            if price < 10:
                return convert_to_persian_numbers(f"{price:.4f}")
            else:
                # گرد کردن به نزدیک‌ترین عدد با 6 رقم معنی‌دار
                magnitude = 10 ** (len(str(int(price))) - 6)
                if magnitude > 0:
                    price = round(price / magnitude) * magnitude
                return convert_to_persian_numbers(f"{price:,}")
        except (ValueError, TypeError) as e:
            print(f"Error formatting price '{price_str}': {e}")
            return "Error"

    def _update_price_labels(self, prices):
        """به‌روزرسانی برچسب‌های قیمت"""
        try:
            print("Available prices:", prices.keys())  # برای دیباگ

            # Get USD to IRR exchange rate
            usd_to_irr_rate = None
            if "usd_to_irr" in prices:
                try:
                    usd_to_irr_rate = float(prices["usd_to_irr"])
                    print(f"USD to IRR rate: {usd_to_irr_rate}")
                except (ValueError, TypeError):
                    print("Error parsing USD to IRR rate")

            # به‌روزرسانی قیمت‌ها
            for key in prices:
                price_value = prices[key]
                
                # برای دلار
                if key.strip() == 'دلار':
                    if isinstance(price_value, str) and ("No Internet" in price_value or "Error" in price_value):
                        self.usd_price_label.setText(price_value)
                    else:
                        try:
                            usd_price = int(float(price_value))
                            self.usd_price_label.setText(convert_to_persian_numbers(f"{usd_price:,}"))
                        except (ValueError, TypeError):
                            self.usd_price_label.setText("Error")
                    print(f"Updated USD price: {price_value}")

                # برای بیت‌کوین
                elif key.strip() == 'بیت‌کوین':
                    self.btc_price_label.setText(self._format_price(price_value))
                    print(f"Updated Bitcoin price: {price_value}")

                # برای اتریوم
                elif key.strip() == 'اتریوم':
                    if isinstance(price_value, str) and ("No Internet" in price_value or "Error" in price_value):
                        self.eth_price_label.setText(price_value)
                    else:
                        try:
                            eth_price = int(float(price_value))
                            self.eth_price_label.setText(convert_to_persian_numbers(f"{eth_price:,}"))
                        except (ValueError, TypeError):
                            self.eth_price_label.setText("Error")
                    print(f"Updated Ethereum price: {price_value}")

                # برای سکه امامی
                elif key.strip() == 'سکه امامی':
                    self.coin_price_label.setText(self._format_price(price_value))
                    print(f"Updated coin price (Emami): {price_value}")

                # برای طلای 18 عیار - بررسی همه حالت‌های ممکن
                elif any(gold_type in key.strip() for gold_type in ['طلای ۱۸ عیار', 'طلای ۱۸عیار', 'طلا ۱۸ عیار']):
                    self.gold_price_label.setText(self._format_price(price_value))
                    print(f"Updated gold price: {price_value} from key: {key}")

                # برای تتر - نمایش قیمت به تومان بدون تبدیل به ریال
                elif key.strip() == 'تتر':
                    if isinstance(price_value, str) and ("No Internet" in price_value or "Error" in price_value):
                        self.tether_price_label.setText(price_value)
                    else:
                        try:
                            tether_price = int(float(price_value))
                            self.tether_price_label.setText(convert_to_persian_numbers(f"{tether_price:,}"))
                            print(f"Updated tether price: {tether_price} Toman")
                        except (ValueError, TypeError) as e:
                            print(f"Error formatting tether price: {e}")
                            self.tether_price_label.setText("Error")

        except (ValueError, TypeError) as e:
            print(f"Error updating labels: {str(e)}")
            self.gold_price_label.setText("Data Error")
            self.coin_price_label.setText("Data Error")
            self.tether_price_label.setText("Data Error")

    def _update_weather_display(self, temperature, icon_type):
        """به‌روزرسانی نمایش دما و آیکون"""
        try:
            # Update temperature label
            if temperature and temperature not in ["Connection Error", "No Internet"]:
                # تبدیل اعداد انگلیسی به فارسی
                persian_temp = convert_to_persian_numbers(temperature)
                self.weather_label.setText(persian_temp)
                print(f"Updated weather temperature: {persian_temp}")
            else:
                # نمایش پیام خطا
                self.weather_label.setText(temperature if temperature else "Data Error")

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
            self.weather_label.setText("Data Error")
            self.weather_icon_label.setPixmap(self._render_svg_to_pixmap(SUN_ICON_SVG))
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GlassWindow()
    window.show()
    sys.exit(app.exec())
