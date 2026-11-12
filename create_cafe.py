
from pathlib import Path

parts = []

def model(name, x, y, links, yaw=0):
    parts.append(
        f'<model name="{name}"><static>true</static>'
        f'<pose>{x} {y} 0 0 0 {yaw}</pose>{links}</model>'
    )

def shape(name, pose, size, color, collision=True):
    visual = f"""
    <visual name="{name}_visual">
      <pose>{pose}</pose>
      <geometry><box><size>{size}</size></box></geometry>
      <material><ambient>{color}</ambient><diffuse>{color}</diffuse></material>
    </visual>"""
    coll = f"""
    <collision name="{name}_collision">
      <pose>{pose}</pose>
      <geometry><box><size>{size}</size></box></geometry>
    </collision>""" if collision else ""
    return visual + coll

def cylinder(name, pose, radius, length, color):
    return f"""
    <visual name="{name}_visual">
      <pose>{pose}</pose>
      <geometry><cylinder><radius>{radius}</radius><length>{length}</length></cylinder></geometry>
      <material><ambient>{color}</ambient><diffuse>{color}</diffuse></material>
    </visual>
    <collision name="{name}_collision">
      <pose>{pose}</pose>
      <geometry><cylinder><radius>{radius}</radius><length>{length}</length></cylinder></geometry>
    </collision>"""

# Floor
model("cafe_floor", 0, 0, f"""
<link name="floor">
  {shape("floor", "0 0 -0.1 0 0 0", "10 8 0.2", "0.75 0.72 0.65 1")}
</link>""")

# Four surrounding walls, leaving a 1.2 m entrance in the south wall
walls = [
    ("north_wall", 0, 4.1, "10.4 0.2 2.5"),
    ("west_wall", -5.1, 0, "0.2 8.4 2.5"),
    ("east_wall", 5.1, 0, "0.2 8.4 2.5"),
    ("south_left", -2.8, -4.1, "4.4 0.2 2.5"),
    ("south_right", 2.8, -4.1, "4.4 0.2 2.5")
]
for name, x, y, size in walls:
    model(name, x, y, f"""
    <link name="wall">
      {shape("wall", "0 0 1.25 0 0 0", size, "0.85 0.82 0.75 1")}
    </link>""")

# Café counter at the back
model("service_counter", 0, 3.15, f"""
<link name="counter">
  {shape("counter_body", "0 0 0.55 0 0 0", "3.5 0.7 1.1", "0.35 0.18 0.08 1")}
  {shape("counter_top", "0 0 1.13 0 0 0", "3.7 0.8 0.08", "0.2 0.2 0.2 1")}
</link>""")

# Four dining tables
table_positions = [(-2.2, 1.25), (2.2, 1.25), (-2.2, -1.65), (2.2, -1.65)]

for i, (x, y) in enumerate(table_positions, 1):
    links = shape("table_top", "0 0 0.75 0 0 0", "1.2 0.8 0.12", "0.45 0.24 0.10 1")
    for j, (lx, ly) in enumerate([(-0.5,-0.3),(0.5,-0.3),(-0.5,0.3),(0.5,0.3)]):
        links += shape(f"leg{j}", f"{lx} {ly} 0.36 0 0 0", "0.08 0.08 0.72", "0.25 0.15 0.08 1")
    model(f"table_{i}", x, y, f'<link name="table">{links}</link>')

# Chairs: two on opposite sides of each table
# Chairs face towards their respective tables
chair_positions = []

for x, y in table_positions:
    chair_positions.extend([
        (x - 0.9, y, 1.5708),   # Left chair faces right
        (x + 0.9, y, -1.5708)   # Right chair faces left
    ])

for i, (x, y, yaw) in enumerate(chair_positions, 1):
    links = shape(
        "seat", "0 0 0.43 0 0 0",
        "0.48 0.48 0.10", "0.12 0.28 0.55 1"
    )

    links += shape(
        "back", "0 0.23 0.78 0 0 0",
        "0.48 0.08 0.65", "0.12 0.28 0.55 1"
    )

    for j, (lx, ly) in enumerate([
        (-0.18,-0.18), (0.18,-0.18),
        (-0.18,0.18), (0.18,0.18)
    ]):
        links += shape(
            f"leg{j}", f"{lx} {ly} 0.21 0 0 0",
            "0.06 0.06 0.42", "0.12 0.12 0.18 1"
        )

    model(f"chair_{i}", x, y, f'<link name="chair">{links}</link>', yaw)

def customer(name, x, y, color):
    links = cylinder("body", "0 0 0.95 0 0 0", 0.20, 0.65, color)
    links += f"""
    <visual name="head">
      <pose>0 0 1.42 0 0 0</pose>
      <geometry><sphere><radius>0.16</radius></sphere></geometry>
      <material><ambient>0.75 0.52 0.35 1</ambient><diffuse>0.75 0.52 0.35 1</diffuse></material>
    </visual>"""
    model(name, x, y, f'<link name="person">{links}</link>')

