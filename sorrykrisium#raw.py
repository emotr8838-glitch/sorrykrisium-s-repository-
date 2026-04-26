# Demo visual fullscreen + bytebeat modes
# MODE 1 -> MODE 2 -> MODE 3 -> MODE 4 -> MODE 5 -> MODE 6
# masing-masing 40 detik lalu loop
# ESC = stop
#
# Visual-only demo:
# invert / shift / tunnel / scroll / blur / melt

import ctypes
import time
import threading
import random
import sounddevice as sd

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

VK_ESCAPE = 0x1B
PATINVERT = 0x005A0049
SRCCOPY = 0x00CC0020

screen_w = 1920
screen_h = 1080

running = True
current_mode = 1
t_counter = 0

sample_rate = 8000
buffer_size = 2048


# =========================================================
# BYTEBEAT 1
# =========================================================

def bytebeat1(t):
    return (
        t * (
            (7 if ((t & 4096) and (t % 65536 < 59392))
             else (t >> 6 if (t & 4096) else 16))
            + (1 & (t >> 14))
        )
        >> (3 & (-t >> (2 if (t & 2048) else 10)))
        | (
            t >> (
                4 if (t & 16384 and t & 4096)
                else 3 if (t & 16384)
                else 2
            )
        )
    ) & 255


# =========================================================
# BYTEBEAT 2
# =========================================================

def bytebeat2(t):
    return (t * ((t >> 9 | t >> 13) & 15) & 129) & 255


# =========================================================
# BYTEBEAT 3
# =========================================================

def bytebeat3(t):
    return (
        ((~t >> 2) *
         (
             2 + (
                 (42 & 2 * t * (7 & (t >> 10)))
                 <
                 (24 & t * ((3 & (t >> 14)) + 2))
             )
         ))
    ) & 255


# =========================================================
# BYTEBEAT 4
# =========================================================

def bytebeat4(t):
    return (
        (
            (
                (((t >> 10) & 44) % 32 >> 1)
                +
                (((t >> 9) & 44) % 32 >> 1)
            )
            *
            (
                1 if (t % 65536) < 32768
                else 1
            )
            *
            t
            |
            (t >> 3)
        )
        *
        (
            t
            |
            (t >> 8)
            |
            (t >> 6)
        )
    ) & 255


# =========================================================
# BYTEBEAT 5
# =========================================================

def bytebeat5(t):
    return (
        (
            (t >> 4 >> (t & (t >> 11)))
            *
            (
                -1 if ((t >> 4 >> (t & (t >> 11))) & 128)
                else 1
            )
        )
        +
        (
            (t >> (t // (2 if (t & 65536) else 3))) & 63
        )
        +
        (
            (30000 // (t & 4095 if (t & 4095) != 0 else 1)) & 100
        )
    ) & 255


# =========================================================
# BYTEBEAT 6
# =========================================================

def bytebeat6(t):
    denom = ((t >> 2) ^ (t >> 12))
    if denom == 0:
        denom = 1

    return (
        (800000 * t) // denom
    ) & 255


# =========================================================
# AUDIO
# =========================================================

def audio_callback(outdata, frames, time_info, status):
    global t_counter, current_mode

    for i in range(frames):
        if current_mode == 1:
            v = bytebeat1(t_counter)

        elif current_mode == 2:
            v = bytebeat2(t_counter)

        elif current_mode == 3:
            v = bytebeat3(t_counter)

        elif current_mode == 4:
            v = bytebeat4(t_counter)

        elif current_mode == 5:
            v = bytebeat5(t_counter)

        else:
            v = bytebeat6(t_counter)

        outdata[i] = [(v - 128) / 128.0]
        t_counter += 1


def start_audio():
    with sd.OutputStream(
        channels=1,
        callback=audio_callback,
        samplerate=sample_rate,
        blocksize=buffer_size,
        dtype="float32"
    ):
        while running:
            time.sleep(0.1)


threading.Thread(
    target=start_audio,
    daemon=True
).start()


# =========================================================
# GDI HELPERS
# =========================================================

def get_hdc():
    hwnd = user32.GetDesktopWindow()
    hdc = user32.GetWindowDC(hwnd)
    return hwnd, hdc


def release_hdc(hwnd, hdc):
    user32.ReleaseDC(hwnd, hdc)


# =========================================================
# EFFECT 1 — INVERT
# =========================================================

def effect1():
    hwnd, hdc = get_hdc()

    gdi32.PatBlt(
        hdc,
        0, 0,
        screen_w,
        screen_h,
        PATINVERT
    )

    release_hdc(hwnd, hdc)


# =========================================================
# EFFECT 2 — SHIFT
# =========================================================

def effect2():
    hwnd, hdc = get_hdc()

    x = random.randint(-30, 30)
    y = random.randint(-30, 30)

    gdi32.BitBlt(
        hdc,
        x, y,
        screen_w,
        screen_h,
        hdc,
        0, 0,
        SRCCOPY
    )

    release_hdc(hwnd, hdc)


# =========================================================
# EFFECT 3 — TUNNEL
# =========================================================

def effect3():
    hwnd, hdc = get_hdc()

    shrink = 20

    gdi32.StretchBlt(
        hdc,
        shrink,
        shrink,
        screen_w - (shrink * 2),
        screen_h - (shrink * 2),
        hdc,
        0,
        0,
        screen_w,
        screen_h,
        SRCCOPY
    )

    release_hdc(hwnd, hdc)


# =========================================================
# EFFECT 4 — SCROLL
# =========================================================

def effect4():
    hwnd, hdc = get_hdc()

    scroll_x = 8

    gdi32.BitBlt(
        hdc,
        scroll_x,
        0,
        screen_w - scroll_x,
        screen_h,
        hdc,
        0,
        0,
        SRCCOPY
    )

    release_hdc(hwnd, hdc)


# =========================================================
# EFFECT 5 — BLUR
# =========================================================

def effect5():
    hwnd, hdc = get_hdc()

    blur = 6

    gdi32.StretchBlt(
        hdc,
        blur,
        blur,
        screen_w - (blur * 2),
        screen_h - (blur * 2),
        hdc,
        0,
        0,
        screen_w,
        screen_h,
        SRCCOPY
    )

    release_hdc(hwnd, hdc)


# =========================================================
# EFFECT 6 — MELT
# =========================================================

def effect6():
    hwnd, hdc = get_hdc()

    x = random.randint(0, screen_w - 50)
    width = random.randint(20, 80)
    drop = random.randint(10, 60)

    gdi32.BitBlt(
        hdc,
        x,
        drop,
        width,
        screen_h - drop,
        hdc,
        x,
        0,
        SRCCOPY
    )

    release_hdc(hwnd, hdc)


# =========================================================
# MODE RUNNER
# =========================================================

def run_mode(mode, effect_func, seconds=40):
    global current_mode, running

    current_mode = mode
    start = time.time()

    while time.time() - start < seconds:
        if user32.GetAsyncKeyState(VK_ESCAPE):
            running = False
            return False

        effect_func()
        time.sleep(0.015)

    return True


# =========================================================
# MAIN LOOP
# =========================================================

try:
    while running:
        if not run_mode(1, effect1):
            break

        if not run_mode(2, effect2):
            break

        if not run_mode(3, effect3):
            break

        if not run_mode(4, effect4):
            break

        if not run_mode(5, effect5):
            break

        if not run_mode(6, effect6):
            break

except KeyboardInterrupt:
    pass

finally:
    running = False
    sd.stop()
    print("Stopped.")