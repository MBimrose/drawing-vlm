from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 60.0
thickness = 10.0
inner_fillet_radius = 2.0
outer_fillet_radius = 4.0
mount_hole_diameter = 4.0
mount_hole_offset = 15.0
counterbore_diameter = 5.0
counterbore_depth = 3.0
rib_width = 6.0
rib_height = 6.0
rib_thickness = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, thickness),
                     (thickness, thickness), (thickness, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

outer_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X) < 0.1 or abs(e.center().X - horizontal_leg_length) < 0.1 or abs(e.center().Y) < 0.1 or abs(e.center().Y - vertical_leg_length) < 0.1]
solid_body = fillet(outer_edges, outer_fillet_radius)

solid_body = solid_body - Pos(mount_hole_offset, 0, thickness/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, vertical_leg_length)

solid_body = solid_body - Pos(horizontal_leg_length, thickness/2, thickness/2) * Rot(0, 90, 0) * Cylinder(counterbore_diameter/2, horizontal_leg_length)
solid_body = solid_body - Pos(horizontal_leg_length - counterbore_depth/2, thickness/2, thickness/2) * Rot(0, 90, 0) * Cylinder((counterbore_diameter+3)/2, counterbore_depth)

rib = Pos(thickness/2, thickness/2, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")