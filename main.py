import pygame
import sys
import math
from datetime import datetime
import random
import threading

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
        self.acceleration = vector(0,0)
    
    def accelerate(self, acc):
        self.acceleration = self.acceleration.accelerator(acc)
    
    def location(self):
        return (self.position_current.x, self.position_current.y)


        

class Solver():
    def __init__(self, gravity:int):
        self.gravity = vector(0, gravity)
        
        
    def update(self, dt:int, substeps:int):
        for i in range(1, substeps):
            
            self.dt_subs = dt/substeps
            # self.applybounds()
            # self.solveCollisions()
            # self.applyGravity()
            # self.updatePositions(self.dt_subs)
            t1 = threading.Thread(target=self.applybounds(), args=(10,))
            t2 = threading.Thread(target=self.solveCollisions(), args=(10,))
            t3 = threading.Thread(target=self.applyGravity(), args=(10,))
            t4 = threading.Thread(target=self.updatePositions(self.dt_subs), args=(10,))
            t1.start()
            t2.start()
            t3.start()
            t4.start()
            t1.join()
            t2.join()
            t3.join()
            t4.join()


    def applyGravity(self):
        for obj in PhysicsObject._registry:
            obj.accelerate(self.gravity)

    def updatePositions(self, dt):
        for obj in PhysicsObject._registry:
            obj.updatePosition(dt)
    
    def applybounds(self):
        self.center = Coordinate(400, 250)
        self.constraint_radius = 250
        for obj in PhysicsObject._registry:
            self.cx = obj.position_current.x
            self.cy = obj.position_current.y


            self.v = Coordinate((self.center.x - self.cx), (self.center.y - self.cy))
            self.dist = math.sqrt((self.v.x**2) + ((self.v.y)**2))

            if self.dist > self.constraint_radius - obj.radius:


                self.n = Coordinate((self.v.x/self.dist),(self.v.y/self.dist))
                self.displacement = self.constraint_radius - obj.radius
                obj.position_current = Coordinate(self.center.x - self.n.x*(self.displacement), self.center.y - self.n.y*(self.displacement))   

    def solveCollisions(self):
        self.count = len(PhysicsObject._registry)
        for i in range(0, self.count):
            for k in range(i + 1, self.count):
                self.object_1 = PhysicsObject._registry[i]
                self.object_2 = PhysicsObject._registry[k]

                self.collision_axis = Coordinate(self.object_1.position_current.x - self.object_2.position_current.x, self.object_1.position_current.y - self.object_2.position_current.y)

                self.mindist = self.object_1.radius + self.object_2.radius

                self.dist = math.sqrt((self.collision_axis.x**2) + (self.collision_axis.y**2))

                if self.dist < self.mindist:
                    self.n = Coordinate(self.collision_axis.x/self.dist, self.collision_axis.y/self.dist)
                    self.delta = self.mindist - self.dist

                    self.object_1.position_current = Coordinate((self.object_1.position_current.x + (0.5 * self.delta * self.n.x)), (self.object_1.position_current.y + (0.5 * self.delta * self.n.y)))
                    self.object_2.position_current = Coordinate((self.object_2.position_current.x - (0.5 * self.delta * self.n.x)), (self.object_2.position_current.y - (0.5 * self.delta * self.n.y)))



pygame.init()
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Render Point as Circle")
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
allpojs = []
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial" , 18 , bold = True)
i = 0
b = PhysicsObject(400, 150, 5, vector(2, 5), WHITE)
def fps_counter():
    fps = str(int(clock.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("RED"))
    screen.blit(fps_t,(0,0))

def rainbow(t):
    r = math.sin(t)
    g = math.sin(t + 0.33 * 2 * math.pi)
    b = math.sin(t + 0.66 * 2 * math.pi)
    return (255 * r**2, 255*g**2, 255*b**2)
times = 0

c = 0

while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


    # Clear the screen
    screen.fill(WHITE)
    pygame.draw.circle(screen, BLACK, (400,250), 250)

    cb = clock.tick() 

    times += cb
    print(times)
            
    if times > 2 and len(allpojs) < 200:
        obj = PhysicsObject(275 + c, 250, 5, vector(2, 500), rainbow(i))
        allpojs.append(obj)
        times = 0
        c = c + 10
        if c > 250:
            c = 0

        # Draw the point as a circle
    for obj in PhysicsObject._registry:
        location = obj.location()
        radius = obj.radius
        pygame.draw.circle(screen, obj.color, location, radius)

    pygame.draw.circle(screen, b.color, b.location(), b.radius)
    
    print(clock.get_fps())
    clock.tick(60)

    # Update the display
    pygame.display.flip()

    Solver(10).update(0.01*clock.tick(60), 2)

    i = i + 0.05

