@echo off
chcp 65001 >nul
echo ==========================================
echo    ساخت نسخه قابل حمل
echo ==========================================
echo.

echo 🔧 مرحله 1: نصب PyInstaller...
pip install pyinstaller

echo.
echo 🧹 مرحله 2: پاک کردن فایل‌های قبلی...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo 📦 مرحله 3: ساخت فایل اجرایی...
pyinstaller --onefile --add-data "app/templates;app/templates" --add-data "app/static;app/static" --add-data "instance;instance" --name "LensWorkshop" run.py

echo.
echo 📁 مرحله 4: ایجاد پوشه نهایی...
mkdir "dist\LensWorkshop_Portable"
move "dist\LensWorkshop.exe" "dist\LensWorkshop_Portable\"

echo.
echo 📄 مرحله 5: ایجاد فایل راه‌اندازی...
(
echo @echo off
echo chcp 65001 ^>nul
echo echo ==========================================
echo echo    نرم‌افزار مدیریت کارگاه عینک‌سازی
echo echo ==========================================
echo echo.
echo echo 🚀 در حال راه‌اندازی سرور...
echo echo.
echo echo ✅ پس از راه‌اندازی، مرورگر را باز کرده و به آدرس زیر بروید:
echo echo 🌐 http://localhost:5000
echo echo.
echo echo 👤 اطلاعات ورود:
echo echo    نام کاربری: admin
echo echo    رمز عبور: admin
echo echo.
echo echo ⚠️  برای خروج، این پنجره را ببندید.
echo echo.
echo LensWorkshop.exe
echo pause
) > "dist\LensWorkshop_Portable\شروع.bat"

echo.
echo 📖 مرحله 6: ایجاد فایل راهنما...
(
echo ==========================================
echo    نرم‌افزار مدیریت کارگاه عینک‌سازی
echo ==========================================
echo.
echo 🚀 نحوه استفاده:
echo 1. فایل "شروع.bat" را دابل کلیک کنید
echo 2. مرورگر خود را باز کرده و به آدرس http://localhost:5000 بروید
echo 3. با اطلاعات زیر وارد شوید:
echo    👤 نام کاربری: admin
echo    🔑 رمز عبور: admin
echo.
echo 💡 نکات مهم:
echo ✅ این نرم‌افزار نیازی به اینترنت ندارد
echo ✅ تمام اطلاعات در همین پوشه ذخیره می‌شود
echo ✅ برای پشتیبان‌گیری از بخش گزارشات استفاده کنید
echo ✅ برای انتقال به سیستم دیگر، کل پوشه را کپی کنید
echo.
echo 🔧 عیب‌یابی:
echo ❌ اگر خطای "Port in use" دیدید، برنامه را ببندید و دوباره اجرا کنید
echo ❌ اگر مرورگر باز نشد، دستی آدرس http://localhost:5000 را وارد کنید
echo ❌ اگر صفحه لود نشد، چند ثانیه صبر کنید و صفحه را refresh کنید
echo.
echo 📞 پشتیبانی:
echo این نرم‌افزار برای مدیریت کارگاه‌های عینک‌سازی طراحی شده است.
echo شامل: مدیریت سفارشات، مشتریان، انواع عدسی و تراش، گزارشات و پشتیبان‌گیری
) > "dist\LensWorkshop_Portable\راهنما.txt"

echo.
echo 🎯 مرحله 7: کپی فایل‌های ضروری...
if exist "instance\database.db" (
    copy "instance\database.db" "dist\LensWorkshop_Portable\"
)

echo.
echo ==========================================
echo ✅ ساخت نسخه قابل حمل تکمیل شد!
echo ==========================================
echo.
echo 📁 مسیر فایل‌ها: dist\LensWorkshop_Portable
echo 🚀 برای اجرا: شروع.bat را دابل کلیک کنید
echo 📦 برای انتقال: کل پوشه LensWorkshop_Portable را کپی کنید
echo.
echo 💡 این پوشه را می‌توانید روی هر سیستم ویندوزی بدون نیاز به نصب اجرا کنید!
echo.
pause
