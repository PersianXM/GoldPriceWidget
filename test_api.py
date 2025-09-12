#!/usr/bin/env python3
"""
Test script to verify CoinGecko API is working correctly
"""
import requests
import json

def test_coingecko_api():
    """Test CoinGecko API for Tether price"""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=usd"

    try:
        print("Testing CoinGecko API...")
        print(f"URL: {url}")

        response = requests.get(url, timeout=10)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ API Response successful!")
            print("Raw Response:")
            print(json.dumps(data, indent=2))

            # Check if tether data exists
            if "tether" in data:
                tether_data = data["tether"]
                if "usd" in tether_data:
                    price = tether_data["usd"]
                    print(f"✅ Tether Price Found: ${price}")
                    return True
                else:
                    print("❌ USD price not found in tether data")
            else:
                print("❌ Tether data not found in response")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Request Error: {str(e)}")

    return False

def test_brs_gold_api():
    """Test BRS API for gold prices"""
    url = "https://BrsApi.ir/Api/Market/Gold_Currency.php?key=B9PS4EgxiEgrngmuNdKa1xdgJybsp8Zi"

    try:
        print("\nTesting BRS Gold API...")
        print(f"URL: {url}")

        response = requests.get(url, timeout=10, verify=False)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ BRS API Response successful!")
            print("Raw Response:")
            print(json.dumps(data, indent=2))

            # Check for gold data
            if "gold" in data and isinstance(data["gold"], list):
                print("✅ Gold data found!")
                for item in data["gold"]:
                    if isinstance(item, dict):
                        symbol = item.get("symbol", "")
                        price = item.get("price", "")
                        print(f"Gold item: {symbol} = {price}")
            else:
                print("❌ Gold data structure not as expected")
        else:
            print(f"❌ API Error: {response.status_code}")

    except Exception as e:
        print(f"❌ Request Error: {str(e)}")

if __name__ == "__main__":
    print("=" * 50)
    print("API TEST SCRIPT")
    print("=" * 50)

    # Test CoinGecko API
    coingecko_success = test_coingecko_api()

    # Test BRS API
    test_brs_gold_api()

    print("\n" + "=" * 50)
    if coingecko_success:
        print("✅ CoinGecko API is working correctly!")
    else:
        print("❌ CoinGecko API has issues")
    print("=" * 50)
