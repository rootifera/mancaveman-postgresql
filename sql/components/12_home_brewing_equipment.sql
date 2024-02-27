-- Home Brewing Equipment
INSERT INTO component_type (name, hardware_category_id)
VALUES ('Airlock', 12),
       ('Bottle Brush', 12),
       ('Bottle Capper', 12),
       ('Bottles', 12),
       ('Bottling Bucket', 12),
       ('Brew Kettle', 12),
       ('Brewing Thermometer', 12),
       ('Carboy Brush', 12),
       ('Carboy', 12),
       ('Cleaning Sanitizer', 12),
       ('Conical Fermenter', 12),
       ('Cornelius Keg', 12),
       ('Counterflow Chiller', 12),
       ('Fermentation Chamber', 12),
       ('Fermenter', 12),
       ('Funnel', 12),
       ('Grain Mill', 12),
       ('Heating Belt', 12),
       ('Hop Spider', 12),
       ('Hydrometer', 12),
       ('Immersion Chiller', 12),
       ('Keg', 12),
       ('Kegging System', 12),
       ('Mash Paddle', 12),
       ('Mashing Bin', 12),
       ('Measuring Cup', 12),
       ('pH Meter', 12),
       ('pH Test Strips', 12),
       ('Plate Chiller', 12),
       ('Pressure Barrel', 12),
       ('Racking Cane', 12),
       ('Refractometer', 12),
       ('Siphon Tubing', 12),
       ('Siphon', 12),
       ('Sparge Arm', 12),
       ('Spoon or Stirrer', 12),
       ('Stir Plate', 12),
       ('Straining Bag', 12),
       ('Temperature Controller', 12),
       ('Thermometer', 12),
       ('Transfer Pump', 12),
       ('Wort Chiller', 12),
       ('Yeast Starter Kit', 12) ON CONFLICT
    DO NOTHING;
