
import math
import random

# Beacon position
beacon_x = 3.7
beacon_y = 3.0

# RSSI model parameters
reference_rssi = -40
reference_distance = 1
path_loss_exponent = 2.2

# Robot starting position in cafe
robot_x = -3.7
robot_y = -3.1

# Calculate distance
distance = math.sqrt(
    (robot_x - beacon_x) ** 2 +
    (robot_y - beacon_y) ** 2
)

# Avoid log(0)
distance = max(distance, 0.1)

# Calculate ideal RSSI
rssi = reference_rssi - (
    10 * path_loss_exponent *
    math.log10(distance / reference_distance)
)

# Add random signal noise
noise = random.gauss(0, 2)
measured_rssi = rssi + noise

print("Robot position:", robot_x, robot_y)
print("Distance from beacon:", round(distance, 2), "m")
print("Simulated RSSI:", round(measured_rssi, 2), "dBm")
