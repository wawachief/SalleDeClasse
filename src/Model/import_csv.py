#
# Import CSV module
# Olivier Lecluse
#

def process_line(ln, csv_sep):
    name = ln.split(csv_sep)[0]
    if '"' in name or "'" in name:
        name = eval(name)
    nom_prenom = name.split(" ")
    if len(nom_prenom) == 2:
        return nom_prenom
    else:
        return [' '.join(nom_prenom[:-1]), nom_prenom[-1]]


def import_csv(file_name, csv_sep):
    file = open(file_name, "r")
    lines = file.readlines()
    lines.pop(0)
    return [process_line(ln, csv_sep) for ln in lines]


if __name__ == "__main__":
    print(process_line("DURAND Robert-Edouard", ";"))
