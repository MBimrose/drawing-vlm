from build123d import *

block_length = 80.0
block_width = 50.0
block_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
through_hole_diameter = 12.0
set_screw_diameter = 4.2
set_screw_head_diameter = 7.0
set_screw_head_depth = 2.0
slot_width = 6.0
slot_length = 30.0
slot_depth = 8.0
chamfer_size = 0.5

solid_body = Box(block_length, block_width, block_thickness)
solid_body = solid_body + Pos(0, 0, block_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body - Cylinder(through_hole_diameter/2, block_thickness + boss_height + 2)

slot_box = Pos(0, 0, block_thickness/2 + boss_height - slot_depth/2) * Box(slot_length, slot_width, slot_depth)
solid_body = solid_body - slot_box

set_screw_x = boss_diameter/4
set_screw_z = block_thickness/2 + boss_height/2
solid_body = solid_body - Pos(set_screw_x, 0, set_screw_z) * Cylinder(set_screw_diameter/2, boss_height + 2)
solid_body = solid_body - Pos(set_screw_x, 0, block_thickness/2 + boss_height - set_screw_head_depth/2) * Cylinder(set_screw_head_diameter/2, set_screw_head_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "block_with_boss_and_slot"
export_step(part, "output.step")