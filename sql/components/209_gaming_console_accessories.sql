INSERT INTO hardware_category (name)
VALUES ('Gaming Console Accessories')

ON CONFLICT
    DO NOTHING;

-- Gaming Console Accessories
INSERT INTO component_type (name, hardware_category_id)
VALUES ('Arcade Stick', 9),
       ('AV Cable', 9),
       ('Battery Pack', 9),
       ('Cartridge Cleaning Kit', 9),
       ('Console Skin', 9),
       ('Console Stand', 9),
       ('Controller Charging Station', 9),
       ('Cooling Fan', 9),
       ('Dance Pad', 9),
       ('Drum Controller', 9),
       ('Expansion Pak', 9),
       ('External Hard Drive', 9),
       ('Game Capture Card', 9),
       ('Game Genie (Cheat Device)', 9),
       ('Gaming Headset', 9),
       ('Guitar Controller', 9),
       ('HDMI Cable', 9),
       ('Joystick', 9),
       ('Keyboard and Mouse Adapter', 9),
       ('Light Gun', 9),
       ('Link Cable', 9),
       ('Memory Card', 9),
       ('Microphone', 9),
       ('Motion Sensor Bar', 9),
       ('Network Adapter', 9),
       ('Paddle Controller', 9),
       ('Power Glove', 9),
       ('R.O.B. (Robotic Operating Buddy)', 9),
       ('Racing Wheel', 9),
       ('RF Switch/Modulator', 9),
       ('Thumb Grips', 9),
       ('Trackball Controller', 9),
       ('Travel Case', 9),
       ('Turbo Button Controller', 9),
       ('Virtual Reality Headset', 9),
       ('VMU (Visual Memory Unit)', 9),
       ('Wired Controller', 9),
       ('Wireless Controller', 9),
       ('Zapper Gun', 9)
ON CONFLICT
    DO NOTHING;
