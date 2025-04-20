## API para llamar a los modelos de IA

Esta API permite llamar a los modelos de IA de manera sencilla y rápida. Se basa en Flask y es fácil de usar. Puedes utilizarla tanto con Ollama como con GitHub Models.

### Requisitos

Si no quieres instalar absolutamente nada en tu máquina local puedes abrir este repositorio como un Dev Container.

Por otro lado, necesitas tener instalado Ollama, pero te recomiendo que lo hagas en tu máquina local en lugar del dev container para tener un rendimiento aceptable. Por otro lado necesitas tener descargados los siguientes modelos:

```bash
ollama pull llama3.2
ollama pull gpt-4-llama2
ollama pull gpt-4-llama2-13b
```




Instalar las dependecias:

```bash
cd text_generation/api
pip install -r requirements.txt
```

Ejecutar el servidor web en modo desarrollo:

```bash
FLASK_DEBUG=1 flask run --host=0.0.0.0 --port=5000
```