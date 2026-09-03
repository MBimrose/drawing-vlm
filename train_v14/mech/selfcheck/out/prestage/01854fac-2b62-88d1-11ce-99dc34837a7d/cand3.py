from build123d import *

plate_width = 80.0
plate_height = 100.0
plate_thickness = 5.0
rib_width = 20.0
rib_height = 80.0
rib_thickness = 3.0
pocket_width = 40.0
pocket_height = 30.0
pocket_fillet_radius = 5.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 5
edge_chamfer = 1.0

base = Box(plate_width, plate_height, plate_thickness)
rib = Pos(0, 0, plate_thickness/2 - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = base + rib

with BuildPart() as pocket_bp:
    with BuildSketch() as ps:
        RectangleRounded(pocket_width, pocket_height, pocket_fillet_radius)
    extrude(amount=plate_thickness + 10)
pocket_solid = pocket_bp.part
solid_body = solid_body - pocket_solid

start_x = -((hole_cols - 1) * hole_spacing_x) / 2
start_y = -((hole_rows - 1) * hole_spacing_y) / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = start_x + i * hole_spacing_x
        y = start_y + j * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, edge_chamfer)

part = solid_body
part.name = "plate_with_rib_pocket_holes"
export_step(part, "output.step")