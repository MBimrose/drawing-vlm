from build123d import *

outer_diameter = 80.0
inner_diameter = 40.0
height = 20.0
wall_thickness = 5.0
rib_width = 10.0
rib_height = 8.0
rib_thickness = 4.0
hole_diameter = 8.5
cbore_diameter = 13.0
cbore_depth = 4.0
hole_spacing = 30.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=height)

solid_body = p.part

rib = Pos(outer_diameter / 2 - rib_thickness / 2, 0, height / 2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

for x in [-hole_spacing / 2, hole_spacing / 2]:
    solid_body = solid_body - Pos(x, 0, height) * CounterBoreHole(hole_diameter / 2, cbore_diameter / 2, cbore_depth, depth=height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "flanged_ring_with_rib"
export_step(part, "output.step")