from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 5.0
chamfer_size = 1.0
hole_diameter = 12.0
hole_offset = 10.0
rib_width = 10.0
rib_height = 10.0
rib_thickness = 4.0
side_hole_diameter = 4.0
side_hole_spacing = 20.0
side_hole_offset = 10.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)
pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket
for x in [-outer_length/2 + hole_offset, outer_length/2 - hole_offset]:
    solid_body = solid_body - Pos(x, 0, outer_height/2) * Cylinder(hole_diameter/2, outer_height)
rib = Pos(0, 0, outer_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib
for y in [-side_hole_spacing, side_hole_spacing]:
    solid_body = solid_body - Pos(-outer_length/2, y, side_hole_offset) * Rot(0, 90, 0) * Cylinder(side_hole_diameter/2, outer_length)

part = solid_body
part.name = "hollow_box_with_pocket_and_holes"
export_step(part, "output.step")