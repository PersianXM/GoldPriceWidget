#!/usr/bin/env python3
"""
Test script to verify price formatting works correctly
"""
import sys
import os

# Add current directory to path to import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions we need to test
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

def format_price(price_str):
    """Test version of the _format_price function"""
    try:
        # Handle both string and numeric types
        if isinstance(price_str, str):
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
        return "خطا"

def test_formatting():
    """Test various price formats"""
    test_cases = [
        "1.0",      # CoinGecko Tether price
        "1.0001",   # CoinGecko with more decimals
        1.0,        # Float
        "50000",    # String number
        50000,      # Integer
        "1.5",      # Decimal string
        "abc",      # Invalid input
    ]

    print("Testing Price Formatting:")
    print("=" * 40)

    for test_case in test_cases:
        result = format_price(test_case)
        print(f"Input: {test_case!r} -> Output: {result!r}")

if __name__ == "__main__":
    test_formatting()
