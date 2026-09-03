from build123d import *
import math

panel_width = 80.0
panel_height = 80.0
panel_thickness = 6.0
rib_width = 30.0
rib_height = 20.0
rib_thickness = 4.0
hole_diameter = 5.0
countersink_diameter = 9.0
countersink_angle = 82.0
hole_spacing = 12.0
hole_count = 5
chamfer_size = 0.5

base = Box(panel_width, panel_height, panel_thickness)
rib = Pos(0, 0, -panel_thickness/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
result = base + rib

csk_radius = countersink_diameter / 2
csk_height = csk_radius / math.tan(math.radians(countersink_angle / 2))
bore_depth = panel_thickness + 10

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    bore = Pos(x, 0, panel_thickness/2 - bore_depth/2) * Cylinder(hole_diameter/2, bore_depth)
    csk = Pos(x, 0, panel_thickness/2 - csk_height/2) * Cone(0, csk_radius, csk_height)
    result = result - (bore + csk)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "panel_with_rib_and_holes"
export_step(part, "output.step")