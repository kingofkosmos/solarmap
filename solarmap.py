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

#TODO: Supersample multiplier to configuration
#TODO: All magic numbers to configuration
#TODO: Automatic wallpaper generation in Github Actions?
#TODO: Weather info
##      Rain/sleet/snow chance? Cloudiness? Sun UV strength?
##      Northern lights forecast?
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
trail_days = 150  # How long the trails are in days

# Planet colors
planet_colors = {
    'Sun':          '#FFF75E',
    'Mercury':      '#815313',
    'Venus':        '#3CB371',
    'Earth_ocean':  '#4A90E2',
    'Earth_land':   "#013C28",
    'Mars':         '#CD5C5C',
    'Jupiter':      '#C88B3A',
    'Saturn':       '#FAD5A5',
    'Uranus':       '#4FD0E0',
    'Neptune':      '#4166F5',
    'Pluto':        '#A0826D'
}




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




# ═══════════════════════════════════════════════════════════════════════════
# 4. WEATHER FORECAST FROM FMI (ONLINE)
# ═══════════════════════════════════════════════════════════════════════════

def get_tomorrow_forecast(lat, lon):
    """Get tomorrow's min/max/avg temperature from FMI."""
    import requests
    import xml.etree.ElementTree as ET
    from datetime import datetime, timedelta
    
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=0, minute=0).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time = tomorrow.replace(hour=23, minute=59).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    url = "https://opendata.fmi.fi/wfs"
    params = {
        'service': 'WFS',
        'version': '2.0.0',
        'request': 'getFeature',
        'storedquery_id': 'fmi::forecast::harmonie::surface::point::multipointcoverage',
        'latlon': f'{lat},{lon}',
        'parameters': 'temperature',
        'starttime': start_time,
        'endtime': end_time
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"FMI connection status: {response.status_code}")
        
        if response.status_code != 200:
            return None, None, None
        
        root = ET.fromstring(response.content)
        
        temps = []
        for elem in root.iter():
            if 'doubleOrNilReasonTupleList' in elem.tag:
                values = elem.text.strip().split()
                temps.extend([float(v) for v in values if v not in ['NaN', '']])

        if temps:
            avg_temp = sum(temps) / len(temps)
            return min(temps), max(temps), avg_temp
        else:
            print("No temps found!")

    except Exception as e:
        print(f"Exception: {e}")
    
    return None, None, None

# Get weather forecast
min_temp, max_temp, avg_temp = get_tomorrow_forecast(latitude, longitude)
weather_line = f"\nSää huomenna:\nmin: {min_temp:+.1f} °C maks: {max_temp:+.1f} °C\nka: {avg_temp:+.1f} °C\n".replace('.', ',') if min_temp is not None else ""

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
        plt.Circle((cx, cy), r, fill=False, linewidth=0.4, color='white', linestyle=(0, (10, 10))))

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
        
        # Black areas (landmasses) → green, White pixels (ocean) → blue
        ocean_rgb = hex2color(planet_colors['Earth_ocean'])
        land_rgb = hex2color(planet_colors['Earth_land'])
        
        # Mask for black vs white pixels
        is_black = image[:, :, :3].max(axis=2) < 0.5  # Black = landmasses
        
        # Apply colors
        for i in range(3):
            image[:, :, i] = np.where(is_black, land_rgb[i], ocean_rgb[i])
        
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
    plot_fading_arc(ax, cx, cy, r, theta_start, theta_end, trail_color, linewidth=1.5, n=100)




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
        phase_name = "Täysikuu"  # "Full moon"
    elif illumination < 0.01:
        phase_name = "Uusikuu"  # "New moon"
    elif is_waxing: # Waxing, growing brighter
        if illumination > 0.55:
            phase_name = "Kasvava kupera kuu"  # "Waxing gibbous"
        elif illumination > 0.45:
            phase_name = "Puolikuu (ensimmäinen neljännes)"  # "First quarter"
        else:
            phase_name = "Kasvava sirppi"  # "Waxing crescent"
    else:  # Waning, getting darker
        if illumination > 0.55:
            phase_name = "Vähenevä kupera kuu"  # "Waning gibbous"
        elif illumination > 0.45:
            phase_name = "Puolikuu (viimeinen neljännes)"  # "Last quarter"
        else:
            phase_name = "Vähenevä sirppi"  # "Waning crescent"

    # Search for next full moon (phase 180°) within next 30 days
    next_full_moon = SearchMoonPhase(180, utc, 30)
    days_to_full = next_full_moon.ut - utc.ut  # Difference in days




