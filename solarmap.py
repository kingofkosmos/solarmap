from astronomy import Time, Body, EclipticLongitude
import math
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import io
import cairosvg

# Planet list and astronomy data
planets = [Body.Mercury, Body.Venus, Body.Earth, Body.Mars,
    Body.Jupiter, Body.Saturn, Body.Uranus, Body.Neptune]

# Utility: convert SVG → OffsetImage
def svg_to_imagebox(svg_path, zoom=0.1):
    """Convert an SVG to a Matplotlib OffsetImage (PNG in memory)."""
    png_bytes = cairosvg.svg2png(url=svg_path)
    image = mpimg.imread(io.BytesIO(png_bytes), format='png')
    return OffsetImage(image, zoom=zoom)

utc = Time.Now()
longitudes = {planet.name: EclipticLongitude(planet, utc) for planet in planets}

# Canvas setup
fig, ax = plt.subplots(figsize=(6, 6))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')
cx, cy = 0.0, 0.0
r_base = 1.0

# Rings
for i in range(2, 10):
    circle = plt.Circle(
    (cx, cy),
    r_base * i / 8,
    fill=False,
    lw=0.3,
    color='gray',
    linestyle=(0, (10, 10))
    )

    ax.add_patch(circle)

# Radii for each planet
planet_radii = {p.name: r_base * i / 8 for i, p in enumerate(planets, start=2)}

# Plot planets using SVG icons
for name, L in longitudes.items():
    L = L % 360.0
    theta_deg = 0 - L
    theta = math.radians(-theta_deg)
    r = planet_radii.get(name, 1.0)
    x = cx + r * math.cos(theta)
    y = cy + r * math.sin(theta)

    svg_path = f"icons/{name.lower()}.svg"
    try:
        imagebox = svg_to_imagebox(svg_path, zoom=0.2)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False)
        ax.add_artist(ab)
    except Exception as e:
        print(f"⚠️ Could not load {svg_path}: {e}")

# Add the Sun at the center
try:
    sun_imagebox = svg_to_imagebox("icons/sun.svg", zoom=0.3)
    sun_ab = AnnotationBbox(sun_imagebox, (cx, cy), frameon=False)
    ax.add_artist(sun_ab)
except Exception as e:
    print(f"⚠️ Could not load sun.svg: {e}")

# Cosmetic
ax.set_aspect('equal', 'box')
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.axis('off')

# Show plot
plt.tight_layout()
fig.set_size_inches(1920/200, 1080/200)  # 300 dpi base
fig.savefig("output.png", dpi=200)
plt.show()
