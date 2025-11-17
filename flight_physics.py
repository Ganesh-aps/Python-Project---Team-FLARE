# flight_physics.py
"""
Physics and algorithm module for the Flight Computer.
Contains clear functions for lift, drag, stall, takeoff, landing, turns, altitude-hold.
"""

import math

# ----- constants -----
AIR_DENSITY = 1.225        # kg/m^3
GRAVITY = 9.81             # m/s^2

# Example aircraft parameters (tweakable)
WING_AREA = 30.0           # m^2
AIRCRAFT_MASS = 5000.0     # kg
LIFT_COEFFICIENT_ZERO = 0.25
LIFT_COEFFICIENT_ALPHA = 0.10   # per degree
LIFT_COEFFICIENT_MAX = 1.6
DRAG_COEFFICIENT_ZERO = 0.02
INDUCED_DRAG_FACTOR = 0.045
MAX_THRUST = 20000.0       # N


# ----- helper physics functions -----

def calculate_lift_coefficient(angle_of_attack_deg: float, flap_angle_deg: float) -> float:
    """Return approximate lift coefficient (linear + flap effect)."""
    return (LIFT_COEFFICIENT_ZERO
            + LIFT_COEFFICIENT_ALPHA * angle_of_attack_deg
            + 0.01 * flap_angle_deg)


def calculate_lift(velocity_mps: float, lift_coefficient: float) -> float:
    """Return lift force in newtons."""
    return 0.5 * AIR_DENSITY * velocity_mps ** 2 * WING_AREA * lift_coefficient


def calculate_drag_coefficient(lift_coefficient: float) -> float:
    """Return drag coefficient (parasitic + induced)."""
    return DRAG_COEFFICIENT_ZERO + INDUCED_DRAG_FACTOR * lift_coefficient ** 2


def calculate_drag(velocity_mps: float, drag_coefficient: float) -> float:
    """Return drag force in newtons."""
    return 0.5 * AIR_DENSITY * velocity_mps ** 2 * WING_AREA * drag_coefficient


def calculate_weight() -> float:
    """Return aircraft weight in newtons."""
    return AIRCRAFT_MASS * GRAVITY


def calculate_stall_speed_for_clean_configuration() -> float:
    """Return theoretical stall speed (m/s) for clean (no-flap) config using CL_max."""
    weight = calculate_weight()
    return math.sqrt(2.0 * weight / (AIR_DENSITY * WING_AREA * LIFT_COEFFICIENT_MAX))


def calculate_turn_radius(velocity_mps: float, bank_angle_deg: float) -> float:
    """Return turn radius in meters. If bank is zero, return math.inf."""
    if abs(bank_angle_deg) < 1e-6:
        return math.inf
    bank_radians = math.radians(bank_angle_deg)
    return velocity_mps ** 2 / (GRAVITY * math.tan(bank_radians))


def calculate_load_factor(bank_angle_deg: float) -> float:
    """Return load factor n = 1 / cos(phi)."""
    bank_radians = math.radians(bank_angle_deg)
    return 1.0 / math.cos(bank_radians)


# ----- algorithm functions (each clearly named) -----

def takeoff_algorithm(velocity_mps: float, altitude_m: float,
                      angle_of_attack_deg: float, flap_angle_deg: float) -> dict:
    """
    TAKEOFF ALGORITHM:
    - Uses lift >= weight to decide takeoff readiness.
    Returns dict containing status, lift, weight, lift_coefficient.
    """
    lift_coefficient = calculate_lift_coefficient(angle_of_attack_deg, flap_angle_deg)
    lift_force = calculate_lift(velocity_mps, lift_coefficient)
    weight_newtons = calculate_weight()

    if altitude_m > 0.1 and lift_force >= weight_newtons:
        status = "AIRBORNE"
    elif lift_force >= weight_newtons and altitude_m <= 0.1:
        status = "TAKEOFF READY (ROTATE)"
    else:
        status = "ROLLING"

    return {
        "algorithm": "TAKEOFF ALGORITHM",
        "status": status,
        "lift_newtons": lift_force,
        "weight_newtons": weight_newtons,
        "lift_coefficient": lift_coefficient
    }


