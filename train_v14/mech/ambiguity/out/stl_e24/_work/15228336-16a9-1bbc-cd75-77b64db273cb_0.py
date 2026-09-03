from build123d import *

base_length = 80.0
base_width = 20.0
base_thickness = 10.0
rib_length = 30.0
rib_width = 6.0
rib_height = 10.0
rib_offset_x = 25.0
rib_offset_y = base_width/2 + rib_width/2
notch_width = 4.0
notch_depth = 3.0
notch_offset_x = rib_offset_x - rib_length/2 + notch_width/2 + 5.0
notch_offset_y = rib_offset_y
hole_diameter = 4.0
hole_depth = 5.0
hole_spacing = 20.0
hole_offset_x = 15.0
hole_offset_y = 0.0
chamfer_size = 0.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
rib = Pos(rib_offset_x, rib_offset_y, base_thickness) * Box(rib_length, rib_width, rib_height)
notch = Pos(notch_offset_x, notch_offset_y, base_thickness + rib_height/2 - notch_depth/2) * Box(notch_width, notch_width, notch_depth)

result = base + rib - notch

for i in range(3):
    hx = hole_offset_x + i * hole_spacing
    hy = hole_offset_y
    result = result - Pos(hx, hy, base_thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

top_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "base_with_rib_notch_holes"
export_step(part, "output.step")