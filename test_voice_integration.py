# test_audio.py
import imageio_ffmpeg as ffmpeg
from pydub import AudioSegment

# Configure before using
AudioSegment.converter = ffmpeg.get_ffmpeg_exe()
AudioSegment.ffprobe = ffmpeg.get_ffmpeg_exe()

print("✅ FFmpeg configured successfully!")
print("Path:", ffmpeg.get_ffmpeg_exe())

# Test creating a simple audio segment
try:
    # Create a 1 second silent audio
    silent = AudioSegment.silent(duration=1000)
    print("✅ AudioSegment working!")
except Exception as e:
    print(f"❌ Error: {e}")