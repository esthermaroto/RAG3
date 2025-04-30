## API para llamar a los modelos de IA

Esta API permite llamar a los modelos de IA de manera sencilla y rápida. Se basa en Flask y es fácil de usar. Puedes utilizarla tanto con Ollama como con GitHub Models.

### Requisitos

Si no quieres instalar absolutamente nada en tu máquina local puedes abrir este repositorio como un Dev Container.

Por otro lado, necesitas tener instalado Ollama, pero te recomiendo que lo hagas en tu máquina local en lugar del dev container para tener un rendimiento aceptable. Por otro lado necesitas tener descargados los siguientes modelos:

```bash
ollama pull mistral
ollama pull phi4-mini
ollama pull gemma3
ollama pull llama3.2
```

Instalar las dependecias:

```bash
cd prompt-engineering/api
pip install -r requirements.txt
```

Ejecutar el servidor web en modo desarrollo:

```bash
FLASK_DEBUG=1 flask run --host=0.0.0.0 --port=5000
```

Con esto te aseguras de que el servidor se reinicie cada vez que hagas un cambio en el código. 