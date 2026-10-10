from build123d import *
import math

# parameters
od = 60.0
length = 80.0
wall_thickness = 5.0
inlet_radius = 8.0
inlet_offset = 15.0
channel_radius = 5.0
boss_radius = 10.0
boss_height = 6.0
spring_hole_radius = 5.0
spring_hole_depth = 15.0
mount_hole_radius = 3.0
mount_hole_spacing_angle = 90.0
chamfer_distance = 2.0

# derived values
inner_radius = od/2 - wall_thickness
x_side_center = od/2 - wall_thickness/2
mount_radius = od/2 - wall_thickness - mount_hole_radius - 1.0
boss_translate_x = od/2 - boss_height/2

# outer cylinder
result = Cylinder(od/2, length)

# shell (open both ends)
z_faces = result.faces().sort_by(Axis.Z)
result = offset(result, amount=-wall_thickness, openings=[z_faces[0], z_faces[-1]])

# central bore
result = result - Cylinder(channel_radius, length)

# side port (along X-axis, cutting through wall)
side_port = Rot(0, 90, 0) * Pos(x_side_center - (wall_thickness + 1.0)/2, 0, inlet_offset) * Cylinder(inlet_radius, wall_thickness + 1.0)
result = result - side_port

# raised boss on outer surface
boss = Rot(0, 90, 0) * Pos(od/2, 0, length/2) * Cylinder(boss_radius, boss_height)
result = result + boss

# spring hole (blind from top)
result = result - Pos(0, 0, length - spring_hole_depth/2) * Cylinder(spring_hole_radius, spring_hole_depth)

# mount holes
for i in range(4):
    angle = math.radians(i * mount_hole_spacing_angle)
    x = mount_radius * math.cos(angle)
    y = mount_radius * math.sin(angle)
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_radius, length + 2)

# chamfer top edges
top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "hollow_cylinder_with_ports"
export_step(part, OUTPUT_PATH)