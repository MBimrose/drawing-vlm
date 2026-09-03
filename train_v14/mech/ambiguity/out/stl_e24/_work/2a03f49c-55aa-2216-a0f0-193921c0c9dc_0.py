from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
corner_fillet_radius = 4.0
boss_diameter = 20.0
boss_height = 12.0
boss_fillet_radius = 2.5
mount_hole_diameter = 5.0
mount_hole_offset = 12.0
counterbore_diameter = 10.0
counterbore_depth = 2.0
slot_length = 20.0
slot_width = 5.0
slot_offset = 20.0
rib_length = 30.0
rib_width = 10.0
rib_height = 3.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

for x, y in [(-slot_offset, 0), (slot_offset, 0)]:
    with BuildPart() as sp:
        with BuildSketch() as ss:
            SlotOverall(slot_length, slot_width)
        extrude(amount=plate_thickness * 2)
    solid_body = solid_body - Pos(x, y, 0) * sp.part

mount_points = [
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, plate_thickness - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness * 2)

solid_body = solid_body + Pos(0, 0, plate_thickness) * Cylinder(boss_diameter/2, boss_height)
solid_body = fillet(solid_body.edges().sort_by(Axis.Z)[-1:], boss_fillet_radius)

solid_body = solid_body + Pos(0, 0, -rib_height/2) * Box(rib_length, rib_width, rib_height)

part = solid_body
part.name = "plate_with_boss_and_ribs"
export_step(part, "output.step")