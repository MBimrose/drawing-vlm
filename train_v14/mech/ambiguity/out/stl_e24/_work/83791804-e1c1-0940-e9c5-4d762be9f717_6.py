from build123d import *

bracket_width = 80.0
bracket_height = 50.0
bracket_thickness = 8.0
bearing_diameter = 30.0
bearing_depth = 12.0
mount_hole_diameter = 5.0
mount_hole_offset = 12.0
through_hole_diameter = 6.0
through_hole_spacing = 20.0
rib_thickness = 4.0
rib_height = 30.0

result = Box(bracket_width, bracket_thickness, bracket_height)
result = result - Rot(90, 0, 0) * Cylinder(bearing_diameter/2, bearing_depth)

mount_points = [
    (-bracket_width/2 + mount_hole_offset, -bracket_height/2 + mount_hole_offset),
    ( bracket_width/2 - mount_hole_offset, -bracket_height/2 + mount_hole_offset),
    (-bracket_width/2 + mount_hole_offset,  bracket_height/2 - mount_hole_offset),
    ( bracket_width/2 - mount_hole_offset,  bracket_height/2 - mount_hole_offset)
]
for x, z in mount_points:
    result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, bracket_thickness)

through_points = [
    (-through_hole_spacing, 0),
    (0, 0),
    (through_hole_spacing, 0)
]
for x, z in through_points:
    result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(through_hole_diameter/2, bracket_thickness)

rib = Box(rib_thickness, rib_thickness, rib_height)
result = result + Pos(bracket_width/2 + rib_thickness/2, -bracket_thickness/2 - rib_thickness/2, 0) * rib
result = result + Pos(-bracket_width/2 - rib_thickness/2, -bracket_thickness/2 - rib_thickness/2, 0) * rib

part = result
part.name = "bracket"
export_step(part, "output.step")