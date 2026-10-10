from build123d import *

leg_length_horizontal = 80.0
leg_length_vertical = 70.0
bracket_thickness = 8.0
profile_thickness = 15.0
boss_diameter = 30.0
boss_height = 20.0
thread_hole_diameter = 10.0
chamfer_size = 2.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
mount_hole_offset = profile_thickness + 10.0
vertical_hole_offset = profile_thickness + 12.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length_horizontal, 0))
            l2 = Line(l1 @ 1, (leg_length_horizontal, profile_thickness))
            l3 = Line(l2 @ 1, (profile_thickness, profile_thickness))
            l4 = Line(l3 @ 1, (profile_thickness, leg_length_vertical + profile_thickness))
            l5 = Line(l4 @ 1, (0, leg_length_vertical + profile_thickness))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
inner_corner_x = profile_thickness
inner_corner_y = profile_thickness

solid_body = solid_body + Pos(inner_corner_x, inner_corner_y, bracket_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body - Pos(inner_corner_x, inner_corner_y, bracket_thickness + boss_height/2) * Cylinder(thread_hole_diameter/2, boss_height)

for x in [mount_hole_offset, mount_hole_offset + mount_hole_spacing, mount_hole_offset + 2 * mount_hole_spacing]:
    solid_body = solid_body - Pos(x, 0, bracket_thickness/2) * Cylinder(mount_hole_diameter/2, bracket_thickness)

for y in [vertical_hole_offset, vertical_hole_offset + mount_hole_spacing]:
    solid_body = solid_body - Pos(0, y, bracket_thickness/2) * Cylinder(mount_hole_diameter/2, bracket_thickness)

top_faces = [f for f in solid_body.faces().filter_by(Axis.Z) if f.center().Z > 0]
top_edges = []
for f in top_faces:
    top_edges.extend(f.edges())
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "L_bracket"
export_step(part, OUTPUT_PATH)