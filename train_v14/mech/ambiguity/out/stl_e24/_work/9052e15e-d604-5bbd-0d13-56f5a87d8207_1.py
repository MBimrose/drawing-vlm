from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
thickness = 8.0
bracket_depth = 20.0
rib_width = 4.0
rib_height = 20.0
rib_offset_from_top = 10.0
hole_diameter = 5.0
cbore_diameter = 8.0
cbore_depth = 3.0
hole_spacing = 30.0
hole_offset_from_corner = 15.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (thickness, vertical_leg_length),
                     (thickness, thickness), (horizontal_leg_length, thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

rib_center_y = vertical_leg_length - rib_offset_from_top - rib_height / 2
rib = Pos(rib_width / 2, rib_center_y, bracket_depth / 2) * Box(rib_width, rib_height, thickness)
solid_body = solid_body + rib

for i in range(2):
    hx = hole_offset_from_corner + i * hole_spacing
    hy = thickness / 2
    solid_body = solid_body - Pos(hx, hy, 0) * Cylinder(hole_diameter / 2, bracket_depth + 1)
    solid_body = solid_body - Pos(hx, hy, 0) * Cylinder(cbore_diameter / 2, cbore_depth)

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")