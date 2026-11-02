# Solarmap Wallpaper

A Python script that generates a visualization of our solar system as a desktop wallpaper.

![Example Output](solarmap.png)

## Features

- Real-time planetary positions using astronomical calculations
- Orbital trails showing recent planetary motion
- 17 largest objects (until Pluto) visualized and positions calculated
- Asteroid belt and Kuiper belt visualization
- Sunrise/sunset times (dependant on your set location coordinates)
- Customizable resolution and colors

## Requirements

- Python 3.x
- See `requirements.txt` for dependencies

## Installation
```bash
git clone https://github.com/yourusername/solarmap.git
cd solarmap
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
```bash
python solarmap.py
```

The script generates `solarmap.png` in the current directory. By default, the
wallpaper resolution is `1920x1080` and the location is Helsinki Central Railway
Station (`60.17101,24.94148`).

Use `--resolution WIDTHxHEIGHT` to choose an output resolution and
`--geolocation LATITUDE,LONGITUDE` to set the location used for moon and
sunrise/sunset data:

```bash
python solarmap.py --resolution 2560x1440 --geolocation 60.17101,24.94148
```

Both arguments are optional.

## Configuration

Edit the configuration section in `solarmap.py`:

- `width_px`, `height_px` - Output resolution (overridden by `--resolution`)
- `latitude`, `longitude` - Your location (overridden by `--geolocation`)
- `supersample_multiplier` - Antialiasing render scale
- `custom_date` - Set a specific date or use "Now"
- `planet_colors` - Customize planet colors

## License

MIT License - see [LICENSE](LICENSE) file for details
