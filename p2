import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import re

def scrape_dan_simpan_shopee(nama_barang):
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    
    try:
        print(f"Mencari {nama_barang} di Shopee...")
        driver.get("https://shopee.co.id/")
        time.sleep(6) # Memberikan waktu untuk menutup pop-up manual jika ada
        
        # Cari produk
        search_bar = driver.find_element(By.CSS_SELECTOR, "input.shopee-searchbar-input__input")
        search_bar.send_keys(nama_barang)
        search_bar.send_keys(Keys.ENTER)
        time.sleep(5)

        # Scroll ke bawah sedikit agar item termuat lebih banyak
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(3)
        
        items = driver.find_elements(By.CSS_SELECTOR, "div.col-xs-2-4")
        data_produk = []
        
        for item in items:
            try:
                nama = item.find_element(By.CSS_SELECTOR, "div[data-sqe='name']").text
                # Ambil teks harga (misal: "150.000")
                harga_raw = item.find_element(By.CSS_SELECTOR, "span[class*='ze48_m']").text
                
                # Membersihkan harga agar menjadi angka murni (integar) untuk sorting
                # Menghapus titik dan karakter non-angka
                harga_bersih = int(re.sub(r'\D', '', harga_raw))
                
                data_produk.append({
                    "Nama Produk": nama,
                    "Harga (Rp)": harga_bersih,
                    "Link": driver.current_url # Ini link halaman pencarian
                })
            except:
                continue

        # --- MENGOLAH DATA DENGAN PANDAS ---
        if data_produk:
            df = pd.DataFrame(data_produk)
            
            # Urutkan berdasarkan harga termurah
            df_sorted = df.sort_values(by="Harga (Rp)", ascending=True)
            
            # Simpan ke Excel
            nama_file = f"harga_promo_{nama_barang.replace(' ', '_')}.xlsx"
            df_sorted.to_excel(nama_file, index=False)
            
            print(f"\nBerhasil! Menemukan {len(df_sorted)} produk.")
            print(f"Data telah disimpan ke: {nama_file}")
            print("\n5 Produk Termurah:")
            print(df_sorted.head(5))
        else:
            print("Tidak ada data yang berhasil diambil.")

    finally:
        driver.quit()

# Jalankan
keyword = "Mouse Wireless"
scrape_dan_simpan_shopee(keyword)
