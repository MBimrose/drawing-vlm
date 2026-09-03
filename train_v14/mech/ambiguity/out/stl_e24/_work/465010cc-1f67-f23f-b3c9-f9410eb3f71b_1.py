from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 12.0
corner_fillet_radius = 5.0
slot_length = 40.0
slot_width = 8.0
slot_spacing = 20.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_distance = 1.0

solid_body = Box(base_length, base_width, base_thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
target_edge = max(vertical_edges, key=lambda e: (e.center().X, e.center().Y))
solid_body = fillet([target_edge], corner_fillet_radius)

slot_positions = [(-slot_spacing/2, 0), (slot_spacing/2, 0)]
for x, y in slot_positions:
    slot = Pos(x, y, 0) * Box(slot_length, slot_width, base_thickness * 2)
    solid_body = solid_body - slot

hole_positions = [
    (base_length/2 - mount_hole_offset, base_width/2 - mount_hole_offset),
    (-base_length/2 + mount_hole_offset, base_width/2 - mount_hole_offset),
    (-base_length/2 + mount_hole_offset, -base_width/2 + mount_hole_offset),
    (base_length/2 - mount_hole_offset, -base_width/2 + mount_hole_offset)
]
for x, y in hole_positions:
    hole = Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, base_thickness * 2)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "base_plate_with_slots_and_holes"
export_step(part, "output.step")