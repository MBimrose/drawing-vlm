from build123d import *

bracket_width = 80.0
bracket_height = 50.0
bracket_thickness = 5.0
cutout_diameter = 30.0
mount_hole_diameter = 5.0
mount_hole_spacing_x = 20.0
mount_hole_spacing_y = 12.0
mount_hole_rows = 2
mount_hole_cols = 4
side_hole_diameter = 6.0
side_hole_offset = 10.0
rib_thickness = 4.0
rib_height = 30.0
chamfer_size = 0.8

result = Box(bracket_width, bracket_thickness, bracket_height)
result = result - Rot(90, 0, 0) * Cylinder(cutout_diameter/2, bracket_thickness + 1)

for i in range(mount_hole_cols):
    for j in range(mount_hole_rows):
        x = (i - (mount_hole_cols - 1) / 2) * mount_hole_spacing_x
        z = (j - (mount_hole_rows - 1) / 2) * mount_hole_spacing_y
        result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, bracket_thickness + 1)

for x in [-bracket_width/2 + side_hole_offset, bracket_width/2 - side_hole_offset]:
    result = result - Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(side_hole_diameter/2, bracket_thickness + 1)

result = result + Pos(bracket_width/2 + rib_thickness/2, -bracket_height/2 + rib_height/2, 0) * Box(rib_thickness, rib_thickness, rib_height)
result = result + Pos(-bracket_width/2 - rib_thickness/2, -bracket_height/2 + rib_height/2, 0) * Box(rib_thickness, rib_thickness, rib_height)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "bracket"
export_step(part, "output.step")