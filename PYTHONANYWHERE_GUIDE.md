# راهنمای نصب ربات تلگرام Shazam روی PythonAnywhere

## مقدمه
این راهنما به شما نشان می‌دهد که چگونه ربات تلگرام Shazam را روی PythonAnywhere نصب و راه‌اندازی کنید. PythonAnywhere یک پلتفرم ابری برای اجرای برنامه‌های پایتون است.

## پیش‌نیازها
1. حساب کاربری PythonAnywhere (حساب رایگان کافی است)
2. توکن ربات تلگرام (از @BotFather)
3. فایل‌های پروژه ربات

## مرحله ۱: آپلود فایل‌ها روی PythonAnywhere

### ۱.۱ ورود به PythonAnywhere
1. به [pythonanywhere.com](https://www.pythonanywhere.com) وارد شوید
2. وارد حساب کاربری خود شوید

### ۱.۲ آپلود فایل‌ها
1. به تب **Files** بروید
2. به مسیر `/home/your_username/` بروید
3. دکمه **Upload a file** را بزنید
4. فایل‌های زیر را آپلود کنید:
   - `shazam_bot.py`
   - `requirements.txt`

## مرحله ۲: تنظیم توکن ربات

### ۲.۱ ویرایش فایل ربات
1. در تب **Files**، فایل `shazam_bot.py` را باز کنید
2. خط زیر را پیدا کنید:
   ```python
   BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```
3. `YOUR_BOT_TOKEN_HERE` را با توکن واقعی ربات خود جایگزین کنید
4. فایل را ذخیره کنید (Ctrl+S)

### ۲.۲ تنظیم کاربر ادمین (اختیاری)
اگر می‌خواهید کاربر ادمین تنظیم کنید:
1. خط زیر را پیدا کنید:
   ```python
   ADMIN_USER_ID = None
   ```
2. `None` را با شناسه عددی کاربری خود در تلگرام جایگزین کنید
3. فایل را ذخیره کنید

## مرحله ۳: نصب پکیج‌های مورد نیاز

### ۳.۱ باز کردن کنسول
1. به تب **Consoles** بروید
2. دکمه **Start a new console** را بزنید
3. **Bash** را انتخاب کنید

### ۳.۲ نصب پکیج‌ها
در کنسول باز شده، دستورات زیر را وارد کنید:

```bash
# نصب پکیج‌ها از فایل requirements.txt
pip install -r requirements.txt

# نصب پکیج‌های اضافی برای پشتیبانی از فایل‌های صوتی
pip install python-telegram-bot aiohttp shazamio
```

## مرحله ۴: تست ربات

### ۴.۱ اجرای دستی ربات
در کنسول bash، دستور زیر را اجرا کنید:

```bash
python3 shazam_bot.py
```

اگر همه چیز درست باشد، باید پیامی مانند این ببینید:
```
2024-XX-XX XX:XX:XX - __main__ - INFO - Starting bot...
```

### ۴.۲ تست ربات در تلگرام
1. به تلگرام بروید
2. ربات خود را پیدا کنید (@your_bot_username)
3. دستور `/start` را ارسال کنید
4. باید پیام خوشامدگویی را ببینید

برای متوقف کردن ربات، `Ctrl+C` را فشار دهید.

## مرحله ۵: راه‌اندازی خودکار ربات

### ۵.۱ ایجاد فایل اجرایی
1. در تب **Files**، دکمه **New file** را بزنید
2. نام فایل را `run_bot.py` بگذارید
3. محتوای زیر را کپی کنید:

```python
#!/usr/bin/env python3
import subprocess
import sys
import os
import signal
import time

def run_bot():
    """Run the Shazam bot"""
    try:
        # Change to the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Run the bot
        subprocess.run([sys.executable, 'shazam_bot.py'])
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}")
        time.sleep(5)  # Wait before retrying
        run_bot()  # Restart the bot

if __name__ == '__main__':
    run_bot()
```

4. فایل را ذخیره کنید

### ۵.۲ تنظیم Scheduled Task
1. به تب **Tasks** بروید
2. دکمه **Set up a new scheduled task** را بزنید
3. تنظیمات زیر را وارد کنید:
   - **Description**: `Shazam Telegram Bot`
   - **Command**: `/home/your_username/run_bot.py`
   - **Frequency**: `Daily`
   - **Hour**: `00`
   - **Minute**: `00`
4. دکمه **Create** را بزنید

### ۵.۳ تنظیم Always-on Task (حساب‌های پولی)
اگر حساب پولی PythonAnywhere دارید:
1. به تب **Tasks** بروید
2. به بخش **Always-on tasks** بروید
3. دکمه **Add an always-on task** را بزنید
4. تنظیمات زیر را وارد کنید:
   - **Description**: `Shazam Telegram Bot`
   - **Command**: `/home/your_username/run_bot.py`
   - **Timeout**: `24 hours`
5. دکمه **Create** را بزنید

## مرحله ۶: مانیتورینگ و لاگ‌ها

### ۶.۱ مشاهده لاگ‌ها
1. به تب **Files** بروید
2. فایل `.bashrc` را باز کنید
3. خط زیر را به انتهای فایل اضافه کنید:
   ```bash
   export PYTHONPATH=/home/your_username:$PYTHONPATH
   ```
4. فایل را ذخیره کنید

### ۶.۲ ایجاد فایل لاگ
1. در تب **Files**، دکمه **New file** را بزنید
2. نام فایل را `bot_log.py` بگذارید
3. محتوای زیر را کپی کنید:

```python
#!/usr/bin/env python3
import logging
import sys
import os
from datetime import datetime

# Set up logging
log_file = '/home/your_username/bot.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Redirect stdout and stderr to log file
sys.stdout = open(log_file, 'a')
sys.stderr = open(log_file, 'a')

print(f"Bot started at {datetime.now()}")
```

4. فایل را ذخیره کنید

### ۶.۳ مشاهده لاگ‌ها
برای مشاهده لاگ‌های ربات:
1. به تب **Consoles** بروید
2. یک کنسول **Bash** جدید باز کنید
3. دستور زیر را اجرا کنید:
   ```bash
   tail -f /home/your_username/bot.log
   ```

## مرحله ۷: عیب‌یابی

### ۷.۱ مشکلات رایج

#### مشکل: ربات اجرا نمی‌شود
**راه‌حل:**
1. مطمئن شوید توکن ربات صحیح است
2. پکیج‌ها را دوباره نصب کنید:
   ```bash
   pip install --upgrade python-telegram-bot aiohttp shazamio
   ```

#### مشکل: خطای Permission denied
**راه‌حل:**
1. مطمئن شوید فایل‌ها در مسیر صحیح هستند
2. دسترسی فایل‌ها را بررسی کنید

#### مشکل: ربات پس از مدتی متوقف می‌شود
**راه‌حل:**
1. برای حساب‌های رایگان، این طبیعی است
2. از Scheduled Task برای راه‌اندازی مجدد استفاده کنید
3. برای حساب‌های پولی، از Always-on task استفاده کنید

### ۷.۲ راه‌حل‌های پیشرفته

#### استفاده از systemd (حساب‌های پولی)
اگر به دسترسی ssh دارید:
1. فایل سرویس ایجاد کنید:
   ```bash
   nano /home/your_username/shazam-bot.service
   ```
2. محتوای زیر را اضافه کنید:
   ```ini
   [Unit]
   Description=Shazam Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=your_username
   WorkingDirectory=/home/your_username
   ExecStart=/usr/bin/python3 /home/your_username/shazam_bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```
3. سرویس را فعال کنید:
   ```bash
   systemctl --user enable shazam-bot.service
   systemctl --user start shazam-bot.service
   ```

## مرحله ۸: به‌روزرسانی ربات

### ۸.۱ به‌روزرسانی کد
1. فایل‌های جدید را آپلود کنید
2. در کنسول bash، ربات را متوقف کنید:
   ```bash
   pkill -f shazam_bot.py
   ```
3. ربات را دوباره اجرا کنید:
   ```bash
   python3 shazam_bot.py
   ```

### ۸.۲ به‌روزرسانی پکیج‌ها
در کنسول bash:
```bash
pip install --upgrade -r requirements.txt
```

## نکات نهایی

1. **حساب رایگان**: در حساب‌های رایگان PythonAnywhere، ربات شما ممکن است هر 24 ساعت متوقف شود و نیاز به راه‌اندازی مجدد داشته باشد.
2. **منابع**: ربات منابع زیادی مصرف نمی‌کند، اما برای عملکرد بهتر، حساب پولی توصیه می‌شود.
3. **امنیت**: توکن ربات خود را در دسترس دیگران قرار ندهید.
4. **پشتیبان‌گیری**: همیشه از فایل‌های خود پشتیبان بگیرید.

## پشتیبانی
اگر در راه‌اندازی ربات با مشکلی مواجه شدید:
1. لاگ‌ها را بررسی کنید
2. مطمئن شوید تمام مراحل را به درستی انجام داده‌اید
3. در صورت نیاز، با پشتیبانی PythonAnywhere تماس بگیرید

موفق باشید! 🎵🤖