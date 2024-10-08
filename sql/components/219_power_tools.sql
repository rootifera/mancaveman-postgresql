INSERT INTO hardware_category (name)
VALUES ('Power Tools')
ON CONFLICT
    DO NOTHING;
-- Power Tools
INSERT INTO component_type (name, hardware_category_id)
VALUES ('Air Compressor', 19),
       ('Angle Grinder', 19),
       ('Band Saw', 19),
       ('Belt Sander', 19),
       ('Bench Grinder', 19),
       ('Biscuit Joiner', 19),
       ('Chainsaw', 19),
       ('Circular Saw', 19),
       ('Compound Miter Saw', 19),
       ('Cordless Drill', 19),
       ('Demolition Hammer', 19),
       ('Drill Press', 19),
       ('Drywall Screw Gun', 19),
       ('Dust Collector', 19),
       ('Electric Planer', 19),
       ('Heat Gun', 19),
       ('Impact Driver', 19),
       ('Impact Wrench', 19),
       ('Jigsaw', 19),
       ('Magnetic Drill Press', 19),
       ('Miter Saw', 19),
       ('Nail Gun', 19),
       ('Orbital Sander', 19),
       ('Oscillating Multi-Tool', 19),
       ('Palm Sander', 19),
       ('Plunge Router', 19),
       ('Polisher', 19),
       ('Reciprocating Saw', 19),
       ('Rotary Hammer', 19),
       ('Rotary Tool', 19),
       ('Router', 19),
       ('Scroll Saw', 19),
       ('Sheet Metal Shear', 19),
       ('Table Saw', 19),
       ('Tile Cutter', 19),
       ('Track Saw', 19),
       ('Welding Machine', 19),
       ('Wood Lathe', 19),
       ('Workbench', 19)
ON CONFLICT
    DO NOTHING;
