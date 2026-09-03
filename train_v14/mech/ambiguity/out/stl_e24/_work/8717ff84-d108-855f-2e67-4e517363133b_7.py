from build123d import *

bracket_length = 80
bracket_width = 55
bracket_thickness = 10
gusset_height = 20
slot_length = 50
slot_width = 6
slot_offset_y = 15
hole_diameter = 6
hole_spacing = 30
hole_offset_x = -bracket_length/2 + 10
fillet_radius = 1
chamfer_distance = 1

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-bracket_length/2, -bracket_width/2),
                (bracket_length/2 - gusset_height, -bracket_width/2),
                (bracket_length/2, 0),
                (bracket_length/2 - gusset_height, bracket_width/2),
                (-bracket_length/2, bracket_width/2),
                close=True
            )
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

slot = Pos(0, slot_offset_y, bracket_thickness/2) * Box(slot_length, slot_width, bracket_thickness)
solid_body = solid_body - slot

for y in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(hole_offset_x, y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)
    solid_body = solid_body - hole

z_edges = solid_body.edges().filter_by(Axis.Z)
sorted_z = z_edges.sort_by(Axis.X)
max_x = sorted_z[-1].center().X
chamfer_edges = [e for e in sorted_z if abs(e.center().X - max_x) < 0.1]
solid_body = chamfer(chamfer_edges, chamfer_distance)

z_edges = solid_body.edges().filter_by(Axis.Z)
sorted_z = z_edges.sort_by(Axis.X)
min_x = sorted_z[0].center().X
fillet_edges = [e for e in sorted_z if abs(e.center().X - min_x) < 0.1]
solid_body = fillet(fillet_edges, fillet_radius)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")