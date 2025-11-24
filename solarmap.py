from astronomy import Time, Body, EclipticLongitude, GeoVector
import math
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import io
import cairosvg
import numpy as np


#Feature additions
#TODO: Asteroid & Kuiper belt rotation
#TODO: Dwarf planets? (Pluto, Ceres, Haumea, Makemake, Eris)
#TODO: Moons? (Galilean moons, Titan, Mars moons)
#TODO: Comets? (Halley, Hale-Bopp)

#Visual customizations
#TODO: Planet labels working with different DPIs
#TODO: Optional background stars
#TODO: Optional colors to rings
#TODO: Optional colors to background
#TODO: Optional rings fading with distance/time
#TODO: Custom time input




# Planet names toggle
show_planet_names = True  # Set to False to hide names

# Planet name offsets (single value, y will be negative of x)
planet_name_offsets = {'Mercury': 0.02, 'Venus': 0.03, 'Earth': 0.03, 'Mars': 0.025, 'Jupiter': 0.08, 'Saturn': 0.06, 'Uranus': 0.04, 'Neptune': 0.04}

# Color toggle
use_colors = True # Set to False for black & white

# Planet colors (approximate realistic colors)
planet_colors = {
    'Mercury': '#815313',
    'Venus': '#3CB371',
    'Earth': '#4A90E2',
    'Mars': '#CD5C5C',
    'Jupiter': '#C88B3A',
    'Saturn': '#FAD5A5',
    'Uranus': '#4FD0E0',
    'Neptune': '#4166F5'
}


# Planet list
planets = [Body.Mercury, Body.Venus, Body.Earth, Body.Mars,
    Body.Jupiter, Body.Saturn, Body.Uranus, Body.Neptune]




# Convert planet SVG icons to OffsetImages
def svg_to_imagebox(svg_path, zoom=0.1, color=None):
    """Convert an SVG to a Matplotlib OffsetImage (PNG in memory)."""
    png_bytes = cairosvg.svg2png(url=svg_path)
    image = mpimg.imread(io.BytesIO(png_bytes), format='png')

    # Colorize if color is provided
    if color is not None:
        from matplotlib.colors import hex2color
        rgb = hex2color(color)
        # Apply color to white pixels (assuming SVGs are white)
        mask = image[:, :, :3].mean(axis=2) > 0.5  # Find white-ish pixels
        for i in range(3):
            image[:, :, i] = np.where(mask, rgb[i], image[:, :, i])

    return OffsetImage(image, zoom=zoom)




# Get current time and calculate ecliptic longitudes (angles from the Sun)
utc = Time.Now().AddDays(0) # AddDays for testing
longitudes = {planet.name: EclipticLongitude(planet, utc) for planet in planets}




# Canvas setup
#   Set wallpaper resolution
width_px = 2560
height_px = 1440
dpi = 200 # Set planet size by changing dpi

fig, ax = plt.subplots(figsize=(1, 1))
fig.set_size_inches(width_px/dpi, height_px/dpi)
fig.patch.set_facecolor('black')
ax.set_facecolor('black')
cx, cy = 0.0, 0.0
r_base = 1.0




# Background stars
#   Calculate aspect-aware limits for stars
fig_width, fig_height = fig.get_size_inches()
aspect = fig_width / fig_height
if aspect > 1:  # Wider than tall
    star_xlim = (-1.3 * aspect, 1.3 * aspect)
    star_ylim = (-1.3, 1.3)
else:  # Taller than wide
    star_xlim = (-1.3, 1.3)
    star_ylim = (-1.3 / aspect, 1.3 / aspect)

#   Generate stars
import numpy as np
np.random.seed(12345)

#   Base stars
num_stars = 200
star_x = np.random.uniform(star_xlim[0], star_xlim[1], num_stars)
star_y = np.random.uniform(star_ylim[0], star_ylim[1], num_stars)
star_sizes = np.random.uniform(0.1, 1.5, num_stars)
ax.scatter(star_x, star_y, s=star_sizes, c='white', alpha=0.3, marker='.')

#   Dense band
band_stars = 1000
band_x = np.random.uniform(star_xlim[0], star_xlim[1], band_stars)
band_y = np.random.normal(0, 0.3, band_stars)
band_sizes = np.random.uniform(0.05, 0.8, band_stars)
ax.scatter(band_x, band_y, s=band_sizes, c='white', alpha=0.2, marker='.')




# Rings
rings = []
step = r_base / 8
current = step * 2  # Double gap
rings.append(current) # Ring 1
for _ in range(1, 4): # Rings 2 to 4
    current += step
    rings.append(current)
current += step * 2 # Double gap
rings.append(current) # Ring 5
for _ in range(5, 8): # Rings 6 to 8
    current += step
    rings.append(current)
for r in rings: # Draw rings, dashed lines
    ax.add_patch(plt.Circle((cx, cy), r, fill=False, lw=0.4, color='white', linestyle=(0, (10, 10))))

#   Radii for each planet
planet_radii = {p.name: rings[i] for i, p in enumerate(planets)}




# Plot objects
#   Sun
sun_imagebox = svg_to_imagebox("icons/sun.svg", zoom=0.3)
sun_ab = AnnotationBbox(sun_imagebox, (cx, cy), frameon=False)
ax.add_artist(sun_ab)

#   Planets
for name, L in longitudes.items():
    L = L % 360.0
    theta_deg = 0 - L
    theta = math.radians(-theta_deg)
    r = planet_radii.get(name, 1.0)
    x = cx + r * math.cos(theta)
    y = cy + r * math.sin(theta)

