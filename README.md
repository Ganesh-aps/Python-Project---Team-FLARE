🛩️ Python-Based Flight Computer for Small-Scale Aircraft & Drones

A lightweight, educational flight-computer system built using Python, aerodynamic equations, and modular algorithms.
Designed for non-life-critical small aircraft, RC planes, drones, UAV R&D, and academic learning.

Contribution :
• Ganesh Singh (Team Lead): Deciding the project and algorithm structure, main takeoff Algorithm and predefined functions, major part of GUI.
• Rishabh Loura – Landing and Stall Algorithm
• Harshvardhan Singh – In flight and Altitude Hold Algorithm
• Shresth Rai – Predefined Constants, Research , Turn Algorithm, GUI Layout .

🔍 Project Overview

This project simulates the core intelligence of a flight computer:

Lift calculation

Drag calculation

Stall detection

Takeoff readiness

Landing logic

Turning physics

Altitude hold

In-flight climb/descend/cruise modes

The system is simple, scalable, and directly inspired by models used in NASA tools like GMAT and PyFME (Python Flight Mechanics Engine).

🚀 Features
✔ Real Aerodynamic Equations

Uses physics formulas for:

Lift coefficient

Lift force

Drag coefficient

Drag force

Stall speed

Turn radius

Load factor

✔ Six Core Flight Algorithms

Takeoff Algorithm

Landing Algorithm

Stall Detection Algorithm

In-Flight Mode Algorithm

Turn Algorithm

Altitude Hold Algorithm

✔ Modular Python Structure

Clean separation of:

flight_physics.py → physics + algorithms

gui.py / interface → simple GUI or terminal control

ready for further integration

✔ Plug-and-Play for Any Small Aircraft

By changing aircraft mass, wing area, thrust, and aerodynamics constants,
this flight computer can be instantly adapted for:

RC Planes

Delivery Drones

VTOL Prototypes

Fixed-Wing Mini UAVs

Academic Simulation Projects

(This is the line you asked earlier →)
“By adjusting parameters like weight, wing area, and wing loading inside the physics file, the same flight-computer logic can be instantly customized to work with any small-scale aircraft design.”

🧠 How It Works
1. Input Parameters

Velocity, altitude, angle of attack, flap angle, bank angle, thrust, etc.

2. Physics Layer (flight_physics.py)

Computes lift, drag, stall speed, turn radius, load factor.

3. Algorithm Layer

Determines:

Are we stalling?

Should we climb or descend?

Is takeoff possible?

Are we in final landing phase?

4. Output

Returns structured data (JSON/dict)
ready to be displayed on the GUI.

🖥️ GUI Module

A simple black-screen style GUI displays:

Current lift

Drag

Flight mode

Stall warnings

Takeoff/Landing status

Altitude hold commands# Python-Project---Team-FLARE
