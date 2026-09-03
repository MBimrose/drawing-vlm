from build123d import *

leg_length = 70.0
leg_width = 20.0
horizontal_length = 40.0
thickness = 8.0
fillet_radius = 4.0
hole_diameter = 5.0
cbore_diameter = 8.0
cbore_depth = 4.0
hole_offset_y = 30.0
rib_width = 5.0
rib_height = 12.0
rib_thickness = 2.0
rib_spacing = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (horizontal_length, 0))
            l2 = Line(l1@1, (horizontal_length, leg_width))
            l3 = Line(l2@1, (leg_width, leg_width))
            l4 = Line(l3@1, (leg_width, leg_length))
            l5 = Line(l4@1, (0, leg_length))
            l6 = Line(l5@1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

z_edges = solid_body.edges().filter_by(Axis.Z)
max_x_edges = z_edges.sort_by(Axis.X)[-2:]
solid_body = fillet(max_x_edges, fillet_radius)

shaft_r = hole_diameter / 2
cbore_r = cbore_diameter / 2
hole_x = horizontal_length
hole_y = leg_width / 2 + hole_offset_y
hole_z = thickness

solid_body = solid_body - Pos(hole_x, hole_y, hole_z) * Cylinder(shaft_r, thickness * 2)
solid_body = solid_body - Pos(hole_x, hole_y, hole_z) * Cylinder(cbore_r, cbore_depth)

rib_count = int((horizontal_length - leg_width) // rib_spacing)
for i in range(rib_count):
    rib_x = leg_width + rib_spacing / 2 + i * rib_spacing
    rib_y = leg_width / 2
    rib = Pos(rib_x, rib_y, rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")