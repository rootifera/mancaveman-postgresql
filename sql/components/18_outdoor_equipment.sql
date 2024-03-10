INSERT INTO hardware_category (name)
VALUES
       ('Outdoor Equipment')
ON CONFLICT
    DO NOTHING;
-- Outdoor Equipment
INSERT INTO component_type (name, hardware_category_id)
VALUES ('Backpack', 18),
       ('Bicycle Repair Kit', 18),
       ('Binoculars', 18),
       ('Camping Chair', 18),
       ('Camping Cookware', 18),
       ('Camping Stove', 18),
       ('Climbing Gear', 18),
       ('Compass', 18),
       ('Cooler Box', 18),
       ('Diving Equipment', 18),
       ('Fishing Gear', 18),
       ('Flashlight', 18),
       ('GPS Device', 18),
       ('Hammock', 18),
       ('Headlamp', 18),
       ('Hiking Boots', 18),
       ('Inflatable Boat', 18),
       ('Insect Repellent', 18),
       ('Kayak', 18),
       ('Mountain Bike', 18),
       ('Outdoor Clothing', 18),
       ('Parachute Hammock', 18),
       ('Picnic Basket', 18),
       ('Portable Grill', 18),
       ('Sleeping Bag', 18),
       ('Sleeping Pad', 18),
       ('Snorkeling Gear', 18),
       ('Snowboard', 18),
       ('Snowshoes', 18),
       ('Solar Charger', 18),
       ('Sunscreen', 18),
       ('Surfboard', 18),
       ('Survival Kit', 18),
       ('Swimming Goggles', 18),
       ('Tent', 18),
       ('Thermal Clothing', 18),
       ('Trekking Poles', 18),
       ('Water Bottle', 18),
       ('Water Filter', 18),
       ('Waterproof Camera', 18),
       ('Weather Station', 18),
       ('Wildlife Camera', 18),
       ('Windbreaker Jacket', 18)
ON CONFLICT
    DO NOTHING;
