from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 6.0
boss_radius = 12.0
boss_height = 5.0
slot_width = 6.0
slot_length = 20.0
hole_diameter = 4.0
hole_spacing_x = 40.0
hole_spacing_y = 12.0
chamfer_size = 0.5

base = Pos(0, 0, leaf_thickness/2) * Box(leaf_length, leaf_width, leaf_thickness)
boss = Pos(0, 0, leaf_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
result = base + boss

slot1 = Pos(-leaf_length/2 + slot_width/2, 0, leaf_thickness/2) * Box(slot_width, slot_length, leaf_thickness)
slot2 = Pos(leaf_length/2 - slot_width/2, 0, leaf_thickness/2) * Box(slot_width, slot_length, leaf_thickness)
result = result - slot1 - slot2

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    ( hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2,  hole_spacing_y/2),
    ( hole_spacing_x/2,  hole_spacing_y/2)
]
for x, y in hole_positions:
    result = result - Pos(x, y, (leaf_thickness + boss_height)/2) * Cylinder(hole_diameter/2, leaf_thickness + boss_height + 2)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "leaf_with_boss_slots_holes"
export_step(part, "output.step")