from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
slot_length = 50.0
slot_width = 4.0
slot_offset_y = 15.0
mount_hole_diameter = 5.0
mount_hole_spacing_x = 60.0
mount_hole_spacing_y = 20.0
boss_diameter = 20.0
boss_height = 8.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

for y_off in [slot_offset_y, -slot_offset_y]:
    with BuildPart() as sp:
        with BuildSketch() as ss:
            SlotOverall(slot_length, slot_width)
        extrude(amount=plate_thickness * 2)
    solid_body = solid_body - Pos(0, y_off, 0) * sp.part

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness * 2)

solid_body = solid_body + Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_slots_holes_boss"
export_step(part, "output.step")