# Registro iniziale
registro = 0b00011001  # Esempio: 0xAC in binario

# Definisci lsb e msb
lsb = 5  # Bit meno significativo
msb = 7  # Bit più significativo

# Calcolo del numero di iterazioni
n_iterazioni = msb - lsb + 1

# Creazione della maschera per l'intervallo tra lsb e msb
maschera = 0
for i in range(lsb, msb + 1):
    maschera |= (1 << i)  # Imposta i bit tra lsb e msb a 1

# Mantieni i bit esterni all'intervallo (li salviamo per reinserirli dopo)
bit_esterni = registro & ~maschera

# Ciclo per incrementare i bit interni
for incremento in range(1 << n_iterazioni):  # Ciclo da 0 a 2^(msb-lsb+1) - 1
    # Operazione sui bit interni (incremento)
    bit_interni = (incremento << lsb) & maschera  # Applica l'incremento e limitalo alla maschera
    print(bin(bit_interni))
    
    # Combina i bit esterni con quelli interni modificati
    registro_modificato = bit_esterni | bit_interni
    print(bin(registro_modificato))
    # Stampa i risultati per ogni iterazione
    print(f"Iterazione {incremento}: Registro modificato = {registro_modificato:#04x}")

