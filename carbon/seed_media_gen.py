"""
Generate a seed-media set for the CARBON test emulators.

Covers every on-device file type the dataset's bug reports need (determined by
auditing the run logs + bug reports):
  - Images: JPG, PNG (large + small), WEBP, animated GIF, plus >=2 in one album
  - Videos: short MP4 clips (H.264)
  - Audio:  MP3 files with ID3 title/artist tags
  - Docs:   TXT + MD (each containing a URL), a ZIP archive, a PDF, nested folders

Output is staged under carbon/seed_media/<android_dest>/... mirroring the
target on-device folders, so push_seed_media can adb-push each subtree to the
matching /sdcard location.

Run:  python seed_media_gen.py
"""
import os
import struct
import wave
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

try:
    import numpy as np
    import imageio
    import imageio_ffmpeg  # noqa: F401  (ensures bundled ffmpeg is available)
    HAVE_VIDEO = True
except Exception as e:
    print(f"[seed] video/audio libs unavailable ({e}); will still make images/docs")
    HAVE_VIDEO = False

SEED_ROOT = Path(__file__).resolve().parent / "seed_media"

# Android public dirs (relative names used as staging subfolders)
PICTURES = SEED_ROOT / "Pictures"
DCIM = SEED_ROOT / "DCIM" / "Camera"
MOVIES = SEED_ROOT / "Movies"
MUSIC = SEED_ROOT / "Music"
DOCUMENTS = SEED_ROOT / "Documents"
DOWNLOAD = SEED_ROOT / "Download"


def _mkdirs():
    for d in [PICTURES, DCIM, MOVIES, MUSIC, DOCUMENTS, DOWNLOAD]:
        d.mkdir(parents=True, exist_ok=True)


