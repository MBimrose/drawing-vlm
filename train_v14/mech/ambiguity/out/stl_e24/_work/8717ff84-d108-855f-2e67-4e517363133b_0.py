from build123d import *

bracket_length = 80.0
bracket_height = 55.0
bracket_thickness = 10.0
gusset_width = 20.0
gusset_height = 30.0
slot_width = 6.0
slot_length = 50.0
slot_offset_y = 12.0
hole_diameter = 6.0
hole_spacing = 30.0
hole_offset_x = 10.0
fillet_radius = 1.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (bracket_length - gusset_width, 0), (bracket_length, bracket_height - gusset_height),
                     (bracket_length - gusset_width, bracket_height), (0, bracket_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(z_edges.sort_by(Axis.X)[:2], fillet_radius)
z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges.sort_by(Axis.X)[-2:], chamfer_distance)

slot_center_x = bracket_length / 2
slot_center_y = bracket_height - slot_offset_y
solid_body = solid_body - Pos(slot_center_x, slot_center_y, bracket_thickness/2) * Box(slot_length, slot_width, bracket_thickness)

hole_y1 = bracket_height / 2
hole_y2 = hole_y1 + hole_spacing
solid_body = solid_body - Pos(hole_offset_x, hole_y1, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)
solid_body = solid_body - Pos(hole_offset_x, hole_y2, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")