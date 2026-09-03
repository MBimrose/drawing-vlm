from build123d import *

outer_width = 80.0
outer_depth = 50.0
outer_height = 30.0
wall_thickness = 5.0
socket_width = 60.0
socket_depth = 40.0
socket_height = 20.0
fillet_radius = 2.0
mount_hole_dia = 4.0
mount_hole_spacing = 60.0

base = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)
base = fillet(base.edges(), fillet_radius)

socket = Pos(0, 0, outer_height - socket_height/2) * Box(socket_width, socket_depth, socket_height)
base = base - socket

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, outer_height) * Rot(90, 0, 0) * Cylinder(mount_hole_dia/2, outer_depth)
    base = base - hole

part = base
part.name = "XMountSocket"
export_step(part, "output.step")