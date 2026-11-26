"""バイアスT 短時間試験。A: オフ12秒 → B: オン10秒 → C: オフ8秒。1秒ごとに平均受信電力(dBFS)を表示。
終了・例外・Ctrl+C のいずれでも必ずバイアスTをオフに戻す。
使い方: python scripts/rx_bias_test.py [--dry] [host]   (--dry はバイアスTをオンにしない動作確認)
"""
import sys, time, os, signal
os.environ.setdefault("SOAPY_SDR_LOG_LEVEL", "WARNING")
import numpy as np, SoapySDR
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CS8

args = [a for a in sys.argv[1:] if not a.startswith("--")]
DRY = "--dry" in sys.argv; host = args[0] if args else "192.168.50.2"
FREQ, RATE = 1090e6, 2e6
dev = SoapySDR.Device(f"driver=remote,remote={host}:55132,remote:driver=hackrf")
KEY = "bias_tx"
print("settings:", [s.key for s in dev.getSettingInfo()], "| bias_tx =", dev.readSetting(KEY), flush=True)

def bias(on):
    dev.writeSetting(KEY, "true" if on else "false")
def safe_off(*_):
    try: bias(False)
    except Exception as e: print("WARN: bias off failed:", e, flush=True)
    print("bias_tx =", dev.readSetting(KEY), "(終了時)", flush=True)
signal.signal(signal.SIGINT, lambda *a: (_ for _ in ()).throw(KeyboardInterrupt()))

dev.setSampleRate(SOAPY_SDR_RX, 0, RATE); dev.setFrequency(SOAPY_SDR_RX, 0, FREQ)
dev.setGain(SOAPY_SDR_RX, 0, "LNA", 16); dev.setGain(SOAPY_SDR_RX, 0, "VGA", 20); dev.setGain(SOAPY_SDR_RX, 0, "AMP", 0)
st = dev.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS8, [0], {"remote:format": "CS8"})
buf = np.empty(2 * 65536, dtype=np.int8)
phases = [("A bias OFF (ベースライン)", 12, False), ("B bias ON", 10, True), ("C bias OFF", 8, False)]
t0 = time.time()
try:
    bias(False); dev.activateStream(st)
    for name, secs, on in phases:
        if on and DRY: name += " ※DRY: 実際はオフのまま"
        elif on: bias(True)
        print(f"== {name}  (bias_tx={dev.readSetting(KEY)})", flush=True)
        start = time.time(); tick = start; pw = []
        while time.time() - start < secs:
            sr = dev.readStream(st, [buf], 65536, timeoutUs=500_000)
            if sr.ret > 0:
                x = buf[:2*sr.ret].astype(np.float32); pw.append(float(np.mean(x*x)))
            if time.time() - tick >= 1.0 and pw:
                print(f"  [{time.time()-t0:5.1f}s] avg power = {10*np.log10(np.mean(pw)/(128.0**2)+1e-12):6.1f} dBFS", flush=True)
                pw = []; tick = time.time()
        if on and not DRY: bias(False)
finally:
    safe_off()
    try: dev.deactivateStream(st); dev.closeStream(st)
    except Exception as e: print("close:", e)
