from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 6.0
boss_radius = 12.0
boss_height = 4.0
rib_width = 6.0
rib_height = 2.0
rib_spacing = 15.0
hole_diameter = 5.0
hole_depth = 3.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.8

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = solid_body + Cylinder(boss_radius, boss_height)

rib_positions = [
    (-(plate_length/2 - rib_spacing), 0),
    ((plate_length/2 - rib_spacing), 0),
    (0, -(plate_width/2 - rib_spacing)),
    (0, (plate_width/2 - rib_spacing))
]
for x, y in rib_positions:
    solid_body = solid_body + Pos(x, y, 0) * Box(rib_width, rib_height, plate_thickness)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_boss_ribs_and_holes"
export_step(part, "output.step")