# سیستم مدیریت عینک‌سازی

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
git clone git clone https://github.com/behbahani-trader/LensCraft.git
cd lens-workshop
```

2. اجرای با Docker Compose:
```bash
docker-compose up --build
```

### روش دوم: نصب مستقیم

1. کلون کردن مخزن:
```bash
git clone https://github.com/yourusername/lens-workshop.git
cd lens-workshop
```

2. ایجاد محیط مجازی:
```bash
python -m venv venv
source venv/bin/activate  # در Windows: venv\Scripts\activate
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
```bash
python app.py
```

## استفاده

پس از راه‌اندازی، می‌توانید به آدرس `http://localhost:5000` مراجعه کنید.

## توسعه

برای توسعه پروژه، مراحل زیر را دنبال کنید:

1. نصب وابستگی‌های توسعه:
```bash
pip install -r requirements-dev.txt
```

2. اجرای تست‌ها:
```bash
pytest
```

3. بررسی کیفیت کد:
```bash
flake8
```

## مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای اطلاعات بیشتر، فایل `LICENSE` را مطالعه کنید. 