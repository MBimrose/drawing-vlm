from build123d import *
import math

outer_diameter = 80.0
width = 20.0
bore_diameter = 20.0
groove_angle = 40.0
groove_depth = 5.0
groove_width = 2 * groove_depth * math.tan(math.radians(groove_angle / 2))
mount_hole_diameter = 8.5
mount_hole_spacing = 30.0
chamfer_size = 0.8
rib_thickness = 4.0
rib_width = 10.0
rib_length = 30.0
pocket_diameter = 12.0
pocket_depth = 4.0

result = Cylinder(outer_diameter / 2, width)
result = result - Cylinder(bore_diameter / 2, width)

with BuildPart() as gp:
    with BuildSketch(Plane.XZ) as gs:
        with BuildLine() as gl:
            l1 = Line((outer_diameter / 2, -groove_width / 2), (outer_diameter / 2 - groove_depth, 0))
            l2 = Line(l1 @ 1, (outer_diameter / 2, groove_width / 2))
            l3 = Line(l2 @ 1, (outer_diameter / 2, -groove_width / 2))
        make_face()
    extrude(amount=width)
groove = gp.part
result = result - groove
result = result - Rot(0, 0, 180) * groove

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter / 2, width)

rib = Pos(0, 0, -width / 2 + rib_thickness / 2) * Box(rib_length, rib_width, rib_thickness)
result = result + rib

pocket = Pos(0, 0, width / 2 - pocket_depth / 2) * Cylinder(pocket_diameter / 2, pocket_depth)
result = result - pocket

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "v_groove_pulley"
export_step(part, "output.step")