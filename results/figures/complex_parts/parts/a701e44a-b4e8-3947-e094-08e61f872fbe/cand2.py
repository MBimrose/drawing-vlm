from build123d import *

horizontal_length = 80.0
vertical_length = 70.0
leg_thickness = 8.0
leg_width = 20.0
fillet_radius = 4.0
slot_width = 8.0
slot_height = 30.0
slot_offset_from_bottom = 20.0
mount_hole_diameter = 5.0
mount_hole_head_diameter = 9.0
mount_hole_head_angle = 90.0
mount_hole_spacing = 30.0
rib_width = 6.0
rib_height = 12.0
rib_spacing = 8.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_length, 0), (horizontal_length, vertical_length),
                     (horizontal_length - leg_thickness, vertical_length),
                     (horizontal_length - leg_thickness, leg_width),
                     (0, leg_width), close=True)
        make_face()
    extrude(amount=leg_thickness)

solid_body = p.part

z_edges = solid_body.edges().filter_by(Axis.Z)
max_x_edges = z_edges.sort_by(Axis.X)[-2:]
solid_body = fillet(max_x_edges, fillet_radius)

slot_center_y = slot_offset_from_bottom + slot_height / 2
slot_box = Pos(horizontal_length - leg_thickness / 2, slot_center_y, leg_thickness / 2) * Box(leg_thickness, slot_height, slot_width)
solid_body = solid_body - slot_box

hole_y_positions = [vertical_length / 2 - mount_hole_spacing / 2, vertical_length / 2 + mount_hole_spacing / 2]
for y in hole_y_positions:
    csk = Pos(horizontal_length - leg_thickness / 2, y, leg_thickness / 2) * CounterSinkHole(mount_hole_diameter / 2, mount_hole_head_diameter / 2, mount_hole_head_angle)
    solid_body = solid_body - csk

rib_count = int((horizontal_length - 2 * leg_thickness) // (rib_width + rib_spacing))
for i in range(rib_count):
    rib_x = leg_thickness + rib_spacing / 2 + i * (rib_width + rib_spacing)
    rib = Pos(rib_x, 0, leg_thickness / 4) * Box(rib_width, rib_height, leg_thickness / 2)
    solid_body = solid_body + rib

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")