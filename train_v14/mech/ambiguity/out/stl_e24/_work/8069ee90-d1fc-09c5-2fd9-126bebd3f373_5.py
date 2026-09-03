from build123d import *

plate_length = 80.0
plate_width = 80.0
plate_thickness = 5.0
edge_fillet_radius = 1.0
edge_chamfer = 1.5
slot_length = 30.0
slot_width = 8.0
slot_offset = 10.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0
boss_diameter = 20.0
boss_depth = 2.0
boss_fillet = 0.5

result = Box(plate_length, plate_width, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), edge_chamfer)

slot_positions = [
    (0, plate_width/2 - slot_offset - slot_width/2),
    (0, -(plate_width/2 - slot_offset - slot_width/2)),
    (plate_length/2 - slot_offset - slot_width/2, 0),
    (-(plate_length/2 - slot_offset - slot_width/2), 0)
]
for x, y in slot_positions:
    result = result - Pos(x, y, 0) * Box(slot_length, slot_width, plate_thickness)

result = fillet(result.edges().filter_by(Axis.Z), edge_fillet_radius)

mount_positions = [
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-(plate_length/2 - mount_hole_offset), plate_width/2 - mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -(plate_width/2 - mount_hole_offset)),
    (-(plate_length/2 - mount_hole_offset), -(plate_width/2 - mount_hole_offset))
]
for x, y in mount_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

with BuildPart() as bp:
    with BuildSketch() as sk:
        RegularPolygon(boss_diameter/2, 8)
    extrude(amount=boss_depth)
boss_solid = bp.part
boss_solid = fillet(boss_solid.edges().filter_by(Axis.Z), boss_fillet)
result = result - Pos(0, 0, plate_thickness/2 - boss_depth) * boss_solid

part = result
part.name = "plate_with_slots_holes_and_octagonal_boss"
export_step(part, "output.step")