customer("customer_1", -3.1, 1.25, "0.1 0.45 0.75 1")
customer("customer_2", 3.1, -1.65, "0.75 0.25 0.2 1")

# Dynamic differential-drive delivery robot
parts.append("""
<model name="cafe_delivery_robot">
  <static>false</static>
  <pose>-3.7 -3.1 0 0 0 0</pose>

  <!-- Main robot chassis -->
  <link name="base_link">

  <inertial>
    <pose>0 0 0.40 0 0 0</pose>
    <mass>6.0</mass>
    <inertia>
      <ixx>0.12</ixx><iyy>0.15</iyy><izz>0.18</izz>
      <ixy>0</ixy><ixz>0</ixz><iyz>0</iyz>
    </inertia>
  </inertial>

  <!-- Lower chassis -->
  <collision name="chassis_collision">
    <pose>0 0 0.18 0 0 0</pose>
    <geometry>
      <box><size>0.45 0.34 0.12</size></box>
    </geometry>
  </collision>

  <visual name="chassis_visual">
    <pose>0 0 0.18 0 0 0</pose>
    <geometry>
      <box><size>0.45 0.34 0.12</size></box>
    </geometry>
    <material>
      <ambient>0.08 0.15 0.35 1</ambient>
      <diffuse>0.08 0.15 0.35 1</diffuse>
    </material>
  </visual>

  <!-- Enclosed food delivery compartment -->
  <collision name="delivery_box_collision">
    <pose>0 0 0.47 0 0 0</pose>
    <geometry>
      <box><size>0.36 0.30 0.46</size></box>
    </geometry>
  </collision>

  <visual name="delivery_box_visual">
    <pose>0 0 0.47 0 0 0</pose>
    <geometry>
      <box><size>0.36 0.30 0.46</size></box>
    </geometry>
    <material>
      <ambient>0.85 0.88 0.92 1</ambient>
      <diffuse>0.85 0.88 0.92 1</diffuse>
    </material>
  </visual>

  <!-- Front delivery compartment door -->
  <visual name="front_door">
    <pose>0.183 0 0.47 0 0 0</pose>
    <geometry>
      <box><size>0.008 0.22 0.34</size></box>
    </geometry>
    <material>
      <ambient>0.1 0.3 0.65 1</ambient>
      <diffuse>0.1 0.3 0.65 1</diffuse>
    </material>
  </visual>

  <!-- Front indicator light -->
  <visual name="indicator_light">
    <pose>0.19 0 0.67 0 0 0</pose>
    <geometry>
      <sphere><radius>0.025</radius></sphere>
    </geometry>
    <material>
      <ambient>0.1 0.9 0.2 1</ambient>
      <diffuse>0.1 0.9 0.2 1</diffuse>
    </material>
  </visual>

  <!-- Rear support ball -->
  <collision name="caster_collision">
    <pose>-0.15 0 0.06 0 0 0</pose>
    <geometry>
      <sphere><radius>0.06</radius></sphere>
    </geometry>
  </collision>

  <visual name="caster_visual">
    <pose>-0.15 0 0.06 0 0 0</pose>
    <geometry>
      <sphere><radius>0.06</radius></sphere>
    </geometry>
    <material>
      <ambient>0.15 0.15 0.15 1</ambient>
      <diffuse>0.15 0.15 0.15 1</diffuse>
    </material>
  </visual>

</link>

  <!-- Left wheel -->
  <link name="left_wheel">
    <pose>0 0.205 0.10 0 0 0</pose>
    <inertial>
      <mass>0.5</mass>
      <inertia>
        <ixx>0.002</ixx><iyy>0.0025</iyy><izz>0.002</izz>
        <ixy>0</ixy><ixz>0</ixz><iyz>0</iyz>
      </inertia>
    </inertial>
    <collision name="left_wheel_collision">
      <geometry><cylinder><radius>0.10</radius><length>0.05</length></cylinder></geometry>
      <pose>0 0 0 1.5708 0 0</pose>
    </collision>
    <visual name="left_wheel_visual">
      <geometry><cylinder><radius>0.10</radius><length>0.05</length></cylinder></geometry>
      <pose>0 0 0 1.5708 0 0</pose>
      <material><ambient>0.1 0.1 0.1 1</ambient></material>
    </visual>
  </link>

  <!-- Right wheel -->
  <link name="right_wheel">
    <pose>0 -0.205 0.10 0 0 0</pose>
    <inertial>
      <mass>0.5</mass>
      <inertia>
        <ixx>0.002</ixx><iyy>0.0025</iyy><izz>0.002</izz>
        <ixy>0</ixy><ixz>0</ixz><iyz>0</iyz>
      </inertia>
    </inertial>
    <collision name="right_wheel_collision">
      <geometry><cylinder><radius>0.10</radius><length>0.05</length></cylinder></geometry>
      <pose>0 0 0 1.5708 0 0</pose>
    </collision>
    <visual name="right_wheel_visual">
      <geometry><cylinder><radius>0.10</radius><length>0.05</length></cylinder></geometry>
      <pose>0 0 0 1.5708 0 0</pose>
      <material><ambient>0.1 0.1 0.1 1</ambient></material>
    </visual>
  </link>

  <!-- Wheel joints -->
  <joint name="left_wheel_joint" type="revolute">
    <parent>base_link</parent>
    <child>left_wheel</child>
    <axis>
      <xyz>0 1 0</xyz>
      <limit><effort>10</effort><velocity>20</velocity></limit>
    </axis>
  </joint>

  <joint name="right_wheel_joint" type="revolute">
    <parent>base_link</parent>
    <child>right_wheel</child>
    <axis>
      <xyz>0 1 0</xyz>
      <limit><effort>10</effort><velocity>20</velocity></limit>
    </axis>
  </joint>

  <!-- Differential-drive controller -->
  <plugin filename="libignition-gazebo-diff-drive-system.so"
          name="ignition::gazebo::systems::DiffDrive">
    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint</right_joint>
    <wheel_separation>0.40</wheel_separation>
    <wheel_radius>0.10</wheel_radius>
    <topic>/model/cafe_delivery_robot/cmd_vel</topic>
  </plugin>
</model>
""")