#   (Store Earth's position for Moon plotting)
    if name == "Earth":
        earth_x, earth_y = x, y

#   Plot planet icons
    svg_path = f"icons/{name.lower()}.svg"
    color = planet_colors.get(name) if use_colors else None
    imagebox = svg_to_imagebox(svg_path, zoom=0.2, color=color)
    ab = AnnotationBbox(imagebox, (x, y), frameon=False)
    ax.add_artist(ab)

    # Add planet name
    if show_planet_names:
        offset = planet_name_offsets.get(name, 0.05)
        ax.text(x + offset, y - offset, name.lower(), 
                color='white', fontsize=8, 
                ha='left', va='top',
                alpha=0.7)


# Asteroids
#   Asteroid belt between Mars and Jupiter
mars_r = planet_radii['Mars']
jupiter_r = planet_radii['Jupiter']
asteroid_belt_inner = mars_r + (jupiter_r - mars_r) * 0.2
asteroid_belt_outer = mars_r + (jupiter_r - mars_r) * 0.8

#   Generate asteroids
np.random.seed(123)
num_asteroids = 2000
asteroid_angles = np.random.uniform(0, 2 * np.pi, num_asteroids)
asteroid_radii = np.random.uniform(asteroid_belt_inner, asteroid_belt_outer, num_asteroids)
asteroid_x = cx + asteroid_radii * np.cos(asteroid_angles)
asteroid_y = cy + asteroid_radii * np.sin(asteroid_angles)
asteroid_sizes = np.random.uniform(0.05, 0.3, num_asteroids)

ax.scatter(asteroid_x, asteroid_y, s=asteroid_sizes, c='white', alpha=0.4, marker='.')

#   Kuiper belt beyond Neptune
neptune_r = planet_radii['Neptune']
kuiper_inner = neptune_r * 1.05
kuiper_outer = neptune_r * 1.5

#   Generate Kuiper belt objects
num_kuiper = 10000
kuiper_angles = np.random.uniform(0, 2 * np.pi, num_kuiper)
kuiper_radii = np.random.uniform(kuiper_inner, kuiper_outer, num_kuiper)
kuiper_x = cx + kuiper_radii * np.cos(kuiper_angles)
kuiper_y = cy + kuiper_radii * np.sin(kuiper_angles)
kuiper_sizes = np.random.uniform(0.03, 0.25, num_kuiper)

#   Fade alpha based on distance
kuiper_alphas = 1.0 - (kuiper_radii - kuiper_inner) / (kuiper_outer - kuiper_inner)
kuiper_alphas *= 0.3

#   Single scatter call with alpha array
ax.scatter(kuiper_x, kuiper_y, s=kuiper_sizes, c='white', 
           alpha=kuiper_alphas, marker='.')

# Jupiter Trojans at L4 and L5 Lagrange points
jupiter_r = planet_radii['Jupiter']
jupiter_L = longitudes['Jupiter'] % 360.0

# L4 (60° ahead) and L5 (60° behind)
for offset in [60, -60]:
    trojan_angle_deg = (jupiter_L + offset) % 360.0

    # Generate cluster in polar coordinates
    num_trojans = 600
    radial_offsets = np.random.normal(0, 0.03, num_trojans) # Radial spread
    angular_offsets = np.random.normal(0, 10, num_trojans)  # Angular spread

    # Convert to Cartesian
    trojan_angles = trojan_angle_deg + angular_offsets
    trojan_radii = jupiter_r + radial_offsets
    trojan_thetas = np.radians(-(0 - trojan_angles))
    trojan_x = cx + trojan_radii * np.cos(trojan_thetas)
    trojan_y = cy + trojan_radii * np.sin(trojan_thetas)
    trojan_sizes = np.random.uniform(0.05, 0.2, num_trojans)

    ax.scatter(trojan_x, trojan_y, s=trojan_sizes, c='white', alpha=0.4, marker='.')




# Earth's Moon
#     Moon ring
moon_ring_size = 250 # To keep Moon ring consistent across DPIs
earth_ring_r = (r_base / 10) * (dpi / moon_ring_size)
ax.add_patch(
    plt.Circle(
        (earth_x, earth_y),
        earth_ring_r,
        fill=False,
        lw=0.4,
        color='white',
        linestyle=(0, (4, 4))))

#     Moon's position relative to Earth
moon_vec = GeoVector(Body.Moon, utc, True)
moon_angle = math.degrees(math.atan2(moon_vec.y, moon_vec.x))
moon_theta_deg = 0 - moon_angle
moon_theta = math.radians(-moon_theta_deg)
moon_x = earth_x + earth_ring_r * math.cos(moon_theta)
moon_y = earth_y + earth_ring_r * math.sin(moon_theta)

#     Plot Moon icon
moon_imagebox = svg_to_imagebox("icons/moon.svg", zoom=0.08)
moon_ab = AnnotationBbox(moon_imagebox, (moon_x, moon_y), frameon=False)
ax.add_artist(moon_ab)




# Canvas setup
#   Limits and aspect
ax.set_aspect('equal', 'box')

#   Calculate axis limits
fig_width, fig_height = fig.get_size_inches()
aspect = fig_width / fig_height

if aspect > 1:  # Wider than tall
    ax.set_xlim(-1.3 * aspect, 1.3 * aspect)
    ax.set_ylim(-1.3, 1.3)
else:  # Taller than wide
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3 / aspect, 1.3 / aspect)

ax.axis('off')




# Save and show
plt.tight_layout()
fig.savefig("solarmap.png", dpi=dpi)
plt.show()
