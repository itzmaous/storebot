import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import aiohttp  # thêm aiohttp để gọi API
import requests
import os
# Tạo intents
intents = discord.Intents.default()
intents.message_content = True

TOKEN = os.getenv("token")
# Khởi tạo bot
bot = commands.Bot(command_prefix="lfms!", intents=intents)

async def fetch_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=vnd"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data[coin_id]["vnd"]
            else:
                return None
# Map currency => coin_id trên CoinGecko
# ID người dùng được phép sử dụng lệnh
ALLOWED_USER_ID = 1219200091777269792  # Thay ID này bằng ID của bạn

# Khi bot sẵn sàng
@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Streaming(
            name="Maous Store!",
            url="https://www.youtube.com/"  # <- Link stream bắt buộc
        )
    )
    print(f"✅ Bot đã đăng nhập với tên {bot.user}")


# Tạo slash command /thanhtoan
@bot.tree.command(name="thanhtoan", description="Gửi thông tin thanh toán bằng Bank")
@app_commands.describe(
    price="Nhập số tiền cần thanh toán",
    content="Nhập nội dung thanh toán"
)
async def thanhtoan(interaction: discord.Interaction, price: int, content: str):
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    embed = discord.Embed(
        title="Thông Tin Thanh Toán",
        description="Dưới đây là thông tin thanh toán của bạn:",
        color=discord.Color.blue()
    )
    embed.add_field(name="Ngân Hàng <:Host:1363016068192276590>", value="```MBBank```", inline=False)
    embed.add_field(name="Chủ Tài Khoản <:Advisor:1363015610602094642>", value="```Đoàn Thị Phương```", inline=False)
    embed.add_field(name="Số Tài Khoản <:Mod:1363016255174475976>", value="```4349141319```", inline=False)
    embed.add_field(name="Số Tiền <:Owner:1363016408723751072>", value=f"```{price:,} VND```", inline=False)
    embed.add_field(name="Nội Dung <:Manager:1363016157615099945>", value=f"```{content}```", inline=False)

    # Thêm ảnh thumbnail vào Embed
    embed.set_image(url="https://cdn.discordapp.com/attachments/1360438958328123657/1366007520346243182/qrcode.gif?ex=680f6124&is=680e0fa4&hm=8e66532bdaff2bea7ab43daabc93350fa20bd00c7b319133314e175c1de5d61e&")  # Thay đổi đường dẫn ảnh thumbnail ở đây
    embed.set_footer(text=f"{current_time}")
    # Gửi Embed vào channel
    await interaction.response.send_message(embed=embed)

