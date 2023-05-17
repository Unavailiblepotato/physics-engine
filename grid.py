import math

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
    
