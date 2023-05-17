import math
import threading
from main import Coordinate, vector

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PhysicsObject:
    _registry = []

    def __init__(self, initial_pos, radius):
        self._registry.append(self)
        self.position_current = initial_pos
        self.position_old = initial_pos
        self.acceleration = Coordinate(0, 0)
        self.radius = radius

    def update_position(self, dt):
        velocity = Coordinate(
            self.position_current.x - self.position_old.x,
            self.position_current.y - self.position_old.y
        )
        self.position_old = self.position_current
        self.position_current = Coordinate(
            self.position_current.x + velocity.x + self.acceleration.x * (dt ** 2),
            self.position_current.y + velocity.y + self.acceleration.y * (dt ** 2)
        )
        self.acceleration = Coordinate(0, 0)

class GridCell:
    def __init__(self):
        self.objects = []

class Grid:
    def __init__(self, width, height, divisions):
        self.width = width
        self.height = height
        self.divisions = divisions
        self.cell_width = width / divisions
        self.cell_height = height / divisions
        self.grid = [[GridCell() for _ in range(divisions)] for _ in range(divisions)]
        self.gravity = vector(0, 10)
    
    def get_cell(self, x, y):
        row = int(x / self.cell_width)
        col = int(y / self.cell_height)
        return self.grid[row][col]
    
    def add_object(self, obj):
        cell = self.get_cell(obj.position_current.x, obj.position_current.y)
        cell.objects.append(obj)

    def update(self, dt):
        for obj in PhysicsObject._registry:
            obj.update_position(dt)
            cell = self.get_cell(obj.position_current.x, obj.position_current.y)
            if obj not in cell.objects:
                for other_obj in cell.objects:
                    if self.check_collision(obj, other_obj):
                        self.resolve_collision(obj, other_obj)
                cell.objects.append(obj)

    def check_collision(self, obj1, obj2):
        distance = math.sqrt(
            (obj1.position_current.x - obj2.position_current.x) ** 2 +
            (obj1.position_current.y - obj2.position_current.y) ** 2
        )
        return distance < obj1.radius + obj2.radius

    def resolve_collision(self, obj1, obj2):
        # Perform collision resolution between obj1 and obj2
        pass
    
    def applyGravity(self):
        for obj in PhysicsObject._registry:
            obj.accelerate(self.gravity)
# Example usage
grid = Grid(800, 600, 10)

# Create objects and add them to the grid
obj1 = PhysicsObject(Coordinate(100, 100), 20)
obj2 = PhysicsObject(Coordinate(200, 200), 30)
grid.add_object(obj1)
grid.add_object(obj2)

# Update the grid and objects over time using multi-threading
dt = 0.1
num_threads = 8  # Specify the number of threads to use

# Create a list to hold the thread objects
threads = []

# Create and start the threads
for _ in range(num_threads):
    thread = threading.Thread(target=grid.update, args=(dt))
    thread.start()
    threads.append(thread)
