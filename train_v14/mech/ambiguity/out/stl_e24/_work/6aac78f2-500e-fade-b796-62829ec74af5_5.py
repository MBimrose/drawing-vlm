from build123d import *

outer_width = 80.0
outer_height = 60.0
thickness = 10.0
wall_thickness = 1.0
chamfer_distance = 2.0
slot_width = 10.0
slot_height = 30.0
slot_offset_y = 15.0
groove_width = 40.0
groove_height = 5.0
groove_depth = 8.0
hole_diameter = 4.0
cbore_diameter = 6.0
cbore_depth = 2.0
hole_spacing = 20.0

solid_body = Box(outer_width, outer_height, thickness)
solid_body = offset(solid_body, amount=-wall_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

slot_cut = Pos(-outer_width/2 + wall_thickness/2, slot_offset_y, 0) * Box(slot_width, slot_height, thickness)
solid_body = solid_body - slot_cut

groove_cut = Pos(0, outer_height/2 - groove_depth/2, 0) * Box(groove_width, groove_depth, groove_height)
solid_body = solid_body - groove_cut

for y in [-hole_spacing/2, hole_spacing/2]:
    shaft = Pos(outer_width/2, y, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, 200)
    solid_body = solid_body - shaft
    cbore = Pos(outer_width/2 - cbore_depth/2, y, 0) * Rot(0, 90, 0) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - cbore

part = solid_body
part.name = "shelled_box_with_slot_groove_holes"
export_step(part, "output.step")