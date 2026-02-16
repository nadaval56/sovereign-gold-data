#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fetch gold price and USD/ILS rate daily
Updates gold-data.json for sovereign gold calculator
"""

import requests
import json
from datetime import datetime

# הגדרות API
GOLD_API_KEY = 'goldapi-kxvn5yly5b34xpl-io'  # API key חינמי מ-goldapi.io
GOLD_API_URL = 'https://www.goldapi.io/api/XAU/USD'
USD_ILS_URL = 'https://api.exchangerate-api.com/v4/latest/USD'

# קבועים של סוברין
SOVEREIGN_PURE_GOLD_GRAMS = 7.32
TROY_OZ_TO_GRAMS = 31.1034768

def get_gold_price():
    """שלוף מחיר זהב מ-GoldAPI"""
    headers = {
        'x-access-token': GOLD_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Fetching gold price from {GOLD_API_URL}...")
        response = requests.get(GOLD_API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'price' in data:
            print(f"✅ Gold price: ${data['price']}/oz")
            return data['price']
        else:
            print(f"❌ Unexpected response format: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching gold price: {e}")
        return None

def get_usd_ils_rate():
    """שלוף שער דולר-שקל"""
    try:
        print(f"Fetching USD/ILS rate from {USD_ILS_URL}...")
        response = requests.get(USD_ILS_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'rates' in data and 'ILS' in data['rates']:
            rate = data['rates']['ILS']
            print(f"✅ USD/ILS rate: {rate}")
            return rate
        else:
            print(f"❌ Unexpected response format: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching USD/ILS rate: {e}")
        return None

def calculate_sovereign_value(gold_price_usd, usd_ils):
    """חשב ערך סוברין בשקלים"""
    gold_price_per_gram = gold_price_usd / TROY_OZ_TO_GRAMS
    sovereign_value_usd = gold_price_per_gram * SOVEREIGN_PURE_GOLD_GRAMS
    sovereign_value_ils = sovereign_value_usd * usd_ils
    
    now = datetime.now()
    
    return {
        'gold_price_oz_usd': round(gold_price_usd, 2),
        'gold_price_gram_usd': round(gold_price_per_gram, 2),
        'usd_ils_rate': round(usd_ils, 4),
        'sovereign_value_ils': round(sovereign_value_ils, 2),
        'sovereign_value_usd': round(sovereign_value_usd, 2),
        'sovereign_gold_grams': SOVEREIGN_PURE_GOLD_GRAMS,
        'last_updated': now.strftime('%Y-%m-%d %H:%M:%S'),
        'last_updated_hebrew': now.strftime('%d.%m.%Y, %H:%M'),
        'last_updated_timestamp': int(now.timestamp())
    }

def load_previous_data():
    """טען נתונים קודמים אם קיימים"""
    try:
        with open('gold-data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("ℹ️  No previous data found")
        return None
    except json.JSONDecodeError as e:
        print(f"⚠️  Error reading previous data: {e}")
        return None

def save_data(data):
    """שמור נתונים ל-JSON"""
    try:
        with open('gold-data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✅ Data saved to gold-data.json")
        return True
    except Exception as e:
        print(f"❌ Error saving data: {e}")
        return False

def main():
    print("=" * 60)
    print("🪙 Sovereign Gold Price Updater")
    print("=" * 60)
    
    # טען נתונים קודמים
    previous_data = load_previous_data()
    
    # שלוף נתונים חדשים
    gold_price = get_gold_price()
    usd_ils = get_usd_ils_rate()
    
    if gold_price and usd_ils:
        print(f"\n📊 Current Data:")
        print(f"   Gold: ${gold_price}/oz")
        print(f"   USD/ILS: ₪{usd_ils}")
        
        # חשב ערך סוברין
        data = calculate_sovereign_value(gold_price, usd_ils)
        
        print(f"\n💰 Sovereign Value:")
        print(f"   ILS: ₪{data['sovereign_value_ils']}")
        print(f"   USD: ${data['sovereign_value_usd']}")
        
        # בדוק אם יש שינוי משמעותי
        if previous_data:
            prev_value = previous_data.get('sovereign_value_ils', 0)
            new_value = data['sovereign_value_ils']
            change = new_value - prev_value
            change_pct = (change / prev_value * 100) if prev_value > 0 else 0
            
            print(f"\n📈 Change from last update:")
            print(f"   {change:+.2f} ₪ ({change_pct:+.2f}%)")
        
        # שמור נתונים
        if save_data(data):
            print("\n✅ Update completed successfully!")
            return 0
        else:
            print("\n❌ Failed to save data")
            return 1
    else:
        print("\n❌ Failed to fetch required data")
        
        # אם יש נתונים קודמים, שמור אותם שוב עם timestamp מעודכן
        if previous_data:
            print("ℹ️  Using previous data as fallback")
            previous_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            previous_data['last_updated_hebrew'] = datetime.now().strftime('%d.%m.%Y, %H:%M')
            save_data(previous_data)
        
        return 1

if __name__ == '__main__':
    exit(main())
