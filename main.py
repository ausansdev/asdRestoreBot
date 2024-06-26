import uuid
import os
import json
import discord
from discord.ext import commands
from src.configuration import *
import requests

bot = commands.Bot(command_prefix="€$*-+!", intents=discord.Intents.all())

with open("src/translation.py", "r") as f:
    translations = {}
    exec(f.read(), globals(), translations)

@bot.tree.command(name="backup", description=translations["backup_description"])
async def backup(interaction: discord.Interaction):
    data = {}
    guild = interaction.guild

    backup_id = str(uuid.uuid4())

    data["roles"] = [{"name": role.name, "permissions": role.permissions.value} for role in guild.roles]

    data["channels"] = [{"name": channel.name, "type": channel.type, "position": channel.position} for channel in guild.channels]

    data["categories"] = [{"name": category.name, "channels": [channel.name for channel in category.channels]} for category in guild.categories]

    data["webhooks"] = [{"name": webhook.name, "url": webhook.url} for webhook in await guild.webhooks()]

    data["guild_name"] = guild.name
    data["guild_icon"] = str(guild.icon.url)


    with open(f"src/backups/{backup_id}.json", "w") as f:
        json.dump(data, f, indent=4)

    await interaction.response.send_message(translations["backup_success"].format(backup_id))


@bot.tree.command(name="restore", description=translations["restore_description"])
async def restore(interaction: discord.Interaction, backup_id: str):
    await interaction.response.defer(thinking=True, ephemeral=True)
    try:
        if not os.path.exists(f"src/backups/{backup_id}.json"):
            await interaction.followup.send(translations["invalid_backup_id"])
            return

        with open(f"src/backups/{backup_id}.json", "r") as f:
            data = json.load(f)

        guild = interaction.guild

        if DELETE_CHANNELS_ROLES_ETC == True:
            for role in guild.roles:
                if role.name!= "@everyone":
                    print(role)
            for channel in guild.channels:
                await channel.delete()
            for category in guild.categories:
                await category.delete()

            for role_data in data["roles"]:
                role = await guild.create_role(name=role_data["name"], permissions=discord.Permissions(role_data["permissions"]))

            channel_positions = {}
            for channel_data in data["channels"]:
                channel = await guild.create_text_channel(channel_data["name"])
                channel_positions[channel_data["name"]] = channel

            for channel_data in data["channels"]:
                channel = channel_positions[channel_data["name"]]
                await channel.edit(position=channel_data["position"])

            category_positions = {}
            for category_data in data["categories"]:
                category = await guild.create_category(category_data["name"])
                category_positions[category_data["name"]] = category

            for category_data in data["categories"]:
                category = category_positions[category_data["name"]]
                await category.edit(position=category_data["position"])

            for category_data in data["categories"]:
                category = category_positions[category_data["name"]]
                for channel_name in category_data["channels"]:
                    channel = discord.utils.get(guild.channels, name=channel_name)
                    if channel:
                        await channel.edit(category=category)

            for webhook_data in data["webhooks"]:
                webhook = discord.utils.get(await guild.webhooks(), name=webhook_data["name"])
                if not webhook:
                    webhook = await guild.create_webhook(name=webhook_data["name"])

            await guild.edit(name=data["guild_name"])
            icon_url = data["guild_icon"]
            icon_response = requests.get(icon_url)
            icon_bytes = icon_response.content
            await guild.edit(icon=icon_bytes)

            channel = interaction.guild.channels[0]
            await channel.send(translations["restore_success"])
        else:
            for role_data in data["roles"]:
                role = await guild.create_role(name=role_data["name"], permissions=discord.Permissions(role_data["permissions"]))

            channel_positions = {}
            for channel_data in data["channels"]:
                channel = await guild.create_text_channel(channel_data["name"])
                channel_positions[channel_data["name"]] = channel

            for channel_data in data["channels"]:
                channel = channel_positions[channel_data["name"]]
                await channel.edit(position=channel_data["position"])

            category_positions = {}
            for category_data in data["categories"]:
                category = await guild.create_category(category_data["name"])
                category_positions[category_data["name"]] = category

            for category_data in data["categories"]:
                category = category_positions[category_data["name"]]
                await category.edit(position=category_data["position"])

            for category_data in data["categories"]:
                category = category_positions[category_data["name"]]
                for channel_name in category_data["channels"]:
                    channel = discord.utils.get(guild.channels, name=channel_name)
                    if channel:
                        await channel.edit(category=category)

            for webhook_data in data["webhooks"]:
                webhook = discord.utils.get(await guild.webhooks(), name=webhook_data["name"])
                if not webhook:
                    webhook = await guild.create_webhook(name=webhook_data["name"])

            await guild.edit(name=data["guild_name"])
            icon_url = data["guild_icon"]
            icon_response = requests.get(icon_url)
            icon_bytes = icon_response.content
            await guild.edit(icon=icon_bytes)

            channel = interaction.guild.channels[0]
            await channel.send(translations["restore_success"])
    except discord.Forbidden:
        await interaction.followup.send(translations["perms_error"])

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers"), status=discord.Status.idle)
    bot.tree.copy_global_to(guild=bot.guilds[0])
    await bot.tree.sync(guild=bot.guilds[0])

bot.run(TOKEN)