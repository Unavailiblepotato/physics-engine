import pygame
import sys
import math
import random

maxballs = 1000

class Coordinate():
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def movement(self, vector):
        xv = vector.dx
        yv = vector.dy
        self.x = self.x + xv
        self.y = self.y + yv
    
    def calc_vector(self, old):
        return vector((self.x - old.x), (self.y - old.y))
    
    def calc_new_pos(self, dis, vel, acc, dt):
        new_x = self.x + dis.x + acc.dx * (dt**2)
        new_y = self.y + dis.y + acc.dy * (dt**2)
        return Coordinate(new_x, new_y)


class vector():
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy
    
    def accelerator(self, acc):
        new_dx = acc.dx + self.dx
        new_dy = acc.dy + self.dy
        return vector(new_dx, new_dy)


class PhysicsObject():
    _registry = []
    
    def __init__(self, initialposx, initialposy, radius, acceleration, color):
        self._registry.append(self)
        self.position_current = Coordinate(initialposx, initialposy)
        self.position_old = self.position_current
        self.acceleration = acceleration
        self.radius = radius
        self.color = color

    def updatePosition(self, dt):
        self.position_change = Coordinate((self.position_current.x - self.position_old.x), (self.position_current.y - self.position_old.y))
        self.velocity = self.position_current.calc_vector(self.position_old)
        self.position_old = self.position_current
        self.position_current = self.position_current.calc_new_pos(self.position_change, self.velocity, self.acceleration, dt)
        self.acceleration = vector(0, 0)
    
    def accelerate(self, acc):
        self.acceleration = self.acceleration.accelerator(acc)
    
    def location(self):
        return (self.position_current.x, self.position_current.y)


class Solver():
    def __init__(self, gravity: int, grid_size: int):
        self.gravity = vector(0, gravity)
        self.grid_size = grid_size
        self.grid = {}
        
    def update(self, dt: int, substeps: int):
        dt_subs = dt / substeps
        self.clearGrid()
        self.updateGrid()
        
        for i in range(substeps):
            self.solveCollisions()

            self.applyBounds()
            self.applyGravity()
            self.updatePositions(dt_subs)
    
    def clearGrid(self):
        self.grid = {}
    
    def updateGrid(self):
        for obj in PhysicsObject._registry:
            grid_x = int(obj.position_current.x / self.grid_size)
            grid_y = int(obj.position_current.y / self.grid_size)
            
            if (grid_x, grid_y) not in self.grid:
                self.grid[(grid_x, grid_y)] = []
                
            self.grid[(grid_x, grid_y)].append(obj)
    
    def getObjectsInGrid(self, grid_x, grid_y):
        objects = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (grid_x + i, grid_y + j) in self.grid:
                    objects.extend(self.grid[(grid_x + i, grid_y + j)])
        
        return objects
    
    def applyGravity(self):
        for obj in PhysicsObject._registry:
            obj.accelerate(self.gravity)

    def updatePositions(self, dt):
        for obj in PhysicsObject._registry:
            obj.updatePosition(dt)
    
    def applyBounds(self):
        center = Coordinate(600, 600)
        constraint_radius = 600
        for obj in PhysicsObject._registry:
            cx = obj.position_current.x
            cy = obj.position_current.y

            v = Coordinate((center.x - cx), (center.y - cy))
            dist = math.sqrt((v.x ** 2) + ((v.y) ** 2))

            if dist > constraint_radius - obj.radius:
                n = Coordinate((v.x / dist), (v.y / dist))
                displacement = constraint_radius - obj.radius
                obj.position_current = Coordinate(
                    center.x - n.x * (displacement),
                    center.y - n.y * (displacement)
                )
    
    def solveCollisions(self):
        for obj in PhysicsObject._registry:
            grid_x = int(obj.position_current.x / self.grid_size)
            grid_y = int(obj.position_current.y / self.grid_size)
            nearby_objects = self.getObjectsInGrid(grid_x, grid_y)
            
            for other_obj in nearby_objects:
                if obj != other_obj:
                    collision_axis = Coordinate(
                        obj.position_current.x - other_obj.position_current.x,
                        obj.position_current.y - other_obj.position_current.y
                    )

                    mindist = obj.radius + other_obj.radius

                    dist = math.sqrt((collision_axis.x ** 2) + (collision_axis.y ** 2))

                    if dist < mindist:
                        n = Coordinate(collision_axis.x / dist, collision_axis.y / dist)
                        delta = mindist - dist

                        obj.position_current = Coordinate(
                            obj.position_current.x + 0.5 * delta * n.x,
                            obj.position_current.y + 0.5 * delta * n.y
                        )
                        other_obj.position_current = Coordinate(
                            other_obj.position_current.x - 0.5 * delta * n.x,
                            other_obj.position_current.y - 0.5 * delta * n.y
                        )


def fps_counter():
    fps = str(int(clock.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("RED"))
    screen.blit(fps_t,(0,0))
    
def ball_count():
    count = (str(len(PhysicsObject._registry)) +"/"+ str(maxballs))
    count_t = font.render(count, 1, pygame.Color("RED"))
    screen.blit(count_t, (0, 25))

def rainbow(t):
    r = math.sin(t)
    g = math.sin(t + 0.33 * 2 * math.pi)
    b = math.sin(t + 0.66 * 2 * math.pi)
    return (255 * r**2, 255*g**2, 255*b**2)
times = 0

pygame.init()
width, height = 1200, 1200
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Render Point as Circle")
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (211, 211, 211)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18, bold=True)
i = 0
c = 0
allpojs = []


while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear the screen
    screen.fill(BLACK)
    pygame.draw.circle(screen, BLACK, (600, 600), 600)

    cb = clock.tick(60)
    times += cb


    if times > 50 and len(PhysicsObject._registry) < maxballs:
        
        obj = PhysicsObject(200 + c, 250, random.randint(3,10), vector(0,0), rainbow(i+1))
        obj = PhysicsObject(1000 - c, 250, random.randint(3,10), vector(0,0), rainbow(i))
        times = 0
        c = c + 30
        if c > 399:
            c = 0


    fps_counter()
    ball_count()

    # Draw the point as a circle
    for obj in PhysicsObject._registry:
        location = obj.location()
        radius = obj.radius
        pygame.draw.circle(screen, obj.color, location, radius, width=1)
        # pygame.draw.circle(screen, WHITE, location, radius, width=1)

    # Update the display
    pygame.display.flip()
    
    Solver(gravity=980, grid_size=20).update(clock.tick(60)/1000, 2)

    i = i + 0.02
    	
    