from build123d import *

plate_width = 100.0
plate_height = 80.0
plate_thickness = 5.0
edge_chamfer = 2.0
rib_width = 20.0
rib_height = 2.0
rib_margin = 5.0
hole_diameter = 4.5
hole_spacing_x = 30.0
hole_spacing_y = 30.0
hole_rows = 2
hole_cols = 2
hole_offset_x = -plate_width/2 + 20.0
hole_offset_y = -plate_height/2 + 20.0

base = Box(plate_width, plate_height, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), edge_chamfer)

rib = Pos(0, -plate_height/2 + rib_width/2, plate_thickness + rib_height/2) * Box(plate_width - 2*rib_margin, rib_width, rib_height)
base = base + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = hole_offset_x + i * hole_spacing_x
        y = hole_offset_y + j * hole_spacing_y
        base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

part = base
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")