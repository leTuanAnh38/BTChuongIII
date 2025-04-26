import os
import smtplib
import shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
import schedule
import time

# Load biến môi trường
load_dotenv()

SENDER = os.getenv("SENDER_EMAIL")
PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER = os.getenv("RECEIVER_EMAIL")

# Gửi Email
def send_email(subject, body):
    message = MIMEMultipart()
    message["From"] = SENDER
    message["To"] = RECEIVER
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, RECEIVER, message.as_string())
        server.quit()
        print(" Email đã được gửi.")
    except Exception as e:
        print(f" Gửi email thất bại: {e}")

# Hàm backup
def backup_database():
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = "backups"
    os.makedirs(backup_folder, exist_ok=True)

    files_backed_up = []

    for file in os.listdir():
        if file.endswith(".sqlite3") or file.endswith(".sql"):
            try:
                dst = os.path.join(backup_folder, f"backup_{now}_{file}")
                shutil.copy(file, dst)
                files_backed_up.append(dst)
                print(f"✔ Backup: {dst}")
            except Exception as e:
                send_email(" Backup thất bại", f"Lỗi backup file {file}: {e}")
                return

    if files_backed_up:
        body = " Backup thành công các file sau:\n" + "\n".join(files_backed_up)
        send_email(" Backup thành công", body)
    else:
        send_email(" Không tìm thấy file backup", "Không có file .sql hoặc .sqlite3 nào để backup.")

# Lịch chạy hằng ngày
schedule.every().day.at("00:00").do(backup_database)

if __name__ == "__main__":
    print("Đang chạy lịch backup lúc 00:00 mỗi ngày...")
    while True:
        schedule.run_pending()
        time.sleep(30)
