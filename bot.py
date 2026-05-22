import discord
from discord.ext import commands, tasks
import datetime
import asyncio 
import json
import os
from flask import Flask
from threading import Thread

DATA_CHANNEL_ID = 123456789012345678  # SẾP DÁN ID KÊNH ẨN VÀO ĐÂY!

# ==========================================
# 🌐 WEB GIẢ ĐỂ ĐÁNH LỪA RENDER (KEEP ALIVE)
# ==========================================
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Lee Store đang hoạt động mượt mà 24/7 nha sếp!"

def run():
    # Ép thằng Render tự động lấy đúng cái cổng của nó
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# 1. CẤU HÌNH BẢO MẬT (DÀNH CHO RENDER)
# ==========================================
TOKEN = os.getenv('TOKEN')
PREFIX = '!'

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

ROLE_BUYER = "𝕭𝖚𝖞𝖊𝖗"
ROLE_1_SAO = "★"
ROLE_2_SAO = "★★"
ROLE_3_SAO = "★★★"

LEE_STORE_LINK = "https://discord.gg/hVjDERZ4g" 
LINK_ANH_BANG_GIA = "https://media.discordapp.net/attachments/1449229498707869728/1503955517087682651/IMG_20260513_100202.jpg"

# ==========================================
# 💾 HỆ THỐNG LƯU TRỮ (Kênh PR & Đơn hàng)
# ==========================================
async def tai_du_lieu():
    """Tải dữ liệu từ mây Discord"""
    channel = bot.get_channel(DATA_CHANNEL_ID)
    if channel:
        async for message in channel.history(limit=1):
            try:
                content = message.content.strip()
                if content.startswith("```json") and content.endswith("```"):
                    content = content[7:-3].strip()
                return json.loads(content)
            except: pass
    return {"pr_channels": [], "buyers": {}}

async def luu_du_lieu(data):
    """Lưu dữ liệu lên mây Discord"""
    channel = bot.get_channel(DATA_CHANNEL_ID)
    if channel:
        try: await channel.purge(limit=5)
        except: pass
        await channel.send(f"```json\n{json.dumps(data, indent=4)}\n```")
