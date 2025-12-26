import os


async def load_cogs(client):
    base_path = "bot/cogs"
    for entry in os.listdir(base_path):
        full_path = os.path.join(base_path, entry)

        # If it's a folder with a .py file that matches the folder name, load it
        print(full_path)
        print(os.path.isdir(full_path))
        if os.path.isdir(full_path):
            module_path = os.path.join(full_path, f"{entry}.py")
            print(module_path)
            if os.path.exists(module_path):
                await client.load_extension(f"bot.cogs.{entry}.{entry}")
