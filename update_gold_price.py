#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fetch gold and silver prices daily
Updates gold-data.json with both precious metals data
Includes: Sovereign gold value + Half-Shekel silver value
"""

import requests
import json
import os
from datetime import datetime

# הגדרות API - ה-keys נשלפים מ-GitHub Secrets!
GOLD_API_KEY = os.environ.get('GOLD_API_KEY', '')
GOLD_API_URL = 'https://www.goldapi.io/api/XAU/USD'
SILVER_API_URL = 'https://www.goldapi.io/api/XAG/USD'  # XAG = Silver

# אפשרות חלופית: Metals-API
METALS_API_KEY = os.environ.get('METALS_API_KEY', '')
METALS_GOLD_URL = 'https://api.metals.live/v1/spot/gold'
METALS_SILVER_URL = 'https://api.metals.live/v1/spot/silver'

USD_ILS_URL = 'https://api.exchangerate-api.com/v4/latest/USD'

# בחר איזה API להשתמש
USE_METALS_API = False  # False = GoldAPI, True = MetalsAPI

# קבועים
TROY_OZ_TO_GRAMS = 31.1034768
SOVEREIGN_PURE_GOLD_GRAMS = 7.32  # סוברין - 7.32 גרם זהב טהור (22 קראט)
HALF_SHEKEL_OPINION_A = 9.0       # מחצית השקל - דעה א': 9 גרם כסף
HALF_SHEKEL_OPINION_B = 9.6       # מחצית השקל - דעה ב': 9.6 גרם כסף

def get_gold_price():
    """שלוף מחיר זהב"""
    if USE_METALS_API:
        # Metals-API
        try:
            url = f"{METALS_GOLD_URL}?access_key={METALS_API_KEY}"
            print(f"Fetching gold price from Metals-API...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'success' in data and data['success'] and 'rate' in data:
                price = data['rate']
                print(f"✅ Gold price: ${price}/oz")
                return price
            else:
                print(f"❌ Unexpected response format: {data}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching gold price: {e}")
            return None
    else:
        # GoldAPI
        headers = {
            'x-access-token': GOLD_API_KEY,
            'Content-Type': 'application/json'
        }
        
        try:
            print(f"Fetching gold price from GoldAPI...")
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

def get_silver_price():
    """שלוף מחיר כסף"""
    if USE_METALS_API:
        # Metals-API
        try:
            url = f"{METALS_SILVER_URL}?access_key={METALS_API_KEY}"
            print(f"Fetching silver price from Metals-API...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'success' in data and data['success'] and 'rate' in data:
                price = data['rate']
                print(f"✅ Silver price: ${price}/oz")
                return price
            else:
                print(f"❌ Unexpected response format: {data}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching silver price: {e}")
            return None
    else:
        # GoldAPI - תומך גם בכסף!
        headers = {
            'x-access-token': GOLD_API_KEY,
            'Content-Type': 'application/json'
        }
        
        try:
            print(f"Fetching silver price from GoldAPI...")
            response = requests.get(SILVER_API_URL, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'price' in data:
                print(f"✅ Silver price: ${data['price']}/oz")
                return data['price']
            else:
                print(f"❌ Unexpected response format: {data}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching silver price: {e}")
            return None

def get_usd_ils_rate():
    """שלוף שער דולר-שקל"""
    try:
        print(f"Fetching USD/ILS rate...")
        response = requests.get(USD_ILS_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'rates' in data and 'ILS' in data['rates']:
            rate = data['rates']['ILS']
            print(f"✅ USD/ILS rate: ₪{rate}")
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
    
    return {
        'gold_price_oz_usd': round(gold_price_usd, 2),
        'gold_price_gram_usd': round(gold_price_per_gram, 2),
        'sovereign_value_ils': round(sovereign_value_ils, 2),
        'sovereign_value_usd': round(sovereign_value_usd, 2),
        'sovereign_gold_grams': SOVEREIGN_PURE_GOLD_GRAMS
    }

def calculate_half_shekel(silver_price_usd, usd_ils):
    """חשב ערך מחצית השקל - שתי דעות"""
    silver_price_per_gram = silver_price_usd / TROY_OZ_TO_GRAMS
    
    # דעה א': 9 גרם כסף
    half_shekel_9g_usd = silver_price_per_gram * HALF_SHEKEL_OPINION_A
    half_shekel_9g_ils = half_shekel_9g_usd * usd_ils
    
    # דעה ב': 9.6 גרם כסף
    half_shekel_96g_usd = silver_price_per_gram * HALF_SHEKEL_OPINION_B
    half_shekel_96g_ils = half_shekel_96g_usd * usd_ils
    
    return {
        'silver_price_oz_usd': round(silver_price_usd, 2),
        'silver_price_gram_usd': round(silver_price_per_gram, 2),
        'half_shekel_9g_ils': round(half_shekel_9g_ils, 2),
        'half_shekel_9g_usd': round(half_shekel_9g_usd, 2),
        'half_shekel_96g_ils': round(half_shekel_96g_ils, 2),
        'half_shekel_96g_usd': round(half_shekel_96g_usd, 2)
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
    print("💰 Gold & Silver Price Updater")
    print("=" * 60)
    
    # טען נתונים קודמים
    previous_data = load_previous_data()
    
    # שלוף נתונים חדשים
    gold_price = get_gold_price()
    silver_price = get_silver_price()
    usd_ils = get_usd_ils_rate()
    
    if gold_price and silver_price and usd_ils:
        print(f"\n📊 Current Data:")
        print(f"   Gold:   ${gold_price}/oz")
        print(f"   Silver: ${silver_price}/oz")
        print(f"   USD/ILS: ₪{usd_ils}")
        
        # חשב ערכים
        sovereign_data = calculate_sovereign_value(gold_price, usd_ils)
        half_shekel_data = calculate_half_shekel(silver_price, usd_ils)
        
        # שלב הכל
        now = datetime.now()
        data = {
            **sovereign_data,
            **half_shekel_data,
            'usd_ils_rate': round(usd_ils, 4),
            'last_updated': now.strftime('%Y-%m-%d %H:%M:%S'),
            'last_updated_hebrew': now.strftime('%d.%m.%Y, %H:%M'),
            'last_updated_timestamp': int(now.timestamp())
        }
        
        print(f"\n💰 Calculated Values:")
        print(f"   Sovereign (7.32g gold): ₪{data['sovereign_value_ils']}")
        print(f"   Half-Shekel 9g silver:  ₪{data['half_shekel_9g_ils']}")
        print(f"   Half-Shekel 9.6g silver: ₪{data['half_shekel_96g_ils']}")
        
        # בדוק שינויים
        if previous_data:
            changes = []
            if 'sovereign_value_ils' in previous_data:
                change = data['sovereign_value_ils'] - previous_data['sovereign_value_ils']
                changes.append(f"Sovereign: {change:+.2f} ₪")
            if 'half_shekel_9g_ils' in previous_data:
                change = data['half_shekel_9g_ils'] - previous_data['half_shekel_9g_ils']
                changes.append(f"Half-Shekel (9g): {change:+.2f} ₪")
            
            if changes:
                print(f"\n📈 Changes from last update:")
                for change in changes:
                    print(f"   {change}")
        
        # שמור נתונים
        if save_data(data):
            print("\n✅ Update completed successfully!")
            return 0
        else:
            print("\n❌ Failed to save data")
            return 1
    else:
        print("\n❌ Failed to fetch required data")
        
        # Fallback - שמור נתונים קודמים עם timestamp מעודכן
        if previous_data:
            print("ℹ️  Using previous data as fallback")
            previous_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            previous_data['last_updated_hebrew'] = datetime.now().strftime('%d.%m.%Y, %H:%M')
            save_data(previous_data)
        
        return 1

if __name__ == '__main__':
    exit(main())
