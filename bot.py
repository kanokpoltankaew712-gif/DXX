import discord
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime

# ========== ตั้งค่า ==========
TOKEN = "MTUzNjc3NTQ2Njk0NDMwNzIzMA.Gqez67.CCAxYGydrHCvnPNMA5VXwNnxoz9q2qSLr-JUAc"
ROLE_ID = 1518611666642669568
TARGET_CHANNEL_ID = 1518592074386112512
LOG_CHANNEL_ID = 1541283315527589928
IMAGE_URL = "https://cdn.discordapp.com/attachments/1467885884354592840/1541542272632488086/92b59e77947f1cd1dcc4a35ada5890c8.png?ex=6a8df89e&is=6a8ca71e&hm=83aa3859bbda3d47de2259c3f3d423c06b26cd6e58da4c9b3fb79fdddfbfed04"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ========== ฟังก์ชันส่ง Log ==========
async def send_log(guild, user, action, role_name):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel is None:
        print(f"❌ ไม่พบห้อง Log ID {LOG_CHANNEL_ID}")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    embed = discord.Embed(
        title="📋 บันทึกการกระทำ",
        description=f"**ผู้ใช้:** {user.mention} ({user.name}#{user.discriminator})\n**ID:** `{user.id}`\n**การกระทำ:** {action}\n**ยศ:** {role_name}\n**เวลา:** {timestamp}",
        color=discord.Color.blue() if "รับ" in action else discord.Color.orange()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text=f"เซิร์ฟเวอร์: {guild.name}", icon_url=guild.icon.url if guild.icon else None)
    
    await channel.send(embed=embed)

# ========== คลาสปุ่ม ==========
class RankView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="รับยศ", style=discord.ButtonStyle.success, custom_id="add_role", emoji="🐢")
    async def add_role_button(self, interaction: discord.Interaction, button: Button):
        if interaction.channel.id != TARGET_CHANNEL_ID:
            await interaction.response.send_message("🐢 ระบบนี้ใช้ได้เฉพาะห้องที่กำหนด", ephemeral=True)
            return

        role = interaction.guild.get_role(ROLE_ID)
        if role is None:
            await interaction.response.send_message("🐢 ไม่พบยศนี้ในเซิร์ฟเวอร์", ephemeral=True)
            return

        member = interaction.user
        bot_member = interaction.guild.me

        if not bot_member.guild_permissions.manage_roles:
            await interaction.response.send_message("🐢 บอทไม่มีสิทธิ์ Manage Roles", ephemeral=True)
            return

        if bot_member.top_role <= role:
            await interaction.response.send_message(f"🐢 บอทมียศต่ำกว่าหรือเท่ากับ {role.name}", ephemeral=True)
            return

        if role in member.roles:
            await interaction.response.send_message("🐢 คุณมียศนี้อยู่แล้ว", ephemeral=True)
        else:
            try:
                await member.add_roles(role)
                await interaction.response.send_message("🐢 คุณได้รับยศ 001 เรียบร้อยแล้ว", ephemeral=True)
                await send_log(interaction.guild, member, "รับยศ", role.name)
            except discord.Forbidden:
                await interaction.response.send_message("🐢 บอทไม่สามารถเพิ่มยศนี้ได้", ephemeral=True)

    @discord.ui.button(label="เอาออก", style=discord.ButtonStyle.danger, custom_id="remove_role", emoji="🐢")
    async def remove_role_button(self, interaction: discord.Interaction, button: Button):
        if interaction.channel.id != TARGET_CHANNEL_ID:
            await interaction.response.send_message("🐢 ระบบนี้ใช้ได้เฉพาะห้องที่กำหนด", ephemeral=True)
            return

        role = interaction.guild.get_role(ROLE_ID)
        if role is None:
            await interaction.response.send_message("🐢 ไม่พบยศนี้ในเซิร์ฟเวอร์", ephemeral=True)
            return

        member = interaction.user
        bot_member = interaction.guild.me

        if not bot_member.guild_permissions.manage_roles:
            await interaction.response.send_message("🐢 บอทไม่มีสิทธิ์ Manage Roles", ephemeral=True)
            return

        if bot_member.top_role <= role:
            await interaction.response.send_message(f"🐢 บอทมียศต่ำกว่าหรือเท่ากับ {role.name}", ephemeral=True)
            return

        if role not in member.roles:
            await interaction.response.send_message("🐢 คุณไม่มีสิทธิ์นี้อยู่แล้ว", ephemeral=True)
        else:
            try:
                await member.remove_roles(role)
                await interaction.response.send_message("🐢 คุณได้ลบยศ 001 ออกเรียบร้อยแล้ว", ephemeral=True)
                await send_log(interaction.guild, member, "เอาออก", role.name)
            except discord.Forbidden:
                await interaction.response.send_message("🐢 บอทไม่สามารถลบยศนี้ได้", ephemeral=True)

