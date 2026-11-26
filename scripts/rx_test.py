import sys, time, os
os.environ.setdefault("SOAPY_SDR_LOG_LEVEL", "WARNING")
import numpy as np, SoapySDR
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CS8, SOAPY_SDR_CS16, SOAPY_SDR_OVERFLOW, SOAPY_SDR_TIMEOUT

rate = float(sys.argv[1]); fmt = sys.argv[2]; prot = sys.argv[3]; secs = float(sys.argv[4])
dev = SoapySDR.Device(f"driver=remote,remote=192.168.2.2:55132,remote:driver=hackrf,remote:prot={prot}")
dev.setSampleRate(SOAPY_SDR_RX, 0, rate)
dev.setFrequency(SOAPY_SDR_RX, 0, 100e6)
dev.setGain(SOAPY_SDR_RX, 0, 20)
dev.setBandwidth(SOAPY_SDR_RX, 0, min(rate, 20e6))
f = SOAPY_SDR_CS8 if fmt == "CS8" else SOAPY_SDR_CS16
dtype = np.int8 if fmt == "CS8" else np.int16
st = dev.setupStream(SOAPY_SDR_RX, f, [0], {"remote:format": fmt})
mtu = dev.getStreamMTU(st)
N = 1 << 16
buf = np.empty(2 * N, dtype=dtype)
dev.activateStream(st)
total = ov = to = err = 0
t0 = time.time()
while time.time() - t0 < secs:
    sr = dev.readStream(st, [buf], N, timeoutUs=1_000_000)
    if sr.ret > 0: total += sr.ret
    elif sr.ret == SOAPY_SDR_OVERFLOW: ov += 1
    elif sr.ret == SOAPY_SDR_TIMEOUT: to += 1
    else: err += 1
dt = time.time() - t0
dev.deactivateStream(st); dev.closeStream(st)
print(f"RATE req={rate/1e6:g}Msps fmt={fmt} prot={prot}: got {total/dt/1e6:.3f} Msps avg over {dt:.1f}s "
      f"({total/1e6:.0f} Msamples, expected {rate*dt/1e6:.0f}) | overflow={ov} timeout={to} other_err={err} mtu={mtu}")
