INSERT INTO hardware_category (name)
VALUES
       ('Home Theater Systems')
ON CONFLICT
    DO NOTHING;
-- Home Theater Systems
INSERT INTO component_type (name, hardware_category_id)
VALUES ('AV Receiver', 14),
       ('Blu-ray Player', 14),
       ('Bookshelf Speakers', 14),
       ('Cable Management Accessories', 14),
       ('Center Channel Speaker', 14),
       ('Digital Media Player', 14),
       ('DVD Player', 14),
       ('Floor-Standing Speakers', 14),
       ('Gaming Console', 14),
       ('Home Theater PC', 14),
       ('Home Theater Projector', 14),
       ('Home Theater Seating', 14),
       ('In-Ceiling Speakers', 14),
       ('In-Wall Speakers', 14),
       ('Media Server', 14),
       ('Media Streaming Device', 14),
       ('Power Conditioner', 14),
       ('Projection Screen', 14),
       ('Remote Control', 14),
       ('Satellite Speakers', 14),
       ('Soundbar', 14),
       ('Speaker Stands and Mounts', 14),
       ('Subwoofer', 14),
       ('Surge Protector', 14),
       ('Surround Sound Processor', 14),
       ('Surround Sound Speakers', 14),
       ('TV Wall Mount', 14),
       ('Turntable', 14),
       ('Universal Remote', 14),
       ('UHD 4K TV', 14),
       ('Video Calibration Equipment', 14),
       ('VR Headset', 14),
       ('Wireless Audio Transmitters', 14),
       ('Wireless Speaker System', 14)
ON CONFLICT
    DO NOTHING;
