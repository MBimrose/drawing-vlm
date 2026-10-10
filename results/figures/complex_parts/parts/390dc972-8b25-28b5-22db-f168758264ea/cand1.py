from build123d import *

outer_diameter = 40.0
inner_diameter = 30.0
length = 60.0
flange_thickness = 10.0
flange_diameter = 60.0
chamfer_size = 2.0
mount_hole_diameter = 4.0
mount_hole_count = 4
mount_hole_radius = (flange_diameter/2 + outer_diameter/2)/2
side_hole_diameter = 6.0
side_hole_offset = 12.0

body = Pos(0, 0, length/2) * Cylinder(outer_diameter/2, length)
flange = Pos(0, 0, length + flange_thickness/2) * Cylinder(flange_diameter/2, flange_thickness)
result = body + flange

bore = Pos(0, 0, (length + flange_thickness)/2) * Cylinder(inner_diameter/2, length + flange_thickness)
result = result - bore

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

import math
for i in range(mount_hole_count):
    a = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(a)
    py = mount_hole_radius * math.sin(a)
    result = result - Pos(px, py, length + flange_thickness/2) * Cylinder(mount_hole_diameter/2, flange_thickness + 2)

side_hole = Pos(0, side_hole_offset, length/2) * Rot(0, 90, 0) * Cylinder(side_hole_diameter/2, outer_diameter + 2)
result = result - side_hole

part = result
part.name = "flanged_tube_with_holes"
export_step(part, "output.step")