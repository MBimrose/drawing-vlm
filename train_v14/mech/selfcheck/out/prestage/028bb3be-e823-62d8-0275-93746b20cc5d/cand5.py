from build123d import *
import math

outer_diameter = 80.0
outer_radius = outer_diameter / 2.0
pulley_width = 20.0
shaft_diameter = 30.0
shaft_radius = shaft_diameter / 2.0
tab_width = 12.0
tab_height = 6.0
rib_height = 4.0
rib_width = 3.0
rib_count = 12
set_screw_diameter = 2.0
chamfer_size = 0.5

base = Cylinder(outer_radius, pulley_width)
tab = Pos(outer_radius, 0, pulley_width/2) * Box(tab_height, rib_width, pulley_width)
result = base + tab

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Pos(outer_radius + rib_height/2, 0, pulley_width/2) * Rot(0, 0, angle) * Box(rib_height, rib_width, pulley_width)
    result = result + rib

result = result - Cylinder(shaft_radius, pulley_width)
result = result - Pos(outer_radius + tab_height/2, 0, pulley_width/2) * Cylinder(set_screw_diameter/2, pulley_width)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "pulley"
export_step(part, "output.step")