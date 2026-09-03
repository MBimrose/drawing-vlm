from build123d import *
import math

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
rib_height = 4.0
rib_offset = 5.0
boss_diameter = 15.0
boss_height = 6.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_spacing = 30.0
slot_width = 20.0
slot_length = plate_depth - 2 * rib_offset
fillet_radius = 1.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_depth, plate_thickness)
rib = Pos(0, 0, plate_thickness + rib_height/2) * Box(plate_width, plate_depth, rib_height)
rib_cut = Pos(0, 0, plate_thickness + rib_height/2) * Box(plate_width - 2*rib_offset, plate_depth - 2*rib_offset, rib_height)
rib = rib - rib_cut
boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + rib + boss

total_height = plate_thickness + rib_height
csk_depth = (countersink_diameter/2 - hole_diameter/2) / math.tan(math.radians(countersink_angle/2))

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    result = result - Pos(x, y, total_height/2) * Cylinder(hole_diameter/2, total_height + 2)
    result = result - Pos(x, y, total_height - csk_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, csk_depth)

slot = Pos(0, 0, total_height/2) * Box(slot_width, slot_length, total_height + 2)
result = result - slot

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "plate_with_rib_boss_holes"
export_step(part, "output.step")