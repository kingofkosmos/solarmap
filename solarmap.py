from astronomy import Time, Body, EclipticLongitude, GeoVector, Observer, SearchRiseSet, Direction, Illumination, SearchMoonPhase, JupiterMoons
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.colors import hex2color
from functools import lru_cache
from zoneinfo import ZoneInfo
from PIL import Image
import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import io
import cairosvg
import numpy as np
import datetime




# ═══════════════════════════════════════════════════════════════════════════
# 1. TO-DO LIST
# ═══════════════════════════════════════════════════════════════════════════

#TODO: Test different resolutions and aspect ratios
#TODO: Move supersample multiplier to configuration
#TODO: Move magic numbers to configuration
#TODO: Automatic wallpaper generation in Github Actions?
#TODO: Comets (Halley, Hale-Bopp)
#TODO: Arguments for command line usage
#TODO: Realistic elliptical orbits (enables rest of the dwarf planets & astrology)
##      Astrology: Sky division to constellations, meanings of planets in different constellations
##      Dwarf planets: Haumea, Makemake, Eris




# ═══════════════════════════════════════════════════════════════════════════
# 2. CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Bottom right text toggle
show_info_text = True  # Set to False to hide info text

# Geolocation coordinates for weather forecast, moon phase and rise/set times
latitude = 60.06977
longitude = 23.66283

# Custom time input
custom_date = "Now"  # Options: None, "Now", "YYYY-MM-DD", or "YYYY-MM-DD HH:MM"

# Orbital trails toggle
trail_days = 100  # How long the trails are in days

# Planet colors
planet_colors = {
    'Sun':               '#FFF75E',
    'Mercury':           '#815313',
    'Venus':             '#3CB371',
    'Earth_ocean':       '#4A90E2',
    'Earth_land_top':    '#013C28',
    'Earth_land_bottom': '#F5F5DC',
    'Mars':              '#CD5C5C',
    'Jupiter':           '#C88B3A',
    'Saturn':            '#FAD5A5',
    'Uranus':            '#4FD0E0',
    'Neptune':           '#4166F5',
    'Pluto':             '#A0826D'
}


# Language: 'fi' or 'en'
LANGUAGE = 'en'

STRINGS = {
    'fi': {
        'full_moon':        'Täysikuu',
        'new_moon':         'Uusikuu',
        'waxing_gibbous':   'Kasvava kupera kuu',
        'first_quarter':    'Puolikuu (ensimmäinen neljännes)',
        'waxing_crescent':  'Kasvava sirppi',
        'waning_gibbous':   'Vähenevä kupera kuu',
        'last_quarter':     'Puolikuu (viimeinen neljännes)',
        'waning_crescent':  'Vähenevä sirppi',
        'days_to_full':     'pv täysikuuhun',
        'daylight_header':  'Päivänvalo huomenna:',
        'daylight_time':    'klo {rise} - {set}',
        'daylight_hours':   '{h} t {m} min',
    },
    'en': {
        'full_moon':        'Full Moon',
        'new_moon':         'New Moon',
        'waxing_gibbous':   'Waxing Gibbous',
        'first_quarter':    'First Quarter',
        'waxing_crescent':  'Waxing Crescent',
        'waning_gibbous':   'Waning Gibbous',
        'last_quarter':     'Last Quarter',
        'waning_crescent':  'Waning Crescent',
        'days_to_full':     'days to full moon',
        'daylight_header':  'Daylight tomorrow:',
        'daylight_time':    '{rise} - {set}',
        'daylight_hours':   '{h} h {m} min',
    }
}

T = STRINGS[LANGUAGE]



# ═══════════════════════════════════════════════════════════════════════════
# 2.1 VISUAL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Random seed for reproducible star/asteroid patterns
RANDOM_SEED = 123

# Star field configuration
STARS_CONFIG = {
    'base_count': 200,
    'base_size_range': (0.1, 1.5),
    'base_alpha': 0.4,
    'band_count': 1000,
    'band_size_range': (0.05, 0.8),
    'band_alpha': 0.3,
    'band_width': 0.3  # Standard deviation for band distribution
}




# ═══════════════════════════════════════════════════════════════════════════
# 3. PLANET POSITION CALCULATIONS
# ═══════════════════════════════════════════════════════════════════════════

def plot_fading_arc(ax, cx, cy, r, theta_start, theta_end, color, linewidth=1.0, n=50, alpha_start=0.6, alpha_end=0.0):
    """Plot an arc with fading alpha from start to end."""
    theta_range = np.linspace(theta_start, theta_end, n)
    
    arc_x = cx + r * np.cos(theta_range)
    arc_y = cy + r * np.sin(theta_range)
    
    alphas = np.linspace(alpha_start, alpha_end, n)
    
    for i in range(n - 1):
        ax.plot([arc_x[i], arc_x[i+1]], 
                [arc_y[i], arc_y[i+1]], 
                color=color, alpha=alphas[i], linewidth=linewidth)

