from build123d import *
import math

pin_total_length = 80.0
pin_shank_diameter = 12.0
pin_tip_length = 20.0
base_thickness = 8.0
base_width = 40.0
base_length = 60.0
mount_hole_diameter = 6.0
mount_hole_offset = 12.0
chamfer_distance = 1.5
embed_depth = 2.0

shank_radius = pin_shank_diameter / 2.0
shank_length = pin_total_length - pin_tip_length - base_thickness

with BuildPart() as pin:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Line((0, base_thickness - embed_depth), (shank_radius, base_thickness - embed_depth))
            Line((shank_radius, base_thickness - embed_depth), (shank_radius, base_thickness + shank_length))
            Line((shank_radius, base_thickness + shank_length), (0, pin_total_length))
            Line((0, pin_total_length), (0, base_thickness - embed_depth))
        make_face()
    revolve(axis=Axis.Z)

pin_body = pin.part

base_plate = Pos(0, 0, base_thickness / 2) * Box(base_length, base_width, base_thickness)
base_plate = chamfer(base_plate.edges(), chamfer_distance)

hole_x = base_length / 2 - mount_hole_offset
hole_y = base_width / 2 - mount_hole_offset
for hx, hy in [(hole_x, hole_y), (-hole_x, hole_y), (-hole_x, -hole_y), (hole_x, -hole_y)]:
    base_plate = base_plate - Pos(hx, hy, base_thickness / 2) * Cylinder(mount_hole_diameter / 2, base_thickness)

result = base_plate + pin_body

part = result
part.name = "pin_with_base_plate"
export_step(part, OUTPUT_PATH)