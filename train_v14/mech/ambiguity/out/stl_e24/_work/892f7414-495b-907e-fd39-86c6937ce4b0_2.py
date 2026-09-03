from build123d import *

bracket_length = 80.0
bracket_width = 30.0
bracket_thickness = 10.0
gusset_thickness = 4.0
gusset_height = 20.0
hole_diameter = 10.0
rib_height = 3.0
rib_width = 2.0
rib_count = 4
rib_margin = 5.0
chamfer_size = 0.5

base = Box(bracket_length, bracket_width, bracket_thickness)
gusset = Pos(-bracket_length/4, 0, -bracket_thickness/2 - gusset_height/2) * Box(gusset_thickness, bracket_width, gusset_height)
result = base + gusset

result = result - Cylinder(hole_diameter/2, 100)

rib_spacing = (bracket_width - 2 * rib_margin) / (rib_count - 1)
for i in range(rib_count):
    y_pos = -bracket_width/2 + rib_margin + i * rib_spacing
    rib = Pos(-bracket_length/4, y_pos, bracket_thickness/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)
    result = result + rib

top_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-rib_count:]
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "bracket_with_gusset_and_ribs"
export_step(part, "output.step")