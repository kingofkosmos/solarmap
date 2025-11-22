from astronomy import Time, Body, EclipticLongitude, GeoVector
import math
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import io
import cairosvg


#TODO: Optional starry background (generated stars or image?)
#TODO: Optional colors to planets, black & whitw or colored
#TODO: Optional colors to rings
#TODO: Optional colors to background
#TODO: Asteroid belt SVG icon
#TODO: Asteroid belt rotation (basic and advanced with different speeds?)
#TODO: Moons (Earth's Moon, Galilean moons, Titan, etc.)
#TODO: Dwarf planets (Pluto, Ceres, Haumea, Makemake, Eris)
#TODO: Comets (Halley, Hale-Bopp)
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
fig, ax = plt.subplots(figsize=(6, 6))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')
cx, cy = 0.0, 0.0
r_base = 1.0




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

#   Store Earth's position
    if name == "Earth":
        earth_x, earth_y = x, y

#   Plot planet icons
    svg_path = f"icons/{name.lower()}.svg"
    imagebox = svg_to_imagebox(svg_path, zoom=0.2)
    ab = AnnotationBbox(imagebox, (x, y), frameon=False)
    ax.add_artist(ab)

# Earth's Moon
#   Ring around Earth
earth_ring_r = r_base / 10
ax.add_patch(
    plt.Circle(
        (earth_x, earth_y),
        earth_ring_r,
        fill=False,
        lw=0.4,
        color='white',
        linestyle=(0, (4, 4))))

# Get Moon's position relative to Earth
moon_vec = GeoVector(Body.Moon, utc, True)
moon_angle = math.degrees(math.atan2(moon_vec.y, moon_vec.x))
moon_theta_deg = 0 - moon_angle
moon_theta = math.radians(-moon_theta_deg)
moon_x = earth_x + earth_ring_r * math.cos(moon_theta)
moon_y = earth_y + earth_ring_r * math.sin(moon_theta)

# Plot Moon icon
moon_imagebox = svg_to_imagebox("icons/moon.svg", zoom=0.08)
moon_ab = AnnotationBbox(moon_imagebox, (moon_x, moon_y), frameon=False)
ax.add_artist(moon_ab)




# Canvas limits and aspect
ax.set_aspect('equal', 'box')
ax.set_xlim(-1.3, 1.3)
ax.set_ylim(-1.3, 1.3)
ax.axis('off')




# Save and show
plt.tight_layout()
fig.set_size_inches(1920/200, 1080/200)  # 300 dpi base
fig.savefig("solarmap.png", dpi=200)
plt.show()
