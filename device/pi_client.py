#!/usr/bin/env python3
import os, time, json, hmac, hashlib, requests, math
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

INGEST_URL = os.getenv("VERCEL_INGEST_URL")
DEVICE_ID = os.getenv("DEVICE_ID", "pi-unknown")
SIGNING_SECRET = (os.getenv("SIGNING_SECRET") or "").encode()
SAMPLE_INTERVAL = int(os.getenv("SAMPLE_INTERVAL_SECONDS", "15"))

CHANNEL = int(os.getenv("CHANNEL", "0"))
VREF = float(os.getenv("VREF", "3.3"))
BETA = float(os.getenv("TEMP_BETA", "3950"))
R0 = float(os.getenv("TEMP_R0", "10000"))
T0_C = float(os.getenv("TEMP_T0_C", "25"))
SERIES_R = float(os.getenv("SERIES_RESISTOR", "10000"))

DATA_DIR = Path(__file__).parent
QUEUE_FILE = DATA_DIR / "queue.jsonl"
QUEUE_FILE.touch(exist_ok=True)

# --- SPI (MCP3008) ---
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)            # bus 0, device 0 (CE0)
spi.max_speed_hz = 1350000

def read_adc(ch: int) -> int:
    resp = spi.xfer2([1, (8 + ch) << 4, 0])
    return ((resp[1] & 3) << 8) | resp[2]

def adc_to_voltage(value: int) -> float:
    return (value / 1023.0) * VREF

def read_temperature_c() -> float:
    raw = read_adc(CHANNEL)
    v = adc_to_voltage(raw)
    if v <= 0 or v >= VREF:
        raise RuntimeError("ADC out of range; check wiring")
    r_ntc = SERIES_R * (v / (VREF - v))
    T0_K = T0_C + 273.15
    inv_T = (1.0 / T0_K) + (1.0 / BETA) * (math.log(r_ntc / R0))
    return (1.0 / inv_T) - 273.15

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def sign_payload(timestamp: str, body_bytes: bytes) -> str:
    return hmac.new(SIGNING_SECRET, timestamp.encode() + b"." + body_bytes, hashlib.sha256).hexdigest()

def enqueue(payload: dict):
    with QUEUE_FILE.open("a") as f:
        f.write(json.dumps(payload) + "\n")

def drain_queue(send_func):
    lines = QUEUE_FILE.read_text().splitlines()
    if not lines:
        return
    kept = []
    ok = 0
    for line in lines:
        try:
            data = json.loads(line)
            send_func(data)
            ok += 1
        except Exception:
            kept.append(line)
    QUEUE_FILE.write_text("\n".join(kept) + ("\n" if kept else ""))
    if ok:
        print(f"[queue] Flushed {ok} readings")

def send_reading(value_c: float, ts_iso: str):
    if not INGEST_URL: raise RuntimeError("VERCEL_INGEST_URL not set")
    if not SIGNING_SECRET: raise RuntimeError("SIGNING_SECRET not set")

    body = {"value": round(value_c, 2), "timestamp": ts_iso, "deviceId": DEVICE_ID}
    body_bytes = json.dumps(body).encode()
    sig = sign_payload(ts_iso, body_bytes)
    headers = {
        "Content-Type": "application/json",
        "X-Device-Id": DEVICE_ID,
        "X-Timestamp": ts_iso,
        "X-Signature": sig,
    }
    r = requests.post(INGEST_URL, data=body_bytes, headers=headers, timeout=5)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text}")
    return r.json()

def loop():
    backoff = 1
    while True:
        ts = now_iso()
        try:
            temp_c = read_temperature_c()
            drain_queue(lambda d: send_reading(d["value"], d["timestamp"]))
            send_reading(temp_c, ts)
            print(f"[ok] {ts} {temp_c:.2f} °C")
            backoff = 1
        except Exception as e:
            print(f"[warn] {e}; backoff {backoff}s")
            try:
                # most failures are network; if we have a temp, queue it
                if "temp_c" in locals():
                    enqueue({"value": float(f"{temp_c:.2f}"), "timestamp": ts, "deviceId": DEVICE_ID})
            except Exception:
                pass
            time.sleep(backoff)
            backoff = min(backoff * 2, 300)
        time.sleep(SAMPLE_INTERVAL)

if __name__ == "__main__":
    loop()
