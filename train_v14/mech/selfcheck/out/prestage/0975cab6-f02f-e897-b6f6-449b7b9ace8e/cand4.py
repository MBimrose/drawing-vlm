from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 4.0
flange_width = 8.0
pocket_length = 30.0
pocket_width = 15.0
pocket_depth = 2.0
hole_diameter = 4.0
hole_spacing = 25.0
fillet_radius = 0.5
chamfer_distance = 0.5
boss_radius = 5.0
boss_height = 3.0
slot_length = 20.0
slot_width = 4.0

base = Box(plate_length, plate_width, plate_thickness)
flange = Pos(0, plate_width/2 + flange_width/2, 0) * Box(plate_length, flange_width, plate_thickness)
result = base + flange

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

boss = Pos(plate_length/2 - boss_radius - 5, 0, boss_height/2) * Cylinder(boss_radius, boss_height)
result = result + boss

slot = Pos(plate_length/2 - slot_length/2, 0, 0) * Box(slot_length, slot_width, plate_thickness)
result = result - slot

part = result
part.name = "plate_with_flange_pocket_boss"
export_step(part, "output.step")