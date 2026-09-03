from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
rib_height = 4.0
rib_offset = 5.0
boss_diameter = 15.0
boss_height = 12.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_spacing = 30.0
fillet_radius = 1.0
internal_rib_width = 4.0
internal_rib_height = 2.0
internal_rib_spacing = 20.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
rib_outer = Pos(0, 0, plate_thickness + rib_height/2) * Box(plate_length, plate_width, rib_height)
rib_inner = Pos(0, 0, plate_thickness + rib_height/2) * Box(plate_length - 2*rib_offset, plate_width - 2*rib_offset, rib_height)
rib = rib_outer - rib_inner
boss = Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)
internal_rib1 = Pos(-internal_rib_spacing/2, 0, plate_thickness + internal_rib_height/2) * Box(internal_rib_width, plate_width, internal_rib_height)
internal_rib2 = Pos(internal_rib_spacing/2, 0, plate_thickness + internal_rib_height/2) * Box(internal_rib_width, plate_width, internal_rib_height)

result = base + rib + boss + internal_rib1 + internal_rib2

csk_depth = (countersink_diameter/2 - hole_diameter/2) / math.tan(math.radians(countersink_angle/2))
shaft_depth = plate_thickness + rib_height - csk_depth
csk_cone = Pos(0, 0, plate_thickness + rib_height - csk_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, csk_depth)
csk_shaft = Pos(0, 0, plate_thickness + rib_height - csk_depth - shaft_depth/2) * Cylinder(hole_diameter/2, shaft_depth)
csk_hole = csk_cone + csk_shaft

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    result = result - Pos(x, y, 0) * csk_hole

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "plate_with_ribs_boss_and_holes"
export_step(part, "output.step")