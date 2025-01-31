import math
import random
import pygame
from equations import calculate_dependent_variables 
import os
import pickle
import noise 
from opensimplex import OpenSimplex
import equations
from functools import lru_cache

# Initialize Pygame
pygame.init()
simplex = OpenSimplex(seed=42)
# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600 
screenheight = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, screenheight))
pygame.display.set_caption("Planet Habitability Simulation")
clock = pygame.time.Clock()

terrain_cache = {}
planet_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 3
# Colors
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
SANDY = (205, 133, 63)
BLUE1 = (70, 130, 180)  # Water
LIGHT_GREEN = (144, 238, 144)  # Sparse plants
BROWN = (139, 69, 19)  # Dry areas

# Font
font = pygame.font.Font(None, 30)

# Independent variables (sliders)
default_variables = {
    "temperature": 20,  # Temperature slider (°C)
    "humidity": 50,     # Humidity slider (%)
    "wind_speed": 10,   # Wind Speed slider (m/s)
    "population": 1000  # Population slider (number of people)
}

# Load saved variables if the file exists
SAVE_FILE = "saved_variables.pkl"
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "rb") as file:
        variables = pickle.load(file)
else:
    variables = default_variables.copy()  # Use default variables if no save file exists

# Save function to persist variables
def save_variables():
    with open(SAVE_FILE, "wb") as file:
        pickle.dump(variables, file)
    print("Variables saved:", variables)

# Sliders configuration (left side for independent variables, right side for dependent)
independent_sliders = [
    {"x": 50, "y": 150, "width": 300, "var": "temperature", "label": "Temperature (°C)"},
    {"x": 50, "y": 250, "width": 300, "var": "humidity", "label": "Humidity (%)"},
    {"x": 50, "y": 350, "width": 300, "var": "wind_speed", "label": "Wind Speed (m/s)"},
    {"x": 50, "y": 450, "width": 300, "var": "population", "label": "Population"}
]


dependent_variables = equations.calculate_dependent_variables(variables)

def draw_slider(x, y, width, value, label):
    value = max(0, min(100, value))  # Ensure value stays within the 0-100 range
    pygame.draw.rect(screen, WHITE, (x, y + 3, width, 6))  # Background bar
    handle_x = x + int((value / 100) * width)
    pygame.draw.circle(screen, (224, 180, 74), (handle_x, y + 5), 8)  # Slider knob
    text = font.render(f"{label}: {value:.2f}", True, WHITE)
    screen.blit(text, (x, y - 25))

center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
previous_terrain = {}

dependent_vars = equations.calculate_dependent_variables(variables)

asi = dependent_variables.get("asi", 0)
solar_intensity = dependent_variables.get("solar_intensity") / 100
@lru_cache(maxsize=None)
def get_terrain_color(noise_value, rainfall, plant_density):
    
    if noise_value < -0.1:
        # Dry regions
        # return BROWN
        transition = rainfall / 100
        return (
            int(BROWN[0] * (1 - transition) + GREEN[0] * transition),
            int(BROWN[1] * (1 - transition) + GREEN[1] * transition),
            int(BROWN[2] * (1 - transition) + GREEN[2] * transition),
        )
    elif noise_value < 0:
        # Sparse plant (plant growth kaam hai)
        transition = rainfall / 100
        return (
            int(SANDY[0] * (1 - transition) + LIGHT_GREEN[0] * transition),
            int(SANDY[1] * (1 - transition) + LIGHT_GREEN[1] * transition),
            int(SANDY[2] * (1 - transition) + LIGHT_GREEN[2] * transition),
        )
    else:
        # Dense vegetation or water (this controls water)
        transition = plant_density / 100
        return (
            int(BROWN[0] * (1 - transition) + BLUE1[0] * transition),
            int(BROWN[1] * (1 - transition) + BLUE1[1] * transition),
            int(BROWN[2] * (1 - transition) + BLUE1[2] * transition),
        )

noise_map = {}

def get_noise_value(x, y):
    if (x, y) in noise_map:
        return noise_map[(x, y)]
    
    noise_value = simplex.noise2(x / 50, y / 50) + 0.5 * simplex.noise2(x / 30, y / 30) + 0.25 * simplex.noise2(x / 10, y / 10)
    
    noise_map[(x, y)] = noise_value
    return noise_value


CLOUD_COLOR = (255, 255, 255, 60)  # White with transparency
cloud_noise_offset = 0  # To animate clouds

