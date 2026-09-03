from build123d import *

outer_width = 80.0
outer_height = 60.0
outer_radius = 12.0
wall_thickness = 5.0
thickness = 12.0
chamfer_size = 1.5
slot_width = 6.0
slot_length = 30.0
slot_depth = 3.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-outer_width/2, -outer_height/2), (outer_width/2, -outer_height/2))
            l2 = Line(l1@1, (outer_width/2, outer_height/2 - outer_radius))
            arc = ThreePointArc(l2@1, (0, outer_height/2 + outer_radius), (-outer_width/2, outer_height/2 - outer_radius))
            l3 = Line(arc@1, (-outer_width/2, -outer_height/2))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - 2 * wall_thickness
inner_radius = outer_radius - wall_thickness

with BuildPart() as p2:
    with BuildSketch() as sk2:
        with BuildLine() as bl2:
            l1 = Line((-inner_width/2, -inner_height/2), (inner_width/2, -inner_height/2))
            l2 = Line(l1@1, (inner_width/2, inner_height/2 - inner_radius))
            arc = ThreePointArc(l2@1, (0, inner_height/2 + inner_radius), (-inner_width/2, inner_height/2 - inner_radius))
            l3 = Line(arc@1, (-inner_width/2, -inner_height/2))
        make_face()
    extrude(amount=thickness - wall_thickness)

solid_body = solid_body - Pos(0, 0, wall_thickness) * p2.part

solid_body = solid_body - Pos(0, 0, slot_depth/2) * Box(slot_width, slot_length, slot_depth)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "custom_profile_with_cavity"
export_step(part, "output.step")