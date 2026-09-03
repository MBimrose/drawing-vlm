from build123d import *
import math

outer_radius = 45.0
plate_thickness = 3.0
rim_width = 5.0
rim_height = 1.5
boss_radius = 10.0
boss_height = 2.0
recess_radius = 12.0
recess_depth = 1.0
chamfer_distance = 0.5
hole_diameter = 4.0
hole_count = 12
hole_radius = outer_radius - rim_width/2
mount_hole_diameter = 6.0
mount_hole_count = 4
mount_hole_radius = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=plate_thickness)

solid_body = p.part

rim = Pos(0, 0, plate_thickness - rim_height/2) * (Cylinder(outer_radius, rim_height) - Cylinder(outer_radius - rim_width, rim_height))
solid_body = solid_body + rim

boss = Pos(0, 0, plate_thickness - boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

recess = Pos(0, 0, plate_thickness - recess_depth/2) * Cylinder(recess_radius, recess_depth)
solid_body = solid_body - recess

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

for i in range(hole_count):
    a = math.radians(i * 360.0 / hole_count)
    solid_body = solid_body - Pos(hole_radius * math.cos(a), hole_radius * math.sin(a), plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)

for i in range(mount_hole_count):
    a = math.radians(i * 360.0 / mount_hole_count)
    solid_body = solid_body - Pos(mount_hole_radius * math.cos(a), mount_hole_radius * math.sin(a), plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

part = solid_body
part.name = "plate_with_rim_boss_and_holes"
export_step(part, "output.step")