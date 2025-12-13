from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest
import config
from handlers.get_user import get_user_by_phone, start_telethon
import handlers.admin_handlers as admin_h
from decorators import troly_only
from handlers.ultils import handle_info_command, help_command
from handlers.telethon_pool import init_telethon_clients

async def check_command(update, context):
    # await start_telethon()

    raw = update.message.text.replace("/check", "").strip()

    if not raw:
        await update.message.reply_text("Nhập số điện thoại, mỗi dòng một số!")
        return

    numbers = raw.split("\n")

    for line in numbers:
        phone_raw = line.strip()
        if not phone_raw:
            continue

        if phone_raw.startswith("0"):
            phone = "+84" + phone_raw[1:]
        elif phone_raw.startswith("84"):
            phone = "+" + phone_raw
        elif phone_raw.startswith("+"):
            phone = phone_raw
        else:
            phone = "+84" + phone_raw

        info = await get_user_by_phone(phone)

        if not info:
            await update.message.reply_text(f"❌ Không tìm thấy: {phone}")
            continue

        text = (
            f"📱 Số điện thoại: {phone}\n"
            f"🆔 ID: {info['id']}\n"
            f"🔗 Username: {info['username']}\n"
            f"⏱️ Last seen: {info['last_seen']}\n"
        )

        # if info["avatar"]:
        #     await update.message.reply_photo(
        #         photo=open(info["avatar"], "rb"),
        #         caption=text,
        #     )
        # else:
        #     await update.message.reply_text(text)
        
        buttons = []

        if info["username"]:
            buttons.append(
                InlineKeyboardButton("💬 NHẮN TIN", url=f"https://t.me/{info['username']}")
            )

        keyboard = InlineKeyboardMarkup([buttons])

        if info["avatar"]:
            await update.message.reply_photo(
                photo=open(info["avatar"], "rb"),
                caption=text,
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text(text, reply_markup=keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Gửi /check + danh sách số để kiểm tra.")


async def post_init(app):
    print("[LOG] Đang khởi tạo Telethon clients...")
    await init_telethon_clients()
    print("[LOG] Telethon đã sẵn sàng!")


def main():
    app = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .request(HTTPXRequest())
        .post_init(post_init)   # 🔥 chạy init telethon trước polling
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check_command))

    app.add_handler(CommandHandler("addtroly", admin_h.add_troly))
    app.add_handler(CommandHandler("removetroly", admin_h.remove_troly))
    app.add_handler(CommandHandler("lstroly", admin_h.list_troly))
    
    app.add_handler(CommandHandler("info", handle_info_command))
    app.add_handler(CommandHandler(["h", "help"], help_command))

    app.run_polling()


if __name__ == "__main__":
    main()