# Wi-Fi beacon marker near counter
model("wifi_beacon_marker", 3.7, 3.0, f"""
<link name="beacon">
  <visual name="beacon_visual">
    <pose>0 0 1.2 0 0 0</pose>
    <geometry><sphere><radius>0.18</radius></sphere></geometry>
    <material><ambient>0.9 0.1 0.1 1</ambient><diffuse>0.9 0.1 0.1 1</diffuse></material>
  </visual>
</link>""")

sdf = """<?xml version="1.0"?>
<sdf version="1.7">
  <world name="indoor_cafe_world">
    <gravity>0 0 -9.8</gravity>
    <plugin filename="libignition-gazebo-physics-system.so"
            name="ignition::gazebo::systems::Physics"/>

    <plugin filename="libignition-gazebo-user-commands-system.so"
            name="ignition::gazebo::systems::UserCommands"/>

    <plugin filename="libignition-gazebo-scene-broadcaster-system.so"
            name="ignition::gazebo::systems::SceneBroadcaster"/>
    <scene>
      <ambient>0.7 0.7 0.7 1</ambient>
      <background>0.6 0.7 0.8 1</background>
    </scene>
    <light name="sun" type="directional">
      <pose>0 0 10 0 0 0</pose>
      <direction>-0.5 0.2 -1</direction>
      <diffuse>0.9 0.9 0.9 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
    </light>
""" + "\n".join(parts) + """
  </world>
</sdf>
"""


actor = """
<actor name="walking_waiter">
  <pose>0 2.2 0 0 0 -1.5708</pose>

  <skin>
    <filename>https://fuel.gazebosim.org/1.0/Mingfei/models/actor/tip/files/meshes/walk.dae</filename>
    <scale>1.0</scale>
  </skin>

  <animation name="walk">
    <filename>https://fuel.gazebosim.org/1.0/Mingfei/models/actor/tip/files/meshes/walk.dae</filename>
  </animation>

  <script>
    <loop>true</loop>
    <auto_start>true</auto_start>

    <trajectory id="0" type="walk">

  <!-- Start near the counter -->
  <waypoint>
    <time>0</time>
    <pose>0 2.2 1 0 0 -1.5708</pose>
  </waypoint>

  <!-- Approach first table -->
  <waypoint>
    <time>4</time>
    <pose>-0.75 1.25 1 0 0 0</pose>
  </waypoint>

  <!-- Cross to second table -->
  <waypoint>
    <time>8</time>
    <pose>0.75 1.25 1 0 0 0</pose>
  </waypoint>

  <!-- Move down the café -->
  <waypoint>
    <time>12</time>
    <pose>0.75 -1.65 1 0 0 0</pose>
  </waypoint>

  <!-- Approach third table -->
  <waypoint>
    <time>16</time>
    <pose>-0.75 -1.65 1 0 0 0</pose>
  </waypoint>

  <!-- Return towards centre aisle -->
  <waypoint>
    <time>20</time>
    <pose>0 -2.5 1 0 0 0</pose>
  </waypoint>

  <!-- Return to counter -->
  <waypoint>
    <time>26</time>
    <pose>0 2.2 1 0 0 0</pose>
  </waypoint>

</trajectory>

  </script>
</actor>
"""

sdf = sdf.replace("  </world>", actor + "\n  </world>")

output = Path.home() / "rssi_project/worlds/indoor_cafe_world.sdf"
output.write_text(sdf)
print(f"Café world created: {output}")
print(f"Models added: {len(parts)}")


