import os
import re

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from utils.item_database_manager import ItemDatabaseManager
from utils.item_database_manager.models import Item

load_dotenv()
TOKEN = os.environ['DISCORD_TOKEN']
WHITELIST = [int(channel_id) for channel_id in
             os.getenv('CHANNELS_WHITELIST').split(',')]
DATABASE_URL = os.environ['DATABASE_URL']

intents = intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
database_manager = ItemDatabaseManager(DATABASE_URL)


@bot.event
async def on_ready():
    print(f'Bot has logged in as {bot.user}')


@bot.tree.command(name='sync', description='Synchronize all commands')
@commands.is_owner()
async def sync(interaction: discord.Interaction):
    synced = await bot.tree.sync()
    await interaction.response.send_message(
        f'Synced {len(synced)} command(s)', ephemeral=True)


@bot.tree.command(name='search_item', description='Searches for an equipment by query')
@app_commands.describe(query='Name or ID of an equipment')
async def search_item(interaction: discord.Interaction, query: str):
    if interaction.channel_id not in WHITELIST:
        await interaction.response.send_message(
            'You can\'t use bot commands here', ephemeral=True)
        return

    await interaction.response.defer()
    async with database_manager:
        if re.match(r'^[1-9]\d*$', query):
            item = await database_manager.get_item(int(query))
            if item is not None:
                await _handle_item(interaction, item)
                return
        else:
            items = await database_manager.search_items(query)
            if items:
                if len(items) > 1:
                    await _handle_items(interaction, items)
                else:
                    await _handle_item(interaction, items[0])
                return

    await interaction.followup.send(f'**❌ Nothing found for** `{query}`')


async def _handle_item(interaction: discord.Interaction, item: Item) -> None:

    DAMAGE_TYPE_EMOJIS = {
        'Physical': '🗡️',
        'Fire': '🔥',
        'Ice': '❄️',
        'Energy': '🔯',
        'Light': '⚡',
        'Poison': '☠️',
        None: ''
    }

    damage_type_emoji = DAMAGE_TYPE_EMOJIS[item.damage_type]
    rarity = item.rarity * '⭐'
    embed = discord.Embed(title=f'{item.title} {damage_type_emoji}\n{rarity}',
                          color=discord.Color.blue())

    item_properties = await database_manager.get_item_properties(item)
    for property_ in item_properties:
        embed.add_field(name=property_.name,
                        value=property_.value,
                        inline=True)

    item_skills = await database_manager.get_item_skills(item)
    for skill in item_skills:
        damage_type_emoji = DAMAGE_TYPE_EMOJIS[skill.damage_type]
        embed.add_field(name=f'{skill.title} {damage_type_emoji}',
                        value=skill.description,
                        inline=False)

    embed.set_thumbnail(url=item.icon_url)
    embed.set_author(name=f'No. {item.item_id}')

    await interaction.followup.send(embed=embed)


async def _handle_items(interaction: discord.Interaction, items: list[Item]) -> None:
    items = items[:20]
    formatted_items = "\n".join(f'`- {item.title} [ID: {item.id}] {item.rarity}⭐`'
                                for item in items)
    response = f'**✅ Multiple items found:**\n{formatted_items}\
                \n***please use **`/search_item [ID]`** to select a specific item***'

    await interaction.followup.send(response)


if __name__ == '__main__':
    bot.run(TOKEN)
