from build123d import *

leg_length = 60.0
leg_width = 20.0
thickness = 10.0
pocket_width = 12.0
pocket_depth = 6.0
pocket_offset = 10.0
hole_diameter = 4.0
rib_thickness = 2.0
rib_width = 4.0
rib_height = 20.0

horizontal = Pos(leg_length/2, leg_width/2, thickness/2) * Box(leg_length, leg_width, thickness)
vertical = Pos(leg_width/2, leg_length/2, thickness/2) * Box(leg_width, leg_length, thickness)
base = horizontal + vertical

pocket = Pos(pocket_offset, leg_width/2, thickness) * Box(pocket_width, pocket_width, pocket_depth)
base = base - pocket

hole1 = Pos(leg_length/2, leg_width/2, thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, leg_length)
base = base - hole1

hole2 = Pos(leg_width/2, leg_length/2, thickness/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, leg_length)
base = base - hole2

rib1 = Pos(leg_length + rib_thickness/2, leg_width/2, thickness/2) * Box(rib_thickness, rib_width, rib_height)
base = base + rib1

rib2 = Pos(leg_width/2, leg_length + rib_thickness/2, thickness/2) * Box(rib_width, rib_thickness, rib_height)
base = base + rib2

part = base
part.name = "L_bracket_with_pocket_holes_and_ribs"
export_step(part, "output.step")