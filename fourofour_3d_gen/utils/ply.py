import struct

def read_custom_ply(data):
    # with open(path, "rb") as f:
    #     # --- Skip header ---
    while True:
        line = data.readline().decode("ascii").strip()
        if line == "end_header":
            break

    fmt = "<14f"  # 14 floats per vertex, little-endian
    size = struct.calcsize(fmt)

    # Read all vertex data
    raw = data.read()
    count = len(raw) // size

    # Bulk unpack
    unpacked = struct.iter_unpack(fmt, raw)

    # Prepare flat lists (ready for foreach_set)
    xyz = []
    f_dc = []
    opacity = []
    scale = []
    rot = []

    for values in unpacked:
        # xyz
        xyz.extend(values[0:3])
        # f_dc
        f_dc.extend(values[3:6])
        # opacity
        opacity.append(values[6])
        # scale
        scale.extend(values[7:10])
        # quaternion (w,x,y,z)
        rot.extend(values[10:14])

    return {
        "xyz": xyz,          # flat [x,y,z,x,y,z,...]
        "f_dc": f_dc,        # flat [r,g,b,r,g,b,...]
        "opacity": opacity,  # list [o,o,o,...]
        "scale": scale,      # flat [sx,sy,sz,...]
        "rot": rot,          # flat [w,x,y,z,w,x,y,z,...]
        "count": count       # number of vertices
    }
