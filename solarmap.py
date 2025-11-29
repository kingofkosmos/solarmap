from astronomy import Time, Body, EclipticLongitude, GeoVector, Observer, SearchRiseSet, Direction, Illumination
import math
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import io
import cairosvg
import numpy as np
from matplotlib import font_manager


#Object additions
#TODO: Dwarf planets? (Pluto, Ceres, Haumea, Makemake, Eris)
#TODO: Moons? (Ganymede, Callisto, Io, Europa, Titan, Phobos, Deimos)
#TODO: Comets? (Halley, Hale-Bopp)

#Visual customizations
#TODO: Fix stars cutoff from top and bottom
#TODO: Bottom right corner info:
#       days to next full moon
#TODO: Kuiper belt rotation (practically invisible)
#TODO: Trojans more teardrop shaped
#TODO: Add asteroid belt rotation back
#TODO: Planet labels working with different DPIs
#TODO: Optional background stars
#TODO: Optional colors to rings
#TODO: Optional colors to background
#TODO: Trailing orbits optimization with wedges




# Custom time input
custom_date = None  # Format: "YYYY-MM-DD", set to None for current time

# Orbital trails toggle
show_trails = True
trail_days = 150  # How many days to show in the past

# Planet names toggle
show_planet_names = False  # Set to False to hide names

# Planet name offsets (single value, y will be negative of x)
planet_name_offsets = {'Mercury': 0.02, 'Venus': 0.03, 'Earth': 0.03, 'Mars': 0.025, 'Jupiter': 0.08, 'Saturn': 0.06, 'Uranus': 0.04, 'Neptune': 0.04}

# Color toggle
use_colors = True # Set to False for black & white