# ==========================================
# 🎫 HỆ THỐNG CẤP ROLE VIP BUYER BẰNG LỆNH CHAT
# ==========================================
@bot.command()
@commands.has_permissions(administrator=True)
async def done(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("❌ Sếp quên tag tên khách rồi! Gõ như vầy nè: `!done @khách`")
        
    user_id = str(member.id)
    stats = {}
    
user_id = str(member.id)
    
    # --- ĐOẠN MỚI THAY VÀO ---
    data = await tai_du_lieu()
    buyers = data.get("buyers", {})
    
    buyers[user_id] = buyers.get(user_id, 0) + 1
    done_count = buyers[user_id]
    
    data["buyers"] = buyers
    await luu_du_lieu(data)
    # --------------------------

    guild = ctx.guild
    roles_to_add = []
    msg_vip = ""
    
    r_buyer = discord.utils.get(guild.roles, name=ROLE_BUYER)
    r_1 = discord.utils.get(guild.roles, name=ROLE_1_SAO)
    r_2 = discord.utils.get(guild.roles, name=ROLE_2_SAO)
    r_3 = discord.utils.get(guild.roles, name=ROLE_3_SAO)

    if r_buyer and r_buyer not in member.roles: roles_to_add.append(r_buyer)
    if done_count >= 5 and r_1 and r_1 not in member.roles: roles_to_add.append(r_1); msg_vip = "🌟 Thăng cấp **1 Sao**!"
    if done_count >= 10 and r_2 and r_2 not in member.roles: roles_to_add.append(r_2); msg_vip = "🌟 Thăng cấp **2 Sao**!"
    if done_count >= 15 and r_3 and r_3 not in member.roles: roles_to_add.append(r_3); msg_vip = "👑 Thăng cấp **3 Sao VIP**!"

    if roles_to_add:
        try: await member.add_roles(*roles_to_add)
        except Exception as e: print(f"Lỗi cấp role: {e}")

    await ctx.send(f"🎉 **Chốt đơn thành công!**\n• Khách hàng: {member.mention}\n• Tổng số đơn đã mua: **{done_count}**\n{msg_vip}")

@bot.event
async def on_ready():
    print(f'🤖 Bot PR & VIP đã thức tỉnh trên Render!')
    if not auto_pr_task.is_running(): 
        auto_pr_task.start()

# ==========================================
# 📢 HỆ THỐNG AUTO PR
# ==========================================
@tasks.loop(minutes=1)
async def auto_pr_task():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    if now.hour == 12 and now.minute == 0:
        data = await tai_du_lieu()
        channels_list = data.get("pr_channels", [])
        
        if not channels_list:
            return print("⚠️ Danh sách kênh PR trống, không chạy.")
            
        embed = discord.Embed(
            title="🌸 LEE STORE - ALL DỊCH VỤ ROBLOX UY TÍN 🌸", 
            description=f"Chào mọi người! Ai có nhu cầu về Roblox - Blox Fruit thì ghé ngay Lee Store nhé!\n\n🔥 **Dịch vụ:**\n• Mua Robux tự động\n• Cày thuê Blox Fruit\n• Gift Gamepass/Perm giá rẻ\n\n👉 **Vào ngay:** {LEE_STORE_LINK}\n━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎", 
            color=0xFFB6C1
        )
        embed.set_image(url=LINK_ANH_BANG_GIA) 
        
        for ch_id in channels_list:
            try:
                channel = bot.get_channel(ch_id)
                if channel: await channel.send(content="📢 @everyone ơi, ghé shop ủng hộ nào!", embed=embed)
            except: pass

@bot.command()
@commands.has_permissions(administrator=True)
async def them_kenh_pr(ctx, channel_id: int):
    data = await tai_du_lieu()
    danh_sach = data.get("pr_channels", [])
    
    if channel_id not in danh_sach:
        danh_sach.append(channel_id)
        data["pr_channels"] = danh_sach
        await luu_du_lieu(data) 
        await ctx.send(f"✅ Đã thêm kênh `{channel_id}` vào mây Discord an toàn!")
    else:
        await ctx.send("⚠️ Kênh này đã có sẵn rồi sếp!")

@bot.command()
@commands.has_permissions(administrator=True)
async def xem_kenh_pr(ctx):
    data = await tai_du_lieu()
    await ctx.send(f"📋 **Danh sách ID kênh PR hiện tại:**\n`{data.get('pr_channels', [])}`")

@bot.command()
@commands.has_permissions(administrator=True)
async def test_pr(ctx):
    await ctx.send("⏳ Đang lấy dữ liệu và test PR...")
    data = await tai_du_lieu()
    channels_list = data.get("pr_channels", [])
    
    embed = discord.Embed(title="🌸 LEE STORE - ALL DỊCH VỤ ROBLOX 🌸", description=f"Chào mọi người! Ghé ngay Lee Store nhé!\n\n👉 **Vào ngay:** {LEE_STORE_LINK}\n━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎━︎", color=0xFFB6C1)
    embed.set_image(url=LINK_ANH_BANG_GIA)
    count = 0
    for ch_id in channels_list:
        try:
            channel = bot.get_channel(ch_id)
            if channel: 
                await channel.send(content="📢 @everyone, ghé shop ủng hộ nào! *(Tin nhắn Test PR)*", embed=embed)
                count += 1
        except Exception as e: await ctx.send(f"❌ Lỗi kênh {ch_id}: {e}")
    await ctx.send(f"✅ Xong! Đã test thành công trên {count} kênh.")

# Bật Web giả lên trước rồi mới bật Bot
keep_alive()
bot.run(TOKEN)