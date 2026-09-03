from build123d import *

leg_length = 60.0
leg_width = 20.0
thickness = 10.0
rib_thickness = 4.0
rib_height = 2.0
pocket_width = 12.0
pocket_depth = 6.0
hole_diameter = 4.0
hole_offset = 15.0

vertical_leg = Pos(leg_width/2, leg_length/2, thickness/2) * Box(leg_width, leg_length, thickness)
horizontal_leg = Pos(leg_length/2, leg_width/2, thickness/2) * Box(leg_length, leg_width, thickness)
base = vertical_leg + horizontal_leg

inner_rib = Pos(leg_width/2, leg_width/2, thickness/2) * Box(rib_thickness, rib_thickness, thickness)
base = base + inner_rib

outer_rib_v = Pos(leg_width/2, leg_length + rib_height/2, thickness/2) * Box(rib_thickness, rib_height, leg_width)
base = base + outer_rib_v

outer_rib_h = Pos(leg_length + rib_height/2, leg_width/2, thickness/2) * Box(rib_height, rib_thickness, leg_width)
base = base + outer_rib_h

pocket = Pos(leg_width/2, leg_length/2, thickness - pocket_depth/2) * Box(pocket_width, pocket_width, pocket_depth)
base = base - pocket

hole = Pos(leg_length, leg_width/2, thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, 200)
base = base - hole

part = base
part.name = "L_bracket_with_ribs"
export_step(part, "output.step")