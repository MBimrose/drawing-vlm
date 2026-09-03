from build123d import *

leg_length_x = 80.0
leg_length_y = 60.0
thickness = 10.0
fillet_radius = 4.0
hole_diameter = 4.0
hole_offset_x = 15.0
hole_offset_y = 30.0
rib_width = 15.0
rib_height = 20.0
rib_thickness = 5.0
counterbore_diameter = 8.0
counterbore_depth = 3.0
through_hole_diameter = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_x, 0), (leg_length_x, thickness),
                     (thickness, thickness), (thickness, leg_length_y),
                     (0, leg_length_y), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

solid_body = solid_body - Pos(hole_offset_x, leg_length_y/2, thickness/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, leg_length_y + 10)

solid_body = solid_body - Pos(leg_length_x, thickness/2, thickness/2) * Rot(0, 90, 0) * Cylinder(through_hole_diameter/2, leg_length_x + 10)
solid_body = solid_body - Pos(leg_length_x - counterbore_depth/2, thickness/2, thickness/2) * Rot(0, 90, 0) * Cylinder(counterbore_diameter/2, counterbore_depth)

rib = Pos(thickness/2, thickness/2, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket_with_rib"
export_step(part, "output.step")