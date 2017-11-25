"""
TODO:
- abstract out models to draw and identify them automatically
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


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

vertices2 = (
    (-1, -1, 1),
    (-1, -1, -1),
    (-1, -3, 1),
    (-1, -3, -1),
    (-3, -1, 1),
    (-3, -1, -1),
    (-3, -3, 1),
    (-3, -3, -1)
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

def cube(camera, first=True):
    name = 1 if first else 2
    selected = camera['selection'] and camera['selection'] == name
    red = (1, 0, 0)
    white = (1, 1, 1)

    glMatrixMode(GL_MODELVIEW)

    glLoadIdentity();
    glTranslatef(camera['x'], camera['y'], camera['z'])
    glRotatef(camera['xrot'], 1.0, 0.0, 0.0)
    glRotatef(camera['yrot'], 0.0, 1.0, 0.0)
    glRotatef(camera['zrot'], 0.0, 0.0, 1.0)

    glEnable(GL_DEPTH_TEST)

    glDepthFunc(GL_LESS) # only draw nearest surface
    glLoadName(name)
    glBegin(GL_QUADS)
    for surface in surfaces:
        for i, vertex in enumerate(surface):
            glColor3fv(colors[i])
            if first:
                glVertex3fv(vertices[vertex])
            else:
                glVertex3fv(vertices2[vertex])
    glEnd()

    glColor3fv(red if selected else white)

    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            if first:
                glVertex3fv(vertices[vertex])
            else:
                glVertex3fv(vertices2[vertex])
    glEnd()

def cube2(camera):
    cube(camera, False)

def doPicking(pos, width, height, camera):
    """\
    Taken from https://svn.code.sf.net/p/kamaelia/code/trunk/Sketches/CL/Topology3D/Experiments/Cubes.py
    Uses OpenGL picking to determine objects that have been hit by mouse pointer.
    see e.g. OpenGL Redbook
    """

    # object picking
    glSelectBuffer(512)
    glRenderMode(GL_SELECT)
    glInitNames()
    glPushName(0) # TODO: necessary for all objects?

    # prepare matrices
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    viewport = glGetIntegerv(GL_VIEWPORT)
    gluPickMatrix(pos[0], height-pos[1], 1, 1, viewport)
    gluPerspective(45, 1.0*width/height, 1.0, 100.0)

    # "draw" objects in select mode
    glMatrixMode(GL_MODELVIEW) # Always load GL_MODELVIEW before drawing
    glPushMatrix()

    cube(camera)
    cube2(camera)

    # restore matrices
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW) # Always load GL_MODELVIEW before drawing
    glPopMatrix()

    # force completion
    glFlush()

    # process hits
    hits = glRenderMode(GL_RENDER)
    hitlist = []
    hitall = False
    if hitall:
        # list of hit objects
        hitlist = [hit[2][0] for hit in hits]
    else:
        nearest = 4294967295
        if not hits:
            print('hit nothing')
        for hit in hits:
            min_depth, max_depth, names = hit
            print('hit {}'.format(names))
            if hit[0] < nearest:
                nearest = hit[0]
                hitlist = [hit[2][0]]

    return hitlist

def main():
    width, height = (800, 600)
    pygame.init()
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    glutInit()

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # fov degrees, aspect ratio, znear, zfar (clipping planes)
    gluPerspective(45, 1.0*width / height, 1.0, 100.0)

    step = 0.2
    angle = 0.3
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

    camera = {
        'x': 0,
        'y': 0,
        'z': -8,
        'xrot': 0,
        'yrot': 0,
        'zrot': 0,
        'selection': None # TODO: move to global game state
    }

    while True:
        glMatrixMode(GL_PROJECTION)
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
                    hits = doPicking(event.pos, width, height, camera)
                    if hits:
                        camera['selection'] = hits[0]
                    else:
                        camera['selection'] = None
                elif event.button == 4:
                    camera['z'] += step
                elif event.button == 5:
                    camera['z'] -= step

        if nav_keys[K_RIGHT]:
            camera['x'] += step
        if nav_keys[K_LEFT]:
            camera['x'] -= step
        if nav_keys[K_UP]:
            camera['y'] += step
        if nav_keys[K_DOWN]:
            camera['y'] -= step
        if nav_keys[K_INSERT]:
            camera['xrot'] -= angle
        if nav_keys[K_DELETE]:
            camera['xrot'] += angle
        if nav_keys[K_HOME]:
            camera['yrot'] -= angle
        if nav_keys[K_PAGEUP]:
            camera['yrot'] += angle
        if nav_keys[K_PAGEDOWN]:
            camera['zrot'] -= angle
        if nav_keys[K_END]:
            camera['zrot'] += angle

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        cube(camera)
        cube2(camera)
        pygame.display.flip()
        pygame.time.wait(10)

main()
