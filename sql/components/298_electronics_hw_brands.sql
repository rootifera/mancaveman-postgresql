INSERT INTO hardware_brand (name)
VALUES ('Analog Devices'),
       ('AVX Corporation'),
       ('Bourns'),
       ('Cypress Semiconductor'),
       ('Fairchild Semiconductor'),
       ('Infineon Technologies'),
       ('KEMET'),
       ('Littelfuse'),
       ('Maxim Integrated'),
       ('Microchip Technology'),
       ('Murata Manufacturing'),
       ('NXP Semiconductors'),
       ('ON Semiconductor'),
       ('Panasonic Electronic Components'),
       ('Renesas Electronics'),
       ('ROHM Semiconductor'),
       ('STMicroelectronics'),
       ('Taiyo Yuden'),
       ('Texas Instruments'),
       ('Toshiba Electronic Devices & Storage'),
       ('Vishay Intertechnology'),
       ('Yageo')
ON CONFLICT
    DO NOTHING;