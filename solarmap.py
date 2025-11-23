from astronomy import Time, Body, EclipticLongitude, GeoVector
import math
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import io
import cairosvg
import numpy as np

#Feature improvements
#TODO: Dwarf planets (Pluto, Ceres, Haumea, Makemake, Eris)
#TODO: Asteroid belt SVG icon (one or multiple clusters?)
#TODO: Asteroid belt rotation (one or multiple?))
#TODO: Moons (Galilean moons, Titan, Mars moons)
#TODO: Comets (Halley, Hale-Bopp)

#Visual improvements
#TODO: Optional labels for planets
#TODO: Optional background stars
#TODO: Optional colors to planets, b&w or colored
#TODO: Optional colors to rings
#TODO: Optional colors to background
#TODO: Optional rings fading with distance/time
#TODO: Custom time input




# Planet list
planets = [Body.Mercury, Body.Venus, Body.Earth, Body.Mars,
    Body.Jupiter, Body.Saturn, Body.Uranus, Body.Neptune]




# Convert planet SVG icons to OffsetImages
def svg_to_imagebox(svg_path, zoom=0.1):
    """Convert an SVG to a Matplotlib OffsetImage (PNG in memory)."""
    png_bytes = cairosvg.svg2png(url=svg_path)
    image = mpimg.imread(io.BytesIO(png_bytes), format='png')
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
    imagebox = svg_to_imagebox(svg_path, zoom=0.2)
    ab = AnnotationBbox(imagebox, (x, y), frameon=False)
    ax.add_artist(ab)

#   Earth's Moon
#       Moon ring
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

#       Moon's position relative to Earth
moon_vec = GeoVector(Body.Moon, utc, True)
moon_angle = math.degrees(math.atan2(moon_vec.y, moon_vec.x))
moon_theta_deg = 0 - moon_angle
moon_theta = math.radians(-moon_theta_deg)
moon_x = earth_x + earth_ring_r * math.cos(moon_theta)
moon_y = earth_y + earth_ring_r * math.sin(moon_theta)

#       Plot Moon icon
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