def landing_algorithm(velocity_mps: float, altitude_m: float,
                      thrust_newtons: float, angle_of_attack_deg: float, flap_angle_deg: float) -> dict:
    """
    LANDING ALGORITHM:
    - Uses altitude, speed and drag vs thrust to decide landing phases.
    """
    lift_coefficient = calculate_lift_coefficient(angle_of_attack_deg, flap_angle_deg)
    drag_coefficient = calculate_drag_coefficient(lift_coefficient)
    drag_force = calculate_drag(velocity_mps, drag_coefficient)

    approach_condition = (altitude_m < 200.0 and velocity_mps < 55.0)
    final_condition = (altitude_m <= 10.0 and velocity_mps <= 16.7)
    touchdown_condition = final_condition and (drag_force >= thrust_newtons)

    if touchdown_condition:
        status = "TOUCHDOWN"
    elif final_condition:
        status = "FINAL"
    elif approach_condition:
        status = "APPROACH"
    else:
        status = "NOT LANDING"

    return {
        "algorithm": "LANDING ALGORITHM",
        "status": status,
        "drag_newtons": drag_force,
        "thrust_newtons": thrust_newtons
    }


def stall_algorithm(velocity_mps: float, angle_of_attack_deg: float, bank_angle_deg: float,
                    flap_angle_deg: float) -> dict:
    """
    STALL ALGORITHM:
    - Stall if angle_of_attack exceeds ~15 deg or velocity below turn-adjusted stall.
    """
    base_stall_speed = calculate_stall_speed_for_clean_configuration()
    # flaps increase CL_max slightly (approx), reduce stall speed a bit
    flap_cl_adjustment = 0.01 * flap_angle_deg
    effective_cl_max = LIFT_COEFFICIENT_MAX + flap_cl_adjustment
    weight_newtons = calculate_weight()
    stall_speed_with_flaps = math.sqrt(2.0 * weight_newtons / (AIR_DENSITY * WING_AREA * effective_cl_max))

    # load factor in a bank increases stall speed
    load_factor = calculate_load_factor(bank_angle_deg)
    stall_speed_in_turn = stall_speed_with_flaps * math.sqrt(load_factor)

    stall_by_aoa = angle_of_attack_deg >= 15.0
    stall_by_speed = velocity_mps <= stall_speed_in_turn

    stall_flag = stall_by_aoa or stall_by_speed

    return {
        "algorithm": "STALL ALGORITHM",
        "stall": stall_flag,
        "stall_speed_clean_mps": base_stall_speed,
        "stall_speed_with_flaps_mps": stall_speed_with_flaps,
        "stall_speed_in_turn_mps": stall_speed_in_turn,
        "angle_of_attack_deg": angle_of_attack_deg
    }


def inflight_algorithm(velocity_mps: float, altitude_m: float,
                       angle_of_attack_deg: float, flap_angle_deg: float,
                       target_altitude_m: float, thrust_newtons: float) -> dict:
    """
    IN-FLIGHT ALGORITHM:
    - Compares lift and weight and altitude error to pick CLIMB / DESCEND / CRUISE.
    """
    lift_coefficient = calculate_lift_coefficient(angle_of_attack_deg, flap_angle_deg)
    lift_force = calculate_lift(velocity_mps, lift_coefficient)
    weight_newtons = calculate_weight()

    if lift_force < weight_newtons and altitude_m < target_altitude_m - 5.0:
        mode = "CLIMB"
    elif lift_force > weight_newtons and altitude_m > target_altitude_m + 5.0:
        mode = "DESCEND"
    else:
        mode = "CRUISE"

    return {
        "algorithm": "IN-FLIGHT ALGORITHM",
        "mode": mode,
        "lift_newtons": lift_force,
        "weight_newtons": weight_newtons
    }


def turn_algorithm(velocity_mps: float, bank_angle_deg: float) -> dict:
    """
    TURN ALGORITHM:
    - Computes turn radius and load factor.
    """
    radius = calculate_turn_radius(velocity_mps, bank_angle_deg)
    load_factor = calculate_load_factor(bank_angle_deg) if abs(bank_angle_deg) > 1e-6 else 1.0

    return {
        "algorithm": "TURN ALGORITHM",
        "turn_radius_m": radius,
        "load_factor": load_factor
    }


def altitude_hold_algorithm(altitude_m: float, target_altitude_m: float, proportional_gain: float = 0.4) -> dict:
    """
    ALTITUDE HOLD ALGORITHM:
    - Very simple proportional controller returning a climb/descend command.
    """
    error_m = target_altitude_m - altitude_m
    commanded_climb_rate_mps = max(-10.0, min(10.0, proportional_gain * error_m))

    if abs(error_m) <= 2.0:
        command = "HOLD"
    elif commanded_climb_rate_mps > 0:
        command = "CLIMB"
    else:
        command = "DESCEND"

    return {
        "algorithm": "ALTITUDE HOLD ALGORITHM",
        "command": command,
        "commanded_climb_rate_mps": commanded_climb_rate_mps,
        "altitude_error_m": error_m
    }