# Slash command /crypto
@bot.tree.command(name="crypto", description="Tạo lệnh thanh toán Crypto (real-time giá)")
@app_commands.describe(
    currency="Chọn loại coin (ltc, btc, usdt)",
    price="Nhập số tiền VNĐ cần thanh toán"
)
async def crypto(interaction: discord.Interaction, currency: str, price: int):
    await interaction.response.defer()

    currency = currency.lower()

    # Gán các thông tin về ví và ảnh theo từng loại coin
    if currency == "ltc":
        address = "ltc1qgvlnv5sfz8t998pzghkzrlkyw8unuevl4n6pxx"
        image_url = "https://cdn.discordapp.com/attachments/1340978671711817758/1366018561851527291/litecoin-ltc-logo.png?ex=680f6b6c&is=680e19ec&hm=c0370d2c8ee387b189e26799b53b9818cfac6f99646d3a4a60449d50e099f24f&"
        coin_id = "litecoin"
        coin_name = "LTC"
    elif currency == "btc":
        address = "bc1qsuc4rc2uknl43kqxemuyv6d3xffnds2j008gj7"
        image_url = "https://cdn.discordapp.com/attachments/1340978671711817758/1366018640608104518/bitcoin-btc-logo.png?ex=680f6b7f&is=680e19ff&hm=134084dc699180e3f6b24082bf7b04eb7de712a5c2b1252b1b157ec2059a9d8c&"
        coin_id = "bitcoin"
        coin_name = "BTC"
    elif currency == "usdt":
        address = "0x700875DF55d904b24469458a6bAE04F6dd7eF91F"
        image_url = "https://cdn.discordapp.com/attachments/1340978671711817758/1366018543484669952/tether-usdt-logo.png?ex=680f6b68&is=680e19e8&hm=d8ed968ceea050264733cdc944e397072ef08c06c5e1272b59b3b1bc2c7cccdc&"
        coin_id = "tether"
        coin_name = "USDT"
    else:
        await interaction.followup.send("Loại coin không hợp lệ! Vui lòng chọn giữa: ltc, btc, usdt.", ephemeral=True)
        return

    # Lấy giá coin
    coin_price = await fetch_price(coin_id)

    if coin_price is None:
        await interaction.followup.send("Không thể lấy giá coin hiện tại. Vui lòng thử lại.", ephemeral=True)
        return

    # Tính toán số lượng coin cần thanh toán
    amount = price / coin_price

    # Lấy giá coin
    coin_price = await fetch_price(coin_id)

    coin_name = currency.upper()

    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    embed = discord.Embed(
        title=f"Thanh Toán Bằng {coin_name}",
        description="Vui lòng chuyển khoản chính xác theo thông tin sau:",
        color=discord.Color.green()
    )
    embed.add_field(name="Loại Coin <:Developer:1363015907697229864>", value=f"```{coin_name}```", inline=True)
    embed.add_field(name="Địa Chỉ Ví <:Advisor:1363015610602094642>", value=f"```{address}```", inline=False)
    embed.add_field(name="Số Lượng <:Manager:1363016157615099945>", value=f"```{amount:.6f} {coin_name}```", inline=True)
    embed.add_field(name="Giá VNĐ <:Admin:1363015709826875442>", value=f"```{price:,} VNĐ```", inline=True)
    embed.set_thumbnail(url=image_url)
    embed.set_footer(text=f"{current_time}")

    await interaction.followup.send(embed=embed)

