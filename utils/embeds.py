import discord


def base_embed(title: str, desc: str, color=discord.Color.pink()):
    """Tạo embed cơ bản"""
    embed = discord.Embed(title=title, description=desc, color=color)
    return embed


def error_embed(desc: str):
    """Embed lỗi"""
    return base_embed("⚠️ Lỗi", desc, color=discord.Color.red())


def success_embed(desc: str):
    """Embed thành công"""
    return base_embed("✅ Thành công", desc, color=discord.Color.green())


def love_embed(desc: str):
    """Embed chủ đề tình yêu"""
    return base_embed("💖 Tình yêu 💖", desc, color=discord.Color.pink())


def job_embed(desc: str):
    """Embed chủ đề công việc"""
    return base_embed("⚒️ Công việc ⚒️", desc, color=discord.Color.gold())
