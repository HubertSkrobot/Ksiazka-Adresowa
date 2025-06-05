import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QListWidget, QInputDialog,
    QGroupBox, QFormLayout
)

PLIK_Z_ADRESAMI = "adresy_ksiazki.json"

class KsiazkaAdresowa(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Książka Adresowa")
        self.setMinimumWidth(550)

        self.adresy = self.wczytaj_adresy()

        # pola do wpisywania danych przez użytkownika
        self.Imie = QLineEdit()
        self.Nazwisko = QLineEdit()
        self.Telefon = QLineEdit()
        self.Ulica = QLineEdit()
        self.Miasto = QLineEdit() 

        # Lista do wyświetlania adresów
        self.listaAdresow = QListWidget()

        #Przyciski do obsługi akcji
        Dodaj = QPushButton("Dodaj adres")
        Szukaj = QPushButton("Szukaj")
        Statystyka = QPushButton("Statystyki")
        Usun = QPushButton("Usuń")

        # Łączenie przycisków z funkcjami
        Dodaj.clicked.connect(self.dodaj_adres)
        Szukaj.clicked.connect(self.szukaj_adresu)
        Statystyka.clicked.connect(self.pokaz_statystyki)
        Usun.clicked.connect(self.usun_adres)

        # Układ formularza
        formularz = QGroupBox("Nowy adres")
        uklad = QFormLayout()
        uklad.addRow("Imię:", self.Imie)
        uklad.addRow("Nazwisko:", self.Nazwisko)
        uklad.addRow("Telefon:", self.Telefon)
        uklad.addRow("Ulica:", self.Ulica)
        uklad.addRow("Miasto:", self.Miasto)
        formularz.setLayout(uklad)

        przyciski = QHBoxLayout()
        for przycisk in [Dodaj, Szukaj, Statystyka, Usun]:
            przyciski.addWidget(przycisk)

        # Glwny układ okna
        glownyUklad = QVBoxLayout()
        glownyUklad.addWidget(formularz)
        glownyUklad.addLayout(przyciski)
        glownyUklad.addWidget(QLabel("Wszystkie zapisane adresy:"))
        glownyUklad.addWidget(self.listaAdresow)

        self.setLayout(glownyUklad)
        self.odswiez_liste()

    def wczytaj_adresy(self): #wczytuje liste adresow z pliku JSON. Jeżeli plik z danymi jest pusty lub uszkodzony, program pokaże komunikat
        if os.path.exists(PLIK_Z_ADRESAMI):
            try:
                with open(PLIK_Z_ADRESAMI, 'r', encoding='utf-8') as plik:
                    return json.load(plik)
            except Exception:
                QMessageBox.warning(self, "Uszkodzony plik!", "Plik z adresami jest uszkodzony. Tworzę nowy.")
                self.adresy = []
                self.zapisz_adresy()
                return []
        else:
            QMessageBox.information(self, "Brak pliku", "Nie znaleziono pliku z adresami. Tworzę nowy.")
            self.adresy = []
            self.zapisz_adresy()
            return []

    def zapisz_adresy(self): # zapisuje dane do pliku
        with open(PLIK_Z_ADRESAMI, 'w', encoding='utf-8') as plik:
            json.dump(self.adresy, plik, indent=4, ensure_ascii=False)

    def dodaj_adres(self): #pobiera dane wpisane w formularzu dodaje nowy adres do pliku i odswieza liste
        imie = self.Imie.text().strip()
        nazwisko = self.Nazwisko.text().strip()
        telefon = self.Telefon.text().strip()
        ulica = self.Ulica.text().strip()
        miasto = self.Miasto.text().strip()

          # sprawdzamy czy wymagane pola są wypełnione
        if not imie or not nazwisko or not ulica or not miasto:
            QMessageBox.warning(self, "Błąd!", "Imię, nazwisko, ulica i miasto są wymagane.")
            return

        # sprawdzamy czy adres już istnieje
        for adres in self.adresy:
            if adres['imie'].lower() == imie.lower() and adres['nazwisko'].lower() == nazwisko.lower():
                QMessageBox.warning(self, "Duplikat!", "Taki użytkownik już istnieje.")
                return

        nowy = {
            "imie": imie,
            "nazwisko": nazwisko,
            "telefon": telefon,
            "ulica": ulica,
            "miasto": miasto
        }

        self.adresy.append(nowy)
        self.zapisz_adresy()
        self.wyczysc_pola()
        self.odswiez_liste()
        QMessageBox.information(self, "Dodano", "Adres został dodany!")

    def wyczysc_pola(self): # czysci pola po dodaniu adresu jakiegos
        self.Imie.clear()
        self.Nazwisko.clear()
        self.Telefon.clear()
        self.Ulica.clear()
        self.Miasto.clear()

    def szukaj_adresu(self): #wyszukuje wpisane osoby po wybranym kryterium
        pola = ["imie", "nazwisko", "telefon", "ulica", "miasto"]
        kryterium, ok1 = QInputDialog.getItem(self, "Szukaj", "Szukaj wg:", pola, 0, False)
        if not ok1:
            return

        wartosc, ok2 = QInputDialog.getText(self, "Szukaj", f"Podaj {kryterium}:")
        if not ok2:
            return

        wyniki = [a for a in self.adresy if a.get(kryterium, '').lower() == wartosc.lower()]
        self.listaAdresow.clear()

        if wyniki:
            for a in wyniki:
                self.listaAdresow.addItem(self.formatuj_adres(a))
        else:
            self.listaAdresow.addItem("Brak wyników.")

    def odswiez_liste(self):
        self.listaAdresow.clear()
        if not self.adresy:
            self.listaAdresow.addItem("Brak zapisanych adresów.")
            return

        for adres in self.adresy:
            self.listaAdresow.addItem(self.formatuj_adres(adres))

    def pokaz_statystyki(self):# liczy i wyswietla statystyki miast
        miasta = {}
        for a in self.adresy:
            m = a["miasto"].strip()
            miasta[m] = miasta.get(m, 0) + 1

        if not miasta:
            tekst = "Brak danych do statystyk."
        else:
            tekst = "Liczba adresów w miastach:\n"
            for miasto, ile in sorted(miasta.items()):
                tekst += f"- {miasto}: {ile}\n"

        QMessageBox.information(self, "Statystyki", tekst)

    def usun_adres(self): #usuwa zazanaczony adres z pliku JSON
        try:
            wybrany = self.listaAdresow.currentItem()
            if not wybrany:
                QMessageBox.warning(self, "Błąd", "Zaznacz adres do usunięcia.")
                return

            tekst = wybrany.text()
            nowa_lista = [a for a in self.adresy if self.formatuj_adres(a) != tekst] # tworzymy nową listę adresów, ale bez tej, którą usuwamy

            if len(nowa_lista) < len(self.adresy): # Sprawdzamy, czy coś zostało usunięte
                self.adresy = nowa_lista
                self.zapisz_adresy()
                self.odswiez_liste()
                QMessageBox.information(self, "Usunięto", "Adres został usunięty.")
            else:
                QMessageBox.warning(self, "Błąd", "Nie znaleziono zaznaczonego adresu.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd krytyczny", f"Coś poszło nie tak przy usuwaniu: {str(e)}")

    def formatuj_adres(self, a): #formatowanie danych adresu tak, żeby był czytelnie wyświetlany
        tel = f", tel: {a['telefon']}" if a.get('telefon') else ""
        return f"{a['imie']} {a['nazwisko']}{tel}, {a['ulica']}, {a['miasto']}"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    okno = KsiazkaAdresowa()
    okno.show()
    sys.exit(app.exec_())
