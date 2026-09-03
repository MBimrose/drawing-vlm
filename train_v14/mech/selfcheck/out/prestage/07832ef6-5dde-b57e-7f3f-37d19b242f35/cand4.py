from build123d import *
import math

shank_radius = 8.0
shank_length = 60.0
flange_radius = 38.0
flange_thickness = 20.0
rib_width = 6.0
rib_height = 12.0
rib_thickness = 4.0
hole_diameter = 5.0
hole_depth = 10.0
hole_pattern_radius = 20.0
pocket_radius = 15.0
pocket_depth = 5.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (shank_radius, 0))
            l2 = Line(l1@1, (shank_radius, shank_length))
            l3 = Line(l2@1, (flange_radius, shank_length))
            l4 = Line(l3@1, (flange_radius, shank_length + flange_thickness))
            l5 = Line(l4@1, (0, shank_length + flange_thickness))
            l6 = Line(l5@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

rib = Pos(shank_radius + rib_thickness/2, 0, shank_length + flange_thickness/2) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + rib

for i in range(4):
    angle = math.radians(i * 360.0 / 4)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    hole = Pos(px, py, shank_length + flange_thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

pocket = Pos(0, 0, shank_length + flange_thickness - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "revolved_flange_with_rib"
export_step(part, "output.step")