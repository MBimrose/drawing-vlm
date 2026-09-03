from build123d import *

rod_length = 80.0
rod_diameter = 20.0
rod_radius = rod_diameter / 2.0
wall_thickness = 4.0
inner_radius = rod_radius - wall_thickness
slot_width = 6.0
slot_length = 12.0
slot_depth = 10.0
slot_center_z = 30.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((rod_radius, 0), (rod_radius, rod_length), (inner_radius, rod_length), (inner_radius, 0), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

slot_box = Pos(0, rod_radius - slot_width / 2.0, slot_center_z) * Box(slot_length, slot_width, slot_depth)
solid_body = solid_body - slot_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_rod_with_slot"
export_step(part, "output.step")