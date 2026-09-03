from build123d import *

outer_length = 100.0
outer_width = 60.0
outer_height = 20.0
wall_thickness = 2.0
base_thickness = 4.0
pocket_width = 20.0
pocket_height = 12.0
pocket_depth = 6.0
pocket_offset_x = 30.0
hole_diameter = 6.0
hole_spacing = 12.0
hole_row_offset = -outer_width/2 + 10.0
chamfer_distance = 0.5
rib_width = 4.0
rib_thickness = 2.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

base_plate = Pos(0, 0, base_thickness/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, base_thickness)
solid_body = solid_body + base_plate

pocket = Pos(0, outer_width/2 - pocket_depth/2, outer_height/2 + pocket_offset_x) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

for i in range(5):
    y_pos = -outer_width/2 + hole_spacing/2 + i * hole_spacing
    hole = Pos(hole_row_offset, y_pos, outer_height/2) * Cylinder(hole_diameter/2, outer_height)
    solid_body = solid_body - hole

rib = Pos(0, 0, base_thickness + rib_thickness/2) * Box(outer_length - 2*wall_thickness, rib_width, rib_thickness)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "hollow_box_with_pocket_and_holes"
export_step(part, "output.step")