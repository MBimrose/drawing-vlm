from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 8.0
slot_length = 50.0
slot_width = 4.0
slot_offset_y = 15.0
chamfer_size = 0.8
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
rib_width = 5.0
rib_length = 20.0
rib_height = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_depth)
    extrude(amount=plate_thickness)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s2:
        Circle(boss_diameter / 2)
    extrude(amount=boss_height)

solid_body = p.part

with BuildPart() as sp:
    with BuildSketch() as ss:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + 10)
slot_tool = sp.part

solid_body = solid_body - Pos(0, slot_offset_y, 0) * slot_tool
solid_body = solid_body - Pos(0, -2 * slot_offset_y, 0) * slot_tool

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

hole_positions = [
    (-plate_width/2 + mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    ( plate_width/2 - mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    (-plate_width/2 + mount_hole_offset,  plate_depth/2 - mount_hole_offset),
    ( plate_width/2 - mount_hole_offset,  plate_depth/2 - mount_hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 10)

rib1 = Pos(-plate_width/2 + rib_width/2 + 5, 0, rib_height/2) * Box(rib_width, rib_length, rib_height)
rib2 = Pos(plate_width/2 - rib_width/2 - 5, 0, rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_boss_slots_ribs"
export_step(part, "output.step")