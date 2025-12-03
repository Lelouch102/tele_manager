from telethon import TelegramClient
import config

clients = []
current_index = 0  # cho round-robin

async def init_telethon_clients():
    global clients

    for idx, app in enumerate(config.TELEGRAM_APPS):
        session_name = f"session_{app['id']}"
        client = TelegramClient(session_name, app["id"], app["hash"])
        await client.start()
        clients.append(client)

    print(f"[LOG] Đã khởi động {len(clients)} Telegram clients")

def get_next_client():
    global current_index
    client = clients[current_index]
    current_index = (current_index + 1) % len(clients)
    return client
