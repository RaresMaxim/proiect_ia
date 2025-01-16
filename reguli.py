import random

class Joc:
    def __init__(self):
        self.tabla = self.initializareTabla()
        self.playerCurent = 1  # 1 pentru jucătorul 1, -1 pentru jucătorul 2
        self.bara = [0, 0]  # [Piese pe bară pentru jucătorul 1, Piese pe bară pentru jucătorul -1]
        self.scoase = [0, 0]  # [Piese scoase pentru jucătorul 1, Piese scoase pentru jucătorul -1]

    def playerToIndex(self, player):
        """
        Converteste jucătorul (1 sau -1) în indexul corespunzător în lista `bar` sau `off`.
        """
        return 0 if player == 1 else 1

    def initializareTabla(self):
        """
        Initializează tabla de joc cu poziția inițială a pieselor.
        Tabla este reprezentată ca o listă de 24 de poziții, fiecare având:
        - Un număr pozitiv (piese ale jucătorului 1)
        - Un număr negativ (piese ale jucătorului 2)
        """
        return [
            -2, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0, -5,
            5, 0, 0, 0, -3, 0, -5, 0, 0, 0, 0, 2
        ]

    def invarteZar(self):
        """
        Simulează aruncarea zarurilor și returnează mutările posibile.
        În cazul zarurilor duble, se returnează de 4 ori același zar.
        """
        zar1 = random.randint(1, 6)
        zar2 = random.randint(1, 6)
        if zar1 == zar2:  # Zaruri duble
            return [zar1] * 4
        return [zar1, zar2]

    def getMutariLegale(self, zar):
        if zar is None:
            raise ValueError("Dice cannot be None in get_legal_moves.")
        mutariLegale = set()  # Folosim un set pentru a elimina mutările duplicate

        # Gestionăm mutările pentru piesele de pe bară
        if self.bara[self.playerToIndex(self.playerCurent)] > 0:
            for zr in zar:
                if self.mutareLegalaDePeBara(zr):
                    mutariLegale.add((-1, 24 - zr if self.playerCurent == 1 else zr - 1))
            return list(mutariLegale)  # Transformăm set-ul în listă

        # Gestionăm mutările pentru scoaterea pieselor din zona 'home'
        if self.suntToatePieseInBaza():
            for zr in zar:
                mutariCasa = self.mutariScoateDinCasa(zr)
                mutariLegale.update(mutariCasa)  # Adăugăm mutările în set

            if mutariLegale:
                return list(mutariLegale)  # Transformăm set-ul în listă

        # Gestionăm mutările normale de pe tablă
        for zr in zar:
            for pozitie in range(24):
                if self.esteMutareLegala(pozitie, zr):
                    pozitieFinala = pozitie - zr if self.playerCurent == 1 else pozitie + zr
                    mutariLegale.add((pozitie, pozitieFinala))

        return list(mutariLegale)  # Transformăm set-ul în listă

    def mutariScoateDinCasa(self, zar):
        """
        Returnează mutările legale pentru scoaterea pieselor din zona 'home' folosind un anumit zar.
        """
        mutariLegale = []
        zonaCasa = range(0, 6) if self.playerCurent == 1 else range(18, 24)

        # Verificăm dacă există o piesă pe poziția exactă pentru scoatere
        pozitie = zar - 1 if self.playerCurent == 1 else 24 - zar
        if pozitie in zonaCasa and self.tabla[pozitie] * self.playerCurent > 0:
            mutariLegale.append((pozitie, 24))
        else:
            # Dacă nu există piese pe poziția exactă, scoatem cea mai mare piesă posibilă
            for point in reversed(zonaCasa):
                if self.tabla[point] * self.playerCurent > 0:
                    # Permitem scoaterea piesei dacă zarul este suficient de mare
                    if zar >= (point + 1 if self.playerCurent == 1 else 24 - point):
                        mutariLegale.append((point, 24))
                    break

        return mutariLegale

    def esteMutareLegala(self, pozitieStart, zar):
        """
        Verifică dacă o mutare este legală pentru piesele de pe tablă.
        """
        pozitieFinala = pozitieStart - zar if self.playerCurent == 1 else pozitieStart + zar
        if pozitieFinala < 0 or pozitieFinala >= 24:
            return False
        if self.tabla[pozitieStart] * self.playerCurent <= 0:
            return False
        if self.tabla[pozitieFinala] * self.playerCurent < -1:
            return False
        return True

    def aplicaMutare(self, pozitieStart, pozitieFinala):
        if pozitieStart == -1:  # Gestionăm mutările din bară
            if self.tabla[pozitieFinala] * self.playerCurent == -1:
                self.bara[self.playerToIndex(-self.playerCurent)] += 1
                self.tabla[pozitieFinala] = 0
            self.tabla[pozitieFinala] += self.playerCurent
            self.bara[self.playerToIndex(self.playerCurent)] -= 1
        elif pozitieFinala == 24:  # Scoatem piesa din joc
            self.tabla[pozitieStart] -= self.playerCurent
            self.scoase[self.playerToIndex(self.playerCurent)] += 1
        else:  # Mutare normală
            if self.tabla[pozitieFinala] * self.playerCurent == -1:
                self.bara[self.playerToIndex(-self.playerCurent)] += 1
                self.tabla[pozitieFinala] = 0
            self.tabla[pozitieStart] -= self.playerCurent
            self.tabla[pozitieFinala] += self.playerCurent
        return self

    def verificareFinal(self):
        """
        Verifică dacă jocul s-a terminat (toate piesele unui jucător au fost scoase).
        """
        return self.scoase[0] == 15 or self.scoase[1] == 15

    def getCastigator(self):
        """
        Returnează câștigătorul (1 sau -1) sau None dacă jocul nu s-a terminat.
        """
        if self.scoase[0] == 15:
            return 1
        elif self.scoase[1] == 15:
            return -1
        return None

    def suntToatePieseInBaza(self):
        """
        Verifică dacă toate piesele jucătorului curent sunt în zona 'home' sau scoase.
        """
        zonaCasa = range(0, 6) if self.playerCurent == 1 else range(18, 24)
        #if(self.current_player == 1):
        nrPieseTotale = abs(sum(self.tabla[i] for i in zonaCasa if self.tabla[i] * self.playerCurent > 0))
        #else:
            #total_pieces = sum(self.board[i] for i in home_range if self.board[i] > 0)
        nrPieseTotale += self.scoase[self.playerToIndex(self.playerCurent)]
        # Verificăm dacă toate cele 15 piese sunt fie în zona 'home', fie scoase
        return abs(nrPieseTotale) == 15

    def clone(self):
        """
        Creează o clonă a stării curente.
        """
        stareClonata = Joc()
        stareClonata.tabla = self.tabla[:]
        stareClonata.playerCurent = self.playerCurent
        stareClonata.bara = self.bara[:]
        stareClonata.scoase = self.scoase[:]
        return stareClonata

    def mutareLegalaDePeBara(self, zar):

        """
        Verifică dacă o piesă a jucătorului curent poate intra de pe bară folosind zarul dat.
        """
        # Determinăm poziția de intrare
        pozitieDeIntrat = 24 - zar if self.playerCurent == 1 else zar - 1
        return self.tabla[pozitieDeIntrat] * self.playerCurent >= -1
    
    def afisareJoc(self):
        """
        Afișează tabla în format text-based.
        """
        print(f"\n--- Tabla de joc --- (Jucătorul curent: {'1 (alb)' if self.playerCurent == 1 else '-1 (negru)'})")

        # Afișăm rândul de sus (punctele 12-23)
        print("Rând sus: ", end="")
        for i in range(12, 24):
            pieseNumarate = self.tabla[i]
            simbol = f"{pieseNumarate:+}" if pieseNumarate != 0 else " 0"
            print(f"{i:2}:{simbol:3} ", end="")
        print("\n" + "-" * 70)

        # Afișăm rândul de jos (punctele 0-11)
        print("Rând jos: ", end="")
        for i in range(11, -1, -1):
            pieseNumarate = self.tabla[i]
            simbol = f"{pieseNumarate:+}" if pieseNumarate != 0 else " 0"
            print(f"{i:2}:{simbol:3} ", end="")

        print("\nBară:", {1: self.bara[0], -1: self.bara[1]})
        print("Scoase:", {1: self.scoase[0], -1: self.scoase[1]})
