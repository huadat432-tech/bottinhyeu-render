import discord
from discord.ext import commands
import asyncio
import random
import os

from utils.file_manager import get_user, update_user


class Jobs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("⚒️ jobs.py đã được load")

    @commands.command(name="lamviec")
    async def lam_viec(self, ctx):
        await self.show_job_menu(ctx, caller=ctx.author)

    async def show_job_menu(self, ctx_or_interaction, caller):
        """Hiển thị menu chọn nghề (cho người gọi cụ thể)"""
        embed = discord.Embed(
            title="⚒️ Chọn công việc",
            description=f"{caller.mention}, hãy chọn một trong hai nghề để kiếm **xu 💰** và **vật phẩm 🎁**:",
            color=discord.Color.blurple()
        )

        view = discord.ui.View(timeout=60)

        # ========================
        # 🧹 Nghề: Nhặt Rác
        # ========================
        async def nhatrac_callback(interaction: discord.Interaction):
            if interaction.user != caller:
                return await interaction.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)

            file_path = os.path.join("images", "nhatrac.gif")
            file = discord.File(file_path, filename="nhatrac.gif") if os.path.exists(file_path) else None

            embed_working = discord.Embed(
                title="🧹 Đang nhặt rác...",
                description="Bạn đang cần mẫn nhặt từng túi rác... 🧺",
                color=discord.Color.orange()
            )
            if file:
                embed_working.set_image(url="attachment://nhatrac.gif")

            await interaction.response.edit_message(embed=embed_working, attachments=[file] if file else None, view=None)

            await asyncio.sleep(5)

            # Kết quả
            items = [None, "🌸 Hoa", "🧸 Gấu bông", "💍 Dây chuyền"]
            weights = [50, 30, 15, 5]
            item = random.choices(items, weights=weights)[0]
            coins_earned = random.randint(1, 4)

            user = get_user(interaction.user.id)
            user["xu"] = user.get("xu", 0) + coins_earned

            if item:
                inv = user.setdefault("inventory", {})
                inv[item] = inv.get(item, 0) + 1
                msg = f"✅ Bạn đã nhặt được **{item}** và kiếm được 💰 **{coins_earned} xu**!"
            else:
                msg = f"😢 Bạn không nhặt được gì... nhưng vẫn kiếm được 💰 **{coins_earned} xu**!"

            update_user(interaction.user.id, user)

            # View tiếp tục hoặc nghỉ
            view2 = discord.ui.View(timeout=30)

            async def tieptuc_callback(i: discord.Interaction):
                if i.user != caller:
                    return await i.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
                await self.show_job_menu(i, caller)

            async def nghingoi_callback(i: discord.Interaction):
                if i.user != caller:
                    return await i.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
                await i.message.edit(
                    embed=discord.Embed(
                        title="🛏️ Nghỉ ngơi",
                        description=f"{caller.mention} đã chọn nghỉ ngơi. Hẹn gặp lại sau!",
                        color=discord.Color.light_grey()
                    ),
                    view=None
                )

            btn_tieptuc = discord.ui.Button(label="🔁 Tiếp tục làm việc", style=discord.ButtonStyle.success)
            btn_tieptuc.callback = tieptuc_callback

            btn_nghi = discord.ui.Button(label="🛑 Nghỉ ngơi", style=discord.ButtonStyle.secondary)
            btn_nghi.callback = nghingoi_callback

            view2.add_item(btn_tieptuc)
            view2.add_item(btn_nghi)

            embed_done = discord.Embed(
                title="🧹 Kết quả công việc",
                description=f"{msg}\n\n🤔 **Bạn muốn làm gì tiếp theo?**",
                color=discord.Color.green()
            )

            await interaction.message.edit(embed=embed_done, view=view2, attachments=[])

        # ========================
        # ⛏️ Nghề: Đào Đá
        # ========================
        async def daoda_callback(interaction: discord.Interaction):
            if interaction.user != caller:
                return await interaction.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)

            file_path = os.path.join("images", "daoda.gif")
            file = discord.File(file_path, filename="daoda.gif") if os.path.exists(file_path) else None

            embed_working = discord.Embed(
                title="⛏️ Đang đào đá...",
                description="Bạn đang đào sâu trong mỏ... 💎",
                color=discord.Color.blue()
            )
            if file:
                embed_working.set_image(url="attachment://daoda.gif")

            await interaction.response.edit_message(embed=embed_working, attachments=[file] if file else None, view=None)

            await asyncio.sleep(5)

            gems = ["💎 Kim cương", "🔮 Ngọc bích", "🥇 Vàng", None]
            weights = [10, 20, 40, 30]
            gem = random.choices(gems, weights=weights)[0]
            coins_earned = random.randint(5, 7)

            user = get_user(interaction.user.id)
            user["xu"] = user.get("xu", 0) + coins_earned

            if gem:
                inv = user.setdefault("inventory", {})
                inv[gem] = inv.get(gem, 0) + 1
                msg = f"✨ Bạn đã đào được **{gem}** và kiếm được 💰 **{coins_earned} xu**!"
            else:
                msg = f"🪨 Bạn không tìm thấy gì cả... nhưng vẫn kiếm được 💰 **{coins_earned} xu**!"

            update_user(interaction.user.id, user)

            view2 = discord.ui.View(timeout=30)

            async def tieptuc_callback(i: discord.Interaction):
                if i.user != caller:
                    return await i.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
                await self.show_job_menu(i, caller)

            async def nghingoi_callback(i: discord.Interaction):
                if i.user != caller:
                    return await i.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
                await i.message.edit(
                    embed=discord.Embed(
                        title="🛏️ Nghỉ ngơi",
                        description=f"{caller.mention} đã chọn nghỉ ngơi. Hẹn gặp lại sau!",
                        color=discord.Color.light_grey()
                    ),
                    view=None
                )

            btn_tieptuc = discord.ui.Button(label="🔁 Tiếp tục làm việc", style=discord.ButtonStyle.success)
            btn_tieptuc.callback = tieptuc_callback

            btn_nghi = discord.ui.Button(label="🛑 Nghỉ ngơi", style=discord.ButtonStyle.secondary)
            btn_nghi.callback = nghingoi_callback

            view2.add_item(btn_tieptuc)
            view2.add_item(btn_nghi)

            embed_done = discord.Embed(
                title="⛏️ Kết quả công việc",
                description=f"{msg}\n\n🤔 **Bạn muốn làm gì tiếp theo?**",
                color=discord.Color.green()
            )

            await interaction.message.edit(embed=embed_done, view=view2, attachments=[])

        # ============== Buttons ==============
        btn1 = discord.ui.Button(label="🧹 Nhặt rác", style=discord.ButtonStyle.success)
        btn1.callback = nhatrac_callback

        btn2 = discord.ui.Button(label="⛏️ Đào đá", style=discord.ButtonStyle.primary)
        btn2.callback = daoda_callback

        view.add_item(btn1)
        view.add_item(btn2)

        # Nếu là Interaction (người bấm Tiếp tục)
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.message.edit(embed=embed, view=view, attachments=[])
        else:
            await ctx_or_interaction.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Jobs(bot))
