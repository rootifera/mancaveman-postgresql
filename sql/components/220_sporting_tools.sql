INSERT INTO hardware_category (name)
VALUES
       ('Sporting Goods')
ON CONFLICT
    DO NOTHING;
-- Sporting Equipment
INSERT INTO component_type (name, hardware_category_id)
VALUES ('Archery Bow', 20),
       ('Badminton Racket', 20),
       ('Baseball Bat', 20),
       ('Baseball Glove', 20),
       ('Basketball', 20),
       ('Batting Gloves', 20),
       ('Bicycle', 20),
       ('Billiard Cue', 20),
       ('Bocce Ball Set', 20),
       ('Bowling Ball', 20),
       ('Boxing Gloves', 20),
       ('Cricket Bat', 20),
       ('Cricket Ball', 20),
       ('Cross Trainer', 20),
       ('Curling Equipment', 20),
       ('Dartboard and Darts', 20),
       ('Disc Golf Discs', 20),
       ('Diving Fins', 20),
       ('Elliptical Machine', 20),
       ('Exercise Bike', 20),
       ('Fencing Foil', 20),
       ('Field Hockey Stick', 20),
       ('Fishing Rod', 20),
       ('Football', 20),
       ('Golf Clubs', 20),
       ('Golf Balls', 20),
       ('Gymnastics Equipment', 20),
       ('Handball', 20),
       ('Hockey Puck', 20),
       ('Hockey Stick', 20),
       ('Horse Riding Equipment', 20),
       ('Ice Skates', 20),
       ('Inline Skates', 20),
       ('Javelin', 20),
       ('Kayak', 20),
       ('Kendo Sword', 20),
       ('Lacrosse Stick', 20),
       ('Ping Pong Paddle', 20),
       ('Polo Equipment', 20),
       ('Racquetball Racket', 20),
       ('Rowing Machine', 20),
       ('Rugby Ball', 20),
       ('Running Shoes', 20),
       ('Scuba Diving Gear', 20),
       ('Skateboard', 20),
       ('Skiing Equipment', 20),
       ('Snowboard', 20),
       ('Soccer Ball', 20),
       ('Softball Equipment', 20),
       ('Squash Racket', 20),
       ('Surfboard', 20),
       ('Swimming Goggles', 20),
       ('Table Tennis Table', 20),
       ('Tennis Racket', 20),
       ('Track and Field Equipment', 20),
       ('Treadmill', 20),
       ('Volleyball', 20),
       ('Weightlifting Equipment', 20),
       ('Windsurfing Equipment', 20),
       ('Yoga Mat', 20)
ON CONFLICT
    DO NOTHING;