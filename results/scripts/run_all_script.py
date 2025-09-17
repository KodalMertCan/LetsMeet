
# run_all.py – führt alle drei Importe nacheinander aus.

import import_excel_script
import import_xml_script
import import_mongo_script 

if __name__ == "__main__":
    import_excel_script.run()
    import_xml_script.run()
    import_mongo_script.run()
    print("Alle Importe abgeschlossen.")
