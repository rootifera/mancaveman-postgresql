INSERT INTO hardware_category (name)
VALUES
       ('Tools')
ON CONFLICT
    DO NOTHING;
-- Manual Tools
INSERT INTO component_type (name, hardware_category_id)
VALUES ('Adjustable Wrench', 21),
       ('Allen Key Set', 21),
       ('Bolt Cutter', 21),
       ('C-Clamp', 21),
       ('Chisel', 21),
       ('Claw Hammer', 21),
       ('Combination Square', 21),
       ('Crowbar', 21),
       ('File Set', 21),
       ('Hacksaw', 21),
       ('Hand Drill', 21),
       ('Hex Key Set', 21),
       ('Level', 21),
       ('Mallet', 21),
       ('Measuring Tape', 21),
       ('Needle Nose Pliers', 21),
       ('Pipe Wrench', 21),
       ('Pliers', 21),
       ('Pry Bar', 21),
       ('Putty Knife', 21),
       ('Ratchet Set', 21),
       ('Saw', 21),
       ('Screwdriver Set', 21),
       ('Sledge Hammer', 21),
       ('Socket Set', 21),
       ('Spanner Set', 21),
       ('Spirit Level', 21),
       ('Staple Gun', 21),
       ('Tape Measure', 21),
       ('Tin Snips', 21),
       ('Torque Wrench', 21),
       ('Utility Knife', 21),
       ('Vice Grips', 21),
       ('Wire Cutters', 21),
       ('Wire Strippers', 21),
       ('Wood Plane', 21),
       ('Wooden Mallet', 21),
       ('Wrench Set', 21)
ON CONFLICT
    DO NOTHING;
