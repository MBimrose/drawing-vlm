from build123d import *

base_width = 60.0
base_depth = 40.0
base_thickness = 8.0
boss_diameter = 12.0
boss_height = 52.0
nose_length = 20.0
hole_diameter = 6.0
hole_offset = 12.0
chamfer_size = 1.5

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_depth, base_thickness)
base = chamfer(base.edges(), chamfer_size)

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (boss_diameter/2, 0))
            l2 = Line(l1@1, (boss_diameter/2, boss_height))
            l3 = Line(l2@1, (0, boss_height + nose_length))
            l4 = Line(l3@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)
boss = Pos(0, 0, base_thickness) * p.part

result = base + boss

hole_positions = [
    (-base_width/2 + hole_offset, -base_depth/2 + hole_offset),
    ( base_width/2 - hole_offset, -base_depth/2 + hole_offset),
    (-base_width/2 + hole_offset,  base_depth/2 - hole_offset),
    ( base_width/2 - hole_offset,  base_depth/2 - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, 200)

part = result
part.name = "base_with_boss_and_holes"
export_step(part, "output.step")