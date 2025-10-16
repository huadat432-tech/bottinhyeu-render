import os
import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
from utils.file_manager import get_user, update_user
from utils.embeds import success_embed, error_embed, base_embed


class Gift(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================
    #  SỰ KIỆN KHI NHẤN NÚT 🎁
    # ==========================
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.data:
            return

        if interaction.data.get("custom_id") == "gift":
            await self.open_gift_menu(interaction)

    # ==========================
    #  MỞ MENU CHỌN QUÀ
    # ==========================
    async def open_gift_menu(self, interaction: discord.Interaction):
        user = get_user(interaction.user.id)
        partner_id = user.get("love_partner")

        if not partner_id:
            await interaction.response.send_message(
                embed=error_embed("💔 Bạn chưa có người yêu để tặng quà!"),
            )
            return

        inventory = user.get("inventory", {})
        if not inventory:
            await interaction.response.send_message(
                embed=error_embed("🎒 Tủ đồ của bạn đang trống!"),
            )
            return

        # Tạo danh sách chọn
        options = [
            discord.SelectOption(
                label=f"{item}",
                description=f"Số lượng: {count}",
                value=item
            )
            for item, count in inventory.items()
        ]

        select = Select(placeholder="🎁 Chọn món quà để tặng", options=options)

        async def select_callback(select_interaction: discord.Interaction):
            chosen_item = select.values[0]
            await self.open_quantity_modal(select_interaction, interaction.user.id, partner_id, chosen_item)

        select.callback = select_callback
        view = View()
        view.add_item(select)

        await interaction.response.send_message(
            embed=base_embed("🎁 Tặng Quà", "Chọn món quà trong tủ đồ để tặng cho người yêu 💝"),
            view=view,
        )

    # ==========================
    #  MỞ MODAL NHẬP SỐ LƯỢNG
    # ==========================
    async def open_quantity_modal(self, interaction: discord.Interaction, giver_id, receiver_id, item_name):
        outer_self = self  # giữ lại tham chiếu tới Gift class

        class QuantityModal(Modal, title=f"Tặng {item_name} 🎁"):
            quantity = TextInput(
                label="Nhập số lượng muốn tặng",
                placeholder="Ví dụ: 3",
                style=discord.TextStyle.short
            )

            async def on_submit(self, modal_interaction: discord.Interaction):
                try:
                    qty = int(self.quantity.value)
                    if qty <= 0:
                        raise ValueError
                except ValueError:
                    await modal_interaction.response.send_message(
                        embed=error_embed("❌ Số lượng không hợp lệ!"),
                    )
                    return

                # Gọi hàm handle_gift từ class Gift
                await outer_self.handle_gift(giver_id, receiver_id, item_name, qty, modal_interaction)

        await interaction.response.send_modal(QuantityModal())

    # ==========================
    #  XỬ LÝ TẶNG QUÀ
    # ==========================
    async def handle_gift(self, giver_id, receiver_id, item, quantity, interaction: discord.Interaction):
        user = get_user(giver_id)
        partner = get_user(receiver_id)

        # Kiểm tra đủ quà
        if item not in user["inventory"] or user["inventory"][item] < quantity:
            await interaction.response.send_message(
                embed=error_embed("❌ Bạn không có đủ số lượng món quà này!"),
            )
            return

        # Trừ vật phẩm
        user["inventory"][item] -= quantity
        if user["inventory"][item] <= 0:
            del user["inventory"][item]

        # Cộng điểm thân mật
        if "hoa" in item.lower():
            gift_points = 5
        elif "gấu" in item.lower():
            gift_points = 10
        elif "dây chuyền" in item.lower():
            gift_points = 15
        else:
            gift_points = 3

        total_points = gift_points * quantity
        user["intimacy"] = user.get("intimacy", 0) + total_points
        partner["intimacy"] = partner.get("intimacy", 0) + total_points

        update_user(giver_id, user)
        update_user(receiver_id, partner)

        # ================================
        # Map quà → GIF trong folder images/
        # ================================
        gif_mapping = {
            "hoa": "images/tanghoa.gif",
            "gấu": "images/tanggaubong.gif",
            "dây chuyền": "images/tangdaychuyen.gif",
        }

        gif_path = None
        for key, path in gif_mapping.items():
            if key.lower() in item.lower():
                gif_path = path
                break

        remaining = user["inventory"].get(item, 0)
        remaining_text = f"\n🎒 Bạn còn lại **{remaining}x {item}** trong tủ đồ." if remaining > 0 else ""

        embed = success_embed(
            f"💝 {interaction.user.mention} vừa tặng **{quantity}x {item}** cho <@{receiver_id}>!\n"
            f"💞 Cả hai nhận được **+{total_points} điểm thân mật!**"
            f"{remaining_text}"
        )

        # ================================
        # Gửi embed kèm GIF công khai cho cả kênh
        # ================================
        if gif_path and os.path.exists(gif_path):
            file = discord.File(gif_path, filename=os.path.basename(gif_path))
            embed.set_image(url=f"attachment://{os.path.basename(gif_path)}")
            await interaction.response.send_message(
                content=f"{interaction.user.mention} vừa tặng quà cho <@{receiver_id}>!",
                embed=embed,
                file=file
            )
        else:
            await interaction.response.send_message(
                content=f"{interaction.user.mention} vừa tặng quà cho <@{receiver_id}>!",
                embed=embed
            )


async def setup(bot):
    await bot.add_cog(Gift(bot))
