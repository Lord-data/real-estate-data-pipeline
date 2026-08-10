## Poner primer letra en mayuscula y organizar en alfabeticamente

nombres = ["ana", "PEDRO", "juAn", "sofia"]
cap_list = sorted([i.capitalize() for i in nombres])
print(cap_list)


## Conteo de palabras:

data = ["data", "python", "data", "sql", "python", "python"]
frecuencia = {}

for palabra in data:
    if palabra not in frecuencia:
        frecuencia[palabra] = 1 
    else: 
        frecuencia[palabra] = frecuencia.get(palabra) +1
    
print(frecuencia)    

## Multiplicar valores pares x3:

numbers = list(range(1,21))
event_numbers = [i*3 for i in numbers if i % 2 == 0] 
print(event_numbers) 
      
### Cambio de clave y valor de diccionario:

grades = {"Ana": 4.5, "Luis": 3.8, "Sofía": 4.2, "Ramiro": 4.2}

new_grades ={}

for i,y in grades.items():
    if y not in new_grades:
         new_grades[y] = [i]
    else:
        new_grades[y].append(i)
print(new_grades)

### Distancia con respecto al origen (0,0)

import math

coords = [(1, 2), (3, 4), (5, 6)]
op = [math.sqrt((x)**2 + (y)**2) for x,y in coords]
print(op)

### Clasificar en una lista nueva, categorias: Baja(20 <), media(20-29) y alta (30 >)

temps = [12, 25, 30, 18, 33, 27]
temps2 = ["Baja" if i < 20  else "Alto" if i >= 30 else "Medio" for i in temps]
print(temps2)

## Crear lista nueva si la temperatura es mayor a 60 farein

temps = [("Bogotá", 18), ("Miami", 86), ("Madrid", 77)]

def celcius_temp (temp, umbral = 60):
    celcius = [(x,(y-32)* 5/9) if y > umbral else (x,y) for x,y in temp]
    return celcius
print(celcius_temp(temps)) 

### Frequencia
ventas = ["pan", "pan", "queso", "leche", "pan", "leche"]
      ## on(1) alta eficiencia
def conteo_alimento(unidad):
    frecuencia = {}
    for i in unidad:
        if i not in frecuencia:
            frecuencia[i] = 1
        else:
            frecuencia[i] += 1
    return frecuencia


        ## on(2) poco eficiente con muchos datos 
def conteo_alimento (unidad): 
    frecuencia = { i:unidad.count(i) for i in unidad} 
    return frecuencia 
    
print(conteo_alimento(ventas))

## Filtrado de datos anidados (list comprehension avanzada)

usuarios = [
    {"nombre": "Ana", "edad": 23, "activo": True},
    {"nombre": "Luis", "edad": 31, "activo": False},
    {"nombre": "Sofía", "edad": 19, "activo": True}
]

def usuarios1(usu):
    new = [u["nombre"] for u in usu if u["edad"] > 20 and u["activo"]]
    return new
print(usuarios1(usuarios))

## Ventas por tienda y producto

ventas = [
    {"tienda": "A", "productos": [("pan", 10), ("leche", 5)]},
    {"tienda": "B", "productos": [("pan", 7), ("queso", 4), ("leche", 2)]},
    {"tienda": "C", "productos": [("pan", 5)]}
]

new = [(i["tienda"],sum(y for x,y in i["productos"])) for i in ventas]

print(new)

## ventas mayores a 12

ventas = [
    {"tienda": "A", "productos": [("pan", 10), ("leche", 5)]},
    {"tienda": "B", "productos": [("pan", 7), ("queso", 4), ("leche", 2)]},
    {"tienda": "C", "productos": [("pan", 5)]}
]

new = [(i["tienda"],sum(y for x,y in i["productos"])) for i in ventas if sum(y for x,y in i["productos"]) > 12]

print(new)

## Diccionario de promedios por categoría

ventas = [
    {"categoria": "lácteos", "productos": [("leche", 5), ("queso", 8)]},
    {"categoria": "carnes", "productos": [("pollo", 10), ("res", 6)]},
    {"categoria": "frutas", "productos": [("manzana", 4), ("pera", 3), ("banano", 2)]},
    {"categoria": "lácteos", "productos": [("yogur", 6)]}
]

