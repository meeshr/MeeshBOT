import os
import json
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, button, Button
from aiohttp import web, ClientSession

# ==========================================================
# 1. الإعدادات العامة والربط (CONFIGURATION & IDs)
# ==========================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GUILD_ID = discord.Object(id=714659822477246534)
FORUM_CHANNEL_ID = 1547663433850425497

# إعدادات السحابة (JSONBin)
BIN_ID = "6aadacc3ac6210605addddde"
API_KEY = "$2a$10$sNyGBL9XmGvTjuTxXfaUB.P.qLh1UtkZ7crgdlln24LWcijefCdZ6"
HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": API_KEY
}

# ==========================================================
# 2. خادم ويب مصغر لمنصة Render
# ==========================================================
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# ==========================================================
# 3. باليت الألوان
# ==========================================================
COLOR_MILK_TEA   = 0x8B6252
COLOR_COZY_BROWN = 0xB18470
COLOR_SOFT_BLUSH = 0xE8A7B8
COLOR_LIGHT_PINK = 0xF5C9D5
COLOR_CREAM      = 0xFFF4E8
COLOR_WARM_WHITE = 0xFFF9F5

# ==========================================================
# 4. باليت الصور والبنرات والـ Thumbnails
# ==========================================================
IMG_WELCOME_BANNER = "https://cdn.discordapp.com/attachments/1521473362373775481/1547882296122675210/35efc6dcbdf1fdfa3cb1848cf691847f.png"
IMG_CHECK_BANNER   = None
IMG_EMPTY_ICON     = "https://raw.githubusercontent.com/meeshr/MeeshBOT/main/pinkloading.gif"

IMG_CLAIM_DEFAULT  = "https://raw.githubusercontent.com/meeshr/MeeshBOT/main/frogconfetti.gif"
IMG_DELETE_ICON    = "https://raw.githubusercontent.com/meeshr/MeeshBOT/main/trash%20.gif"
IMG_UNCLAIM_ICON   = "https://raw.githubusercontent.com/meeshr/MeeshBOT/main/cry.gif"
IMG_CLEAR_ICON     = "https://raw.githubusercontent.com/meeshr/MeeshBOT/main/clean.gif"

# ==========================================================
# 5. الترقيم والإيموجيات
# ==========================================================
ITEM_NUM_FORMAT = "〈 {id} 〉"

def format_item_num(item_id: int) -> str:
    return ITEM_NUM_FORMAT.format(id=item_id)

EMOJI_STAR_PINK   = "<:4046pinkstar:1547907775236022322>"
EMOJI_STAR_YELLOW = "<:1805yellowstar:1547911937919156255>"
EMOJI_STAR_PURPLE = "<:6834purplestar:1547907780848001105>"
EMOJI_STAR_GREEN  = "<:5581greenstar:1547907776926322739>"
EMOJI_STAR_BLUE   = "<:8891bluestar:1547907782748020747>"

EMOJI_SPARKLE     = "<:971460simplesparkles:1547910333220528168>"
EMOJI_FROG        = "<:4251heartfrog:1547911274044719244>"
EMOJI_LOCK        = "<:822050lock:1547911158525071452>"
EMOJI_TULIP       = "<:26725tulip:1547911001289261096>"
EMOJI_CLOSE       = "<:814373redtick:1547911458229194772>"
EMOJI_HEART       = "<:7443pinkheart:1547911767684808745>"

WELCOME_MESSAGE = f"""## سجلي هنا كل شيء يعجبك، خاطرك فيه، أو تفكرين تشترينه

\u200F• {EMOJI_STAR_PINK} **إضافة غرض للقائمة** ⟵ `/add_wish`
\u200F• {EMOJI_STAR_YELLOW} **تصفح القائمة والحجز منها** ⟵ `/check_wishes`
\u200F• {EMOJI_STAR_GREEN} **إلغاء حجز غرض كنتي حجزتيه** ⟵ `/unclaim_wish`
\u200F• {EMOJI_STAR_BLUE} **حذف غرض برقم الغرض** ⟵ `/delete_wish`
\u200F• {EMOJI_STAR_PURPLE} **مسح القائمة كاملة** ⟵ `/clear_wishes`

\u200F**لو تبين تاخذين غرض:**
\u200F__تصفحي القائمة واضغطي على زر الغرض اللي تبغينه__"""

BTN_AVAILABLE_TEXT = "خليه علي {num}"
BTN_CLAIMED_TEXT   = "راحت عليك {num}"

STATUS_AVAILABLE = f"{EMOJI_HEART} متاح"
STATUS_CLAIMED   = f"{EMOJI_LOCK} مع \u202A{{name}}\u202C"

GUIDE_CHECK_WISHES = f"\n\n\u200Fاختاري رقم الغرض من الأزرار تحت {EMOJI_TULIP}"

