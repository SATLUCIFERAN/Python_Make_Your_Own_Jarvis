
import httpx
import asyncio 


# 1. Define the asynchronous function (coroutine)

async def fetch_report(api_url: str, name: str):    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, timeout=5)         
    print(f"[{name}] Data received! Status: {response.status_code}")
    return len(response.text)

# 2. Define the main function that coordinates the tasks

async def main():
    stock_api = "https://httpbin.org/delay/3" 
    weather_api = "https://httpbin.org/delay/1" 

    print("J.A.R.V.I.S. begins fetching tasks...")
    start_time = asyncio.get_event_loop().time()    
    sizes = await asyncio.gather(
        fetch_report(stock_api, "Stocks"),
        fetch_report(weather_api, "Weather")
    )
    end_time = asyncio.get_event_loop().time()    
    print(f"\nTotal concurrent fetch time: {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    asyncio.run(main())