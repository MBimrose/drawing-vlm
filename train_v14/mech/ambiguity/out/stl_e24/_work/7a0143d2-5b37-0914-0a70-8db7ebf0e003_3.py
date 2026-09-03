from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 70.0
leg_thickness = 10.0
bracket_depth = 10.0
slot_width = 6.0
slot_depth = 5.0
slot_offset_from_end = 30.0
hole_diameter = 5.0
hole_spacing = 40.0
hole_offset_from_end = 20.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_thickness, 0), (leg_thickness, vertical_leg_length - leg_thickness),
                     (leg_thickness + horizontal_leg_length, vertical_leg_length - leg_thickness),
                     (leg_thickness + horizontal_leg_length, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

slot_center_x = leg_thickness + slot_offset_from_end + slot_width / 2
slot_center_y = vertical_leg_length - slot_depth / 2
slot_cut = Pos(slot_center_x, slot_center_y, bracket_depth / 2) * Box(slot_width, slot_depth, bracket_depth)
solid_body = solid_body - slot_cut

hole_center_x = leg_thickness + hole_offset_from_end
hole_center_y = vertical_leg_length
for dx in [-hole_spacing / 2, hole_spacing / 2]:
    hx = hole_center_x + dx
    hy = hole_center_y - leg_thickness / 2
    hole_cut = Pos(hx, hy, bracket_depth / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, leg_thickness)
    solid_body = solid_body - hole_cut

chamfer_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[:1]
solid_body = chamfer(chamfer_edges, chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")