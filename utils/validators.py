def validar_rut(rut):
    try:
        rut = rut.replace(".", "").replace("-", "").upper()
        cuerpo = rut[:-1]
        dv = rut[-1]
        
        reverso = map(int, reversed(str(cuerpo)))
        factors = [2, 3, 4, 5, 6, 7]
        s = sum(d * f for d, f in zip(reverso, factors * 10)) # Cycle factors
        res = (-s) % 11
        
        if res == 10: dv_calc = "K"
        elif res == 11: dv_calc = "0"
        else: dv_calc = str(res)
        
        return dv == dv_calc
    except:
        return False