from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
corner_fillet_radius = 4.0
slot_length = 20.0
slot_width = 5.0
slot_offset = 12.0
mount_hole_diameter = 5.0
mount_hole_counterbore_diameter = 10.0
mount_hole_counterbore_depth = 2.0
mount_hole_offset = 12.0
boss_diameter = 20.0
boss_height = 15.0
rib_width = 20.0
rib_length = 30.0
rib_height = 3.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

with BuildPart() as slot_p:
    with BuildSketch() as slot_s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + 2)
slot_cutter = slot_p.part

solid_body = solid_body - Pos(-plate_length/2 + slot_offset, 0, 0) * slot_cutter
solid_body = solid_body - Pos(plate_length/2 - slot_offset, 0, 0) * slot_cutter

hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 2)
    solid_body = solid_body - Pos(x, y, plate_thickness - mount_hole_counterbore_depth/2) * Cylinder(mount_hole_counterbore_diameter/2, mount_hole_counterbore_depth)

solid_body = solid_body + Pos(0, 0, plate_thickness) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + Pos(0, 0, -rib_height/2) * Box(rib_width, rib_length, rib_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "plate_with_boss_and_ribs"
export_step(part, "output.step")