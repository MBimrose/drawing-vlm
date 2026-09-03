from build123d import *

panel_width = 80.0
panel_height = 80.0
panel_thickness = 6.0
rib_width = 6.0
rib_height = 30.0
rib_thickness = 4.0
rib_offset_y = 10.0
hole_diameter = 5.0
hole_spacing = 12.0
num_holes = 5
chamfer_distance = 0.5

base = Box(panel_width, panel_height, panel_thickness)
left_rib = Pos(-panel_width/2 + rib_width/2, rib_offset_y + rib_height/2, 0) * Box(rib_width, rib_height, rib_thickness)
right_rib = Pos(panel_width/2 - rib_width/2, rib_offset_y + rib_height/2, 0) * Box(rib_width, rib_height, rib_thickness)

result = base + left_rib + right_rib

for i in range(num_holes):
    x = -((num_holes-1)*hole_spacing)/2 + i * hole_spacing
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, panel_thickness + 3)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "panel_with_ribs_and_holes"
export_step(part, "output.step")