# Cache for SVG conversions to avoid repeated processing
@lru_cache(maxsize=128)
def _svg_to_png_cached(svg_path):
    """Cached SVG to PNG conversion."""
    return cairosvg.svg2png(url=svg_path)

def svg_to_imagebox(svg_path, zoom=0.1, color=None):
    """Convert an SVG to a Matplotlib OffsetImage (PNG in memory)."""
    # Get cached PNG bytes (color-independent)
    png_bytes = _svg_to_png_cached(svg_path)
    image = mpimg.imread(io.BytesIO(png_bytes), format='png')

    # Colorize if color is provided
    if color is not None:
        rgb = hex2color(color)
        mask = image[:, :, :3].mean(axis=2) > 0.5
        for i in range(3):
            image[:, :, i] = np.where(mask, rgb[i], image[:, :, i])

    return OffsetImage(image, zoom=zoom)

# Get current time
if custom_date is None or custom_date == "Now":
    utc = Time.Now()
elif ' ' in custom_date:
    # Format with time: "YYYY-MM-DD HH:MM"
    date_part, time_part = custom_date.split(' ')
    year, month, day = map(int, date_part.split('-'))
    hour, minute = map(int, time_part.split(':'))
    utc = Time.Make(year, month, day, hour, minute, 0)
else:
    # Format without time: "YYYY-MM-DD"
    year, month, day = map(int, custom_date.split('-'))
    utc = Time.Make(year, month, day, 0, 0, 0)

# Planet list
planets = [Body.Mercury, Body.Venus, Body.Earth, Body.Mars,
    Body.Jupiter, Body.Saturn, Body.Uranus, Body.Neptune, Body.Pluto]


# Calculate longitudes (angles from the Sun)
longitudes = {planet.name: EclipticLongitude(planet, utc) for planet in planets}

def longitude_to_theta(longitude):
    """Convert ecliptic longitude to plotting angle (radians)."""
    L = longitude % 360
    theta_deg = 0 - L
    return math.radians(-theta_deg)




# ═══════════════════════════════════════════════════════════════════════════
# 5. CANVAS INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

# Set wallpaper resolution
width_px = 1920
height_px = 1080

reference_height = 1440
reference_dpi = 100 # Reference DPI for scaling, change for bigger/smaller planets and stars
dpi = int(height_px * (reference_dpi / reference_height))

fig, ax = plt.subplots(figsize=(1, 1))
fig.set_size_inches(width_px/dpi, height_px/dpi)
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

# Cache figure dimensions for reuse
fig_width, fig_height = fig.get_size_inches()
fig_aspect = fig_width / fig_height

cx, cy = 0, 0
r_base = 0.80  # Ring radius base unit, change for bigger/smaller rings

# Taskbar offset upwards percentage, change to move image upwards
taskbar_offset = 0.02

# Shift center up by 5% of y-axis range
cy_offset = taskbar_offset * 2.6  # 2.6 is your y-axis range (from -1.3 to 1.3)
cy = cy + cy_offset




# ═══════════════════════════════════════════════════════════════════════════
# 6. PLANETARY RINGS AND RADII
# ═══════════════════════════════════════════════════════════════════════════

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
current += step * 2 # Extra gap before Pluto
rings.append(current) # Ring 9 (Pluto)
for i, r in enumerate(rings[:-1]):  # All rings except the last one
    ax.add_patch(
        plt.Circle((cx, cy), r, fill=False, linewidth=0.4, color='white', alpha=0.4, linestyle=(0, (13, 16))))

# Radii for each planet
planet_radii = {p.name: rings[i] for i, p in enumerate(planets)}




# ═══════════════════════════════════════════════════════════════════════════
# 7. BACKGROUND STARS
# ═══════════════════════════════════════════════════════════════════════════

# Calculate aspect-aware limits for stars
aspect = fig_width / fig_height
if fig_aspect > 1:  # Wider than tall
    star_xlim = (-1.3 * aspect, 1.3 * aspect)
    star_ylim = (-1.3, 1.3)
else:  # Taller than wide
    star_xlim = (-1.3, 1.3)
    star_ylim = (-1.3 / aspect, 1.3 / aspect)

# Generate stars
np.random.seed(RANDOM_SEED)

# Base stars
num_stars = STARS_CONFIG['base_count']
star_x = np.random.uniform(star_xlim[0], star_xlim[1], num_stars)
star_y = np.random.uniform(star_ylim[0], star_ylim[1], num_stars)
base_min, base_max = STARS_CONFIG['base_size_range']
star_sizes = np.random.uniform(base_min, base_max, num_stars)

# Dense band
band_stars = STARS_CONFIG['band_count']
band_x = np.random.uniform(star_xlim[0], star_xlim[1], band_stars)
band_y = np.random.normal(0, STARS_CONFIG['band_width'], band_stars)
band_min, band_max = STARS_CONFIG['band_size_range']
band_sizes = np.random.uniform(band_min, band_max, band_stars)

# Mask out stars inside Neptune's ring
neptune_radius = planet_radii['Neptune']
star_distances = np.sqrt((star_x - cx)**2 + (star_y - cy)**2)
band_distances = np.sqrt((band_x - cx)**2 + (band_y - cy)**2)

