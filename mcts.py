import random
import math
from reguli import Joc 

class Nod:
    def __init__(self, stare, parinte=None, mutare=None, zar=None):
        # Inițializează un nod al arborelui MCTS
        self.stare = stare  # Starea jocului asociată acestui nod
        self.parinte = parinte  # Nodul părinte
        self.mutare = mutare  # Mutarea care a dus la acest nod
        self.copil = []  # Lista de copii ai nodului
        self.mutareNetestata = stare.getMutariLegale(zar) if stare else []  # Mutările încă neexplorate
        self.vizite = 0  # Numărul de vizite ale acestui nod
        self.wins = 0  # Numărul de câștiguri asociate acestui nod
        self.scor = []  # Lista scorurilor pentru acest nod

    def expandatMaxim(self):
        # Verifică dacă nodul a fost complet expandat (toate mutările posibile au fost explorate)
        return len(self.mutareNetestata) == 0

    def celMaiBunCopil(self, weight=0.5):
        # Diversificare: Adaugă un termen de explorare pentru a favoriza și nodurile mai puțin vizitate
        return max(
            self.copil,
            key=lambda child: child.scorMediu() + weight * math.sqrt(math.log(self.vizite + 1) / (child.vizite + 1))
        )

    def expandare(self, zar):
        # Expandează un nod selectând o mutare neexplorată
        if zar is None:
            raise ValueError("Zarul nu poate fii None")

        # Selectăm o mutare neexplorată
        mutare = self.mutareNetestata.pop()
        while mutare not in self.stare.getMutariLegale(zar):
            if not self.mutareNetestata:
                return None  # Dacă nu mai sunt mutări valide, întoarcem None
            mutare = self.mutareNetestata.pop()

        # Aplicăm mutarea pentru a crea o nouă stare
        start, end = mutare
        nextStare = self.stare.clone()
        nextStare.aplicaMutare(start, end)
        
        # Cream un nou nod copil cu starea rezultată
        nodCopil = Nod(nextStare, parinte=self, mutare=mutare, zar=zar)
        nodCopil.scor.append(evaluareStare(nextStare))  # Adăugăm scorul euristic pentru noul nod
        self.copil.append(nodCopil)
        return nodCopil

    def update(self, result):
        # Actualizează statistici ale nodului pe baza rezultatului simulării
        self.vizite += 1  # Incrementăm numărul de vizite
        self.scor.append(result)  # Adăugăm scorul simulării

    def scorMediu(self):
        # Calculează scorul mediu al nodului
        return sum(self.scor) / len(self.scor) if self.scor else 0

def evaluareStare(stare):
    """
    Evaluează starea curentă folosind reguli euristice și afișează contribuțiile la scor.
    """
    scorNod = 0

    for pozitie in range(24):
        # Blocarea unei zone între pozițiile 17 și 23
        if 17 <= pozitie <= 23 and stare.tabla[pozitie] * stare.playerCurent > 1:
            scorNod += 7  # Creștem importanța blocării zonelor

        # Scoaterea unei piese a adversarului
        if stare.tabla[pozitie] * stare.playerCurent == -1:
            scorNod += 6

        # Avansarea pieselor pentru jucătorul curent în zonele strategice
        if stare.playerCurent == -1 and 0 <= pozitie <= 6:
            scorNod += abs(stare.tabla[pozitie]) * 1.5
        elif stare.playerCurent == 1 and 18 <= pozitie <= 23:
            scorNod += abs(stare.tabla[pozitie]) * 1.5

        # Reducerea riscurilor prin păstrarea pieselor în siguranță (mai mult de 1 piesă pe poziție)
        if stare.tabla[pozitie] * stare.playerCurent > 1:
            scorNod += 3

        # Penalizare pentru piesele rămase singure pe tablă
        if stare.tabla[pozitie] * stare.playerCurent == 1:
            scorNod -= 4

        # Penalizare suplimentară pentru piesele care pot fi luate de adversar
        if stare.tabla[pozitie] * stare.playerCurent == 1 and stare.tabla[pozitie] * -stare.playerCurent == -1:
            scorNod -= 6

    # Bonus pentru scoaterea pieselor proprii
    pieseScoase = stare.scoase[stare.playerToIndex(stare.playerCurent)]
    scorNod += 12 * pieseScoase  # Creștem bonusul pentru piesele scoase

    return scorNod

