import discord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv

def run_bot():  # Định nghĩa hàm chạy bot
    load_dotenv()  # Tải các biến môi trường từ file .env
    TOKEN = os.getenv('discord_token')  # Lấy token của bot từ biến môi trường
    intents = discord.Intents.default()  # Cài đặt các intents mặc định cho bot
    intents.message_content = True  # Cho phép bot đọc nội dung tin nhắn
    client = discord.Client(intents=intents)  # Khởi tạo client Discord với các intents đã cài đặt


    queues = {}  # Khởi tạo dictionary để lưu trữ các hàng đợi cho các kênh thoại
    voice_clients = {}  # Khởi tạo dictionary để lưu trữ các voice client (kết nối kênh thoại)
    yt_dl_options = {"format": "bestaudio/best"}  # Cài đặt tùy chọn cho yt-dlp để tải âm thanh tốt nhất
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)  # Khởi tạo đối tượng yt_dlp với các tùy chọn trên


    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}  # Cài đặt cho FFmpeg để xử lý âm thanh và kết nối lại nếu bị mất kết nối


    @client.event  # Định nghĩa sự kiện khi bot đã sẵn sàng
    async def on_ready():  # Khi bot đã đăng nhập thành công và sẵn sàng hoạt động
        print(f'{client.user} is now jamming')  # In ra thông báo rằng bot đã sẵn sàng

    @client.event  # Định nghĩa sự kiện khi có tin nhắn gửi đến bot
    async def on_message(message):  # Khi bot nhận được tin nhắn
        if message.content.startswith("?play"):  # Nếu tin nhắn bắt đầu bằng "?play"

            try:
                voice_client = await message.author.voice.channel.connect()  # Kết nối bot vào kênh thoại của người gửi tin nhắn
                voice_clients[voice_client.guild.id] = voice_client  # Lưu trữ kết nối voice client cho server
            except Exception as e:
                print(e)  # In ra lỗi nếu có


            try:
                url = message.content.split()[1]  # Lấy URL từ tin nhắn (sau từ "?play")
                loop = asyncio.get_event_loop()  # Lấy vòng lặp sự kiện bất đồng bộ
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))  # Lấy thông tin âm thanh từ URL mà không tải xuống
                song = data['url']  # Lấy URL của âm thanh từ thông tin trích xuất
                player = discord.FFmpegOpusAudio(song, **ffmpeg_options)  # Tạo đối tượng audio player với các tùy chọn FFmpeg
                voice_clients[message.guild.id].play(player)  # Phát âm thanh trong kênh thoại
            except Exception as e:
                print(e)  # In ra lỗi nếu có


        if message.content.startswith("?pause"):  # Nếu tin nhắn bắt đầu bằng "?pause"
            try:
                voice_clients[message.guild.id].pause()  # Tạm dừng phát âm thanh
            except Exception as e:
                print(e)  # In ra lỗi nếu có


        if message.content.startswith("?resume"):  # Nếu tin nhắn bắt đầu bằng "?resume"
            try:
                voice_clients[message.guild.id].resume()  # Tiếp tục phát âm thanh đã tạm dừng
            except Exception as e:
                print(e)  # In ra lỗi nếu có


        if message.content.startswith("?stop"):  # Nếu tin nhắn bắt đầu bằng "?stop"
            try:
                voice_clients[message.guild.id].stop()  # Dừng phát âm thanh
                await voice_clients[message.guild.id].disconnect()  # Ngắt kết nối với kênh thoại
            except Exception as e:
                print(e)  # In ra lỗi nếu có


    client.run(TOKEN)  # Chạy bot với token đã cung cấp để kết nối với Discord
