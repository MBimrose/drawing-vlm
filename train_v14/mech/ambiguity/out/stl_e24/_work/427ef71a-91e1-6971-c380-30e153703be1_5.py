from build123d import *

outer_width = 50.0
outer_depth = 60.0
outer_height = 30.0
wall_thickness = 5.0
slot_width = 8.0
slot_height = 15.0
hole_diameter = 5.0
hole_spacing_x = 40.0
hole_spacing_y = 20.0
chamfer_size = 1.0
rib_thickness = 3.0
rib_height = 10.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)

bottom_edges = solid_body.edges().sort_by(Axis.Z)[:1]
solid_body = chamfer(bottom_edges, chamfer_size)

inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness
cut_depth = outer_height - wall_thickness
cut_box = Pos(0, 0, outer_height - cut_depth/2) * Box(inner_width, inner_depth, cut_depth)
solid_body = solid_body - cut_box

slot_box = Pos(0, -outer_depth/2 + wall_thickness/2, wall_thickness + slot_height/2) * Box(slot_width, wall_thickness, slot_height)
solid_body = solid_body - slot_box

rib_box = Pos(0, outer_depth/2 - wall_thickness/2, wall_thickness + rib_height/2) * Box(rib_thickness, wall_thickness, rib_height)
solid_body = solid_body + rib_box

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2)
]
for x, y in hole_positions:
    hole = Pos(x, y, outer_height/2) * Cylinder(hole_diameter/2, outer_height)
    solid_body = solid_body - hole

part = solid_body
part.name = "box_with_slot_rib_holes"
export_step(part, "output.step")