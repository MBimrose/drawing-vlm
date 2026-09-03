from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 12.0
groove_width = 10.0
groove_depth = 4.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 3
hole_cols = 4
edge_chamfer = 1.0

base = Box(plate_length, plate_width, plate_thickness)
groove = Pos(0, 0, plate_thickness/2 - groove_depth/2) * Box(groove_width, plate_length, groove_depth)
solid_body = base - groove

start_x = -plate_length/2 + hole_spacing_x/2
start_y = -plate_width/2 + hole_spacing_y/2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = start_x + i * hole_spacing_x
        y = start_y + j * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 2)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, edge_chamfer)

part = solid_body
part.name = "plate_with_groove_and_holes"
export_step(part, "output.step")