from astronomy import Time, Body, EclipticLongitude
import math
import matplotlib.pyplot as plt

# List of planets
planets = [Body.Mercury, Body.Venus, Body.Earth, Body.Mars, Body.Jupiter, Body.Saturn, Body.Uranus, Body.Neptune]

# Get current date and time
utc = Time.Now()

# Get longitudes from Astronomy Engine
longitudes = {}
for planet in planets:
    lon = EclipticLongitude(planet, utc)
    longitudes[planet.name] = lon

# Canvas setup
fig, ax = plt.subplots(figsize=(6,6))
cx, cy = 0.0, 0.0
r_base = 1.0

# Draw concentric rings
for i in range(1,9):
    circle = plt.Circle((cx, cy), r_base * i/8, fill=False, lw=0.5, alpha=0.2)
    ax.add_patch(circle)

# Calculate radii so each planet matches its ring
planet_radii = {}
for idx, planet in enumerate(planets, start=1):
    planet_radii[planet.name] = r_base * idx / 8

# Plot planets at their respective radii
for name, L in longitudes.items():
    L = L % 360.0
    theta_deg = 0 - L
    theta = math.radians(-theta_deg)
    r = planet_radii.get(name, 1.0)
    x = cx + r * math.cos(theta)
    y = cy + r * math.sin(theta)

    ax.plot(x, y, 'o')
    ax.text(x, y, ' ' + name, va='center', ha='left', fontsize=8)

# Cosmetic
ax.set_aspect('equal', 'box')
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.axis('off')
plt.show()
