import sys
import re
import os
import requests
from bs4 import BeautifulSoup

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QStackedWidget
from PyQt6.QtGui import QFont, QFontDatabase, QPixmap, QColor, QPainter
from PyQt6.QtCore import Qt, QTimer, QSize, QByteArray
from PyQt6.QtSvg import QSvgRenderer

# --- داده‌های SVG برای آیکون‌ها ---
GOLD_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="gold-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
<stop offset="0%" style="stop-color:#FDE08D;stop-opacity:1"/>
<stop offset="100%" style="stop-color:#D9A443;stop-opacity:1"/>
</linearGradient></defs>
<path d="M4 8 L6 16 L18 16 L20 8 Z" fill="url(#gold-gradient)" stroke="#B48834" stroke-width="1"/>
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

def convert_to_persian_numbers(input_str):
    """اعداد انگلیسی را به فارسی تبدیل می‌کند."""
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    translation_table = str.maketrans(english_digits, persian_digits)
    return input_str.translate(translation_table)

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
        container_widget.setFixedHeight(40)

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

        # --- ساخت ویجت‌های مجزا برای طلا و سکه ---
        gold_container = QWidget()
        gold_layout = QHBoxLayout(gold_container)
        gold_layout.setContentsMargins(20, 8, 20, 8)  # حاشیه بیشتر
        gold_layout.setSpacing(10)  # فاصله بیشتر بین آیتم‌ها
        gold_layout.addStretch()
        gold_layout.addWidget(self.gold_price_label)
        gold_layout.addWidget(self.gold_icon_label)
        gold_layout.addStretch()

        coin_container = QWidget()
        coin_layout = QHBoxLayout(coin_container)
        coin_layout.setContentsMargins(20, 8, 20, 8)  # حاشیه بیشتر
        coin_layout.setSpacing(10)  # فاصله بیشتر بین آیتم‌ها
        coin_layout.addStretch()
        coin_layout.addWidget(self.coin_price_label)
        coin_layout.addWidget(self.coin_icon_label)
        coin_layout.addStretch()

        # --- ساخت استک ویجت برای جابجایی بین حالت‌ها ---
        self.stack = QStackedWidget()
        self.stack.addWidget(coin_container)  # ایندکس 0
        self.stack.addWidget(gold_container)  # ایندکس 1

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

        # --- تایمر برای به‌روزرسانی خودکار ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_prices)
        self.timer.start(900000) # هر ۱۵ دقیقه
        self.update_prices()
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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            print(f"Current mode: {self.display_mode}")  # برای دیباگ
            if self.display_mode == 'coin':
                print("Switching to gold")  # برای دیباگ
                self.stack.setCurrentIndex(1)  # نمایش طلا
                self.display_mode = 'gold'
            else:
                print("Switching to coin")  # برای دیباگ
                self.stack.setCurrentIndex(0)  # نمایش سکه
                self.display_mode = 'coin'
            print(f"New mode: {self.display_mode}")  # برای دیباگ
        elif event.button() == Qt.MouseButton.RightButton:
            self.close()

    def _get_price_from_site(self, soup, market_row, fallback_regex):
        price_text = "پیدا نشد"
        try:
            # ... (کد استخراج قیمت بدون تغییر باقی می‌ماند)
            row = soup.find('tr', {'data-market-row': market_row})
            if row and (price_cell := row.find('td')):
                price_text = price_cell.text.strip()
            elif (label_element := soup.find(string=fallback_regex)):
                if (parent_row := label_element.find_parent('tr')) and (price_cell := parent_row.find('td')):
                    price_text = price_cell.text.strip()
            
            price_value_rial = int(re.sub(r'[^0-9]', '', price_text))
            price_value_toman = price_value_rial // 10
            return convert_to_persian_numbers(f"{price_value_toman:,}")
        except (ValueError, AttributeError):
            return "خطا"

    def update_prices(self):
        try:
            url = "https://www.tgju.org/"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # متن هر دو لیبل را به‌روز می‌کنیم، حتی اگر یکی از آن‌ها مخفی باشد
            gold_price = self._get_price_from_site(soup, 'geram18', re.compile(r"\s*گرم\s+طلای\s+۱۸\s*"))
            coin_price = self._get_price_from_site(soup, 'sekee', re.compile(r"\s*سکه\s+امامی\s*"))

            self.gold_price_label.setText(gold_price)
            self.coin_price_label.setText(coin_price)

        except requests.exceptions.RequestException:
             self.gold_price_label.setText("خطای اتصال")
             self.coin_price_label.setText("خطای اتصال")
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GlassWindow()
    window.show()
    sys.exit(app.exec())

