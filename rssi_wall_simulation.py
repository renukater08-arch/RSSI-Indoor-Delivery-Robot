
import math
import matplotlib.pyplot as plt

# Beacon position
beacon_x = 10
beacon_y = 5

# Wall position
wall_x = 6
wall_y_min = 0
wall_y_max = 8

# RSSI parameters
reference_rssi = -40
path_loss_exponent = 2.2
wall_loss = 8  # Illustrative additional loss in dB

# Store results
distances = []
rssi_without_wall = []
rssi_with_wall = []

# Move robot along the horizontal path
for robot_x in range(1, 16):

    robot_y = 5

    # Calculate distance
    distance = math.sqrt(
        (beacon_x - robot_x) ** 2 +
        (beacon_y - robot_y) ** 2
    )

    distance = max(distance, 0.1)

    # Calculate normal RSSI
    rssi = reference_rssi - (
        10 * path_loss_exponent *
        math.log10(distance)
    )

    # Check whether the wall blocks the direct path
    wall_blocks = (
        robot_x < wall_x < beacon_x
        and wall_y_min <= robot_y <= wall_y_max
    )

    # Apply additional wall loss
    if wall_blocks:
        blocked_rssi = rssi - wall_loss
    else:
        blocked_rssi = rssi

    distances.append(distance)
    rssi_without_wall.append(rssi)
    rssi_with_wall.append(blocked_rssi)

# Plot results
plt.figure(figsize=(10, 6))

plt.plot(
    distances,
    rssi_without_wall,
    marker='o',
    label='Without Wall'
)

plt.plot(
    distances,
    rssi_with_wall,
    marker='s',
    label='With Wall'
)

plt.title("Effect of Wall Attenuation on Wi-Fi RSSI")
plt.xlabel("Distance from Beacon (metres)")
plt.ylabel("RSSI (dBm)")

plt.grid(True)
plt.legend()
plt.show()
