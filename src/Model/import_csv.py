# Salle de classe by Lecluse DevCorp
# file author : Olivier Lecluse
# Licence GPL-v3 - see LICENCE.txt
#
# Import CSV module

def process_line(ln, csv_sep):
    name = ln.split(csv_sep)[0]
    if name == "":
        return name
    if name[0] == name[-1] and name[0] in ['"', "'"]:
        name = name[1:-1]
    nom_prenom = name.split(" ")
    if len(nom_prenom) == 2:
        return nom_prenom
    else:
        return [' '.join(nom_prenom[:-1]), nom_prenom[-1]]


def import_csv(file_name, csv_sep):
    file = open(file_name, "r")
    lines = file.readlines()
    lines.pop(0)
    result = []
    for ln in lines:
        nom_prenom = process_line(ln, csv_sep)
        if nom_prenom != "":
            result.append(nom_prenom)
    return result


if __name__ == "__main__":
    print(process_line("DURAND Robert-Edouard", ";"))
