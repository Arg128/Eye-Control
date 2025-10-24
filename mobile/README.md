# Eye Control Mobile

Este proyecto es una aplicación móvil de seguimiento ocular desarrollada con React Native. La aplicación está diseñada para funcionar en plataformas Android e iOS, proporcionando una interfaz intuitiva para el seguimiento ocular y la calibración.

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

- **android/**: Contiene la configuración y los archivos específicos para la versión Android de la aplicación.
  - **app/**: Contiene el código fuente de la aplicación Android.
    - **src/**: Contiene los archivos fuente de la aplicación.
      - **main/**: Contiene el manifiesto de Android y el código Java.
  - **gradle/**: Archivos relacionados con la configuración de Gradle.
  - **build.gradle**: Script de construcción de Gradle a nivel de proyecto.

- **ios/**: Contiene la configuración y los archivos específicos para la versión iOS de la aplicación.

- **src/**: Contiene los componentes, servicios, pantallas y utilidades de la aplicación.
  - **components/**: Componentes reutilizables de la interfaz de usuario.
  - **services/**: Funciones para la detección ocular y la interacción con APIs externas.
  - **screens/**: Pantallas principales de la aplicación.
  - **utils/**: Funciones de utilidad.
  - **types/**: Tipos e interfaces utilizados en la aplicación.
  - **App.tsx**: Punto de entrada de la aplicación.

- **package.json**: Configuración de npm con dependencias y scripts del proyecto.
- **tsconfig.json**: Configuración de TypeScript.
- **babel.config.js**: Configuración de Babel.
- **metro.config.js**: Configuración del empaquetador Metro.

## Instalación

Para instalar las dependencias del proyecto, ejecuta:

```
npm install
```

## Ejecución

Para ejecutar la aplicación en un emulador o dispositivo Android, utiliza:

```
npx react-native run-android
```

Para ejecutar la aplicación en un emulador o dispositivo iOS, utiliza:

```
npx react-native run-ios
```

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT.