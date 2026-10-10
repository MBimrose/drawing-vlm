from build123d import *

leg_length = 80.0
leg_width = 40.0
thickness = 15.0
wall_thickness = 4.0
bearing_diameter = 20.0
bearing_depth = 12.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_width, 0), (leg_width, leg_length/2),
                     (leg_width/2, leg_length/2), (leg_width/2, leg_length),
                     (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

bearing_hole = Pos(leg_width/2, leg_length - bearing_depth/2, thickness/2) * Rot(90, 0, 0) * Cylinder(bearing_diameter/2, bearing_depth)
solid_body = solid_body - bearing_hole

for x, y in [(leg_width/2 - mount_hole_spacing/2, leg_length/2),
             (leg_width/2 + mount_hole_spacing/2, leg_length/2)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")