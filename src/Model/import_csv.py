#
# Import CSV module
# Olivier Lecluse
#

def process_line(l, csv_sep):
    name = l.split(csv_sep)[0]
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
    return [ process_line(l, csv_sep) for l in lines ]

if __name__ == "__main__":
    print(import_csv("/home/wawa/Bureau/TS4.csv", ";"))