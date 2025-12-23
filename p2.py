import sys

# --- PATCH UNTUK PYTHON 3.12+ ---
try:
    from distutils.version import LooseVersion
except ImportError:
    from packaging.version import Version as LooseVersion
    import distutils
    import distutils.version
    distutils.version.LooseVersion = LooseVersion
# --------------------------------

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re

def scrape_shopee_to_excel(keyword, limit_produk=20):
    # Konfigurasi Browser
    options = uc.ChromeOptions()
    # options.add_argument('--headless') # Aktifkan jika tidak ingin melihat jendela browser
    
    driver = uc.Chrome(options=options)
    
    try:
        print(f"Membuka Shopee untuk mencari: {keyword}...")
        driver.get("https://shopee.co.id/")
        
        # Menunggu halaman utama terbuka (max 10 detik)
        wait = WebDriverWait(driver, 10)
        
        # Cari kotak pencarian
        search_bar = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.shopee-searchbar-input__input")))
        search_bar.send_keys(keyword)
        search_bar.send_keys(Keys.ENTER)
        
        print("Menunggu hasil pencarian... (Selesaikan captcha jika muncul)")
        time.sleep(7) # Waktu untuk loading produk & scroll manual jika ada captcha

        # Scroll perlahan agar produk termuat (Lazy Load)
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

        # Ambil semua container produk
        items = driver.find_elements(By.CSS_SELECTOR, "div.col-xs-2-4")
        
        hasil_data = []
        
        for item in items[:limit_produk]:
            try:
                # Ambil Nama
                nama = item.find_element(By.CSS_SELECTOR, "div[data-sqe='name']").text
                
                # Ambil Harga (Shopee sering pakai class dinamis, kita pakai selector yang umum)
                harga_raw = item.find_element(By.CSS_SELECTOR, "span[class*='ze48_m']").text
                
                # Bersihkan harga (Hapus 'Rp' dan titik)
                harga_angka = int(re.sub(r'\D', '', harga_raw))
                
                # Ambil Link Produk
                link_produk = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                hasil_data.append({
                    "Nama Produk": nama,
                    "Harga (Rp)": harga_angka,
                    "Link": link_produk
                })
            except Exception:
                continue

        # Proses dengan Pandas
        if hasil_data:
            df = pd.DataFrame(hasil_data)
            
            # Urutkan dari yang termurah
            df_sorted = df.sort_values(by="Harga (Rp)", ascending=True)
            
            # Simpan ke Excel
            filename = f"promo_{keyword.replace(' ', '_')}.xlsx"
            df_sorted.to_excel(filename, index=False)
            
            print("-" * 30)
            print(f"BERHASIL!")
            print(f"Total produk ditemukan: {len(df_sorted)}")
            print(f"File tersimpan sebagai: {filename}")
            print("-" * 30)
            print("5 Produk Termurah:")
            print(df_sorted.head(5))
        else:
            print("Gagal mengambil data. Coba cek apakah ada Captcha di layar browser.")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        
    finally:
        print("\nMenutup browser dalam 5 detik...")
        time.sleep(5)
        driver.quit()

# --- JALANKAN PROGRAM ---
if __name__ == "__main__":
    # Ganti keyword sesuai keinginanmu
    cari_barang = "SSD NVME 512GB" 
    scrape_shopee_to_excel(cari_barang)
