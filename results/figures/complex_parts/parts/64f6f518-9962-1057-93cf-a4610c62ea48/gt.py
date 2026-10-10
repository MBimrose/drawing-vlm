from build123d import *

spine_height = 45.0
spine_bottom_radius = 5.0
spine_top_radius = 2.5
leaf_extension = 30.0
leaf_thickness = 6.0
pin_pocket_diameter = 4.0
pin_pocket_radius = pin_pocket_diameter / 2.0
pin_offset_x = spine_top_radius + leaf_extension / 2.0
pin_offset_z = spine_height / 2.0
hole_diameter = 5.0
hole_radius = hole_diameter / 2.0
hole_spacing = 15.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (spine_bottom_radius, 0))
            l2 = Line(l1 @ 1, (spine_top_radius, spine_height))
            l3 = Line(l2 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

spine_solid = p.part

leaf = Pos(spine_top_radius + leaf_extension / 2.0, 0, spine_height / 2.0) * Box(leaf_extension, leaf_thickness, spine_height)

result = spine_solid + leaf

pocket = Pos(pin_offset_x, 0, pin_offset_z) * Rot(90, 0, 0) * Cylinder(pin_pocket_radius, leaf_thickness)
result = result - pocket

for x_offset in (-hole_spacing, 0, hole_spacing):
    hole = Pos(spine_top_radius + leaf_extension / 2.0 + x_offset, 0, pin_offset_z) * Rot(90, 0, 0) * Cylinder(hole_radius, leaf_thickness)
    result = result - hole

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "spine_leaf_assembly"
export_step(part, OUTPUT_PATH)