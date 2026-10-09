# import subprocess
# import sys

# print("Installation des dépendances...")
# subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

# print("Téléchargement des données...")
# subprocess.run([sys.executable, "download_data.py"], check=True)

# notebooks = [
#     "analyse_jalon_1.ipynb",
#     "analyse_jalon_2.ipynb",
#     "analyse_jalon_3.ipynb",
#     "analyse_jalon_4.ipynb",
# ]

# for nb in notebooks:
#     print(f"Exécution de {nb}...")
#     subprocess.run([
#         sys.executable, "-m", "jupyter", "nbconvert",
#         "--to", "notebook", "--execute", "--inplace", nb
#     ], check=True)

# print("Terminé : toutes les étapes ont été exécutées dans l'ordre.")

# import subprocess
# import sys

# print("Vérification et installation de pip dans l'environnement...")
# try:
#     subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
# except subprocess.CalledProcessError:
#     # Si pip n'est pas présent, on l'installe via ensurepip
#     subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)

# print("Installation des dépendances...")
# subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

# print("Téléchargement des données...")
# subprocess.run([sys.executable, "download_data.py"], check=True)

# notebooks = [
#     "analyse_jalon_1.ipynb",
#     "analyse_jalon_2.ipynb",
#     "analyse_jalon_3.ipynb",
#     "analyse_jalon_4.ipynb",
# ]

# for nb in notebooks:
#     print(f"Exécution de {nb}...")
#     subprocess.run([
#         sys.executable, "-m", "jupyter", "nbconvert",
#         "--to", "notebook", "--execute", "--inplace", nb
#     ], check=True)

# print("Terminé : toutes les étapes ont été exécutées dans l'ordre.")


import os
import sys
import platform
import subprocess
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent

NOTEBOOKS = [
    "Analyse_jalon_1.ipynb",
    "Analyse_jalon_2.ipynb",
    "analyse_jalon_3.ipynb",
    "analyse_jalon_4.ipynb",
]


def run_command(command, cwd=ROOT_DIR):
    """Execute a command and return its status and output."""
    print(f"\n$ {' '.join(map(str, command))}")

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            print(result.stdout)
        return True, result.stdout

    except subprocess.CalledProcessError as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        print(output)
        return False, output

    except FileNotFoundError as exc:
        print(f"Commande introuvable : {exc}")
        return False, str(exc)


def get_venv_python():
    """Return the Python executable inside .venv."""
    if platform.system() == "Windows":
        return ROOT_DIR / ".venv" / "Scripts" / "python.exe"

    return ROOT_DIR / ".venv" / "bin" / "python"


def install_uv():
    """Install uv if it is not already available."""
    success, _ = run_command(["uv", "--version"])

    if success:
        return True

    print("📦 Installation de uv...")
    return run_command([
        sys.executable, "-m", "pip", "install", "uv"
    ])[0]


def setup_uv():
    """Create the uv environment and install project dependencies."""
    if not (ROOT_DIR / "pyproject.toml").exists():
        print("❌ Fichier pyproject.toml introuvable.")
        return False

    if not install_uv():
        print("❌ Impossible d'installer ou d'utiliser uv.")
        return False

    # Create/synchronize the project environment and dependencies.
    success, _ = run_command(["uv", "sync"])
    if not success:
        return False

    # Ensure notebook execution dependencies are available.
    success, _ = run_command([
        "uv", "add", "--dev", "nbconvert", "ipykernel"
    ])
    return success


def setup_pip():
    """Create a virtual environment and install requirements."""
    requirements = ROOT_DIR / "requirements.txt"

    if not requirements.exists():
        print("❌ Fichier requirements.txt introuvable.")
        return False

    venv_python = get_venv_python()

    if not venv_python.exists():
        print("🐍 Création de l'environnement virtuel .venv...")

        success, _ = run_command([
            sys.executable, "-m", "venv", ".venv"
        ])

        if not success:
            return False

    print("📦 Mise à jour de pip...")
    success, _ = run_command([
        str(venv_python), "-m", "pip", "install", "--upgrade", "pip"
    ])

    if not success:
        return False

    print("📦 Installation des dépendances...")
    success, _ = run_command([
        str(venv_python), "-m", "pip",
        "install", "-r", "requirements.txt"
    ])

    if not success:
        return False

    print("📦 Installation de Jupyter et ipykernel...")
    success, _ = run_command([
        str(venv_python), "-m", "pip",
        "install", "nbconvert", "ipykernel"
    ])

    return success


def run_pipeline(manager):
    """Execute all notebooks with the selected environment."""

    print("\n" + "=" * 55)
    print("   EXECUTION DU PIPELINE DE DONNEES")
    print("=" * 55)

    if manager == "uv":
        python_cmd = ["uv", "run", "python"]
        jupyter_cmd = ["uv", "run", "jupyter", "nbconvert"]

    elif manager == "pip":
        python_exe = str(get_venv_python())

        if not Path(python_exe).exists():
            print("❌ L'environnement .venv est introuvable.")
            return False

        python_cmd = [python_exe]
        jupyter_cmd = [python_exe, "-m", "jupyter", "nbconvert"]

    else:
        python_cmd = [sys.executable]
        jupyter_cmd = [
            sys.executable, "-m", "jupyter", "nbconvert"
        ]

    success, output = run_command(
        python_cmd + ["-m", "jupyter", "--version"]
    )

    if not success:
        print("❌ Jupyter n'est pas disponible dans cet environnement.")
        return False

    executed = 0

    for notebook in NOTEBOOKS:
        notebook_path = ROOT_DIR / notebook

        if not notebook_path.is_file():
            print(f"⚠️ Notebook introuvable : {notebook}")
            continue

        print(f"\n📓 Exécution de {notebook}...")

        command = jupyter_cmd + [
            "--to", "notebook",
            "--execute",
            "--inplace",
            "--ExecutePreprocessor.timeout=600",
            notebook,
        ]

        success, output = run_command(command)

        if not success:
            print(f"❌ Échec de l'exécution : {notebook}")
            return False

        print(f"✅ {notebook} exécuté avec succès.")
        executed += 1

    if executed == 0:
        print("\n❌ Aucun notebook n'a été exécuté.")
        return False

    print(f"\n🎉 Pipeline terminé : {executed} notebook(s) exécuté(s).")
    return True


def main():
    print("=" * 55)
    print("   PIPELINE D'ANALYSE DE DONNEES")
    print("=" * 55)
    print("1. uv (recommandé)")
    print("2. pip (environnement .venv)")
    print("3. Environnement Python actuel")
    print("=" * 55)

    choice = input("Votre choix (1/2/3) : ").strip()

    if choice == "1":
        manager = "uv"
        if not setup_uv():
            sys.exit(1)

    elif choice == "2":
        manager = "pip"
        if not setup_pip():
            sys.exit(1)

    elif choice == "3":
        manager = "current"
        print("Utilisation de l'environnement Python actuel.")

        success, _ = run_command([
            sys.executable, "-m", "pip", "--version"
        ])

        if not success:
            print("⚠️ Vérifie que pip est disponible si des installations sont nécessaires.")

        # Do not install anything in the current environment.
    else:
        print("❌ Choix invalide.")
        sys.exit(1)

    if run_pipeline(manager):
        print("\n✅ TOUT EST TERMINÉ AVEC SUCCÈS !")
    else:
        print("\n❌ Le pipeline a échoué.")
        sys.exit(1)


if __name__ == "__main__":
    main()