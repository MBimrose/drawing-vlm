from build123d import *

bracket_length = 80.0
bracket_width = 30.0
bracket_thickness = 8.0
pocket_length = 40.0
pocket_width = 12.0
pocket_depth = 4.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_x = 20.0
hole_offset_y = 0.0
rib_height = 3.0
rib_width = 6.0
rib_thickness = 2.0
mount_hole_diameter = 8.0
mount_hole_spacing = 25.0
mount_hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(0, 0, bracket_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

through_hole = Pos(hole_offset_x - bracket_length/2, hole_offset_y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)
solid_body = solid_body - through_hole

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    mount_hole = Pos(-bracket_length/2 + mount_hole_offset, y, 0) * Cylinder(mount_hole_diameter/2, bracket_thickness)
    solid_body = solid_body - mount_hole

rib = Pos(0, 0, -rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "bracket"
export_step(part, "output.step")