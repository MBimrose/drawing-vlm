from build123d import *
import math

tri_side = 60.0
plate_thickness = 10.0
lip_height = 3.0
lip_extension = 5.0
central_hole_dia = 12.0
chamfer_dist = 1.0
tri_height = math.sqrt(3) / 2 * tri_side
lip_tri_side = tri_side + 2 * lip_extension

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(tri_side, 3)
    extrude(amount=plate_thickness)
base = p.part

with BuildPart() as p2:
    with BuildSketch() as s2:
        RegularPolygon(lip_tri_side, 3)
    extrude(amount=lip_height)
lip = Pos(0, 0, plate_thickness) * p2.part

combined = base + lip
combined = combined - Cylinder(central_hole_dia / 2, plate_thickness + lip_height + 10)
vertical_edges = combined.edges().filter_by(Axis.Z)
combined = chamfer(vertical_edges, chamfer_dist)

part = combined
part.name = "triangular_plate_with_lip"
export_step(part, "output.step")