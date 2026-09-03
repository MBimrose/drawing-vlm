from build123d import *

arm_length = 80.0
start_width = 30.0
start_thickness = 10.0
end_width = 50.0
end_thickness = 20.0
hole_diameter = 8.0
chamfer_size = 1.0
rib_width = 5.0
rib_height = 5.0
pocket_width = 10.0
pocket_depth = 5.0
pocket_offset = 25.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Rectangle(start_width, start_thickness)
    with BuildSketch(Plane.XY.offset(arm_length)) as s2:
        Rectangle(end_width, end_thickness)
    loft()

solid_body = p.part
solid_body = solid_body - Pos(0, 0, arm_length / 2) * Cylinder(hole_diameter / 2, arm_length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

rib = Pos(0, 0, arm_length / 2) * Box(rib_width, rib_height, arm_length)
solid_body = solid_body + rib

pocket = Pos(0, 0, arm_length - pocket_depth / 2) * Box(pocket_width, pocket_depth, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "tapered_arm_with_rib"
export_step(part, "output.step")