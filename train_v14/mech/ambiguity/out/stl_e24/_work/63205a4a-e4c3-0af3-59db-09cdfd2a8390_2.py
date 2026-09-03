from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 80.0
leg_width = 20.0
thickness = 8.0
rib_height = 30.0
rib_thickness = 4.0
hole_diameter = 5.0
hole_offset_from_bottom = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (0, vertical_leg_length), (leg_width, vertical_leg_length),
                     (leg_width, leg_width), (horizontal_leg_length, leg_width),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=thickness)
base = p.part

with BuildPart() as p_rib:
    with BuildSketch() as sk_rib:
        with BuildLine() as bl_rib:
            Polyline((leg_width, leg_width), (leg_width + rib_height, leg_width),
                     (leg_width, leg_width + rib_height), close=True)
        make_face()
    extrude(amount=rib_thickness)
rib = p_rib.part

solid = base + rib

hole_center_x = leg_width / 2.0
hole_center_y = hole_offset_from_bottom
solid = solid - Pos(hole_center_x, hole_center_y, 0) * Cylinder(hole_diameter/2, thickness * 2)

z_edges = solid.edges().filter_by(Axis.Z)
min_x_edges = z_edges.sort_by(Axis.X)[:1]
min_xy_edge = min_x_edges.sort_by(Axis.Y)[:1]
solid = chamfer(min_xy_edge, chamfer_size)

y_edges = solid.edges().filter_by(Axis.Y)
min_z_edges = y_edges.sort_by(Axis.Z)[:1]
min_x_yz_edge = min_z_edges.sort_by(Axis.X)[:1]
solid = chamfer(min_x_yz_edge, chamfer_size)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")