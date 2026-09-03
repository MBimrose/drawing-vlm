from build123d import *

plate_size = 80.0
plate_thickness = 8.0
boss_size = 40.0
boss_height = 4.0
central_hole_dia = 20.0
corner_hole_dia = 6.0
corner_cbore_dia = 12.0
corner_cbore_depth = 2.0
corner_offset = 10.0
slot_width = 4.0
slot_length = 20.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_size, plate_size)
    extrude(amount=plate_thickness)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s2:
        Rectangle(boss_size, boss_size)
    extrude(amount=boss_height)

solid_body = p.part
total_h = plate_thickness + boss_height
solid_body = solid_body - Pos(0, 0, total_h/2) * Cylinder(central_hole_dia/2, total_h + 1)

corner_pts = [
    (plate_size/2 - corner_offset, plate_size/2 - corner_offset),
    (-plate_size/2 + corner_offset, plate_size/2 - corner_offset),
    (-plate_size/2 + corner_offset, -plate_size/2 + corner_offset),
    (plate_size/2 - corner_offset, -plate_size/2 + corner_offset),
]
for x, y in corner_pts:
    solid_body = solid_body - Pos(x, y, total_h/2) * Cylinder(corner_hole_dia/2, total_h + 1)
    solid_body = solid_body - Pos(x, y, total_h - corner_cbore_depth/2) * Cylinder(corner_cbore_dia/2, corner_cbore_depth)

slot_centers = [
    (0, plate_size/2 - slot_width/2),
    (0, -plate_size/2 + slot_width/2),
    (plate_size/2 - slot_width/2, 0),
    (-plate_size/2 + slot_width/2, 0),
]
for x, y in slot_centers:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Box(slot_width, slot_length, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_boss_holes_slots"
export_step(part, "output.step")