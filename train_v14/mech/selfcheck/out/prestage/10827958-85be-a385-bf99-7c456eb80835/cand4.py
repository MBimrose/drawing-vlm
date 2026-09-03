from build123d import *

lever_length = 80.0
lever_width = 20.0
lever_thickness = 10.0
crown_radius = lever_width / 2.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_offset_from_end = 10.0
chamfer_distance = 0.5
slot_width = 6.0
slot_length = 12.0
slot_offset = 30.0
boss_radius = 3.0
boss_height = 5.0
boss_offset = 40.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-lever_width/2, 0), (lever_width/2, 0))
            l2 = Line(l1@1, (lever_width/2, lever_length - crown_radius))
            arc = ThreePointArc(l2@1, (0, lever_length), (-lever_width/2, lever_length - crown_radius))
            l3 = Line(arc@1, (-lever_width/2, 0))
        make_face()
    extrude(amount=lever_thickness)

solid_body = p.part

for x, y in [(-hole_spacing/2, hole_offset_from_end), (hole_spacing/2, hole_offset_from_end)]:
    solid_body = solid_body - Pos(x, y, lever_thickness/2) * Cylinder(hole_diameter/2, lever_thickness * 2)

solid_body = solid_body - Pos(0, slot_offset, lever_thickness/2) * Box(slot_width, slot_length, lever_thickness * 2)

solid_body = solid_body + Pos(lever_width/2 - boss_radius, boss_offset, lever_thickness + boss_height/2) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "lever"
export_step(part, "output.step")