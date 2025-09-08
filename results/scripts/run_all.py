
# run_all.py – führt alle drei Importe nacheinander aus.

import import_excel_script
import import_xml
import import_mongo

if __name__ == "__main__":
    import_excel_script.run()
    import_xml.run()
    import_mongo.run()
    print("Alle Importe abgeschlossen.")
