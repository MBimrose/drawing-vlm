from build123d import *
import math

outer_diameter = 40
length = 80
wall_thickness = 3
tab_width = 12
tab_height = 6
tab_thickness = 4
hole_diameter = 8
counterbore_diameter = 12
counterbore_depth = 4

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

tab = Pos(outer_radius, 0, -tab_width/2) * Box(tab_thickness, tab_height, tab_width)
solid_body = solid_body + tab

cbore = Pos(outer_radius - counterbore_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(counterbore_diameter/2, counterbore_depth)
shaft = Pos(0, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, outer_diameter + 20)
solid_body = solid_body - cbore - shaft

part = solid_body
part.name = "hollow_cylinder_with_tab_and_counterbore"
export_step(part, "output.step")