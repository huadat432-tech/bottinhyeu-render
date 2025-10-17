import discord
from discord.ext import commands
from discord.ui import View, Button
import json
import random
from utils.file_manager import get_user, update_user, load_data, save_data
from utils.embeds import love_embed, success_embed, error_embed


class SetLoveView(View):
    """View gồm nút chấp nhận / từ chối lời tỏ tình"""
    def __init__(self, lover_id, target_id):
        super().__init__(timeout=60)
        self.lover_id = lover_id
        self.target_id = target_id

    @discord.ui.button(label="💘 Chấp nhận", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("❌ Bạn không phải người được tỏ tình!", ephemeral=True)
            return

        data = load_data()

        lover = str(self.lover_id)
        target = str(self.target_id)

        # Nếu 1 trong 2 người đã có người yêu
        if data[lover]["love_partner"] or data[target]["love_partner"]:
            await interaction.response.send_message("💔 Một trong hai bạn đã có người yêu rồi!", ephemeral=True)
            return

        # Cập nhật dữ liệu
        data[lover]["love_partner"] = self.target_id
        data[target]["love_partner"] = self.lover_id
        save_data(data)

        gif_url = "https://media.tenor.com/-bT34mCszlUAAAAd/hearts-love.gif"
        desc = f"💞 **{interaction.user.mention}** và **<@{self.lover_id}>** đã chính thức trở thành một cặp đôi!\n\n💘 Chúc hai bạn mãi hạnh phúc 💖"

        embed = love_embed(desc)
        embed.set_image(url=gif_url)
        await interaction.response.edit_message(embed=embed, view=None)
        await interaction.channel.send(f"🎉 Mọi người ơi, {interaction.user.mention} và <@{self.lover_id}> vừa thành đôi! 💞")

    @discord.ui.button(label="💔 Từ chối", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("❌ Bạn không phải người được tỏ tình!", ephemeral=True)
            return

        gif_url = "https://media.tenor.com/XF3b4dyWj9sAAAAC/broken-heart.gif"
        embed = love_embed(f"💔 **{interaction.user.mention}** đã từ chối tình cảm của **<@{self.lover_id}>**...\nDuyên chưa tới rồi 😢")
        embed.set_image(url=gif_url)
        await interaction.response.edit_message(embed=embed, view=None)


class BreakUpView(View):
    """View gồm nút đồng ý chia tay / suy nghĩ lại"""
    def __init__(self, lover_id, partner_id):
        super().__init__(timeout=60)
        self.lover_id = lover_id
        self.partner_id = partner_id

    @discord.ui.button(label="💔 Đồng ý chia tay", style=discord.ButtonStyle.danger)
    async def accept_breakup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in [self.lover_id, self.partner_id]:
            await interaction.response.send_message("❌ Bạn không liên quan đến mối quan hệ này!", ephemeral=True)
            return

        data = load_data()
        lover = str(self.lover_id)
        partner = str(self.partner_id)

        # Xóa người yêu
        data[lover]["love_partner"] = None
        data[partner]["love_partner"] = None
        save_data(data)

        gif_url = "https://media.tenor.com/XF3b4dyWj9sAAAAC/broken-heart.gif"
        desc = f"💔 **<@{self.lover_id}>** và **<@{self.partner_id}>** đã chia tay...\nChúc cả hai sớm tìm thấy hạnh phúc mới!"

        embed = love_embed(desc)
        embed.set_image(url=gif_url)
        await interaction.response.edit_message(embed=embed, view=None)
        await interaction.channel.send(f"💔 {interaction.user.mention} đã xác nhận chia tay với đối phương.")

    @discord.ui.button(label="🤔 Suy nghĩ lại", style=discord.ButtonStyle.secondary)
    async def reconsider(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in [self.lover_id, self.partner_id]:
            await interaction.response.send_message("❌ Bạn không liên quan đến mối quan hệ này!", ephemeral=True)
            return

        await interaction.response.send_message("💖 Quyết định chưa được thực hiện. Hãy suy nghĩ kỹ trước khi chia tay!", ephemeral=True)


class Love(commands.Cog):
    """Xử lý tỏ tình, chấp nhận, từ chối và chia tay"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("💌 love.py đã được load")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Xử lý khi bấm nút '💌 Tỏ tình' từ menu chính"""
        if not interaction.data or "custom_id" not in interaction.data:
            return

        if interaction.data["custom_id"] == "love":
            await self.open_love_menu(interaction)

    async def open_love_menu(self, interaction: discord.Interaction):
        """Hiển thị form tỏ tình"""
        embed = love_embed("💌 **Nhập ID hoặc tag người bạn muốn tỏ tình** 💞\n(Ví dụ: `@User` hoặc `123456789012345678`)")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name="love")
    async def setlove_command(self, ctx, member: discord.Member = None):
        """(Tuỳ chọn) Lệnh thủ công: bzmenu love @user"""
        if member is None:
            await ctx.send(embed=error_embed("Hãy tag người bạn muốn tỏ tình!"))
            return

        await self.start_love(ctx, member)

    async def start_love(self, ctx, member: discord.Member):
        """Bắt đầu tỏ tình"""
        if member.bot:
            await ctx.send(embed=error_embed("Không thể tỏ tình với bot 😅"))
            return
        if member.id == ctx.author.id:
            await ctx.send(embed=error_embed("Bạn không thể tự tỏ tình với chính mình!"))
            return

        lover_data = get_user(ctx.author.id)
        target_data = get_user(member.id)

        if lover_data["love_partner"]:
            await ctx.send(embed=error_embed("💔 Bạn đã có người yêu rồi!"))
            return
        if target_data["love_partner"]:
            await ctx.send(embed=error_embed(f"💔 {member.mention} đã có người yêu mất rồi!"))
            return

        desc = f"💞 **{ctx.author.mention}** đang tỏ tình với **{member.mention}**!\n\n{member.mention}, bạn có chấp nhận lời tỏ tình này không?"
        embed = love_embed(desc)

        view = SetLoveView(ctx.author.id, member.id)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="chiatay")
    async def breakup_command(self, ctx, member: discord.Member = None):
        """Lệnh thủ công chia tay: bzchiatay @user"""
        if member is None:
            await ctx.send(embed=error_embed("Hãy tag người bạn muốn chia tay!"))
            return

        if member.id == ctx.author.id:
            await ctx.send(embed=error_embed("Bạn không thể chia tay chính mình!"))
            return

        lover_data = get_user(ctx.author.id)
        target_data = get_user(member.id)

        if lover_data["love_partner"] != member.id or target_data["love_partner"] != ctx.author.id:
            await ctx.send(embed=error_embed("💔 Hai bạn không phải là một cặp đôi!"))
            return

        desc = f"💔 **{ctx.author.mention}** muốn chia tay với **{member.mention}**!\n\n{member.mention}, bạn có đồng ý không?"
        embed = love_embed(desc)

        view = BreakUpView(ctx.author.id, member.id)
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Love(bot))
