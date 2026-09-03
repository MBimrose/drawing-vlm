from build123d import *

leg_long = 80.0
leg_short = 60.0
thickness = 10.0
fillet_radius = 4.0
hole_diameter = 4.0
hole_offset = 15.0
counterbore_diameter = 8.0
counterbore_depth = 3.0
through_hole_diameter = 5.0
gusset_width = 15.0
gusset_thickness = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_long, 0), (leg_long, thickness), (thickness, thickness), (thickness, leg_short), (0, leg_short), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

solid_body = solid_body - Pos(hole_offset, thickness/2, thickness/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, thickness)
solid_body = solid_body - Pos(leg_long, thickness/2, thickness/2) * Rot(0, 90, 0) * Cylinder(through_hole_diameter/2, leg_long)
solid_body = solid_body - Pos(leg_long - counterbore_depth/2, thickness/2, thickness/2) * Rot(0, 90, 0) * Cylinder(counterbore_diameter/2, counterbore_depth)

with BuildPart() as g:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((0, 0), (gusset_width, 0), (0, gusset_width), close=True)
        make_face()
    extrude(amount=gusset_thickness)

solid_body = solid_body + g.part

part = solid_body
part.name = "L_bracket_with_gusset"
export_step(part, "output.step")