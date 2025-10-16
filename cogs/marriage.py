import discord
from discord.ext import commands
from utils.file_manager import get_user, update_user, load_data, save_data
from utils.embeds import base_embed, success_embed, error_embed


# ==============================
#  CẤU HÌNH
# ==============================
MARRY_REQUIRE_INTIMACY = 300  # điểm thân mật tối thiểu để cưới
MARRY_GIF = "https://media.tenor.com/psbW8r6Vb1EAAAAC/anime-wedding.gif"  # GIF cô dâu chú rể
MARRY_BG = 0xFFB6C1  # màu hồng pastel 💗


# ==============================
#  COG CHÍNH
# ==============================
class Marriage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("💍 marriage.py đã được load")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Xử lý khi bấm nút '💍 Cưới' trong menu chính"""
        if not interaction.data or "custom_id" not in interaction.data:
            return

        if interaction.data["custom_id"] == "marry":
            await self.open_marry_menu(interaction)

    async def open_marry_menu(self, interaction: discord.Interaction):
        user = get_user(interaction.user.id)
        partner_id = user["love_partner"]

        if not partner_id:
            await interaction.response.send_message(
                embed=error_embed("💔 Bạn chưa có người yêu để cưới!"), ephemeral=True
            )
            return

        partner = get_user(partner_id)

        # kiểm tra điểm thân mật
        if user["intimacy"] < MARRY_REQUIRE_INTIMACY or partner["intimacy"] < MARRY_REQUIRE_INTIMACY:
            await interaction.response.send_message(
                embed=error_embed(
                    f"💞 Cả hai cần ít nhất **{MARRY_REQUIRE_INTIMACY} điểm thân mật** để tổ chức đám cưới!\n"
                    f"Hiện tại bạn có **{user['intimacy']} điểm**, người yêu có **{partner['intimacy']} điểm**."
                ),
                ephemeral=True
            )
            return

        # Kiểm tra đã cưới chưa
        if user.get("married") or partner.get("married"):
            await interaction.response.send_message(
                embed=error_embed("💍 Một trong hai người đã kết hôn rồi!"), ephemeral=True
            )
            return

        # Cập nhật trạng thái cưới
        user["married"] = True
        partner["married"] = True
        update_user(interaction.user.id, user)
        update_user(partner_id, partner)

        # Gửi thông báo hoành tráng trong kênh
        bride = f"<@{interaction.user.id}>"
        groom = f"<@{partner_id}>"

        embed = discord.Embed(
            title="💞 LỄ THÀNH HÔN NGẬP TRÀN TÌNH YÊU 💞",
            description=(
                f"🌸 Hôm nay, trước sự chứng kiến của mọi người 🌸\n\n"
                f"💐 **{bride}** và **{groom}** 💐\n"
                f"đã chính thức nên duyên vợ chồng 💍\n\n"
                f"🎉 Hãy cùng chúc mừng đôi uyên ương trăm năm hạnh phúc 🎉"
            ),
            color=MARRY_BG
        )
        embed.set_image(url=MARRY_GIF)
        embed.set_footer(text="💗 Tình yêu là vĩnh cửu 💗")

        await interaction.response.send_message(embed=embed)
        await interaction.channel.send(f"🎊 **CẢ SERVER CHÚ Ý!** 🎊\n"
                                       f"💞 {bride} và {groom} vừa tổ chức **đám cưới cực kỳ hoành tráng** 💍💐")

        # gửi quà thưởng
        reward = 200
        user["xu"] += reward
        partner["xu"] += reward
        update_user(interaction.user.id, user)
        update_user(partner_id, partner)
        await interaction.followup.send(
            embed=success_embed(f"💝 Cả hai nhận được **{reward} xu tình yêu** như quà cưới từ hệ thống!"), ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Marriage(bot))
