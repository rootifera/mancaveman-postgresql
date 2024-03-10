INSERT INTO hardware_category (name)
VALUES
       ('Model Kits and Miniatures')
ON CONFLICT
    DO NOTHING;
-- Model Kits and Miniatures
INSERT INTO component_type (name, hardware_category_id)
VALUES ('Aircraft Model Kits', 16),
       ('Anime Figure Kits', 16),
       ('Architectural Model Kits', 16),
       ('Car Model Kits', 16),
       ('Dinosaur Model Kits', 16),
       ('Diorama Kits', 16),
       ('Fantasy Miniatures', 16),
       ('Figure Model Kits', 16),
       ('Gundam Model Kits', 16),
       ('Historical Miniatures', 16),
       ('Military Model Kits', 16),
       ('Miniature Buildings', 16),
       ('Miniature Painting Supplies', 16),
       ('Model Boats and Ships', 16),
       ('Model Railroad Kits', 16),
       ('Model Rocketry Kits', 16),
       ('Model Tool Kits', 16),
       ('Monster Model Kits', 16),
       ('Motorcycle Model Kits', 16),
       ('Robot Model Kits', 16),
       ('Scale Model Kits', 16),
       ('Science Fiction Model Kits', 16),
       ('Spacecraft Model Kits', 16),
       ('Superhero Model Kits', 16),
       ('Tabletop Game Miniatures', 16),
       ('Tank Model Kits', 16),
       ('Train Model Kits', 16),
       ('Truck Model Kits', 16),
       ('Warship Model Kits', 16),
       ('Wildlife Miniatures', 16)
ON CONFLICT
    DO NOTHING;