star_mask = star_distances > neptune_radius * 1.05
band_mask = band_distances > neptune_radius * 1.05

star_x = star_x[star_mask]
star_y = star_y[star_mask]
star_sizes = star_sizes[star_mask]

band_x = band_x[band_mask]
band_y = band_y[band_mask]
band_sizes = band_sizes[band_mask]

# Plot stars
ax.scatter(star_x, star_y, s=star_sizes, c='white', alpha=STARS_CONFIG['base_alpha'], marker='.')
ax.scatter(band_x, band_y, s=band_sizes, c='white', alpha=STARS_CONFIG['band_alpha'], marker='.')




# ═══════════════════════════════════════════════════════════════════════════
# 8. PLOTTING PLANETS AND OBJECTS
# ═══════════════════════════════════════════════════════════════════════════

# Sun
sun_color = planet_colors['Sun']
sun_imagebox = svg_to_imagebox("icons/sun.svg", zoom=0.4, color=sun_color)
sun_ab = AnnotationBbox(sun_imagebox, (cx, cy), frameon=False)
ax.add_artist(sun_ab)

# Planets and Dwarf Planets
for name, L in longitudes.items():
    theta = longitude_to_theta(L)
    r = planet_radii.get(name, 1)
    x = cx + r * math.cos(theta)
    y = cy + r * math.sin(theta)

# (Store Earth's position for Moon plotting)
    if name == "Earth":
        earth_x, earth_y = x, y

# Plot planet icons
    svg_path = "icons/moon.svg" if name == "Pluto" else f"icons/{name.lower()}.svg"
    
    # Set zoom level (custom for Pluto)
    zoom = 0.08 if name == "Pluto" else 0.3

    # Special handling for Earth to add two colors
    if name == "Earth":
        png_bytes = cairosvg.svg2png(url=svg_path)
        image = mpimg.imread(io.BytesIO(png_bytes), format='png')
        
        # Black areas (landmasses) → gradient green-to-beige, White pixels (ocean) → blue
        ocean_rgb = hex2color(planet_colors['Earth_ocean'])
        land_rgb_top = hex2color(planet_colors['Earth_land_top'])
        land_rgb_bottom = hex2color(planet_colors['Earth_land_bottom'])

        # Build per-row gradient for land (top = green, bottom = beige)
        h = image.shape[0]
        t = np.linspace(0, 0.8, h)[:, np.newaxis]  # shape (h, 1)
        land_gradient = (1 - t) * np.array(land_rgb_top) + t * np.array(land_rgb_bottom)  # (h, 3)

        is_black = image[:, :, :3].max(axis=2) < 0.5

        for i in range(3):
            land_color_channel = np.broadcast_to(land_gradient[:, i:i+1], image.shape[:2])
            image[:, :, i] = np.where(is_black, land_color_channel, ocean_rgb[i])

        imagebox = OffsetImage(image, zoom=zoom)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False)
        ax.add_artist(ab)
    else:
        color = planet_colors.get(name)
        imagebox = svg_to_imagebox(svg_path, zoom=zoom, color=color)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False)
        ax.add_artist(ab)

# Orbital trails
# Calculate orbital periods (in days) for each planet
orbital_periods = {
    'Mercury': 88,
    'Venus': 225,
    'Earth': 365,
    'Mars': 687,
    'Jupiter': 4333,
    'Saturn': 10759,
    'Uranus': 30687,
    'Neptune': 60190,
    'Pluto': 90560
}

for planet in planets:
    name = planet.name

    # Skip Pluto's trail
    if name == 'Pluto':
        continue

    r = planet_radii.get(name, 1)
    
    # Calculate current position
    current_theta = longitude_to_theta(longitudes[name])

    # Calculate what fraction of orbit to show based on trail_days
    period = orbital_periods[name]
    arc_fraction = trail_days / period
    arc_span = 360 * arc_fraction
    
    # Create arc from current position backwards
    theta_start = current_theta
    theta_end = current_theta - math.radians(arc_span)
    
    # Get trail color
    trail_color = planet_colors['Earth_ocean'] if name == 'Earth' else planet_colors.get(name, 'white')

    # Plot trail
    arc_span_rad = abs(theta_start - theta_end)
    n_segments = max(100, int(arc_span_rad / (2 * math.pi) * 1000))
    plot_fading_arc(ax, cx, cy, r, theta_start, theta_end, trail_color, linewidth=1.5, n=n_segments)




# ═══════════════════════════════════════════════════════════════════════════
# 9. ASTEROIDS
# ═══════════════════════════════════════════════════════════════════════════

# Asteroid belt between Mars and Jupiter
mars_r = planet_radii['Mars']
jupiter_r = planet_radii['Jupiter']
asteroid_belt_inner = mars_r + (jupiter_r - mars_r) * 0.1
asteroid_belt_outer = mars_r + (jupiter_r - mars_r) * 0.9

