from build123d import *

plate_length = 100
plate_width = 60
plate_thickness = 8
rib_width = 20
rib_thickness = 4
pocket_length = 30
pocket_width = 20
pocket_depth = 4
hole_diameter = 6
hole_spacing_x = 20
hole_spacing_y = 20
hole_rows = 2
hole_cols = 4
chamfer_size = 0.5
side_rib_width = 10
side_rib_offset = 30

base = Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, -plate_thickness/2 - rib_thickness/2) * Box(rib_width, rib_thickness, rib_thickness)
side_rib1 = Pos(-side_rib_offset, 0, -plate_thickness/2 - rib_thickness/2) * Box(side_rib_width, rib_thickness, rib_thickness)
side_rib2 = Pos(side_rib_offset, 0, -plate_thickness/2 - rib_thickness/2) * Box(side_rib_width, rib_thickness, rib_thickness)

solid_body = base + rib + side_rib1 + side_rib2

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

pocket_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-4:]
solid_body = chamfer(pocket_edges, chamfer_size)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_thickness + 20)
        solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_ribs_pocket_and_holes"
export_step(part, "output.step")