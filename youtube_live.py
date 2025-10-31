import subprocess

# URL استریم یوتیوب
youtube_url = "rtmp://a.rtmp.youtube.com/live2/jd1t-g6tb-3m6h-w9tp-1esa"

# تنظیمات ffmpeg برای مصرف کم اینترنت و کیفیت پایدار
cmd = [
    "ffmpeg",
    "-f", "avfoundation",
    "-framerate", "30",  # فریم‌ریت پایین‌تر برای کاهش حجم
    "-pixel_format", "uyvy422",
    "-video_size", "640x480",  # رزولوشن 480p به‌جای 720p
    "-i", "0:0",
    "-vf", "format=yuv420p",
    "-c:v", "libx264",
    "-preset", "superfast",  # فشرده‌سازی سریع‌تر
    "-b:v", "600k",          # کاهش bitrate برای صرفه‌جویی در پهنای باند
    "-maxrate", "700k",
    "-bufsize", "900k",
    "-c:a", "aac",
    "-b:a", "96k",           # کاهش bitrate صدا
    "-ar", "44100",          # نرخ نمونه‌برداری استاندارد
    "-f", "flv",
    youtube_url
]

subprocess.run(cmd)
