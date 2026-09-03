from build123d import *

bracket_width = 60.0
bracket_height = 40.0
bracket_thickness = 10.0
gusset_extension = 20.0
gusset_height = 30.0
fillet_radius = 1.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
mount_hole_offset = 10.0
slot_length = 50.0
slot_width = 6.0
slot_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-bracket_width/2, -bracket_height/2),
                (bracket_width/2, -bracket_height/2),
                (bracket_width/2 + gusset_extension, 0),
                (bracket_width/2, bracket_height/2),
                (-bracket_width/2, bracket_height/2),
                close=True
            )
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
positive_x_edges = [e for e in vertical_edges if e.center().X > 0]
solid_body = fillet(positive_x_edges, fillet_radius)

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(-bracket_width/2 + mount_hole_offset, y, bracket_thickness/2) * Cylinder(mount_hole_diameter/2, bracket_thickness)

solid_body = solid_body - Pos(0, slot_offset, bracket_thickness/2) * Box(slot_length, slot_width, bracket_thickness)

part = solid_body
part.name = "bracket_with_gusset"
export_step(part, "output.step")