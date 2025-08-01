from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import traceback

# ابتدا تنظیمات محیطی و ایمپورت‌های پایه
from app.database import engine, get_db
from app import models

# ایجاد جداول دیتابیس
models.Base.metadata.create_all(bind=engine)

# تنظیمات تلگرام - باید قبل از ایجاد روترها باشد
from telegram import Bot
from telegram.ext import Application, CommandHandler
from telegram import Update

app = FastAPI(
    title="سیگنال تحلیلگران برتر",
    description="سیستم مدیریت سیگنال‌دهی حرفه‌ای",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

# ایمپورت روترها بعد از تعریف app
from app.routers import (
    auth as auth_router,
    users as users_router,
    admin as admin_router,
    signals as signals_router,
    payments as payments_router,
    support as support_router
)

# افزودن سرویس فایل‌های استاتیک
app.mount("/static", StaticFiles(directory="static"), name="static")

# افزودن روترها
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(admin_router.router)
app.include_router(signals_router.router)
app.include_router(payments_router.router)
app.include_router(support_router.router)

# تابع ایجاد کاربر ادمین
def create_admin_user():
    try:
        ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))
        ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
        
        if not ADMIN_TELEGRAM_ID:
            print("ADMIN_TELEGRAM_ID not set in environment variables!")
            return

        db: Session = next(get_db())
        admin = db.query(models.User).filter(
            models.User.telegram_id == ADMIN_TELEGRAM_ID
        ).first()
        
        if not admin:
            new_admin = models.User(
                telegram_id=ADMIN_TELEGRAM_ID,
                username=ADMIN_USERNAME,
                full_name="Admin User",
                status="admin",
                is_active=True
            )
            db.add(new_admin)
            db.commit()
            print("Admin user created successfully!")
        else:
            admin.status = "admin"
            db.commit()
            print("User upgraded to admin!")
    except Exception as e:
        print(f"Error creating admin: {str(e)}")
        traceback.print_exc()
    finally:
        db.close()

# روت اصلی برای سرویس دهی index.html
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

# روت برای دسترسی مستقیم به index.html
@app.get("/index.html", response_class=HTMLResponse)
async def read_index():
    return await read_root()

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

# ==================== Telegram Bot Setup ==================== 
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

# هندلر دستور /start
async def start(update: Update, context):
    if update.message:
        await update.message.reply_text(
            "🚀 به ربات سیگنال تحلیلگران برتر خوش آمدید!\n"
            "برای دسترسی به اپلیکیشن از دکمه منو استفاده کنید."
        )

# تنظیم وب‌هوک هنگام استارت
@app.on_event("startup")
async def on_startup():
    create_admin_user()  # ایجاد ادمین هنگام راه‌اندازی
    
    if TELEGRAM_BOT_TOKEN:
        await bot.set_webhook(url=f"https://signal-analyst-project.onrender.com/webhook")
        
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
    if not TELEGRAM_BOT_TOKEN:
        return {"status": "error", "message": "Telegram bot token not configured"}
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    await application.process_update(update)
    data = await request.json()
    update = Update.de_json(data, bot)
    
    await application.process_update(update)
    return {"status": "ok"}

# اجرای سرور
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", "8000")),
        log_level="info",
        reload=True
    )
