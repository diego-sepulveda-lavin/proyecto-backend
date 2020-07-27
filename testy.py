data = {
    'factura': {
        'folio': '99', 
        'fecha_emision': '27-07-2020', 
        'fecha_recepcion': '27-07-2020', 
        'monto_neto': '10000', 
        'monto_iva': '1900', 
        'monto_otros_impuestos': '', 
        'monto_total': '11900', 
        'proveedor_id': '4', 
        'entradas_inventario': [
            {
                'cantidad': '1', 
                'precio_costo_unitario': '1500', 
                'costo_total': 1500, 
                'usuario_id': 1, 
                'producto_id': '1'
            }, 
            {
                
                'cantidad': '2', 
                'precio_costo_unitario': '1000', 
                'costo_total': 2000, 
                'usuario_id': 1, 
                'producto_id': '2'
            }
        ]
    }, 
    'detalleEntrada': {
        'cantidad': None, 
        'precio_costo_unitario': None, 
        'costo_total': None, 
        'usuario_id': 1, 
        'producto_id': None
    }
}
print(data['factura']['folio'])