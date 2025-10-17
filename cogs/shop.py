import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import json
from utils.file_manager import get_user, update_user
from utils.embeds import success_embed, error_embed, base_embed


# ==============================
#  HÀM LOAD DỮ LIỆU SHOP
# ==============================
def load_shop_items():
    with open("data/config.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("shop_items", {})


# ==============================
#  MODAL NHẬP SỐ LƯỢNG
# ==============================
async def open_quantity_modal(interaction: discord.Interaction, item_name: str):
    class QuantityModal(discord.ui.Modal, title=f"💰 Mua {item_name}"):
        quantity = discord.ui.TextInput(
            label="Nhập số lượng muốn mua",
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
                    ephemeral=True
                )
                return

            await handle_purchase(modal_interaction, item_name, qty)

    await interaction.response.send_modal(QuantityModal())


# ==============================
#  XỬ LÝ MUA HÀNG
# ==============================
async def handle_purchase(interaction: discord.Interaction, item_name: str, quantity: int):
    shop_items = load_shop_items()
    item = shop_items.get(item_name)

    if not item:
        await interaction.response.send_message(embed=error_embed("❌ Món quà này không tồn tại!"), ephemeral=True)
        return

    total_price = item["price"] * quantity
    user = get_user(interaction.user.id)

    if user["xu"] < total_price:
        await interaction.response.send_message(embed=error_embed("💸 Bạn không đủ xu để mua món này!"), ephemeral=True)
        return

    # Trừ xu & thêm vào inventory
    user["xu"] -= total_price
    user.setdefault("inventory", {})
    user["inventory"][item_name] = user["inventory"].get(item_name, 0) + quantity
    update_user(interaction.user.id, user)

    await interaction.response.send_message(
        embed=success_embed(f"🛍️ Bạn đã mua **{quantity}x {item_name}** với giá **{total_price} xu** 💘"),
        ephemeral=True
    )


# ==============================
#  VIEW MUA QUÀ
# ==============================
class BuyGiftView(View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id

        items = load_shop_items()
        options = [
            discord.SelectOption(label=name, description=f"{info['price']} xu", value=name)
            for name, info in items.items()
        ]
        self.add_item(GiftSelect(options, user_id))


class GiftSelect(Select):
    def __init__(self, options, user_id):
        super().__init__(placeholder="🎁 Chọn món quà để mua", options=options)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
            return
        chosen_item = self.values[0]
        await open_quantity_modal(interaction, chosen_item)


# ==============================
#  MỞ SHOP
# ==============================
async def open_shop(interaction: discord.Interaction):
    embed = base_embed(
        "🛍️ SHOP TÌNH YÊU 💘",
        "Dùng **xu tình yêu** để mua quà tặng nửa kia của bạn!\n\n"
        "Chọn hành động bên dưới:"
    )
    view = BuyGiftView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# ==============================
#  XEM TỦ ĐỒ
# ==============================
async def open_inventory(interaction: discord.Interaction):
    user = get_user(interaction.user.id)
    inventory = user.get("inventory", {})

    if not inventory:
        await interaction.response.send_message(embed=error_embed("🎒 Tủ đồ của bạn đang trống!"), ephemeral=True)
        return

    desc = "\n".join([f"**{item}** × {count}" for item, count in inventory.items()])
    embed = base_embed("🎒 Tủ đồ của bạn", desc)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==============================
#  COG CHÍNH
# ==============================
class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("🛍️ shop.py đã được load")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.data or "custom_id" not in interaction.data:
            return

        if interaction.data["custom_id"] == "shop":
            await open_shop(interaction)
        elif interaction.data["custom_id"] == "inventory":
            await open_inventory(interaction)


async def setup(bot):
    await bot.add_cog(Shop(bot))
