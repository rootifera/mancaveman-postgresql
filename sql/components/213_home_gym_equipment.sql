INSERT INTO hardware_category (name)
VALUES ('Home Gym Equipment')

ON CONFLICT
    DO NOTHING;
-- Home Gym Equipment
INSERT INTO component_type (name, hardware_category_id)
VALUES ('Adjustable Bench', 13),
       ('Adjustable Dumbbells', 13),
       ('Barbell', 13),
       ('Battle Ropes', 13),
       ('Dip Station', 13),
       ('Elliptical Trainer', 13),
       ('Exercise Ball', 13),
       ('Exercise Bike', 13),
       ('Foam Roller', 13),
       ('Gym Flooring', 13),
       ('Gym Mat', 13),
       ('Hand Grips', 13),
       ('Jump Rope', 13),
       ('Kettlebells', 13),
       ('Medicine Ball', 13),
       ('Pilates Equipment', 13),
       ('Power Rack', 13),
       ('Pull-up Bar', 13),
       ('Punching Bag', 13),
       ('Resistance Bands', 13),
       ('Rowing Machine', 13),
       ('Sandbags', 13),
       ('Speed Bag', 13),
       ('Spin Bike', 13),
       ('Squat Rack', 13),
       ('Stability Ball', 13),
       ('Stationary Bike', 13),
       ('Step Platform', 13),
       ('Treadmill', 13),
       ('Weight Plates', 13),
       ('Weighted Vest', 13),
       ('Yoga Mat', 13)
ON CONFLICT
    DO NOTHING;
