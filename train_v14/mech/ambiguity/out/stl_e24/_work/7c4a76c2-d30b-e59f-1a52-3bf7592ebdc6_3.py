from build123d import *

vertical_leg_height = 60.0
horizontal_leg_length = 70.0
leg_width = 30.0
thickness = 8.0
inner_fillet_radius = 5.0
mount_hole_diameter = 6.0
mount_hole_cbore_diameter = 10.0
mount_hole_cbore_depth = 3.0
mount_hole_spacing = 40.0
mount_hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_width, 0), (leg_width, vertical_leg_height),
                     (leg_width + horizontal_leg_length, vertical_leg_height),
                     (leg_width + horizontal_leg_length, vertical_leg_height + leg_width),
                     (0, vertical_leg_height + leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - leg_width) < 1e-3 and abs(e.center().Y - vertical_leg_height) < 1e-3]
solid_body = fillet(inner_edges, inner_fillet_radius)

for x, y in [(leg_width/2, mount_hole_offset), (leg_width/2, mount_hole_offset + mount_hole_spacing)]:
    solid_body = solid_body - Pos(x, y, thickness - mount_hole_cbore_depth/2) * Cylinder(mount_hole_cbore_diameter/2, mount_hole_cbore_depth)
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(mount_hole_diameter/2, thickness + 1)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")