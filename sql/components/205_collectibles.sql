INSERT INTO hardware_category (name)
VALUES ('Collectibles')

ON CONFLICT
    DO NOTHING;
-- Collectibles
INSERT INTO component_type (name, hardware_category_id)
VALUES ('Action Figures', 5),
       ('Action Figures - Anime', 5),
       ('Action Figures - Cartoons', 5),
       ('Action Figures - Fantasy', 5),
       ('Action Figures - Horror', 5),
       ('Action Figures - Movie Characters', 5),
       ('Action Figures - Sci-Fi', 5),
       ('Action Figures - Superheroes', 5),
       ('Antique Coins', 5),
       ('Antique Maps', 5),
       ('Autographed Memorabilia', 5),
       ('Baseball Cards', 5),
       ('Classic Board Games', 5),
       ('Classic Vinyl Albums', 5),
       ('Collectible Coins', 5),
       ('Collectible Comic Strips', 5),
       ('Collectible Pins', 5),
       ('Collectible Statues', 5),
       ('Comic Art', 5),
       ('Comic Books', 5),
       ('Die-Cast Model Cars', 5),
       ('Dolls and Toys', 5),
       ('Funko Pop! Figures', 5),
       ('Hot Wheels', 5),
       ('Lego Sets', 5),
       ('Magic: The Gathering Cards', 5),
       ('Model Trains', 5),
       ('Movie Memorabilia', 5),
       ('Movie Props', 5),
       ('Nostalgic Lunchboxes', 5),
       ('Rare Art Prints', 5),
       ('Rare Books', 5),
       ('Rare Stamps', 5),
       ('Sports Memorabilia', 5),
       ('Star Wars Collectibles', 5),
       ('Trading Cards', 5),
       ('Vintage Action Figures', 5),
       ('Vintage Cameras', 5),
       ('Vintage Magazines', 5),
       ('Vintage Newspapers', 5),
       ('Vintage Postcards', 5),
       ('Vintage Posters', 5),
       ('Vintage Toy Trucks', 5),
       ('Vintage Video Game Consoles', 5),
       ('Vintage Vinyl Records', 5),
       ('Vinyl Records', 5),
       ('Warhammer Miniatures', 5),
       ('Watches and Timepieces', 5)
ON CONFLICT
    DO NOTHING;