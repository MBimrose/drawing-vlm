from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
thickness = 10.0
depth = 20.0
inner_fillet_radius = 2.0
countersink_diameter = 6.0
countersink_angle = 90.0
countersink_depth = 4.0
hole_offset_from_end = 20.0
rib_width = 5.0
rib_height = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, thickness),
                     (thickness, thickness), (thickness, leg_length_short),
                     (0, leg_length_short), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part

# Cut inner corner relief
solid_body = solid_body - Pos(thickness/2, thickness/2, depth/2) * Box(thickness, thickness, depth)

# Add rib
solid_body = solid_body + Pos(rib_width/2, rib_height/2, depth/2) * Box(rib_width, rib_height, depth)

# Fillet all edges
solid_body = fillet(solid_body.edges(), inner_fillet_radius)

# Countersink hole on short leg
hole_x = thickness / 2
hole_y = leg_length_short - hole_offset_from_end
solid_body = solid_body - Pos(hole_x, hole_y, depth) * CounterSinkHole(countersink_diameter/2, countersink_diameter/2, countersink_depth, countersink_angle)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")