# Generate asteroids
np.random.seed(RANDOM_SEED)
num_asteroids = 7000
asteroid_angles = np.random.uniform(0, 2 * np.pi, num_asteroids)
asteroid_radii = np.random.uniform(asteroid_belt_inner, asteroid_belt_outer, num_asteroids)

# Calculate rotation as average of Mars and Jupiter
mars_L = longitudes['Mars'] % 360
jup_L  = longitudes['Jupiter'] % 360
belt_L = (mars_L + jup_L) / 2

rotation = math.radians(belt_L)
rotated_angles = asteroid_angles + rotation

asteroid_x = cx + asteroid_radii * np.cos(rotated_angles)
asteroid_y = cy + asteroid_radii * np.sin(rotated_angles)
asteroid_sizes = np.random.uniform(0.02, 0.15, num_asteroids)

# Fade in from inner edge (fast), fade out at outer edge (slow)
belt_width = asteroid_belt_outer - asteroid_belt_inner
normalized_pos = (asteroid_radii - asteroid_belt_inner) / belt_width

# Fast fade in, slow fade out
asteroid_alphas = np.ones(num_asteroids) * 0.4
fade_in_mask = normalized_pos < 0.5
fade_out_mask = normalized_pos > 0.5

asteroid_alphas[fade_in_mask] = (normalized_pos[fade_in_mask] / 0.2) * 0.4
asteroid_alphas[fade_out_mask] = (1 - (normalized_pos[fade_out_mask] - 0.6) / 0.4) * 0.4

# Generate color variation for asteroids
base_color = np.array([168, 152, 128]) / 255  # #A89880 in RGB
color_variation = np.random.uniform(-0.2, 0.2, (num_asteroids, 3))
asteroid_colors = np.clip(base_color + color_variation, 0, 1)

ax.scatter(asteroid_x, asteroid_y, s=asteroid_sizes, c=asteroid_colors, alpha=asteroid_alphas, marker='.')




# ═══════════════════════════════════════════════════════════════════════════
# 9.1 KUIPER BELT
# ═══════════════════════════════════════════════════════════════════════════

# Ranges for Kuiper belt
neptune_r = planet_radii['Neptune']
kuiper_inner = neptune_r * 1.05
kuiper_outer = neptune_r * 1.5

# Generate Kuiper belt objects
num_kuiper = 6000
kuiper_angles = np.random.uniform(0, 2 * np.pi, num_kuiper)
kuiper_radii = np.random.uniform(kuiper_inner, kuiper_outer, num_kuiper)

# Rotate slightly slower than Neptune (95% of Neptune's rotation)
neptune_L = longitudes['Neptune'] % 360.0
kuiper_rotation = math.radians(neptune_L * 0.95)
rotated_kuiper_angles = kuiper_angles + kuiper_rotation

kuiper_x = cx + kuiper_radii * np.cos(rotated_kuiper_angles)
kuiper_y = cy + kuiper_radii * np.sin(rotated_kuiper_angles)
kuiper_sizes = np.random.uniform(0.03, 0.25, num_kuiper)

# Fade alpha based on distance
kuiper_alphas = 1.0 - (kuiper_radii - kuiper_inner) / (kuiper_outer - kuiper_inner)
kuiper_alphas *= 0.8

# Generate color variation for Kuiper belt
base_color = np.array([149, 165, 181]) / 255  # #95A5B5 in RGB
color_variation = np.random.uniform(-0.2, 0.2, (num_kuiper, 3))
kuiper_colors = np.clip(base_color + color_variation, 0, 1)

ax.scatter(kuiper_x, kuiper_y, s=kuiper_sizes, c=kuiper_colors, 
           alpha=kuiper_alphas, marker='.')




# ═══════════════════════════════════════════════════════════════════════════
# 9.2 JUPITER TROJANS
# ═══════════════════════════════════════════════════════════════════════════

# Jupiter Trojans - get Jupiter's position
jupiter_r = planet_radii['Jupiter']
jupiter_L = longitudes['Jupiter'] % 360

def trojan_cloud(jupiter_r, jupiter_L, offset_deg, n=700):
    # L4 (+60°) or L5 (−60°)
    center_angle = math.radians(-(0 - ((jupiter_L + offset_deg) % 360)))

    # radial distribution (slightly elongated)
    radial = np.random.normal(0, 0.03, n)

    # angular distribution (teardrop shape)
    # more particles near center, fading outward
    angular_core = np.random.normal(0, 5, n)          # central clump
    angular_tail = np.random.normal(15, 8, n)         # stretched tail

    # blend core/tail weights smoothly
    blend = np.random.uniform(0, 1, n)
    angular = angular_core * (1 - blend) + angular_tail * blend

    # sign: tail outward from Jupiter
    angular *= np.sign(offset_deg)

    theta = center_angle + np.radians(angular)
    rr = jupiter_r + radial

    x = cx + rr * np.cos(theta)
    y = cy + rr * np.sin(theta)
    size = np.random.uniform(0.05, 0.2, n)

    ax.scatter(x, y, s=size, c='#8B6F47', alpha=0.35, marker='.')

trojan_cloud(jupiter_r, jupiter_L, +60)   # L4
trojan_cloud(jupiter_r, jupiter_L, -60)   # L5




