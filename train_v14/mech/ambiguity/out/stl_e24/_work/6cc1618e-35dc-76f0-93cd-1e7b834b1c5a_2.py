from build123d import *

outer_radius = 30.0
inner_radius = 20.0
length = 80.0
wall_thickness = outer_radius - inner_radius
groove_depth = 2.0
groove_start = 30.0
groove_length = 20.0
chamfer_size = 1.0
hole_diameter = 5.0
hole_offset = 15.0
slot_width = 8.0
slot_height = 4.0
slot_offset = 25.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, length))
            l2 = Line(l1 @ 1, (inner_radius, length))
            l3 = Line(l2 @ 1, (inner_radius, groove_start + groove_length))
            l4 = Line(l3 @ 1, (inner_radius + groove_depth, groove_start + groove_length))
            l5 = Line(l4 @ 1, (inner_radius + groove_depth, groove_start))
            l6 = Line(l5 @ 1, (inner_radius, groove_start))
            l7 = Line(l6 @ 1, (inner_radius, 0))
            l8 = Line(l7 @ 1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

hole_cyl = Pos(outer_radius - wall_thickness/2, wall_thickness/2, length - hole_offset) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, wall_thickness)
solid_body = solid_body - hole_cyl

slot_box = Pos(outer_radius - wall_thickness/2, wall_thickness/2, length - slot_offset) * Box(slot_width, wall_thickness, slot_height)
solid_body = solid_body - slot_box

part = solid_body
part.name = "revolved_tube_with_groove_hole_slot"
export_step(part, "output.step")