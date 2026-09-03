from build123d import *

outer_diameter = 80.0
inner_diameter = 40.0
thickness = 10.0
bore_diameter = 20.0
slot_width = 5.0
slot_length = 20.0
chamfer_size = 0.5
mount_hole_diameter = 5.0
mount_hole_spacing = 60.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
slot_center_radius = (outer_radius + inner_radius) / 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
        Circle(inner_radius)
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(bore_diameter / 2, thickness * 2)

for x, y in [(0, mount_hole_spacing / 2), (0, -mount_hole_spacing / 2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, thickness * 2)

for x in [slot_center_radius, -slot_center_radius]:
    solid_body = solid_body - Pos(x, 0, 0) * Box(slot_length, slot_width, thickness * 2)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "ring_with_slots_and_mount_holes"
export_step(part, "output.step")