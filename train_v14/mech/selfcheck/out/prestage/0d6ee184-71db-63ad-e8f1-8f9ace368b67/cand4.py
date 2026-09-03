from build123d import *

bracket_width = 70
bracket_height = 30
bracket_thickness = 10
rib_width = 40
rib_height = 12
fillet_radius = 2
hole_diameter = 5
hole_spacing = 30
hole_offset_y = 15

base = Box(bracket_width, bracket_height, bracket_thickness)
rib = Pos(0, bracket_height/2 + rib_height/2, 0) * Box(rib_width, rib_height, bracket_thickness)
solid_body = base + rib

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole_positions = [(-hole_spacing/2, -bracket_height/2 + hole_offset_y),
                  (hole_spacing/2, -bracket_height/2 + hole_offset_y),
                  (0, bracket_height/2 + rib_height/2)]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")