# ═══════════════════════════════════════════════════════════════════════════
# 10. MOONS AND DWARF PLANETS
# ═══════════════════════════════════════════════════════════════════════════

# Jupiter's moons
jupiter_theta = longitude_to_theta(longitudes['Jupiter'])
jupiter_x = cx + jupiter_r * math.cos(jupiter_theta)
jupiter_y = cy + jupiter_r * math.sin(jupiter_theta)

moon_radii = {
    'Io': 0.10,
    'Europa': 0.11,
    'Ganymede': 0.13,
    'Callisto': 0.14
}

jm = JupiterMoons(utc)
moon_data = {
    'Io': jm.io,
    'Europa': jm.europa,
    'Ganymede': jm.ganymede,
    'Callisto': jm.callisto
}

# Jupiter moon colors
jupiter_moon_colors = {
    'Io': '#F4D03F',
    'Europa': '#D4C5B0',
    'Ganymede': '#8B7E66',
    'Callisto': '#4A4A4A'
}

# Jupiter moon zooms
jupiter_moon_zooms = {
    'Io': 0.11,
    'Europa': 0.10,
    'Ganymede': 0.15,
    'Callisto': 0.13
}

# Jupiter moon trail fractions
jupiter_moon_trails = {
    'Io': 1/4,
    'Europa': 1/5,
    'Ganymede': 1/8,
    'Callisto': 1/10
}

for moon_name, moon_vec in moon_data.items():
    angle = math.degrees(math.atan2(moon_vec.y, moon_vec.x))
    theta = math.radians(-(0 - angle))
    r = moon_radii[moon_name]
    x = jupiter_x + r * math.cos(theta)
    y = jupiter_y + r * math.sin(theta)

    moon_color = jupiter_moon_colors[moon_name]
    moon_zoom = jupiter_moon_zooms[moon_name]
    
    # Plot Jupiter's moon
    imagebox = svg_to_imagebox("icons/moon.svg", zoom=moon_zoom, color=moon_color)
    ab = AnnotationBbox(imagebox, (x, y), frameon=False)
    ax.add_artist(ab)
    
    # Plot trail
    current_theta_deg = 0 - angle
    arc_span = 360 * jupiter_moon_trails[moon_name]
    
    theta_start = math.radians(-current_theta_deg)
    theta_end = math.radians(-(current_theta_deg + arc_span))
    
    plot_fading_arc(ax, jupiter_x, jupiter_y, r, theta_start, theta_end, moon_color, linewidth=0.8)

# Earth's Moon
earth_moon_data = {
    'Moon': {
        'orbit_r': 0.06,
        'color': 'white',
        'zoom': 0.11,
        'trail_fraction': 1/2
    }
}

for moon_name, data in earth_moon_data.items():
    # Get position from astronomy library
    moon_vec = GeoVector(Body.Moon, utc, True)
    moon_angle = math.degrees(math.atan2(moon_vec.y, moon_vec.x))
    moon_theta_deg = 0 - moon_angle
    moon_theta = math.radians(-moon_theta_deg)
    
    x = earth_x + data['orbit_r'] * math.cos(moon_theta)
    y = earth_y + data['orbit_r'] * math.sin(moon_theta)
    
    # Plot moon
    imagebox = svg_to_imagebox("icons/moon.svg", zoom=data['zoom'], color=data['color'])
    ax.add_artist(AnnotationBbox(imagebox, (x, y), frameon=False))
    
    # Plot trail
    arc_span = 360 * data['trail_fraction']
    theta_start = math.radians(-moon_theta_deg)
    theta_end = math.radians(-(moon_theta_deg + arc_span))
    
    plot_fading_arc(ax, earth_x, earth_y, data['orbit_r'], theta_start, theta_end, data['color'], linewidth=1.0)

# Neptune's moon Triton
neptune_theta = longitude_to_theta(longitudes['Neptune'])
neptune_r_plot = planet_radii['Neptune']
neptune_x = cx + neptune_r_plot * math.cos(neptune_theta)
neptune_y = cy + neptune_r_plot * math.sin(neptune_theta)

epoch_jd_2025 = 2460676.5 # Reference epoch: January 1, 2025, 00:00 UTC (JD 2460676.5)
days_since_epoch = utc.ut - epoch_jd_2025

neptune_moon_data = {
    'Triton': {
        'epoch_angle': 2.733989,
        'period': 5.877,
        'orbit_r': 0.08,
        'color': '#E6E6FA',
        'zoom': 0.09,
        'trail_fraction': 1/2,
        'retrograde': True  # Triton orbits backwards
    }
}

