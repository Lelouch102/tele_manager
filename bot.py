from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest
import config
from handlers.get_user import (
    get_user_by_phone,
    get_user_by_username,
    get_contacts_count,
    delete_all_contacts,
)

import handlers.admin_handlers as admin_h
from decorators import troly_only, admin_only
from handlers.ultils import handle_info_command, help_command
from handlers.telethon_pool import init_telethon_clients
import logging

logging.getLogger("httpx").setLevel(logging.WARNING)

@troly_only
async def check_command(update, context):
    raw = update.message.text.replace("/check", "").strip()

    if not raw:
        await update.message.reply_text("Nhập số điện thoại hoặc username, mỗi dòng một giá trị!")
        return

    lines = raw.split("\n")

    for line in lines:
        value = line.strip()
        if not value:
            continue

        # ===============================
        # 🔍 PHÂN LOẠI INPUT
        # ===============================
        is_phone = value.isdigit() and len(value) == 9

        # ===============================
        # 🔵 XỬ LÝ SỐ ĐIỆN THOẠI
        # ===============================
        if is_phone:
            if value.startswith("0"):
                phone = "+84" + value[1:]
            else:
                phone = "+84" + value

            info = await get_user_by_phone(phone)

            label = phone

        else:
            # ===============================
            # 🔵 XỬ LÝ USERNAME
            # ===============================
            username = value.replace("@", "")
            info = await get_user_by_username(username)
            label = "@" + username

        # ===============================
        # ❌ KHÔNG TÌM THẤY
        # ===============================
        if not info:
            await update.message.reply_text(f"❌ Không tìm thấy: {label}")
            continue

        # ===============================
        # 📌 THÔNG TIN USER
        # ===============================
        text = (
            f"🔎 Kết quả cho: {label}\n"
            f"🆔 ID: {info['id']}\n"
            f"👤 Username: {info['username']}\n"
            f"⏱️ Last seen: {info['last_seen']}\n"
        )

        # ===============================
        # 🔘 NÚT NHẮN TIN
        # ===============================
        buttons = []
        if info["username"]:
            buttons.append(
                InlineKeyboardButton("💬 NHẮN TIN", url=f"https://t.me/{info['username']}")
            )

        keyboard = InlineKeyboardMarkup([buttons])

        # ===============================
        # 🖼️ ẢNH ĐẠI DIỆN
        # ===============================
        if info.get("avatar"):
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

@admin_only
async def contacts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Đang kiểm tra danh bạ...")

    count = await get_contacts_count()

    await update.message.reply_text(
        f"📇 Số contact hiện tại: <b>{count}</b>",
        parse_mode="HTML"
    )

@admin_only
async def clear_contacts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = await get_contacts_count()

    if count == 0:
        await update.message.reply_text("📭 Danh bạ đang trống.")
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ YES - Xóa", callback_data="clear_contacts_yes"),
            InlineKeyboardButton("❌ NO - Hủy", callback_data="clear_contacts_no"),
        ]
    ])

    await update.message.reply_text(
        f"⚠️ Bạn sắp xóa <b>{count}</b> contact.\n"
        f"Hành động này <b>KHÔNG THỂ HOÀN TÁC</b>.\n\n"
        f"Bạn có chắc không?",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
@troly_only
async def clear_contacts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "clear_contacts_no":
        await query.edit_message_text("❌ Đã hủy thao tác xóa contact.")
        return

    if query.data == "clear_contacts_yes":
        await query.edit_message_text("⏳ Đang xóa contact...")

        deleted = await delete_all_contacts()

        await query.edit_message_text(
            f"✅ Đã xóa thành công <b>{deleted}</b> contact.",
            parse_mode="HTML"
        )
    
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

    app.add_handler(CommandHandler("contacts", contacts_command))
    app.add_handler(CommandHandler("clearcontacts", clear_contacts_command))
    app.add_handler(CallbackQueryHandler(clear_contacts_callback, pattern="^clear_contacts_"))


    app.add_handler(CommandHandler("addtroly", admin_h.add_troly))
    app.add_handler(CommandHandler("removetroly", admin_h.remove_troly))
    app.add_handler(CommandHandler("lstroly", admin_h.list_troly))
    
    app.add_handler(CommandHandler("info", handle_info_command))
    app.add_handler(CommandHandler(["h", "help"], help_command))

    app.run_polling()


if __name__ == "__main__":
    main()