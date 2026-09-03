from build123d import *

leg_length = 80.0
leg_width = 60.0
thickness = 8.0
extrude_depth = 15.0
fillet_radius = 4.0
hole_diameter = 6.0
notch_width = 12.0
notch_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_width+thickness, 0), (leg_width+thickness, thickness),
                     (thickness, thickness), (thickness, leg_length), (0, leg_length), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, fillet_radius)

notch = Pos(leg_width + thickness - notch_width/2, thickness/2, extrude_depth - notch_depth/2) * Box(notch_width, notch_depth, notch_depth)
solid_body = solid_body - notch

hole_r = hole_diameter / 2
hole_h = extrude_depth + 10
for x, y in [(thickness/2, leg_length/3), (thickness/2, 2*leg_length/3), (leg_width + thickness/2, thickness/2)]:
    solid_body = solid_body - Pos(x, y, extrude_depth/2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")