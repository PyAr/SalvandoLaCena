Para leer valores se puede usar el siguiente método:
====================================================


mkfifo /tmp/lector

start_reader_service.sh (start_reader monitorea wheel_reader.sh y lo vuelve a levantar cuando cae. wheel reader, llama al comando test_read.py y lo redirige al fifo /tmp/lector)

Luego hacer cat /tmp/lector o el equivalente en el código python

