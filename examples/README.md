##  Manual de Uso:


##  Importante:
    Para realizar el guardado del calibrado en archivos .pkl; primero deberás de configuar en el directorio de tus librerias
    los archivos: 'Calibrator_v2.py' tal como se muestra en el cuerpo del 'eyeGestures' folder; en cambio tambien puedes
    copiar y pegar dentro de la clase 'Calibrator' lo siguiente:

    ´´´
    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove unpickleable entries
        if 'lock' in state:
            del state['lock']
        if 'calcualtion_coroutine' in state:
            del state['calcualtion_coroutine']
        if 'fit_coroutines' in state:
            del state['fit_coroutines']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # Recreate the lock and other non-picklable objects
        self.lock = threading.Lock()
        self.calcualtion_coroutine = threading.Thread(target=self.__async_post_fit)
        self.fit_coroutines = []

    ´´´

    Luego de ello sigue con los siguientes pasos.
    
### 1.- Ejecuta una Calibración:
    Entra a ´´´GitHubCopilot.py´´´ para realizar una calibración siguiendo los puntos verdes; una vez acabado sal del script
    usando cambios entre la pestañas y cerrando dotos los procesos anexados.

### 2.- Probar la funcionalidad en tu PC:
    Ahora ingresa a ´´´GitHubCopiloy_Tracking.py´´´ para probar en directo el movimiento a travez del mouse