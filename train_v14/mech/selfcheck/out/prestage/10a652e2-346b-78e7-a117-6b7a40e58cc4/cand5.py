from build123d import *

leg_length_x = 80.0
leg_length_y = 60.0
thickness = 10.0
depth = 20.0
rib_thickness = 5.0
rib_height = 5.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset = 10.0

profile_points = [
    (0, 0),
    (leg_length_x, 0),
    (leg_length_x, thickness),
    (thickness, thickness),
    (thickness, leg_length_y),
    (0, leg_length_y),
]

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(*profile_points, close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part
rib = Pos(rib_thickness/2, rib_height/2, depth/2) * Box(rib_thickness, rib_height, depth)
solid_body = solid_body + rib
solid_body = fillet(solid_body.edges(), fillet_radius)

hole_positions = [
    (hole_offset, hole_offset),
    (hole_offset + hole_spacing, hole_offset),
    (hole_offset + 2 * hole_spacing, hole_offset),
    (hole_offset, hole_offset + hole_spacing),
    (hole_offset, hole_offset + 2 * hole_spacing),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, depth/2) * Cylinder(hole_diameter/2, depth)

part = solid_body
part.name = "L_bracket_with_rib"
export_step(part, "output.step")