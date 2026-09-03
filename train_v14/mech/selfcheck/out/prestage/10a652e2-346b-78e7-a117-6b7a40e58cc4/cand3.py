from build123d import *

horizontal_length = 80.0
vertical_height = 60.0
thickness = 10.0
depth = 20.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_y = 25.0
hole_spacing = 30.0
gusset_thickness = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_length, 0), (horizontal_length, thickness),
                     (thickness, thickness), (thickness, vertical_height), (0, vertical_height), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part

for y in [hole_offset_y, hole_offset_y + hole_spacing]:
    solid_body = solid_body - Pos(thickness/2, y, depth/2) * Cylinder(hole_diameter/2, depth)

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((0, 0), (gusset_thickness, 0), (0, gusset_thickness), close=True)
        make_face()
    extrude(amount=depth)

solid_body = solid_body + g.part
solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")