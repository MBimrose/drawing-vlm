from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 6.0
boss_radius = 12.0
boss_height = 5.0
hole_diameter = 4.0
hole_spacing_x = 40.0
hole_spacing_y = 12.0
slot_width = 6.0
slot_length = 20.0
chamfer_dist = 0.5
rib_width = 8.0
rib_height = 2.0

result = Box(leaf_length, leaf_width, leaf_thickness)

for x, y in [(-hole_spacing_x/2, -hole_spacing_y/2), (hole_spacing_x/2, -hole_spacing_y/2),
             (-hole_spacing_x/2, hole_spacing_y/2), (hole_spacing_x/2, hole_spacing_y/2)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, leaf_thickness * 2)

result = result - Pos(-leaf_length/2 + slot_width/2, 0, 0) * Box(slot_width, slot_length, leaf_thickness * 2)
result = result - Pos(leaf_length/2 - slot_width/2, 0, 0) * Box(slot_width, slot_length, leaf_thickness * 2)

result = result + Pos(0, 0, leaf_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)

rib = Pos(0, 0, -leaf_thickness/2 + rib_height/2) * Box(rib_width, leaf_width - 10, rib_height)
result = result + rib

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_dist)

part = result
part.name = "leaf_with_boss_and_rib"
export_step(part, "output.step")