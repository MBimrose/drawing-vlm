from build123d import *

outer_diameter = 80.0
thickness = 10.0
bore_diameter = 20.0
slot_width = 5.0
slot_length = outer_diameter
mount_hole_diameter = 5.0
mount_hole_offset = 30.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=thickness)

solid_body = p.part

# Central bore
solid_body = solid_body - Pos(0, 0, thickness / 2) * Cylinder(bore_diameter / 2, thickness)

# Slot cut across the washer
solid_body = solid_body - Pos(0, 0, thickness / 2) * Box(slot_length, slot_width, thickness)

# Mount holes
solid_body = solid_body - Pos(0, mount_hole_offset, thickness / 2) * Cylinder(mount_hole_diameter / 2, thickness)
solid_body = solid_body - Pos(0, -mount_hole_offset, thickness / 2) * Cylinder(mount_hole_diameter / 2, thickness)

# Chamfer all vertical edges
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "washer_with_slot_and_mount_holes"
export_step(part, "output.step")