def draw_clouds(radius, cloud_density):
    global cloud_noise_offset
    cloud_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    # Adjust the radius of the clouds based on cloud density
    # adjusted_radius = radius * (cloud_density / 100)
    adjusted_radius = min(radius * (cloud_density / 100), planet_radius)  # Ensure cloud radius doesn't exceed planet radius

    # for y in range(center_y - adjusted_radius, center_y + adjusted_radius, 5):
    for y in range(int(center_y - adjusted_radius), int(center_y + adjusted_radius), 5):
        for x in range(int(center_x - adjusted_radius), int(center_x + adjusted_radius), 5):
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if distance <= adjusted_radius:
                noise_value = simplex.noise2((x + cloud_noise_offset) / 80, (y + cloud_noise_offset) / 80)
                if noise_value > 0.2:  # Adjust this threshold for cloud density
                    pygame.draw.circle(cloud_surface, CLOUD_COLOR, (x, y), 5)

    screen.blit(cloud_surface, (0, 0))
    cloud_noise_offset += variables["wind_speed"] * 0.5  # Increasing speed effect

def draw_shading_overlay(radius, asi):
    
    max_darkness = 180  # Max darkness level (0-255)
    darkness = min(max_darkness, int(asi * 1.8))  # Scale darkness with solar intensity

    # Create a semi-transparent dark layer
    shading_surface = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
    pygame.draw.circle(shading_surface, (0, 0, 0, darkness), (radius, radius), radius)

    # Blit the shading overlay onto the planet
    screen.blit(shading_surface, (center_x - radius, center_y - radius))

def solar(radius):
    max_glow_alpha = min(255, 100 + int(solar_intensity * 1.55))

    glow_r = min(255, 240 + int(solar_intensity * 0.3))  
    glow_g = min(255, 200 + int(solar_intensity * 0.3))
    glow_b = min(255, 58 + int(solar_intensity * 0.3))

    glow_color = (glow_r, glow_g, glow_b, max_glow_alpha)

    glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    glow_outer_radius = radius + 50  # Outer edge of the glow
    glow_inner_radius = radius + 20  # Inner edge of the glow (cuts out center)

    # Draw outer glow
    pygame.draw.circle(glow_surface, glow_color, (center_x, center_y), glow_outer_radius)

    # Cut out the center using an inner transparent circle
    pygame.draw.circle(glow_surface, (0, 0, 0, 0), (center_x, center_y), glow_inner_radius)

    screen.blit(glow_surface, (0, 0))

#solar2
def draw_planet(radius, rainfall, plant_density, asi, cloud_density):
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    # # Adjust glow intensity based on solar intensity (0 to 100 mapped to 100 to 255)
    # max_glow_alpha = min(255, 100 + int(asi * 1.55))

    # for i in range(radius + 5, radius + 30, 10):  # Gradient extends beyond the planet
    #     alpha = max(0, max_glow_alpha - (i - radius) * 5)  # Fade effect
    #     glow_color = (255,250,255, alpha)
    #     # (255, 240, 58, alpha)  # Light yellow with transparency
    #     glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    #     pygame.draw.circle(glow_surface, glow_color, (center_x, center_y), i)
    #     screen.blit(glow_surface, (0, 0))

    max_glow_alpha = min(255, 100 + int(asi * 1.55))

    glow_r = min(255, 240 + int(asi * 0.3))  
    glow_g = min(255, 240 + int(asi * 0.3))
    glow_b = min(255, 240 + int(asi * 0.3))

    for i in range(radius + 5, radius + 30, 10):  # Gradient extends beyond the planet
        alpha = max(0, max_glow_alpha - (i - radius) * 5)  # Fade effect
        glow_color = (glow_r, glow_g, glow_b, alpha)
        glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, (center_x, center_y), i)
        screen.blit(glow_surface, (0, 0))
        
    for y in range(center_y - radius, center_y + radius, 3):
        for x in range(center_x - radius, center_x + radius, 3):
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if distance <= radius:
                noise_value = get_noise_value(x, y)  # Performance improvement
                color = get_terrain_color(noise_value, rainfall, plant_density)
                pygame.draw.rect(screen, color, (x, y, 3, 3))

    draw_shading_overlay(radius, asi)
    draw_clouds(radius, cloud_density)

def draw_dynamic_planet(variables):
    
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    planet_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 3  # Ensure planet fits within screen
    rainfall = dependent_variables.get("rainfall_intensity") / 10

    for y in range(center_y - planet_radius, center_y + planet_radius, 3): 
        for x in range(center_x - planet_radius, center_x + planet_radius, 3):  

            distance_from_center = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            if distance_from_center <= planet_radius:
                noise_value = simplex.noise2(x / 50, y / 50) + 0.5 * simplex.noise2(x / 30, y / 30) + 0.25 * simplex.noise2(x / 10, y / 10) 
                terrain_color = get_terrain_color(noise_value, rainfall, plants_density)
                pygame.draw.rect(screen, terrain_color, (x, y, 2, 2))  # Smaller rectangles for smoothness

def draw_dependent_variables(dependent_variables):
    y_offset = 80
    bar_width = 250
    x_offset = SCREEN_WIDTH - 350
    vertical_spacing = 30

    for key, value in dependent_variables.items():
        if y_offset + vertical_spacing > screenheight - 50:
            break
        draw_horizontal_bar(x_offset, y_offset, bar_width, value, key)
        y_offset += vertical_spacing


