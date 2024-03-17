INSERT INTO hardware_category (name)
VALUES ('Memorabilia')
ON CONFLICT
    DO NOTHING;
-- Memorabilia
INSERT INTO component_type (name, hardware_category_id)
VALUES ('Autographed Items', 15),
       ('Band Merchandise', 15),
       ('Baseball Cards', 15),
       ('Basketball Cards', 15),
       ('Celebrity Photographs', 15),
       ('Comic Books', 15),
       ('Concert Posters', 15),
       ('Film Props', 15),
       ('Football Cards', 15),
       ('Historical Documents', 15),
       ('Hockey Cards', 15),
       ('Limited Edition Collectibles', 15),
       ('Movie Posters', 15),
       ('Music Albums', 15),
       ('Numismatic Coins', 15),
       ('Philatelic Stamps', 15),
       ('Rare Books', 15),
       ('Signed Jerseys', 15),
       ('Signed Sports Equipment', 15),
       ('Sports Memorabilia', 15),
       ('Sports Trophies', 15),
       ('Television Memorabilia', 15),
       ('Theater Memorabilia', 15),
       ('Trading Card Games', 15),
       ('TV Show Props', 15),
       ('Vinyl Records', 15),
       ('Vintage Advertising Items', 15),
       ('Vintage Toys', 15),
       ('War Memorabilia', 15)
ON CONFLICT
    DO NOTHING;
