from build123d import *

horizontal_length = 80.0
vertical_height = 70.0
thickness = 8.0
depth = 12.0
fillet_radius = 4.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset_from_base = 15.0
pocket_diameter = 20.0
pocket_depth = 6.0
gusset_width = 30.0
gusset_height = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_height), (thickness, vertical_height),
                     (thickness, thickness), (horizontal_length + thickness, thickness),
                     (horizontal_length + thickness, 0), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, fillet_radius)

for i in range(3):
    y_pos = hole_offset_from_base + i * hole_spacing
    solid_body = solid_body - Pos(thickness / 2, y_pos, depth / 2) * Cylinder(hole_diameter / 2, depth)

pocket_center_x = (horizontal_length + thickness) / 2
solid_body = solid_body - Pos(pocket_center_x, thickness / 2, depth - pocket_depth / 2) * Cylinder(pocket_diameter / 2, pocket_depth)

with BuildPart() as g:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((0, 0), (gusset_width, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=depth)

gusset_body = Pos(thickness / 2, thickness / 2, 0) * g.part
solid_body = solid_body + gusset_body

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")