def _gradient(w, h, c1, c2):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(c1[0] * (1 - t) + c2[0] * t)
        g = int(c1[1] * (1 - t) + c2[1] * t)
        b = int(c1[2] * (1 - t) + c2[2] * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    d = ImageDraw.Draw(img)
    d.rectangle([w // 4, h // 4, 3 * w // 4, 3 * h // 4], outline=(255, 255, 255), width=6)
    return img


def make_images():
    # Large JPG + PNG (bigger than a 1080x2280 screen so pinch-zoom has room)
    _gradient(1600, 2600, (200, 40, 40), (40, 40, 200)).save(PICTURES / "photo_large_01.jpg", quality=90)
    _gradient(2000, 1500, (40, 160, 60), (10, 30, 90)).save(PICTURES / "photo_large_02.png")
    # Two images in the SAME album/folder (swipe-to-next-photo case _642)
    _gradient(1200, 1600, (240, 200, 40), (200, 60, 120)).save(DCIM / "album_a.jpg", quality=90)
    _gradient(1200, 1600, (60, 200, 220), (30, 60, 160)).save(DCIM / "album_b.jpg", quality=90)
    # Small image smaller than screen (case _678: ~834x700)
    _gradient(834, 700, (180, 180, 180), (60, 60, 60)).save(PICTURES / "photo_small_834x700.jpg", quality=90)
    # WEBP (case _363)
    _gradient(1280, 960, (120, 40, 160), (240, 220, 60)).save(PICTURES / "image_webp_01.webp")
    # Extra PNG (case _289 mentions both jpg and png)
    _gradient(1080, 1080, (255, 120, 0), (0, 80, 160)).save(PICTURES / "image_square.png")
    # Animated GIF (case _847)
    frames = []
    for i in range(8):
        f = Image.new("RGB", (480, 480), (0, 0, 0))
        dd = ImageDraw.Draw(f)
        x = 40 + i * 40
        dd.ellipse([x, 180, x + 120, 300], fill=(255, 200 - i * 20, i * 30))
        frames.append(f)
    frames[0].save(PICTURES / "animated_01.gif", save_all=True, append_images=frames[1:],
                   duration=120, loop=0)
    print("[seed] images done")


def make_videos():
    if not HAVE_VIDEO:
        print("[seed] SKIP videos (no ffmpeg)")
        return
    # Two short 720p H.264 clips, ~4s each, moving color block
    for name, base in [("clip_01.mp4", (30, 60, 160)), ("clip_02.mp4", (160, 40, 40))]:
        path = MOVIES / name
        w, h, fps, secs = 1280, 720, 24, 4
        writer = imageio.get_writer(str(path), fps=fps, codec="libx264",
                                    macro_block_size=None, ffmpeg_log_level="error")
        total = fps * secs
        for i in range(total):
            frame = np.zeros((h, w, 3), dtype=np.uint8)
            frame[:, :] = base
            x = int((w - 200) * (i / total))
            frame[h // 2 - 100:h // 2 + 100, x:x + 200] = (240, 240, 240)
            writer.append_data(frame)
        writer.close()
    # One copy into Download too (mpvKt picker defaults to Downloads)
    import shutil
    shutil.copy(MOVIES / "clip_01.mp4", DOWNLOAD / "sample_video.mp4")
    print("[seed] videos done")


def _write_mp3(path, seconds=5, freq=440, title="Seed Track", artist="CARBON Seed"):
    """Write a minimal valid MP3 via ffmpeg (from a generated tone WAV)."""
    if not HAVE_VIDEO:
        return
    import subprocess
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    tmp_wav = path.with_suffix(".wav")
    # generate a sine-tone WAV
    framerate = 44100
    n = int(framerate * seconds)
    with wave.open(str(tmp_wav), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(framerate)
        for i in range(n):
            val = int(32767 * 0.3 * np.sin(2 * np.pi * freq * (i / framerate)))
            w.writeframes(struct.pack("<h", val))
    # transcode to mp3 with ID3 tags
    subprocess.run([ffmpeg, "-y", "-i", str(tmp_wav),
                    "-metadata", f"title={title}", "-metadata", f"artist={artist}",
                    "-metadata", "album=CARBON Seed Album",
                    "-codec:a", "libmp3lame", "-qscale:a", "5", str(path)],
                   check=True, capture_output=True)
    tmp_wav.unlink(missing_ok=True)


def make_audio():
    if not HAVE_VIDEO:
        print("[seed] SKIP audio (no ffmpeg)")
        return
    tracks = [("song_01.mp3", 440, "Morning Light", "Aurora"),
              ("song_02.mp3", 523, "Blue Horizon", "Aurora"),
              ("song_03.mp3", 659, "Night Drive", "Nocturne")]
    for name, freq, title, artist in tracks:
        _write_mp3(MUSIC / name, seconds=6, freq=freq, title=title, artist=artist)
    print("[seed] audio done")


def make_docs():
    # TXT + MD each containing a URL (Markor case _2746)
    (DOCUMENTS / "note.txt").write_text(
        "Seed note for testing.\nVisit https://example.com/page for details.\n",
        encoding="utf-8")
    (DOCUMENTS / "readme.md").write_text(
        "# Seed Markdown\n\nA link: https://github.com/example/repo\n\n- item one\n- item two\n",
        encoding="utf-8")
    # A small PDF (valid minimal PDF)
    pdf = (b"%PDF-1.4\n"
           b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
           b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
           b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 300 200]>>endobj\n"
           b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
           b"0000000052 00000 n \n0000000101 00000 n \n"
           b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n170\n%%EOF\n")
    (DOCUMENTS / "document.pdf").write_bytes(pdf)
    # Nested folders with files (File-Manager case _136)
    sub = DOCUMENTS / "SampleFolder" / "Nested"
    sub.mkdir(parents=True, exist_ok=True)
    (sub / "inner.txt").write_text("nested file\n", encoding="utf-8")
    (DOCUMENTS / "SampleFolder" / "top.txt").write_text("top file\n", encoding="utf-8")
    # A ZIP archive (File-Manager case _195)
    zip_path = DOWNLOAD / "archive.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("hello.txt", "inside the zip\n")
        z.writestr("folder/data.txt", "more zip content\n")
    print("[seed] docs done")


def main():
    _mkdirs()
    make_images()
    make_videos()
    make_audio()
    make_docs()
    # Report what was generated
    print("\n[seed] generated files:")
    for p in sorted(SEED_ROOT.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(SEED_ROOT)}  ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
