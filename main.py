import pygame
from equations import calculate_dependent_variables

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1300, 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Planet Habitability Simulation")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Font
font = pygame.font.Font(None, 30)

# Independent variables (sliders)
variables = {
    "temperature": 20,  # Temperature slider (°C)
    "humidity": 50,     # Humidity slider (%)
    "wind_speed": 10,   # Wind Speed slider (m/s)
    "population": 1000  # Population slider (number of people)
}

# Dependent variables (calculated dynamically)
dependent_variables = {}

# Sliders configuration (left side for independent variables, right side for dependent)
independent_sliders = [
    {"x": 50, "y": 100, "width": 300, "var": "temperature", "label": "Temperature (°C)"},
    {"x": 50, "y": 200, "width": 300, "var": "humidity", "label": "Humidity (%)"},
    {"x": 50, "y": 300, "width": 300, "var": "wind_speed", "label": "Wind Speed (m/s)"},
    {"x": 50, "y": 400, "width": 300, "var": "population", "label": "Population"}
]

# Helper Functions
def draw_slider(x, y, width, value, label):
    pygame.draw.rect(screen, WHITE, (x, y, width, 10))
    pygame.draw.circle(screen, GREEN, (x + int((value / 100) * width), y + 5), 10)
    text = font.render(f"{label}: {value:.2f}", True, WHITE)
    screen.blit(text, (x, y - 25))

# Helper function for drawing thinner horizontal bars
def draw_horizontal_bar(x, y, width, value, label):
    bar_height = 8  # Very thin bar height
    bar_value = min(width, max(0, int(value * 1.5)))  # Adjust bar width based on value
    pygame.draw.rect(screen, BLUE, (x-60, y, bar_value, bar_height))  # Draw the horizontal bar
    text = font.render(f"{label}: {value:.2f}", True, WHITE)
    screen.blit(text, (x + bar_value + 10, y))  # Place label next to the bar

# Start Y position for dependent variables
y_offset = 100
bar_width = 200  # Make bar width a bit wider to ensure readability
x_offset = SCREEN_WIDTH - 600
# Adjust the vertical spacing for bars
vertical_spacing = 15  # A bit more space between bars

# Loop through dependent variables and draw each one
for idx, (key, value) in enumerate(dependent_variables.items()):
    if y_offset + vertical_spacing > SCREEN_HEIGHT:
        break  # Stop drawing if we exceed screen height
    
    # Draw each bar with reduced dimensions
    draw_horizontal_bar(x_offset, y_offset, bar_width, value, key)
    
    # Increment the Y offset for the next dependent variable
    y_offset += vertical_spacing  # Increase spacing between bars

# If necessary, we can implement scrolling here for longer lists

def draw_simulation():
    """
    Draw the simulation in the center.
    """
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    pygame.draw.circle(screen, GREEN, (center_x, center_y), 100)
    text = font.render("Simulation Area", True, BLACK)
    screen.blit(text, (center_x - 60, center_y - 10))


# Main Simulation Loop
running = True
dragging_slider = None
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for slider in independent_sliders:
                x, y, width, var, _ = slider.values()
                if x <= event.pos[0] <= x + width and y <= event.pos[1] <= y + 20:
                    dragging_slider = slider

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_slider = None

        elif event.type == pygame.MOUSEMOTION and dragging_slider:
            x, y, width, var, _ = dragging_slider.values()
            relative_x = event.pos[0] - x
            value = max(0, min(100, (relative_x / width) * 100))
            variables[var] = value

    # Update dependent variables
    dependent_variables = calculate_dependent_variables(variables)

    # Draw elements
    draw_simulation()  # Center: simulation

    # Draw independent variable sliders (left side)
    for slider in independent_sliders:
        draw_slider(slider["x"], slider["y"], slider["width"], variables[slider["var"]], slider["label"])

    # Draw dependent variable horizontal bars (right side)
    y_offset = 100
    for key, value in dependent_variables.items():
        draw_horizontal_bar(SCREEN_WIDTH - 350, y_offset, 300, value, key)
        y_offset += 40  # Spacing between bars

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
