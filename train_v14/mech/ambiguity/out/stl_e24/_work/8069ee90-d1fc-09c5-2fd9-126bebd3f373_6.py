from build123d import *

plate_size = 80.0
plate_thickness = 5.0
octagon_diameter = 20.0
slot_width = 8.0
slot_length = 30.0
slot_offset = 5.0
chamfer_size = 2.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0
fillet_radius = 0.5

solid = Box(plate_size, plate_size, plate_thickness)

with BuildPart() as oct_bp:
    with BuildSketch() as oct_sk:
        RegularPolygon(octagon_diameter/2, 8)
    extrude(amount=plate_thickness + 10)
solid = solid - oct_bp.part

slot_center_dist = octagon_diameter/2 + slot_offset + slot_length/2
for angle in [0, 90, 180, 270]:
    slot = Rot(0, 0, angle) * Pos(slot_center_dist, 0, 0) * Box(slot_length, slot_width, plate_thickness + 10)
    solid = solid - slot

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

mount_points = [
    (plate_size/2 - mount_hole_offset, plate_size/2 - mount_hole_offset),
    (-plate_size/2 + mount_hole_offset, plate_size/2 - mount_hole_offset),
    (-plate_size/2 + mount_hole_offset, -plate_size/2 + mount_hole_offset),
    (plate_size/2 - mount_hole_offset, -plate_size/2 + mount_hole_offset),
]
for x, y in mount_points:
    solid = solid - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 10)

solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)

part = solid
part.name = "plate_with_octagon_slots_and_mount_holes"
export_step(part, "output.step")