ventas1 = {}

for i in ventas:
    if i["categoria"] not in ventas1:
        ventas1[i["categoria"]] = i["productos"]
    else:
        ventas1[i["categoria"]].extend(i["productos"])

promedio = {i:sum(y for x,y in t)/len(t) for i,t in ventas1.items()}
print(promedio)

## Filtrar y transformar ventas por categoría

ventas = [
    {"categoria": "lácteos", "productos": [("leche", 5), ("queso", 8)]},
    {"categoria": "carnes", "productos": [("pollo", 10), ("res", 6)]},
    {"categoria": "frutas", "productos": [("manzana", 4), ("pera", 3), ("banano", 2)]},
    {"categoria": "lácteos", "productos": [("yogur", 6), ("mantequilla", 10)]}
]

ventas1 = {}

for i in ventas:
    if i["categoria"] not in ventas1:
        ventas1[i["categoria"]] = i["productos"]
    else:
        ventas1[i["categoria"]].extend(i["productos"])

promedio = {i.upper():sum(y for x,y in t) for i,t in ventas1.items() if sum(y for x,y in t) >= 20}
print(promedio)

## Ejercicio 18 — Subagrupación y filtrado interno

ventas = [
    {"categoria": "lácteos", "subcategoria": "líquidos", "productos": [("leche", 5), ("yogur", 6)]},
    {"categoria": "lácteos", "subcategoria": "sólidos", "productos": [("queso", 8), ("mantequilla", 10)]},
    {"categoria": "carnes", "subcategoria": "aves", "productos": [("pollo", 10)]},
    {"categoria": "carnes", "subcategoria": "rojas", "productos": [("res", 6), ("cerdo", 4)]},
    {"categoria": "frutas", "subcategoria": "tropicales", "productos": [("banano", 2), ("piña", 5)]}
]

my_d = {}

for i in ventas:
    cat = i["categoria"]
    sub = i["subcategoria"]
    if cat not in my_d:
        my_d[cat] = {sub:i["productos"]}
    else:
        if sub not in my_d[cat]:
            my_d[cat][sub]=i["productos"]
        else:
            my_d[cat][sub].extend(i["productos"])
        
new_d = {
    j: inner
    for j, i in my_d.items()
    if (inner := {m: total
                  for m, n in i.items()
                  if (total := sum(p for l, p in n)) >= 10})
}

print(new_d) 

### jercicio 19 total de productos por tienda

ventas = [
    {"tienda": "A", "categorias": {
        "lácteos": [("leche", 5), ("yogur", 6)],
        "frutas": [("manzana", 4)]
    }},
    {"tienda": "A", "categorias": {
        "lácteos": [("queso", 8)],
        "frutas": [("banano", 3)]
    }},
    {"tienda": "B", "categorias": {
        "carnes": [("pollo", 10)],
        "lácteos": [("leche", 4)]
    }},
]

new_d = {}

for i in ventas:
    store = i["tienda"]
    for c,v in i["categorias"].items():
        if store not in new_d:
            new_d[store] = {c:v}
        else:
            if c not in new_d[store]:
                new_d[store][c] = v
            else:
                new_d[store][c].extend(v)
                
d = {i:{l:sum(p for t,p in v) for l,v in m.items()} for i,m in new_d.items()}

print(d)

## Solución alterna
ventas = [
    {"tienda": "A", "categorias": {
        "lácteos": [("leche", 5), ("yogur", 6)],
        "frutas": [("manzana", 4)]
    }},
    {"tienda": "A", "categorias": {
        "lácteos": [("queso", 8)],
        "frutas": [("banano", 3)]
    }},
    {"tienda": "B", "categorias": {
        "carnes": [("pollo", 10)],
        "lácteos": [("leche", 4)]
    }},
]

new_d = {}

for i in ventas:
    store = i["tienda"]
    for c,v in i["categorias"].items():
        new_d.setdefault(store,{}).setdefault(c,[]).extend(v)

print(new_d)
                
d = {i:{l:sum(p for _,p in v) for l,v in m.items()} for i,m in new_d.items()}       