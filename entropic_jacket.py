import numpy as np
from scipy.constants import R
import csv

# System Parameters
combustion_chamber_volume = 1.0  # m^3
initial_temperature = 300.0  # K
initial_pressure = 101325.0  # Pa

# Fuel Composition (moles)
n_methanol = 1.0
n_hydrogen = 2.0

# Air Composition (moles)
n_oxygen = 6.5  # Stoichiometric amount for methanol combustion
n_nitrogen = 3.76 * n_oxygen  # Approximate air composition

# Turbine Efficiency and Power Generation
turbine_efficiency = 0.4  # Typical efficiency
megawatt_conversion = 1000 * 1000  # MW to W conversion

# Stoichiometric Coefficients
methanol_combustion_coefficients = {
    'CH3OH': 1,
    'O2': 1.5,
    'CO2': 1,
    'H2O': 2
}

hydrogen_combustion_coefficients = {
    'H2': 1,
    'O2': 0.5,
    'H2O': 1
}

# Ideal Gas Functions
def calc_temperature(pressure, volume, n_total):
    return pressure * volume / (n_total * R)

def calc_pressure(temperature, volume, n_total):
    return n_total * R * temperature / volume

def calc_n_total(pressure, volume, temperature):
    return pressure * volume / (R * temperature)

def calc_combustion_energy(n_methanol, n_hydrogen):
    # Enthalpy changes (values in J/mol)
    delta_h_methanol = -726000  # For CH3OH combustion
    delta_h_hydrogen = -241800  # For H2 combustion
    
    total_energy_released = (n_methanol * delta_h_methanol) + (n_hydrogen * delta_h_hydrogen)
    return total_energy_released

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def update(self, setpoint, measured_value, dt):
        error = setpoint - measured_value
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        return output

def compression_stroke(volume, temperature, pressure, compression_ratio):
    compressed_volume = volume / compression_ratio
    compressed_temperature = temperature * (compressed_volume / volume) ** (1.4 - 1)
    compressed_pressure = pressure * (compressed_volume / volume) ** (-1.4)
    return compressed_volume, compressed_temperature, compressed_pressure

def combustion_stroke(compressed_temperature, compressed_volume, n_methanol, n_hydrogen, n_oxygen, n_nitrogen):
    total_energy_released = calc_combustion_energy(n_methanol, n_hydrogen)
    specific_heat_capacity = 29.1  # Approximate for O2, N2, CO2, H2O mix, J/(mol*K)
    n_total = n_methanol + n_hydrogen + n_oxygen + n_nitrogen

    delta_t = total_energy_released / (n_total * specific_heat_capacity)
    combustion_temperature = compressed_temperature + delta_t
    combustion_pressure = calc_pressure(combustion_temperature, compressed_volume, n_total)
    return combustion_temperature, combustion_pressure

def energy_generation(combustion_energy_released, turbine_efficiency):
    # Energy output from the turbine (in Joules)
    energy_output = combustion_energy_released * turbine_efficiency
    energy_mw = energy_output / megawatt_conversion  # Convert to MW
    return energy_output, energy_mw

def perform_methanation(n_hydrogen, co2_captured):
    # Simplified methanation reaction: CO2 + 4H2 -> CH4 + 2H2O
    n_methane_produced = min(n_hydrogen / 4, co2_captured)
    return n_methane_produced

def perform_electrolysis(energy_output):
    # Electrolysis efficiency (simplified)
    electrolysis_efficiency = 0.7
    energy_used_for_electrolysis = energy_output * electrolysis_efficiency
    mol_of_h2_produced = energy_used_for_electrolysis / (237.13 * 1000)  # 237.13 kJ/mol for H2
    return mol_of_h2_produced

def main():
    # Example PID usage within the loop
    pid = PIDController(kp=1.0, ki=0.1, kd=0.05)
    setpoint_temperature = 1500  # Example value in Kelvin
    dt = 0.1  # Timestep for PID updates

    # Open a CSV file to log the results
    with open('simulation_results.csv', mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(['Cycle', 'Compression Temperature (K)', 'Compression Pressure (kPa)',
                         'Combustion Temperature (K)', 'Combustion Pressure (kPa)', 'Adjusted Hydrogen Injection',
                         'Energy Output (J)', 'Energy Output (MW)', 'Methane Produced (mol)', 'Hydrogen Produced (mol)'])

        for cycle in range(10):
            compressed_volume, compressed_temperature, compressed_pressure = compression_stroke(
                combustion_chamber_volume, initial_temperature, initial_pressure, compression_ratio=10.0
            )

            measured_temperature = compressed_temperature
            pid_output = pid.update(setpoint_temperature, measured_temperature, dt)

            adjusted_hydrogen_injection = n_hydrogen * (1 + pid_output / 100)  # Simplified adjustment

            combustion_temperature, combustion_pressure = combustion_stroke(
                compressed_temperature, compressed_volume, n_methanol, adjusted_hydrogen_injection, n_oxygen, n_nitrogen
            )

            total_energy_released = calc_combustion_energy(n_methanol, adjusted_hydrogen_injection)
            energy_output, energy_mw = energy_generation(total_energy_released, turbine_efficiency)
            co2_captured = n_methanol  # Simplified: 1 mol CH3OH -> 1 mol CO2
            methane_produced = perform_methanation(adjusted_hydrogen_injection, co2_captured)
            hydrogen_produced = perform_electrolysis(energy_output)

            # Print and log the data
            print(f"Cycle {cycle + 1}:")
            print(f"  Compression - Temperature: {compressed_temperature:.2f} K, Pressure: {compressed_pressure / 1000:.2f} kPa")
            print(f"  Combustion - Temperature: {combustion_temperature:.2f} K, Pressure: {combustion_pressure / 1000:.2f} kPa")
            print(f"  Adjusted Hydrogen Injection: {adjusted_hydrogen_injection:.2f} mol")
            print(f"  Energy Output: {energy_output:.2f} J ({energy_mw:.3f} MW)")
            print(f"  Methane Produced: {methane_produced:.2f} mol, Hydrogen Produced: {hydrogen_produced:.2f} mol\n")

            writer.writerow([cycle + 1, compressed_temperature, compressed_pressure / 1000,
                            combustion_temperature, combustion_pressure / 1000, adjusted_hydrogen_injection,
                            energy_output, energy_mw, methane_produced, hydrogen_produced])

if __name__ == "__main__":
    main()