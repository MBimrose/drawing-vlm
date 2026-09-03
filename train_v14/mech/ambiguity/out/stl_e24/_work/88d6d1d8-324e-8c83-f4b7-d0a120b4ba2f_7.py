from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 2.0
vent_slot_length = 12.0
vent_slot_width = 3.0
vent_spacing_x = 15.0
vent_spacing_y = 8.0
vent_rows = 4
vent_cols = 4
mount_hole_dia = 4.0
mount_hole_offset = 6.0
chamfer_size = 0.3
rib_width = 10.0
rib_length = plate_length
rib_height = 1.0
rib_spacing = 30.0
boss_length = 30.0
boss_width = 20.0
boss_height = 1.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
base = p.part
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

mount_pts = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset)
]
for x, y in mount_pts:
    base = base - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_dia/2, plate_thickness + 1)

vent_pts = []
start_x = -plate_length/2 + mount_hole_offset + vent_spacing_x/2
start_y = -plate_width/2 + mount_hole_offset + vent_spacing_y/2
for i in range(vent_cols):
    for j in range(vent_rows):
        x = start_x + i*vent_spacing_x
        y = start_y + j*vent_spacing_y
        vent_pts.append((x, y))
for x, y in vent_pts:
    base = base - Pos(x, y, plate_thickness/2) * Box(vent_slot_length, vent_slot_width, plate_thickness + 1)

rib1 = Pos(0, -rib_spacing/2, plate_thickness + rib_height/2) * Box(rib_width, rib_length, rib_height)
rib2 = Pos(0, rib_spacing/2, plate_thickness + rib_height/2) * Box(rib_width, rib_length, rib_height)
boss = Pos(0, 0, plate_thickness + boss_height/2) * Box(boss_length, boss_width, boss_height)

part = base + rib1 + rib2 + boss
part.name = "ventilated_plate_with_ribs_and_boss"
export_step(part, "output.step")