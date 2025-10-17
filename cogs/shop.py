import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import json
from utils.file_manager import get_user, update_user
from utils.embeds import success_embed, error_embed, base_embed

# ==============================
#  DANH SÁCH KHUNG ẢNH
# ==============================
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

# ==============================
#  HÀM LOAD DỮ LIỆU SHOP
# ==============================
def load_shop_items():
    with open("data/config.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("shop_items", {})

# ==============================
#  MODAL NHẬP SỐ LƯỢNG QUÀ
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
#  XỬ LÝ MUA QUÀ
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
#  XỬ LÝ MUA KHUNG ẢNH
# ==============================
async def handle_frame_purchase(interaction: discord.Interaction, frame_id: str):
    frame = FRAMES_SHOP.get(frame_id)
    
    if not frame:
        await interaction.response.send_message(embed=error_embed("❌ Khung này không tồn tại!"), ephemeral=True)
        return

    user = get_user(interaction.user.id)
    
    # Kiểm tra đã sở hữu chưa
    owned_frames = user.get("owned_frames", ["frame_basic"])
    if frame_id in owned_frames:
        await interaction.response.send_message(
            embed=error_embed(f"❌ Bạn đã sở hữu khung **{frame['name']}** rồi!"),
            ephemeral=True
        )
        return

    # Kiểm tra xu
    if user["xu"] < frame["price"]:
        await interaction.response.send_message(
            embed=error_embed(f"💸 Bạn không đủ xu! Cần **{frame['price']} xu** để mua khung này."),
            ephemeral=True
        )
        return

    # Kiểm tra có đang yêu ai không
    if not user.get("love_partner"):
        await interaction.response.send_message(
            embed=error_embed("💔 Bạn cần có người yêu trước khi mua khung ảnh couple!"),
            ephemeral=True
        )
        return

    # Trừ xu & thêm khung vào danh sách sở hữu
    user["xu"] -= frame["price"]
    owned_frames.append(frame_id)
    user["owned_frames"] = owned_frames
    user["current_frame"] = frame_id  # Tự động set làm khung hiện tại
    update_user(interaction.user.id, user)

    # Cập nhật khung cho người yêu luôn
    partner_id = user["love_partner"]
    partner_data = get_user(partner_id)
    partner_owned = partner_data.get("owned_frames", ["frame_basic"])
    if frame_id not in partner_owned:
        partner_owned.append(frame_id)
        partner_data["owned_frames"] = partner_owned
    partner_data["current_frame"] = frame_id
    update_user(partner_id, partner_data)

    embed = success_embed(
        f"🎉 Mua khung thành công!\n\n"
        f"Bạn đã mua **{frame['name']}** với giá **{frame['price']} xu**\n"
        f"Khung đã được áp dụng cho cả 2 người! 💖"
    )
    embed.set_image(url=frame["url"])
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ==============================
#  VIEW CHÍNH SHOP
# ==============================
class ShopMainView(View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id

    @discord.ui.button(label="🎁 Mua Quà Tặng", style=discord.ButtonStyle.primary, row=0)
    async def buy_gifts(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Không phải shop của bạn!", ephemeral=True)
            return
        
        await show_gifts_shop(interaction)

    @discord.ui.button(label="🖼️ Mua Khung Ảnh", style=discord.ButtonStyle.success, row=0)
    async def buy_frames(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Không phải shop của bạn!", ephemeral=True)
            return
        
        await show_frames_shop(interaction)

# ==============================
#  HIỂN THỊ SHOP QUÀ TẶNG
# ==============================
async def show_gifts_shop(interaction: discord.Interaction):
    embed = base_embed(
        "🎁 CỬA HÀNG QUÀ TẶNG",
        "Mua quà để tặng người yêu và tăng độ thân mật! 💕\n\n"
        "Chọn món quà bên dưới:"
    )
    
    shop_items = load_shop_items()
    for name, info in shop_items.items():
        embed.add_field(
            name=f"{name}",
            value=f"💰 Giá: **{info['price']} xu**\n📝 {info.get('description', 'Món quà tuyệt vời')}",
            inline=True
        )
    
    view = BuyGiftView(interaction.user.id)
    await interaction.response.edit_message(embed=embed, view=view)

# ==============================
#  HIỂN THỊ SHOP KHUNG ẢNH
# ==============================
async def show_frames_shop(interaction: discord.Interaction):
    user = get_user(interaction.user.id)
    owned_frames = user.get("owned_frames", ["frame_basic"])
    current_xu = user.get("xu", 0)

    embed = discord.Embed(
        title="🖼️ CỬA HÀNG KHUNG ẢNH COUPLE",
        description=f"💰 Xu của bạn: **{current_xu} xu**\n\n"
                    "Mua khung đẹp để trang trí hồ sơ couple! 💖\n"
                    "Khung sẽ được áp dụng cho cả 2 người!",
        color=0xFF1493
    )

    for frame_id, frame in FRAMES_SHOP.items():
        status = "✅ Đã sở hữu" if frame_id in owned_frames else "🛒 Chưa mua"
        
        embed.add_field(
            name=f"{frame['name']} {status}",
            value=f"💰 Giá: **{frame['price']} xu**\n"
                  f"📝 {frame['description']}",
            inline=True
        )

    view = BuyFrameView(interaction.user.id, owned_frames)
    await interaction.response.edit_message(embed=embed, view=view)

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
        
        # Nút quay lại
        back_button = Button(label="◀️ Quay lại", style=discord.ButtonStyle.secondary)
        back_button.callback = self.back_callback
        self.add_item(back_button)

    async def back_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
            return
        await open_shop(interaction)

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
#  VIEW MUA KHUNG
# ==============================
class BuyFrameView(View):
    def __init__(self, user_id, owned_frames):
        super().__init__(timeout=60)
        self.user_id = user_id

        # Tạo options cho các khung chưa sở hữu
        options = []
        for frame_id, frame in FRAMES_SHOP.items():
            if frame_id not in owned_frames:
                options.append(
                    discord.SelectOption(
                        label=frame["name"],
                        description=f"{frame['price']} xu",
                        value=frame_id,
                        emoji="🖼️"
                    )
                )
        
        if options:
            self.add_item(FrameSelect(options, user_id))
        
        # Nút quay lại
        back_button = Button(label="◀️ Quay lại", style=discord.ButtonStyle.secondary)
        back_button.callback = self.back_callback
        self.add_item(back_button)

    async def back_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
            return
        await open_shop(interaction)

class FrameSelect(Select):
    def __init__(self, options, user_id):
        super().__init__(placeholder="🖼️ Chọn khung để mua", options=options)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
            return
        
        chosen_frame = self.values[0]
        await handle_frame_purchase(interaction, chosen_frame)

# ==============================
#  MỞ SHOP
# ==============================
async def open_shop(interaction: discord.Interaction):
    user = get_user(interaction.user.id)
    current_xu = user.get("xu", 0)
    
    embed = base_embed(
        "🛍️ SHOP TÌNH YÊU 💘",
        f"💰 Xu của bạn: **{current_xu} xu**\n\n"
        "Dùng **xu tình yêu** để mua quà tặng và khung ảnh!\n\n"
        "Chọn mục bạn muốn xem:"
    )
    
    view = ShopMainView(interaction.user.id)
    await interaction.response.edit_message(embed=embed, view=view)

# ==============================
#  XEM TỦ ĐỒ
# ==============================
async def open_inventory(interaction: discord.Interaction):
    user = get_user(interaction.user.id)
    inventory = user.get("inventory", {})
    owned_frames = user.get("owned_frames", ["frame_basic"])
    current_frame = user.get("current_frame", "frame_basic")

    embed = discord.Embed(
        title="🎒 TỦ ĐỒ CỦA BẠN",
        description="",
        color=0x9B59B6
    )

    # Hiển thị quà tặng
    if inventory:
        gifts_text = "\n".join([f"🎁 **{item}** × {count}" for item, count in inventory.items()])
        embed.add_field(name="🎁 Quà Tặng", value=gifts_text, inline=False)
    else:
        embed.add_field(name="🎁 Quà Tặng", value="*Chưa có quà nào*", inline=False)

    # Hiển thị khung ảnh
    if owned_frames:
        frames_list = []
        for f in owned_frames:
            frame = FRAMES_SHOP.get(f)
            if frame:
                status = "✅ Đang dùng" if f == current_frame else ""
                frames_list.append(f"🖼️ {frame['name']} {status}")
        
        frames_text = "\n".join(frames_list) if frames_list else "🖼️ Khung Cơ Bản (mặc định)"
        embed.add_field(name="🖼️ Khung Ảnh", value=frames_text, inline=False)

    embed.set_footer(text="💡 Bấm nút 'Thay khung' để đổi khung ảnh couple")
    
    # Thêm nút thay khung nếu có nhiều hơn 1 khung
    view = None
    if len(owned_frames) > 1:
        view = InventoryView(interaction.user.id, owned_frames, current_frame)
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class InventoryView(discord.ui.View):
    """View cho tủ đồ với nút thay khung"""
    def __init__(self, user_id, owned_frames, current_frame):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.owned_frames = owned_frames
        self.current_frame = current_frame
    
    @discord.ui.button(label="🖼️ Thay khung", style=discord.ButtonStyle.primary)
    async def change_frame_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Đây không phải tủ đồ của bạn!", ephemeral=True)
            return
        
        # Hiển thị menu chọn khung
        current_frame_name = FRAMES_SHOP.get(self.current_frame, {}).get('name', 'Không xác định')
        
        embed = discord.Embed(
            title="🖼️ Thay Khung Ảnh Couple",
            description=f"Khung hiện tại: **{current_frame_name}**\n\n"
                        "Chọn khung bạn muốn sử dụng:",
            color=0xFF69B4
        )
        
        view = ChangeFrameSelectView(self.user_id, self.owned_frames, self.current_frame)
        await interaction.response.edit_message(embed=embed, view=view)


class ChangeFrameSelectView(discord.ui.View):
    """View với select menu để chọn khung"""
    def __init__(self, user_id, owned_frames, current_frame):
        super().__init__(timeout=60)
        self.user_id = user_id
        
        # Tạo select menu
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
            self.add_item(InventoryFrameSelect(options, user_id))


class InventoryFrameSelect(discord.ui.Select):
    """Select menu để chọn khung từ tủ đồ"""
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
        embed.set_image(url=frame["url"])
        embed.set_footer(text="💕 Hãy xem hồ sơ couple để thấy khung mới!")
        
        await interaction.response.edit_message(embed=embed, view=None)

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
