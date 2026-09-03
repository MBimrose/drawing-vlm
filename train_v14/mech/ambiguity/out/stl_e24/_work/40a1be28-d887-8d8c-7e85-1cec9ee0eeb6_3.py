from build123d import *

base_radius = 20.0
mid_radius = 12.0
top_radius = 18.0
height = 40.0
mid_height = height * 0.5
top_height = height * 0.8
flange_width = 60.0
flange_depth = 40.0
flange_thickness = 8.0
bolt_hole_diameter = 5.0
bolt_hole_offset = 10.0
central_hole_diameter = 8.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(mid_height)) as s2:
        Circle(mid_radius)
    with BuildSketch(Plane.XY.offset(top_height)) as s3:
        Circle(top_radius)
    loft()

solid_body = p.part
flange = Pos(0, 0, top_height + flange_thickness / 2) * Box(flange_width, flange_depth, flange_thickness)
solid_body = solid_body + flange

hole_height = height + flange_thickness + 10
solid_body = solid_body - Cylinder(central_hole_diameter / 2, hole_height)

bolt_positions = [
    (-flange_width / 2 + bolt_hole_offset, -flange_depth / 2 + bolt_hole_offset),
    (flange_width / 2 - bolt_hole_offset, -flange_depth / 2 + bolt_hole_offset),
    (-flange_width / 2 + bolt_hole_offset, flange_depth / 2 - bolt_hole_offset),
    (flange_width / 2 - bolt_hole_offset, flange_depth / 2 - bolt_hole_offset),
]
for x, y in bolt_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(bolt_hole_diameter / 2, hole_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "lofted_flange_with_holes"
export_step(part, "output.step")