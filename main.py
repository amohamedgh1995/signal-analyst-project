from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from app import models
from app.database import engine
from app.routers import users, admin, auth, signals, payments, support
import traceback

# ایجاد جداول دیتابیس
models.Base.metadata.create_all(bind=engine)
# این خطوط را در بالای فایل اضافه کنید
import os
from fastapi import FastAPI, Request
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler
app = FastAPI(
    title="سیگنال تحلیلگران برتر",
    description="سیستم مدیریت سیگنال‌دهی حرفه‌ای",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

# افزودن سرویس فایل‌های استاتیک
app.mount("/", StaticFiles(directory="static", html=True), name="static")


# افزودن روترها
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(signals.router)
app.include_router(payments.router)
app.include_router(support.router)

# روت اصلی برای سرویس دهی index.html
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

# روت برای دسترسی مستقیم به index.html
@app.get("/index.html", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

# مدیریت خطاهای سفارشی
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "detail": "خطای سرور داخلی",
            "code": "SERVER_ERROR"
        },
    )
# خطوط جدید اضافه کنید
import os
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from fastapi import Request

# تنظیمات تلگرام
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# هندلر دستور /start
async def start(update: Update, context):
    await update.message.reply_text(
        "🚀 به ربات سیگنال تحلیلگران برتر خوش آمدید!\n"
        "برای دسترسی به اپلیکیشن از دکمه منو استفاده کنید."
    )

# تنظیم وب‌هوک هنگام استارت
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(url="https://signal-analyst-project.onrender.com/webhook")
    
    # تنظیم منوی ربات
    await bot.set_chat_menu_button(
        menu_button={
            "type": "web_app",
            "text": "📊 Open App",
            "web_app": {"url": "https://signal-analyst-project.onrender.com"}
        }
    )

# هندلر وب‌هوک
@app.post("/webhook")
async def telegram_webhook(request: Request):
    dp = Dispatcher(bot, None, workers=0)
    dp.add_handler(CommandHandler("start", start))
    
    data = await request.json()
    update = Update.de_json(data, bot)
    
    await dp.process_update(update)
    return {"status": "ok"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=True
    )
