from build123d import *
import math

outer_diameter = 60.0
thickness = 10.0
hub_diameter = 15.0
hub_height = 5.0
central_hole_diameter = 10.0
slot_width = 2.0
slot_depth = 4.0
slot_count = 12
chamfer_size = 0.5

base = Pos(0, 0, thickness / 2) * Cylinder(outer_diameter / 2, thickness)
hub = Pos(0, 0, thickness + hub_height / 2) * Cylinder(hub_diameter / 2, hub_height)
result = base + hub

hole = Pos(0, 0, (thickness + hub_height) / 2) * Cylinder(central_hole_diameter / 2, thickness + hub_height)
result = result - hole

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(hub_diameter / 2 - slot_depth / 2, 0, thickness + hub_height / 2) * Box(slot_width, slot_depth, hub_height)
    result = result - slot

top_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "flanged_disk_with_slots"
export_step(part, "output.step")