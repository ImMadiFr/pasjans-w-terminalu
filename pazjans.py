#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import os
import sys

class Karta:
    def __init__(self, kolor, wartosc):
        self.kolor = kolor
        self.wartosc = wartosc
        self.odkryta = False
    
    def __str__(self):
        if not self.odkryta:
            return "██"
        
        kolory_symbole = {
            'pik': '♠',
            'trefl': '♣', 
            'kier': '♥',
            'karo': '♦'
        }
        
        wartosci_symbole = {
            1: 'A', 11: 'J', 12: 'Q', 13: 'K'
        }
        
        wartosc_str = wartosci_symbole.get(self.wartosc, str(self.wartosc))
        symbol = kolory_symbole[self.kolor]
        
        # Kolorowanie kart
        if self.kolor in ['kier', 'karo']:
            return f"\033[91m{wartosc_str}{symbol}\033[0m"  # Czerwony
        else:
            return f"\033[90m{wartosc_str}{symbol}\033[0m"  # Czarny
    
    def czy_czerwona(self):
        return self.kolor in ['kier', 'karo']
    
    def czy_czarna(self):
        return self.kolor in ['pik', 'trefl']

class Pasjans:
    def __init__(self):
        self.talia = self.stworz_talie()
        self.tasuj_talie()
        self.kolumny = [[] for _ in range(7)]
        self.podstawy = {'pik': [], 'trefl': [], 'kier': [], 'karo': []}
        self.stos = []
        self.odrzucone = []
        self.rozdaj_karty()
    
    def stworz_talie(self):
        kolory = ['pik', 'trefl', 'kier', 'karo']
        talia = []
        for kolor in kolory:
            for wartosc in range(1, 14):
                talia.append(Karta(kolor, wartosc))
        return talia
    
    def tasuj_talie(self):
        random.shuffle(self.talia)
    
    def rozdaj_karty(self):
        idx = 0
        # Rozdaj karty do kolumn
        for i in range(7):
            for j in range(i + 1):
                if idx < len(self.talia):
                    karta = self.talia[idx]
                    if j == i:  # Górna karta w kolumnie
                        karta.odkryta = True
                    self.kolumny[i].append(karta)
                    idx += 1
        
        # Pozostałe karty do stosu
        self.stos = self.talia[idx:]
    
    def wyswietl_plansze(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 60)
        print("                    PASJANS ")
        print("=" * 60)
        
        # Wyświetl stos i odrzucone
        stos_str = f"[{len(self.stos)}]" if self.stos else "[ ]"
        odrzucone_str = str(self.odrzucone[-1]) if self.odrzucone else "[ ]"
        print(f"\nStos: {stos_str}  Odrzucone: {odrzucone_str}")
        
        # Wyświetl podstawy
        print("\nPodstawy:")
        for kolor, karty in self.podstawy.items():
            if karty:
                print(f"{kolor.capitalize()}: {karty[-1]}", end="  ")
            else:
                print(f"{kolor.capitalize()}: [ ]", end="  ")
        print("\n")
        
        # Wyświetl kolumny
        print("Kolumny (1-7):")
        max_dlugosc = max(len(kolumna) for kolumna in self.kolumny) if any(self.kolumny) else 0
        
        for i in range(max_dlugosc):
            for j in range(7):
                if i < len(self.kolumny[j]):
                    print(f" {self.kolumny[j][i]} ", end=" ")
                else:
                    print("    ", end=" ")
            print()
        
        print("\nNumery kolumn:")
        for i in range(1, 8):
            print(f" {i}  ", end=" ")
        print()
    
    def czy_mozna_polozyc_na_kolumne(self, karta, kolumna_idx):
        kolumna = self.kolumny[kolumna_idx]
        if not kolumna:
            return karta.wartosc == 13  # Tylko król na pustą kolumnę
        
        gorna_karta = kolumna[-1]
        if not gorna_karta.odkryta:
            return False
        
        # Musi być o 1 mniej i przeciwny kolor
        return (karta.wartosc == gorna_karta.wartosc - 1 and 
                karta.czy_czerwona() != gorna_karta.czy_czerwona())
    
    def czy_mozna_polozyc_na_podstawe(self, karta):
        podstawa = self.podstawy[karta.kolor]
        if not podstawa:
            return karta.wartosc == 1  # As na pustą podstawę
        return karta.wartosc == podstawa[-1].wartosc + 1
    
    def przesun_karte(self, skad, dokad, ile=1):
        if skad == 's':  # Ze stosu
            if not self.odrzucone:
                print("Brak kart w odrzuconych!")
                return False
            karta = self.odrzucone.pop()
        elif skad.isdigit():  # Z kolumny
            kolumna_idx = int(skad) - 1
            if 0 <= kolumna_idx < 7 and self.kolumny[kolumna_idx]:
                if ile == 1:
                    karta = self.kolumny[kolumna_idx].pop()
                else:
                    # Przesuwanie wielu kart
                    if len(self.kolumny[kolumna_idx]) >= ile:
                        karty = self.kolumny[kolumna_idx][-ile:]
                        self.kolumny[kolumna_idx] = self.kolumny[kolumna_idx][:-ile]
                        return karty
                    else:
                        print("Za mało kart w kolumnie!")
                        return False
            else:
                print("Nieprawidłowa kolumna źródłowa!")
                return False
        else:
            print("Nieprawidłowe źródło!")
            return False
        
        # Sprawdź gdzie przenieść
        if dokad == 'p':  # Na podstawę
            if self.czy_mozna_polozyc_na_podstawe(karta):
                self.podstawy[karta.kolor].append(karta)
                self.odkryj_nastepna_karte(skad)
                return True
            else:
                # Cofnij
                if skad == 's':
                    self.odrzucone.append(karta)
                else:
                    self.kolumny[int(skad) - 1].append(karta)
                print("Nie można położyć tej karty na podstawę!")
                return False
        elif dokad.isdigit():  # Na kolumnę
            kolumna_idx = int(dokad) - 1
            if 0 <= kolumna_idx < 7:
                if self.czy_mozna_polozyc_na_kolumne(karta, kolumna_idx):
                    self.kolumny[kolumna_idx].append(karta)
                    self.odkryj_nastepna_karte(skad)
                    return True
                else:
                    # Cofnij
                    if skad == 's':
                        self.odrzucone.append(karta)
                    else:
                        self.kolumny[int(skad) - 1].append(karta)
                    print("Nie można położyć tej karty na tę kolumnę!")
                    return False
            else:
                print("Nieprawidłowa kolumna docelowa!")
                return False
        
        print("Nieprawidłowy cel!")
        return False
    
    def odkryj_nastepna_karte(self, skad):
        if skad.isdigit():
            kolumna_idx = int(skad) - 1
            if (0 <= kolumna_idx < 7 and 
                self.kolumny[kolumna_idx] and 
                not self.kolumny[kolumna_idx][-1].odkryta):
                self.kolumny[kolumna_idx][-1].odkryta = True
    
    def dobierz_ze_stosu(self):
        if self.stos:
            karta = self.stos.pop()
            karta.odkryta = True
            self.odrzucone.append(karta)
        elif self.odrzucone:
            # Przetasuj odrzucone z powrotem na stos
            self.stos = self.odrzucone[:]
            self.odrzucone = []
            for karta in self.stos:
                karta.odkryta = False
            print("Przetasowano karty z powrotem na stos!")
        else:
            print("Brak kart w stosie!")
    
    def czy_wygrana(self):
        return all(len(podstawa) == 13 for podstawa in self.podstawy.values())
    
    def wyswietl_pomoc(self):
        print("\n" + "="*50)
        print("INSTRUKCJA GRY:")
        print("="*50)
        print("d - dobierz kartę ze stosu")
        print("ruch SKĄD DOKĄD - przenieś kartę")
        print("  SKĄD: s (stos) lub 1-7 (kolumna)")
        print("  DOKĄD: p (podstawa) lub 1-7 (kolumna)")
        print("  Przykład: 'ruch s 3' - ze stosu do kolumny 3")
        print("  Przykład: 'ruch 1 p' - z kolumny 1 na podstawę")
        print("h - pokaż tę pomoc")
        print("q - wyjście z gry")
        print("="*50)
        input("\nNaciśnij Enter aby kontynuować...")
    
    def graj(self):
        print("Witaj w Pasjansie Klondike!")
        print("Wpisz 'h' aby zobaczyć instrukcje.")
        
        while True:
            self.wyswietl_plansze()
            
            if self.czy_wygrana():
                print("\n🎉 GRATULACJE! WYGRAŁEŚ! 🎉")
                break
            
            komenda = input("\nWpisz komendę: ").lower().strip()
            
            if komenda == 'q':
                print("Dzięki za grę!")
                break
            elif komenda == 'h':
                self.wyswietl_pomoc()
            elif komenda == 'd':
                self.dobierz_ze_stosu()
            elif komenda.startswith('ruch'):
                parts = komenda.split()
                if len(parts) == 3:
                    _, skad, dokad = parts
                    self.przesun_karte(skad, dokad)
                else:
                    print("Nieprawidłowa komenda! Użyj: ruch SKĄD DOKĄD")
            else:
                print("Nieprawidłowa komenda! Wpisz 'h' aby zobaczyć pomoc.")
            
            input("\nNaciśnij Enter aby kontynuować...")

if __name__ == "__main__":
    try:
        gra = Pasjans()
        gra.graj()
    except KeyboardInterrupt:
        print("\n\nGra przerwana. Dzięki za grę!")
        sys.exit(0)