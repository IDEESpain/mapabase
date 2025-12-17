import argparse
import logging
import time
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any

import geopandas as gpd
import mercantile as me
import pandas as pd
from joblib import Parallel, delayed
from shapely.geometry import box

# --- Global Configuration ---
LOG_FORMAT = "%(asctime)s - %(levelname)-8s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# --- Utility Functions ---

def setup_logging(log_file="log-vtiles.txt"):
    """Configures logging to both console and file."""
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # File handler
    file_handler = logging.FileHandler(log_file, "w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    
    # Add handler to root logger
    logging.getLogger().addHandler(file_handler)
    logging.info("Logging configured.")

def handle_interrupt(sig, frame):
    """Gracefully exits on SIGINT."""
    logging.warning("Process interrupted by user. Exiting.")
    sys.exit(0)

# --- Configuration Management ---

class Config:
    """Handles loading and accessing configuration from JSON files."""
    def __init__(self, config_path: str, vtiles_config_path: str):
        self.config_path = Path(config_path)
        self.vtiles_config_path = Path(vtiles_config_path)
        self.data = self._load_config()
        self.vtiles_data = self._load_vtiles_config()

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Loads a JSON file with error handling."""
        if not path.is_file():
            logging.error(f"Configuration file not found: {path}")
            raise FileNotFoundError(f"Configuration file not found: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_config(self) -> Dict[str, Any]:
        return self._load_json(self.config_path)

    def _load_vtiles_config(self) -> Dict[str, Any]:
        return self._load_json(self.vtiles_config_path)

    def __getitem__(self, key: str) -> Any:
        """Allows dictionary-style access to config data."""
        return self.data.get(key)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Allows dictionary-style .get() access to config data."""
        return self.data.get(key, default)
    
    @property
    def zoom_levels(self) -> List[Dict[str, Any]]:
        return self.vtiles_data.get("zoom_levels", [])

# --- Core Pipeline Logic ---

class VectorTilePipeline:
    """Orchestrates the entire vector tile generation process."""

    
    def __init__(self, config: Config):
        self.config = config
        self.num_cores = config.get('num_cores') or os.cpu_count() or 2
        
        # Ensure environment is set up if needed
        if 'LD_LIBRARY_PATH' not in os.environ:
            os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib:/usr/local/boost/1.60.0/lib64'
            logging.info("Updated LD_LIBRARY_PATH environment variable.")

    def _run_command(self, command: List[str], cwd: str = None):
        """Executes a shell command with robust logging and error handling."""
        command_str = " ".join(map(shlex.quote, command))
        logging.info(f"Executing command: {command_str}")
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=cwd)
            logging.debug(f"Command successful: {command_str}")
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed: {command_str}")
            logging.error(f"Return code: {e.returncode}")
            # The stdout/stderr might not be available on Popen object in the same way
            if hasattr(e, 'stdout') and e.stdout: logging.error(f"STDOUT: {e.stdout.strip()}")
            if hasattr(e, 'stderr') and e.stderr: logging.error(f"STDERR: {e.stderr.strip()}")
            raise

    def compress_geospatial_files(self):
        """Converts VRT files to gzipped GeoJSONSeq using ogr2ogr."""
        logging.info("Starting conversion from VRT to gzipped GeoJSONSeq.")
        
        source_map = {
            "input_vrt_IGN": "gz_folder_IGN",
            "input_vrt_comunidades": "gz_folder_comunidades",
            "input_vrt_municipios": "gz_folder_municipios"
        }

        for input_key, output_key in source_map.items():
            input_dir = Path(self.config[input_key])
            output_dir = Path(self.config[output_key])
            output_dir.mkdir(parents=True, exist_ok=True)

            if not input_dir.is_dir():
                logging.warning(f"Input directory not found, skipping: {input_dir}")
                continue

            vrt_files = list(input_dir.glob("*.vrt"))
            
            def process_file(vrt_file: Path):
                output_file = output_dir / f"{vrt_file.stem}.gz"
                command = [
                    "ogr2ogr",
                    "-f", "GeoJSONSeq",
                    "-skipfailures",
                    str(output_file),
                    str(vrt_file)
                ]
                self._run_command(command)

            Parallel(n_jobs=self.num_cores)(delayed(process_file)(f) for f in vrt_files)
        logging.info("Finished VRT to GeoJSONSeq conversion.")

    def _build_tippecanoe_command(self, zoom_config: Dict, output_file: Path, input_data_path: Path = None) -> Dict[str, List[str]]:
        """Builds the tippecanoe command arguments for different layer types."""
        zoom = str(zoom_config['level'])
        
        if not input_data_path:
            if self.config['min_zoom_IGN'] <= int(zoom) <= self.config['max_zoom_IGN']:
                input_data_path = Path(self.config['gz_folder_IGN'])
            elif self.config['min_zoom_comunidades'] <= int(zoom) <= self.config['max_zoom_comunidades']:
                input_data_path = Path(self.config['gz_folder_comunidades'])
            else:
                input_data_path = Path(self.config['gz_folder_municipios'])

        base_args = [
            "--force",
            f"-z{zoom}", f"-Z{zoom}",
            "-j", json.dumps(zoom_config["filter"]),
            "-t", self.config["temp_directory"],
            "--no-feature-limit",
            "--no-tile-size-limit",
            "--convert-stringified-ids-to-numbers",
            "--attribute-type=population:int",
            "--attribute-type=sqkm:int",
            "-pC"
        ]

        commands = {}

        def create_layer_args(layers):
            args = []
            for layer in layers:
                source_file = input_data_path / layer['file']
                if source_file.exists():
                    args.extend([f"--named-layer={layer['name']}:{source_file}"])
                else:
                    logging.warning(f"Source file for layer '{layer['name']}' not found, skipping: {source_file}")
            return args

        if zoom_config.get('layers'):
            layer_args = create_layer_args(zoom_config['layers'])
            if layer_args:
                cmd = ["tippecanoe", "-o", str(output_file.with_name(f"{output_file.stem}_layers.mbtiles"))]
                cmd.extend(layer_args)
                cmd.extend(base_args)
                cmd.extend(["--buffer=44", "--coalesce", "--reorder"])
                if int(zoom) < 11:
                    cmd.append("--simplification=12")
                commands['layers'] = cmd

        if zoom_config.get('layers_with_labels'):
            layer_args = create_layer_args(zoom_config['layers_with_labels'])
            if layer_args:
                cmd = ["tippecanoe", "-P", "-o", str(output_file.with_name(f"{output_file.stem}_labels.mbtiles"))]
                cmd.extend(layer_args)
                cmd.extend(base_args)
                cmd.append("--buffer=127")
                commands['labels'] = cmd
            
        if zoom_config.get('layers_no_coalesce'):
            layer_args = create_layer_args(zoom_config['layers_no_coalesce'])
            if layer_args:
                cmd = ["tippecanoe", "-P", "-o", str(output_file.with_name(f"{output_file.stem}_no_coalesce.mbtiles"))]
                cmd.extend(layer_args)
                cmd.extend(base_args)
                cmd.extend(["--buffer=44", "--reorder"])
                commands['no_coalesce'] = cmd
            
        return commands

    def generate_tiles(self, mbtiles_dir: Path, temp_dir: Path, input_data_path: Path = None, zoom_configs: List[Dict[str, Any]] = None):
        """Generates MBTiles for specified zoom levels using Tippecanoe."""
        if zoom_configs is None:
            zoom_configs = self.config.zoom_levels

        logging.info(f"Starting MBTiles generation for {len(zoom_configs)} zoom level(s). Output directory: {mbtiles_dir}")
        mbtiles_dir.mkdir(parents=True, exist_ok=True)
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        for zoom_config in zoom_configs:
            if zoom_config.get('process', 'yes') == 'no':
                continue
            
            zoom_level = zoom_config['level']
            logging.info(f"Processing zoom level: {zoom_level}")
            
            output_basename = f"CNIG_{zoom_level}"
            final_mbtile = mbtiles_dir / f"{output_basename}.mbtiles"

            tippecanoe_commands = self._build_tippecanoe_command(zoom_config, final_mbtile, input_data_path)
            
            if not tippecanoe_commands:
                logging.warning(f"No layers to process for zoom {zoom_level}. Skipping.")
                continue

            for layer_type, command in tippecanoe_commands.items():
                logging.info(f"Generating '{layer_type}' tiles for zoom {zoom_level}...")
                self._run_command(command)
            
            layer_types = list(tippecanoe_commands.keys())
            intermediate_files = [mbtiles_dir / f"{output_basename}_{suffix}.mbtiles" for suffix in ['layers', 'labels', 'no_coalesce'] if suffix in layer_types]

            if len(intermediate_files) > 1:
                logging.info(f"Joining MBTiles for zoom {zoom_level}...")
                join_command = ["tile-join", "-pk", "-pC", "--force", "-o", str(final_mbtile)]
                join_command.extend(map(str, intermediate_files))
                self._run_command(join_command)
                
                for f in intermediate_files:
                    f.unlink(missing_ok=True)
            elif len(intermediate_files) == 1:
                intermediate_files[0].rename(final_mbtile)

        logging.info("Finished MBTiles generation.")

    def flatten_pbf_extraction_folder(self, source_base: Path):

        logging.info(f"Restructuring tiles from {source_base}")
        for cnig_folder in source_base.glob("CNIG_*"):
            if not cnig_folder.is_dir():
                continue
            for zoom_folder in cnig_folder.glob("[0-9]*"):
                if not zoom_folder.is_dir():
                    continue
                target_folder = source_base / zoom_folder.name
                if target_folder.exists():
                    shutil.rmtree(target_folder)
                shutil.move(str(zoom_folder), str(target_folder))

            metadata_file = cnig_folder / "metadata.json"
            if metadata_file.exists():
                zoom_folders = [f for f in cnig_folder.iterdir() if f.is_dir() and f.name.isdigit()]
                for target_folder in zoom_folders:
                    shutil.move(str(metadata_file), str(target_folder / "metadata.json"))

            shutil.rmtree(cnig_folder)
        logging.info("Tiles restructuring finished.")

    def extract_pbf_from_mbtiles(self, mbtiles_dir: Path, output_pbf_dir: Path):
        logging.info(f"Extracting PBF tiles from {mbtiles_dir} to {output_pbf_dir}.")
        mbtiles_files = list(mbtiles_dir.glob("*.mbtiles"))
        output_pbf_dir.mkdir(parents=True, exist_ok=True)

        def extract_file(mbtile_path: Path):
            output_folder = output_pbf_dir / mbtile_path.stem
            if output_folder.exists():
                shutil.rmtree(output_folder)
            command = ["mb-util", "--image_format=pbf", str(mbtile_path), str(output_folder)]
            self._run_command(command)

        Parallel(n_jobs=self.num_cores)(delayed(extract_file)(f) for f in mbtiles_files)

        self.flatten_pbf_extraction_folder(output_pbf_dir)
        logging.info("Finished PBF extraction.")

    def organize_final_tiles(self, pbf_source_dir: Path, final_dest_dir: Path):
        logging.info(f"Organizing final tiles from {pbf_source_dir} to {final_dest_dir} using rsync.")
        final_dest_dir.mkdir(exist_ok=True)
        command = [
            "rsync",
            "-a",
            "--info=progress2",
            "--include=*/",
            "--include=*.pbf",
            "--include=metadata.json",
            "--exclude=*",
            str(pbf_source_dir.resolve()) + "/",
            str(final_dest_dir.resolve())
        ]
        self._run_command(command)
        logging.info("Final tiles organized.")
    
    def _merge_updated_tiles(self, update_pbf_dir: Path, final_dest_dir: Path, tiles_to_replace: set):
        """Merges new tiles into the final destination by overwriting."""
        logging.info(f"Merging {len(tiles_to_replace)} updated tiles into {final_dest_dir}.")
        for z, x, y in tiles_to_replace:
            zoom_str = str(z)
            source_file = update_pbf_dir / zoom_str / str(x) / f"{y}.pbf"
            if source_file.exists():
                dest_dir = final_dest_dir / zoom_str / str(x)
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_file = dest_dir / f"{y}.pbf"
                shutil.copy2(source_file, dest_file)
            
    def generate_master_metadata(self):
        """Generates a master metadata.json using config_vtiles without parsing all tile JSONs."""
        logging.info("Generating master metadata.json based on config_vtiles.")

        dest_folder = Path(self.config["destination_folder"])
        vector_layers = {}
        tilestats = {}

        for zoom_level_conf in self.config.vtiles_data.get("zoom_levels", []):
            for layer_type in ['layers', 'layers_with_labels', 'layers_no_coalesce']:
                for layer in zoom_level_conf.get(layer_type, []):
                    layer_id = layer['name']
                    if layer_id not in vector_layers:
                        vector_layers[layer_id] = {
                            "id": layer_id,
                            "minzoom": zoom_level_conf['level'],
                            "maxzoom": zoom_level_conf['level'],
                            "description": layer.get('description', ''),
                            "fields": {}
                        }
                    else:
                        vec_layer = vector_layers[layer_id]
                        vec_layer['minzoom'] = min(vec_layer['minzoom'], zoom_level_conf['level'])
                        vec_layer['maxzoom'] = max(vec_layer['maxzoom'], zoom_level_conf['level'])

        if not vector_layers:
            logging.warning("No vector layers found in config_vtiles. Skipping master metadata generation.")
            return

        output_json = {
            "tilejson": "3.0.0",
            "name": "Mapa Ciudadano del Sistema Cartográfico Nacional",
            "description": "Servicio de visualización (Servicio de Teselas Vectoriales, MVT) del Sistema Cartográfico Nacional. Base de datos multiescala con cobertura completa y continua para España, que combina diferentes fuentes de datos. Teselas desde nivel de zoom 0 hasta nivel de zoom 17",
            "type": "overlay",
            "scheme": "xyz",
            "format": "pbf",
            "version": "1.0.0",
            "tiles": ["https://vt-mapabase.idee.es/1.0.0/mapabase/{z}/{x}/{y}.pbf"],
            "attribution": "<a href='https://www.scne.es//'>CC BY 4.0 scne</a>",
            "bounds": [-180, -90, 180, 90],
            "center": [-11.5, 35.789, 5],
            "minzoom": 0,
            "maxzoom": 18,
            "MetadataUrl": "https://ideespain.github.io/mapabase/",
            "vector_layers": sorted(list(vector_layers.values()), key=lambda x: x['id']),
            "tilestats": tilestats,
        }

        output_path = dest_folder / 'metadata.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_json, f, ensure_ascii=False, indent=4)

        logging.info(f"Master metadata.json successfully created at {output_path}")



    def run_full_process(self):
        """Executes the entire pipeline for all data."""
        setup = self.config.get('setup', {})
        
        if setup.get('compress_geojson') == 'yes':
            self.compress_geospatial_files()
        
        mbtiles_dir = Path(self.config['destination_mbtiles'])
        temp_dir = Path(self.config['temp_directory'])
        final_dest = Path(self.config['destination_folder'])
        
        pbf_output_dir = temp_dir / "pbfs_extracted"
        if pbf_output_dir.exists():
            shutil.rmtree(pbf_output_dir)

        if setup.get('tiling_layers') == 'yes':
            self.generate_tiles(mbtiles_dir, temp_dir)
        
        if setup.get('to_folder') == 'yes':
            self.extract_pbf_from_mbtiles(mbtiles_dir, pbf_output_dir)
        
        if setup.get('move_to_final_folder') == 'yes':
            self.organize_final_tiles(pbf_output_dir, final_dest)
            
        if setup.get('join_json') == 'yes':
            self.generate_master_metadata()

        logging.info("Cleaning up temporary directories...")
        shutil.rmtree(temp_dir)
        if mbtiles_dir.exists():
            shutil.rmtree(mbtiles_dir)


    def _get_bbox_for_region(self, region_code: int, mode: str) -> List[float]:
        """Reads a feature file, finds a region by its code, and returns its bounding box."""
        if mode == 'comunidades':
            file_path = self.config.get('aux_comunidades_file')
            code_str = str(region_code).zfill(2)
            filter_logic = lambda gdf: gdf[gdf["codigo"].str.slice(2, 4) == code_str]
        elif mode == 'municipios':
            file_path = self.config.get('aux_municipios_file')
            code_str = str(region_code).zfill(5)
            filter_logic = lambda gdf: gdf[gdf["codigo"].str.slice(-5) == code_str]
        else:
            raise ValueError(f"Invalid region mode: {mode}")

        if not file_path or not Path(file_path).exists():
            raise FileNotFoundError(f"Auxiliary file for '{mode}' not found at path: {file_path}")
        
        logging.info(f"Reading regions from {file_path} to find code '{code_str}'")
        gdf = gpd.read_file(file_path)
        
        region_gdf = filter_logic(gdf)
        
        if region_gdf.empty:
            logging.warning(f"No region found for code '{region_code}' in mode '{mode}'.")
            return None
            
        bounds = region_gdf.iloc[0].geometry.bounds
        bbox = [bounds[0], bounds[1], bounds[2], bounds[3]]
        logging.info(f"Found BBOX for code '{region_code}': {bbox}")
        return bbox

    def _get_tile_aligned_bbox(self, bbox: List[float], zooms: List[int]) -> List[float]:
        """Calculates a bounding box that snaps to the outer boundaries of all tiles intersecting the given bbox."""
        logging.info(f"Calculating tile-aligned BBOX for {bbox} at zooms {zooms}")
        
        intersecting_tiles = list(me.tiles(*bbox, zooms=zooms))
        
        if not intersecting_tiles:
            logging.warning("No intersecting tiles found for the given BBOX. Returning original BBOX.")
            return bbox

        first_bounds = me.bounds(intersecting_tiles[0])
        min_lon, min_lat, max_lon, max_lat = first_bounds.west, first_bounds.south, first_bounds.east, first_bounds.north

        for tile in intersecting_tiles[1:]:
            bounds = me.bounds(tile)
            min_lon = min(min_lon, bounds.west)
            min_lat = min(min_lat, bounds.south)
            max_lon = max(max_lon, bounds.east)
            max_lat = max(max_lat, bounds.north)
            
        aligned_bbox = [min_lon, min_lat, max_lon, max_lat]
        logging.info(f"Original BBOX: {bbox} -> Tile-aligned BBOX: {aligned_bbox}")
        return aligned_bbox

    def _prepare_clipped_sources(self, bbox: List[float], clipped_gz_dir: Path, zoom_configs: List[Dict[str, Any]]) -> Path:
        """Clips VRT sources to a given BBOX using ogr2ogr for a specific set of zoom levels."""
        logging.info(f"Preparing clipped data sources for BBOX {bbox} into {clipped_gz_dir}")
        clipped_gz_dir.mkdir(parents=True, exist_ok=True)
        
        required_files = set()
        source_map = {}
        for zc in zoom_configs:
            zoom = zc['level']
            if self.config['min_zoom_IGN'] <= zoom <= self.config['max_zoom_IGN']:
                vrt_base = Path(self.config['input_vrt_IGN'])
            elif self.config['min_zoom_comunidades'] <= zoom <= self.config['max_zoom_comunidades']:
                vrt_base = Path(self.config['input_vrt_comunidades'])
            else:
                vrt_base = Path(self.config['input_vrt_municipios'])

            for layer_type in ['layers', 'layers_with_labels', 'layers_no_coalesce']:
                for layer in zc.get(layer_type, []):
                    file_name = layer['file']
                    if file_name not in required_files:
                        required_files.add(file_name)
                        source_map[file_name] = vrt_base / file_name.replace('.gz', '.vrt')

        bbox_str = [str(c) for c in bbox]

        def clip_file(file_name: str):
            source_vrt = source_map[file_name]
            output_gz = clipped_gz_dir / file_name
            if source_vrt.exists():
                command = [
                    "ogr2ogr",
                    "-f", "GeoJSONSeq",
                    "-clipdst", *bbox_str,
                    str(output_gz),
                    str(source_vrt)
                ]
                self._run_command(command)
        
        Parallel(n_jobs=self.num_cores)(delayed(clip_file)(f) for f in required_files)
        
        logging.info("Finished clipping data sources.")
        return clipped_gz_dir

    def run_update_process(self, mode: str, bbox: List[float] = None):
        """Runs a seamless and performant update by processing each zoom level individually."""
        if not bbox or len(bbox) != 4:
            raise ValueError("A valid BBOX is required for update operations.")

        logging.info(f"Starting seamless update for BBOX: {bbox}")
        setup = self.config.get('setup', {})
        
        if setup.get('compress_geojson') == 'yes':
            self.compress_geospatial_files()
            
        base_temp_dir = Path(self.config["temp_directory"])
        update_mbtiles_dir = base_temp_dir / "update_mbtiles"
        update_pbf_dir = base_temp_dir / "update_pbfs"
        final_dest_dir = Path(self.config["destination_folder"])
        
        if update_mbtiles_dir.exists(): shutil.rmtree(update_mbtiles_dir)
        if update_pbf_dir.exists(): shutil.rmtree(update_pbf_dir)

        active_zoom_configs = [z for z in self.config.zoom_levels if z.get('process', 'yes') == 'yes']
        active_zoom_levels = [z['level'] for z in active_zoom_configs]
        
        tiles_to_replace = set((t.z, t.x, t.y) for t in me.tiles(*bbox, zooms=active_zoom_levels))
        
        for zoom_config in active_zoom_configs:
            zoom_level = zoom_config['level']
            logging.info(f"--- Starting update process for zoom level {zoom_level} ---")

            clipped_gz_dir_zoom = base_temp_dir / f"clipped_gz_z{zoom_level}"
            if clipped_gz_dir_zoom.exists(): shutil.rmtree(clipped_gz_dir_zoom)

            tile_aligned_bbox = self._get_tile_aligned_bbox(bbox, [zoom_level])
            
            buffer = 0.01
            buffered_tile_aligned_bbox = [
                tile_aligned_bbox[0] - buffer, 
                tile_aligned_bbox[1] - buffer, 
                tile_aligned_bbox[2] + buffer, 
                tile_aligned_bbox[3] + buffer
            ]
            
            clipped_data_path = self._prepare_clipped_sources(buffered_tile_aligned_bbox, clipped_gz_dir_zoom, [zoom_config])
            
            if setup.get('tiling_layers') == 'yes':
                self.generate_tiles(
                    mbtiles_dir=update_mbtiles_dir,
                    temp_dir=base_temp_dir,
                    input_data_path=clipped_data_path,
                    zoom_configs=[zoom_config]
                )

            shutil.rmtree(clipped_gz_dir_zoom)
            logging.info(f"--- Finished update process for zoom level {zoom_level} ---")

        if setup.get('to_folder') == 'yes':
            self.extract_pbf_from_mbtiles(update_mbtiles_dir, update_pbf_dir)

        if setup.get('move_to_final_folder') == 'yes':
            self._merge_updated_tiles(update_pbf_dir, final_dest_dir, tiles_to_replace)

        if setup.get('join_json') == 'yes':
            self.generate_master_metadata()

        logging.info("Cleaning up main temporary update directories...")
        shutil.rmtree(update_mbtiles_dir)
        if update_pbf_dir.exists(): shutil.rmtree(update_pbf_dir)
        logging.info("Seamless update process complete.")

