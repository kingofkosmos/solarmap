from astronomy import Time, Body, EclipticLongitude

# List of planet names as strings
planets = [Body.Mercury, Body.Venus, Body.Earth, Body.Mars, Body.Jupiter, Body.Saturn, Body.Uranus, Body.Neptune]

# Get current date and time
utc = Time.Now()

#  Calculate and print heliocentric longitudes for each planet
print("Planetary heliocentric longitudes:")
for planet in planets:
    lon = EclipticLongitude(planet, utc)
    print(f"{planet.name}: {lon:.2f}°")
