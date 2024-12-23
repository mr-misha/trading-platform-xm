import asyncio
import random


# Utility function to simulate delay
async def simulate_delay():
    await asyncio.sleep(random.uniform(0.1, 1))
