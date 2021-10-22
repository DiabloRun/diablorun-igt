if __name__ == "__main__":
    slots = {}

    with open("inventory.csv") as f:
        header = True

        for line in f:
            if header:
                header = False
                continue

            if not line.strip():
                continue

            res_width, res_height, slot, x, y, w, h = line.strip().split(",")
            res = res_width + "_" + res_height

            if not res in slots:
                slots[res] = {}

            slots[res][slot] = [int(x), int(y), int(
                x) + int(w), int(y) + int(h)]

            if slot == "primary_left":
                slots[res]["secondary_left"] = slots[res][slot]

            if slot == "primary_right":
                slots[res]["secondary_right"] = slots[res][slot]

    for res in slots:
        print("RECTS_" + res + " = {")
        for slot in slots[res]:
            l, t, r, b = slots[res][slot]
            print("    '" + slot + "': [" + str(l) + ", " +
                  str(t) + ", " + str(r) + ", " + str(b) + "],")
        print("}")
        print("")