for moon_name, data in neptune_moon_data.items():
    # Calculate position (retrograde uses subtraction instead of addition)
    if data.get('retrograde', False):
        angle = (data['epoch_angle'] - days_since_epoch / data['period'] * 360) % 360
    else:
        angle = (data['epoch_angle'] + days_since_epoch / data['period'] * 360) % 360
    
    theta = math.radians(-(0 - angle))
    
    x = neptune_x + data['orbit_r'] * math.cos(theta)
    y = neptune_y + data['orbit_r'] * math.sin(theta)
    
    # Plot moon
    moon_color = data['color']
    imagebox = svg_to_imagebox("icons/moon.svg", zoom=data['zoom'], color=moon_color)
    ax.add_artist(AnnotationBbox(imagebox, (x, y), frameon=False))
    
    # Plot trail (reverse direction for retrograde)
    current_theta_deg = 0 - angle
    arc_span = 360 * data['trail_fraction']
    
    theta_start = math.radians(-current_theta_deg)
    if data.get('retrograde', False):
        theta_end = math.radians(-(current_theta_deg - arc_span))
    else:
        theta_end = math.radians(-(current_theta_deg + arc_span))
    
    plot_fading_arc(ax, neptune_x, neptune_y, data['orbit_r'], theta_start, theta_end, moon_color, linewidth=0.7)

# Saturn's moons
saturn_theta = longitude_to_theta(longitudes['Saturn'])
saturn_r = planet_radii['Saturn']
saturn_x = cx + saturn_r * math.cos(saturn_theta)
saturn_y = cy + saturn_r * math.sin(saturn_theta)

# Saturn moon data
saturn_moon_data = {
    'Titan': {
        'epoch_angle': 356.104439,
        'period': 15.945,
        'orbit_r': 0.11,
        'color': '#FFA500',
        'zoom': 0.14,
        'trail_fraction': 1/8
    },
    'Rhea': {
        'epoch_angle': 2.830452,
        'period': 4.518,
        'orbit_r': 0.10,
        'color': '#C0C0C0',
        'zoom': 0.06,
        'trail_fraction': 1/4
    },
    'Iapetus': {
        'epoch_angle': 5.711541,
        'period': 79.33,
        'orbit_r': 0.12,
        'color': '#8B7355',
        'zoom': 0.06,
        'trail_fraction': 1/12
    }
}

for moon_name, data in saturn_moon_data.items():
    # Calculate position
    angle = (data['epoch_angle'] + days_since_epoch / data['period'] * 360) % 360
    theta = math.radians(-(0 - angle))
    
    x = saturn_x + data['orbit_r'] * math.cos(theta)
    y = saturn_y + data['orbit_r'] * math.sin(theta)
    
    # Plot Saturn's moon
    moon_color = data['color']
    imagebox = svg_to_imagebox("icons/moon.svg", zoom=data['zoom'], color=moon_color)
    ax.add_artist(AnnotationBbox(imagebox, (x, y), frameon=False))
    
    # Plot trail
    current_theta_deg = 0 - angle
    arc_span = 360 * data['trail_fraction']
    
    theta_start = math.radians(-current_theta_deg)
    theta_end = math.radians(-(current_theta_deg + arc_span))
    
    plot_fading_arc(ax, saturn_x, saturn_y, data['orbit_r'], theta_start, theta_end, moon_color, linewidth=0.8)

# Uranus's moons
uranus_theta = longitude_to_theta(longitudes['Uranus'])
uranus_r = planet_radii['Uranus']
uranus_x = cx + uranus_r * math.cos(uranus_theta)
uranus_y = cy + uranus_r * math.sin(uranus_theta)

# Uranus's moons data
uranus_moon_data = {
    'Titania': {
        'epoch_angle': 0.855326,
        'period': 8.706,
        'orbit_r': 0.07,
        'color': '#B0A090',
        'zoom': 0.06,
        'trail_fraction': 1/6
    },
    'Oberon': {
        'epoch_angle': 0.910603,
        'period': 13.463,
        'orbit_r': 0.08,
        'color': '#8B8680',
        'zoom': 0.06,
        'trail_fraction': 1/8
    }
}

for moon_name, data in uranus_moon_data.items():
    # Calculate position
    angle = (data['epoch_angle'] + days_since_epoch / data['period'] * 360) % 360
    theta = math.radians(-(0 - angle))
    
    x = uranus_x + data['orbit_r'] * math.cos(theta)
    y = uranus_y + data['orbit_r'] * math.sin(theta)
    
    # Plot moon
    moon_color = data['color']
    imagebox = svg_to_imagebox("icons/moon.svg", zoom=data['zoom'], color=moon_color)
    ax.add_artist(AnnotationBbox(imagebox, (x, y), frameon=False))
    
    # Plot trail
    current_theta_deg = 0 - angle
    arc_span = 360 * data['trail_fraction']
    
    theta_start = math.radians(-current_theta_deg)
    theta_end = math.radians(-(current_theta_deg + arc_span))
    
    plot_fading_arc(ax, uranus_x, uranus_y, data['orbit_r'], theta_start, theta_end, moon_color, linewidth=0.7)

# Dwarf Planet Ceres
ceres_L_epoch = 315.17       # Orbital Longitude on this date
ceres_mean_motion = 0.21387  # Degrees per day

# Calculate current position
ceres_L = (ceres_L_epoch + ceres_mean_motion * days_since_epoch) % 360
ceres_theta = math.radians(-(0 - ceres_L))

