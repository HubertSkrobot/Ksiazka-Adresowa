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

        self.adresy = self._wczytaj_adresy()

        # Pola do wpisywania danych przez użytkownika
        self.pole_imie = QLineEdit()
        self.pole_nazwisko = QLineEdit()
        self.pole_telefon = QLineEdit()
        self.pole_ulica = QLineEdit()
        self.pole_miasto = QLineEdit()

        # Lista do wyświetlania adresów
        self.lista_adresow = QListWidget()

        # Przyciski do obsługi akcji
        przycisk_dodaj = QPushButton("Dodaj adres")
        przycisk_szukaj = QPushButton("Szukaj")
        przycisk_statystyka = QPushButton("Statystyki")
        przycisk_usun = QPushButton("Usuń")

        # Łączenie przycisków z odpowiednimi funkcjami
        przycisk_dodaj.clicked.connect(self._dodaj_adres)
        przycisk_szukaj.clicked.connect(self._szukaj_adres)
        przycisk_statystyka.clicked.connect(self._pokaz_statystyki)
        przycisk_usun.clicked.connect(self._usun_adres)

        # Układ formularza
        formularz = QGroupBox("Nowy adres")
        uklad_formularza = QFormLayout()
        uklad_formularza.addRow("Imię:", self.pole_imie)
        uklad_formularza.addRow("Nazwisko:", self.pole_nazwisko)
        uklad_formularza.addRow("Telefon:", self.pole_telefon)
        uklad_formularza.addRow("Ulica:", self.pole_ulica)
        uklad_formularza.addRow("Miasto:", self.pole_miasto)
        formularz.setLayout(uklad_formularza)

        przyciski = QHBoxLayout()
        for przycisk in [przycisk_dodaj, przycisk_szukaj, przycisk_statystyka, przycisk_usun]:
            przyciski.addWidget(przycisk)

        # Glwny uklad okna aplikacji
        glowny_uklad = QVBoxLayout()
        glowny_uklad.addWidget(formularz)
        glowny_uklad.addLayout(przyciski)
        glowny_uklad.addWidget(QLabel("Wszystkie zapisane adresy:"))
        glowny_uklad.addWidget(self.lista_adresow)

        self.setLayout(glowny_uklad)

        # Odświezamy liste na starcie
        self._odswiez_liste_adresow()

    def _wczytaj_adresy(self): #wczytuje liste adresow z pliku JSON. Jeżeli plik z danymi jest pusty lub uszkodzony, program pokaże komunikat
        if os.path.exists(PLIK_Z_ADRESAMI):
            try:
                with open(PLIK_Z_ADRESAMI, 'r', encoding='utf-8') as plik:
                    return json.load(plik)
            except json.JSONDecodeError:
                QMessageBox.warning(self, "Błąd wczytywania",
                                    "Plik z danymi jest uszkodzony lub pusty. Zaczynamy z pustą książką adresową.")
                return []
        return []

    def _zapisz_adresy(self): # zapisuje dane do pliku
        with open(PLIK_Z_ADRESAMI, 'w', encoding='utf-8') as plik:
            json.dump(self.adresy, plik, indent=4, ensure_ascii=False)

    def _dodaj_adres(self):
        """
        Pobiera dane z formularza, waliduje je i dodaje nowy adres.
        Zapisuje zmiany i odświeża listę.
        """
        imie = self.pole_imie.text().strip()
        nazwisko = self.pole_nazwisko.text().strip()
        telefon = self.pole_telefon.text().strip()
        ulica = self.pole_ulica.text().strip()
        miasto = self.pole_miasto.text().strip()

        # sprawdzamy czy wymagane pola są wypełnione
        if not imie or not nazwisko or not ulica or not miasto:
            QMessageBox.warning(self, "Błąd", "Imię, nazwisko, ulica i miasto są wymagane.")
            return

        #sprawdzamy czy adres już istnieje
        for adres in self.adresy:
            if adres['imie'].lower() == imie.lower() and \
               adres['nazwisko'].lower() == nazwisko.lower():
                QMessageBox.warning(self, "Duplikat", "Taki użytkownik już istnieje w książce.")
                return

        nowy_adres = {
            "imie": imie,
            "nazwisko": nazwisko,
            "telefon": telefon,
            "ulica": ulica,
            "miasto": miasto
        }
        self.adresy.append(nowy_adres)
        self._zapisz_adresy()
        self._wyczysc_pola()
        self._odswiez_liste_adresow()
        QMessageBox.information(self, "Sukces", "Adres został dodany!")

    def _wyczysc_pola(self): # czysci pola po dodaniu adresu jakiegos
        self.pole_imie.clear()
        self.pole_nazwisko.clear()
        self.pole_telefon.clear()
        self.pole_ulica.clear()
        self.pole_miasto.clear()

    def _szukaj_adres(self): # wyszukuje wpisane osoby po wybranym kryterium
        kryteria = ["imie", "nazwisko", "telefon", "ulica", "miasto"]
        kryterium, wybor = QInputDialog.getItem(self, "Szukaj", "Szukaj wg:", kryteria, 0, False)
        if not wybor:
            return

        wartosc, wpisanie = QInputDialog.getText(self, "Szukaj", f"Podaj {kryterium}:")
        if not wpisanie:
            return

        wyniki = [adres for adres in self.adresy if adres.get(kryterium, '').lower() == wartosc.lower()] # dodatkowe ignorowanie wielkosci liter

        self.lista_adresow.clear()
        if wyniki:
            for adres in wyniki:
                self.lista_adresow.addItem(self._formatuj_adres(adres))
        else:
            self.lista_adresow.addItem("Brak wyników.")

    def _odswiez_liste_adresow(self):
        self.lista_adresow.clear()
        if not self.adresy:
            self.lista_adresow.addItem("Książka adresowa jest pusta. Dodaj pierwszy adres!")
            return

        for adres in self.adresy:
            self.lista_adresow.addItem(self._formatuj_adres(adres))

    def _pokaz_statystyki(self): # liczy i wyswietla statystyki miast
        miasta = {}
        for adres in self.adresy:
            miasto = adres.get("miasto", "Nieokreślone miasto").strip()
            miasta[miasto] = miasta.get(miasto, 0) + 1

        if not miasta:
            komunikat = "Brak danych do wygenerowania statystyk."
        else:
            komunikat = "Liczba adresów w miastach:\n"
            for miasto, liczba in sorted(miasta.items()): # Sortowanie dla czytelności
                komunikat += f"- {miasto}: {liczba} adresów\n"

        QMessageBox.information(self, "Statystyki", komunikat)

    def _usun_adres(self): #usuwa zazanaczony adres z pliku JSON
        zaznaczony_element = self.lista_adresow.currentItem()
        if not zaznaczony_element:
            QMessageBox.warning(self, "Błąd", "Proszę zaznaczyć adres do usunięcia.")
            return

        tekst_do_usuniecia = zaznaczony_element.text()

        nowa_lista_adresow = [ # tworzymy nową listę adresów, ale bez tej, którą usuwamy
            a for a in self.adresy if self._formatuj_adres(a) != tekst_do_usuniecia
        ]

        if len(nowa_lista_adresow) < len(self.adresy): # Sprawdzamy, czy coś zostało usunięte
            self.adresy = nowa_lista_adresow
            self._zapisz_adresy()
            self._odswiez_liste_adresow()
            QMessageBox.information(self, "Usunięto", "Adres został pomyślnie usunięty.")
        else:
            QMessageBox.warning(self, "Błąd", "Nie udało się znaleźć zaznaczonego adresu.")


    def _formatuj_adres(self, adres): #formatowanie danych adresu tak, żeby był czytelnie wyświetlany
        telefon_info = f", tel: {adres['telefon']}" if adres.get('telefon') else ""
        return f"{adres['imie']} {adres['nazwisko']}{telefon_info}, {adres['ulica']}, {adres['miasto']}"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    okno = KsiazkaAdresowa()
    okno.show()
    sys.exit(app.exec_())
