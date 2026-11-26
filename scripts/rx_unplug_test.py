"""ストリーミング中の HackRF 抜き差し試験用。1 秒ごとに受信サンプル数と戻りコードを記録する。
使い方: python scripts/rx_unplug_test.py <rate> <seconds> [host]
"""
import sys, time, os
os.environ.setdefault("SOAPY_SDR_LOG_LEVEL", "WARNING")
import numpy as np, SoapySDR
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CS8

rate = float(sys.argv[1]); secs = float(sys.argv[2]); host = sys.argv[3] if len(sys.argv) > 3 else "192.168.50.2"
t0 = time.time()
def log(m): print(f"[{time.time()-t0:5.1f}s] {m}", flush=True)

dev = SoapySDR.Device(f"driver=remote,remote={host}:55132,remote:driver=hackrf")
dev.setSampleRate(SOAPY_SDR_RX, 0, rate); dev.setFrequency(SOAPY_SDR_RX, 0, 100e6); dev.setGain(SOAPY_SDR_RX, 0, 20)
st = dev.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS8, [0], {"remote:format": "CS8"})
buf = np.empty(2 * (1 << 16), dtype=np.int8)
dev.activateStream(st); log("streaming started")
tick = time.time(); samples = 0; codes = {}
try:
    while time.time() - t0 < secs:
        sr = dev.readStream(st, [buf], 1 << 16, timeoutUs=500_000)
        if sr.ret > 0: samples += sr.ret
        else: codes[sr.ret] = codes.get(sr.ret, 0) + 1
        if time.time() - tick >= 1.0:
            log(f"samples/s={samples/1e6:6.2f}M  non-data codes={codes if codes else '-'}"); tick = time.time(); samples = 0; codes = {}
except Exception as e:
    log(f"EXCEPTION: {type(e).__name__}: {e}")
for name, fn in (("deactivateStream", lambda: dev.deactivateStream(st)), ("closeStream", lambda: dev.closeStream(st))):
    try: fn(); log(f"{name} ok")
    except Exception as e: log(f"{name} FAILED: {type(e).__name__}: {e}")
log("done")
