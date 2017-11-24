import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

vertices = (
    (1, 1, 1),
    (1, 1, -1),
    (1, -1, 1),
    (1, -1, -1),
    (-1, 1, 1),
    (-1, 1, -1),
    (-1, -1, 1),
    (-1, -1, -1)
)

edges = (
    (0, 1),
    (0, 2),
    (0, 4),
    (1, 3),
    (1, 5),
    (2, 3),
    (2, 6),
    (3, 7),
    (4, 5),
    (4, 6),
    (5, 7),
    (6, 7)
)

surfaces = (
    (0, 1, 3, 2),
    (4, 5, 7, 6),
    (0, 1, 5, 4),
    (2, 3, 7, 6),
    (0, 2, 6, 4),
    (1, 3, 7, 5)
)

colors = (
    (0, 0, 1),
    (1, 1, 1),
    (0, 1, 0),
    (0, 1, 1),
    (0, 0, 1),
    (1, 1, 1),
    (0, 1, 0),
    (0, 1, 1),
)

def cube():
    glBegin(GL_QUADS)
    for surface in surfaces:
        for i, vertex in enumerate(surface):
            glColor3fv(colors[i])
            glVertex3fv(vertices[vertex])
    glEnd()

    glColor3fv(colors[1])

    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def get_coords(window_coords):
    x, y = window_coords
    z = glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
    print gluUnProject(x, y, z) # TODO: y value has to be transformed?

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    # fov degrees, aspect ratio, znear, zfar (clipping planes)
    gluPerspective(30, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -8)

    step = 0.2
    angle = 3
    nav_keys = {
        K_RIGHT: False, # right,
        K_LEFT: False, # left,
        K_UP: False, # up,
        K_DOWN: False, # down,
        K_INSERT: False, # rot_xr,
        K_DELETE: False, # rot_xl,
        K_HOME: False, # rot_yr,
        K_PAGEUP: False, # rot_yl,
        K_PAGEDOWN: False, # rot_zr,
        K_END: False, # rot_yl
    }

    # print glRenderMode(GL_SELECT)
    # nameStack = glRenderMode(GL_RENDER)
    # print nameStack

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()
                elif event.key in nav_keys:
                    nav_keys[event.key] = True
            elif event.type == pygame.KEYUP:
                if event.key in nav_keys:
                    nav_keys[event.key] = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    get_coords(event.pos)
                elif event.button == 4:
                    glTranslatef(0.0, 0.0, step)
                elif event.button == 5:
                    glTranslatef(0.0, 0.0, -step)

        if nav_keys[K_RIGHT]:
            glTranslatef(step, 0.0, 0.0)
        if nav_keys[K_LEFT]:
            glTranslatef(-step, 0.0, 0.0)
        if nav_keys[K_UP]:
            glTranslatef(0.0, step, 0.0)
        if nav_keys[K_DOWN]:
            glTranslatef(0.0, -step, 0.0)
        if nav_keys[K_INSERT]:
            glRotatef(1, angle, 0, 0)
        if nav_keys[K_DELETE]:
            glRotatef(1, -angle, 0, 0)
        if nav_keys[K_HOME]:
            glRotatef(1, 0, angle, 0)
        if nav_keys[K_PAGEUP]:
            glRotatef(1, 0, -angle, 0)
        if nav_keys[K_PAGEDOWN]:
            glRotatef(1, 0, 0, -angle)
        if nav_keys[K_END]:
            glRotatef(1, 0, 0, angle)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        cube()
        pygame.display.flip()
        pygame.time.wait(10)

main()
