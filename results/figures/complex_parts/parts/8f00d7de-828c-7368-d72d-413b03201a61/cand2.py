from build123d import *

base_length = 60.0
base_width = 40.0
base_thickness = 8.0
boss_diameter = 12.0
boss_height = 20.0
pin_length = 52.0
pin_base_diameter = 12.0
pin_tip_diameter = 4.0
chamfer_distance = 1.5
hole_diameter = 6.0
hole_offset = 12.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
base = chamfer(base.edges(), chamfer_distance)

boss = Pos(0, 0, base_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (pin_base_diameter/2, 0))
            l2 = Line(l1@1, (pin_base_diameter/2, pin_length - 20))
            l3 = Line(l2@1, (pin_tip_diameter/2, pin_length))
            l4 = Line(l3@1, (0, pin_length))
            l5 = Line(l4@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)
pin = Pos(0, 0, base_thickness + boss_height) * p.part

result = base + boss + pin

hole_positions = [
    (-base_length/2 + hole_offset, -base_width/2 + hole_offset),
    ( base_length/2 - hole_offset, -base_width/2 + hole_offset),
    (-base_length/2 + hole_offset,  base_width/2 - hole_offset),
    ( base_length/2 - hole_offset,  base_width/2 - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, base_thickness/2) * Cylinder(hole_diameter/2, base_thickness + 1)

part = result
part.name = "base_plate_with_boss_and_pin"
export_step(part, "output.step")