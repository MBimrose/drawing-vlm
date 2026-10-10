from build123d import *

base_width = 70.0
base_length = 80.0
base_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
step_diameter = 15.0
step_height = 30.0
top_diameter = 12.0
top_height = 20.0
hole_diameter = 5.0
hole_spacing = 30.0
chamfer_size = 1.0
rib_thickness = 3.0
rib_height = 5.0
slot_width = 12.0
slot_length = 20.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_length, base_thickness)
boss = Pos(0, 0, base_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
step = Pos(0, 0, base_thickness + boss_height + step_height/2) * Cylinder(step_diameter/2, step_height)
top = Pos(0, 0, base_thickness + boss_height + step_height + top_height/2) * Cylinder(top_diameter/2, top_height)
rib = Pos(0, 0, base_thickness + rib_height/2) * Box(base_width - 20, rib_thickness, rib_height)

result = base + boss + step + top + rib

total_height = base_thickness + boss_height + step_height + top_height
for x, y in [(-hole_spacing/2, -hole_spacing/2), (hole_spacing/2, -hole_spacing/2),
             (-hole_spacing/2, hole_spacing/2), (hole_spacing/2, hole_spacing/2)]:
    result = result - Pos(x, y, total_height/2) * Cylinder(hole_diameter/2, total_height + 10)

slot_z = base_thickness + boss_height + step_height + top_height/2
result = result - Pos(0, 0, slot_z) * Box(top_diameter, slot_width, slot_length)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "stepped_boss_plate"
export_step(part, "output.step")