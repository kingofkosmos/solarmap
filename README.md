# Solarmap Wallpaper

A Python script that generates a visualization of our solar system as a desktop wallpaper.

![Example Output](solarmap.png)

## Features

- Real-time planetary positions using astronomical calculations
- Orbital trails showing recent planetary motion
- Major moons (Earth's Moon, Jupiter's Galilean moons, Saturn's Titan, etc.)
- Asteroid belt and Kuiper belt visualization
- Moon phase indicator
- Weather forecast (FMI API for Finland)
- Sunrise/sunset times
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

The script generates `solarmap.png` in the current directory. By default, the wallpaper resolution is `1920x1080` and the generated map is in English.

Use `--resolution WIDTHxHEIGHT` to choose an output resolution, and `--language` to choose English (`en`) or Finnish (`fi`):

```bash
python solarmap.py --resolution 2560x1440 --language fi
```

Both arguments are optional. For example, `python solarmap.py --language fi` keeps the default `1920x1080` resolution.

## Configuration

Edit the configuration section in `solarmap.py`:

- `latitude`, `longitude` - Your location for weather/sunrise times
- `custom_date` - Set a specific date or use "Now"
- `planet_colors` - Customize planet colors

## License

MIT License - see [LICENSE](LICENSE) file for details
