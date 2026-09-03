from build123d import *

base_width = 80.0
base_height = 60.0
base_thickness = 8.0
arc_radius = 10.0
arc_spacing = 30.0
boss_diameter = 30.0
boss_height = 6.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-base_width/2, -base_height/2), (base_width/2, -base_height/2))
            l2 = Line(l1@1, (base_width/2, base_height/2 - arc_radius))
            a1 = ThreePointArc(l2@1, (base_width/2 - arc_radius, base_height/2), (base_width/2 - arc_spacing, base_height/2 - arc_radius))
            a2 = ThreePointArc(a1@1, (-(base_width/2 - arc_spacing), base_height/2), (-(base_width/2 - arc_radius), base_height/2 - arc_radius))
            l3 = Line(a2@1, (-base_width/2, -base_height/2))
        make_face()
    extrude(amount=base_thickness)

solid_body = p.part
solid_body = solid_body + Pos(0, 0, base_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

hole_points = [
    (-hole_spacing_x, -hole_spacing_y/2),
    (0, -hole_spacing_y/2),
    (hole_spacing_x, -hole_spacing_y/2),
    (-hole_spacing_x, hole_spacing_y/2),
    (0, hole_spacing_y/2),
    (hole_spacing_x, hole_spacing_y/2),
]
for x, y in hole_points:
    solid_body = solid_body - Pos(x, y, base_thickness/2) * Cylinder(hole_diameter/2, base_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "base_plate_with_boss"
export_step(part, "output.step")