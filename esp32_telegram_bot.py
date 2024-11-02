from datetime import datetime
import os
import sys
import subprocess
import importlib
import platform
import time
from colorama import init, Fore, Style
import requests
import pandas as pd
from telegram import Bot, Update , KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, JobQueue ,filters ,MessageHandler
import asyncio

# راه‌اندازی Colorama
init(autoreset=True)

# توکن ربات تلگرام
TELEGRAM_TOKEN = "Your Telegram-Bot Token"
# شناسه ادمین‌ها
ADMIN_IDS = [381200758]  # به جای 123456789 شناسه ادمین‌ها را قرار دهید

def auto_lib_downloader(libs):
    osnames = platform.system()
    python_executable = sys.executable  

    for lib in libs:
        try:
            importlib.import_module(lib)
            print(Fore.GREEN + f"[+] Library '{lib}' has been imported successfully.")
        except ImportError:
            print(Fore.YELLOW + f"[-] Library '{lib}' is not installed.")
            print(Fore.CYAN + f"[/] Downloading library '{lib}'...")

            result = subprocess.run(
                [python_executable, "-m", "pip", "install", lib],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                print(Fore.GREEN + f"[++] Library '{lib}' has been successfully installed and imported.")
            else:
                print(Fore.RED + f"[!!] Failed to install '{lib}'. Error:\n{result.stderr}")

    print(Fore.GREEN + "[++] All libraries have been processed.")

# تابع پاکسازی صفحه
def clear():
    osnames = platform.system()
    subprocess.run(['cls' if osnames == "Windows" else 'clear'], shell=True)
    
auto_lib_downloader(['pandas', 'openpyxl', 'requests', 'colorama', 'python-telegram-bot', 'python-telegram-bot[job-queue]','matplotlib'])
import matplotlib.pyplot as plt
clear()

# آدرس ESP32 و مسیر ذخیره فایل‌ها
esp32_ip = "http://192.168.1.115/data"
output_directory = "Z:\\ESP32"

# تابع لاگ کردن درخواست‌ها
def log_user_request(update, request_type, request_data):
    try:
        user = update.effective_user
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"user_requests_{today}.xlsx"
        full_path = os.path.join(output_directory, filename)

        df = pd.DataFrame([{
            "User ID": user.id,
            "Username": user.username,
            "Full Name": f"{user.first_name} {user.last_name}",
            "Request Type": request_type,
            "Request Data": request_data,
            "Date": today,
            "Time": datetime.now().strftime("%H:%M:%S")
        }])

        try:
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            if os.path.exists(full_path):
                existing_df = pd.read_excel(full_path)
                df = pd.concat([existing_df, df], ignore_index=True)

            df.to_excel(full_path, index=False)
            print(Fore.GREEN + f"[+] User request logged in {full_path}.")
        except Exception as e:
            print(Fore.RED + f"[-] Failed to log user request: {e}")
    except Exception as e:
        print(Fore.RED + f"[-] Error def log_user_request(update, request_type, request_data): {e}")

# تابع دریافت اطلاعات از ESP32
def fetch_data():
    try:
        response = requests.get(esp32_ip, timeout=30)
        response.raise_for_status()
        data = response.json()
        if all(key in data for key in ["time", "date", "temperature", "humidity", "buy_price", "sell_price", "ping", "devices"]):
            return data
        else:
            print(Fore.RED + "[-] Invalid data structure received from ESP32.")
            return None
    except requests.RequestException as e:
        print(Fore.RED + f"[-] Error fetching data: {e}")
        return None

# تابع دریافت IP عمومی
def fetch_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=30)
        response.raise_for_status()
        return response.json().get("ip", "N/A")
    except requests.RequestException as e:
        print(Fore.RED + f"[-] Error fetching public IP: {e}")
        return "N/A"

