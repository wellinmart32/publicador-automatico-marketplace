import os

carpeta_principal = "ArticulosMarketplace"

for i in range(1, 6):
    ruta_gitkeep = os.path.join(carpeta_principal, f"Articulo_{i}", "imagenes", ".gitkeep")
    
    # Crear archivo vacío
    with open(ruta_gitkeep, 'w') as f:
        pass
    
    print(f"✓ Creado: {ruta_gitkeep}")

print("\n✅ Todos los archivos .gitkeep creados")
