from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
pocket_length = 40.0
pocket_width = 30.0
hole_diameter = 4.0
hole_depth = 6.0
hole_rows = 2
hole_cols = 3
hole_spacing_x = 20.0
hole_spacing_y = 30.0
fillet_radius = 2.0
chamfer_distance = 1.0
rib_height = 2.0
rib_width = 10.0
rib_length = 30.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

all_edges = solid_body.edges()
vertical_after = solid_body.edges().filter_by(Axis.Z)
non_vertical_edges = [e for e in all_edges if e not in vertical_after]
solid_body = chamfer(non_vertical_edges, chamfer_distance)

pocket = Pos(0, 0, plate_thickness/2) * Box(pocket_length, pocket_width, plate_thickness)
solid_body = solid_body - pocket

rib = Pos(0, 0, plate_thickness - rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

x_start = -((hole_cols - 1) * hole_spacing_x) / 2
y_start = -((hole_rows - 1) * hole_spacing_y) / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = x_start + i * hole_spacing_x
        y = y_start + j * hole_spacing_y
        hole = Pos(x, y, plate_thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
        solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_pocket_rib_and_holes"
export_step(part, "output.step")