# تابع ذخیره داده‌ها در فایل اکسل
def save_to_excel(data):
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"data_log_{today}.xlsx"
        full_path = os.path.join(output_directory, filename)

        readable_date = datetime.fromtimestamp(int(data["date"])).strftime("%Y-%m-%d")
        df = pd.DataFrame([{
            "Time": data["time"],
            "Date": readable_date,
            "Temperature": data["temperature"],
            "Humidity": data["humidity"],
            "Buy Price": data["buy_price"],
            "Sell Price": data["sell_price"],
            "Ping": "Success" if data["ping"] else "Failed",
            "Devices": data["devices"]
        }])

        try:
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            if os.path.exists(full_path):
                existing_df = pd.read_excel(full_path)
                df = pd.concat([existing_df, df], ignore_index=True)

            df.to_excel(full_path, index=False)
            print(Fore.GREEN + f"[+] Data saved to {full_path}.")
        except Exception as e:
            print(Fore.RED + f"[-] Failed to save data to Excel: {e}")
    except Exception as e:
        print(Fore.RED + f"[-] Error def save_to_excel(data): {e}")

# تابع پردازش دستور /esp32 از کاربر
async def esp32_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = fetch_data()
        if data:
            public_ip = fetch_public_ip()  # دریافت IP عمومی
            save_to_excel(data)
            log_user_request(update, "esp32", "Fetch ESP32 data")  # لاگ درخواست کاربر
            message = f"""
            🕒 **Time:** {data["time"]}
            📅 **Date:** {datetime.fromtimestamp(int(data["date"])).strftime("%Y-%m-%d")}
            🌡️ **Temperature:** {data["temperature"]}
            💧 **Humidity:** {data["humidity"]}
            💲 **Buy Price:** {data["buy_price"]}
            💵 **Sell Price:** {data["sell_price"]}
            📶 **Ping:** {"Success" if data["ping"] else "Failed"}
            📡 **Devices Connected:** {data["devices"]}
            🌐 **Public IP:** {public_ip}
            """
            try:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='Markdown')
                print(Fore.GREEN + "[+] Data sent to Telegram successfully.")
            except Exception as e:
                print(Fore.RED + f"[-] Error sending data to Telegram: {e}")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="No data available from ESP32.")
    except Exception as e:
        print(Fore.RED + f"[-] Error async def esp32_command(update: Update, context: ContextTypes.DEFAULT_TYPE): {e}")
# تابع تولید و ارسال نمودار
async def send_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"data_log_{today}.xlsx"
        full_path = os.path.join(output_directory, filename)

        if os.path.exists(full_path):
            # خواندن داده‌های دما و رطوبت
            df = pd.read_excel(full_path)
            times = df["Time"]
            temperatures = df["Temperature"]
            humidities = df["Humidity"]

            # تولید نمودار
            plt.figure(figsize=(10, 5))
            plt.plot(times, temperatures, label="Temperature (°C)", color="red")
            plt.plot(times, humidities, label="Humidity (%)", color="blue")
            plt.xlabel("Time")
            plt.ylabel("Value")
            plt.title("Temperature and Humidity Over Time")
            plt.legend()
            chart_path = os.path.join(output_directory, "chart.png")
            plt.savefig(chart_path)
            plt.close()

            # ارسال نمودار به تلگرام
            with open(chart_path, 'rb') as file:
                try:
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=file, caption="Temperature and Humidity Chart")
                    log_user_request(update, "chart", "Retrieve today's chart PNG")  # لاگ درخواست کاربر
                    print(Fore.GREEN + "[+] Chart sent to Telegram successfully.")
                except Exception as e:
                    log_user_request(update, "chart", "Not Retrieve today's chart PNG")  # لاگ درخواست کاربر
                    print(Fore.RED + f"[-] Error sending chart to Telegram: {e}")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="No data file available for today.")
    except Exception as e:
        print(Fore.RED + f"[-] Error async def send_chart(update: Update, context: ContextTypes.DEFAULT_TYPE): {e}")


