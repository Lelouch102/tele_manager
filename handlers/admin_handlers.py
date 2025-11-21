import decorators
import logging
import os

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext
from db.troly import assistant_manager

# Thiết lập logging
logger = logging.getLogger(__name__)

@decorators.admin_only
async def add_troly(update: Update, context: CallbackContext):
    """Thêm một trợ lý mới vào danh sách"""
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Sử dụng: /addtroly <ID> [@username] <Tên Tele>")
            return

        troly_id = args[0]
        if not troly_id.isdigit():
            await update.message.reply_text("❌ ID phải là số.")
            return
        troly_id = int(troly_id)

        if args[1].startswith('@'):
            username = args[1]
            tele_name = ' '.join(args[2:]) if len(args) > 2 else ''
        else:
            username = ''
            tele_name = ' '.join(args[1:]) if len(args) > 1 else ''

        # Kiểm tra xem trợ lý đã tồn tại chưa
        existing_troly = assistant_manager.get_assistant_by_id(troly_id)
        if existing_troly:
            await update.message.reply_text("❌ Trợ lý với ID này đã tồn tại.")
            return

        # Thêm trợ lý vào database
        result = assistant_manager.add_assistant(troly_id, username, tele_name)
        if result:
            await update.message.reply_text("✅ Thêm trợ lý thành công.")
            logger.info(f"Thêm trợ lý mới: ID={troly_id}, Username={username}, Tên Tele={tele_name}")
        else:
            await update.message.reply_text("❌ Lỗi khi thêm trợ lý vào database.")
            logger.error(f"Lỗi khi thêm trợ lý: ID={troly_id}, Username={username}, Tên Tele={tele_name}")

    except Exception as e:
        logger.error(f"❌ Lỗi trong hàm add_troly: {e}")
        await update.message.reply_text(f"❌ Lỗi: {e}")

@decorators.admin_only
async def remove_troly(update: Update, context: CallbackContext):
    """Xóa một trợ lý khỏi danh sách"""
    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("Sử dụng: /removetroly <ID>")
            return

        troly_id = args[0]
        if not troly_id.isdigit():
            await update.message.reply_text("❌ ID phải là số.")
            return
        troly_id = int(troly_id)

        # Kiểm tra xem trợ lý có tồn tại không
        existing_troly = assistant_manager.get_assistant_by_id(troly_id)
        if not existing_troly:
            await update.message.reply_text("❌ Trợ lý với ID này không tồn tại.")
            return

        # Xóa trợ lý khỏi database
        delete_result = assistant_manager.delete_assistant(troly_id)
        if delete_result:
            await update.message.reply_text("✅ Xóa trợ lý thành công.")
            logger.info(f"Xóa trợ lý: ID={troly_id}")
        else:
            await update.message.reply_text("❌ Lỗi khi xóa trợ lý khỏi database.")
            logger.error(f"Lỗi khi xóa trợ lý: ID={troly_id}")

    except Exception as e:
        logger.error(f"❌ Lỗi trong hàm remove_troly: {e}")
        await update.message.reply_text(f"❌ Lỗi: {e}")

@decorators.admin_only
async def list_troly(update: Update, context: CallbackContext):
    """Liệt kê danh sách trợ lý"""
    try:
        troly_list = assistant_manager.get_all_assistants()
        if not troly_list:
            await update.message.reply_text("❌ Chưa có trợ lý nào.")
            return

        message = "*📌 Danh sách trợ lý:*\n"
        for t in troly_list:
            msg = f"- *ID:* `{t['id_tele']}`"
            if t.get("username"):
                msg += f"  |  *Username:* {t['username']}"
            if t.get("name"):
                msg += f"  |  *Tên Tele:* {t['name']}"
            message += msg + "\n"

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        logger.info("Đã liệt kê danh sách trợ lý.")

    except Exception as e:
        logger.error(f"❌ Lỗi trong hàm list_troly: {e}")
        await update.message.reply_text(f"❌ Lỗi: {e}")