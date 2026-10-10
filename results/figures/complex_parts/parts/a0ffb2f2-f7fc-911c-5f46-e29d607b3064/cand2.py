from build123d import *

head_diameter = 30.0
head_thickness = 10.0
shank_diameter = 10.0
shank_length = 45.0
slot_width = 4.0
slot_depth = 2.0
slot_length = 30.0
chamfer_size = 1.0
cbore_diameter = 8.0
cbore_depth = 5.0

head_radius = head_diameter / 2.0
shank_radius = shank_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (shank_radius, 0), (shank_radius, shank_length),
                     (head_radius, shank_length), (head_radius, shank_length + head_thickness),
                     (0, shank_length + head_thickness), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

slot_box = Pos(0, 0, shank_length / 2.0) * Box(slot_width, slot_depth, slot_length)
solid_body = solid_body - slot_box

cbore_cyl = Pos(0, 0, shank_length + head_thickness - cbore_depth / 2.0) * Cylinder(cbore_diameter / 2.0, cbore_depth)
solid_body = solid_body - cbore_cyl

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "pin_with_slot_and_cbore"
export_step(part, "output.step")