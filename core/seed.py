from database import db
from models.models import HelpCategory, HelpArticle


CATEGORIES = [
    {"name": "شروع سریع", "slug": "quick-start", "order": 1},
    {"name": "آموزش DeepSeek", "slug": "deepseek", "order": 2},
    {"name": "مدیریت پروژه", "slug": "project-management", "order": 3},
    {"name": "آموزش WordPress", "slug": "wordpress", "order": 4},
    {"name": "عیب‌یابی", "slug": "troubleshooting", "order": 5},
    {"name": "پرسش‌های متداول", "slug": "faq", "order": 6},
]

ARTICLES = [
    ("quick-start", "معرفی نرم‌افزار", "intro",
     "WP AI Factory ابزاری است که با دریافت توضیحات مشتری، پرامپت تخصصی برای DeepSeek می‌سازد و پاسخ JSON آن را به فایل‌های واقعی وردپرس تبدیل می‌کند. هیچ API متصل نیست؛ همه چیز دستی است."),
    ("quick-start", "ایجاد اولین پروژه", "first-project",
     "از منوی پروژه‌ها → ایجاد پروژه، نام و نوع سایت را وارد کنید. سپس نیازمندی‌ها، قابلیت‌ها و صفحات را ثبت کنید و معماری را تأیید کنید."),
    ("quick-start", "تولید اولین پرامپت", "first-prompt",
     "پس از تأیید معماری، به تب «پرامپت» پروژه بروید، مرحله را انتخاب و «تولید پرامپت» را بزنید. متن را کپی و در DeepSeek ارسال کنید."),
    ("deepseek", "ارسال پرامپت به DeepSeek", "send-prompt",
     "کافی است متن پرامپت را در چت DeepSeek Paste کنید. اگر پاسخ طولانی شد، در چند پیام ادامه دهید و در نهایت JSON را دریافت کنید."),
    ("deepseek", "وارد کردن پاسخ", "import-response",
     "پاسخ JSON را در بخش Import پروژه قرار دهید. نرم‌افزار ساختار را بررسی و فایل‌ها را می‌سازد. پاسخ ناقص نیز پذیرفته می‌شود و می‌توانید ادامه دهید."),
    ("project-management", "مدیریت فایل‌ها", "files",
     "در تب «فایل‌ها» ساختار درختی workspace را می‌بینید. می‌توانید فایل را ببینید، ویرایش کنید یا نسخه جدید بسازید."),
    ("project-management", "خروجی گرفتن", "export",
     "از تب «خروجی» می‌توانید ZIP آماده نصب (wp-content / theme / plugin) و گزارش HTML را دریافت کنید."),
    ("wordpress", "وردپرس چیست؟", "what-is-wp",
     "وردپرس یک CMS متن‌باز برای ساخت وب‌سایت است که از قالب و افزونه پشتیبانی می‌کند."),
    ("wordpress", "قالب چیست؟", "theme",
     "قالب مجموعه‌ای از فایل‌های PHP/CSS/JS در مسیر wp-content/themes است که ظاهر سایت را تعریف می‌کند."),
    ("wordpress", "افزونه چیست؟", "plugin",
     "افزونه منطق تجاری را به وردپرس اضافه می‌کند و در wp-content/plugins قرار می‌گیرد."),
    ("troubleshooting", "JSON نامعتبر", "invalid-json",
     "اگر JSON با خطا مواجه شد، مطمئن شوید DeepSeek پاسخ را داخل بلوک ```json برگرداند و هیچ کاراکتر اضافه در ابتدا/انتهای آن نباشد."),
    ("troubleshooting", "پاسخ ناقص", "partial",
     "اگر پاسخ کامل نبود، در همان پرامپت ادامه دهید یا مرحله بعد را جداگانه تولید کنید؛ نرم‌افزار نوشتن فایل‌های تکراری را مدیریت می‌کند."),
    ("faq", "آیا API Key لازم است؟", "api-key",
     "نه. کل ارتباط با DeepSeek دستی است."),
    ("faq", "آیا اینترنت لازم است؟", "internet",
     "برای ارسال به DeepSeek بله؛ ولی خود نرم‌افزار بدون اینترنت اجرا می‌شود."),
    ("faq", "آیا خروجی روی هاست نصب می‌شود؟", "install-host",
     "بله، ZIP خروجی ساختار استاندارد wp-content را دارد و مستقیماً قابل استفاده است."),
]


def seed_help():
    if HelpCategory.query.count() > 0:
        return
    cat_map = {}
    for c in CATEGORIES:
        cat = HelpCategory(**c)
        db.session.add(cat)
        db.session.flush()
        cat_map[c["slug"]] = cat.id

    for cat_slug, title, slug, content in ARTICLES:
        db.session.add(HelpArticle(
            category_id=cat_map[cat_slug],
            title=title, slug=slug, content=content,
        ))
    db.session.commit()