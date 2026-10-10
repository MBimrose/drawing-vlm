from build123d import *
import math

blade_length = 70.0
root_width = 30.0
tip_width = 10.0
root_thickness = 6.0
tip_thickness = 2.0
loft_steps = 10
step_height = blade_length / loft_steps
twist_per_step = 15.0
hub_diameter = 20.0
hub_height = 10.0
central_hole_diameter = 4.0
mount_hole_diameter = 6.0
mount_hole_radius = 30.0
edge_chamfer = 1.0
slot_width = 4.0
slot_length = blade_length * 0.6
slot_center = blade_length * 0.5

with BuildPart() as p:
    for i in range(loft_steps + 1):
        t = i / loft_steps
        w = root_width + (tip_width - root_width) * t
        th = root_thickness + (tip_thickness - root_thickness) * t
        z = i * step_height
        rot = i * twist_per_step
        with BuildSketch(Plane.XY.offset(z).rotated((0, 0, rot))) as sk:
            Rectangle(w, th)
    loft()
blade = p.part

blade = blade - Pos(0, 0, slot_center) * Box(slot_width, slot_length, 200)

hub = Pos(0, 0, hub_height/2) * Cylinder(hub_diameter/2, hub_height)
hub = hub - Pos(0, 0, hub_height) * Cylinder(central_hole_diameter/2, 20)
for angle in range(0, 360, 30):
    px = mount_hole_radius * math.cos(math.radians(angle))
    py = mount_hole_radius * math.sin(math.radians(angle))
    hub = hub - Pos(px, py, hub_height) * Cylinder(mount_hole_diameter/2, 20)

top_edges = hub.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
hub = chamfer(top_edges, edge_chamfer)

part = blade + hub
part.name = "propeller_blade_with_hub"
export_step(part, OUTPUT_PATH)