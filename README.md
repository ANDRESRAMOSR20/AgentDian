# AgentDian

La aplicación consiste en un `ChatBot` implementadoun asistente 
virtual que ayude a respondes preguntas y ser de guía en el 
proceso de facturación de la DIAN en base a documentos ya quemados
y que el usuario puede agregar para que el asistente tenga más
conocimientos.


## Instrucciones de instalación:

> **Nota:** Asegúrate de tener la versión de Python 3.12.

Clona este repositorio con 

```bash 
git clone https://github.com/ANDRESRAMOSR20/AgentDian.git
```

Va a la carpeta del proyecto con:
```bash
cd AgentDian
```

Crea un entorno virtual con:

```bash
python -m venv  ./
```

Descarga las dependencias necesarios:

```bash
pip install -r requirements.txt
```

Se requiere de un modelo en local usando Ollama, en caso de no 
tenerlo descargalo [aqu](https://ollama.com/). Y usa el modelo
con:

```bash
ollama pull hf.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF:IQ4_NL
```

Para comprobar que el modelo esta funcionando ve al siguiente archivo:


![alt text](img/image.png)

Haz click en el boton:
![alt text](img/image1.png)

Deberia dar una respuesta como lo siguiente:

![alt text](img/image2.png)

> **Nota:** En caso de errores ve al siguiente apartado para instalación de dependencias. 

Y ejecuta la aplicación con:

```bash
streamlit run app.py
```

----
----

## Dependencias y librerias usadas

Las librerias usadas para el proyecto que se 
encuentran en el archivo **requirements.txt** son:
   * streamlit
   * PyPDF2
   * python-docx
   * langchain (0.3.17)
   *  langchain-chroma (0.2.1)
   * langchain-community (0.3.16)
   * langchain-core (0.3.33)
   * langchain-huggingface (0.1.2)
   * langchain-ollama (0.2.3)
   * langchain-text-splitters (0.3.5)
   * langgraph (0.2.69)
   * langgraph-checkpoint (2.0.10)
   * langgraph-sdk (0.1.51)
   * langsmith (0.3.4)
   * pdfplumber
 * 
Se requiere tener dependencias como `Cmake`, `gcc`,`CUDA`  y `c++`. En caso de no tenerlas puedes instarlas con:


### WIndows
Instala desde las páginas principales de [Cmake](https://cmake.org/download/), [gcc](https://gcc.gnu.org/install/binaries.html), [CUDA](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/) y [C++](https://visualstudio.microsoft.com/es/vs/features/cplusplus/)

### Linux/Unix🐧


**Base Debian**:

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/sources.list.d/cuda.list
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub
sudo apt update
sudo apt install cuda cmake build-essential #incluye gcc y c++

```

**Base Fedora/RHEL**:

```bash
sudo dnf install cmake gcc-c++
```

Para instalar **CUDA** haz lo siguiente:

```bash
wget https://developer.download.nvidia.com/compute/cuda/12.8.0/local_installers/cuda_12.8.0_570.86.10_linux.run
sudo sh cuda_12.8.0_570.86.10_linux.run
```


**Base Arch Linux**:

```bash
sudo pacman -S cmake base-devel cuda #incluye gcc y c++
```

**Sistemas con gestor o repositorio de Nix como NixOs**:

```bash
nix-env -iA nixpkgs.cmake nixpkgs.gcc nixpkgs.gnumake nixpkgs.cudatoolkit
```

Desde el archivo `/etc/nixos/configuration.nix` sería:

```bash
environment.systemPackages = with pkgs; [
  gcc
  gnumake
  cmake
  cudatoolkit
];
```
---
---

## Ejecución y ejemplos de uso




----
----

## Colaboradores:

- Andres Felipe Ramos Rojas <br>
- Verónica Ruíz Bautista
- Samuel Alvarez
- Juan Pablo Montoya Valencia