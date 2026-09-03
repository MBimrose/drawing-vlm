from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 5.0
boss_diameter = 20.0
boss_height = 10.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 4
fillet_radius = 1.5
chamfer_distance = 0.5
rib_thickness = 2.0
rib_height = 2.0
rib_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

boss = Pos(0, 0, bracket_thickness + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

rib = Pos(0, -bracket_width / 2 + rib_offset + rib_thickness / 2, -rib_height / 2) * Box(bracket_length - 2 * rib_offset, rib_thickness, rib_height)
solid_body = solid_body + rib

hole_h = bracket_thickness + boss_height + rib_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, hole_h)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")