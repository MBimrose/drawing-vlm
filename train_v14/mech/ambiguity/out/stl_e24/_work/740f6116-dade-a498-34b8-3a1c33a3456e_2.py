from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 8.0
slot_length = 50.0
slot_width = 4.0
slot_offset_y = 15.0
mount_hole_diameter = 5.0
mount_hole_offset_x = 30.0
mount_hole_offset_y = 10.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s2:
        Circle(boss_diameter / 2)
    extrude(amount=boss_height)

solid_body = p.part

with BuildPart() as slot_p:
    with BuildSketch() as slot_s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + boss_height + 20)
slot_tool = slot_p.part

solid_body = solid_body - Pos(0, slot_offset_y, 0) * slot_tool
solid_body = solid_body - Pos(0, -2 * slot_offset_y, 0) * slot_tool

hole_tool = Cylinder(mount_hole_diameter / 2, plate_thickness + boss_height + 20)
for x, y in [(mount_hole_offset_x, mount_hole_offset_y),
             (-mount_hole_offset_x, mount_hole_offset_y),
             (mount_hole_offset_x, -mount_hole_offset_y),
             (-mount_hole_offset_x, -mount_hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, 0) * hole_tool

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_boss_slots_holes"
export_step(part, "output.step")