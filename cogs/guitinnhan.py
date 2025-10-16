import discord
from discord.ext import commands
import asyncio
from typing import Optional

class GuiTinNhan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_sessions = {}

    async def cleanup_messages(self, *messages):
        """Xóa nhiều tin nhắn một cách an toàn"""
        for msg in messages:
            if msg:
                try:
                    await msg.delete()
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    pass

    @commands.command(name="andanh", aliases=["anon", "anonymous"])
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def andanh(self, ctx):
        """Gửi tin nhắn ẩn danh hoàn toàn - không để lại dấu vết"""
        
        try:
            await ctx.message.delete()
        except:
            pass

        if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            temp_msg = await ctx.send("⚠️ Bot cần quyền `Manage Messages` để hoạt động tốt nhất.")
            await asyncio.sleep(5)
            await self.cleanup_messages(temp_msg)
            return

        try:
            dm_channel = await ctx.author.create_dm()
        except discord.Forbidden:
            temp_msg = await ctx.send(f"{ctx.author.mention} ⚠️ Vui lòng bật DM để sử dụng lệnh này (Settings → Privacy & Safety → Allow direct messages).")
            await asyncio.sleep(10)
            await self.cleanup_messages(temp_msg)
            return

        try:
            guide_embed = discord.Embed(
                title="💌 Hệ thống tin nhắn ẩn danh",
                description=(
                    "Bạn sẽ thực hiện các bước sau **trong DM này**:\n\n"
                    "**Bước 1:** @tag người bạn muốn gửi tin nhắn\n"
                    "**Bước 2:** Nhập nội dung tin nhắn\n"
                    "**Bước 3:** Chọn cách gửi (DM hoặc kênh)\n\n"
                    "🔒 Hoàn toàn ẩn danh - không ai biết bạn là ai!\n"
                    "⏱️ Thời gian: 2 phút/bước"
                ),
                color=discord.Color.purple()
            )
            guide_embed.set_footer(text="🔒 Bảo mật tuyệt đối | Create: 🌸 Boizzzz 🗡")
            await dm_channel.send(embed=guide_embed)
        except discord.Forbidden:
            return

        def check_dm(m):
            return m.author == ctx.author and m.channel == dm_channel

        # Lấy danh sách thành viên để hiển thị
        members = [m for m in ctx.guild.members if not m.bot and m.id != ctx.author.id]
        
        if not members:
            await dm_channel.send("❌ Không có thành viên nào khác trong server!")
            return
        
        # Tạo danh sách toàn bộ thành viên
        member_list = "\n".join([f"**{i+1}.** {m.display_name} (`{m.id}`)" for i, m in enumerate(members)])
        
        tag_embed = discord.Embed(
            title="👥 Bước 1: Chọn người nhận",
            description=(
                f"Gõ tên hoặc ID người bạn muốn gửi tin nhắn ẩn danh.\n\n"
                f"**📋 Danh sách toàn bộ thành viên ({len(members)} người):**\n{member_list}\n\n"
                f"📝 Ví dụ: `Boizzzz` hoặc `123456789` (ID)\n\n"
                f"⏱️ Thời gian: 2 phút"
            ),
            color=discord.Color.purple()
        )
        await dm_channel.send(embed=tag_embed)

        try:
            tag_msg = await self.bot.wait_for("message", check=check_dm, timeout=120)
            text = tag_msg.content.strip()
            
            receiver = None
            
            # Kiểm tra nếu là số (STT)
            if text.isdigit():
                stt = int(text)
                if 1 <= stt <= len(members):
                    receiver = members[stt - 1]
                else:
                    await dm_channel.send(f"❌ STT không hợp lệ! Vui lòng chọn từ 1 đến {len(members)}")
                    return
            else:
                # Thử tìm từ mentions
                if tag_msg.mentions:
                    receiver = tag_msg.mentions[0]
                else:
                    # Tìm từ tên hoặc ID
                    search_name = text.replace("@", "").lower()
                    
                    # Tìm người có tên khớp
                    for member in members:
                        if (search_name == member.display_name.lower() or 
                            search_name == member.name.lower() or
                            search_name == str(member.id)):
                            receiver = member
                            break
            
            if not receiver:
                await dm_channel.send(f"❌ Không tìm thấy thành viên '{text}'!")
                return
            
            receiver = ctx.guild.get_member(receiver.id)
            
            # Kiểm tra nếu là bot
            if receiver.bot:
                await dm_channel.send("❌ Không thể gửi tin nhắn cho bot!")
                return
            
            # Kiểm tra nếu chọn chính mình
            if receiver.id == ctx.author.id:
                await dm_channel.send("❌ Không thể gửi tin nhắn cho chính bạn!")
                return
            
            # Kiểm tra nếu người nhận có trong server
            member = ctx.guild.get_member(receiver.id)
            if not member:
                await dm_channel.send(f"❌ **{receiver.display_name}** không có trong server này!")
                return

            await self.cleanup_messages(tag_msg)

            confirm_embed = discord.Embed(
                title="✅ Đã chọn người nhận",
                description=f"**{receiver.display_name}** (@{receiver.name})\n\nĐang chuyển sang bước tiếp theo...",
                color=discord.Color.green()
            )
            
            if receiver.display_avatar:
                confirm_embed.set_thumbnail(url=receiver.display_avatar.url)
            
            await dm_channel.send(embed=confirm_embed)

        except asyncio.TimeoutError:
            await dm_channel.send("⏰ Hết thời gian. Vui lòng sử dụng lệnh `!andanh` lại.")
            return

        # Bước 2: Nhận nội dung tin nhắn
        content_embed = discord.Embed(
            title="✍️ Bước 2: Nhập nội dung",
            description=f"Nhập tin nhắn bạn muốn gửi đến **{receiver.display_name}**\n\n⏱️ Thời gian: 3 phút",
            color=discord.Color.blue()
        )
        await dm_channel.send(embed=content_embed)

        try:
            content_msg = await self.bot.wait_for("message", check=check_dm, timeout=180)
            message_text = content_msg.content
            
            if len(message_text) > 2000:
                await dm_channel.send("❌ Tin nhắn quá dài (tối đa 2000 ký tự).")
                return
            
            if len(message_text.strip()) == 0:
                await dm_channel.send("❌ Tin nhắn không được để trống.")
                return

            await self.cleanup_messages(content_msg)

        except asyncio.TimeoutError:
            await dm_channel.send("⏰ Hết thời gian. Vui lòng sử dụng lệnh `!andanh` lại.")
            return

        # Bước 3: Chọn cách gửi
        choice_embed = discord.Embed(
            title="📤 Bước 3: Chọn cách gửi",
            description="Chọn phương thức gửi tin nhắn:",
            color=discord.Color.gold()
        )
        
        view = AnonymousView(ctx, receiver, message_text, dm_channel, self.bot)
        await dm_channel.send(embed=choice_embed, view=view)


