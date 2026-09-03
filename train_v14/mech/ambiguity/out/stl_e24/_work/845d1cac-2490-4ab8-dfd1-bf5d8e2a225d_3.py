from build123d import *

strap_length = 80.0
strap_width = 12.0
strap_thickness = 6.0
boss_diameter = 12.0
boss_height = 20.0
slot_length = 15.0
slot_width = 4.0
slot_depth = 3.0
hole_diameter = 3.0
hole_spacing = 20.0
fillet_radius = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(strap_length, strap_width)
    extrude(amount=strap_thickness)

solid_body = p.part

slot_box = Pos(0, strap_width/2 - slot_depth/2, strap_thickness/2) * Box(slot_length, slot_depth, slot_width)
solid_body = solid_body - slot_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

for x in [-hole_spacing, 0, hole_spacing]:
    hole = Pos(x, 0, strap_thickness/2) * Cylinder(hole_diameter/2, strap_thickness)
    solid_body = solid_body - hole

boss = Pos(strap_length/2 + boss_height/2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "strap_with_boss"
export_step(part, "output.step")