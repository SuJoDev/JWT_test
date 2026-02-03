import asyncio
import aiohttp
import time
import random
from statistics import mean

from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("DATABASE_URL")
USER_IDS = list(range(1001, 1101)) 
TRACK_IDS = list(range(1, 501))

async def simulate_listen(session, user_id, track_id):
    payload = {"user_id": user_id, "track_id": track_id}
    try:
        start = time.time()
        async with session.post(f"{BASE_URL}/listen", json=payload, timeout=10) as resp:
            elapsed = time.time() - start
            return elapsed if resp.status == 200 else None
    except Exception:
        return None

async def simulate_get_track(session, track_id):
    try:
        start = time.time()
        async with session.get(f"{BASE_URL}/tracks/{track_id}", timeout=10) as resp:
            elapsed = time.time() - start
            return elapsed if resp.status == 200 else None
    except Exception:
        return None

async def run_load_test(concurrent_users: int, actions_per_user: int):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(concurrent_users * actions_per_user):
            user_id = random.choice(USER_IDS)
            track_id = random.choice(TRACK_IDS)
            # Чередуем действия: 70% — прослушивание, 30% — просмотр трека
            if random.random() < 0.7:
                tasks.append(simulate_listen(session, user_id, track_id))
            else:
                tasks.append(simulate_get_track(session, track_id))
        
        results = await asyncio.gather(*tasks)
    
    successful = [r for r in results if r is not None]
    failed = len(results) - len(successful)
    avg_time = mean(successful) if successful else 0.0
    max_time = max(successful) if successful else 0.0

    print(f"Пользователей: {concurrent_users:3d} | "
          f"Запросов: {len(results):3d} | "
          f"Успешно: {len(successful):3d} | "
          f"Ошибок: {failed:2d} | "
          f"Среднее время: {avg_time:.3f} с | "
          f"Макс.: {max_time:.3f} с")
    
    return len(successful), failed, avg_time

async def main():
    print("Нагрузочное тестирование музыкального сервиса\n")
    scenarios = [
        (10, 20),   # 200 запросов
        (50, 10),   # 500 запросов
        (100, 10),  # 1000 запросов
        (200, 5),   # 1000 запросов (высокая параллельность)
        (500, 2),   # 1000 запросов (макс. конкуренция)
    ]

    for users, actions in scenarios:
        await run_load_test(users, actions)
        await asyncio.sleep(2)  # пауза для стабилизации

if __name__ == "__main__":
    asyncio.run(main())