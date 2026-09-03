from build123d import *

panel_width = 80.0
panel_height = 50.0
panel_thickness = 5.0
corner_fillet_radius = 4.0
hole_diameter = 7.0
hole_spacing = 8.0
hole_count = 9
hole_row_y = -panel_height / 4
pocket_radius = 8.0
pocket_depth = panel_thickness / 2
rib_width = 20.0
rib_height = 10.0
rib_thickness = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(panel_width, panel_height)
    extrude(amount=panel_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, hole_row_y, 0) * Cylinder(hole_diameter / 2, panel_thickness * 2)

solid_body = solid_body - Pos(0, 0, panel_thickness - pocket_depth / 2) * Cylinder(pocket_radius, pocket_depth)

rib = Pos(0, -panel_height / 2 + rib_height / 2, rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "panel_with_rib"
export_step(part, "output.step")