# decorators.py

from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext
from config import ADMIN_IDS
import logging
from db.troly import AssistantManager 
import time

assistant_manager= AssistantManager()
# Thiết lập logging
logger = logging.getLogger(__name__)

CACHE_EXPIRATION = 300

def cache_data(context: CallbackContext, key: str, load_function):
    if key not in context.bot_data or not isinstance(context.bot_data[key], dict) or \
            time.time() - context.bot_data[key].get("timestamp", 0) > CACHE_EXPIRATION:
        data = load_function()
        if isinstance(data, set):
            data = list(data)
        context.bot_data[key] = {"data": data, "timestamp": time.time()}
        logging.info(f"🔄 Cache làm mới: key={key}, data={data}")
    else:
        logging.info(f"✅ Lấy từ cache: key={key}, data={context.bot_data[key]['data']}")
    return context.bot_data[key]["data"]


def troly_only(func):
    """Chỉ cho trợ lý hoặc admin sử dụng."""
    @wraps(func)
    async def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if update.edited_message:
           logger.info("Bỏ qua tin nhắn đã sửa.")
           return
        
        troly_ids = cache_data(context, 'troly_ids', assistant_manager.load_troly_ids)

        if user_id not in troly_ids and user_id not in ADMIN_IDS:
            await send_no_permission(update)
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def admin_only(func):
    """Chỉ admin có thể thực hiện lệnh."""
    @wraps(func)
    async def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await send_no_permission(update)
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

async def send_no_permission(update: Update):
    """Gửi thông báo không có quyền."""
    try:
        if update.callback_query:
            await update.callback_query.answer("Bạn không có quyền thực hiện hành động này.", show_alert=True)
        elif update.message:
            await update.message.reply_text("❌ Bạn không có quyền thực hiện hành động này.")
    except Exception as e:
        logging.error(f"Lỗi khi gửi phản hồi quyền hạn: {e}")