import discord
from discord.ext import commands
from utils.file_manager import get_user, update_user
from utils.embeds import error_embed
import random
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import asyncio

# Danh sách khung ảnh couple
FRAMES_SHOP = {
    "frame_basic": {
        "name": "💕 Khung Cơ Bản",
        "price": 0,
        "url": "https://media.tenor.com/GFJg0P5OljEAAAAC/love-couple.gif",
        "description": "Khung mặc định cho mọi cặp đôi",
        "color": "#FFB6C1"
    },
    "frame_cute": {
        "name": "🌸 Khung Dễ Thương",
        "price": 500,
        "url": "https://media.tenor.com/ExlcsKkFAtUAAAAC/cute-anime-couple.gif",
        "description": "Khung anime couple siêu đáng yêu",
        "color": "#FFD700"
    },
    "frame_romantic": {
        "name": "💖 Khung Lãng Mạn",
        "price": 1000,
        "url": "https://media.tenor.com/KSH5iQ2KzfwAAAAC/anime-couple-love.gif",
        "description": "Khung tình yêu lãng mạn ngọt ngào",
        "color": "#FF1493"
    },
    "frame_luxury": {
        "name": "💎 Khung Sang Trọng",
        "price": 2000,
        "url": "https://media.tenor.com/kcR14mcX2nUAAAAC/anime-couple.gif",
        "description": "Khung cao cấp dành cho đôi VIP",
        "color": "#FFD700"
    },
    "frame_sakura": {
        "name": "🌸 Khung Hoa Anh Đào",
        "price": 1500,
        "url": "https://media.tenor.com/7vKQH_RgC9AAAAAC/anime-couple-kiss.gif",
        "description": "Khung mùa xuân lãng mạn Nhật Bản",
        "color": "#FFB6C1"
    },
    "frame_starry": {
        "name": "⭐ Khung Đêm Sao",
        "price": 1800,
        "url": "https://media.tenor.com/dZW9JqH0JAYAAAAC/anime-couple-love.gif",
        "description": "Khung đêm đầy sao cho couple mơ mộng",
        "color": "#4169E1"
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
        user_data = get_user(interaction.user.id)
        partner_id = user_data.get("love_partner")
        
        if not partner_id:
            try:
                await interaction.response.send_message(
                    embed=error_embed("💔 Bạn chưa có người yêu! Hãy tỏ tình trước đã nhé 💌"),
                    ephemeral=True
                )
            except:
                pass
            return

        # Defer để tránh timeout
        try:
            await interaction.response.defer(ephemeral=False)
        except Exception as e:
            print(f"⚠️ Lỗi defer: {e}")

        try:
            partner_data = get_user(partner_id)
            partner_member = interaction.guild.get_member(partner_id)
            user_member = interaction.guild.get_member(interaction.user.id)

            # Lấy khung ảnh đang dùng
            current_frame = user_data.get("current_frame", "frame_basic")
            frame_data = FRAMES_SHOP.get(current_frame, FRAMES_SHOP["frame_basic"])
            frame_name = frame_data["name"]
            frame_color = frame_data.get("color", "#FFB6C1")

            # Trạng thái mối quan hệ
            if user_data.get("married"):
                status = "💍 Đã kết hôn"
            else:
                status = "💘 Đang hẹn hò"

            # Tính cấp độ tình yêu
            intimacy = user_data.get("intimacy", 0)
            level = intimacy // 100 + 1
            progress = intimacy % 100

            # Tạo thanh progress bar
            progress_bar = self.create_progress_bar(progress, 100)

            # Download ảnh avatar
            user_avatar_url = user_member.avatar.url if user_member and user_member.avatar else None
            partner_avatar_url = partner_member.avatar.url if partner_member and partner_member.avatar else None
            
            # Tạo ảnh profile với khung
            profile_image = await self.create_profile_image(
                user_avatar_url, 
                partner_avatar_url,
                user_member.name if user_member else "User",
                partner_member.name if partner_member else "Partner",
                status,
                intimacy,
                frame_color
            )
            
            file = discord.File(profile_image, filename="profile.png")
            
            # Tạo embed
            embed = discord.Embed(
                title=f"💖 HỒ SƠ CẶP ĐÔI 💖",
                color=0xFF1493
            )
            
            embed.set_image(url="attachment://profile.png")
            
            # Thông tin chi tiết
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
                name="🖼️ Khung hiện tại",
                value=frame_name,
                inline=True
            )

            embed.add_field(
                name=f"💰 Xu của {user_member.name if user_member else 'Bạn'}",
                value=f"{user_data.get('xu', 0)} xu",
                inline=True
            )

            embed.add_field(
                name=f"💰 Xu của {partner_member.name if partner_member else 'Partner'}",
                value=f"{partner_data.get('xu', 0)} xu",
                inline=True
            )

            gifts_given = user_data.get("gifts_given", 0)
            embed.add_field(
                name="🎁 Quà đã tặng",
                value=f"{gifts_given} món",
                inline=True
            )

            embed.set_footer(text="💗 Tình yêu là điều kỳ diệu nhất 💗")

            # Gửi message
            await interaction.followup.send(embed=embed, file=file, ephemeral=False)
                
        except asyncio.TimeoutError:
            try:
                await interaction.followup.send(
                    embed=error_embed("⏰ Quá lâu để tạo profile, vui lòng thử lại!"),
                    ephemeral=True
                )
            except Exception as e:
                print(f"❌ Lỗi gửi timeout message: {e}")
        except Exception as e:
            print(f"❌ Lỗi tạo ảnh profile: {e}")
            try:
                await interaction.followup.send(
                    embed=error_embed(f"❌ Lỗi hiển thị profile: {str(e)[:100]}"),
                    ephemeral=True
                )
            except Exception as e2:
                print(f"❌ Lỗi gửi error message: {e2}")

    async def create_profile_image(self, user_avatar_url, partner_avatar_url, user_name, partner_name, status, intimacy, frame_color):
        """Tạo ảnh profile với 2 avatar và khung"""
        try:
            # Kích thước canvas
            width, height = 800, 400
            img = Image.new('RGB', (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Màu khung từ hex
            try:
                frame_rgb = tuple(int(frame_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            except:
                frame_rgb = (255, 182, 193)  # Default pink
            
            # Tải avatar với timeout
            user_avatar = Image.new('RGBA', (150, 150), (200, 200, 200))
            partner_avatar = Image.new('RGBA', (150, 150), (200, 200, 200))
            
            try:
                if user_avatar_url:
                    response = requests.get(user_avatar_url, timeout=5)
                    user_avatar = Image.open(io.BytesIO(response.content)).convert('RGBA')
                    user_avatar = user_avatar.resize((150, 150), Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"⚠️ Lỗi tải avatar user: {e}")
            
            try:
                if partner_avatar_url:
                    response = requests.get(partner_avatar_url, timeout=5)
                    partner_avatar = Image.open(io.BytesIO(response.content)).convert('RGBA')
                    partner_avatar = partner_avatar.resize((150, 150), Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"⚠️ Lỗi tải avatar partner: {e}")
            
            # Tạo avatar tròn với khung
            user_avatar_with_frame = self.create_circular_avatar(user_avatar, frame_rgb, border_width=8)
            partner_avatar_with_frame = self.create_circular_avatar(partner_avatar, frame_rgb, border_width=8)
            
            # Đặt vị trí avatar
            user_x, user_y = 100, 125
            partner_x, partner_y = 550, 125
            
            img.paste(user_avatar_with_frame, (user_x, user_y), user_avatar_with_frame)
            img.paste(partner_avatar_with_frame, (partner_x, partner_y), partner_avatar_with_frame)
            
            # Vẽ trái tim ở giữa
            heart_x, heart_y = width // 2, 180
            draw.text((heart_x - 20, heart_y - 20), "💖", fill=frame_rgb)
            
            # Vẽ tên
            font_default = ImageFont.load_default()
            
            # Tên người dùng - trái
            draw.text((user_x + 10, user_y + 160), user_name[:15], fill=frame_rgb, font=font_default)
            
            # Tên partner - phải
            draw.text((partner_x + 10, partner_y + 160), partner_name[:15], fill=frame_rgb, font=font_default)
            
            # Trạng thái ở dưới trái tim
            draw.text((heart_x - 30, heart_y + 30), status, fill=(100, 100, 100), font=font_default)
            draw.text((heart_x - 50, heart_y + 60), f"Thân mật: {intimacy}", fill=(100, 100, 100), font=font_default)
            
            # Lưu ảnh vào BytesIO
            image_bytes = io.BytesIO()
            img.save(image_bytes, format='PNG')
            image_bytes.seek(0)
            return image_bytes
            
        except Exception as e:
            print(f"❌ Lỗi trong create_profile_image: {e}")
            # Tạo ảnh fallback đơn giản
            img = Image.new('RGB', (800, 400), color=(255, 200, 200))
            image_bytes = io.BytesIO()
            img.save(image_bytes, format='PNG')
            image_bytes.seek(0)
            return image_bytes

    def create_circular_avatar(self, avatar_img, frame_color, border_width=8):
        """Tạo avatar tròn với khung màu"""
        try:
            size = avatar_img.size[0]
            total_size = size + (border_width * 2)
            
            # Tạo ảnh với khung
            frame_img = Image.new('RGBA', (total_size, total_size), (255, 255, 255, 0))
            
            # Vẽ khung tròn
            frame_draw = ImageDraw.Draw(frame_img)
            frame_draw.ellipse([0, 0, total_size - 1, total_size - 1], fill=frame_color)
            
            # Vẽ avatar vào giữa
            frame_img.paste(avatar_img, (border_width, border_width), avatar_img)
            
            # Tạo mask tròn cho avatar
            mask = Image.new('L', (total_size, total_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([0, 0, total_size - 1, total_size - 1], fill=255)
            
            result = Image.new('RGBA', (total_size, total_size), (255, 255, 255, 0))
            result.paste(frame_img, (0, 0), mask)
            
            return result
        except Exception as e:
            print(f"❌ Lỗi create_circular_avatar: {e}")
            return Image.new('RGBA', (166, 166), (200, 200, 200, 255))

    def create_progress_bar(self, current, total, length=10):
        """Tạo thanh progress bar"""
        filled = int((current / total) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"`{bar}`"

    @commands.command(name="thaykhung")
    async def change_frame(self, ctx, frame_id: str = None):
        """Đổi khung ảnh couple - Hiển thị menu chọn khung"""
        try:
            user_data = get_user(ctx.author.id)
            partner_id = user_data.get("love_partner")

            if not partner_id:
                await ctx.send(embed=error_embed("💔 Bạn chưa có người yêu!"))
                return

            # Hiển thị menu chọn khung
            owned_frames = user_data.get("owned_frames", ["frame_basic"])
            current_frame = user_data.get("current_frame", "frame_basic")
            
            embed = discord.Embed(
                title="🖼️ Thay Khung Ảnh Couple",
                description=f"Khung hiện tại: **{FRAMES_SHOP.get(current_frame, {}).get('name', 'Không xác định')}**\n\n"
                            "Chọn khung bạn muốn sử dụng bên dưới:",
                color=0xFF69B4
            )
            
            # Hiển thị các khung đã sở hữu
            for frame_id in owned_frames:
                frame = FRAMES_SHOP.get(frame_id)
                if frame:
                    status = "✅ Đang dùng" if frame_id == current_frame else ""
                    embed.add_field(
                        name=f"{frame['name']} {status}",
                        value=f"ID: `{frame_id}`",
                        inline=True
                    )
            
            view = ChangeFrameView(ctx.author.id, owned_frames, current_frame)
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            print(f"❌ Lỗi command thaykhung: {e}")
            await ctx.send(embed=error_embed(f"❌ Lỗi: {str(e)[:100]}"))


class ChangeFrameView(discord.ui.View):
    """View để chọn khung ảnh"""
    def __init__(self, user_id, owned_frames, current_frame):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.current_frame = current_frame
        
        # Tạo select menu với các khung đã sở hữu
        options = []
        for frame_id in owned_frames:
            frame = FRAMES_SHOP.get(frame_id)
            if frame:
                is_current = "✅ " if frame_id == current_frame else ""
                options.append(
                    discord.SelectOption(
                        label=f"{is_current}{frame['name']}",
                        value=frame_id,
                        description=frame['description'][:100],
                        emoji="🖼️"
                    )
                )
        
        if options:
            self.add_item(FrameSelectMenu(options, user_id))

class FrameSelectMenu(discord.ui.Select):
    """Select menu để chọn khung"""
    def __init__(self, options, user_id):
        super().__init__(
            placeholder="🖼️ Chọn khung bạn muốn sử dụng...",
            options=options,
            min_values=1,
            max_values=1
        )
        self.user_id = user_id
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Đây không phải menu của bạn!", ephemeral=True)
            return
        
        selected_frame = self.values[0]
        
        # Lấy dữ liệu user
        user_data = get_user(interaction.user.id)
        partner_id = user_data.get("love_partner")
        
        if not partner_id:
            await interaction.response.send_message(
                embed=error_embed("💔 Bạn chưa có người yêu!"),
                ephemeral=True
            )
            return
        
        # Đổi khung cho cả 2 người
        user_data["current_frame"] = selected_frame
        update_user(interaction.user.id, user_data)

        partner_data = get_user(partner_id)
        partner_data["current_frame"] = selected_frame
        update_user(partner_id, partner_data)

        frame = FRAMES_SHOP[selected_frame]
        
        embed = discord.Embed(
            title="✅ Đổi khung thành công!",
            description=f"Đã đổi khung couple thành **{frame['name']}**\n"
                        f"Khung đã được áp dụng cho cả 2 người! 💖",
            color=0x00FF00
        )
        embed.set_footer(text="💕 Hãy xem hồ sơ couple để thấy khung mới!")
        
        await interaction.response.edit_message(embed=embed, view=None)


async def setup(bot):
    await bot.add_cog(Profile(bot))
