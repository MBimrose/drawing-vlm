from build123d import *

leg_length = 60.0
leg_height = 50.0
leg_thickness = 8.0
leg_width = 15.0
inner_fillet_radius = 3.0
chamfer_distance = 0.5
hole_diameter = 22.0
hole_center_x = 20.0
hole_center_y = 15.0
rib_width = 10.0
rib_height = 20.0
rib_thickness = leg_thickness

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length, 0))
            l2 = Line(l1 @ 1, (leg_length, leg_width))
            l3 = Line(l2 @ 1, (leg_width, leg_width))
            l4 = Line(l3 @ 1, (leg_width, leg_height))
            l5 = Line(l4 @ 1, (0, leg_height))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=leg_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), inner_fillet_radius)

rib = Pos(leg_width/2, leg_height/2, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

solid_body = solid_body - Pos(hole_center_x, hole_center_y, leg_thickness/2) * Cylinder(hole_diameter/2, leg_thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "L_bracket_with_rib"
export_step(part, "output.step")