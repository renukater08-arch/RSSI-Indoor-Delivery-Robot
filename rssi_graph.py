
import math
import random
import matplotlib.pyplot as plt

# RSSI model parameters
reference_rssi = -40
reference_distance = 1
path_loss_exponent = 2.2

# Store values
distances = []
theoretical_rssi = []
measured_rssi = []

# Generate RSSI readings
for d in range(1, 21):

    # Calculate theoretical RSSI
    rssi = reference_rssi - (
        10 * path_loss_exponent *
        math.log10(d / reference_distance)
    )

    # Add random noise (standard deviation = 2 dB)
    noise = random.gauss(0, 2)
    noisy_rssi = rssi + noise

    # Store values
    distances.append(d)
    theoretical_rssi.append(rssi)
    measured_rssi.append(noisy_rssi)

# Plot both curves
plt.figure(figsize=(10, 6))

plt.plot(
    distances,
    theoretical_rssi,
    marker='o',
    label='Theoretical RSSI'
)

plt.scatter(
    distances,
    measured_rssi,
    color='red',
    label='Measured RSSI (with noise)'
)

plt.title("Theoretical vs Noisy RSSI")
plt.xlabel("Distance from Beacon (metres)")
plt.ylabel("RSSI (dBm)")

plt.grid(True)
plt.legend()

plt.show()
