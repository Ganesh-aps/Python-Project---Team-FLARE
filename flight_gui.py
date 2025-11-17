# flight_gui.py
"""
Simple black-screen GUI that continuously displays flight parameters.
Uses tkinter and the algorithms in flight_physics.py.
Run this file to start the GUI: python flight_gui.py
"""

import tkinter as tk
import math
import random
import time
from flight_physics import (
    takeoff_algorithm, landing_algorithm, stall_algorithm,
    inflight_algorithm, turn_algorithm, altitude_hold_algorithm,
    calculate_lift_coefficient, calculate_lift, calculate_drag_coefficient, calculate_drag
)

# GUI update period (milliseconds)
UPDATE_INTERVAL_MS = 1000

# Simulation initial state (you can change these initial numbers)
state = {
    "time_seconds": 0.0,
    "velocity_mps": 70.0,           # m/s (~252 km/h)
    "altitude_m": 500.0,
    "angle_of_attack_deg": 2.0,
    "flap_angle_deg": 0.0,
    "bank_angle_deg": 0.0,
    "thrust_newtons": 10000.0,
    "target_altitude_m": 2000.0
}

# Create main window
root = tk.Tk()
root.title("Flight Computer - Black Screen")
root.configure(bg="black")

# Use a monospace font for neat alignment
FONT = ("Consolas", 14)

# Helper to make a white label on black background
def make_label(master, text="", font=FONT):
    return tk.Label(master, text=text, fg="white", bg="black", font=font, anchor="w")

# Title
title_label = make_label(root, "FLIGHT COMPUTER (AUTO UPDATE)", ("Consolas", 18, "bold"))
title_label.pack(padx=10, pady=(10, 6), anchor="w")

# Container for parameters
frame = tk.Frame(root, bg="black")
frame.pack(padx=10, pady=6, fill="both", expand=True)

# Create many labels for each algorithm and key values
velocity_label = make_label(frame)
altitude_label = make_label(frame)
aoa_label = make_label(frame)
flap_label = make_label(frame)
bank_label = make_label(frame)
thrust_label = make_label(frame)

lift_label = make_label(frame)
drag_label = make_label(frame)

takeoff_label = make_label(frame)
landing_label = make_label(frame)
stall_label = make_label(frame)
inflight_label = make_label(frame)
turn_label = make_label(frame)
altitude_hold_label = make_label(frame)

# Pack labels in order
for lbl in (velocity_label, altitude_label, aoa_label, flap_label, bank_label, thrust_label,
            lift_label, drag_label,
            takeoff_label, landing_label, stall_label, inflight_label, turn_label, altitude_hold_label):
    lbl.pack(anchor="w")

# Update function: simulate state, run algorithms, update labels
def update_display():
    # Simulate small changes so screen looks live
    state["time_seconds"] += UPDATE_INTERVAL_MS / 1000.0
    t = state["time_seconds"]

    # Gentle simulated dynamics (sine + small noise)
    state["velocity_mps"] = max(0.0, 60.0 + 20.0 * math.sin(t / 10.0) + random.uniform(-2, 2))
    state["altitude_m"] = max(0.0, 400.0 + 200.0 * math.sin(t / 18.0) + random.uniform(-5, 5))
    state["angle_of_attack_deg"] = max(-5.0, min(15.0, 2.0 + 3.0 * math.sin(t / 8.0) + random.uniform(-0.5, 0.5)))
    state["flap_angle_deg"] = 10.0 if state["altitude_m"] < 50.0 else 0.0
    state["bank_angle_deg"] = 12.0 * math.sin(t / 7.0)
    state["thrust_newtons"] = 12000.0 + 1500.0 * math.sin(t / 12.0)

    # Physics values
    lift_coeff = calculate_lift_coefficient(state["angle_of_attack_deg"], state["flap_angle_deg"])
    lift_force = calculate_lift(state["velocity_mps"], lift_coeff)
    drag_coeff = calculate_drag_coefficient(lift_coeff)
    drag_force = calculate_drag(state["velocity_mps"], drag_coeff)

    # Run all algorithms (each returns a dict with algorithm name)
    takeoff_result = takeoff_algorithm(state["velocity_mps"], state["altitude_m"],
                                       state["angle_of_attack_deg"], state["flap_angle_deg"])
    landing_result = landing_algorithm(state["velocity_mps"], state["altitude_m"],
                                       state["thrust_newtons"], state["angle_of_attack_deg"], state["flap_angle_deg"])
    stall_result = stall_algorithm(state["velocity_mps"], state["angle_of_attack_deg"],
                                   state["bank_angle_deg"], state["flap_angle_deg"])
    inflight_result = inflight_algorithm(state["velocity_mps"], state["altitude_m"],
                                         state["angle_of_attack_deg"], state["flap_angle_deg"],
                                         state["target_altitude_m"], state["thrust_newtons"])
    turn_result = turn_algorithm(state["velocity_mps"], state["bank_angle_deg"])
    altitude_hold_result = altitude_hold_algorithm(state["altitude_m"], state["target_altitude_m"])

    # Update labels (formatted)
    velocity_label.config(text=f"Velocity: {state['velocity_mps']:.1f} m/s   ({state['velocity_mps']*3.6:.0f} km/h)")
    altitude_label.config(text=f"Altitude: {state['altitude_m']:.1f} m   Target: {state['target_altitude_m']:.1f} m")
    aoa_label.config(text=f"Angle of Attack: {state['angle_of_attack_deg']:.2f} deg")
    flap_label.config(text=f"Flap Angle: {state['flap_angle_deg']:.1f} deg")
    bank_label.config(text=f"Bank Angle: {state['bank_angle_deg']:.1f} deg")
    thrust_label.config(text=f"Thrust: {state['thrust_newtons']:.0f} N")

    lift_label.config(text=f"--- LIFT/DRAG CALCULATIONS ---  Lift: {lift_force:.0f} N   Drag: {drag_force:.0f} N")
    drag_label.config(text=f"Lift Coef: {lift_coeff:.3f}   Drag Coef: {drag_coeff:.4f}")

    takeoff_label.config(text=f"--- TAKEOFF ALGORITHM ---  Status: {takeoff_result['status']}")
    landing_label.config(text=f"--- LANDING ALGORITHM ---  Status: {landing_result['status']}")
    stall_label.config(text=f"--- STALL ALGORITHM ---  Stall: {stall_result['stall']}  Stall speed (m/s): {stall_result['stall_speed_in_turn_mps']:.1f}")
    inflight_label.config(text=f"--- IN-FLIGHT ALGORITHM ---  Mode: {inflight_result['mode']}")
    # turn radius might be inf
    radius_text = "∞" if math.isinf(turn_result['turn_radius_m']) else f"{turn_result['turn_radius_m']:.0f} m"
    turn_label.config(text=f"--- TURN ALGORITHM ---  Radius: {radius_text}  Load: {turn_result['load_factor']:.2f}")
    altitude_hold_label.config(text=f"--- ALTITUDE HOLD ALGORITHM ---  Command: {altitude_hold_result['command']}  Climb rate: {altitude_hold_result['commanded_climb_rate_mps']:.2f} m/s")

    # schedule next update
    root.after(UPDATE_INTERVAL_MS, update_display)


# Start the update loop and GUI mainloop
root.after(100, update_display)
root.mainloop()
