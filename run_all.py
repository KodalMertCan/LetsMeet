
# run_all.py – führt alle drei Importe nacheinander aus.

import import_excel
import import_xml
import import_mongo

if __name__ == "__main__":
    import_excel.run()
    import_xml.run()
    import_mongo.run()
    print("Alle Importe abgeschlossen.")
