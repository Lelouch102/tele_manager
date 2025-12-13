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
from handlers.telethon_pool import get_next_client
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.contacts import GetContactsRequest
from telethon.tl.functions.contacts import DeleteContactsRequest

# api_id = config.API_ID
# api_hash = config.API_HASH

# session_name = f"session_{api_id}"
# client = TelegramClient(session_name, api_id, api_hash)


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
    client = get_next_client()  # 🔥 lấy client khác nhau mỗi lần gọi
    print(f"[LOG] Dùng client session: {client.session.filename}")

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
        return None

    user = result.users[0]

    # Xử lý last seen
    if isinstance(user.status, UserStatusOnline):
        last_seen = "🟢 Đang online"
    elif isinstance(user.status, UserStatusOffline):
        now = datetime.now(timezone.utc)
        diff = now - user.status.was_online

        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60

        if days > 0: last_seen = f"🔵 Online {days} ngày trước"
        elif hours > 0: last_seen = f"🔵 Online {hours} giờ trước"
        elif minutes > 0: last_seen = f"🔵 Online {minutes} phút trước"
        else: last_seen = "🔵 Vừa mới online"
    else:
        last_seen = "⚪ Ẩn last seen"

    return {
        "id": user.id,
        "first_name": user.first_name,
        "username": user.username,
        "phone": user.phone,
        "last_seen": last_seen,
        "avatar": None,
    }
    
async def get_user_by_username(username: str):
    username = username.replace("@", "").strip()

    client = get_next_client()
    print(f"[LOG] Dùng client session: {client.session.filename}")

    try:
        full = await client(GetFullUserRequest(username))
    except Exception as e:
        print("[ERROR] Lỗi khi gọi GetFullUserRequest:", e)
        return None

    # ⭐ LẤY USER TỪ full.users[]
    if not full.users or len(full.users) == 0:
        return None

    user = full.users[0]   # ⭐ Đây mới là user thật

    # ---------------------------
    # Xử lý last seen
    # ---------------------------
    status = user.status

    if isinstance(status, UserStatusOnline):
        last_seen = "🟢 Đang online"

    elif isinstance(status, UserStatusOffline):
        now = datetime.now(timezone.utc)
        diff = now - status.was_online

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

    # ---------------------------
    # ⭐ Return
    # ---------------------------
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "phone": getattr(user, "phone", None),
        "bot": user.bot,
        "last_seen": last_seen
    }
    
async def get_contacts_count():
    client = get_next_client()
    print(f"[LOG] Dùng client session: {client.session.filename}")

    try:
        result = await client(GetContactsRequest(hash=0))
        count = len(result.users)
        print(f"[LOG] Tổng số contact hiện tại: {count}")
        return count
    except Exception as e:
        print("[ERROR] Lỗi khi lấy danh sách contact:", e)
        return 0

async def delete_all_contacts():
    client = get_next_client()
    print(f"[LOG] Dùng client session: {client.session.filename}")

    try:
        # Lấy toàn bộ contacts
        result = await client(GetContactsRequest(hash=0))
        users = result.users

        if not users:
            print("[LOG] Không có contact nào để xóa.")
            return 0

        user_ids = [u.id for u in users]

        # Xóa contacts
        await client(DeleteContactsRequest(id=user_ids))

        print(f"[LOG] Đã xóa {len(user_ids)} contact.")
        return len(user_ids)

    except Exception as e:
        print("[ERROR] Lỗi khi xóa contact:", e)
        return 0
    
    
# async def start_telethon():
#     print("[LOG] Khởi động Telethon...")
#     await client.start()
#     print("[LOG] Telethon đã sẵn sàng!")
