from build123d import *
import math

outer_radius = 30
wall_thickness = 5
inner_radius = outer_radius - wall_thickness
length = 80
rib_width = 6
rib_height = 8
rib_count = 12
shaft_diameter = 20
shaft_length = 30
mount_hole_diameter = 10
mount_hole_depth = 20
chamfer_size = 1

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

rib = Pos(outer_radius + rib_width/2, 0, 0) * Box(rib_width, rib_height, length)
for i in range(rib_count):
    angle = i * 360 / rib_count
    result = result + Rot(0, 0, angle) * rib

shaft = Pos(0, 0, -length/2 - shaft_length/2) * Cylinder(shaft_diameter/2, shaft_length)
result = result + shaft

mount_hole = Pos(0, 0, length/2 - mount_hole_depth/2) * Cylinder(mount_hole_diameter/2, mount_hole_depth)
result = result - mount_hole

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")