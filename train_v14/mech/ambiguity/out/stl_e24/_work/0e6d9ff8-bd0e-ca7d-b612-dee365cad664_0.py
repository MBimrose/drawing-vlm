from build123d import *

leg_length = 60.0
leg_width = 20.0
thickness = 10.0
rib_width = 4.0
rib_height = 20.0
rib_thickness = 2.0
pocket_width = 12.0
pocket_depth = 6.0
hole_diameter = 4.0
hole_offset = 30.0

vertical = Pos(leg_width/2, leg_length/2, thickness/2) * Box(leg_width, leg_length, thickness)
horizontal = Pos(leg_length/2, leg_width/2, thickness/2) * Box(leg_length, leg_width, thickness)
base = vertical + horizontal

rib_v = Pos(leg_width/2, leg_length + rib_thickness/2, thickness/2) * Box(rib_width, rib_thickness, rib_height)
rib_h = Pos(leg_length + rib_thickness/2, leg_width/2, thickness/2) * Box(rib_thickness, rib_width, rib_height)
base = base + rib_v + rib_h

pocket = Pos(leg_width/2, leg_width/2, thickness - pocket_depth/2) * Box(pocket_width, pocket_width, pocket_depth)
base = base - pocket

hole_h = Pos(leg_length, hole_offset, thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, 100)
hole_v = Pos(hole_offset, leg_length, thickness/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, 100)
base = base - hole_h - hole_v

part = base
part.name = "L_bracket_with_ribs"
export_step(part, "output.step")