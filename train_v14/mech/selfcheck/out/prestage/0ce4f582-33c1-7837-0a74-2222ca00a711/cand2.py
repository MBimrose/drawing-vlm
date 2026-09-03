from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 20.0
slot_width = 5.0
slot_length = 30.0
hole_diameter = 8.5
hole_spacing = 20.0
counterbore_diameter = 12.0
counterbore_depth = 3.0
chamfer_size = 1.0
rib_width = 4.0
rib_height = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part

slot1 = Pos(outer_diameter / 2 - slot_width / 2, 0, thickness / 2) * Box(slot_width, slot_length, thickness)
slot2 = Pos(-(outer_diameter / 2 - slot_width / 2), 0, thickness / 2) * Box(slot_width, slot_length, thickness)
solid_body = solid_body - slot1 - slot2

for x, y in [(-hole_spacing / 2, 0), (hole_spacing / 2, 0)]:
    solid_body = solid_body - Pos(x, y, thickness - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(hole_diameter / 2, thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

rib = Pos(0, 0, thickness / 2) * Box(rib_width, rib_height, thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "flanged_ring_with_slots_and_ribs"
export_step(part, "output.step")