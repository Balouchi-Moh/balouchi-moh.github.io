# راهنمای انتشار مقاله (بدون دست زدن به کد)

## یک‌بار راه‌اندازی
1. محتوای این بسته را در ریشه ریپوی سایت کپی کن (پوشه‌های `content`، `templates`، `tools`، `data/posts-legacy.json` و `.github/workflows/build.yml`).
2. در GitHub: Settings → Pages → Source را همان‌طور که هست بگذار (Deploy from a branch). تغییری لازم نیست.
3. در GitHub: Settings → Actions → General → Workflow permissions → گزینه «Read and write permissions» را بزن.
4. اگر شاخه اصلی ریپو `main` نیست (مثلاً `master`)، در فایل `.github/workflows/build.yml` عبارت `branches: [main]` را به نام شاخه‌ات تغییر بده.
5. فایل `data/posts.json` از این به بعد خودکار ساخته می‌شود. مقاله‌های قدیمی در `data/posts-legacy.json` هستند.

## انتشار مقاله جدید
1. در GitHub به پوشه `content/posts` برو → Add file → Create new file.
2. نام فایل: `<slug>.en.md` (مثلاً `pull-planning.en.md`). slug فقط حروف کوچک انگلیسی، عدد و خط تیره.
3. محتوا را از `_template.en.md` کپی کن، سرایند (بین دو خط ---) را پر کن و متن را بنویس. status را `published` بگذار.
4. همین کار را برای `<slug>.fa.md` تکرار کن. slug و date باید یکی باشد.
5. Commit changes. حدود یک دقیقه بعد صفحه‌های مقاله و `data/posts.json` خودکار ساخته می‌شوند (در تب Actions می‌توانی ببینی).

## نکته‌ها
- فقط انگلیسی یا فقط فارسی هم می‌شود. نسخه دیگر به همان صفحه موجود اشاره می‌کند.
- پیش‌نویس: `status: draft` بگذار؛ صفحه ساخته نمی‌شود.
- ویرایش: فایل `.md` را باز کن، اصلاح کن، Commit کن.
- حذف: فایل‌های `.md` را پاک کن؛ صفحه‌های ساخته‌شده هم خودکار حذف می‌شوند.
- اگر ساخت خطا داد، در تب Actions پیام خطا (مثلاً نبودن date) نوشته شده است.
- مقاله‌های قدیمی (Takt، مدیریت دانش، ساخت ناب) دست‌نخورده می‌مانند.
