import math

# Constants
k1 = 0.8  # Solar Intensity multiplier
k2 = 1.5  # Photosynthesis to Oxygen multiplier
k3 = 0.05  # Population effect on Oxygen
k4 = 0.03  # Population effect on Carbon Dioxide
k5 = 0.02  # Photosynthesis effect on Carbon Dioxide
k6 = 0.1  # Rainfall Intensity multiplier
k7 = 0.01  # Solar Intensity effect on UV Index
k8 = 0.02  # Population effect on Pollution
k9 = 0.005  # Wind effect on Pollution
k10 = 0.05  # Crop Yield multiplier
k11 = 0.7  # Rainfall effect on Water Resources
k12 = 0.2  # Wind effect on Water Resources
k13 = 0.01  # Population effect on Water Resources
T_min = 20  # Minimum temperature for Crop Yield

def calculate_dependent_variables(variables):
    """
    Calculate dependent variables based on independent variables.
    :param variables: Dictionary containing independent variables.
    :return: Dictionary containing dependent variables.
    """
    # Independent variables
    temperature = variables["temperature"]
    humidity = variables["humidity"]
    wind_speed = variables["wind_speed"]
    population = variables["population"]

    # Dependent variables calculations
    solar_intensity = k1 * humidity * temperature
    cloud_density = (humidity**2) / max(temperature, 1)  # Avoid division by zero
    photosynthesis = solar_intensity * math.cos(math.radians(cloud_density))
    # photosynthesis = solar_intensity * (0.5 + 0.5 * math.cos((cloud_density)))
    oxygen = k2 * photosynthesis - k3 * population
    carbon_dioxide = k4 * population - k5 * photosynthesis
    # carbon_dioxide = 1.5 * population - 0.005 * photosynthesis
    asi = math.sqrt(oxygen**2 + carbon_dioxide**2)
    rainfall_intensity = k6 * humidity * temperature * (1 + wind_speed / 100)
    radius_of_wet_ground = rainfall_intensity * wind_speed
    rainfall_area = math.pi * radius_of_wet_ground**2
    # solar_intensity_slope = cloud_density + 1 / max(cloud_density, 1)  # Avoid division by zero
    power = solar_intensity**2 + wind_speed
    uv_index = k7 * solar_intensity * temperature
    pollution = k8 * population - k9 * wind_speed
    health_risk = math.log(max(0.0001, 1 + uv_index * pollution))
    plants_density = photosynthesis / 10
    crop_yield = k10 * (temperature - T_min) * humidity * plants_density if temperature > T_min else 0
    hunger = population / max(crop_yield, 1)  # Avoid division by zero
    water_resources = k11 * rainfall_intensity + k12 * wind_speed - k13 * population
    thirst = population / max(rainfall_area, 1)  # Avoid division by zero

    # Return dependent variables
    return {
        "solar_intensity": solar_intensity,
        "cloud_density": cloud_density,
        "photosynthesis": int(photosynthesis),
        "oxygen": oxygen,  # Ensure non-negative oxygen
        "carbon_dioxide": carbon_dioxide,  # Ensure non-negative carbon dioxide
        "asi": asi,
        "rainfall_intensity": rainfall_intensity,
        "radius_of_wet_ground": radius_of_wet_ground,
        "rainfall_area": rainfall_area,
        # "solar_intensity_slope": solar_intensity_slope,
        "power": power,
        "uv_index": uv_index,
        "pollution": pollution,
        "health_risk": health_risk,
        "plants_density": plants_density,
        "crop_yield": crop_yield,
        "hunger": hunger,
        "water_resources": water_resources,
        "thirst": thirst
    }

