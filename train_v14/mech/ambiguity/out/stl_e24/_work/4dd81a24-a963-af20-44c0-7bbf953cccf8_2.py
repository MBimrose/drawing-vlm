from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
chamfer_distance = 2.0
hole_diameter = 4.5
hole_spacing_x = 30.0
hole_spacing_y = 30.0
hole_rows = 2
hole_cols = 2
hole_offset_x = -20.0
hole_offset_y = -20.0
rib_height = 2.0
rib_width = 6.0
rib_offset = 5.0
pocket_depth = 2.0
pocket_width = 40.0
pocket_length = 60.0
pocket_offset_x = 0.0
pocket_offset_y = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

rib = Pos(0, -plate_width/2 + rib_offset, plate_thickness + rib_height/2) * Box(plate_length - 2*rib_offset, rib_width, rib_height)
solid_body = solid_body + rib

pocket = Pos(pocket_offset_x, pocket_offset_y, plate_thickness + rib_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        hx = hole_offset_x + (i - (hole_cols-1)/2) * hole_spacing_x
        hy = hole_offset_y + (j - (hole_rows-1)/2) * hole_spacing_y
        hole = Pos(hx, hy, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)
        solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_rib_pocket_holes"
export_step(part, "output.step")