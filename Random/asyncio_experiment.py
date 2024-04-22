import asyncio
import random
import time



"""
https://stackoverflow.com/questions/62528272/what-does-asyncio-create-task-do

What does asyncio.create_task() do?

It submits the coroutine to run "in the background", i.e. concurrently with the current task and all other tasks, 
switching between them at await points.
It returns an awaitable handle called a "task" which you can also use to cancel the execution of the coroutine.

"""
async def a_forever_loop():
    while True:
        await asyncio.sleep(0.1)
        print("This loop is running!")
        await asyncio.sleep(5)
        pass
async def a_function_that_sometimes_needs_to_run():
    while True:
        print("Rolling dice...")
        if random.randint(0, 10) == 0:
            print("This function is running!")
        await asyncio.sleep(0.1)
#asyncio.create_task(a_forever_loop())
#asyncio.create_task(a_function_that_sometimes_needs_to_run())

async def main():
    task1 = asyncio.create_task(a_forever_loop())
    task2 = asyncio.create_task(a_function_that_sometimes_needs_to_run())
    await task1
    await task2
asyncio.run(main())