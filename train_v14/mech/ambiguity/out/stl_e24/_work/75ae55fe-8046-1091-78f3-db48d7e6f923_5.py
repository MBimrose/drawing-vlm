from build123d import *

bracket_width = 80.0
bracket_height = 25.0
bracket_thickness = 8.0
pocket_width = 40.0
pocket_height = 15.0
pocket_depth = 12.0
rib_width = 6.0
rib_height = 8.0
rib_thickness = 3.0
rib_spacing = 10.0
hole_diameter = 5.0
hole_offset = 8.0
hole_spacing = 12.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_width, bracket_thickness)
    extrude(amount=bracket_height)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

pocket = Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - Pos(0, -bracket_thickness/2 + pocket_depth/2, 0) * pocket

num_ribs = int((bracket_width - rib_spacing) // rib_spacing)
for i in range(num_ribs):
    x_pos = -bracket_width/2 + rib_spacing/2 + i * rib_spacing
    rib = Box(rib_width, rib_height, rib_thickness)
    solid_body = solid_body + Pos(x_pos, bracket_thickness/2 + rib_height/2, bracket_height/2) * rib

for i in range(2):
    z_pos = bracket_height/2 + (i - 0.5) * hole_spacing
    hole = Rot(90, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness + 10)
    solid_body = solid_body - Pos(-bracket_width/2 + hole_offset, 0, z_pos) * hole

for i in range(2):
    z_pos = bracket_height/2 + (i - 0.5) * hole_spacing
    hole = Rot(90, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness + 10)
    solid_body = solid_body - Pos(bracket_width/2 - hole_offset, 0, z_pos) * hole

part = solid_body
part.name = "bracket_with_pocket_ribs_holes"
export_step(part, "output.step")