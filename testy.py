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

entrada_inv_a_mod1 = {
    'id': 19, 
    'cantidad': 2, 
    'precio_costo_unitario': 5000, 
    'costo_total': 10000, 
    'fecha_registro': 'Tue, 28 Jul 2020 12:54:19 GMT', 
    'usuario_id': 1, 
    'factura_compra_id': 13, 
    'producto_id': 3, 
    'producto': {
        'id': 3, 
        'sku': 'yrt67', 
        'descripcion': 'Carne', 
        'codigo_barra': '6456', 
        'unidad_entrega': 'unidad', 
        'categoria_id': 1, 
        'precio_venta_unitario': 5000, 
        'margen_contribucion': 0.1
    }
}
encontrada la entrada en inv y no hacer nada 19
entrada_inv_a_mod2 = {
    'cantidad': 100, 
    'precio_costo_unitario': 100, 
    'costo_total': 10000, 
    'fecha_registro': 'Tue, 28 Jul 2020 12:54:19 GMT', 
    'usuario_id': 1, 
    'factura_compra_id': 13, 
    'producto_id': 8, 
    'producto': {
        'id': 8, 
        'sku': '65645te', 
        'descripcion': 'Chicle Menta', 
        'codigo_barra': '453453', 
        'unidad_entrega': 'unidad', 
        'categoria_id': 1, 
        'precio_venta_unitario': 300, 
        'margen_contribucion': 0.1
    }
}

encontrada la entrada en inv y no hacer nada 20

entrada_inv_a_mod3 = {
    'cantidad': '123', 
    'precio_costo_unitario': '1500', 
    'costo_total': 184500, 
    'usuario_id': 1, 
    'producto_id': '3'
}
KeyError: 'id'


venta = {
    'buscador': '', 
    'detalleProductos': [
        {
            'descripcion': 'Chocolate', 
            'cantidad': 1, 
            'precio_venta_unitario': 2000, 
            'total': 2000, 
            'producto_id': 1
        }, 
        {
            'descripcion': 'Pan', 
            'cantidad': 1, 
            'precio_venta_unitario': 1000, 
            'total': 1000, 
            'producto_id': 2
        },
        {
            'descripcion': 'Carne', 
            'cantidad': 1, 
            'precio_venta_unitario': 5000, 
            'total': 5000, 
            'producto_id': 3
        }
    ],
    'datosVenta': {
        'monto_neto': 6723, 
        'monto_iva': 1278, 
        'monto_total': 8000, 
        'monto_recibido': '10000', 
        'vuelto': 2000, 
        'tipo_documento': 'boleta', 
        'numero_documento': '1', 
        'forma_pago': 'efectivo'
    }
}