from build123d import *

lever_length = 80
lever_width = 12
lever_thickness = 6
boss_diameter = 12
boss_height = 15
slot_length = 30
slot_width = 6
slot_depth = 3
hole_diameter = 4
hole_spacing = 20
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, -lever_width/2), (lever_length, -lever_width/2),
                     (lever_length, lever_width/2), (0, lever_width/2), close=True)
        make_face()
    extrude(amount=lever_thickness)

solid_body = p.part

slot = Pos(lever_length/2, lever_width/2 - slot_depth/2, lever_thickness/2) * Box(slot_length, slot_depth, slot_width)
solid_body = solid_body - slot

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(lever_length/2 + x, 0, lever_thickness/2) * Cylinder(hole_diameter/2, lever_thickness)
    solid_body = solid_body - hole

boss = Pos(lever_length + boss_height/2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "lever_with_boss"
export_step(part, "output.step")