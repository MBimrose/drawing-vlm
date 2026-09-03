from build123d import *

outer_width = 50.0
outer_depth = 60.0
outer_height = 30.0
wall_thickness = 5.0
inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness
opening_width = 30.0
opening_height = 20.0
slot_width = 3.0
slot_height = 15.0
hole_diameter = 5.0
hole_spacing = 30.0
chamfer_size = 1.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

opening_cut = Pos(0, outer_depth/2 - wall_thickness/2, outer_height/2) * Box(opening_width, wall_thickness, opening_height)
solid_body = solid_body - opening_cut

slot_cut = Pos(0, -outer_depth/2 + wall_thickness/2, outer_height/2 - opening_height/2 + slot_height/2) * Box(slot_width, wall_thickness, slot_height)
solid_body = solid_body - slot_cut

for x in [-hole_spacing/2, hole_spacing/2]:
    hole_cut = Pos(x, outer_depth/2 - wall_thickness/2, outer_height/2) * Cylinder(hole_diameter/2, wall_thickness)
    solid_body = solid_body - hole_cut

bottom_edges = solid_body.edges().sort_by(Axis.Z)[:1]
front_bottom_edge = bottom_edges.sort_by(Axis.Y)[-1:]
solid_body = chamfer(front_bottom_edge, chamfer_size)

part = solid_body
part.name = "hollow_box_with_openings"
export_step(part, "output.step")