# ==========================================================
# 6. قاعدة البيانات السحابية (JSONBin Cloud DB)
# ==========================================================
wishes_db = {}

async def load_db_async():
    url = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"
    try:
        async with ClientSession() as session:
            async with session.get(url, headers=HEADERS, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    record = data.get("record", {})
                    if isinstance(record, dict):
                        return {int(k): v for k, v in record.items() if str(k).isdigit()}
                    return {}
    except Exception as e:
        print("خطأ قراءة البيانات من السحابة:", e)
    return {}

async def save_db_async(data):
    url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
    formatted_data = {str(k): v for k, v in data.items()}
    try:
        async with ClientSession() as session:
            async with session.put(url, headers=HEADERS, json=formatted_data, timeout=10) as resp:
                if resp.status == 200:
                    print("✓ تم الحفظ في JSONBin بنجاح")
                else:
                    print(f"فشل الحفظ في JSONBin: status {resp.status}")
    except Exception as e:
        print("خطأ حفظ البيانات في السحابة:", e)

# ==========================================================
# 7. الأزرار والتفاعلات
# ==========================================================
class DismissWelcomeView(View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=None)
        self.owner_id = owner_id

    @button(label="إخفاء", emoji=discord.PartialEmoji.from_str(EMOJI_CLOSE), style=discord.ButtonStyle.secondary)
    async def dismiss(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id == self.owner_id or interaction.user.guild_permissions.manage_messages:
            await interaction.message.delete()
        else:
            await interaction.response.send_message("خاص بصاحبة المساحة", ephemeral=True)

class ClaimWishView(View):
    def __init__(self, friend_id: int, friend_name: str, items: list):
        super().__init__(timeout=180)
        self.friend_id = friend_id
        self.friend_name = friend_name
        
        for itm in items[:25]:
            item_id = itm["id"]
            num_str = format_item_num(item_id)
            if itm["claimed"]:
                btn = Button(
                    label=BTN_CLAIMED_TEXT.format(num=num_str),
                    emoji=discord.PartialEmoji.from_str(EMOJI_LOCK),
                    style=discord.ButtonStyle.secondary,
                    disabled=True,
                    custom_id=f"claim_{friend_id}_{item_id}"
                )
            else:
                btn = Button(
                    label=BTN_AVAILABLE_TEXT.format(num=num_str),
                    emoji=discord.PartialEmoji.from_str(EMOJI_FROG),
                    style=discord.ButtonStyle.primary,
                    custom_id=f"claim_{friend_id}_{item_id}"
                )
                btn.callback = self.make_claim_callback(item_id)
            self.add_item(btn)

    def make_claim_callback(self, item_id: int):
        async def callback(interaction: discord.Interaction):
            items = wishes_db.get(self.friend_id, [])
            target = next((i for i in items if i["id"] == item_id), None)
            
            if not target:
                await interaction.response.send_message("الغرض غير موجود بالقائمة", ephemeral=True)
                return
                
            num_str = format_item_num(item_id)
            if target["claimed"]:
                await interaction.response.send_message(f"سبقوك عليه، رقم `{num_str}` {EMOJI_LOCK}", ephemeral=True)
                return

            target["claimed"] = True
            target["claimed_by"] = interaction.user.display_name
            await save_db_async(wishes_db)

            for child in self.children:
                if isinstance(child, Button) and child.custom_id == f"claim_{self.friend_id}_{item_id}":
                    child.disabled = True
                    child.label = BTN_CLAIMED_TEXT.format(num=num_str)
                    child.emoji = discord.PartialEmoji.from_str(EMOJI_LOCK)
                    child.style = discord.ButtonStyle.secondary
            
            await interaction.response.edit_message(view=self)

            embed_success = discord.Embed(
                description=(
                    "## \u200Fتم الحجز بنجاح\n\n"
                    f"### \u200Fصار لك الغرض {num_str}\n\n"
                    f"### \u200Fلـ: **{self.friend_name}**\n\n"
                    f"### \u200Fالغرض: **{target['name']}**"
                ),
                color=COLOR_COZY_BROWN
            )

            # فحص الرابط وإسناد الصورة مباشرة وبشكل حتمي
            img_to_show = target.get("image_url")
            if not img_to_show or not str(img_to_show).strip().startswith("http"):
                img_to_show = IMG_CLAIM_DEFAULT

            if img_to_show:
                embed_success.set_image(url=img_to_show)

            embed_success.set_footer(text="Wishlist • سرّك في بير")
            await interaction.followup.send(embed=embed_success, ephemeral=True)

        return callback

# ==========================================================
# 8. البوت والأحداث
# ==========================================================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    global wishes_db
    wishes_db = await load_db_async()
    bot.tree.clear_commands(guild=GUILD_ID)
    await bot.tree.sync(guild=GUILD_ID)
    await bot.tree.sync()
    print(f"Online: {bot.user} | Loaded DB users: {len(wishes_db)}")

@bot.event
async def on_thread_create(thread: discord.Thread):
    if thread.parent_id == FORUM_CHANNEL_ID:
        await asyncio.sleep(2)
        embeds_list = []

        if IMG_WELCOME_BANNER:
            embed_banner = discord.Embed(color=COLOR_SOFT_BLUSH)
            embed_banner.set_image(url=IMG_WELCOME_BANNER)
            embeds_list.append(embed_banner)

        embed_text = discord.Embed(
            description=WELCOME_MESSAGE,
            color=COLOR_SOFT_BLUSH
        )
        embed_text.set_footer(text="Wishlist")
        embeds_list.append(embed_text)
        
        try:
            await thread.send(embeds=embeds_list, view=DismissWelcomeView(owner_id=thread.owner_id))
        except Exception as e:
            print(f"Error: {e}")

# ==========================================================
# 9. أوامر السلاش
# ==========================================================

@bot.tree.command(name="add_wish", description="إضافة غرض للـ Wishlist")
@app_commands.describe(
    item_name="اسم الغرض أو وصفه",
    item_url="رابط الشراء أو صفحة المنتج (اختياري)",
    image_file="صورة للغرض (اختياري)",
    image_link="رابط صورة مباشر (اختياري)"
)
async def add_wish(
    interaction: discord.Interaction, 
    item_name: str, 
    item_url: str = None, 
    image_file: discord.Attachment = None, 
    image_link: str = None
):
    if isinstance(interaction.channel, discord.Thread):
        if interaction.channel.parent_id == FORUM_CHANNEL_ID and interaction.channel.owner_id != interaction.user.id:
            await interaction.response.send_message(
                f"{EMOJI_LOCK} هذه المساحة مو مساحتك، تقدرين تضيفين أغراضك في المنشور الخاص فيك فقط",
                ephemeral=True
            )
            return

    user_id = interaction.user.id
    if user_id not in wishes_db:
        wishes_db[user_id] = []
    
    item_id = len(wishes_db[user_id]) + 1
    
    final_item_url = None
    if item_url and item_url.strip().startswith(("http://", "https://")):
        final_item_url = item_url.strip()

    final_image_url = None
    if image_file:
        final_image_url = image_file.url
    elif image_link and image_link.startswith(("http://", "https://")):
        final_image_url = image_link

    wishes_db[user_id].append({
        "id": item_id,
        "name": item_name,
        "item_url": final_item_url,
        "image_url": final_image_url,
        "claimed": False,
        "claimed_by": None
    })
    
    await save_db_async(wishes_db)
    
    num_str = format_item_num(item_id)
    title_text = f"[{item_name}]({final_item_url})" if final_item_url else item_name
    
    embed = discord.Embed(
        description=f"## {EMOJI_SPARKLE} تم إضافة الغرض \u200E\n### {num_str} — {title_text}",
        color=COLOR_LIGHT_PINK
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    
    if final_image_url:
        embed.set_image(url=final_image_url)
        
    embed.set_footer(text="Wishlist")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="check_wishes", description="تصفح Wishlist")
@app_commands.describe(friend="صاحبة الـ Wishlist")
async def check_wishes(interaction: discord.Interaction, friend: discord.Member):
    is_owner = (interaction.user.id == friend.id)
    items = wishes_db.get(friend.id, [])

    if not items:
        embed_empty = discord.Embed(
            description=f"## \u200F{EMOJI_SPARKLE} القائمة فاضية\n### \u200Fما بعد انضافت أي أغراض",
            color=COLOR_CREAM
        )
        if IMG_EMPTY_ICON:
            embed_empty.set_image(url=IMG_EMPTY_ICON)
        await interaction.response.send_message(embed=embed_empty, ephemeral=True)
        return

    if is_owner:
        desc_lines = [
            f"## {EMOJI_SPARKLE} Wishlist الخاصة بك \u200E",
            "### مراجعة لأغراضك المسجلة\n"
        ]
        for itm in items:
            name_display = f"[{itm['name']}]({itm['item_url']})" if itm.get("item_url") else itm['name']
            img_link = f" • [صورة]({itm['image_url']})" if itm.get("image_url") else ""
            num_str = format_item_num(itm['id'])
            desc_lines.append(f"**{num_str}** {name_display}{img_link}")

        embed = discord.Embed(
            description="\n".join(desc_lines),
            color=COLOR_SOFT_BLUSH
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        if IMG_CHECK_BANNER:
            embed.set_image(url=IMG_CHECK_BANNER)

        embed.set_footer(text="Wishlist • 🤫 حالة الأغراض مخفية عنك للمفاجأة ")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    desc_lines = [
        f"## Wishlist \u200E{EMOJI_SPARKLE}",
        f"###  تصفح لقائمة لـ {friend.display_name} \u202A\u202C\n"
    ]
    for itm in items:
        status = STATUS_CLAIMED.format(name=itm['claimed_by']) if itm["claimed"] else STATUS_AVAILABLE
        name_display = f"[{itm['name']}]({itm['item_url']})" if itm.get("item_url") else itm['name']
        img_link = f" • [صورة]({itm['image_url']})" if itm.get("image_url") else ""
        num_str = format_item_num(itm['id'])
        desc_lines.append(f"**{num_str}** {name_display}{img_link}\n> {status}\n")

    desc_lines.append(GUIDE_CHECK_WISHES)

    embed = discord.Embed(
        description="\n".join(desc_lines),
        color=COLOR_SOFT_BLUSH
    )
    embed.set_thumbnail(url=friend.display_avatar.url)
    if IMG_CHECK_BANNER:
        embed.set_image(url=IMG_CHECK_BANNER)

    embed.set_footer(text="Wishlist")
    
    view = ClaimWishView(friend_id=friend.id, friend_name=friend.display_name, items=items)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="unclaim_wish", description="إلغاء حجز غرض كنتي قد حجزتيه")
@app_commands.describe(friend="صاحبة الـ Wishlist", item_id="رقم الغرض المراد إلغاء حجزه")
async def unclaim_wish(interaction: discord.Interaction, friend: discord.Member, item_id: int):
    items = wishes_db.get(friend.id, [])
    
    target_item = next((itm for itm in items if itm["id"] == item_id), None)
    if not target_item:
        await interaction.response.send_message("الغرض مو موجود بالقائمة", ephemeral=True)
        return

    if not target_item["claimed"]:
        await interaction.response.send_message("هذا الغرض مو محجوز ومتاح للجميع", ephemeral=True)
        return

    if target_item.get("claimed_by") != interaction.user.display_name:
        await interaction.response.send_message("ما تقدرين تكنسلين غرض حاجزته بنت ثانية", ephemeral=True)
        return

    target_item["claimed"] = False
    target_item["claimed_by"] = None
    await save_db_async(wishes_db)

    num_str = format_item_num(item_id)
    embed = discord.Embed(
        description=(
            f"## 🔺 تم إلغاء الحجز  \u200E\n"
            f"### تم إلغاء حجزك للغرض {num_str}\n\n"
            "صار الغرض متاح بالقائمة من جديد للكل"
        ),
        color=COLOR_MILK_TEA
    )
    if IMG_UNCLAIM_ICON:
        embed.set_image(url=IMG_UNCLAIM_ICON)

    embed.set_footer(text="Wishlist")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="delete_wish", description="حذف غرض معين من قائمتك برقم الغرض")
@app_commands.describe(item_id="رقم الغرض المراد حذفه")
async def delete_wish(interaction: discord.Interaction, item_id: int):
    user_id = interaction.user.id
    items = wishes_db.get(user_id, [])
    
    target_item = next((itm for itm in items if itm["id"] == item_id), None)
    if not target_item:
        await interaction.response.send_message("الرقم مو موجود بقائمتك", ephemeral=True)
        return

    removed_image = target_item.get("image_url")

    items.remove(target_item)
    for idx, itm in enumerate(items, start=1):
        itm["id"] = idx

    await save_db_async(wishes_db)
    
    num_str = format_item_num(item_id)
    embed = discord.Embed(
        description=(
            f"## {EMOJI_SPARKLE} تم الحذف بنجاح \u200E\n"
            f"### تم حذف الغرض {num_str}\n\n"
            "> تم تحديث وترتيب أرقام قائمتك تلقائياً"
        ),
        color=COLOR_MILK_TEA
    )

    if removed_image:
        embed.set_image(url=removed_image)
    elif IMG_DELETE_ICON:
        embed.set_image(url=IMG_DELETE_ICON)

    embed.set_footer(text="Wishlist")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="clear_wishes", description="مسح كل أغراض قائمتك والبدء من جديد")
async def clear_wishes(interaction: discord.Interaction):
    user_id = interaction.user.id
    wishes_db[user_id] = []
    await save_db_async(wishes_db)

    embed = discord.Embed(
        description=(
            f"## {EMOJI_SPARKLE} تم تصفير القائمة \u200E\n"
            "### قائمتك الآن فاضية وجاهزة للبداية من جديد"
        ),
        color=COLOR_COZY_BROWN
    )
    if IMG_CLEAR_ICON:
        embed.set_image(url=IMG_CLEAR_ICON)

    embed.set_footer(text="Wishlist")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ==========================================================
# 10. تشغيل الويب سيرفر والبوت معاً
# ==========================================================
async def main():
    await start_web_server()
    async with bot:
        await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
