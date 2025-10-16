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
fig.patch.set_facecolor('black')
ax.set_facecolor('black')
cx, cy = 0.0, 0.0 # Center of the plot
r_base = 1.0 # Base radius for the outermost ring

# Draw concentric rings
for i in range(2,10):
    circle = plt.Circle((cx, cy), r_base * i/8, fill=False, lw=0.3, color='gray')
    ax.add_patch(circle)

# Calculate radii so each planet matches its ring
planet_radii = {}
for idx, planet in enumerate(planets, start=2):
    planet_radii[planet.name] = r_base * idx / 8

# Planet symbols
planet_symbols = {
    'Mercury': '☿',
    'Venus': '♀',
    'Earth': '⊕',
    'Mars': '♂',
    'Jupiter': '♃',
    'Saturn': '♄',
    'Uranus': '♅',
    'Neptune': '♆'
}

# Mid-tone astrology-based colors for planets
planet_colors = {
    'Mercury': '#8888aa',   # mid lavender/gray
    'Venus':   '#ff80a0',   # mid pink
    'Earth':   '#3399ff',   # mid blue
    'Mars':    '#ff6666',   # mid red
    'Jupiter': '#ffcc66',   # mid orange/yellow
    'Saturn':  '#ffe066',   # mid yellow
    'Uranus':  '#66ffe0',   # mid cyan
    'Neptune': '#6666cc'    # mid purple/blue
}

# Plot planets at their respective radii
for name, L in longitudes.items():
    L = L % 360.0
    theta_deg = 0 - L
    theta = math.radians(-theta_deg)
    r = planet_radii.get(name, 1.0)
    x = cx + r * math.cos(theta)
    y = cy + r * math.sin(theta)

    ax.plot(x, y, 'o', color=planet_colors.get(name, '#cccccc'), markersize=20)
    ax.text(x, y, planet_symbols[name], va='center', ha='center', fontsize=20)

# Add the Sun in the center
sun_symbol = '☉'
ax.plot(cx, cy, 'o', color='yellow', markersize=28, zorder=10)
ax.text(cx, cy, sun_symbol, va='center', ha='center', fontsize=28, zorder=11)

# Cosmetic
ax.set_aspect('equal', 'box')
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.axis('off')
plt.show()
