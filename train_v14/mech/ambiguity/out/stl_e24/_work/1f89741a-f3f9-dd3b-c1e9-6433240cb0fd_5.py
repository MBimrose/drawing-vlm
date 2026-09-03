from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
rib_height = 4.0
rib_offset = 5.0
boss_diameter = 15.0
boss_height = 6.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_spacing = 30.0
fillet_radius = 1.0
slot_width = 20.0
slot_length = plate_length - 20.0
slot_depth = 2.0

base = Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_length, plate_width, rib_height)
result = base + rib

pocket = Pos(0, 0, plate_thickness/2 + rib_height - rib_height/2) * Box(plate_length - 2*rib_offset, plate_width - 2*rib_offset, rib_height)
result = result - pocket

boss = Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + boss

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    result = result - Pos(x, y, plate_thickness/2 + rib_height) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness + rib_height, countersink_angle)

slot = Pos(0, 0, plate_thickness/2 + rib_height - slot_depth/2) * Box(slot_width, slot_length, slot_depth)
result = result - slot

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "plate_with_rib_boss_and_holes"
export_step(part, "output.step")