import discord
from discord.ext import commands
from utils.file_manager import get_user
from utils.embeds import error_embed
import random

# Một vài khung đôi / gif đẹp (có thể thêm tuỳ thích)
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

        # Trạng thái mối quan hệ
        if user_data.get("married"):
            status = "💍 **Đã cưới**"
        else:
            status = "💘 **Đang hẹn hò**"

        # Lấy ảnh khung đôi ngẫu nhiên
        frame = random.choice(COUPLE_FRAMES)

        # Tạo Embed đẹp
        embed = discord.Embed(
            title="💖 HỒ SƠ CẶP ĐÔI 💖",
            description=f"🌸 Câu chuyện tình yêu của {user_member.mention} và {partner_member.mention} 🌸",
            color=0xFF69B4
        )

        embed.add_field(name="💞 Tên hai bạn", value=f"{user_member.name} ❤️ {partner_member.name}", inline=False)
        embed.add_field(name="💓 Điểm thân mật", value=f"**{user_data['intimacy']}** điểm", inline=True)
        embed.add_field(name="💰 Xu tình yêu (bạn)", value=f"{user_data['xu']} xu", inline=True)
        embed.add_field(name="💰 Xu tình yêu (người yêu)", value=f"{partner_data['xu']} xu", inline=True)
        embed.add_field(name="📜 Trạng thái", value=status, inline=False)

        embed.set_image(url=frame)
        embed.set_footer(text="💗 Hãy yêu và được yêu 💗")

        # Ảnh đại diện 2 người làm thumbnail
        if user_member.avatar and partner_member.avatar:
            embed.set_thumbnail(url=user_member.avatar.url)
            embed.set_author(name=f"{user_member.name} 💕 {partner_member.name}", icon_url=partner_member.avatar.url)

        await interaction.response.send_message(embed=embed, ephemeral=False)


async def setup(bot):
    await bot.add_cog(Profile(bot))
