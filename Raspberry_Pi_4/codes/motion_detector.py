#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import statistics

# ——— GPIO pins ———
TRIG_ENTRY, ECHO_ENTRY = 17, 26
TRIG_EXIT,  ECHO_EXIT  = 22, 23

# ——— Parameters ———
THRESHOLD_ENTRY    = 50      # cm
THRESHOLD_EXIT     = 50      # cm
MIN_DISTANCE       = 2       # cm
MAX_DISTANCE       = 300     # cm
SAMPLES            = 7       # pulses per measurement
INTER_SENSOR_DELAY = 0.05    # s between triggering sensors
DEBOUNCE_SEC       = 1.0     # ignore new events for 1s after count
PRINT_INTERVAL     = 5       # status print every 5s

# ——— Setup ———
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_ENTRY, GPIO.OUT)
GPIO.setup(ECHO_ENTRY, GPIO.IN)
GPIO.setup(TRIG_EXIT,  GPIO.OUT)
GPIO.setup(ECHO_EXIT,  GPIO.IN)

def get_distance(trig_pin, echo_pin, samples=SAMPLES):
    readings = []
    for _ in range(samples):
        # send 10µs pulse
        GPIO.output(trig_pin, True)
        time.sleep(1e-5)
        GPIO.output(trig_pin, False)

        # wait for echo start
        start = time.time()
        while GPIO.input(echo_pin) == 0 and (time.time() - start) < 0.02:
            pass
        t0 = time.time()

        # wait for echo end
        while GPIO.input(echo_pin) == 1 and (time.time() - t0) < 0.02:
            pass
        t1 = time.time()

        dt = t1 - t0
        dist = (dt * 34300) / 2
        if MIN_DISTANCE < dist < MAX_DISTANCE:
            readings.append(dist)
        time.sleep(0.01)
    return statistics.median(readings) if readings else MAX_DISTANCE

def main():
    count = 0
    state = 'idle'
    last_event = time.time() - DEBOUNCE_SEC
    next_status = time.time() + PRINT_INTERVAL

    print("🚀 People counter (state machine) started")

    try:
        while True:
            # 1) measure entry sensor
            d_entry = get_distance(TRIG_ENTRY, ECHO_ENTRY)
            time.sleep(INTER_SENSOR_DELAY)
            # 2) measure exit sensor
            d_exit  = get_distance(TRIG_EXIT,  ECHO_EXIT)

            # **Print raw distances each cycle**
            print(f"entry: {d_entry:.1f} cm, exit: {d_exit:.1f} cm")

            now = time.time()

            # State machine
            if state == 'idle':
                if d_entry < THRESHOLD_ENTRY:
                    state = 'entering'
                elif d_exit < THRESHOLD_EXIT:
                    state = 'exiting'

            elif state == 'entering':
                if d_exit < THRESHOLD_EXIT and (now - last_event) > DEBOUNCE_SEC:
                    count += 1
                    print(f"✅ Person ENTERED → Count = {count}")
                    last_event = now
                    state = 'idle'

            elif state == 'exiting':
                if d_entry < THRESHOLD_ENTRY and (now - last_event) > DEBOUNCE_SEC:
                    count = max(0, count - 1)
                    print(f"❌ Person EXITED → Count = {count}")
                    last_event = now
                    state = 'idle'

            # periodic status print
            if now >= next_status:
                print(f"Status: Count = {count}")
                next_status = now + PRINT_INTERVAL

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n🔴 Exiting... cleaning up GPIO.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
