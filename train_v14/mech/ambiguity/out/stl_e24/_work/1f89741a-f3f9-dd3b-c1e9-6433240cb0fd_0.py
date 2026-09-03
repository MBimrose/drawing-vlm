from build123d import *
import math

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
slot_width = 8.0
slot_length = 20.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, plate_thickness + rib_height/2) * Box(plate_length, plate_width, rib_height)
inner_cut = Pos(0, 0, plate_thickness + rib_height/2) * Box(plate_length - 2*rib_offset, plate_width - 2*rib_offset, rib_height)
boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

result = base + rib - inner_cut + boss

csk_depth = (countersink_diameter/2 - hole_diameter/2) / math.tan(math.radians(countersink_angle/2))
shaft_depth = plate_thickness + rib_height - csk_depth
csk_cone = Pos(0, 0, plate_thickness + rib_height - csk_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, csk_depth)
shaft_cyl = Pos(0, 0, plate_thickness + rib_height - csk_depth - shaft_depth/2) * Cylinder(hole_diameter/2, shaft_depth)
csk_hole = csk_cone + shaft_cyl

for x in [-hole_spacing, 0, hole_spacing]:
    result = result - Pos(x, 0, 0) * csk_hole

slot = Pos(0, 0, plate_thickness + rib_height - plate_thickness/2) * Box(slot_length, plate_width - 2*rib_offset, plate_thickness)
result = result - slot

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "plate_with_rib_boss_and_holes"
export_step(part, "output.step")