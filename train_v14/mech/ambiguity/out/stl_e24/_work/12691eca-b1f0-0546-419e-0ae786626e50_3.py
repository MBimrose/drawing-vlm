from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
leg_thickness = 10.0
bracket_thickness = 10.0
inner_fillet_radius = 2.0
outer_fillet_radius = 4.0
clearance_hole_diameter = 4.0
clearance_hole_offset = 15.0
mount_hole_diameter = 5.0
mount_hole_counterbore_diameter = 8.0
mount_hole_counterbore_depth = 3.0
mount_hole_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length_short),
                     (0, leg_length_short), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

outer_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X) < 0.1 or abs(e.center().X - leg_length_long) < 0.1 or abs(e.center().Y) < 0.1 or abs(e.center().Y - leg_length_short) < 0.1]
solid_body = fillet(outer_edges, outer_fillet_radius)

solid_body = solid_body - Pos(clearance_hole_offset, 0, bracket_thickness/2) * Rot(90, 0, 0) * Cylinder(clearance_hole_diameter/2, 200)

solid_body = solid_body - Pos(leg_length_long, mount_hole_offset, bracket_thickness/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, 200)

solid_body = solid_body - Pos(leg_length_long - mount_hole_counterbore_depth/2, mount_hole_offset, bracket_thickness/2) * Rot(0, 90, 0) * Cylinder(mount_hole_counterbore_diameter/2, mount_hole_counterbore_depth)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")