import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import discord
from discord.ext import commands
from discord import app_commands
from utils.file_manager import get_user, update_user
from utils.embeds import success_embed, error_embed

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("🪙 admin.py đã được load")

    # Prefix: bzaddxu @user 100
    @commands.command(name="bzaddxu")
    @commands.has_permissions(administrator=True)
    async def add_xu_prefix(self, ctx, member: discord.Member, amount: int):
        user = get_user(member.id)
        user["xu"] += amount
        update_user(member.id, user)
        await ctx.send(embed=success_embed(f"💰 Đã cộng **{amount} xu tình yêu** cho {member.mention}!"))

    # Slash: /addxu user: @user amount: 100
    @app_commands.command(name="addxu", description="Cộng xu tình yêu cho người chơi (admin).")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_xu_slash(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        data = get_user(user.id)
        data["xu"] += amount
        update_user(user.id, data)
        await interaction.response.send_message(
            embed=success_embed(f"💖 Đã cộng **{amount} xu tình yêu** cho {user.mention}!"),
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
