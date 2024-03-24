INSERT INTO hardware_brand (name)
VALUES ('Autograph Warehouse'),
       ('Celebrity Authentics'),
       ('Collectible Canvas'),
       ('Funko'),
       ('Heritage Auctions'),
       ('Highland Mint'),
       ('Iconic Replicas'),
       ('Legacy Effects'),
       ('Movie Prop Replicas'),
       ('NECA'),
       ('Panini'),
       ('Precious Collectibles'),
       ('Quantum Mechanix'),
       ('Rare Memorabilia Ltd'),
       ('Sideshow Collectibles'),
       ('Sports Memorabilia'),
       ('Topps'),
       ('Ultra PRO'),
       ('Unique Memorabilia Co'),
       ('Valuable Collectibles Inc')
ON CONFLICT
    DO NOTHING;