# تابع پردازش دستور /esp32_all از کاربر
async def esp32_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"data_log_{today}.xlsx"
        full_path = os.path.join(output_directory, filename)

        if os.path.exists(full_path):
            with open(full_path, 'rb') as file:
                try:
                    await context.bot.send_document(chat_id=update.effective_chat.id, document=file, caption="Here's the Excel file for today's data.")
                    log_user_request(update, "esp32_all", "Retrieve today's Excel file")  # لاگ درخواست کاربر
                    print(Fore.GREEN + "[+] Excel file sent to Telegram successfully.")
                except Exception as e:
                    print(Fore.RED + f"[-] Error sending Excel file to Telegram: {e}")
                    log_user_request(update, "esp32_all", "Not Retrieve today's Excel file")  # لاگ درخواست کاربر
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="No data file available for today.")
    except Exception as e:
        print(Fore.RED + f"[-] Error async def esp32_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE): {e}")

# تابع ذخیره اطلاعات به صورت خودکار هر دقیقه
async def scheduled_fetch_and_save(context: ContextTypes.DEFAULT_TYPE):
    try:
        data = fetch_data()
        if data:
            save_to_excel(data)
            print(Fore.GREEN + "[+] Data fetched and saved automatically.")
        else:
            print(Fore.YELLOW + "[*] No data fetched; attempting to save offline data.")
    except Exception as e:
        print(Fore.RED + f"[-] Error async def scheduled_fetch_and_save(context: ContextTypes.DEFAULT_TYPE): {e}")
        
