import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# ==========================
#  FLASK WEB SERVER (Keep Alive)
# ==========================
app = Flask('')

@app.route('/')
def home():
    return "✅ Bot đang chạy!"

def run():
    # QUAN TRỌNG: Lấy PORT từ Render
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================
#  KHỞI TẠO BOT
# ==========================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="bz", intents=intents)

# ==========================
#  KHI BOT SẴN SÀNG
# ==========================
@bot.event
async def on_ready():
    print(f"✅ Bot đã sẵn sàng dưới tên: {bot.user}")
    print("📜 Đang load các cogs...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Đã load: {filename}")
            except Exception as e:
                print(f"❌ Lỗi khi load {filename}: {e}")
    print("✨ Tất cả cogs đã sẵn sàng!")

# ==========================
#  LỆNH MENU CHÍNH
# ==========================
@bot.command(name="menu")
async def menu_command(ctx):
    from utils.embeds import base_embed
    from discord.ui import View, Button
    embed = base_embed(
        "💘 Menu Tình Yêu 💘",
        "Chọn tính năng bên dưới nhé!\n\n"
        "📝 **Hướng dẫn các nút:**\n"
        "💌 **Tỏ tình** → Gửi lời tỏ tình tới người bạn thích 💞 dùng lệnh bzlove và tên người bạn thích\n"
        "🛍️ **Shop** → Mua vật phẩm, quà tặng để tặng cho nửa kia của bạn để tăng điểm thân mật 🎁\n"
        "🎒 **Tủ đồ** → Xem những món quà bạn đang sở hữu 🎒\n"
        "🎁 **Tặng quà** → Gửi quà cho nửa kia của bạn để tăng độ thân mật 💖\n"
        "💍 **Cưới** → Kết hôn cùng người thương của bạn, cả 2 cùng tiến vào hôn nhân 💍\n"
        "👩‍❤️‍👨 **Hồ sơ couple** → Xem thông tin tình yêu và cấp độ của bạn và nửa kia 💕"
    )
    
    # 🌸 Thêm ghi chú nhỏ (footer)
    embed.set_footer(text="Crate: 🌸 Boizzzz 🗡")
    
    view = View()
    view.add_item(Button(label="💌 Tỏ tình", style=discord.ButtonStyle.primary, custom_id="love"))
    view.add_item(Button(label="🛍️ Shop", style=discord.ButtonStyle.success, custom_id="shop"))
    view.add_item(Button(label="🎒 Tủ đồ", style=discord.ButtonStyle.secondary, custom_id="inventory"))
    view.add_item(Button(label="🎁 Tặng quà", style=discord.ButtonStyle.primary, custom_id="gift"))
    view.add_item(Button(label="💍 Cưới", style=discord.ButtonStyle.danger, custom_id="marry"))
    view.add_item(Button(label="👩‍❤️‍👨 Hồ sơ couple", style=discord.ButtonStyle.secondary, custom_id="profile"))
    await ctx.send(embed=embed, view=view)

# ==========================
#  LỆNH ĐỒNG BỘ SLASH
# ==========================
@bot.command()
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Slash commands đã được đồng bộ!")

# ==========================
#  CHẠY BOT
# ==========================
bot.remove_command("help")

if __name__ == "__main__":
    keep_alive()  # Khởi động Flask server
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
