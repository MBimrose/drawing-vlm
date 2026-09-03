from build123d import *

width = 80.0
height = 60.0
thickness = 10.0
wall_thickness = 1.0
rib_width = 20.0
rib_height = 10.0
notch_width = 12.0
notch_height = 8.0
notch_offset = 5.0
pocket_width = 40.0
pocket_height = 30.0
pocket_depth = 6.0
hole_diameter = 4.0
cbore_diameter = 6.0
cbore_depth = 2.0
hole_spacing = 20.0
chamfer_size = 2.0

solid_body = Box(width, height, thickness)
solid_body = offset(solid_body, amount=-wall_thickness)

rib = Pos(0, 0, thickness/2 - rib_height/2) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body + rib

notch = Pos(-width/2 + notch_offset, height/2 - notch_height/2, 0) * Box(notch_width, notch_height, thickness)
solid_body = solid_body - notch

pocket = Pos(0, height/2 - pocket_depth/2, 0) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

for y in [-hole_spacing/2, hole_spacing/2]:
    cbore = Pos(width/2 - cbore_depth/2, y, 0) * Rot(0, 90, 0) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - cbore
    shaft = Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, width + 20)
    solid_body = solid_body - shaft

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "shelled_box_with_features"
export_step(part, "output.step")