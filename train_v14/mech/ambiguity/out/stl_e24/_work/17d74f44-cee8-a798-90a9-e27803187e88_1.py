from build123d import *

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
housing_length = 80.0
slot_width = 8.0
slot_depth = wall_thickness - 0.5
slot_length = 40.0
boss_radius = 6.0
boss_height = 12.0
boss_offset = 20.0
countersink_diameter = 6.0
countersink_angle = 82.0
countersink_depth = wall_thickness + 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, housing_length))
            l3 = Line(l2 @ 1, (inner_radius, housing_length))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

slot_box = Pos(outer_radius - slot_depth / 2, 0, housing_length / 2) * Box(slot_depth, slot_length, slot_width)
solid_body = solid_body - slot_box

boss = Pos(inner_radius, -boss_offset, housing_length / 2) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

csk = Pos(inner_radius, -boss_offset, housing_length / 2) * Rot(0, 90, 0) * CounterSinkHole(countersink_diameter / 2, countersink_diameter, countersink_depth, countersink_angle)
solid_body = solid_body - csk

part = solid_body
part.name = "housing_with_slot_and_boss"
export_step(part, "output.step")