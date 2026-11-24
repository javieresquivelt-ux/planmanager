DJANGO
Relación de proyectos propuestos a desarrollar

Este documento detalla 11 propuestas de proyectos concebidos para estudiantes que
han superado el módulo de Django en el programa de máster de desarrollo full stack.

Cada una de estas propuestas está meticulosamente diseñada para proporcionar una
experiencia de aprendizaje profunda y práctica. Se especifican claramente el objetivo
primordial del proyecto, los modelos de datos recomendados para la implementación,
las funcionalidades esenciales que deben ser incluidas obligatoriamente, y desafíos
opcionales que pueden extender el alcance del proyecto para aquellos alumnos que
deseen profundizar aún más en sus habilidades.

El propósito fundamental de este documento es ofrecer una guía sólida y estructurada
que permita a los estudiantes aplicar los conocimientos adquiridos en un contexto real y
desafiante, fomentando así su crecimiento y preparación para el mundo laboral en el
ámbito del desarrollo web.

Índice

1. Gestor de Tareas Avanzado
2. Red Social de Aficiones
3. Plataforma de Publicación de Artículos
4. Gestor de Reservas
5. App de Gestión de Eventos
6. CRM Básico
7. Sistema de Inventario
8. Biblioteca Digital
9. Aplicación Multilingüe de Recetas
10. Gestor de Proyectos con Roles
11. Tienda Online Minimalista

2
3
4
5
6
7
8
9
10
11
12

1. Gestor de Tareas Avanzado

Objetivo

Sistema tipo Trello, con tableros, columnas y tareas movibles. Si no lo conoces Trello es un
sistema de gestión de tareas muy utilizado.

Modelos sugeridos:

●  User
●  Board
●  TaskList
●  Task

Funcionalidades clave:

●  Registro, login, logout
●  CRUD de tareas y tableros
●  Asignación de tareas a usuarios
●  Prioridad, etiquetas, fechas límite
●  Posibilidad de mover tareas (usando Vanilla JS o React)

Extras o retos opcionales:

●  Exportación de tareas a CSV/JSON
●  Notificaciones por email

2. Red Social de Aficiones

Objetivo

Mini red social temática para compartir publicaciones e intereses.

Modelos sugeridos

●  User
●  Profile
●  Post
●  Comment
●  Like
●  Follow

Funcionalidades clave:

●  Registro, login, logout
●  Publicaciones con texto e imagen
●  Seguir y dejar de seguir
●  Muro con publicaciones de seguidos

Extras o retos opcionales:

●  Sistema de notificaciones
●  Carga asincrónica de publicaciones

3. Plataforma de Publicación de Artículos

Objetivo

Blog o revista colaborativa con roles de redacción y revisión.

Modelos sugeridos

●  User, Article, Category, Tag, Comment, Review

Funcionalidades clave

●  Publicación de artículos con revisión
●  Comentarios y sistema de tags
●  Administración editorial

Extras o retos opcionales

●  Sistema de 'Me gusta'
●  Filtros y búsqueda por autor/categoría

4. Gestor de Reservas

Objetivo

Sistema para reservar recursos como pistas deportivas o salas.

Modelos sugeridos

●  Resource
●  Booking
●  Availability
●  User

Funcionalidades clave

●  Calendario de disponibilidad
●  Evitar solapamiento de reservas
●  Reservas recurrentes

Extras o retos opcionales

●  Notificaciones de reserva/cancelación
●  Panel de gestión para admins

5. App de Gestión de Eventos

Objetivo

Aplicación para la organización y registro de eventos.

Modelos sugeridos

●  Event
●  User
●  Registration
●  Category

Funcionalidades clave

●  Crear y apuntarse a eventos
●  Aforo limitado
●  Visualización por calendario

Extras o retos opcionales

●  Exportación de asistentes
●  Confirmación por correo

6. CRM Básico

Objetivo

Sistema de gestión de clientes para uso comercial.

Modelos sugeridos

Interaction

●  Client
●
●  User
●  Company

Funcionalidades clave

●  CRUD de clientes e interacciones
●  Relación entre comerciales y clientes
●  Buscador por nombre, email o empresa

Extras o retos opcionales

●  Visualización de estadísticas
●  Exportación a Excel o CSV

7. Sistema de Inventario

Objetivo

Aplicación para controlar stock y movimientos de productos.

Modelos sugeridos

●  Product
●  Supplier
●  StockMovement
●  Category

Funcionalidades clave:

●  Registro de entradas/salidas
●  Alerta de stock mínimo
●  Filtro por proveedor o categoría

Extras o retos opcionales:

Importación masiva por CSV

●
●  Gráficos de movimientos

8. Biblioteca Digital

Objetivo

Gestión de préstamos y devoluciones de libros.

Modelos sugeridos:

●  Book
●  Author
●  Loan
●  User

Funcionalidades clave:

●  Préstamo y devolución de libros
●  Historial de préstamos por usuario
●  Valoraciones o reseñas

Extras o retos opcionales:

●  Carga de portadas de libros
●  Buscador avanzado

9. Aplicación Multilingüe de Recetas

Objetivo

Recetario colaborativo con traducción de contenido.

Modelos sugeridos

Ingredient

●  Recipe
●
●  User
●  Category

Funcionalidades clave:

●  Crear, editar y buscar recetas
●  Valoraciones
●  Traducción de recetas e ingredientes

Extras o retos opcionales:

●  Subida de fotos
●  Filtro por dificultad, tiempo o tipo

10. Gestor de Proyectos con Roles

Objetivo

Aplicación para colaborar en proyectos con roles definidos.

Modelos sugeridos

●  Project
●  Task
●  User
●  Role
●  Assignment

Funcionalidades clave:

●  Crear proyectos con tareas asignadas
●  Roles con permisos distintos
●  Vista general del estado del proyecto

Extras o retos opcionales:

●  Gráfico de avance por proyecto
●  Sistema de mensajería interna

11. Tienda Online Minimalista

Objetivo

E-commerce básico sin pasarela de pago real.

Modelos sugeridos

●  Product
●  Order
●  OrderItem
●  User
●  Category

Funcionalidades clave:

●  Listado y detalle de productos
●  Añadir al carrito y crear pedido
●  Panel para gestionar pedidos

Extras o retos opcionales:

●  Carga de imágenes
●  Pasarela de pago simulada


