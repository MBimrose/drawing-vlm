from build123d import *

bracket_width = 60.0
bracket_height = 50.0
bracket_thickness = 10.0
gusset_extension = 20.0
gusset_height = 30.0
slot_length = 50.0
slot_width = 6.0
slot_offset_from_top = 10.0
hole_diameter = 6.0
hole_offset_x = 15.0
hole_offset_y = 25.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (bracket_width, 0), (bracket_width + gusset_extension, gusset_height),
                     (bracket_width, bracket_height), (0, bracket_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

slot_center_x = bracket_width / 2
slot_center_y = bracket_height - slot_offset_from_top - slot_width / 2
solid_body = solid_body - Pos(slot_center_x, slot_center_y, bracket_thickness / 2) * Box(slot_length, slot_width, bracket_thickness)

solid_body = solid_body - Pos(hole_offset_x, hole_offset_y, bracket_thickness / 2) * Cylinder(hole_diameter / 2, bracket_thickness)

mount_y = bracket_height
mount_x1 = bracket_width / 2 - mount_hole_spacing / 2
mount_x2 = bracket_width / 2 + mount_hole_spacing / 2
solid_body = solid_body - Pos(mount_x1, mount_y, bracket_thickness / 2) * Cylinder(mount_hole_diameter / 2, bracket_thickness)
solid_body = solid_body - Pos(mount_x2, mount_y, bracket_thickness / 2) * Cylinder(mount_hole_diameter / 2, bracket_thickness)

part = solid_body
part.name = "bracket_with_gusset"
export_step(part, "output.step")