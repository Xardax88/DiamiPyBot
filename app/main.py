import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

handler = discord.FileHandler(filename='error.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True     

bot = commands.Bot(command_prefix='>', intents=intents)



@bot.event
async def on_ready():
    
    print(f'{bot.user.name} se ha conectado a Discord!')
    print('Cargando cogs...')
    await load_all_cogs()
    print('------')

    try:
        # Sincroniza los comandos definidos en el árbol de la aplicación con Discord
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comando(s) slash.")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")


async def load_all_cogs():

    for filename in os.listdir('./cogs'):

        if filename.endswith('.py') and filename != '__init__.py':
            try:

                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'-> Cog cargado: {filename[:-3]}')
            except Exception as e:
                print(f'Error al cargar el cog {filename[:-3]}: {e}')

bot.run(TOKEN, log_handler=handler, log_level=discord.LogLevel.DEBUG)