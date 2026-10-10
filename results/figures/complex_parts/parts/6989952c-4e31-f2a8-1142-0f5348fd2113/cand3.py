from build123d import *
import math

outer_radius = 30.0
inner_radius = 10.0
total_height = 60.0
waist_height = 30.0
flange_thickness = 15.0
fillet_radius = 2.0
hole_diameter = 6.0
hole_count = 6
hole_offset = 8.0
pocket_width = 12.0
pocket_depth = 8.0
pocket_height = 5.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, flange_thickness))
            l3 = Line(l2@1, (inner_radius, flange_thickness))
            l4 = Line(l3@1, (inner_radius, flange_thickness + waist_height))
            l5 = Line(l4@1, (outer_radius, flange_thickness + waist_height))
            l6 = Line(l5@1, (outer_radius, total_height))
            l7 = Line(l6@1, (0, total_height))
            l8 = Line(l7@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

pocket = Pos(0, 0, total_height - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

hole_r = hole_diameter / 2
hole_pos_r = outer_radius - hole_offset
for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pos_r * math.cos(angle)
    py = hole_pos_r * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height/2) * Cylinder(hole_r, total_height + 10)

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "revolved_flanged_shaft"
export_step(part, "output.step")