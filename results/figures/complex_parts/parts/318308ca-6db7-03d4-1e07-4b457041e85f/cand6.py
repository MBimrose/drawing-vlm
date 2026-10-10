from build123d import *

leg_length = 80.0
leg_width = 30.0
thickness = 15.0
wall_thickness = 4.0
bearing_diameter = 20.0
bearing_depth = 12.0
hole_diameter = 6.0
hole_spacing = 30.0
hole_offset = 20.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_width + thickness, 0), (leg_width + thickness, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length), (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

bearing_cut = Pos(leg_width/2, leg_length, thickness/2) * Rot(90, 0, 0) * Cylinder(bearing_diameter/2, bearing_depth)
solid_body = solid_body - bearing_cut

for i in range(2):
    hx = leg_width + thickness/2 + i * hole_spacing
    hy = leg_length/2 + hole_offset
    solid_body = solid_body - Pos(hx, hy, thickness/2) * Cylinder(hole_diameter/2, thickness + 1)

vert_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vert_edges, fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")