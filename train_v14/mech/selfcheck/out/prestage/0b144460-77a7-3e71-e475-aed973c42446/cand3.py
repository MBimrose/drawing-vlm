from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
edge_fillet_radius = 2.0
hole_diameter = 6.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 4
hole_cols = 5
rib_width = 5.0
rib_height = 5.0
rib_spacing = 15.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), edge_fillet_radius)

rib_count = int((plate_length - 2 * rib_spacing) // rib_spacing)
for i in range(rib_count):
    x = -plate_length/2 + rib_spacing + i * rib_spacing + rib_spacing/2
    rib = Pos(x, 0, plate_thickness + rib_height/2) * Box(rib_width, plate_width - 2 * edge_fillet_radius, rib_height)
    solid_body = solid_body + rib

for col in range(hole_cols):
    for row in range(hole_rows):
        x = (col - (hole_cols - 1) / 2) * hole_spacing_x
        y = (row - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, plate_thickness/2 + rib_height/2) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)
        solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")