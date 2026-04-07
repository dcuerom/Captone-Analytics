import subprocess
import re
import os
import csv
import time

# Paths to the instances
instances = {
    "A-n32-k5": "Instancias de Prueba VRP/A/A-n32-k5.vrp",
    "A-n80-k10": "Instancias de Prueba VRP/A/A-n80-k10.vrp",
    "B-n56-k7": "Instancias de Prueba VRP/B/B-n56-k7.vrp",
    "E-n33-k4": "Instancias de Prueba VRP/E/E-n33-k4.vrp",
    "M-n200-k17": "Instancias de Prueba VRP/M/M-n200-k17.vrp",
    "tai-n386-k46": "Instancias de Prueba VRP/tai/tai-n386-k46.vrp",
    "Golden_20-n421-k38": "Instancias de Prueba VRP/Golden/Golden_20-n421-k38.vrp"
}

# Configuration
ITERATIONS = 10
OUTPUT_DIR = "resultados/cvrp"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "consolidado_cvrp_10_iter.csv")

# Regex to find the metrics in stdout
OPTIMO_REGEX = re.compile(r">>>> Optimo Encontrado CVRP Consolidado \(Total Distancia Grilla\): ([\d\.]+)")
TIEMPO_REGEX = re.compile(r">>>> Tiempo de Cómputo Total: ([\d\.]+) segundos")

def run_benchmark():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Initialize the CSV file with headers if it doesn't exist
    file_exists = os.path.isfile(OUTPUT_FILE)
    
    with open(OUTPUT_FILE, mode='a', newline='') as f:
        # User requested CSV structure with | as separator
        # interacion | Instancia | Optimo | tiempo de computo
        writer = csv.writer(f, delimiter='|')
        if not file_exists:
            writer.writerow(["iteracion", "Instancia", "Optimo", "tiempo de computo"])
        
        for name, path in instances.items():
            print(f"=== Evaluando instancia: {name} ({ITERATIONS} iteraciones) ===")
            for i in range(1, ITERATIONS + 1):
                print(f"  Iteración {i}/{ITERATIONS}...", end=" ", flush=True)
                
                start_exec = time.time()
                try:
                    # Execute the algorithm script
                    result = subprocess.run(
                        ["python3", "algoritmo/cvrp_genetic.py", path],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    stdout = result.stdout
                    
                    # Extract distance and time
                    optimo_match = OPTIMO_REGEX.search(stdout)
                    tiempo_match = TIEMPO_REGEX.search(stdout)
                    
                    if optimo_match and tiempo_match:
                        optimo = optimo_match.group(1)
                        tiempo = tiempo_match.group(1)
                        writer.writerow([i, name, optimo, tiempo])
                        f.flush() # Ensure it's written in real-time
                        print(f"Hecho (D={optimo}, T={tiempo}s)")
                    else:
                        print("Fallo - No se pudieron extraer los resultados")
                        writer.writerow([i, name, "Error", "Error"])
                        
                except subprocess.CalledProcessError as e:
                    print(f"Fallo - Error de ejecución: {e}")
                    writer.writerow([i, name, "Crashed", "Crashed"])
                except Exception as e:
                    print(f"Fallo - Error inesperado: {e}")
                    writer.writerow([i, name, "Exception", "Exception"])

if __name__ == "__main__":
    run_benchmark()
