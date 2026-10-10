from build123d import *
import math

channel_length = 80.0
outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
half_len = channel_length / 2.0
edge_chamfer = 0.6
rib_length = 20.0
rib_thickness = wall_thickness / 2.0
boss_diameter = 12.0
boss_height = 6.0
boss_offset_from_bottom = 15.0
sensor_hole_diameter = 6.0
sensor_chamfer = 0.4

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((outer_radius, -half_len), (outer_radius, half_len),
                      (inner_radius, half_len), (inner_radius, -half_len), close=True)
        make_face()
    revolve(axis=Axis.Z)

channel = p.part

rib_body = Pos(inner_radius - rib_thickness, 0, 0) * Box(rib_thickness, rib_length, rib_thickness)
rib_body = chamfer(rib_body.edges().filter_by(Axis.X), edge_chamfer)
channel = channel + rib_body

boss_center_y = -half_len + boss_offset_from_bottom + boss_height / 2.0
boss_radius = boss_diameter / 2.0
boss_body = Pos(inner_radius - boss_radius, boss_center_y, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
channel = channel + boss_body

hole_body = Pos(inner_radius - boss_radius, boss_center_y, 0) * Rot(0, 90, 0) * Cylinder(sensor_hole_diameter / 2.0, boss_height + 2.0)
channel = channel - hole_body

part = channel
part.name = "sensor_channel"
export_step(part, OUTPUT_PATH)