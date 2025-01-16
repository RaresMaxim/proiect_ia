from reguli import Joc
from mcts import mcts


def main():
    stare = Joc()
    simulari = None

    # Selectăm numărul de simulări la începutul jocului
    while simulari is None:
        try:
            simulari = int(input("Introduceți numărul de simulări pentru Monte Carlo: "))
            if simulari <= 0:
                print("Te rog să introduci un număr pozitiv.")
                simulari = None
        except ValueError:
            print("Te rog să introduci un număr valid.")

    while not stare.verificareFinal():
        print("\n--- Tabla curentă ---")
        stare.afisareJoc()

        if stare.playerCurent == 1:  # Jucătorul uman
            zar = stare.invarteZar()
            while zar:
                print(f"Este randul tau. Zaruri: {zar}")
                mutari = stare.getMutariLegale(zar)

                if not mutari:
                    print("Nu ai mutari posibile. Tura pierduta.")
                    break

                print("Mutari legale:")
                for i, mutare in enumerate(mutari):
                    print(f"{i + 1}: {mutare}")

                alegere = None
                while alegere is None:
                    try:
                        alegere = int(input("Alege mutarea: ")) - 1
                        if alegere < 0 or alegere >= len(mutari):
                            print("Alegere invalida. Incearca din nou.")
                            alegere = None
                    except ValueError:
                        print("Te rog să introduci un numar valid.")

                # Aplicăm mutarea aleasă
                start, end = mutari[alegere]
                stare.aplicaMutare(start, end)

                if end == 24:  # Scoaterea piesei din joc
                    print(f"Piesa de pe pozitia {start} a fost scoasa.")
                else:  # Mutare obișnuită
                    print(f"Piesa mutata de la {start} la {end}.")

                # Determinăm zarul folosit
                if start == -1:  # Mutare de pe bară
                    zarUtilizat = 24 - end if stare.playerCurent == 1 else end + 1
                elif end == 24:  # Scoaterea piesei din joc
                   # Calculăm zarul utilizat normal
                    zarUtilizat = (start - 1) if stare.playerCurent == 1 else (24 - start)
                    
                    # Dacă zarul calculat nu există, verificăm condiția pentru zaruri mai mari
                    if zarUtilizat not in zar:
                        # Găsim cel mai mic zar mai mare decât poziția piesei
                        zarUtilizat = next((die for die in zar if die > zarUtilizat), None)
                else:  # Mutare normală
                    zarUtilizat = abs(end - start)

                if zarUtilizat in zar:
                    zar.remove(zarUtilizat)
                else:
                    print(f"Eroare: Zarul calculat ({zarUtilizat}) nu exista în lista zarurilor: {zar}")

        else:  # Monte Carlo Tree Search AI
            zar = stare.invarteZar()
            while zar:
                print(f"Monte Carlo Tree Search calculează mutarea  Zaruri: {zar}")
                miscareBuna, _ = mcts(stare.clone(), zar, simulari)

                if miscareBuna:
                    start, end = miscareBuna
                    stare.aplicaMutare(start, end)

                    if end == 24:  # Scoaterea piesei din joc
                        print(f"Monte Carlo Tree Search a scos piesa de pe poziția {start}.")
                    else:
                        print(f"Monte Carlo Tree Search a mutat piesa de la {start} la {end}.")

                    # Determinăm zarul folosit
                    if start == -1:  # Mutare de pe bară
                        zarUtilizat = 24 - end if stare.playerCurent == 1 else end + 1
                    elif end == 24:  # Scoaterea piesei din joc
                        # Calculăm zarul utilizat normal
                        zarUtilizat = (start - 1) if stare.playerCurent == 1 else (24 - start)
                        
                        # Dacă zarul calculat nu există, verificăm condiția pentru zaruri mai mari
                        if zarUtilizat not in zar:
                             # Găsim cel mai mic zar mai mare decât poziția piesei
                            possible_die = next((die for die in sorted(zar) if die > zarUtilizat), None)
    
                            # Dacă nu există un zar mai mare, folosim cel mai mare zar disponibil
                            zarUtilizat = possible_die if possible_die is not None else max(zar)
                        
                        # Dacă încă nu există un zar valid, aruncăm o eroare pentru debugging
                        if zarUtilizat is None:
                            raise ValueError(f"Nu există un zar valid pentru poziția {start}. Zaruri disponibile: {stare.dice}")
                    else:  # Mutare normală
                        zarUtilizat = abs(end - start)

                    if zarUtilizat in zar:
                        zar.remove(zarUtilizat)
                    else:
                        print(f"Eroare: Zarul calculat ({zarUtilizat}) nu există în lista zarurilor: {zar}")
                else:
                    print("Monte Carlo Tree Search nu are mutări posibile. Tura pierdută.")
                    break

        stare.playerCurent *= -1

    print("\nJocul s-a terminat!")
    winner = stare.getCastigator()
    if winner == 1:
        print("Felicitări! Ai câștigat.")
    else:
        print("Monte Carlo AI a câștigat.")


if __name__ == "__main__":
    main()
