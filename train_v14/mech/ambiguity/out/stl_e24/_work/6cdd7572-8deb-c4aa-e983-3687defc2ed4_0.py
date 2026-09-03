from build123d import *

width = 40.0
depth = 12.0
thickness = 4.0
rib_width = 6.0
rib_height = 2.0
rib_offset = 5.0
slot_width = 2.0
slot_length = 8.0
slot_offset = 10.0
hole_diameter = 3.3
hole_spacing = 20.0
hole_offset = 10.0
chamfer_size = 0.5

base = Pos(0.5 * width, 0, 0.5 * thickness) * Box(width, depth, thickness)
rib = Pos(rib_offset, 0, 0.5 * thickness) * Box(rib_width, rib_height, thickness)
result = base + rib

slot = Pos(slot_offset, depth / 2, 0.5 * thickness) * Box(slot_width, slot_length, thickness)
result = result - slot

slot_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
result = chamfer(slot_edges, chamfer_size)

for x, y in [(width - hole_offset, 0), (width - hole_offset - hole_spacing, 0)]:
    result = result - Pos(x, y, 0.5 * thickness) * Cylinder(hole_diameter / 2, thickness)

part = result
part.name = "plate_with_rib_slot_holes"
export_step(part, "output.step")