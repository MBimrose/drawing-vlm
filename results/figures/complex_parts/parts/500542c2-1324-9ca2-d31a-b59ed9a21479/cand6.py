from build123d import *
import math

gear_outer_radius = 40.0
gear_inner_radius = 30.0
gear_thickness = 10.0
hub_radius = 10.0
hub_height = 5.0
tooth_width = 8.0
tooth_height = 6.0
num_teeth = 20
central_bore_diameter = 6.0
chamfer_size = 0.5

base = Cylinder(gear_inner_radius, gear_thickness)
hub = Pos(0, 0, gear_thickness/2 + hub_height/2) * Cylinder(hub_radius, hub_height)
result = base + hub

tooth_radius = gear_inner_radius + tooth_height/2
for i in range(num_teeth):
    angle_deg = i * 360.0 / num_teeth
    angle_rad = math.radians(angle_deg)
    px = tooth_radius * math.cos(angle_rad)
    py = tooth_radius * math.sin(angle_rad)
    tooth = Pos(px, py, gear_thickness/2) * Rot(0, 0, angle_deg) * Box(tooth_width, tooth_height, gear_thickness)
    result = result + tooth

result = result - Cylinder(central_bore_diameter/2, 100)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "gear_with_hub_and_teeth"
export_step(part, "output.step")