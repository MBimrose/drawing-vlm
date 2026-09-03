from build123d import *

outer_width = 80.0
outer_height = 60.0
outer_thickness = 12.0
wall_thickness = 5.0
slot_width = 6.0
slot_length = 30.0
slot_depth = 3.0
chamfer_size = 1.0
hole_diameter = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-outer_width/2, -outer_height/2), (outer_width/2, -outer_height/2))
            l2 = Line(l1@1, (outer_width/2, outer_height/2 - outer_width/4))
            arc = ThreePointArc(l2@1, (0, outer_height/2 + outer_width/4), (-outer_width/2, outer_height/2 - outer_width/4))
            l3 = Line(arc@1, l1@0)
        make_face()
    extrude(amount=outer_thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_cut = Pos(0, 0, slot_depth/2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot_cut

hole_cut = Pos(0, 0, outer_thickness/2) * Cylinder(hole_diameter/2, outer_thickness)
solid_body = solid_body - hole_cut

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "shelled_box_with_slot_and_hole"
export_step(part, "output.step")