from build123d import *

horizontal_length = 70.0
vertical_length = 55.0
leg_thickness = 12.0
bracket_thickness = 8.0
inner_fillet_radius = 3.0
slot_width = 10.0
slot_length = 20.0
slot_offset = 15.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
rib_height = 4.0
rib_width = 15.0
rib_thickness = 10.0
pocket_diameter = 8.0
pocket_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_length, 0), (horizontal_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_length),
                     (0, vertical_length), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edge = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
solid_body = fillet([inner_edge], inner_fillet_radius)

slot_center_x = horizontal_length - slot_offset - slot_length / 2
slot_center_y = leg_thickness / 2
solid_body = solid_body - Pos(slot_center_x, slot_center_y, bracket_thickness/2) * Box(slot_length, slot_width, bracket_thickness)

mount_center_x = horizontal_length - mount_hole_offset
mount_center_y = leg_thickness / 2
solid_body = solid_body - Pos(mount_center_x, mount_center_y, bracket_thickness/2) * Cylinder(mount_hole_diameter/2, bracket_thickness)

pocket_center_x = leg_thickness / 2
pocket_center_y = vertical_length - pocket_offset
solid_body = solid_body - Pos(pocket_center_x, pocket_center_y, bracket_thickness/2) * Cylinder(pocket_diameter/2, bracket_thickness)

rib = Pos(leg_thickness/2, leg_thickness/2, -rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")