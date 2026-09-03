from build123d import *

base_width = 70.0
base_depth = 30.0
base_thickness = 6.0
spine_width = 60.0
spine_thickness = 4.0
spine_height = 8.0
hole_diameter = 4.0
hole_spacing = 40.0

base = Pos(0, 0, base_thickness / 2) * Box(base_width, base_depth, base_thickness)

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((-spine_width/2, 0), (spine_width/2, 0))
            l2 = Line(l1@1, (spine_width/2, spine_height - spine_thickness))
            a1 = ThreePointArc(l2@1, (0, spine_height), (-spine_width/2, spine_height - spine_thickness))
            l3 = Line(a1@1, l1@0)
        make_face()
    extrude(amount=spine_thickness)
spine = p.part

result = base + spine

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, 20)

part = result
part.name = "base_with_spine_and_holes"
export_step(part, "output.step")