def simulareNMutari(stare, zar, nrMutari):
    """
    Simulează următoarele n mutări sau până la sfârșitul jocului.
    Returnează media scorurilor calculate în timpul simulării.
    """
    scorTotal = 0
    mutariSimulate = 0
    while mutariSimulate < nrMutari and not stare.verificareFinal():
        mutariLegale = stare.getMutariLegale(zar)
        if not mutariLegale:
            # Dacă nu există mutări legale, terminăm tura și ne întoarcem la părinte
            zar = stare.invarteZar()
            stare.playerCurent *= -1
            continue

        mutare = random.choice(mutariLegale)
        stare.aplicaMutare(*mutare)
        zar = stare.invarteZar()
        stare.playerCurent *= -1
        mutariSimulate += 1

        # Calculăm scorul la fiecare pas
        scorTotal += evaluareStare(stare)

    # Returnăm media scorurilor
    return scorTotal / mutariSimulate if mutariSimulate > 0 else evaluareStare(stare)

def mcts(stareInitiala, zar, simulari, nrMutari=50):
    # Implementarea algoritmului Monte Carlo Tree Search
    radacina = Nod(stareInitiala, zar=zar)  # Creăm nodul rădăcină

    # Alocăm simulările pe baza scorurilor mutărilor
    while radacina.mutareNetestata:
        radacina.expandare(zar)  # Expandează toate mutările posibile

    scorTotal = sum(child.scorMediu() for child in radacina.copil)
    if scorTotal > 0:
        alocare = [int(simulari * (child.scorMediu() / scorTotal)) for child in radacina.copil]
    else:
        alocare = [simulari // len(radacina.copil) for _ in radacina.copil]

    for copil, alloc in zip(radacina.copil, alocare):
        for _ in range(alloc):
            nod = copil
            stare = nod.stare.clone()

            # Pasul 1: Selecție
            while not nod.mutareNetestata and nod.copil:
                nod = nod.celMaiBunCopil(weight=0.1)
                mutariLegale = stare.getMutariLegale(zar)
                if not mutariLegale:
                    break
                mutare = random.choice(mutariLegale)
                stare.aplicaMutare(*mutare)

            # Pasul 2: Expansiune
            if not stare.verificareFinal() and nod.mutareNetestata:
                nod = nod.expandare(zar)

            # Pasul 3: Evaluare euristică sau simulare pe mai multe mutări
            result = simulareNMutari(stare, zar, nrMutari)

            # Pasul 4: Backpropagation
            while nod is not None:
                nod.update(result)
                nod = nod.parinte

    # Generăm statistici pentru mutările posibile
    detaliMutare = []
    mutariLegale = stareInitiala.getMutariLegale(zar)
    for i, copil in enumerate(radacina.copil):  # Adăugăm enumerate pentru indexare
        detaliMutare.append({
            'mutare': copil.mutare,
            'vizite': copil.vizite,
            'scorMediu': copil.scorMediu(),
            'index': i  # Indexul copilului în lista root.copil
        })
    
    if not detaliMutare:
        return None, 0

    # Sortăm mutările după scorul mediu și vizite pentru afișare
    detaliMutare.sort(key=lambda x: (x['scorMediu'], x['vizite']), reverse=True)

    # Afișăm statisticile pentru utilizator
    print("\nStatistici mutări posibile:")
    for stat in detaliMutare:
        print(f"Mutare: {stat['mutare']}, Vizite: {stat['vizite']}, Scor mediu: {stat['scorMediu']:.2f}")

    # Returnăm cea mai bună mutare și numărul de vizite
    ceaMaiBunaMiscare = detaliMutare[0]['mutare']
    nrViziteCeaMaiBunaMiscare = detaliMutare[0]['vizite']
    print(f"Mutarea selectată: {ceaMaiBunaMiscare} (Vizite: {nrViziteCeaMaiBunaMiscare}, Scor mediu: {detaliMutare[0]['scorMediu']:.2f})")
    return ceaMaiBunaMiscare, nrViziteCeaMaiBunaMiscare
