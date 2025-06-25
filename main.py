import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio
BOT_TOKEN = "MTM4NzA1MDA0MDU1NTQ3MTAwMA.GR-Tuv.OvEGU15smKdFDpC-bKUAah-Hsf7-bKYhmn-K7Y" 
EMBED_IMAGE_URL = "https://cdn.blacked.com/scene/videoimages/100024/mainLandscape/1538996342179/blacked-tiny-blonde-teen-takes-huge-black-cock_1920x1080.jpeg"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.guild_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def send_embed_to_owner(guild: discord.Guild, title: str, description: str, color: discord.Color):
    owner = guild.owner
    if owner is None:
        print(f"❌ Owner of '{guild.name}' not found.")
        return
    
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=f"Server: {guild.name}")
    embed.timestamp = datetime.utcnow()
    
    try:
        await owner.send(embed=embed)
        print(f"✅ DM sent to owner of '{guild.name}'.")
    except discord.Forbidden:
        print(f"❌ Owner of '{guild.name}' has DMs closed. Message could not be sent.")
    except Exception as e:
        print(f"❌ Failed to send DM: {e}")

@bot.event
async def on_ready():
    print(f"✅ Bot is online: {bot.user} Servers: {len(bot.guilds)}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} slash commands synced.")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")



@bot.event
async def on_guild_channel_create(channel: discord.abc.GuildChannel):
    guild = channel.guild
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
        if entry.target.id == channel.id:
            if entry.user and entry.user.id != guild.owner_id:
                print(f"Unauthorized channel creation: {entry.user} created {channel.name}")
                try:
                    await channel.delete(reason="Unauthorized channel creation")
                    print(f"✅ Unauthorized channel deleted: {channel.name}")
                except Exception as e:
                    print(f"❌ Failed to delete channel: {e}")
                
                try:
                    if not entry.user.bot:
                        await guild.kick(entry.user, reason="Unauthorized channel creation")
                        print(f"✅ Unauthorized user kicked: {entry.user}")
                        await send_embed_to_owner(guild, "🚫 Unauthorized Channel Creation", f"{entry.user.mention} created channel `{channel.name}` and has been kicked.", discord.Color.red())
                    else:
                        await send_embed_to_owner(guild, "⚠️ Suspicious Bot Activity", f"Bot `{entry.user.name}` created channel `{channel.name}`.", discord.Color.orange())
                except Exception as e:
                    print(f"❌ Kick failed: {e}")
            break

@bot.event
async def on_guild_channel_delete(channel: discord.abc.GuildChannel):
    guild = channel.guild
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
        if entry.target.id == channel.id:
            if entry.user and entry.user.id != guild.owner_id:
                print(f"Unauthorized channel deletion: {entry.user} deleted {channel.name}")
                try:
                    if not entry.user.bot:
                        await guild.kick(entry.user, reason="Unauthorized channel deletion")
                        print(f"✅ Unauthorized user kicked: {entry.user}")
                        await send_embed_to_owner(guild, "🚫 Unauthorized Channel Deletion", f"{entry.user.mention} deleted channel `{channel.name}` and has been kicked.", discord.Color.red())
                    else:
                        await send_embed_to_owner(guild, "⚠️ Suspicious Bot Activity", f"Bot `{entry.user.name}` deleted channel `{channel.name}`.", discord.Color.orange())
                except Exception as e:
                    print(f"❌ Kick failed: {e}")
            break