# Planet colors
planet_colors = {
    'Sun':      '#FFD700',
    'Mercury':  '#815313',
    'Venus':    '#3CB371',
    'Earth':    '#4A90E2',
    'Mars':     '#CD5C5C',
    'Jupiter':  '#C88B3A',
    'Saturn':   '#FAD5A5',
    'Uranus':   '#4FD0E0',
    'Neptune':  '#4166F5'
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




# Get current time
if custom_date:
    year, month, day = map(int, custom_date.split('-'))
    utc = Time.Make(year, month, day, 0, 0, 0)
else:
    utc = Time.Now()

# Calculate longitudes (angles from the Sun)
longitudes = {planet.name: EclipticLongitude(planet, utc) for planet in planets}




# Canvas setup
#   Set wallpaper resolution
width_px = 2560
height_px = 1440

reference_height = 1440
reference_dpi = 200
dpi = int(height_px * (reference_dpi / reference_height))

fig, ax = plt.subplots(figsize=(1, 1))
fig.set_size_inches(width_px/dpi, height_px/dpi)
fig.patch.set_facecolor('black')
ax.set_facecolor('black')
cx, cy = 0.0, 0.0
r_base = 0.95

# Taskbar offset upwards percentage, so image is not behind taskbar
taskbar_offset = 0.025

# Shift center up by 5% of y-axis range
cy_offset = taskbar_offset * 2.6  # 2.6 is your y-axis range (from -1.3 to 1.3)
cy = cy + cy_offset




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
sun_color = planet_colors['Sun'] if use_colors else None
sun_imagebox = svg_to_imagebox("icons/sun.svg", zoom=0.3, color=sun_color)
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
asteroid_belt_inner = mars_r + (jupiter_r - mars_r) * 0.1
asteroid_belt_outer = mars_r + (jupiter_r - mars_r) * 0.9

#   Generate asteroids
np.random.seed(123)
num_asteroids = 6000
asteroid_angles = np.random.uniform(0, 2 * np.pi, num_asteroids)
asteroid_radii = np.random.uniform(asteroid_belt_inner, asteroid_belt_outer, num_asteroids)

mars_L = longitudes['Mars'] % 360.0
jup_L  = longitudes['Jupiter'] % 360.0

belt_L = mars_L + 0.5 * ((jup_L - mars_L) % 360.0)


rotation = math.radians(belt_L)   # same direction as planets

rotated_angles = asteroid_angles + rotation

asteroid_x = cx + asteroid_radii * np.cos(rotated_angles)
asteroid_y = cy + asteroid_radii * np.sin(rotated_angles)

asteroid_x = cx + asteroid_radii * np.cos(asteroid_angles)
asteroid_y = cy + asteroid_radii * np.sin(asteroid_angles)
asteroid_sizes = np.random.uniform(0.02, 0.15, num_asteroids)  # Smaller

# Fade in from inner edge (fast), fade out at outer edge (slow)
belt_width = asteroid_belt_outer - asteroid_belt_inner
normalized_pos = (asteroid_radii - asteroid_belt_inner) / belt_width  # 0 to 1

# Fast fade in, slow fade out
asteroid_alphas = np.ones(num_asteroids) * 0.4
fade_in_mask = normalized_pos < 0.5
fade_out_mask = normalized_pos > 0.5

asteroid_alphas[fade_in_mask] = (normalized_pos[fade_in_mask] / 0.2) * 0.4
asteroid_alphas[fade_out_mask] = (1 - (normalized_pos[fade_out_mask] - 0.6) / 0.4) * 0.4

ax.scatter(asteroid_x, asteroid_y, s=asteroid_sizes, c='white', alpha=asteroid_alphas, marker='.')




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




# Orbital trails
if show_trails:
    for planet in planets:
        name = planet.name
        r = planet_radii.get(name, 1.0)
        
        # Calculate past positions
        trail_positions_x = []
        trail_positions_y = []
        
        for day_offset in range(0, trail_days + 1, 2):  # Every 2 days for performance
            past_time = utc.AddDays(-day_offset)
            past_L = EclipticLongitude(planet, past_time) % 360.0
            past_theta_deg = 0 - past_L
            past_theta = math.radians(-past_theta_deg)
            past_x = cx + r * math.cos(past_theta)
            past_y = cy + r * math.sin(past_theta)
            trail_positions_x.append(past_x)
            trail_positions_y.append(past_y)
        
        # Plot trail with fading alpha
        num_points = len(trail_positions_x)
        alphas = np.linspace(0.6, 0, num_points)  # Fade from 0.6 to 0
        
        for i in range(num_points - 1):
            ax.plot([trail_positions_x[i], trail_positions_x[i+1]], 
                   [trail_positions_y[i], trail_positions_y[i+1]], 
                   color=planet_colors.get(name, 'white') if use_colors else 'white', alpha=alphas[i], linewidth=1.5)

# Moon trail
moon_trail_days = 15

if show_trails:
    trail_positions_x = []
    trail_positions_y = []
    
    for day_offset in range(0, moon_trail_days + 1, 1):  # Every day
        past_time = utc.AddDays(-day_offset)
        past_moon_vec = GeoVector(Body.Moon, past_time, True)
        past_moon_angle = math.degrees(math.atan2(past_moon_vec.y, past_moon_vec.x))
        past_moon_theta_deg = 0 - past_moon_angle
        past_moon_theta = math.radians(-past_moon_theta_deg)
        past_moon_x = earth_x + earth_ring_r * math.cos(past_moon_theta)
        past_moon_y = earth_y + earth_ring_r * math.sin(past_moon_theta)
        trail_positions_x.append(past_moon_x)
        trail_positions_y.append(past_moon_y)
    
    # Plot trail with fading alpha
    num_points = len(trail_positions_x)
    alphas = np.linspace(0.6, 0, num_points)
    
    for i in range(num_points - 1):
        ax.plot([trail_positions_x[i], trail_positions_x[i+1]], 
               [trail_positions_y[i], trail_positions_y[i+1]], 
               color='white', alpha=alphas[i], linewidth=1.0)




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




# Bottom right corner info
from astronomy import SearchRiseSet, Direction, Observer

# Location coordinates
latitude = 60.06977
longitude = 23.66283

# Get sunrise and sunset for today
observer = Observer(latitude, longitude, 0)
sunrise_time_obj = SearchRiseSet(Body.Sun, observer, Direction.Rise, utc, 1)
sunset_time_obj = SearchRiseSet(Body.Sun, observer, Direction.Set, utc, 1)

# Convert to local time (Helsinki is UTC+2 in winter, UTC+3 in summer)
local_offset_hours = 2  # Adjust to 3 for summer time

# Use Calendar() to get datetime components (returns tuple: year, month, day, hour, minute, second)
sunrise_cal = sunrise_time_obj.Calendar()
sunset_cal = sunset_time_obj.Calendar()

sunrise_hour = (sunrise_cal[3] + local_offset_hours) % 24
sunrise_minute = sunrise_cal[4]

sunset_hour = (sunset_cal[3] + local_offset_hours) % 24
sunset_minute = sunset_cal[4]

sunrise_time = f"{sunrise_hour:02d}:{sunrise_minute:02d}"
sunset_time = f"{sunset_hour:02d}:{sunset_minute:02d}"

# Calculate daylight hours
daylight_minutes = (sunset_hour * 60 + sunset_minute) - (sunrise_hour * 60 + sunrise_minute)
daylight_hours = daylight_minutes // 60
daylight_mins = daylight_minutes % 60


# Get moon phase
illum = Illumination(Body.Moon, utc)
phase_angle = illum.phase_angle  # 0° = new moon, 180° = full moon
illumination = illum.phase_fraction

# Determine phase name
if phase_angle < 22.5 or phase_angle >= 337.5:
    phase_name = "New Moon"
elif phase_angle < 67.5:
    phase_name = "Waxing crescent"
elif phase_angle < 112.5:
    phase_name = "First quarter"
elif phase_angle < 157.5:
    phase_name = "Waxing gibbous"
elif phase_angle < 202.5:
    phase_name = "Full moon"
elif phase_angle < 247.5:
    phase_name = "Waning gibbous"
elif phase_angle < 292.5:
    phase_name = "Last quarter"
else:
    phase_name = "Waning crescent"

# Position for moon phase circle
moon_indicator_x = text_x - 0.05
moon_indicator_y = text_y + 0.25
moon_radius = 0.035

# Draw dark gray base circle
ax.add_patch(plt.Circle((moon_indicator_x, moon_indicator_y), moon_radius, 
                        fill=True, color='#404040', alpha=0.9, zorder=10))

# Draw illuminated part with proper terminator
theta = np.linspace(0, 2*np.pi, 200)

if phase_angle < 180:  # Waxing
    # Right semicircle (always lit during waxing)
    mask_right = np.cos(theta) >= 0
    # Left side varies with phase
    k = np.cos(np.radians(phase_angle))  # -1 (new) to 1 (full)
    
    x_coords = []
    y_coords = []
    for i, t in enumerate(theta):
        cos_t = np.cos(t)
        sin_t = np.sin(t)
        if cos_t >= 0:  # Right side
            x_coords.append(moon_indicator_x + moon_radius * cos_t)
            y_coords.append(moon_indicator_y + moon_radius * sin_t)
        else:  # Left side - ellipse
            x_coords.append(moon_indicator_x + moon_radius * k * cos_t)
            y_coords.append(moon_indicator_y + moon_radius * sin_t)
    
    ax.fill(x_coords, y_coords, color='white', alpha=0.9, zorder=11)
    
else:  # Waning
    # Left semicircle (always lit during waning)
    k = np.cos(np.radians(180 - phase_angle))  # 1 (full) to -1 (new)
    
    x_coords = []
    y_coords = []
    for i, t in enumerate(theta):
        cos_t = np.cos(t)
        sin_t = np.sin(t)
        if cos_t <= 0:  # Left side
            x_coords.append(moon_indicator_x + moon_radius * cos_t)
            y_coords.append(moon_indicator_y + moon_radius * sin_t)
        else:  # Right side - ellipse
            x_coords.append(moon_indicator_x + moon_radius * k * cos_t)
            y_coords.append(moon_indicator_y + moon_radius * sin_t)
    
    ax.fill(x_coords, y_coords, color='white', alpha=0.9, zorder=11)


# Calculate text position (bottom right with taskbar offset)
fig_width, fig_height = fig.get_size_inches()
aspect = fig_width / fig_height

if aspect > 1:
    text_x = 1.3 * aspect - 0.05
    text_y = -1.3 + (taskbar_offset * 2.6) + 0.1
else:
    text_x = 1.3 - 0.05
    text_y = (-1.3 / aspect) + (taskbar_offset * 2.6) + 0.1

# Add text
info_text = f"{phase_name}\n☀ {sunrise_time}  🌙 {sunset_time}\nDaylight: {daylight_hours} h {daylight_mins} min"
ax.text(text_x, text_y, info_text,
        color='white', fontsize=10,
        ha='right', va='bottom',
        alpha=0.7,
        fontproperties=font_manager.FontProperties(family='Segoe UI Emoji'))




# Save and show
plt.tight_layout()
fig.savefig("solarmap.png", dpi=dpi)
plt.show()
