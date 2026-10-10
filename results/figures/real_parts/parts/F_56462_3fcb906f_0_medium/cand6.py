from build123d import *

outer_width = 80.0
outer_height = 30.0
wall_thickness = 5.0
inner_diameter = 18.5
extrude_depth = 30.0
fillet_radius = 2.0
notch_width = 10.0
notch_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-outer_width/2, outer_height/2), (outer_width/2, outer_height/2))
            l2 = Line(l1@1, (outer_width/2, outer_height/2 - wall_thickness))
            l3 = Line(l2@1, (inner_diameter/2 + wall_thickness, outer_height/2 - wall_thickness))
            a1 = ThreePointArc(l3@1, (inner_diameter/2 + wall_thickness, -outer_height/2), (-(inner_diameter/2 + wall_thickness), outer_height/2 - wall_thickness))
            l4 = Line(a1@1, (-outer_width/2, outer_height/2 - wall_thickness))
            l5 = Line(l4@1, (-outer_width/2, outer_height/2))
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part
solid_body = solid_body - Cylinder(inner_diameter/2, extrude_depth * 2)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "notched_block_with_hole"
export_step(part, "output.step")