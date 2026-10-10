from build123d import *
import math

shaft_diameter = 20.0
shaft_radius = shaft_diameter / 2.0
central_length = 30.0
flange_thickness = 15.0
flange_outer_diameter = 60.0
flange_outer_radius = flange_outer_diameter / 2.0
hole_diameter = 6.0
hole_pitch_radius = 22.0
fillet_radius = 2.0
slot_width = 4.0
slot_length = 12.0
slot_depth = shaft_radius - 1.0

central_cyl = Cylinder(shaft_radius, central_length)
lower_flange = Pos(0, 0, -(central_length/2 + flange_thickness/2)) * Cylinder(flange_outer_radius, flange_thickness)
upper_flange = Pos(0, 0, (central_length/2 + flange_thickness/2)) * Cylinder(flange_outer_radius, flange_thickness)

base = central_cyl + lower_flange + upper_flange

for i in range(6):
    angle = math.radians(i * 360.0 / 6)
    px = hole_pitch_radius * math.cos(angle)
    py = hole_pitch_radius * math.sin(angle)
    base = base - Pos(px, py, -(central_length/2 + flange_thickness/2)) * Cylinder(hole_diameter/2, flange_thickness)
    base = base - Pos(px, py, central_length/2 + flange_thickness/2) * Cylinder(hole_diameter/2, flange_thickness)

slot = Pos(flange_outer_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_length)
base = base - slot

base = fillet(base.edges(), fillet_radius)

part = base
part.name = "shaft_with_flanges"
export_step(part, OUTPUT_PATH)