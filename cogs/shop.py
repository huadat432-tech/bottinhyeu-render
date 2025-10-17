import discord
from discord.ext import commands
from utils.file_manager import get_user, update_user
from utils.embeds import error_embed
import os

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
        try:
            if not interaction.data or "custom_id" not in interaction.data:
                return
            
            if interaction.data["custom_id"] == "profile":
                await self.show_profile(interaction)
        except Exception as e:
            print(f"❌ Lỗi interaction profile: {e}")

    async def show_profile(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=False)
        except Exception as e:
            print(f"Lỗi defer: {e}")
            return

        try:
            user_data = get_user(interaction.user.id)
            partner_id = user_data.get("love_partner")
            
            if not partner_id:
                await interaction.followup.send(
                    embed=error_embed("💔 Bạn chưa có người yêu! Hãy tỏ tình trước đã nhé 💌"),
                    ephemeral=True
                )
                return

            partner_data = get_user(partner_id)
            partner_member = interaction.guild.get_member(partner_id)
            user_member = interaction.guild.get_member(interaction.user.id)

            if not user_member or not partner_member:
                await interaction.followup.send(
                    embed=error_embed("❌ Không tìm thấy thông tin thành viên"),
                    ephemeral=True
                )
                return

            # Lấy khung ảnh đang dùng
            current_frame = user_data.get("current_frame", "frame_basic")
            frame_data = FRAMES_SHOP.get(current_frame, FRAMES_SHOP["frame_basic"])
            frame_name = frame_data["name"]
            frame_url = frame_data["url"]

            # Trạng thái mối quan hệ
            if user_data.get("married"):
                status = "💍 Đã kết hôn"
                status_color = 0xFFD700
            else:
                status = "💘 Đang hẹn hò"
                status_color = 0xFF1493

            # Tính cấp độ tình yêu
            intimacy = user_data.get("intimacy", 0)
            level = intimacy // 100 + 1
            progress = intimacy % 100
            progress_bar = self.create_progress_bar(progress, 100)

            # Tạo embed chính
            embed = discord.Embed(
                title="💖 HỒ SƠ CẶP ĐÔI 💖",
                description=f"👨‍❤️‍👨 **{user_member.name}** 💕 **{partner_member.name}**\n\n{status}",
                color=status_color
            )
            
            # Hiển thị khung ảnh GIF
            embed.set_image(url=frame_url)
            
            # Avatar trái
            embed.set_thumbnail(url=user_member.avatar.url if user_member.avatar else "")
            
            # Tên tác giả với avatar phải
            embed.set_author(
                name=f"{user_member.name} 💕 {partner_member.name}",
                icon_url=partner_member.avatar.url if partner_member.avatar else ""
            )

            # Thông tin chi tiết
            embed.add_field(
                name="💞 Cấp độ tình yêu",
                value=f"**Level {level}** ⭐\n{progress_bar}\n{progress}/100 điểm",
                inline=False
            )

            embed.add_field(
                name="💓 Điểm thân mật",
                value=f"**{intimacy}** 💕",
                inline=True
            )

            embed.add_field(
                name="🖼️ Khung hiện tại",
                value=frame_name,
                inline=True
            )

            embed.add_field(
                name=f"💰 Xu của {user_member.name}",
                value=f"**{user_data.get('xu', 0)}** xu",
                inline=True
            )

            embed.add_field(
                name=f"💰 Xu của {partner_member.name}",
                value=f"**{partner_data.get('xu', 0)}** xu",
                inline=True
            )

            gifts_given = user_data.get("gifts_given", 0)
            embed.add_field(
                name="🎁 Quà đã tặng",
                value=f"**{gifts_given}** món",
                inline=True
            )

            embed.set_footer(text="💗 Tình yêu là điều kỳ diệu nhất 💗")

            await interaction.followup.send(embed=embed, ephemeral=False)

        except Exception as e:
            print(f"❌ Lỗi show_profile: {e}")
            try:
                await interaction.followup.send(
                    embed=error_embed(f"❌ Lỗi: {str(e)[:100]}"),
                    ephemeral=True
                )
            except:
                pass

    def create_progress_bar(self, current, total, length=10):
        """Tạo thanh progress bar"""
        filled = int((current / total) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"`{bar}`"

    @commands.command(name="mua_khung")
    async def buy_frame(self, ctx, frame_id: str):
        """Mua khung ảnh couple"""
        try:
            # Lấy thông tin người dùng
            user_data = get_user(ctx.author.id)
            partner_id = user_data.get("love_partner")
            
            if not partner_id:
                await ctx.send(embed=error_embed("💔 Bạn chưa có người yêu!"))
                return
            
            # Lấy khung và thông tin giá tiền
            frame = FRAMES_SHOP.get(frame_id)
            if not frame:
                await ctx.send(embed=error_embed("❌ Khung không hợp lệ!"))
                return
            
            price = frame["price"]
            
            # Kiểm tra xem người dùng có đủ xu để mua không
            if user_data.get("xu", 0) < price:
                await ctx.send(embed=error_embed(f"💸 Bạn không đủ xu để mua khung {frame['name']}!"))
                return
            
            # Cập nhật xu của người dùng
            user_data["xu"] -= price
            if "owned_frames" not in user_data:
                user_data["owned_frames"] = []
            
            if frame_id not in user_data["owned_frames"]:
                user_data["owned_frames"].append(frame_id)
            
            update_user(ctx.author.id, user_data)

            # Cập nhật khung cho partner nếu họ cũng sở hữu khung này
            partner_data = get_user(partner_id)
            if "owned_frames" not in partner_data:
                partner_data["owned_frames"] = []

            if frame_id not in partner_data["owned_frames"]:
                partner_data["owned_frames"].append(frame_id)

            update_user(partner_id, partner_data)

            # Thông báo thành công
            embed = discord.Embed(
                title="✅ Mua khung thành công!",
                description=f"Bạn đã mua thành công khung **{frame['name']}** cho
