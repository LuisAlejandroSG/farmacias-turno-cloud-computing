-- Crear tabla de farmacias
CREATE TABLE IF NOT EXISTS farmacias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    telefonico VARCHAR(20),
    horario_apertura TIME,
    horario_cierre TIME,
    domingo_turno BOOLEAN DEFAULT FALSE,
    esta_activa BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para optimización
CREATE INDEX idx_ciudad ON farmacias(ciudad);
CREATE INDEX idx_domingo_turno ON farmacias(domingo_turno);
CREATE INDEX idx_activa ON farmacias(esta_activa);

-- Insertar datos de ejemplo (Coronel, Lota, Arauco)
INSERT INTO farmacias (nombre, ciudad, direccion, telefonico, horario_apertura, horario_cierre, domingo_turno, esta_activa) VALUES
-- CORONEL
('Farmacia Ahumada', 'Coronel', 'Avenida Colón 560', '412453210', '08:00:00', '21:00:00', true, true),
('Farmacias SalcoBrand', 'Coronel', 'Calle Cochrane 240', '412456789', '08:00:00', '20:30:00', false, true),
('Farmacia Cruz Azul', 'Coronel', 'Avenida Lota 120', '412454321', '09:00:00', '21:00:00', true, true),
('Farmacia Dra. Sótero del Río', 'Coronel', 'Calle Ramírez 85', '412452100', '08:30:00', '20:00:00', false, true),
('Farmacia Integral', 'Coronel', 'Pasaje Balmaceda 15', '412458765', '08:00:00', '21:30:00', true, true),

-- LOTA
('Farmacia Ahumada', 'Lota', 'Calle Isidora Goyenechea 340', '412560123', '08:00:00', '21:00:00', true, true),
('Farmacias SalcoBrand', 'Lota', 'Avenida Pedro Montt 450', '412561234', '08:00:00', '20:30:00', false, true),
('Farmacia Cruz Azul', 'Lota', 'Calle Manuel Rodríguez 200', '412562345', '09:00:00', '21:00:00', true, true),
('Farmacia San Miguel', 'Lota', 'Pasaje Industrial 50', '412563456', '08:30:00', '20:00:00', false, true),

-- ARAUCO
('Farmacia Ahumada', 'Arauco', 'Avenida Arauco 680', '412760000', '08:00:00', '21:00:00', true, true),
('Farmacias SalcoBrand', 'Arauco', 'Calle O''Higgins 290', '412761111', '08:00:00', '20:30:00', false, true),
('Farmacia Cruz Azul', 'Arauco', 'Calle Arturo Prat 125', '412762222', '09:00:00', '21:00:00', true, true),
('Farmacia Lo''s Andes', 'Arauco', 'Pasaje Comercial 35', '412763333', '08:30:00', '20:00:00', false, true);

-- Vista para consultas rápidas de farmacias en turno (domingo)
CREATE VIEW farmacias_domingo_turno AS
SELECT id, nombre, ciudad, direccion, telefonico, horario_apertura, horario_cierre
FROM farmacias
WHERE domingo_turno = true AND esta_activa = true
ORDER BY ciudad, nombre;

-- Vista para farmacias activas
CREATE VIEW farmacias_activas AS
SELECT id, nombre, ciudad, direccion, telefonico, horario_apertura, horario_cierre, domingo_turno
FROM farmacias
WHERE esta_activa = true
ORDER BY ciudad, nombre;
