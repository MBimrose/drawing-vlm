from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
leg_thickness = 10.0
bracket_depth = 12.0
fillet_radius = 2.0
clearance_hole_diameter = 4.5
clearance_hole_offset = 5.0
mount_hole_diameter = 6.0
mount_hole_offset = 5.0
rib_width = 6.0
rib_height = 6.0
rib_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

solid_body = solid_body - Pos(leg_thickness/2, vertical_leg_length - clearance_hole_offset, 0) * Cylinder(clearance_hole_diameter/2, bracket_depth + 1)
solid_body = solid_body - Pos(horizontal_leg_length/2, leg_thickness/2, 0) * Cylinder(mount_hole_diameter/2, bracket_depth + 1)
solid_body = solid_body - Pos(leg_thickness/2, vertical_leg_length/2, 0) * Cylinder(mount_hole_diameter/2, bracket_depth + 1)

rib = Pos(leg_thickness/2, leg_thickness/2, bracket_depth - rib_depth/2) * Box(rib_width, rib_height, rib_depth)
solid_body = solid_body + rib

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")