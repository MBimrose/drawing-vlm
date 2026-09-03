from build123d import *

panel_width = 80.0
panel_height = 50.0
panel_thickness = 5.0
corner_fillet_radius = 4.0
hole_diameter = 7.0
hole_spacing = 8.0
hole_count = 9
rib_width = 10.0
rib_height = 30.0
rib_thickness = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(panel_width, panel_height)
    extrude(amount=panel_thickness)
base = p.part
base = fillet(base.edges().filter_by(Axis.Z), corner_fillet_radius)

rib = Pos(0, 0, panel_thickness - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
result = base + rib

start_x = -((hole_count - 1) * hole_spacing) / 2
hole_y = -panel_height / 4
for i in range(hole_count):
    x = start_x + i * hole_spacing
    result = result - Pos(x, hole_y, panel_thickness/2) * Cylinder(hole_diameter/2, panel_thickness + 10)

result = result - Pos(0, 0, panel_thickness - panel_thickness/4) * Cylinder(8.0, panel_thickness/2)

part = result
part.name = "panel_with_rib_and_holes"
export_step(part, "output.step")