class AnonymousView(discord.ui.View):
    def __init__(self, ctx, receiver, message_text, dm_channel, bot):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.receiver = receiver
        self.message_text = message_text
        self.dm_channel = dm_channel
        self.bot = bot

    async def cleanup_dm_messages(self):
        """Xóa tin nhắn trong DM sau khi hoàn tất"""
        await asyncio.sleep(0.5)
        try:
            async for message in self.dm_channel.history(limit=10):
                if message.author == self.bot.user:
                    try:
                        await message.delete()
                    except:
                        pass
        except:
            pass

    @discord.ui.button(label="🕊️ Gửi riêng (DM)", style=discord.ButtonStyle.success, emoji="🕊️")
    async def send_dm(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gửi tin nhắn qua DM"""
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Không phải phiên của bạn!", ephemeral=True)

        member = self.ctx.guild.get_member(self.receiver.id)
        server_info = f"từ **{self.ctx.guild.name}**" if member else ""

        embed_send = discord.Embed(
            title="💌 Tin nhắn ẩn danh",
            description=self.message_text,
            color=discord.Color.from_rgb(255, 105, 180)
        )
        embed_send.set_footer(text=f"💫 Từ một người bí ẩn {server_info}".strip())
        embed_send.timestamp = discord.utils.utcnow()

        try:
            await self.receiver.send(embed=embed_send)
            
            success_embed = discord.Embed(
                title="✅ Đã gửi thành công!",
                description=f"Tin nhắn đã được gửi riêng (DM) đến **{self.receiver.display_name}**\n\n🔒 Hoàn toàn ẩn danh, không có dấu vết nào.",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=success_embed, view=None)
            
            await asyncio.sleep(5)
            await self.cleanup_dm_messages()
            
        except discord.Forbidden:
            error_embed = discord.Embed(
                title="❌ Không thể gửi",
                description=f"**{self.receiver.display_name}** đã tắt DM hoặc chặn bot.",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=error_embed, view=None)
            await asyncio.sleep(5)
            await self.cleanup_dm_messages()

        self.stop()

    @discord.ui.button(label="📢 Gửi vào kênh", style=discord.ButtonStyle.primary, emoji="📢")
    async def send_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Hiển thị menu chọn kênh"""
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Không phải phiên của bạn!", ephemeral=True)

        channels = [
            ch for ch in self.ctx.guild.text_channels 
            if ch.permissions_for(self.ctx.guild.me).send_messages
        ]
        
        if not channels:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="❌ Lỗi",
                    description="Không tìm thấy kênh nào có thể gửi.",
                    color=discord.Color.red()
                ),
                view=None
            )
            return

        options = [
            discord.SelectOption(
                label=f"#{ch.name}", 
                value=str(ch.id),
                description=f"Kênh: {ch.category.name if ch.category else 'Không có danh mục'}"
            )
            for ch in channels[:25]
        ]

        select = ChannelSelect(
            self.ctx, self.receiver, self.message_text, 
            self.dm_channel, self.bot, options
        )
        view = discord.ui.View(timeout=120)
        view.add_item(select)

        select_embed = discord.Embed(
            title="📜 Chọn kênh gửi",
            description="Chọn kênh để gửi tin nhắn ẩn danh:",
            color=discord.Color.blurple()
        )
        await interaction.response.edit_message(embed=select_embed, view=view)

    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Hủy thao tác"""
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Không phải phiên của bạn!", ephemeral=True)

        cancel_embed = discord.Embed(
            title="🚫 Đã hủy",
            description="Thao tác đã được hủy bỏ.",
            color=discord.Color.orange()
        )
        await interaction.response.edit_message(embed=cancel_embed, view=None)
        await asyncio.sleep(3)
        await self.cleanup_dm_messages()
        self.stop()


class ChannelSelect(discord.ui.Select):
    def __init__(self, ctx, receiver, message_text, dm_channel, bot, options):
        super().__init__(
            placeholder="🎯 Chọn kênh muốn gửi...",
            options=options,
            min_values=1,
            max_values=1
        )
        self.ctx = ctx
        self.receiver = receiver
        self.message_text = message_text
        self.dm_channel = dm_channel
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ Không phải phiên của bạn!", ephemeral=True)

        selected_channel = self.ctx.guild.get_channel(int(self.values[0]))
        
        if not selected_channel:
            await interaction.response.edit_message(
                embed=discord.Embed(title="❌ Kênh không tồn tại", color=discord.Color.red()),
                view=None
            )
            return

        embed_send = discord.Embed(
            title="💌 Tin nhắn ẩn danh",
            description=self.message_text,
            color=discord.Color.from_rgb(138, 43, 226)
        )
        embed_send.set_footer(text="💫 Từ một người bí ẩn trong server")
        embed_send.timestamp = discord.utils.utcnow()

        try:
            await selected_channel.send(
                content=f"{self.receiver.mention} 💌",
                embed=embed_send
            )

            success_embed = discord.Embed(
                title="✅ Đã gửi thành công!",
                description=f"Tin nhắn đã được gửi vào kênh **#{selected_channel.name}**\n\n🔒 Hoàn toàn ẩn danh, không có dấu vết nào.",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=success_embed, view=None)
            
            await asyncio.sleep(5)
            try:
                async for message in self.dm_channel.history(limit=10):
                    if message.author == self.bot.user:
                        await message.delete()
            except:
                pass

        except discord.Forbidden:
            error_embed = discord.Embed(
                title="❌ Không thể gửi",
                description=f"Bot không có quyền gửi tin nhắn vào **#{selected_channel.name}**",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=error_embed, view=None)


async def setup(bot):
    await bot.add_cog(GuiTinNhan(bot))