@bot.event
async def on_member_remove(member: discord.Member):
    guild = member.guild
    await bot.wait_until_ready()
    await asyncio.sleep(2)

    async for entry in guild.audit_logs(limit=3, action=discord.AuditLogAction.kick):
        if entry.target.id == member.id:
            if entry.user and entry.user.id != guild.owner_id:
                print(f"Unauthorized kick: {entry.user} kicked {member}")
                try:
                    if not entry.user.bot:
                        await guild.kick(entry.user, reason="Performed unauthorized kick")
                        print(f"✅ Unauthorized user kicked: {entry.user}")
                        await send_embed_to_owner(guild, "🚫 Unauthorized Kick", f"{entry.user.mention} kicked {member.mention} and has been kicked.", discord.Color.red())
                    else:
                        await send_embed_to_owner(guild, "⚠️ Suspicious Bot Activity", f"Bot `{entry.user.name}` kicked member `{member.name}`.", discord.Color.orange())
                except Exception as e:
                    print(f"❌ Kick failed: {e}")
            return

@bot.event
async def on_member_join(member: discord.Member):
    if member.bot:
        guild = member.guild
        entry = None
        try:
            async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                if log.target.id == member.id:
                    entry = log
                    break
        except Exception as e:
            print(f"Audit log error (on_member_join): {e}")

        if entry and entry.user and entry.user.id != guild.owner_id:
            print(f"Unauthorized bot addition: {entry.user} added {member}")
            try:
                dm_channel = await entry.user.create_dm()
                embed = discord.Embed(
                    title="🚫 Unauthorized Bot Addition!",
                    description=f"You have been **kicked** from the server for adding a bot without permission.\n\nIf you wish to add a bot, please contact the server owner.",
                    color=discord.Color.red()
                )
                embed.set_image(url=EMBED_IMAGE_URL)
                embed.set_footer(text=f"Server: {guild.name}")
                embed.timestamp = datetime.utcnow()
                try:
                    await dm_channel.send(embed=embed)
                    print(f"✅ {entry.user.name} sent DM.")
                except discord.Forbidden:
                    print(f"❌ {entry.user.name}'s DMs are closed. Message could not be sent.")
                except Exception as e:
                    print(f"❌ Failed to send DM: {e}")

                await member.kick(reason="Unauthorized bot")
                print(f"✅ Unauthorized bot kicked: {member.name}")
                await send_embed_to_owner(guild, "🚫 Unauthorized Bot Addition", f"{entry.user.mention} added an unauthorized bot {member.mention}, and the bot has been kicked. {entry.user.mention} has been kicked.", discord.Color.red())
                
                try:
                    if not entry.user.bot:
                        await guild.kick(entry.user, reason="Unauthorized bot addition")
                        print(f"✅ Unauthorized user kicked: {entry.user}")
                except Exception as e:
                    print(f"❌ User kick failed: {e}")

            except Exception as e:
                print(f"❌ Bot kick or DM failed: {e}")
        elif entry and entry.user:
            print(f"New bot added (by owner): {member.name}")
            await send_embed_to_owner(guild, "ℹ️ New Bot Added", f"Bot: {member.mention} added by {entry.user.mention}", discord.Color.blue())
        else:
             print(f"New bot added (without log): {member.name}")
             await send_embed_to_owner(guild, "ℹ️ New Bot Added", f"Bot: {member.mention} joined the server.", discord.Color.blue())



@bot.tree.command(name="serverinfo", description="Displays information about the server.")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("This command can only be used within a server.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"{guild.name} Server Information",
        description=f"Founded: {guild.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Member Count", value=guild.member_count, inline=True)
    embed.add_field(name="Channel Count", value=len(guild.channels), inline=True)
    embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Not found", inline=True)
    embed.add_field(name="Role Count", value=len(guild.roles), inline=True)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.set_footer(text=f"ID: {guild.id}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kick", description="Kicks a member from the server.")
@app_commands.describe(member="The member to kick", reason="Reason for kicking (optional)")
@app_commands.checks.has_permissions(administrator=True) # Only administrators can use this command
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
    if member.id == interaction.user.id:
        await interaction.response.send_message("You cannot kick yourself!", ephemeral=True)
        return
    if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("You cannot kick someone with an equal or higher role than yours.", ephemeral=True)
        return
    if member.id == interaction.guild.owner_id:
        await interaction.response.send_message("You cannot kick the server owner!", ephemeral=True)
        return
    
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="✅ Member Kicked",
            description=f"{member.mention} has been kicked.\n**Reason:** {reason}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        await send_embed_to_owner(interaction.guild, "ℹ️ Member Kicked", f"{interaction.user.mention} kicked {member.mention}. Reason: {reason}", discord.Color.orange())
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to kick members.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to kick: {e}", ephemeral=True)

