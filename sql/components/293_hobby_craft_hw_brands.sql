INSERT INTO hardware_brand (name)
VALUES ('Beads and Beyond'),
       ('Canvas Corner'),
       ('Ceramic Crafts Corporation'),
       ('Creative Arts Co.'),
       ('Easel and Palette Supplies'),
       ('FiberArts Inc.'),
       ('Fine Arts Materials Ltd.'),
       ('GlassCraft Supplies'),
       ('Jewelry Jems Manufacturing'),
       ('Knit and Stitch'),
       ('LeatherWorks Ltd.'),
       ('MetalCrafts Supplies Co.'),
       ('Model Makers Inc.'),
       ('PaintCraft Supplies'),
       ('Papercraft Creations'),
       ('Quilt Quarters'),
       ('Sculpture Studio Supplies'),
       ('Stationery and Stamps Store'),
       ('Textile Treasures'),
       ('Woodwork Wonders')
ON CONFLICT
    DO NOTHING;
