from build123d import *

lever_length = 80.0
lever_width = 20.0
lever_thickness = 10.0
crown_radius = 10.0
boss_diameter = 6.0
boss_height = 6.0
hole_diameter = 5.0
hole_offset = 12.0
chamfer_dist = 0.5
slot_width = 6.0
slot_length = 12.0
slot_offset = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-lever_width/2, 0), (-lever_width/2, lever_length - crown_radius))
            a1 = ThreePointArc(l1 @ 1, (0, lever_length), (lever_width/2, lever_length - crown_radius))
            l2 = Line(a1 @ 1, (lever_width/2, 0))
            l3 = Line(l2 @ 1, l1 @ 0)
        make_face()
    extrude(amount=lever_thickness)

solid_body = p.part
solid_body = solid_body + Pos(0, lever_length/2, lever_thickness + boss_height/2) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_height)

for x in [-hole_offset/2, hole_offset/2]:
    solid_body = solid_body - Pos(x, lever_thickness/2, lever_thickness/2) * Cylinder(hole_diameter/2, lever_thickness)

solid_body = solid_body - Pos(0, slot_offset, lever_thickness/2) * Box(slot_width, slot_length, lever_thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_dist)

part = solid_body
part.name = "lever"
export_step(part, "output.step")