from build123d import *

bracket_length = 80.0
bracket_height = 50.0
bracket_thickness = 5.0
cutout_diameter = 30.0
mount_hole_diameter = 6.0
mount_hole_offset = 12.0
rib_width = 4.0
rib_height = 30.0
rib_thickness = 4.0
clearance_hole_diameter = 5.0
clearance_hole_spacing = 20.0
clearance_hole_rows = 2
clearance_hole_cols = 3

result = Box(bracket_length, bracket_thickness, bracket_height)
result = result - Rot(90, 0, 0) * Cylinder(cutout_diameter/2, bracket_thickness + 1)

for x in [-bracket_length/2 + mount_hole_offset, bracket_length/2 - mount_hole_offset]:
    result = result - Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, bracket_thickness + 1)

rib = Box(rib_width, rib_thickness, rib_height)
result = result + Pos(bracket_length/2 + rib_width/2, 0, 0) * rib
result = result + Pos(-bracket_length/2 - rib_width/2, 0, 0) * rib

for i in range(clearance_hole_cols):
    for j in range(clearance_hole_rows):
        x = (i - (clearance_hole_cols-1)/2) * clearance_hole_spacing
        z = (j - (clearance_hole_rows-1)/2) * clearance_hole_spacing
        result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(clearance_hole_diameter/2, bracket_thickness + 1)

part = result
part.name = "bracket"
export_step(part, "output.step")