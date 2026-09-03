from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 15.0
slot_width = 10.0
slot_depth = 12.0
set_screw_diameter = 6.0
set_screw_depth = 8.0
mount_hole_diameter = 2.5
mount_hole_spacing = 25.0
chamfer_size = 1.0
rib_thickness = 2.0
rib_height = 12.0

solid_body = Box(block_length, block_width, block_height)

slot_cut = Pos(0, -block_width/2 + slot_depth/2, 0) * Box(block_length, slot_depth, slot_width)
solid_body = solid_body - slot_cut

set_screw_cut = Pos(block_length/2 - set_screw_depth/2, -block_width/2 + 10, 0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - set_screw_cut

for dx in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    for dy in [-mount_hole_spacing/2, mount_hole_spacing/2]:
        mount_cut = Pos(dx, dy, 0) * Cylinder(mount_hole_diameter/2, block_height + 10)
        solid_body = solid_body - mount_cut

rib = Pos(block_length/2 - rib_thickness/2, -block_width/2 + rib_height/2, 0) * Box(rib_thickness, rib_height, rib_thickness)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Y)[-1]
top_edges = top_face.edges().filter_by(Axis.Z)
solid_body = chamfer(top_edges, chamfer_size)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, 0.5)

part = solid_body
part.name = "block_with_slot_and_rib"
export_step(part, "output.step")