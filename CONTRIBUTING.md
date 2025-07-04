# راهنمای مشارکت در پروژه LensCraft

## روند ارسال Pull Request
- ابتدا یک Fork از مخزن ایجاد کنید.
- یک Branch جدید برای تغییرات خود بسازید.
- تغییرات را اعمال و Commit کنید.
- Pull Request خود را به شاخه اصلی (main) ارسال کنید.

## سبک کد
- از ابزارهای lint و formatter مانند `black`, `isort`, `flake8` برای کدهای پایتون استفاده کنید.
- برای کدهای جاوااسکریپت از ESLint و Prettier استفاده کنید (در صورت وجود).

## اجرای تست‌ها
- برای تست‌های پایتون:
  ```bash
  pytest
  ```
- برای تست‌های جاوااسکریپت:
  ```bash
  npm test
  ```

## سایر نکات
- توضیحات کافی در Pull Request بنویسید.
- سعی کنید هر Pull Request فقط یک موضوع را پوشش دهد.
