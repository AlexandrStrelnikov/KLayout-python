class CMD:
    SAY_HELLO = (0).to_bytes(2,byteorder="big")
    CLOSE_CONNECTION = (1).to_bytes(2,byteorder="big")
    FLOAT64_X1 = (2).to_bytes(2,byteorder="big")
    FLOAT64_XNUM = (3).to_bytes(2,byteorder="big")
    POLYGON = (4).to_bytes(2,byteorder="big")
    BOX_PROPS = (5).to_bytes(2,byteorder="big")
    CLEAR_POLYGONS = (6).to_bytes(2,byteorder="big")
    SET_ABS = (7).to_bytes(2,byteorder="big")
    SIMULATE = (8).to_bytes(2,byteorder="big")
    VISUALIZE = (9).to_bytes(2,byteorder="big")
    SET_LINSPACE_SWEEP = (10).to_bytes(2,byteorder="big")