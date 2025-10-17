import discord
from discord.ext import commands
from utils.file_manager import get_user
from utils.embeds import error_embed
import random
from datetime import datetime

COUPLE_FRAMES = [
    "https://media.tenor.com/GFJg0P5OljEAAAAC/love-couple.gif",
    "https://media.tenor.com/ExlcsKkFAtUAAAAC/cute-anime-couple.gif",
    "https://media.tenor.com/KSH5iQ2KzfwAAAAC/anime-couple-love.gif",
    "https://media.tenor.com/kcR14mcX2nUAAAAC/anime-couple.gif"
]

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("💞 profile.py đã được load")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Khi bấm nút '👩‍❤️‍👨 Hồ sơ couple'"""
        if not interaction.data or "custom_id" not in interaction.data:
            return
        if interaction.data["custom_id"] == "profile":
            await self.show_profile(interaction)

    async def show_profile(self, interaction: discord.Interaction):
        user_data = get_user(interaction.user.id)
        partner_id = user_data.get("love_partner")
        
        if not partner_id:
            await interaction.response.send_message(
                embed=error_embed("💔 Bạn chưa có người yêu! Hãy tỏ tình trước đã nhé 💌"),
                ephemeral=True
            )
            return

        partner_data = get_user(partner_id)
        partner_member = interaction.guild.get_member(partner_id)
        user_member = interaction.guild.get_member(interaction.user.id)

        # Tính ngày yêu nhau
        relationship_days = user_data.get("relationship_days", 0)
        
        # Trạng thái mối quan hệ
        if user_data.get("married"):
            status = "💍 Đã cưới"
            status_color = 0xFFD700
        else:
            status = "💘 Đang hẹn hò"
            status_color = 0xFF69B4

        # Lấy ảnh khung đôi ngẫu nhiên
        frame = random.choice(COUPLE_FRAMES)

        # Tạo Embed chuyên nghiệp
        embed = discord.Embed(
            title="✨ HỒ SƠ CẶP ĐÔI ✨",
            color=status_color,
            timestamp=datetime.now()
        )

        # Header với tên hai người
        embed.description = (
            f"```\n"
            f"{user_member.name} 💕 {partner_member.name}\n"
            f"```"
        )

        # Phần trạng thái
        embed.add_field(
            name="👑 Trạng thái quan hệ",
            value=status,
            inline=False
        )

        # Thống kê tình yêu
        embed.add_field(
            name="💞 Điểm thân mật",
            value=f"`{user_data['intimacy']}` ⭐",
            inline=True
        )

        embed.add_field(
            name="📅 Ngày yêu nhau",
            value=f"`{relationship_days}` ngày",
            inline=True
        )

        embed.add_field(
            name="💎 Tổng xu yêu",
            value=f"`{user_data['xu'] + partner_data['xu']}` xu 💰",
            inline=True
        )

        # Chi tiết từng người
        embed.add_field(
            name=f"👤 {user_member.name}",
            value=f"**Xu:** `{user_data['xu']}`\n**Cấp độ:** `Lv. {user_data.get('level', 1)}`",
            inline=True
        )

        embed.add_field(
            name=f"👤 {partner_member.name}",
            value=f"**Xu:** `{partner_data['xu']}`\n**Cấp độ:** `Lv. {partner_data.get('level', 1)}`",
            inline=True
        )

        # Khung hình
        embed.set_image(url=frame)

        # Avatar
        if user_member.avatar and partner_member.avatar:
            embed.set_thumbnail(url=user_member.avatar.url)
            embed.set_author(
                name=f"{user_member.name} 💕 {partner_member.name}",
                icon_url=partner_member.avatar.url
            )

        embed.set_footer(
            text="💗 Yêu thương và được yêu là hạnh phúc | Hồ sơ cặp đôi",
            icon_url=interaction.guild.icon.url if interaction.guild.icon else None
        )

        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Profile(bot))