# --- Main Execution ---

def main():
    """Main entry point controlled by config file."""
    start_time = time.time()
    setup_logging()
    signal.signal(signal.SIGINT, handle_interrupt)
    
    try:
        config = Config('config.json', 'config_vtiles.json')
        pipeline = VectorTilePipeline(config)
        
        update_mode = config.get('update', "").strip()

        if update_mode:
            logging.info(f"Starting update run with mode: {update_mode}")
            
            if update_mode in ['bbox', 'nacional', 'peninsula']:
                update_bbox = None
                if update_mode == 'bbox':
                    update_bbox = config.get('bbox')
                elif update_mode == 'nacional':
                    update_bbox = [-19.22, 26.62, 6.35, 44.80]
                elif update_mode == 'peninsula':
                    update_bbox = [-9.94, 35.01, 4.64, 44.1]
                
                if not update_bbox:
                    raise ValueError(f"BBOX not found in config for update mode '{update_mode}'")
                
                pipeline.run_update_process(mode=update_mode, bbox=update_bbox)

            elif update_mode in ['comunidades', 'municipios']:
                key = 'lista_comunidades' if update_mode == 'comunidades' else 'lista_municipios'
                region_codes = config.get(key)
                
                if not region_codes:
                    raise ValueError(f"List of region codes ('{key}') not found in config for update mode '{update_mode}'")
                    
                for code in region_codes:
                    logging.info(f"--- Processing region code: {code} for {update_mode} ---")
                    update_bbox = pipeline._get_bbox_for_region(region_code=code, mode=update_mode)
                    if update_bbox:
                        pipeline.run_update_process(mode=update_mode, bbox=update_bbox)
                    else:
                        logging.error(f"Could not find BBOX for region code {code}. Skipping.")
            else:
                raise ValueError(f"Update mode '{update_mode}' is not recognized.")

        else:
            logging.info("Starting full pipeline run.")
            pipeline.run_full_process()
            
    except Exception as e:
        logging.critical(f"A critical error occurred: {e}", exc_info=True)
        sys.exit(1)
        
    end_time = time.time()
    duration = end_time - start_time
    logging.info(f"Pipeline finished successfully in {time.strftime('%H:%M:%S', time.gmtime(duration))}.")

if __name__ == "__main__":
    main()