# Lệnh vouch
# Lệnh vouch
@bot.tree.command(name="bought", description="Thêm role buyer cho user")
@app_commands.describe(user="Chọn người dùng để add role buyer")
async def vouch(interaction: discord.Interaction, user: discord.Member):
    # Kiểm tra quyền: chỉ admin mới có thể thực hiện lệnh này
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Bạn không có quyền thực hiện lệnh này! (Admin Only)", ephemeral=True)
        return

    # Thay thế role ID với ID thực tế của role bạn muốn thêm
    role_id = 1340669678951071827  # Thay ID này bằng ID role của bạn

    role = discord.utils.get(interaction.guild.roles, id=role_id)

    if role is None:
        await interaction.response.send_message(f"Role với ID `{role_id}` không tồn tại trong server!", ephemeral=True)
        return

    # Thêm role cho user
    try:
        await user.add_roles(role)
        await interaction.response.send_message(f"Đã thêm role `{role.name}` cho {user.mention}!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("Tôi không có quyền thêm role này!", ephemeral=True)


@bot.tree.command(name="storeinfo", description="Thông tin về Maous Store")
async def store(interaction: discord.Interaction):
    message = """
# Maous Store
Bạn Đang Chưa Có Acc Pre Để Chơi Các Sever Như Hypixel?
Và Tài Chính Không Đủ Để Mua Acc Pre Gốc Từ Minecraft?

Nhưng Không Sao!
Ở **Maous Store**, Bạn Có Thể Mua acc Pre Giá Rẻ Và Hợp Với Tài Chính Của Mình!!!

### -- **Maous Store** --                             - <@1219200091777269792> -
https://discord.gg/YgwMmXQZ7K
    """

    await interaction.response.send_message(message)

@bot.tree.command(name="invite", description="Mời Maous Store vào server của bạn")
async def invite(interaction: discord.Interaction):
    invite_link = discord.utils.oauth_url(bot.user.id)
    discord_link = "https://discord.gg/YgwMmXQZ7K"
    image_url = "https://img.upanh.tv/2025/04/28/wallpaperflare.com_wallpaper-1.jpg"
    embed = discord.Embed(title="<:Creator:1363015970657927370> Đường dẫn Maous Store <:Creator:1363015970657927370>", description=f"Ấn vào đường dẫn bên dưới để mời Statsify tới máy chủ discord của bạn: \n \n <:Host:1363016068192276590> [**Invite**]({invite_link})\n <:Manager:1363016157615099945> [Discord]({discord_link})", color=discord.Color.red())
    embed.set_thumbnail(url=image_url)
    await interaction.response.send_message(embed=embed)

# Thêm token API của bạn vào đây (có thể lấy tại https://www.exchangerate-api.com/)
API_KEY = "f8469d943c1843f456c624ce"

@bot.tree.command(name="convert", description="Chuyển đổi giữa các loại tiền tệ")
@app_commands.describe(amount="Số tiền bạn muốn chuyển đổi", from_currency="Loại tiền tệ ban đầu", to_currency="Loại tiền tệ bạn muốn chuyển đến")
async def convert(interaction: discord.Interaction, amount: float, from_currency: str, to_currency: str):
    # Gọi API để lấy tỷ giá hối đoái
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
    response = requests.get(url)
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if response.status_code != 200:
        await interaction.response.send_message("Có lỗi xảy ra khi lấy tỷ giá. Vui lòng thử lại sau.", ephemeral=True)
        return
    
    data = response.json()
    
    if 'conversion_rates' not in data:
        await interaction.response.send_message("Không thể tìm thấy tỷ giá cho các loại tiền tệ này.", ephemeral=True)
        return
    
    rates = data['conversion_rates']
    
    if to_currency.upper() not in rates:
        await interaction.response.send_message(f"Không thể chuyển đổi từ {from_currency.upper()} sang {to_currency.upper()}.", ephemeral=True)
        return

    # Tính toán số tiền sau khi chuyển đổi
    converted_amount = amount * rates[to_currency.upper()]
    
    # Tạo embed kết quả
    embed = discord.Embed(title="<:Creator:1363015970657927370> Kết quả chuyển đổi <:Creator:1363015970657927370>", color=discord.Color.blue())
    embed.add_field(name="<:Admin:1363015709826875442> Số tiền bạn muốn chuyển <:Admin:1363015709826875442>", value=f"```{amount:,.0f} {from_currency.upper()}```", inline=False)
    embed.add_field(name="<:Host:1363016068192276590> Số tiền sau chuyển đổi <:Host:1363016068192276590>", value=f"```{converted_amount:.2f} {to_currency.upper()}```", inline=False)
    embed.set_footer(text=f"{current_time}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="status", description="Thay đổi trạng thái và hoạt động của bot với một thông điệp tùy chỉnh")
async def status(interaction: discord.Interaction, status: str, doing: str, text: str):
    """Thay đổi trạng thái và kiểu hoạt động của bot."""

    # Kiểm tra nếu người dùng không phải là người được phép
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return

    # Xử lý trạng thái
    status = status.lower()
    if status == "online":
        bot_status = discord.Status.online
    elif status == "idle":
        bot_status = discord.Status.idle
    elif status == "dnd":
        bot_status = discord.Status.dnd
    elif status == "offline":
        bot_status = discord.Status.offline
    else:
        await interaction.response.send_message(
            "⚠️ Trạng thái không hợp lệ. Chọn từ: **online, idle, dnd, offline**.",
            ephemeral=True
        )
        return

    # Xử lý hoạt động
    doing = doing.lower()
    if doing == "playing":
        activity = discord.Game(name=text)
    elif doing == "watching":
        activity = discord.Activity(type=discord.ActivityType.watching, name=text)
    elif doing == "listening":
        activity = discord.Activity(type=discord.ActivityType.listening, name=text)
    elif doing == "competing":
        activity = discord.Activity(type=discord.ActivityType.competing, name=text)
    else:
        await interaction.response.send_message(
            "⚠️ Hoạt động không hợp lệ. Chọn từ: **playing, watching, listening, competing**.",
            ephemeral=True
        )
        return

    # Thay đổi trạng thái và hoạt động
    await bot.change_presence(status=bot_status, activity=activity)

    await interaction.response.send_message(
        f"✅ Đã thay đổi trạng thái thành **{status.capitalize()}** với hoạt động **{doing.capitalize()}**: {text}",
        ephemeral=True
    )

# Chạy bot với token
bot.run(TOKEN)