# ═══════════════════════════════════════════════════════════════════════════
# 12.2 PLOT INFO TEXT
# ═══════════════════════════════════════════════════════════════════════════

    cal = utc.Calendar()
    date_str = f"{int(cal[0])}-{int(cal[1]):02d}-{int(cal[2]):02d}"

    info_text = (
        f"{phase_name}\n"
        f"{days_to_full:.0f} pv täysikuuhun\n"
        f"{weather_line}"
        f"\n"
        f"Päivänvalo huomenna:\n"
        f"klo {sunrise_time} - {sunset_time}\n"
        f"{daylight_hours} t {daylight_mins} min"
    )

    # Count lines to position moon indicator at first line
    num_lines = info_text.count('\n')+2
    line_height = 0.04  # Adjust if needed for your text size

    # Position for moon phase circle (aligned with first line)
    moon_indicator_x = text_x - 0.04
    moon_indicator_y = text_y + (num_lines - 1) * line_height  # Top line position
    moon_radius = 0.035

    # Draw dark gray base circle
    ax.add_patch(plt.Circle((moon_indicator_x, moon_indicator_y), moon_radius, fill=True, color='#404040', alpha=0.9, zorder=10))

    # Draw illuminated part
    if illumination > 0.01:
        theta = np.linspace(np.pi/2, -np.pi/2, 100)
        
        if is_waxing:
            # Right side lit
            x_outer = moon_indicator_x + moon_radius * np.cos(theta)
            y_outer = moon_indicator_y + moon_radius * np.sin(theta)
            
            terminator_x_pos = moon_radius - (2 * illumination * moon_radius)
            curve_amount = abs(illumination - 0.5) * 2
            ellipse_width = curve_amount * moon_radius
            
            if illumination < 0.5:
                x_terminator = moon_indicator_x + ellipse_width * np.cos(theta)
            else:
                x_terminator = moon_indicator_x - ellipse_width * np.cos(theta)
            y_terminator = moon_indicator_y + moon_radius * np.sin(theta)
            
            x_lit = np.concatenate([x_outer, x_terminator[::-1]])
            y_lit = np.concatenate([y_outer, y_terminator[::-1]])
            
            ax.fill(x_lit, y_lit, color='white', alpha=0.9, zorder=11, linewidth=0)

        else:
            # Left side lit
            x_outer = moon_indicator_x - moon_radius * np.cos(theta)
            y_outer = moon_indicator_y + moon_radius * np.sin(theta)
            
            terminator_x_pos = -moon_radius + (2 * illumination * moon_radius)
            curve_amount = abs(illumination - 0.5) * 2
            ellipse_width = curve_amount * moon_radius
            
            if illumination > 0.5:
                x_terminator = moon_indicator_x + ellipse_width * np.cos(theta)
            else:
                x_terminator = moon_indicator_x - ellipse_width * np.cos(theta)
            y_terminator = moon_indicator_y + moon_radius * np.sin(theta)
            
            x_lit = np.concatenate([x_outer, x_terminator[::-1]])
            y_lit = np.concatenate([y_outer, y_terminator[::-1]])
            
            ax.fill(x_lit, y_lit, color='white', alpha=0.9, zorder=11, linewidth=0)

    # Plot info text
    ax.text(text_x, text_y, info_text,
            color='white', fontsize=12,
            ha='right', va='bottom',
            alpha=0.7)

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
            alpha=0.3)



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