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
            await interaction.response.send_message(
                embed=error_embed("💔 Bạn chưa có người yêu! Hãy tỏ tình trước đã nhé 💌"),
                ephemeral=True
            )
            return

        # Defer để tránh timeout
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=False)

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

        # Gửi message (dùng followup vì đã defer)
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=False)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=False)

    def create_progress_bar(self, current, total, length=10):
        """Tạo thanh progress bar"""
        filled = int((current / total) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"`{bar}`"

    @commands.command(name="thaykhung")
    async def change_frame(self, ctx, frame_id: str = None):
        """Đổi khung ảnh couple - Hiển thị menu chọn khung"""
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
            description=f"Khung hiện tại: **{FRAMES_SHOP.get(current_frame, FRAMES_SHOP['frame_basic'])['name']}**\n\n"
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
        save_user(interaction.user.id, user_data)

        partner_data = get_user(partner_id)
        partner_data["current_frame"] = selected_frame
        save_user(partner_id, partner_data)

        frame = FRAMES_SHOP[selected_frame]
        
        embed = discord.Embed(
            title="✅ Đổi khung thành công!",
            description=f"Đã đổi khung couple thành **{frame['name']}**\n"
                        f"Khung đã được áp dụng cho cả 2 người! 💖",
            color=0x00FF00
        )
        embed.set_image(url=frame["url"])
        embed.set_footer(text="💕 Hãy xem hồ sơ couple để thấy khung mới!")
        
        await interaction.response.edit_message(embed=embed, view=None)

async def setup(bot):
    await bot.add_cog(Profile(bot))
