from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
rib_height = 2.0
rib_width = 2.0
hole_diameter = 4.5
hole_spacing_x = 30.0
hole_spacing_y = 30.0
hole_rows = 2
hole_cols = 3
hole_offset_x = 10.0
hole_offset_y = 10.0
chamfer_distance = 2.0

base = Box(plate_length, plate_width, plate_thickness)
vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_distance)

rib = Pos(0, -plate_width/2 + rib_width/2, plate_thickness + rib_height/2) * Box(plate_length, rib_width, rib_height)
base = base + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = -plate_length/2 + hole_offset_x + i * hole_spacing_x
        y = -plate_width/2 + hole_offset_y + j * hole_spacing_y
        base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 2)

part = base
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")