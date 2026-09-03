from build123d import *

plate_length = 100.0
plate_width = 60.0
plate_thickness = 8.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0
hole_diameter = 6.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
num_holes_x = 4
num_holes_y = 2
chamfer_size = 0.5
rib_height = 4.0
rib_width = 10.0
rib_spacing = 30.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = (i - (num_holes_x - 1) / 2) * hole_spacing_x
        y = (j - (num_holes_y - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)

for i in range(3):
    x = (i - 1) * rib_spacing
    rib = Pos(x, 0, -rib_height/2) * Box(rib_width, rib_height, rib_height)
    solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_pocket_holes_ribs"
export_step(part, "output.step")