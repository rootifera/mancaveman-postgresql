INSERT INTO hardware_brand (name)
VALUES ('Nike'),
       ('Adidas'),
       ('Under Armour'),
       ('Puma'),
       ('Reebok'),
       ('Asics'),
       ('New Balance'),
       ('Columbia Sportswear'),
       ('The North Face'),
       ('Wilson'),
       ('Easton'),
       ('Mizuno'),
       ('Rawlings'),
       ('Spalding'),
       ('Yonex'),
       ('Salomon'),
       ('Merrell'),
       ('Patagonia'),
       ('Burton Snowboards'),
       ('Schwinn'),
       ('Trek'),
       ('Specialized'),
       ('Ping'),
       ('Titleist'),
       ('Callaway'),
       ('Babolat'),
       ('Speedo'),
       ('Garmin'),
       ('Suunto'),
       ('Life Fitness')
ON CONFLICT
    DO NOTHING;