# Plot Ceres
# Visual radius placed between Mars and Jupiter for clarity
ceres_r = (planet_radii['Mars'] + planet_radii['Jupiter']) / 2  
ceres_x = cx + ceres_r * math.cos(ceres_theta)
ceres_y = cy + ceres_r * math.sin(ceres_theta)

ceres_imagebox = svg_to_imagebox("icons/moon.svg", zoom=0.05, color='#A0826D')
ax.add_artist(AnnotationBbox(ceres_imagebox, (ceres_x, ceres_y), frameon=False))




# ═══════════════════════════════════════════════════════════════════════════
# 11. CANVAS FINALIZATION
# ═══════════════════════════════════════════════════════════════════════════

# Limits and aspect
ax.set_aspect('equal', 'box')

# Calculate axis limits
if fig_aspect > 1:  # Wider than tall
    ax.set_xlim(-1.3 * aspect, 1.3 * aspect)
    ax.set_ylim(-1.3, 1.3)
else:  # Taller than wide
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3 / aspect, 1.3 / aspect)

ax.axis('off')




# ═══════════════════════════════════════════════════════════════════════════
# 12. BOTTOM RIGHT INFO
# ═══════════════════════════════════════════════════════════════════════════

if show_info_text:
    # Calculate text position (bottom right with taskbar offset)
    if fig_aspect > 1:
        text_x = 1.3 * aspect - 0.07
        text_y = -1.2 + (taskbar_offset * 2.6)
    else:
        text_x = 1.3 - 0.07
        text_y = (-1.3 / aspect) + (taskbar_offset * 2.6) + 0.1

    # Convert astronomy Time to Python datetime in UTC
    cal = [int(x) for x in utc.Calendar()[:6]]
    dt_utc = datetime.datetime(*cal, tzinfo=datetime.timezone.utc)

    # Get sunrise and sunset for today
    observer = Observer(latitude, longitude, 0)
    sunrise_time_obj = SearchRiseSet(Body.Sun, observer, Direction.Rise, utc, 1)
    sunset_time_obj = SearchRiseSet(Body.Sun, observer, Direction.Set, utc, 1)

    # Convert to local time
    sunrise_cal = sunrise_time_obj.Calendar()
    sunset_cal = sunset_time_obj.Calendar()

    sunrise_utc = datetime.datetime(*[int(x) for x in sunrise_cal[:6]], tzinfo=datetime.timezone.utc)
    sunset_utc = datetime.datetime(*[int(x) for x in sunset_cal[:6]], tzinfo=datetime.timezone.utc)

    sunrise_local = sunrise_utc.astimezone(ZoneInfo('Europe/Helsinki'))
    sunset_local = sunset_utc.astimezone(ZoneInfo('Europe/Helsinki'))

    sunrise_time = f"{sunrise_local.hour}.{sunrise_local.minute:02d}"
    sunset_time = f"{sunset_local.hour}.{sunset_local.minute:02d}"

    # Calculate daylight hours
    daylight_duration = sunset_local - sunrise_local
    daylight_hours = daylight_duration.seconds // 3600
    daylight_mins = (daylight_duration.seconds % 3600) // 60




# ═══════════════════════════════════════════════════════════════════════════
# 12.1 MOON PHASE
# ═══════════════════════════════════════════════════════════════════════════

    # Get moon phase info
    illum = Illumination(Body.Moon, utc)
    phase_angle = illum.phase_angle
    illumination = illum.phase_fraction

    # Determine waxing vs waning by checking if illumination is increasing
    # Sample 1 hour later to see if moon is getting brighter or darker
    future_illum = Illumination(Body.Moon, utc.AddDays(1.0/24.0))
    is_waxing = future_illum.phase_fraction > illumination

    # Determine phase name
    if illumination > 0.99:
        phase_name = T['full_moon']
    elif illumination < 0.01:
        phase_name = T['new_moon']
    elif is_waxing: # Waxing, growing brighter
        if illumination > 0.55:
            phase_name = T['waxing_gibbous']
        elif illumination > 0.45:
            phase_name = T['first_quarter']
        else:
            phase_name = T['waxing_crescent']
    else:  # Waning, getting darker
        if illumination > 0.55:
            phase_name = T['waning_gibbous']
        elif illumination > 0.45:
            phase_name = T['last_quarter']
        else:
            phase_name = T['waning_crescent']

    # Search for next full moon (phase 180°) within next 30 days
    next_full_moon = SearchMoonPhase(180, utc, 30)
    days_to_full = next_full_moon.ut - utc.ut  # Difference in days




# ═══════════════════════════════════════════════════════════════════════════
# 12.2 PLOT INFO TEXT
# ═══════════════════════════════════════════════════════════════════════════

    cal = utc.Calendar()
    date_str = f"{int(cal[0])}-{int(cal[1]):02d}-{int(cal[2]):02d}"

info_boxes = []

# 1. Moon phase
moon_text = f"\n\n\n{phase_name}\n{days_to_full:.0f} {T['days_to_full']}"
info_boxes.append(moon_text)

