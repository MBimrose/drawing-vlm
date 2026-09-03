from build123d import *
import math

outer_diameter = 80.0
outer_radius = outer_diameter / 2.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_radius = boss_diameter / 2.0
boss_height = 2.0
rib_width = 3.0
rib_length = 15.0
rib_height = 1.0
rib_count = 12
pocket_diameter = 70.0
pocket_radius = pocket_diameter / 2.0
pocket_depth = 1.0
hole_diameter = 4.0
hole_radius = hole_diameter / 2.0
hole_depth = 2.0
hole_count = 12
hole_circle_radius = 30.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=plate_thickness)

solid_body = p.part
top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

solid_body = solid_body + Pos(0, 0, boss_height/2) * Cylinder(boss_radius, boss_height)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(boss_radius + rib_length/2, 0, rib_height/2) * Box(rib_width, rib_length, rib_height)
    solid_body = solid_body + rib

solid_body = solid_body - Pos(0, 0, plate_thickness - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)

for i in range(hole_count):
    angle = i * 360.0 / hole_count
    x = hole_circle_radius * math.cos(math.radians(angle))
    y = hole_circle_radius * math.sin(math.radians(angle))
    solid_body = solid_body - Pos(x, y, plate_thickness - hole_depth/2) * Cylinder(hole_radius, hole_depth)

part = solid_body
part.name = "plate_with_boss_ribs_pockets"
export_step(part, "output.step")