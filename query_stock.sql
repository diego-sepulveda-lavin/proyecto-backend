SELECT * FROM (
SELECT p.id, p.sku, p.descripcion, SUM(e_inv.cantidad) as cantidad
FROM productos as p
LEFT JOIN entradas_inventario as e_inv
ON p.id = e_inv.producto_id
group by p.id, p.sku, p.descripcion

UNION

SELECT p.id, p.sku, p.descripcion, SUM(s_inv.cantidad) as cantidad
FROM productos as p
LEFT JOIN salidas_inventario as s_inv
ON p.id = s_inv.producto_id
group by p.id, p.sku, p.descripcion
) as a order by a.id
