import discord
from discord.ext import commands
from utils.file_manager import get_user
from utils.embeds import error_embed
import random
from datetime import datetime
from PIL import Image, ImageDraw
import io
import aiohttp

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

    def create_circular_avatar(self, avatar_img, size=180):
        """Tạo avatar hình tròn"""
        # Tạo mask tròn
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        
        # Áp dụng mask
        avatar_img.putalpha(mask)
        return avatar_img

    async def create_couple_image(self, user_member, partner_member):
        """Tạo hình ghép avatar 2 người với trái tim giữa"""
        try:
            # Tải avatar
            user_avatar_data = await self.download_image(user_member.avatar.url if user_member.avatar else user_member.default_avatar.url)
            partner_avatar_data = await self.download_image(partner_member.avatar.url if partner_member.avatar else partner_member.default_avatar.url)

            user_img = Image.open(io.BytesIO(user_avatar_data)).convert("RGBA").resize((160, 160), Image.Resampling.LANCZOS)
            partner_img = Image.open(io.BytesIO(partner_avatar_data)).convert("RGBA").resize((160, 160), Image.Resampling.LANCZOS)

            # Tạo avatar hình tròn
            user_img = self.create_circular_avatar(user_img, 160)
            partner_img = self.create_circular_avatar(partner_img, 160)

            # Tạo hình nền trắng
            base = Image.new("RGB", (600, 200), color=(255, 255, 255))
            base_rgba = base.convert("RGBA")
            
            # Vẽ trái tim giữa trước
            draw = ImageDraw.Draw(base_rgba)
            heart_x, heart_y = 300, 100
            self.draw_heart(draw, heart_x, heart_y, 50, fill=(255, 105, 180), outline=(255, 20, 147), width=4)

            # Ghép avatar trái (vị trí: 50, 20)
            base_rgba.paste(user_img, (50, 20), user_img)
            
            # Ghép avatar phải (vị trí: 390, 20)
            base_rgba.paste(partner_img, (390, 20), partner_img)

            # Ghép frame đè lên cùng
            try:
                frame_img = Image.open("images/frame_basic.png").convert("RGBA").resize((600, 200), Image.Resampling.LANCZOS)
                base_rgba = Image.alpha_composite(base_rgba, frame_img)
            except Exception as e:
                print(f"Không tìm thấy frame: {e}")

            # Chuyển về RGB để lưu
            base_rgba = base_rgba.convert("RGB")

            # Lưu vào bytes
            img_bytes = io.BytesIO()
            base_rgba.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            return img_bytes

        except Exception as e:
            print(f"Lỗi tạo hình: {e}")
            return None

    async def download_image(self, url):
        """Tải hình từ URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.read()

    def draw_heart(self, draw, x, y, size, fill, outline, width):
        """Vẽ hình trái tim đơn giản"""
        # Vẽ trái tim bằng cách kết hợp 2 vòng tròn và 1 tam giác
        # Hai vòng tròn ở trên
        left_circle = (x - size // 2, y - size // 3, x, y + size // 3)
        right_circle = (x, y - size // 3, x + size // 2, y + size // 3)
        
        # Tam giác ở dưới
        triangle = [(x - size // 2, y), (x + size // 2, y), (x, y + size)]
        
        # Vẽ
        draw.ellipse(left_circle, fill=fill, outline=outline, width=width)
        draw.ellipse(right_circle, fill=fill, outline=outline, width=width)
        draw.polygon(triangle, fill=fill)
        draw.line(triangle + [triangle[0]], fill=outline, width=width)

    async def show_profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
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

        # Tính ngày yêu nhau
        relationship_days = user_data.get("relationship_days", 0)
        
        # Trạng thái mối quan hệ
        if user_data.get("married"):
            status = "💍 Đã cưới"
            status_color = 0xFFD700
        else:
            status = "💘 Đang hẹn hò"
            status_color = 0xFF69B4

        # Tạo hình ghép
        couple_image = await self.create_couple_image(user_member, partner_member)

        # Tạo Embed cân đối
        embed = discord.Embed(
            title="✨ HỒ SƠ CẶP ĐÔI ✨",
            color=status_color,
            timestamp=datetime.now()
        )

        # Hình trái tim + avatar ở trên
        if couple_image:
            file = discord.File(couple_image, filename="couple.png")
            embed.set_image(url="attachment://couple.png")

        # Thông tin trạng thái
        embed.add_field(
            name="👑 Trạng thái",
            value=status,
            inline=False
        )

        # Thống kê cân đối 2 cột
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

        # Xu của 2 người
        embed.add_field(
            name=f"💰 {user_member.name}",
            value=f"`{user_data['xu']}` xu",
            inline=True
        )

        embed.add_field(
            name=f"💰 {partner_member.name}",
            value=f"`{partner_data['xu']}` xu",
            inline=True
        )

        # Tổng cộng
        embed.add_field(
            name="✨ Tổng cộng",
            value=f"`{user_data['xu'] + partner_data['xu']}` xu 💎",
            inline=False
        )

        embed.set_footer(text="💗 Yêu thương là hạnh phúc lớn nhất")

        # Gửi
        if couple_image:
            await interaction.followup.send(embed=embed, file=file, ephemeral=False)
        else:
            await interaction.followup.send(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Profile(bot))
