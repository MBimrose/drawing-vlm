from build123d import *

arm_length = 70.0
base_radius = 15.0
mid_radius = 10.0
tip_radius = 5.0
mid_section_z = arm_length * 0.5
tip_section_z = arm_length
boss_diameter = 20.0
boss_height = 10.0
split_gap = 2.0
chamfer_distance = 1.0
hole_diameter = 4.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(mid_section_z)) as s2:
        Ellipse(mid_radius, mid_radius * 0.8)
    with BuildSketch(Plane.XY.offset(tip_section_z)) as s3:
        Circle(tip_radius)
    loft()

arm = p.part
boss = Pos(0, 0, boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
combined = arm + boss

cut_box = Pos(0, -500, arm_length / 2) * Box(split_gap, 1000, arm_length)
split_arm = combined - cut_box

y_faces = split_arm.faces().filter_by(Axis.Y).sort_by(Axis.Y)
min_y_face = y_faces[0]
chamfer_edges = min_y_face.edges()
chamfered = chamfer(chamfer_edges, chamfer_distance)

hole = Pos(0, 0, (boss_height + 2) / 2) * Cylinder(hole_diameter / 2, boss_height + 2)
result = chamfered - hole

part = result
part.name = "split_arm_with_boss"
export_step(part, "output.step")