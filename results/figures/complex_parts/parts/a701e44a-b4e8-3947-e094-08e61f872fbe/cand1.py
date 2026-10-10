from build123d import *
import math

leg_length = 80.0
leg_width = 20.0
leg_thickness = 8.0
vertical_leg_length = 70.0
pocket_length = 30.0
pocket_width = 12.0
pocket_offset = 20.0
hole_diameter = 6.0
countersink_diameter = 10.0
countersink_depth = 2.0
fillet_radius = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_length - leg_thickness, leg_width),
                     (leg_length - leg_thickness, vertical_leg_length),
                     (leg_length - 2 * leg_thickness, vertical_leg_length),
                     (leg_length - 2 * leg_thickness, leg_width),
                     (0, leg_width), close=True)
        make_face()
    extrude(amount=leg_thickness)

solid_body = p.part

pocket_center_x = pocket_offset + pocket_length / 2
pocket_center_y = leg_width / 2
pocket = Pos(pocket_center_x, pocket_center_y, 0) * Box(pocket_length, pocket_width, leg_thickness)
solid_body = solid_body - pocket

hole_center_x = leg_length - leg_thickness / 2
hole_center_y = vertical_leg_length / 2
shaft_hole = Pos(hole_center_x, hole_center_y, 0) * Cylinder(hole_diameter / 2, leg_thickness)
solid_body = solid_body - shaft_hole

csk_cone = Pos(hole_center_x, hole_center_y, leg_thickness - countersink_depth) * Cone(hole_diameter / 2, countersink_diameter / 2, countersink_depth)
solid_body = solid_body - csk_cone

vertical_edges = solid_body.edges().filter_by(Axis.Z)
outer_edges = [e for e in vertical_edges if e.center().X > 0]
solid_body = fillet(outer_edges, fillet_radius)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")