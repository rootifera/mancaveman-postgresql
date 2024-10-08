INSERT INTO hardware_category (name)
VALUES ('Hobby and Craft Supplies')

ON CONFLICT
    DO NOTHING;

-- Craft and Hobby Supplies
INSERT INTO component_type (name, hardware_category_id)
VALUES ('Acrylic Paint', 11),
       ('Beading Supplies', 11),
       ('Brushes', 11),
       ('Calligraphy Pens', 11),
       ('Canvas', 11),
       ('Ceramic Clay', 11),
       ('Charcoal Pencils', 11),
       ('Craft Glue', 11),
       ('Craft Scissors', 11),
       ('Crochet Hooks', 11),
       ('Cross Stitch Kits', 11),
       ('Decorative Paper', 11),
       ('Embroidery Floss', 11),
       ('Fabric Dye', 11),
       ('Fabric', 11),
       ('Felting Supplies', 11),
       ('Glitter', 11),
       ('Hot Glue Gun', 11),
       ('Jewelry Making Kits', 11),
       ('Knitting Needles', 11),
       ('Leatherworking Tools', 11),
       ('Modelling Clay', 11),
       ('Needlepoint Kits', 11),
       ('Oil Paint', 11),
       ('Origami Paper', 11),
       ('Palette Knives', 11),
       ('Pastels', 11),
       ('Polymer Clay', 11),
       ('Quilting Supplies', 11),
       ('Ribbon', 11),
       ('Scrapbooking Supplies', 11),
       ('Sewing Machine', 11),
       ('Sewing Needles', 11),
       ('Sewing Patterns', 11),
       ('Sketchbooks', 11),
       ('Stamps and Ink Pads', 11),
       ('Stencils', 11),
       ('Stretched Canvas', 11),
       ('Textile Yarn', 11),
       ('Watercolor Paint', 11),
       ('Wire for Jewelry Making', 11),
       ('Wood Carving Tools', 11),
       ('Wool Roving', 11),
       ('Yarn', 11)
ON CONFLICT
    DO NOTHING;
