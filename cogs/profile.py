import discord
from discord.ext import commands
from utils.file_manager import get_user, save_user
from utils.embeds import error_embed
import random

# Danh sách khung ảnh couple
FRAMES_SHOP = {
    "frame_basic": {
        "name": "💕 Khung Cơ Bản",
        "price": 0,
        "url": "https://media.tenor.com/GFJg0P5OljEAAAAC/love-couple.gif",
        "description": "Khung mặc định cho mọi cặp đôi"
    },
    "frame_cute": {
        "name": "🌸 Khung Dễ Thương",
        "price": 500,
        "url": "https://media.tenor.com/ExlcsKkFAtUAAAAC/cute-anime-couple.gif",
        "description": "Khung anime couple siêu đáng yêu"
    },
    "frame_romantic": {
        "name": "💖 Khung Lãng Mạn",
        "price": 1000,
        "url": "https://media.tenor.com/KSH5iQ2KzfwAAAAC/anime-couple-love.gif",
        "description": "Khung tình yêu lãng mạn ngọt ngào"
    },
    "frame_luxury": {
        "name": "💎 Khung Sang Trọng",
        "price": 2000,
        "url": "https://media.tenor.com/kcR14mcX2nUAAAAC/anime-couple.gif",
        "description": "Khung cao cấp dành cho đôi VIP"
    },
    "frame_sakura": {
        "name": "🌸 Khung Hoa Anh Đào",
        "price": 1500,
        "url": "https://media.tenor.com/7vKQH_RgC9AAAAAC/anime-couple-kiss.gif",
        "description": "Khung mùa xuân lãng mạn Nhật Bản"
    },
    "frame_starry": {
        "name": "⭐ Khung Đêm Sao",
        "price": 1800,
        "url": "https://media.tenor.com/dZW9JqH0JAYAAAAC/anime-couple-love.gif",
        "description": "Khung đêm đầy sao cho couple mơ mộng"
    }
}

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

        # Lấy khung ảnh đang dùng (mặc định là frame_basic)
        current_frame = user_data.get("current_frame", "frame_basic")
        frame_url = FRAMES_SHOP.get(current_frame, FRAMES_SHOP["frame_basic"])["url"]
        frame_name = FRAMES_SHOP.get(current_frame, FRAMES_SHOP["frame_basic"])["name"]

        # Trạng thái mối quan hệ
        if user_data.get("married"):
            status = "💍 **Đã kết hôn**"
            status_icon = "💍"
        else:
            status = "💘 **Đang hẹn hò**"
            status_icon = "💘"

        # Tính cấp độ tình yêu dựa trên điểm thân mật
        intimacy = user_data.get("intimacy", 0)
        level = intimacy // 100 + 1  # Mỗi 100 điểm = 1 level
        progress = intimacy % 100  # Tiến trình đến level tiếp theo

        # Tạo thanh progress bar
        progress_bar = self.create_progress_bar(progress, 100)

        # Tạo Embed đẹp
        embed = discord.Embed(
            title=f"{status_icon} HỒ SƠ CẶP ĐÔI {status_icon}",
            description=f"💖 **{user_member.name}** ❤️ **{partner_member.name}** 💖",
            color=0xFF1493
        )

        # Thông tin couple
        embed.add_field(
            name="💞 Cấp độ tình yêu",
            value=f"**Level {level}** ⭐\n{progress_bar} {progress}/100",
            inline=False
        )

        embed.add_field(
            name="💓 Điểm thân mật",
            value=f"**{intimacy}** điểm",
            inline=True
        )

        embed.add_field(
            name="📜 Trạng thái",
            value=status,
            inline=True
        )

        embed.add_field(
            name="🖼️ Khung hiện tại",
            value=frame_name,
            inline=True
        )

        # Tài sản của 2 người
        embed.add_field(
            name=f"💰 Xu của {user_member.name}",
            value=f"{user_data.get('xu', 0)} xu",
            inline=True
        )

        embed.add_field(
            name=f"💰 Xu của {partner_member.name}",
            value=f"{partner_data.get('xu', 0)} xu",
            inline=True
        )

        # Số quà đã tặng nhau (nếu có tracking)
        gifts_given = user_data.get("gifts_given", 0)
        embed.add_field(
            name="🎁 Quà đã tặng",
            value=f"{gifts_given} món",
            inline=True
        )

        # Set khung ảnh
        embed.set_image(url=frame_url)
        
        # Ảnh đại diện 2 người
        if user_member.avatar and partner_member.avatar:
            embed.set_thumbnail(url=user_member.avatar.url)
            embed.set_author(
                name=f"{user_member.name} 💕 {partner_member.name}",
                icon_url=partner_member.avatar.url
            )

        embed.set_footer(text="💗 Tình yêu là điều kỳ diệu nhất 💗")

        await interaction.response.send_message(embed=embed, ephemeral=False)

    def create_progress_bar(self, current, total, length=10):
        """Tạo thanh progress bar"""
        filled = int((current / total) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"`{bar}`"

    @commands.command(name="changeframe")
    async def change_frame(self, ctx, frame_id: str = None):
        """Đổi khung ảnh couple - Cả 2 người trong cặp đều có thể đổi"""
        user_data = get_user(ctx.author.id)
        partner_id = user_data.get("love_partner")

        if not partner_id:
            await ctx.send(embed=error_embed("💔 Bạn chưa có người yêu!"))
            return

        if not frame_id:
            # Hiển thị danh sách khung đã sở hữu
            owned_frames = user_data.get("owned_frames", ["frame_basic"])
            embed = discord.Embed(
                title="🖼️ Khung ảnh đã sở hữu",
                description="Dùng lệnh: `bzchangeframe <id>` để đổi khung",
                color=0xFF69B4
            )
            
            for frame_id in owned_frames:
                frame = FRAMES_SHOP.get(frame_id)
                if frame:
                    embed.add_field(
                        name=frame["name"],
                        value=f"ID: `{frame_id}`",
                        inline=True
                    )
            
            await ctx.send(embed=embed)
            return

        # Kiểm tra xem có sở hữu khung này không
        owned_frames = user_data.get("owned_frames", ["frame_basic"])
        if frame_id not in owned_frames:
            await ctx.send(embed=error_embed(f"❌ Bạn chưa sở hữu khung này! Hãy mua tại shop."))
            return

        if frame_id not in FRAMES_SHOP:
            await ctx.send(embed=error_embed(f"❌ Khung `{frame_id}` không tồn tại!"))
            return

        # Đổi khung cho cả 2 người
        user_data["current_frame"] = frame_id
        save_user(ctx.author.id, user_data)

        partner_data = get_user(partner_id)
        partner_data["current_frame"] = frame_id
        save_user(partner_id, partner_data)

        frame_name = FRAMES_SHOP[frame_id]["name"]
        
        embed = discord.Embed(
            title="✅ Đổi khung thành công!",
            description=f"Đã đổi khung couple thành {frame_name}",
            color=0x00FF00
        )
        embed.set_image(url=FRAMES_SHOP[frame_id]["url"])
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))
