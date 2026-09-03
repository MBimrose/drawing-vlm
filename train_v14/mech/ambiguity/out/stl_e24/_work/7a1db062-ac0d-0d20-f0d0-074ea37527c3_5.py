from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
through_hole_diameter = 12.0
set_screw_diameter = 4.2
set_screw_offset = boss_diameter / 4.0
slot_width = 6.0
slot_length = 30.0
slot_depth = 8.0
chamfer_distance = 1.0
rib_height = 4.0
rib_thickness = 3.0
rib_spacing = 20.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = solid_body + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(through_hole_diameter/2, boss_height + plate_thickness + 10)
solid_body = solid_body - Pos(set_screw_offset, 0, plate_thickness/2 + boss_height/2) * Cylinder(set_screw_diameter/2, boss_height + plate_thickness + 10)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 + boss_height - slot_depth/2) * Box(slot_length, slot_width, slot_depth)
solid_body = solid_body + Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_thickness, plate_width - 2 * rib_spacing, rib_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "plate_with_boss_and_rib"
export_step(part, "output.step")