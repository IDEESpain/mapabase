import geopandas as gpd
import json

def main():
    print("Generando excel de municipios...")

    f = open ("./config.json")
    var_dict=json.load(f)

    geojson_municipios=gpd.read_file(var_dict["aux_municipios_file"])

    geojson_municipios["codigo_ine_mun"]=geojson_municipios["codigo"].str.slice(-5).astype(int)
    geojson_municipios["codigo_ine_pais"]=geojson_municipios["codigo"].str.slice(0,2).astype(int)
    geojson_municipios["cod_com_aut"]=geojson_municipios["codigo"].str.slice(2,4).astype(int)
    geojson_municipios["codigo_ine_prov"]=geojson_municipios["codigo"].str.slice(4,6).astype(int)

    excel_path=f"{var_dict['lib_path']}{var_dict['municipios_file']}"

    geojson_municipios.drop(["geometry","proveedor"], axis=1).to_excel(excel_path)


    print("Excel generado correctamente")



if __name__ == '__main__':
    main()
