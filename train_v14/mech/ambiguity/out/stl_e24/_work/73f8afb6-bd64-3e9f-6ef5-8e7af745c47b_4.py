from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
cap_height = 30.0
groove_width = 6.0
groove_depth = 2.0
groove_position = 12.0
chamfer_distance = 0.8
tab_width = 20.0
tab_height = 10.0
tab_thickness = 4.0
hole_diameter = 5.0
hole_spacing = 12.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

base = Cylinder(outer_radius, cap_height) - Cylinder(inner_radius, cap_height)
base = chamfer(base.edges(), chamfer_distance)

groove_cyl = Pos(0, 0, groove_position - groove_width / 2) * Cylinder(inner_radius - groove_depth, groove_width)
base = base - groove_cyl

tab = Pos(outer_radius + tab_thickness / 2, 0, 0) * Box(tab_thickness, tab_width, tab_height)
base = base + tab

for y in [-hole_spacing / 2, hole_spacing / 2]:
    hole = Pos(outer_radius + tab_thickness / 2, y, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, tab_thickness + 1)
    base = base - hole

part = base
part.name = "cap_with_groove_and_tab"
export_step(part, "output.step")