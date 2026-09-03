from build123d import *

leg_length = 80.0
leg_width = 20.0
thickness = 4.0
rib_height = 12.0
rib_width = 6.0
rib_thickness = 2.0
hole_diameter = 5.0
counterbore_diameter = 8.0
counterbore_depth = 3.0
hole_spacing = 30.0
hole_offset_from_end = 15.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness), (thickness, thickness), (thickness, leg_length), (0, leg_length), close=True)
        make_face()
    extrude(amount=leg_width)

solid_body = p.part

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, fillet_radius)

rib = Pos(rib_thickness/2, leg_length - rib_height/2, leg_width/2) * Box(rib_thickness, rib_height, rib_width)
solid_body = solid_body + rib

for x, y in [(leg_length - hole_offset_from_end - hole_spacing/2, thickness/2),
             (leg_length - hole_offset_from_end + hole_spacing/2, thickness/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, leg_width + 1)
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(counterbore_diameter/2, counterbore_depth)

part = solid_body
part.name = "L_bracket_with_rib_and_holes"
export_step(part, "output.step")