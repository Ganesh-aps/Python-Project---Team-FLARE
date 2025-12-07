# flight_gui.py
import tkinter as tk
from tkinter import ttk
import random
import math
import time

from flight_physics import (
    takeoff_algorithm,
    landing_algorithm,
    stall_algorithm,
    inflight_algorithm,
    turn_algorithm,
    altitude_hold_algorithm,
    calculate_lift_coefficient,
    calculate_lift,
    calculate_drag_coefficient,
    calculate_drag,
)

# ---------------- GUI COLORS ----------------
BG = "#0f0f0f"
CARD = "#1a1a1a"
FG = "#e5e5e5"
ACCENT = "#3ba55d"
WARNING = "#d9534f"

# ---------------- INITIAL STATE ----------------
state = {
    "velocity_mps": 70.0,
    "altitude_m": 500.0,
    "angle_of_attack_deg": 2.0,
    "flap_angle_deg": 0.0,
    "bank_angle_deg": 0.0,
    "thrust_newtons": 10000.0,
    "target_altitude_m": 2000.0,
    "time_seconds": 0.0,
}

UPDATE_INTERVAL_MS = 1000
running = False

# ---------------- GUI SETUP ----------------
root = tk.Tk()
root.title("Flight Computer")
root.geometry("800x650")
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")
style.configure("Card.TLabelframe", background=CARD, foreground=FG, borderwidth=0)
style.configure("Card.TLabelframe.Label", background=CARD, foreground=FG, font=("Segoe UI", 11, "bold"))

# ---------------- TITLE ----------------
title = tk.Label(root, text="FLIGHT COMPUTER", font=("Segoe UI", 22, "bold"), bg=BG, fg=FG)
title.pack(pady=10)

# ---------------- WARNING PANEL ----------------
warning_frame = ttk.LabelFrame(root, text="Warnings", style="Card.TLabelframe")
warning_frame.pack(pady=8)

warning_display = tk.Label(
    warning_frame, text="No Active Warnings", bg=CARD, fg=WARNING,
    font=("Segoe UI", 11), width=55, height=2
)
warning_display.pack(padx=10, pady=10)

# ---------------- STATUS BOX ----------------
status_frame = ttk.LabelFrame(root, text="Flight Status (All 6 Algorithms)", style="Card.TLabelframe")
status_frame.pack(pady=10)

status_display = tk.Text(
    status_frame, width=70, height=12, bg="#0a0a0a",
    fg="#7fffb2", font=("Consolas", 12), relief="flat"
)
status_display.pack(padx=8, pady=8)

# ---------------- METERS ----------------
meter_frame = tk.Frame(root, bg=BG)
meter_frame.pack(pady=5)

speed_label = tk.Label(meter_frame, text="Speed: 0", bg=BG, fg=FG, font=("Segoe UI", 11))
alt_label = tk.Label(meter_frame, text="Altitude: 0", bg=BG, fg=FG, font=("Segoe UI", 11))
thrust_label = tk.Label(meter_frame, text="Thrust: 0", bg=BG, fg=FG, font=("Segoe UI", 11))

speed_label.grid(row=0, column=0, padx=25)
alt_label.grid(row=0, column=1, padx=25)
thrust_label.grid(row=0, column=2, padx=25)

# ---------------- BOTTOM CONTROLS ----------------
BOTTOM_SPACER = tk.Frame(root, height=40, bg=BG)
BOTTOM_SPACER.pack()

bottom_bar = tk.Frame(root, bg=BG)
bottom_bar.pack(pady=5)

btn_area = tk.Frame(bottom_bar, bg=BG)
btn_area.grid(row=0, column=1, padx=20)

def start_computing():
    global running
    running = True
    update_data()

def stop_computing():
    global running
    running = False

start_btn = ttk.Button(btn_area, text="START", command=start_computing)
stop_btn = ttk.Button(btn_area, text="STOP", command=stop_computing)
start_btn.pack(pady=5, ipadx=10)
stop_btn.pack(pady=5, ipadx=10)

# ---------------- THE LIVE UPDATE LOOP ----------------
def update_data():
    global running, state
    if not running:
        return

    # Time step
    state["time_seconds"] += 1
    t = state["time_seconds"]

    # Randomized dynamics for realism
    state["velocity_mps"] = max(0, 60 + 20 * math.sin(t / 10) + random.uniform(-4, 4))
    state["altitude_m"] = max(0, 400 + 200 * math.sin(t / 18) + random.uniform(-8, 8))
    state["angle_of_attack_deg"] = max(-5, min(15, 2 + 3 * math.sin(t / 8) + random.uniform(-1, 1)))
    state["flap_angle_deg"] = 10 if state["altitude_m"] < 50 else 0
    state["bank_angle_deg"] = 15 * math.sin(t / 6)
    state["thrust_newtons"] = 12000 + 1500 * math.sin(t / 12)

    v = state["velocity_mps"]
    alt = state["altitude_m"]
    aoa = state["angle_of_attack_deg"]
    flaps = state["flap_angle_deg"]
    bank = state["bank_angle_deg"]
    thrust = state["thrust_newtons"]
    target_alt = state["target_altitude_m"]

    # Physics
    lc = calculate_lift_coefficient(aoa, flaps)
    lift = calculate_lift(v, lc)
    dc = calculate_drag_coefficient(lc)
    drag = calculate_drag(v, dc)

    # Algorithms
    r_take = takeoff_algorithm(v, alt, aoa, flaps)
    r_land = landing_algorithm(v, alt, thrust, aoa, flaps)
    r_stall = stall_algorithm(v, aoa, bank, flaps)
    r_flight = inflight_algorithm(v, alt, aoa, flaps, target_alt, thrust)
    r_turn = turn_algorithm(v, bank)
    r_alt = altitude_hold_algorithm(alt, target_alt)

    # Update meters
    speed_label.config(text=f"Speed: {v:.1f} m/s")
    alt_label.config(text=f"Altitude: {alt:.1f} m")
    thrust_label.config(text=f"Thrust: {thrust:.0f} N")

    # Update warnings
    if r_stall["stall"]:
        warning_display.config(text="STALL WARNING!", fg="red")
    elif thrust < 2000:
        warning_display.config(text="LOW THRUST", fg="yellow")
    else:
        warning_display.config(text="No Active Warnings", fg=ACCENT)

    # Update big status box
    status_display.delete("1.0", tk.END)
    status_display.insert(tk.END,
f"""
Velocity: {v:.1f} m/s
Altitude: {alt:.1f} m
AoA: {aoa:.2f}°
Bank: {bank:.1f}°
Flaps: {flaps}°
Thrust: {thrust:.0f} N

Lift: {lift:.0f} N    Drag: {drag:.0f} N
Lift Coef: {lc:.3f}   Drag Coef: {dc:.4f}

TAKEOFF → {r_take['status']}
LANDING → {r_land['status']}
STALL → {r_stall['stall']}
IN-FLIGHT → {r_flight['mode']}
TURN → Radius: {r_turn['turn_radius_m']:.1f} m   Load: {r_turn['load_factor']:.2f}
ALT HOLD → {r_alt['command']}   Climb Rate: {r_alt['commanded_climb_rate_mps']:.2f} m/s
"""
    )

    # Schedule next update
    root.after(UPDATE_INTERVAL_MS, update_data)

root.mainloop()


