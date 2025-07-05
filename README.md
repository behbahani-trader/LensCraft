# سیستم مدیریت عینک‌سازی

[![CI](https://github.com/behbahani-trader/LensCraft/actions/workflows/ci.yml/badge.svg)](https://github.com/behbahani-trader/LensCraft/actions)
[![Coverage](https://img.shields.io/codecov/c/github/behbahani-trader/LensCraft)](https://github.com/behbahani-trader/LensCraft)

این پروژه یک سیستم مدیریت برای عینک‌سازی است که به شما امکان می‌دهد سفارشات، مشتریان و فریم‌ها را به راحتی مدیریت کنید.

## ویژگی‌ها

- مدیریت سفارشات (ثبت، ویرایش، حذف)
- مدیریت مشتریان (ثبت، ویرایش، حذف)
- داشبورد مدیریتی
- گزارش‌گیری
- پشتیبانی از زبان فارسی
- رابط کاربری زیبا و کاربرپسند

## پیش‌نیازها

- Python 3.11 یا بالاتر
- Node.js 18 یا بالاتر
- Docker و Docker Compose (اختیاری)

## نصب و راه‌اندازی

### روش اول: استفاده از Docker

1. کلون کردن مخزن:
```bash
git clone https://github.com/behbahani-trader/LensCraft.git
cd LensCraft
```
2. اجرای برنامه با Docker Compose:
```bash
docker-compose up --build
```

### روش دوم: نصب مستقیم (ویندوز و لینوکس)

1. کلون کردن مخزن:
```bash
git clone https://github.com/behbahani-trader/LensCraft.git
cd LensCraft
```
2. ایجاد محیط مجازی:
- در ویندوز:
```bat
python -m venv venv
venv\Scripts\activate
```
- در لینوکس/مک:
```bash
python3 -m venv venv
source venv/bin/activate
```
3. نصب وابستگی‌های Python:
```bash
pip install -r requirements.txt
```
4. نصب وابستگی‌های Node.js:
```bash
npm install
```
5. ساخت فایل‌های استاتیک:
```bash
npm run build
```
6. اجرای برنامه:
- در ویندوز:
```bat
run_app.bat
```
یا:
```bat
python app.py
```
- در لینوکس/مک:
```bash
python3 app.py
```

### اسکریپت‌های کاربردی ویندوز

- `run_app.bat` : اجرای سریع برنامه
- `build_exe.bat` : ساخت نسخه اجرایی (exe)
- `build_portable.bat` و `create_portable.bat` : ساخت نسخه پرتابل
- `install_requirements.bat` : نصب سریع وابستگی‌ها

## مستندات و راهنما

- [راهنمای نصب آفلاین](./راهنمای_نصب_آفلاین.md)
- [مستندات API و توسعه](./docs/)
- فایل‌های راهنما و مستندات بیشتر در پوشه `docs/` موجود است.

## استفاده

پس از راه‌اندازی، می‌توانید به آدرس `http://localhost:5000` مراجعه کنید.

## توسعه

1. نصب وابستگی‌های توسعه:
```bash
pip install -r requirements-dev.txt
```
2. اجرای تست‌های پایتون:
```bash
pytest
```
3. اجرای تست‌های جاوااسکریپت:
```bash
npm test
```
4. بررسی کیفیت کد:
```bash
flake8
```

## مشارکت و گزارش باگ

پیشنهادات و گزارش باگ را می‌توانید از طریق [Issues](https://github.com/behbahani-trader/LensCraft/issues) در گیت‌هاب ثبت کنید.

## مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای اطلاعات بیشتر، فایل `LICENSE` را مطالعه کنید.

---

[مشاهده پروژه در گیت‌هاب](https://github.com/behbahani-trader/LensCraft)