@bot.tree.command(name="ban", description="Bans a member from the server.")
@app_commands.describe(member="The member to ban", reason="Reason for banning (optional)")
@app_commands.checks.has_permissions(administrator=True) 
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
    if member.id == interaction.user.id:
        await interaction.response.send_message("You cannot ban yourself!", ephemeral=True)
        return
    if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("You cannot ban someone with an equal or higher role than yours.", ephemeral=True)
        return
    if member.id == interaction.guild.owner_id:
        await interaction.response.send_message("You cannot ban the server owner!", ephemeral=True)
        return

    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="✅ Member Banned",
            description=f"{member.mention} has been banned.\n**Reason:** {reason}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        await send_embed_to_owner(interaction.guild, "ℹ️ Member Banned", f"{interaction.user.mention} banned {member.mention}. Reason: {reason}", discord.Color.orange())
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to ban members.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to ban: {e}", ephemeral=True)

@bot.tree.command(name="unban", description="Unbans a banned member.")
@app_commands.describe(user_id="The ID of the user to unban", reason="Reason for unbanning (optional)")
@app_commands.checks.has_permissions(administrator=True) 
async def unban(interaction: discord.Interaction, user_id: str, reason: str = "No reason provided."):
    try:
        user_id_int = int(user_id)
        user = await bot.fetch_user(user_id_int)
        
        if user is None:
            await interaction.response.send_message("No user found with that ID.", ephemeral=True)
            return

        banned_users = [entry.user async for entry in interaction.guild.bans()]
        if user not in banned_users:
            await interaction.response.send_message(f"{user.mention} is not banned.", ephemeral=True)
            return

        await interaction.guild.unban(user, reason=reason)
        embed = discord.Embed(
            title="✅ Member Unbanned",
            description=f"{user.mention} has been unbanned.\n**Reason:** {reason}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        await send_embed_to_owner(interaction.guild, "ℹ️ Member Unbanned", f"{interaction.user.mention} unbanned {user.mention}. Reason: {reason}", discord.Color.orange())
    except ValueError:
        await interaction.response.send_message("Please provide a valid user ID.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to unban members.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to unban: {e}", ephemeral=True)

@bot.tree.command(name="clear", description="Deletes a specified number of messages.")
@app_commands.describe(amount="Number of messages to delete (1-100)")
@app_commands.checks.has_permissions(administrator=True) 
async def clear(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
    try:
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        embed = discord.Embed(
            title="✅ Messages Cleared",
            description=f"{len(deleted)} messages have been deleted in this channel.",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed)
        await send_embed_to_owner(interaction.guild, "ℹ️ Messages Cleared", f"{interaction.user.mention} cleared {len(deleted)} messages from `{interaction.channel.name}`.", discord.Color.orange())
    except discord.Forbidden:
        await interaction.followup.send("I do not have permission to delete messages.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Failed to clear messages: {e}", ephemeral=True)

@bot.tree.command(name="mute", description="Mutes a member for a specified duration.")
@app_commands.describe(member="The member to mute", duration_minutes="Duration in minutes to mute", reason="Reason for muting (optional)")
@app_commands.checks.has_permissions(administrator=True)
async def mute(interaction: discord.Interaction, member: discord.Member, duration_minutes: int, reason: str = "No reason provided."):
    if member.id == interaction.user.id:
        await interaction.response.send_message("You cannot mute yourself!", ephemeral=True)
        return
    if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("You cannot mute someone with an equal or higher role than yours.", ephemeral=True)
        return
    if member.id == interaction.guild.owner_id:
        await interaction.response.send_message("You cannot mute the server owner!", ephemeral=True)
        return

    try:
        duration = datetime.timedelta(minutes=duration_minutes)
        await member.timeout(duration, reason=reason)
        embed = discord.Embed(
            title="✅ Member Muted",
            description=f"{member.mention} has been muted for {duration_minutes} minutes.\n**Reason:** {reason}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        await send_embed_to_owner(interaction.guild, "ℹ️ Member Muted", f"{interaction.user.mention} muted {member.mention}. Reason: {reason}", discord.Color.orange())
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to mute members.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to mute: {e}", ephemeral=True)

@bot.tree.command(name="unmute", description="Unmutes a muted member.")
@app_commands.describe(member="The member to unmute", reason="Reason for unmuting (optional)")
@app_commands.checks.has_permissions(administrator=True) 
async def unmute(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
    if not member.is_timed_out():
        await interaction.response.send_message(f"{member.mention} is not currently muted.", ephemeral=True)
        return

    try:
        await member.timeout(None, reason=reason)
        embed = discord.Embed(
            title="✅ Member Unmuted",
            description=f"{member.mention} has been unmuted.\n**Reason:** {reason}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        await send_embed_to_owner(interaction.guild, "ℹ️ Member Unmuted", f"{interaction.user.mention} unmuted {member.mention}. Reason: {reason}", discord.Color.orange())
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to unmute members.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to unmute: {e}", ephemeral=True)

@bot.tree.command(name="create_text_channel", description="Creates a new text channel.")
@app_commands.describe(name="Name of the channel")
@app_commands.checks.has_permissions(administrator=True) 
async def create_text_channel(interaction: discord.Interaction, name: str):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("This command can only be used within a server.", ephemeral=True)
        return
    try:
        channel = await guild.create_text_channel(name)
        embed = discord.Embed(
            title="✅ Channel Created",
            description=f"Text channel {channel.mention} has been created.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        await send_embed_to_owner(guild, "ℹ️ New Channel Created", f"{interaction.user.mention} created new text channel `{channel.name}`.", discord.Color.blue())
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to create channels.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to create channel: {e}", ephemeral=True)

@bot.tree.command(name="create_voice_channel", description="Creates a new voice channel.")
@app_commands.describe(name="Name of the channel")
@app_commands.checks.has_permissions(administrator=True) 
async def create_voice_channel(interaction: discord.Interaction, name: str):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("This command can only be used within a server.", ephemeral=True)
        return
    try:
        channel = await guild.create_voice_channel(name)
        embed = discord.Embed(
            title="✅ Channel Created",
            description=f"Voice channel `{channel.name}` has been created.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        await send_embed_to_owner(guild, "ℹ️ New Channel Created", f"{interaction.user.mention} created new voice channel `{channel.name}`.", discord.Color.blue())
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to create channels.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to create channel: {e}", ephemeral=True)

@bot.tree.command(name="create_role", description="Creates a new role.")
@app_commands.describe(name="Name of the role", color_hex="Hex color code for the role (e.g., #FF0000)", mentionable="Can the role be @mentioned?")
@app_commands.checks.has_permissions(administrator=True) 
async def create_role(interaction: discord.Interaction, name: str, color_hex: str = "#000000", mentionable: bool = False):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("This command can only be used within a server.", ephemeral=True)
        return
    
    try:
        color = discord.Color(int(color_hex.lstrip('#'), 16))
    except ValueError:
        await interaction.response.send_message("Please provide a valid hex color code (e.g., #FF0000).", ephemeral=True)
        return

    try:
        role = await guild.create_role(name=name, color=color, mentionable=mentionable)
        embed = discord.Embed(
            title="✅ Role Created",
            description=f"Role {role.mention} has been created.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        await send_embed_to_owner(guild, "ℹ️ New Role Created", f"{interaction.user.mention} created new role `{role.name}`.", discord.Color.blue())
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to create roles.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to create role: {e}", ephemeral=True)

@bot.tree.command(name="add_role", description="Gives a role to a member.")
@app_commands.describe(member="The member to give the role to", role="The role to give")
@app_commands.checks.has_permissions(administrator=True) #
async def add_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("You cannot assign a role equal to or higher than your highest role.", ephemeral=True)
        return
    if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("You cannot assign a role to someone with an equal or higher role than yours.", ephemeral=True)
        return

    try:
        await member.add_roles(role)
        embed = discord.Embed(
            title="✅ Role Given",
            description=f"{member.mention} has been given the {role.mention} role.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        await send_embed_to_owner(interaction.guild, "ℹ️ Role Given", f"{interaction.user.mention} gave {member.mention} the `{role.name}` role.", discord.Color.blue())
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to manage roles.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to add role: {e}", ephemeral=True)

@bot.tree.command(name="remove_role", description="Removes a role from a member.")
@app_commands.describe(member="The member to remove the role from", role="The role to remove")
@app_commands.checks.has_permissions(administrator=True) 
async def remove_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("You cannot remove a role equal to or higher than your highest role.", ephemeral=True)
        return
    if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("You cannot remove a role from someone with an equal or higher role than yours.", ephemeral=True)
        return
        
    try:
        await member.remove_roles(role)
        embed = discord.Embed(
            title="✅ Role Removed",
            description=f"The {role.mention} role has been removed from {member.mention}.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        await send_embed_to_owner(interaction.guild, "ℹ️ Role Removed", f"{interaction.user.mention} removed the `{role.name}` role from {member.mention}.", discord.Color.blue())
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to manage roles.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to remove role: {e}", ephemeral=True)

@bot.tree.command(name="ping", description="Shows the bot's latency.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! 🏓 `{round(bot.latency * 1000)}ms`", ephemeral=True)

@bot.tree.command(name="userinfo", description="Displays information about a user.")
@app_commands.describe(member="The member to view information for (optional)")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(
        title=f"{member.name}'s Information",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="Discriminator", value=member.discriminator, inline=True)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Joined Discord", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    if roles:
        embed.add_field(name="Roles", value=", ".join(roles), inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Shows the bot's commands.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Bot Command List",
        description="Here's a list of my important commands:",
        color=discord.Color.purple()
    )
    embed.add_field(name="/serverinfo", value="Displays information about the server.", inline=False)
    embed.add_field(name="/userinfo [member]", value="Displays information about a user.", inline=False)
    embed.add_field(name="/kick <member> [reason]", value="Kicks a member from the server.", inline=False)
    embed.add_field(name="/ban <member> [reason]", value="Bans a member from the server.", inline=False)
    embed.add_field(name="/unban <user_id> [reason]", value="Unbans a banned member.", inline=False)
    embed.add_field(name="/clear <amount>", value="Deletes a specified number of messages.", inline=False)
    embed.add_field(name="/mute <member> <duration_minutes> [reason]", value="Mutes a member for a specified duration.", inline=False)
    embed.add_field(name="/unmute <member> [reason]", value="Unmutes a muted member.", inline=False)
    embed.add_field(name="/create_text_channel <name>", value="Creates a new text channel.", inline=False)
    embed.add_field(name="/create_voice_channel <name>", value="Creates a new voice channel.", inline=False)
    embed.add_field(name="/create_role <name> [color_hex] [mentionable]", value="Creates a new role.", inline=False)
    embed.add_field(name="/add_role <member> <role>", value="Gives a role to a member.", inline=False)
    embed.add_field(name="/remove_role <member> <role>", value="Removes a role from a member.", inline=False)
    embed.add_field(name="/ping", value="Shows the bot's latency.", inline=False)

    embed.set_footer(text="This bot is designed to help with server security.")
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
