import email
from email.header import decode_header
import imaplib
import re
import threading
import time
from bs4 import BeautifulSoup

from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout


class OrderMonitorApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "LightBlue"

        self.en_cours = False

        # Écran principal
        screen = MDScreen()

        layout = MDBoxLayout(orientation="vertical")

        # Barre de titre
        toolbar = MDTopAppBar(title="Universal Order Monitor")
        layout.add_widget(toolbar)

        # Zone de formulaire
        form_layout = MDBoxLayout(
            orientation="vertical",
            spacing="10dp",
            padding="20dp",
            size_hint_y=None,
        )
        form_layout.bind(minimum_height=form_layout.setter("height"))

        self.email_input = MDTextField(
            hint_text="Adresse Gmail",
            text="zak.h.hachani@gmail.com",
            icon_right="email",
        )
        form_layout.add_widget(self.email_input)

        self.pass_input = MDTextField(
            hint_text="Mot de passe d'application",
            password=True,
            icon_right="key",
        )
        form_layout.add_widget(self.pass_input)

        self.btn_control = MDRaisedButton(
            text="DÉMARRER LA SURVEILLANCE",
            pos_hint={"center_x": 0.5},
            size_hint_x=1,
            on_release=self.toggle_surveillance,
        )
        form_layout.add_widget(self.btn_control)

        layout.add_widget(form_layout)

        # Zone de logs / résultats (Correction : padding déplacé sur log_layout)
        scroll = MDScrollView()
        self.log_layout = MDBoxLayout(
            orientation="vertical", 
            spacing="10dp", 
            padding="10dp", 
            size_hint_y=None
        )
        self.log_layout.bind(minimum_height=self.log_layout.setter("height"))

        scroll.add_widget(self.log_layout)
        layout.add_widget(scroll)

        screen.add_widget(layout)
        return screen

    def add_log_card(self, text, is_error=False):
        # Ajoute une carte visuelle dans l'application
        def _add(dt):
            card = MDCard(
                orientation="vertical",
                padding="15dp",
                size_hint_y=None,
                height="120dp",
                size_hint_x=0.95,
                pos_hint={"center_x": 0.5},
                md_bg_color=(
                    [0.8, 0.2, 0.2, 1] if is_error else [0.15, 0.2, 0.3, 1]
                ),
            )
            label = MDLabel(
                text=text, theme_text_color="Custom", text_color=[1, 1, 1, 1]
            )
            card.add_widget(label)
            self.log_layout.add_widget(card)

        Clock.schedule_once(_add)

    def toggle_surveillance(self, instance):
        if not self.en_cours:
            if not self.email_input.text or not self.pass_input.text:
                self.add_log_card(" Veuillez remplir tous les champs !", is_error=True)
                return

            self.en_cours = True
            self.btn_control.text = "ARRÊTER LA SURVEILLANCE"
            self.btn_control.md_bg_color = [0.8, 0.2, 0.2, 1]
            self.add_log_card(" Surveillance universelle activée...")

            threading.Thread(target=self.boucle_surveillance, daemon=True).start()
        else:
            self.en_cours = False
            self.btn_control.text = "DÉMARRER LA SURVEILLANCE"
            self.btn_control.md_bg_color = self.theme_cls.primary_color
            self.add_log_card(" Surveillance arrêtée.")

    def boucle_surveillance(self):
        gmail_user = self.email_input.text.strip()
        gmail_pass = self.pass_input.text.strip()

        while self.en_cours:
            try:
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(gmail_user, gmail_pass)
                mail.select("inbox")

                # Recherche universelle des e-mails non lus contenant "commande" ou "order"
                status, messages = mail.search(
                    None, '(UNSEEN OR (SUBJECT "commande") (SUBJECT "order"))'
                )

                if status == "OK" and messages[0]:
                    for num in messages[0].split():
                        _, msg_data = mail.fetch(num, "(RFC822)")
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])

                                subject_header = decode_header(msg["Subject"])[0]
                                subject = subject_header[0]
                                encoding = subject_header[1]
                                if isinstance(subject, bytes):
                                    subject = subject.decode(encoding or "utf-8", errors="ignore")

                                html_body = ""
                                if msg.is_multipart():
                                    for part in msg.walk():
                                        if part.get_content_type() == "text/html":
                                            payload = part.get_payload(decode=True)
                                            if payload:
                                                html_body = payload.decode(errors="ignore")
                                            break
                                else:
                                    payload = msg.get_payload(decode=True)
                                    if payload:
                                        html_body = payload.decode(errors="ignore")

                                num_cmd, client, qte, prix = self.extraire_donnees(
                                    subject, html_body
                                )

                                affichage = (
                                    f" NOUVELLE COMMANDE #{num_cmd}\n"
                                    f" Client : {client}\n"
                                    f" Articles : {qte} |  Total : {prix}"
                                )
                                self.add_log_card(affichage)

                mail.logout()
            except Exception as e:
                self.add_log_card(f" Erreur : {e}", is_error=True)

            for _ in range(30):
                if not self.en_cours:
                    break
                time.sleep(1)

    def extraire_donnees(self, sujet, html_body):
        soup = BeautifulSoup(html_body, "html.parser")
        texte = soup.get_text()

        # Recherche flexible du numéro de commande (ex: Commande #1234, Order #1234, #1234)
        order_match = re.search(
            r"(?:commande|order)\s*(?:#|numéro|n°)?\s*(\d+)", sujet or texte, re.IGNORECASE
        )
        if not order_match:
            order_match = re.search(r"#(\d+)", sujet or texte)
        num_commande = order_match.group(1) if order_match else "Inconnu"

        # Recherche flexible du client
        client_match = re.search(
            r"(?:placée par|passée par|par)\s+([A-Za-z\s]+)", sujet or texte, re.IGNORECASE
        )
        if not client_match:
            client_match = re.search(
                r"([A-Za-z\s]+)\s+(?:a passé|a commandé)", texte, re.IGNORECASE
            )
        nom_client = client_match.group(1).strip() if client_match else "Client"

        # Quantification des articles
        quantites = re.findall(r"(?:×|x)\s*(\d+)", texte)
        total_articles = sum(int(q) for q in quantites) if quantites else 1

        # Recherche universelle du prix total
        total_match = re.search(
            r"(?:total|montant|prix)\s*[:\s]*([\d\.,]+)\s*([A-Za-z]{3}|€|\$|£)", texte, re.IGNORECASE
        )
        if not total_match:
            total_match = re.search(r"([\d\.,]+)\s*(€|\$|£|USD|EUR)", texte)

        prix_total = (
            f"{total_match.group(1)} {total_match.group(2)}"
            if total_match
            else "Inconnu"
        )

        return num_commande, nom_client, total_articles, prix_total


if __name__ == "__main__":
    OrderMonitorApp().run()
