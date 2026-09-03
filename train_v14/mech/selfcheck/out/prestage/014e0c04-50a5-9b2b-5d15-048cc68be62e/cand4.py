from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 6.0
slot_width = 12.0
slot_depth = bracket_thickness
central_hole_diameter = 12.0
mount_hole_diameter = 5.0
mount_hole_offset = 15.0
rib_width = 6.0
rib_height = 3.0
chamfer_size = 0.5

solid_body = Box(bracket_length, bracket_width, bracket_thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

slot_box = Pos(0, bracket_width/2 - slot_depth/2, 0) * Box(slot_width, slot_depth, slot_depth)
solid_body = solid_body - slot_box

solid_body = solid_body - Cylinder(central_hole_diameter/2, bracket_thickness)

for x in [-bracket_length/2 + mount_hole_offset, bracket_length/2 - mount_hole_offset]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, bracket_thickness)

rib = Pos(0, 0, bracket_thickness/2 + rib_height/2) * Box(rib_width, bracket_length - 2*mount_hole_offset, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "bracket"
export_step(part, "output.step")