from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
bracket_thickness = 10.0
inner_fillet_radius = 2.0
hole_diameter = 6.0
hole_offset_from_end = 30.0
rib_width = 10.0
rib_height = 10.0
rib_thickness = 5.0
mount_hole_diameter = 5.0
mount_hole_spacing = 20.0
mount_hole_offset = 25.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, bracket_thickness),
                     (bracket_thickness, bracket_thickness), (bracket_thickness, leg_length_short),
                     (0, leg_length_short), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - bracket_thickness) < 0.1 and abs(e.center().Y - bracket_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

rib = Pos(bracket_thickness/2, bracket_thickness/2, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

hole_cyl = Pos(bracket_thickness/2, leg_length_short - hole_offset_from_end, bracket_thickness/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, leg_length_short)
solid_body = solid_body - hole_cyl

for i in range(3):
    x = mount_hole_offset + i * mount_hole_spacing
    y = bracket_thickness / 2
    mount_cyl = Pos(x, y, bracket_thickness) * Cylinder(mount_hole_diameter/2, bracket_thickness)
    solid_body = solid_body - mount_cyl

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")