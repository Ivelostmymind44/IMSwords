# This code is written by Google Gemini
import requests
from bs4 import BeautifulSoup
import csv
import string
import time


def scrape_ims_dictionary():
    # ایجاد لیست حروف الفبا (a تا z) به همراه بخش 'elements' (عناصر)
    letters = list (string.ascii_lowercase) + ['elements']
    base_url = "https://fa.ims.ir/واژه-نامه/{}/"
    all_words = []

    print ("در حال شروع استخراج داده‌ها از سایت انجمن ریاضی ایران...")
    print ("-" * 50)

    for letter in letters:
        url = base_url.format (letter)
        print (f"در حال دریافت واژگان حرف: {letter.upper ()}")

        try:
            # استفاده از Header برای جلوگیری از مسدود شدن توسط سرور
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get (url, headers=headers, timeout=15)

            if response.status_code != 200:
                print (f"  خطا در دریافت {letter} (کد وضعیت: {response.status_code})")
                continue

            # تحلیل کدهای HTML صفحه
            soup = BeautifulSoup (response.text, 'html.parser')
            table = soup.find ('table')  # پیدا کردن جدول کلمات

            if not table:
                print (f"  جدولی برای حرف {letter} پیدا نشد.")
                continue

            # پیدا کردن تمام سطرهای جدول
            tbody = table.find ('tbody')
            rows = tbody.find_all ('tr') if tbody else table.find_all ('tr')[1:]

            extracted_count = 0
            for row in rows:
                cols = row.find_all (['td', 'th'])
                # اگر سطر حداقل شامل دو ستون (انگلیسی و فارسی) باشد
                if len (cols) >= 2:
                    english = cols[0].get_text (strip=True)
                    persian = cols[1].get_text (strip=True)

                    # استخراج ستون‌های اضافی (دانشنامه و پیشنهادات اعضا) در صورت وجود
                    extra_col1 = cols[2].get_text (strip=True) if len (cols) > 2 else ""
                    extra_col2 = cols[3].get_text (strip=True) if len (cols) > 3 else ""

                    if english:  # نادیده گرفتن سطرهای کاملا خالی
                        all_words.append ({
                            'English Word': english,
                            'Persian Translation': persian,
                            'Encyclopedia Translation': extra_col1,
                            'User Suggestion': extra_col2
                        })
                        extracted_count += 1

            print (f"  -> {extracted_count} واژه استخراج شد.")

            # ایجاد وقفه یک ثانیه‌ای برای فشار نیاوردن به سرور سایت
            time.sleep (1)

        except Exception as e:
            print (f"  خطا در پردازش حرف '{letter}': {e}")

    # ذخیره داده‌ها در فایل CSV
    if all_words:
        filename = "ims_dictionary.csv"
        # استفاده از utf-8-sig برای پشتیبانی کامل اکسل از حروف فارسی
        with open (filename, mode='w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter (f, fieldnames=['English Word', 'Persian Translation', 'Encyclopedia Translation',
                                                    'User Suggestion'])
            writer.writeheader ()
            writer.writerows (all_words)

        print ("-" * 50)
        print (f"استخراج با موفقیت به پایان رسید! کل واژگان ({len (all_words)} کلمه) در فایل '{filename}' ذخیره شدند.")
    else:
        print ("هیچ واژه‌ای استخراج نشد. ممکن است ساختار سایت تغییر کرده باشد.")


if __name__ == "__main__":
    scrape_ims_dictionary ()
