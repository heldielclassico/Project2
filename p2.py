import sys
import os

# --- PATCH UNTUK PYTHON 3.12+ (LooseVersion Error) ---
try:
    from distutils.version import LooseVersion
except ImportError:
    from packaging.version import Version as LooseVersion
    import distutils
    import distutils.version
    distutils.version.LooseVersion = LooseVersion

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re

def scrape_shopee(keyword, limit=15):
    options = uc.ChromeOptions()
    
    # --- PENGATURAN AGAR TIDAK ERROR DI LINUX/SERVER ---
    if sys.platform == "linux" or sys.platform == "linux2":
        options.add_argument('--headless') # Jalankan tanpa jendela (wajib di server)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Jika Chrome terinstal di lokasi standar Linux
        if os.path.exists("/usr/bin/google-chrome"):
            options.binary_location = "/usr/bin/google-chrome"
    
    # Jika di Windows dan Chrome tidak ketemu, aktifkan baris di bawah ini:
    # options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    try:
        driver = uc.Chrome(options=options)
        print(f"Mencari produk: {keyword}...")
        
        driver.get("https://shopee.co.id/")
        wait = WebDriverWait(driver, 20)
        
        # Cari kotak input
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.shopee-searchbar-input__input")))
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)
        
        time.sleep(10) # Waktu tunggu untuk loading & bypass bot detection
        
        # Scroll otomatis agar item muncul
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

        items = driver.find_elements(By.CSS_SELECTOR, "div.col-xs-2-4")
        data_list = []

        for item in items[:limit]:
            try:
                nama = item.find_element(By.CSS_SELECTOR, "div[data-sqe='name']").text
                harga_raw = item.find_element(By.CSS_SELECTOR, "span[class*='ze48_m']").text
                
                # Pembersihan harga ke angka
                harga_angka = int(re.sub(r'\D', '', harga_raw))
                link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                data_list.append({
                    "Nama": nama,
                    "Harga (Rp)": harga_angka,
                    "Link": link
                })
            except:
                continue

        if data_list:
            df = pd.DataFrame(data_list)
            df = df.sort_values(by="Harga (Rp)", ascending=True) # Urutkan termurah
            
            # Simpan ke Excel
            filename = f"hasil_{keyword.replace(' ', '_')}.xlsx"
            df.to_excel(filename, index=False)
            
            print(f"\nSelesai! {len(df)} produk disimpan ke {filename}")
            print(df.head())
        else:
            print("Gagal mengambil data. Cek apakah ada Captcha di browser.")

    except Exception as e:
        print(f"Error terjadi: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    kata_kunci = "Mouse Logitech"
    scrape_shopee(kata_kunci)