# 2. Daylight
daylight_text = (
    f"{T['daylight_header']}\n"
    f"{T['daylight_time'].format(rise=sunrise_time, set=sunset_time)}\n"
    f"{T['daylight_hours'].format(h=daylight_hours, m=daylight_mins)}"
)
info_boxes.append(daylight_text)


# Draw stacked info boxes
box_width = 0.5
box_spacing = 0.0
box_padding = 0.015
current_y = text_y
    
for i, box_text in enumerate(reversed(info_boxes)):
    # Count lines in this box
    num_lines = box_text.count('\n') + 1
    line_height = 0.035
    box_height = num_lines * line_height + 2 * box_padding - 0.01
    
    # Draw white outline rectangle
    box_left = text_x - box_width
    box_bottom = current_y
    
    
    # Draw text inside box (left-aligned)
    text_x_pos = box_left + box_padding
    text_y_pos = box_bottom + box_padding
    
    ax.text(text_x_pos, text_y_pos, box_text,
            color='white', fontsize=11,
            ha='left', va='bottom',
            alpha=0.7, zorder=11)
    
    # Special handling for first box (moon phase) - add moon indicator
    if i == len(info_boxes) - 1:
        moon_radius = 0.03

        # top-left inside the box
        moon_indicator_x = box_left + moon_radius + box_padding
        moon_indicator_y = box_bottom + box_height - moon_radius - box_padding - 0.02

        # Draw dark gray base circle
        ax.add_patch(plt.Circle((moon_indicator_x, moon_indicator_y), moon_radius, 
                                fill=True, color='#404040', alpha=0.9, zorder=12))
        
        # Draw illuminated part
        if illumination > 0.01:
            theta = np.linspace(np.pi/2, -np.pi/2, 100)
            
            if is_waxing:
                # Right side lit
                x_outer = moon_indicator_x + moon_radius * np.cos(theta)
                y_outer = moon_indicator_y + moon_radius * np.sin(theta)
                
                curve_amount = abs(illumination - 0.5) * 2
                ellipse_width = curve_amount * moon_radius
                
                if illumination < 0.5:
                    x_terminator = moon_indicator_x + ellipse_width * np.cos(theta)
                else:
                    x_terminator = moon_indicator_x - ellipse_width * np.cos(theta)
                y_terminator = moon_indicator_y + moon_radius * np.sin(theta)
                
                x_lit = np.concatenate([x_outer, x_terminator[::-1]])
                y_lit = np.concatenate([y_outer, y_terminator[::-1]])
                
                ax.fill(x_lit, y_lit, color='white', alpha=0.9, zorder=13, linewidth=0)
            else:
                # Left side lit
                x_outer = moon_indicator_x - moon_radius * np.cos(theta)
                y_outer = moon_indicator_y + moon_radius * np.sin(theta)
                
                curve_amount = abs(illumination - 0.5) * 2
                ellipse_width = curve_amount * moon_radius
                
                if illumination > 0.5:
                    x_terminator = moon_indicator_x + ellipse_width * np.cos(theta)
                else:
                    x_terminator = moon_indicator_x - ellipse_width * np.cos(theta)
                y_terminator = moon_indicator_y + moon_radius * np.sin(theta)
                
                x_lit = np.concatenate([x_outer, x_terminator[::-1]])
                y_lit = np.concatenate([y_outer, y_terminator[::-1]])
                
                ax.fill(x_lit, y_lit, color='white', alpha=0.9, zorder=13, linewidth=0)

    # Move up for next box
    current_y += box_height + box_spacing

# Plot date separately in bottom right corner
if fig_aspect > 1:
    date_x = 1.3 * aspect - 0.07
    date_y = -1.3 + 0.05
else:
    date_x = 1.3 - 0.07
    date_y = (-1.3 / aspect) + 0.05

ax.text(date_x, date_y, f"{date_str}",
        color='white', fontsize=12,
        ha='right', va='bottom',
        alpha=0.2)




# ═══════════════════════════════════════════════════════════════════════════
# 13. FINALIZE AND SAVE IMAGE
# ═══════════════════════════════════════════════════════════════════════════

plt.tight_layout()

# Supersample entire image for antialiasing with overscan
supersample_final = 4  # Render at 4x resolution
overscan = 1.04  # 4 % extra on each side
temp_dpi = int(dpi * supersample_final * overscan)

# Save to memory buffer instead of file
buffer = io.BytesIO()
fig.savefig(buffer, format='png', dpi=temp_dpi)
buffer.seek(0)

# Load from buffer, crop and downsample
img = Image.open(buffer)
w, h = img.size

# Calculate crop area (remove overscan)
crop_w = int(width_px * supersample_final)
crop_h = int(height_px * supersample_final)
left = (w - crop_w) // 2
top = (h - crop_h) // 2
cropped = img.crop((left, top, left + crop_w, top + crop_h))

# Downsample to final size with high-quality resampling
final_img = cropped.resize((width_px, height_px), Image.LANCZOS)
final_img.save("solarmap.png")
print("Solar map saved as solarmap.png")

buffer.close()
