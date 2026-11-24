STAGES = [
    ("requirements_analysis", "تحلیل نیازمندی‌ها"),
    ("architecture_design", "طراحی معماری"),
    ("ui_ux_design", "طراحی UI/UX"),
    ("theme_generation", "تولید قالب"),
    ("plugin_generation", "تولید افزونه"),
    ("feature_implementation", "پیاده‌سازی امکانات"),
    ("code_review", "بازبینی کد"),
    ("final_packaging", "بسته‌بندی نهایی"),
]

STAGE_TITLES = dict(STAGES)

JSON_CONTRACT = """{
  "project_id": "<slug>",
  "batch_id": "batch-001",
  "files": [
    {"path": "wp-content/themes/custom-theme/style.css",
     "content": "/* CSS */"}
  ],
  "completed": true,
  "message": "توضیح کوتاه (اختیاری)"
}"""


def build_stage_prompt(stage: str, ctx: dict) -> str:
    head = f"""### نقش
تو یک مهندس ارشد وردپرس، PHP، JavaScript، CSS و UI/UX هستی.

### اطلاعات پروژه
- نام: {ctx['name']}
- Slug: {ctx['slug']}
- نوع سایت: {ctx['type']}
- زبان سایت: {ctx['language']}
- نسخه وردپرس هدف: {ctx['wp_version']}
- قابلیت‌های موردنیاز: {', '.join(ctx['features']) or '-'}
- صفحات موردنیاز: {', '.join(ctx['pages']) or '-'}
- سلیقه طراحی: {ctx['design'] or '-'}
- توضیحات مشتری:
{ctx['requirements'] or '-'}

### معماری تأییدشده
{ctx['architecture'] or '-'}
"""

    body = STAGE_BODIES.get(stage, "")
    tail = f"""
### قرارداد خروجی (بسیار مهم)
پاسخ را **فقط** به‌صورت یک بلوک ```json و مطابق قرارداد زیر برگردان:
```json
{JSON_CONTRACT}
```
- همه مسیرها نسبی و نسبت به ریشه پروژه هستند (مثلاً `wp-content/themes/...`).
- هیچ فایل خارج از `wp-content/` یا `docs/` نساز.
- از کد مخرب، رمز عبور، توکن و API Key استفاده نکن.
- اگر پاسخ ناتمام ماند، `completed: false` بگذار و باقی را در بچ بعدی ادامه بده.
"""
    return head + "\n" + body + "\n" + tail


STAGE_BODIES = {
    "requirements_analysis": """
### وظیفه
تحلیل دقیق نیازمندی‌ها. یک سند Markdown تولید کن شامل:
- خلاصه پروژه
- پرسوناها
- فهرست قابلیت‌ها با اولویت
- فهرست صفحات و ارتباط آن‌ها
- ریسک‌ها
خروجی را در فایل `docs/requirements.md` قرار بده.
""",
    "architecture_design": """
### وظیفه
طراحی معماری اطلاعاتی سایت. فایل `docs/architecture.md` را با موارد زیر بساز:
- درخت صفحات و سلسله‌مراتب
- جایگاه قالب و افزونه
- جداول پایگاه‌داده سفارشی
- CPT ها و Taxonomies
""",
    "ui_ux_design": """
### وظیفه
طراحی UI/UX. یک فایل `docs/design-system.md` بساز شامل:
- پالت رنگ (حداقل ۶ رنگ با Hex)
- تایپوگرافی
- Grid و Spacing
- کامپوننت‌ها (دکمه، کارت، فرم)
- راهنمای RTL و Responsive
""",
    "theme_generation": """
### وظیفه
تولید قالب واقعی وردپرس در `wp-content/themes/custom-theme/` شامل:
- style.css با هدر استاندارد قالب
- functions.php با register_nav_menus و theme_support
- header.php ، footer.php ، index.php ، front-page.php
- single.php ، archive.php ، search.php ، 404.php
- assets/css/main.css و assets/js/main.js
- template-parts/ برای بخش‌های قابل استفاده مجدد
همه فایل‌ها باید استاندارد وردپرس، RTL و واکنش‌گرا باشند.
""",
    "plugin_generation": """
### وظیفه
تولید افزونه اختصاصی در `wp-content/plugins/custom-core/` شامل:
- custom-core.php با هدر افزونه
- includes/class-cpt.php (Custom Post Types)
- includes/class-taxonomies.php
- includes/class-admin.php
- includes/class-forms.php
- includes/class-business-logic.php
منطق تجاری را داخل افزونه قرار بده، نه قالب.
اگر وابستگی رسمی مثل WooCommerce لازم بود فقط آن را به‌عنوان وابستگی معرفی کن.
""",
    "feature_implementation": """
### وظیفه
پیاده‌سازی امکانات کلیدی (بر اساس فهرست بالا). فایل‌های تکمیلی داخل قالب یا افزونه بساز.
اگر نیاز به جدول دیتابیس است، از dbDelta در هوک activation استفاده کن.
""",
    "code_review": """
### وظیفه
بازبینی کدهای تولیدشده. فایل `docs/code-review.md` بساز شامل:
- باگ‌های احتمالی
- مسائل امنیتی (nonce, sanitize, escape)
- بهبودهای پیشنهادی
- بررسی استانداردهای وردپرس
""",
    "final_packaging": """
### وظیفه
بسته‌بندی نهایی. فایل `docs/installation.md` بساز شامل:
- ساختار فایل‌ها
- مراحل نصب روی هاست
- وابستگی‌ها
- چک‌لیست امنیت
""",
}