import numpy as np
import matplotlib.pyplot as plt

# the showdown between contra-rotating propellers and coaxial (transvere and quad-copter are being omitted)

# horizontal contra rotating propellers and airframe (better mission and acessory packages with rear-tail mounted propellers) (ekrano)
# vertical coaxial blades and center of mass (ka50)

# Constants
rho = 1.225   # Air density (kg/m^3)

# Vertical (KA-50) Parameters
ka50_lift_drag_ratio = 5           # Hypothetical efficiency
ka50_thrust_weight_ratio = 1.2     # High thrust required for vertical lift
ka50_efficiency = 0.7              # Efficiency in energy conversion
ka50_fuel_consumption_rate = 0.8   # Fuel consumption rate (kg/s)

# Horizontal (Ekranoplan) Parameters
ekrano_lift_drag_ratio = 15        # Higher lift-to-drag ratio due to fixed wing
ekrano_thrust_weight_ratio = 0.5   # Lower thrust since it's not for vertical lift
ekrano_efficiency = 0.9            # More efficient in horizontal flight
ekrano_fuel_consumption_rate = 0.4 # Lower fuel consumption rate (kg/s)

# Mission Profile Parameters
initial_fuel_ka50 = 100           # Initial fuel mass (kg)
initial_fuel_ekrano = 100         # Initial fuel mass (kg)
payload_weight = 50               # Payload weight (kg)
initial_velocity = 0              # Initial velocity (m/s)
time_step = 1                     # Time step for simulation (s)
total_time = 3600                 # Total simulation time (s)

def calculate_thrust(t_w_ratio, weight):
    return t_w_ratio * weight

def calculate_drag(l_d_ratio, lift):
    return lift / l_d_ratio

def simulate(mission_time, time_step, initial_fuel, thrust_weight_ratio, lift_drag_ratio, efficiency, fuel_consumption_rate):
    fuel = initial_fuel
    weight = payload_weight + fuel
    velocity = initial_velocity
    distance_covered = 0
    fuel_history = []
    distance_history = []
    fuel_rate_history = []

    for t in range(0, mission_time, time_step):
        thrust = calculate_thrust(thrust_weight_ratio, weight)
        lift = weight  # Assuming level flight for simplicity
        drag = calculate_drag(lift_drag_ratio, lift)
        net_thrust = thrust - drag

        if net_thrust > 0:
            acceleration = net_thrust / weight
        else:
            acceleration = 0

        velocity += acceleration * time_step
        distance_covered += velocity * time_step

        # Fuel consumption
        fuel_consumed = fuel_consumption_rate * time_step
        fuel -= fuel_consumed
        weight = payload_weight + fuel
        
        fuel_history.append(fuel)
        distance_history.append(distance_covered)
        fuel_rate_history.append(fuel_consumed)
        
        if fuel <= 0:
            break

    return fuel_history, distance_history, fuel_rate_history

# Run simulations
fuel_ka50, distance_ka50, fuel_rate_ka50 = simulate(total_time, time_step, initial_fuel_ka50, ka50_thrust_weight_ratio, ka50_lift_drag_ratio, ka50_efficiency, ka50_fuel_consumption_rate)
fuel_ekrano, distance_ekrano, fuel_rate_ekrano = simulate(total_time, time_step, initial_fuel_ekrano, ekrano_thrust_weight_ratio, ekrano_lift_drag_ratio, ekrano_efficiency, ekrano_fuel_consumption_rate)

# Plot results
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(range(len(fuel_ka50)), fuel_ka50, label="KA-50 Fuel")
plt.plot(range(len(fuel_ekrano)), fuel_ekrano, label="Ekrano Fuel")
plt.xlabel('Time (s)')
plt.ylabel('Fuel (kg)')
plt.legend()
plt.title('Fuel Consumption Over Time')

plt.subplot(1, 2, 2)
plt.plot(range(len(distance_ka50)), distance_ka50, label="KA-50 Distance")
plt.plot(range(len(distance_ekrano)), distance_ekrano, label="Ekrano Distance")
plt.xlabel('Time (s)')
plt.ylabel('Distance (m)')
plt.legend()
plt.title('Distance Covered Over Time')

plt.tight_layout()
plt.show()
