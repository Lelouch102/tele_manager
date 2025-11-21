# handlers/get_user.py

from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import (
    InputPhoneContact,
    UserStatusOnline,
    UserStatusOffline
)
from telethon.errors import UserPrivacyRestrictedError
from datetime import datetime, timezone
import config

api_id = config.API_ID
api_hash = config.API_HASH

session_name = f"session_{api_id}"
client = TelegramClient(session_name, api_id, api_hash)


# async def can_message_user(user_id):
#     try:
#         # Thử lấy entity user (KHÔNG gửi tin nhắn)
#         await client.get_entity(user_id)
        
#         # Thử mở dialog
#         dialogs = await client.get_dialogs(limit=1)
#         return True
#     except UserPrivacyRestrictedError:
#         return False
#     except Exception as e:
#         print("[LOG] Không thể mở chat:", e)
#         return False
    

# async def can_message_user(user_id):
#     try:
#         await client.send_message(user_id, "👋")
#         return True
#     except UserPrivacyRestrictedError:
#         return False
#     except Exception as e:
#         print("[LOG] Không thể nhắn tin:", e)
#         return False

async def get_user_by_phone(phone: str):
    print(f"[LOG] Bắt đầu lấy thông tin số: {phone}")

    try:
        result = await client(
            ImportContactsRequest([
                InputPhoneContact(
                    client_id=0,
                    phone=phone,
                    first_name="check",
                    last_name=""
                )
            ])
        )

    except Exception as e:
        print("[ERROR] Lỗi khi gọi ImportContactsRequest:", e)
        return None

    if not result.users:
        print("[LOG] Không tìm thấy user")
        return None

    user = result.users[0]

    # --------------------------
    # LAST SEEN FORMAT
    # --------------------------
    if isinstance(user.status, UserStatusOnline):
        last_seen = "🟢 Đang online"

    elif isinstance(user.status, UserStatusOffline):
        now = datetime.now(timezone.utc)
        diff = now - user.status.was_online

        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60

        if days > 0:
            last_seen = f"🔵 Online {days} ngày trước"
        elif hours > 0:
            last_seen = f"🔵 Online {hours} giờ trước"
        elif minutes > 0:
            last_seen = f"🔵 Online {minutes} phút trước"
        else:
            last_seen = "🔵 Vừa mới online"

    else:
        last_seen = "⚪ Ẩn last seen"

    # --------------------------
    # AVATAR
    # --------------------------
    avatar_path = None
    # if user.photo:
    #     avatar_path = f"avatar_{user.id}.jpg"
    #     try:
    #         await client.download_profile_photo(user.id, file=avatar_path)
    #     except Exception as e:
    #         print("[ERROR] Lỗi tải avatar:", e)

    # --------------------------
    # CHECK CHAT & ADD
    # --------------------------

    return {
        "id": user.id,
        "first_name": user.first_name,
        "username": user.username,
        "phone": user.phone,
        "last_seen": last_seen,
        "avatar": avatar_path,
    }


async def start_telethon():
    print("[LOG] Khởi động Telethon...")
    await client.start()
    print("[LOG] Telethon đã sẵn sàng!")
