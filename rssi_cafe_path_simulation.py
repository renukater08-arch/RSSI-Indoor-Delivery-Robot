
import math
import random
import matplotlib.pyplot as plt
import csv

# Make results reproducible
random.seed(42)

# Café robot starting position
start_x = -3.7
start_y = -3.1

# Wi-Fi beacon position
beacon_x = 3.7
beacon_y = 3.0

# RSSI model parameters
reference_rssi = -40
reference_distance = 1
path_loss_exponent = 2.2
noise_std = 2

# Store simulation results
path_progress = []
distances = []
model_distances = []
theoretical_rssi = []
measured_rssi = []
robot_positions = []

# Number of positions along the robot path
number_of_steps = 50

# Simulate robot movement towards the beacon
for step in range(number_of_steps + 1):

    # Calculate movement progress (0 to 1)
    progress = step / number_of_steps

    # Calculate robot position
    robot_x = start_x + progress * (beacon_x - start_x)
    robot_y = start_y + progress * (beacon_y - start_y)

    # Calculate actual distance from robot to beacon
    actual_distance = math.sqrt(
        (beacon_x - robot_x) ** 2 +
        (beacon_y - robot_y) ** 2
    )

    # Apply minimum distance for RSSI calculation
    model_distance = max(actual_distance, 1.0)

    # Calculate theoretical RSSI
    rssi = reference_rssi - (
        10 * path_loss_exponent *
        math.log10(model_distance / reference_distance)
    )

    # Add random noise
    noise = random.gauss(0, noise_std)
    noisy_rssi = rssi + noise

    # Store results
    path_progress.append(progress * 100)
    distances.append(actual_distance)
    model_distances.append(model_distance)
    theoretical_rssi.append(rssi)
    measured_rssi.append(noisy_rssi)
    robot_positions.append((robot_x, robot_y))

# Save simulation data to CSV
with open("rssi_cafe_data.csv", "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Progress (%)",
        "Robot X",
        "Robot Y",
        "Distance (m)",
        "Model Distance (m)",
        "Theoretical RSSI (dBm)",
        "Measured RSSI (dBm)"
    ])

    for i in range(len(path_progress)):
        writer.writerow([
            round(path_progress[i], 2),
            round(robot_positions[i][0], 2),
            round(robot_positions[i][1], 2),
            round(distances[i], 2),
            round(model_distances[i], 2),
            round(theoretical_rssi[i], 2),
            round(measured_rssi[i], 2)
        ])

print("CSV dataset saved: rssi_cafe_data.csv")



# Display final results
print("Café RSSI Path Simulation Completed")
print("-----------------------------------")
print("Starting position:", start_x, start_y)
print("Beacon position:", beacon_x, beacon_y)
print("Total path distance:", round(distances[0], 2), "m")
print("Initial RSSI:", round(measured_rssi[0], 2), "dBm")
print("Final RSSI:", round(measured_rssi[-1], 2), "dBm")

# Plot RSSI graph
plt.figure(figsize=(10, 6))

plt.plot(
    path_progress,
    theoretical_rssi,
    label="Theoretical RSSI",
    linewidth=2
)

plt.scatter(
    path_progress,
    measured_rssi,
    label="Measured RSSI (with noise)",
    s=20
)

plt.title("RSSI Variation Along Café Robot Path")
plt.xlabel("Robot Movement Progress (%)")
plt.ylabel("RSSI (dBm)")
plt.grid(True)
plt.legend()

# Save graph
plt.savefig("rssi_cafe_path_graph.png", dpi=300)

plt.show()
