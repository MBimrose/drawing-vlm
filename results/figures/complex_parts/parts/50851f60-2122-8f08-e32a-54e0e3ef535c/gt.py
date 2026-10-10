from build123d import *

outer_diameter = 60.0
inner_diameter = 30.0
collar_height = 20.0
pocket_width = 40.0
pocket_height = 10.0
pocket_depth = 8.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
fillet_radius = 2.0
chamfer_distance = 1.0
slot_width = 4.0
slot_length = 12.0
slot_depth = 6.0
slot_count = 4

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, collar_height))
            l2 = Line(l1@1, (inner_radius + fillet_radius, collar_height))
            a1 = ThreePointArc(l2@1, (inner_radius, collar_height), (inner_radius, collar_height - fillet_radius))
            l3 = Line(a1@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

result = p.part

for x, y in [(-mount_hole_spacing / 2, 0), (mount_hole_spacing / 2, 0)]:
    result = result - Pos(x, y, collar_height / 2) * Cylinder(mount_hole_diameter / 2, collar_height + 1)

result = result - Pos(0, 0, collar_height - pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)

import math
for i in range(slot_count):
    slot = Rot(0, 0, i * 360.0 / slot_count) * Pos(outer_radius - slot_depth / 2, 0, collar_height / 2) * Box(slot_depth, slot_width, slot_length)
    result = result - slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "collar_with_pocket_and_slots"
export_step(part, OUTPUT_PATH)