# توابع مدیریت ادمین‌ها
async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # بررسی اینکه آیا کاربر ادمین است
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("این قابلیت فقط برای ادمین‌ها قابل دسترسی است.")
            log_user_request(update, "admin", "you are not admin")  # لاگ درخواست کاربر
            return

        # ایجاد کیبورد دکمه‌ای برای ادمین‌ها
        keyboard = [
            [KeyboardButton("📂 ارسال کل فایل‌های اکسل"), KeyboardButton("📂 ارسال کل فایل‌های لاگ")],
            [KeyboardButton("📜 نمایش لاگ‌ها به صورت متن")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text("لطفاً یکی از گزینه‌ها را انتخاب کنید:", reply_markup=reply_markup)
        log_user_request(update, "admin", "you are admin")  # لاگ درخواست کاربر
    except Exception as e:
        print(Fore.RED + f"[-] Error async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE): {e}")
        

# تابع ارسال کل فایل‌های اکسل
async def send_all_excel_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id not in ADMIN_IDS:
            return

        excel_files = [f for f in os.listdir(output_directory) if f.endswith(".xlsx")]
    
        if not excel_files:
            await update.message.reply_text("هیچ فایل اکسل موجود نیست.")
            log_user_request(update, "admin", "Excel not Finde")  # لاگ درخواست کاربر
        else:
            for file in excel_files:
                file_path = os.path.join(output_directory, file)
                with open(file_path, 'rb') as f:
                    await context.bot.send_document(chat_id=update.effective_chat.id, document=f)
            await update.message.reply_text("تمام فایل‌های اکسل ارسال شدند.")
            log_user_request(update, "admin", "All Excel Send.")  # لاگ درخواست کاربر
    except Exception as e:
        print(Fore.RED + f"[-] Error async def send_all_excel_files(update: Update, context: ContextTypes.DEFAULT_TYPE): {e}")

# تابع ارسال کل فایل‌های لاگ
async def send_all_log_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id not in ADMIN_IDS:
            return

        log_files = [f for f in os.listdir(output_directory) if f.startswith("user_requests_") and f.endswith(".xlsx")]
    
        if not log_files:
            await update.message.reply_text("هیچ فایل لاگ موجود نیست.")
            log_user_request(update, "admin", "Log Not Finde")  # لاگ درخواست کاربر
        else:
            for file in log_files:
                file_path = os.path.join(output_directory, file)
                with open(file_path, 'rb') as f:
                    await context.bot.send_document(chat_id=update.effective_chat.id, document=f)
            await update.message.reply_text("تمام فایل‌های لاگ ارسال شدند.")
            log_user_request(update, "admin", "All Log File Send.")  # لاگ درخواست کاربر
    except Exception as e:
        print(Fore.RED + f"[-] Error async def send_all_log_files(update: Update, context: ContextTypes.DEFAULT_TYPE): {e}")

async def view_log_as_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id not in ADMIN_IDS:
            return

        today = datetime.now().strftime("%Y-%m-%d")
        log_file_path = os.path.join(output_directory, f"user_requests_{today}.xlsx")
    
        if not os.path.exists(log_file_path):
            await update.message.reply_text("⚠️ فایل لاگ برای امروز وجود ندارد.")
            log_user_request(update, "view_log_as_text", "no log file for today")
            return
    
        try:
            df = pd.read_excel(log_file_path)
        except Exception as e:
            await update.message.reply_text("⚠️ خطا در خواندن فایل لاگ.")
            print(Fore.RED + f"[-] Error reading log file: {e}")
            return
    
        # ساخت پیام متنی با فرمت زیباتر
        log_messages = []
        for idx, row in df.iterrows():
            log_message = (
                f"📄 Log Entry #{idx + 1}\n"
                f"👤 User ID: `{row['User ID']}`\n"
                f"🔗 Username: @{row['Username']}\n"
                f"📝 Full Name: {row['Full Name']}\n"
                f"📂 Request Type: {row['Request Type']}\n"
                f"🔍 Request Data: {row['Request Data']}\n"
                f"📅 Date: {row['Date']}\n"
                f"⏰ Time: {row['Time']}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
            log_messages.append(log_message)

        # ارسال لاگ‌ها به صورت تک به تک با تأخیر
        for log_message in log_messages:  # ارسال هر لاگ به صورت جداگانه
            # Escape کاراکترهای خاص
            log_message = log_message.replace("_", "\\_") \
                                     .replace("*", "\\*") \
                                     .replace("[", "\\[") \
                                     .replace("]", "\\]") \
                                     .replace("(", "\\(") \
                                     .replace(")", "\\)") \
                                     .replace("~", "\\~") \
                                     .replace(">", "\\>") \
                                     .replace("|", "\\|") \
                                     .replace("#", "\\#") \
                                     .replace("-", "\\-")  # Escape کاراکتر '-'
        
            await update.message.reply_text(log_message, parse_mode='MarkdownV2')
            await asyncio.sleep(1)  # تأخیر ۱ ثانیه‌ای بین ارسال‌ها

        log_user_request(update, "view_log_as_text", "logs displayed as text")
    except Exception as e:
        print(Fore.RED + f"[-] Error async def view_log_as_text(update: Update, context: ContextTypes.DEFAULT_TYPE): {e}")

# راه‌اندازی بات تلگرام با استفاده از ApplicationBuilder
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# افزودن CommandHandler برای دستور /esp32
app.add_handler(CommandHandler("esp32", esp32_command))
# افزودن CommandHandler برای دستور /esp32_all
app.add_handler(CommandHandler("esp32_all", esp32_all_command))
# افزودن CommandHandler برای دستور /chart
app.add_handler(CommandHandler("chart", send_chart))
# هندلر پیام "admin" برای نمایش دکمه‌های ادمین
app.add_handler(CommandHandler("admin", handle_admin))
# app.add_handler(MessageHandler(filters.Text("admin"), handle_admin))
# هندلرهای مربوط به دکمه‌ها
app.add_handler(MessageHandler(filters.Text("📂 ارسال کل فایل‌های اکسل"), send_all_excel_files))
app.add_handler(MessageHandler(filters.Text("📂 ارسال کل فایل‌های لاگ"), send_all_log_files))
app.add_handler(MessageHandler(filters.Text("📜 نمایش لاگ‌ها به صورت متن"), view_log_as_text))


# استفاده از JobQueue درون Application
app.job_queue.run_repeating(scheduled_fetch_and_save, interval=60)  # هر 60 ثانیه یک بار

# شروع بات و اجرای وظایف
print(Fore.GREEN + "Bot is running...")
app.run_polling()