def draw_horizontal_bar(x, y, width, value, label):
    bar_height = 5
    bar_value = int(min(width, max(0, (value / 100) * width)))
    pygame.draw.rect(screen, GRAY, (x, y, width, bar_height), border_radius=3)
    pygame.draw.rect(screen, (224, 180, 74), (x, y, bar_value, bar_height), border_radius=3)
    text = font.render(f"{label}: {value:.2f}", True, WHITE)
    screen.blit(text, (x, y - 20))


def reset_variables():
    global variables
    variables = default_variables.copy()

def draw_button(x, y, width, height, text, color, hover_color, is_hovering):
    button_color = hover_color if is_hovering else color
    pygame.draw.rect(screen, button_color, (x, y, width, height))
    text_surface = font.render(text, True, WHITE)
    text_x = x + (width - text_surface.get_width()) // 2
    text_y = y + (height - text_surface.get_height()) // 2
    screen.blit(text_surface, (text_x, text_y))

num_stars = 120
stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, screenheight), random.uniform(0.5, 2), random.randint(1, 3)) for _ in range(num_stars)]

def draw_stars():
    for i in range(len(stars)):
        x, y, speed, size = stars[i]
        
        # Twinkle effect: Randomly change star brightness
        if random.random() < 0.08:  # 5% chance to change size each frame
            size = random.randint(1, 3)
        
        pygame.draw.circle(screen, WHITE, (int(x), y), size)

        # Move sideways and wrap around
        x = (x + 1) % SCREEN_WIDTH
        stars[i] = (x, y, speed, size)  # U

# def draw_small_planets():
#     small_planets = [
#         {"x": SCREEN_WIDTH // 7, "y": SCREEN_HEIGHT // 18, "radius": 30, "color": (180, 180, 180)},
#         {"x": 3 * SCREEN_WIDTH // 4, "y": SCREEN_HEIGHT // 4, "radius": 40, "color": (160, 160, 160)}
#     ]

#     for planet in small_planets:
#         pygame.draw.circle(screen, planet["color"], (planet["x"], planet["y"]), planet["radius"])
       



running = True
dragging_slider = None
while running:
    screen.fill(BLACK)
    draw_stars() 
    # solar(200) 
    # draw_small_planets()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for slider in independent_sliders:
                x, y, width, var, _ = slider.values()
                if x <= event.pos[0] <= x + width and y - 10 <= event.pos[1] <= y + 20:
                    dragging_slider = slider
                if 50 <= event.pos[0] <= 170 and 500 <= event.pos[1] <= 540:
                    reset_variables()
                if 200 <= event.pos[0] <= 320 and 500 <= event.pos[1] <= 540:
                    save_variables()

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_slider = None

        elif event.type == pygame.MOUSEMOTION and dragging_slider:
            x, y, width, var, _ = dragging_slider.values()
            relative_x = event.pos[0] - x
            value = max(0, min(100, (relative_x / width) * 100))
            variables[var] = value

    dependent_variables = calculate_dependent_variables(variables)

    # Draw the planet and terrain
    # draw_dynamic_planet(variables)

    dependent_variables = equations.calculate_dependent_variables(variables)
    # rainfall = dependent_variables.get("rainfall_area", 50)  # Update rainfall
    # plants_density = dependent_variables.get("plants_density")  # Update plant density
    plants_density = max(0, min(100, dependent_variables.get("plants_density", 0))) #subtract pollution to make it darker based on pollution levels
    # rainfall_area = max(0, min(100, dependent_variables.get("rainfall_area", 0)))
    rainfall_area = dependent_variables.get("rainfall_area", 0) / 1000000000
    asi = dependent_variables.get("asi") / 100
    solar_intensity = dependent_variables.get("solar_intensity") / 100
    cloud_density = int(dependent_variables.get("cloud_density"))
    # print("rainfall area =", rainfall_area)
    # print("Solar intensity =", solar_intensity)
    rainfall_intensity = dependent_variables.get("rainfall_intensity", 0)
    print("rainfall density =", rainfall_intensity)
    # draw_planet(200, plants_density, variables["humidity"])
    # draw_planet(200, plants_density, rainfall_area, solar_intensity, cloud_density)
    draw_planet(200, plants_density, rainfall_area, asi, cloud_density)
    # Draw sliders and dependent variables
    for slider in independent_sliders:
        draw_slider(slider["x"], slider["y"], slider["width"], variables[slider["var"]], slider["label"])

    draw_dependent_variables(dependent_variables)

    mouse_pos = pygame.mouse.get_pos()
    is_hovering_default = 50 <= mouse_pos[0] <= 170 and 500 <= mouse_pos[1] <= 540
    is_hovering_save = 200 <= mouse_pos[0] <= 320 and 500 <= event.pos[1] <= 540
    draw_button(50, 500, 120, 40, "Default", GRAY, (194, 197, 204), is_hovering_default)
    draw_button(200, 500, 120, 40, "Save", GREEN, (100, 255, 100), is_hovering_save)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()


