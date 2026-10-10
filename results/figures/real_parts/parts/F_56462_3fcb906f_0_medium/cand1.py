from build123d import *

channel_width = 40.0
channel_height = 30.0
wall_thickness = 4.0
extrude_length = 30.0
inner_fillet_radius = 3.0
hole_diameter = 18.5
hole_offset_x = 0.0
hole_offset_y = 0.0

outer_width = channel_width + 2 * wall_thickness
outer_height = channel_height + wall_thickness

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-outer_width/2, outer_height/2), (outer_width/2, outer_height/2))
            l2 = Line(l1@1, (outer_width/2, outer_height/2 - wall_thickness))
            l3 = Line(l2@1, (channel_width/2, outer_height/2 - wall_thickness))
            l4 = Line(l3@1, (channel_width/2, -outer_height/2 + wall_thickness))
            a1 = ThreePointArc(l4@1, (0, -outer_height/2), (-channel_width/2, -outer_height/2 + wall_thickness))
            l5 = Line(a1@1, (-channel_width/2, outer_height/2 - wall_thickness))
            l6 = Line(l5@1, (-outer_width/2, outer_height/2 - wall_thickness))
            l7 = Line(l6@1, (-outer_width/2, outer_height/2))
        make_face()
    extrude(amount=extrude_length)

solid_body = p.part
inner_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(inner_edges, inner_fillet_radius)
solid_body = solid_body - Pos(hole_offset_x, hole_offset_y, extrude_length/2) * Cylinder(hole_diameter/2, extrude_length + 10)

part = solid_body
part.name = "u_channel"
export_step(part, "output.step")