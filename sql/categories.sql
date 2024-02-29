INSERT INTO hardware_category (name)
VALUES ('Arcade Machines and Accessories'),
       ('Audio and Video Equipment'),
       ('Automotive Accessories'),
       ('Board Games and Puzzles'),
       ('Collectibles'),
       ('Computer Hardware'),
       ('Electronic Components'),
       ('Electronics'),
       ('Gaming Console Accessories'),
       ('Gaming Consoles'),
       ('Hobby and Craft Supplies'),
       ('Home Brewing Equipment'),
       ('Home Gym Equipment'),
       ('Home Theater Systems'),
       ('Memorabilia'),
       ('Model Kits and Miniatures'),
       ('Music Instruments and Equipment'),
       ('Outdoor Equipment'),
       ('Power Tools'),
       ('Sporting Goods'),
       ('Tools')
ON CONFLICT
    DO NOTHING;
