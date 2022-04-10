# Parte de electrónica relacionada al juego

- `client.py`: un demo de como "leer" los datos del volante, se ejecuta separado y sirve para probar que todo esté bien armado y corriendo; también tiene anotaciones sobre la no-linearidad de los valores que se reciben

- `main.py`: el código en micropython para poner adentro del microcontrolador

    - configura el ADC (conversor analógico digital) y un pin para usar el led

    - levanta el wifi en modo AP

    - hace titilar el led para indicar que está listo

    - levanta un socket y se pone a esperar una conexión

    - una vez conectado, cada vez que recibe un byte lee el ADC y contesta el valor

- `foto1.jpeg` y `foto2.jpeg`: fotos del circuito conectado

- `conexiones.jpeg`: un esquemático a mano de cómo son las conexiones
