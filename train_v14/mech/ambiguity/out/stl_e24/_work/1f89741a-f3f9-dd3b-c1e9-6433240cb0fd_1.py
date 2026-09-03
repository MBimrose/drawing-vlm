from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
rib_height = 4.0
rib_width = 5.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_spacing = 30.0
fillet_radius = 1.0
boss_diameter = 15.0
boss_height = 2.0
reinforcement_rib_width = 20.0
reinforcement_rib_height = 2.0

base = Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_length, plate_width, rib_height)
result = base + rib

pocket = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_length - 2*rib_width, plate_width - 2*rib_width, rib_height)
result = result - pocket

boss = Pos(0, 0, plate_thickness/2 + rib_height - boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + boss

reinforcement = Pos(0, 0, plate_thickness/2 + rib_height - reinforcement_rib_height/2) * Box(reinforcement_rib_width, plate_width - 2*rib_width, reinforcement_rib_height)
result = result + reinforcement

shaft_r = hole_diameter / 2
csk_r = countersink_diameter / 2
csk_half_angle = math.radians(countersink_angle / 2)
csk_depth = (csk_r - shaft_r) / math.tan(csk_half_angle)

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    shaft = Pos(x, y, 0) * Cylinder(shaft_r, plate_thickness + rib_height + 20)
    result = result - shaft
    csk = Pos(x, y, plate_thickness/2 + rib_height - csk_depth/2) * Cone(shaft_r, csk_r, csk_depth)
    result = result - csk

vertical_edges = result.edges().filter_by(Axis.Z)
result = fillet(vertical_edges, fillet_radius)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")