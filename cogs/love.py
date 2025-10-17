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
        
        # Khởi tạo các field cần thiết
        if "owned_frames" not in data[lover]:
            data[lover]["owned_frames"] = ["frame_basic"]
        if "current_frame" not in data[lover]:
            data[lover]["current_frame"] = "frame_basic"
        if "owned_frames" not in data[target]:
            data[target]["owned_frames"] = ["frame_basic"]
        if "current_frame" not in data[target]:
            data[target]["current_frame"] = "frame_basic"
            
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

        # Xóa người yêu và reset trạng thái
        data[lover]["love_partner"] = None
        data[lover]["married"] = False
        data[lover]["intimacy"] = 0
        data[lover]["gifts_given"] = 0
        
        data[partner]["love_partner"] = None
        data[partner]["married"] = False
        data[partner]["intimacy"] = 0
        data[partner]["gifts_given"] = 0
        
        save_data(data)

        gif_url = "https://media.tenor.com/XF3b4dyWj9sAAAAC/broken-heart.gif"
        desc = f"💔 **<@{self.lover_id}>** và **<@{self.partner_id}>** đã chia tay...\nChúc cả hai sớm tìm thấy hạnh phúc mới!"

        embed = love_embed(desc)
        embed.set_image(url=gif_url)
        await interaction.response.edit_message(embed=embed, view=None)
        await interaction.channel.send(f"💔 {interaction.user.mention} đã xác nhận chia tay với đối phương.")

    @