# ========== เมื่อบอทพร้อม ==========
@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user} พร้อมทำงานแล้ว!")

    for guild in bot.guilds:
        bot_member = guild.me
        print(f"\n📌 เซิร์ฟเวอร์: {guild.name}")
        print(f"   บอทมียศสูงสุด: {bot_member.top_role.name}")
        print(f"   มีสิทธิ์ Manage Roles: {bot_member.guild_permissions.manage_roles}")

        if not bot_member.guild_permissions.manage_roles:
            print(f"   ⚠️ บอทขาดสิทธิ์ Manage Roles!")
        else:
            target_role = guild.get_role(ROLE_ID)
            if target_role:
                if bot_member.top_role <= target_role:
                    print(f"   ⚠️ บอทยศ '{bot_member.top_role.name}' ต่ำกว่าหรือเท่ากับ '{target_role.name}'")
                    print(f"   🔧 กรุณาจัดลำดับยศบอทให้สูงกว่า {target_role.name}")
                else:
                    print(f"   ✅ บอทสามารถจัดการยศ {target_role.name} ได้")
            else:
                print(f"   ⚠️ ไม่พบยศ ID {ROLE_ID} ในเซิร์ฟเวอร์นี้")

    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if channel is None:
        print(f"❌ ไม่พบห้อง ID {TARGET_CHANNEL_ID}")
        return

    embed = discord.Embed(
        title="🐢 ระบบรับยศอัตโนมัติ",
        description=(
            "กดปุ่มด้านล่างเพื่อรับยศหรือเอาออกได้ทันที\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "**ยศที่รับได้**\n"
            f"<@&{ROLE_ID}>\n\n"
            "**วิธีใช้งาน**\n"
            "• กดปุ่ม `🐢 รับยศ` เพื่อรับยศ\n"
            "• กดปุ่ม `🐢 เอาออก` เพื่อลบยศ\n\n"
            "ระบบจะส่งยศให้อัตโนมัติทันที"
        ),
        color=discord.Color.from_rgb(255, 215, 0)
    )
    embed.set_image(url=IMAGE_URL)
    embed.set_footer(
        text=f"ระบบอัตโนมัติ • {guild.name}",
        icon_url=guild.icon.url if guild.icon else None
    )

    view = RankView()

    async for message in channel.history(limit=10):
        if message.author == bot.user and message.embeds:
            if "ระบบรับยศ" in message.embeds[0].title:
                await message.delete()
                break

    await channel.send(embed=embed, view=view)
    print(f"✅ ส่งข้อความระบบรับยศไปยังห้อง {channel.name} (ID: {channel.id}) เรียบร้อย")

# ========== คำสั่ง ==========
@bot.command(name="roomid")
async def show_channel_id(ctx):
    embed = discord.Embed(
        title="🆔 ไอดีห้อง",
        description=f"ห้องนี้มี ID: `{ctx.channel.id}`",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name="rank")
@commands.has_permissions(administrator=True)
async def send_rank_message(ctx):
    if ctx.channel.id != TARGET_CHANNEL_ID:
        await ctx.send("🐢 คำสั่งนี้ใช้ได้เฉพาะห้องที่กำหนด", ephemeral=True)
        return

    embed = discord.Embed(
        title="🐢 ระบบรับยศอัตโนมัติ",
        description=(
            "กดปุ่มด้านล่างเพื่อรับยศหรือเอาออกได้ทันที\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "**ยศที่รับได้**\n"
            f"<@&{ROLE_ID}>\n\n"
            "**วิธีใช้งาน**\n"
            "• กดปุ่ม `🐢 รับยศ` เพื่อรับยศ\n"
            "• กดปุ่ม `🐢 เอาออก` เพื่อลบยศ\n\n"
            "ระบบจะส่งยศให้อัตโนมัติทันที"
        ),
        color=discord.Color.from_rgb(255, 215, 0)
    )
    embed.set_image(url=IMAGE_URL)
    embed.set_footer(
        text=f"ระบบอัตโนมัติ • {ctx.guild.name}",
        icon_url=ctx.guild.icon.url if ctx.guild.icon else None
    )

    view = RankView()
    await ctx.send(embed=embed, view=view)
    await ctx.message.delete()

# ========== รัน ==========
bot.run(TOKEN)
