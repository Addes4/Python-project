import random  # för att slumpa ord på spelplanen
import tkinter as tk  # för att skapa GUI (grafiskt användargränssnitt)
from tkinter import simpledialog, messagebox  # frågor och meddelanden

# Definierar klassen för Memory-spelet
class MemoryGameGUI:
    # Konstruktör som initierar spelet
    def __init__(self, root, size): 
        self.size = size  # Brädets storlek (antal rader och kolumner)
        self.board = [["---" for _ in range(size)] for _ in range(size)]  # Skapar ett tomt bräde
        self.revealed = [[False for _ in range(size)] for _ in range(size)]  # Håller koll på om en ruta är avslöjad
        self.words = []  # Lista för att lagra ord som används i spelet
        self.first_pick = None  # Håller koll på första valda kortet
        self.attempts = 0  # Räknare för antalet försök
        self.buttons = [[None for _ in range(size)] for _ in range(size)]  # Lista för att lagra GUI-knappar

        # Initierar spelets komponenter
        self.root=root # root som instansvariabel
        self.load_words()  # Laddar ord från en fil
        self.populate_board()  # Fyller brädet med ord
        self.create_gui(root)  # Skapar det grafiska gränssnittet

    # Laddar ord från textfilen memo.txt
    def load_words(self):
        try:
            with open("memo.txt", "r") as file:
                all_words = [line.strip() for line in file if line.strip()]  # Läser in och rensar tomma rader
                self.words = random.sample(all_words, self.size * self.size // 2) * 2 # Väljer slumpmässiga ord och dubblar dem (för matchning)
                random.shuffle(self.words)  # Blandar orden
                self.longest_word_length = max(len(word) for word in self.words)  # Hittar längsta ordet
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Fel", f"Ett fel uppstod: {e}")  # Felhantering
            exit(1)  # Avslutar programmet om det är ett fel

    # Fyller brädet med ord
    def populate_board(self):
        word_index = 0
        for i in range(self.size):
            for j in range(self.size):
                self.board[i][j] = self.words[word_index]
                word_index += 1

    # Skapar GUI (grafiska användargränssnittet)
    def create_gui(self, root):
        # Rubrik
        title = tk.Label(root, text="Memory Game")

        # Spelplan
        board_frame = tk.Frame(root)
        board_frame.pack()

        # Skapar knappar för varje ruta i spelplanen
        for i in range(self.size):
            for j in range(self.size):
                button = tk.Button(
                    board_frame,
                    text="-" * self.longest_word_length,  # Initialt text på knappen i realtion med det största antalet bokstäver av orden
                    width=8,
                    height=4,
                    command=lambda x=i, y=j: self.handle_click(x, y),  # Klickhändelse
                )
                # Lägger till knappen i GUI
                button.grid(row=i, column=j, padx=5, pady=5)  # Pad ser till att mellanrummen mellan knapparna är jämna
                self.buttons[i][j] = button  # Sparar knappen i listan

        # Information om antal försök
        self.info_label = tk.Label(root, text="Försök: 0")
        self.info_label.pack()

    # Hanterar knappklick
    def handle_click(self, x, y):
        if self.revealed[x][y]:  # Ignorera om rutan redan är avslöjad
            return

        # Visa ordet på knappen när man fått rätt
        self.revealed[x][y] = True
        self.buttons[x][y].config(text=self.board[x][y], state="disabled") # låt hittade par synas

        # Om första valet
        if self.first_pick is None:
            self.first_pick = (x, y)
        else:
            # Om andra valet
            x1, y1 = self.first_pick
            if self.board[x][y] == self.board[x1][y1]:  # Kolla om det är en match
                pass
            else:  # Om det inte är en match
                self.root.after(1000, self.hide_tiles, x, y, x1, y1)  # Döljer rutor efter 1000 millisekunder = 1 sekund

            self.attempts += 1  # Öka försöksräknaren oavsett par eller ej
            self.info_label.config(text=f"Försök: {self.attempts}") # uppdaterar abntal försök
            self.first_pick = None  # Återställ första valet

        if self.is_game_over():  # Kontrollera om spelet är över
            self.end_game(self.root)

    # Döljer två rutor om de inte matchar
    def hide_tiles(self, x, y, x1, y1):
        self.revealed[x][y] = False
        self.revealed[x1][y1] = False
        self.buttons[x][y].config(text="-" * self.longest_word_length, state="normal")
        self.buttons[x1][y1].config(text="-" * self.longest_word_length, state="normal")

    # Kontrollerar om spelet är över
    def is_game_over(self):
        return all(all(row) for row in self.revealed) # "är alla synliga så är det slut"

    # Hanterar slutet på spelet
    def end_game(self, root):
        player_name = simpledialog.askstring("Grattis!", f"Du klarade det på {self.attempts} försök! Vad heter du?")
        if player_name:
            self.save_highscore(player_name)  # Spara highscore
        root.quit()  # Stäng spelet

    # Sparar highscore till en fil
    def save_highscore(self, player_name):
        highscore_file = "highscores.txt"
    
        # Läs in befintliga highscores från filen
        highscores = []
        try:
            with open(highscore_file, "r") as file:
                for line in file:
                    name, attempts, size = line.strip().split(",") # strip "isolerar" texten
                    highscores.append({"name": name, "attempts": int(attempts), "size": int(size)}) # split delar upp texten efter varje kommatecken till namn, attempts osv
        except FileNotFoundError:
            print("Highscore filen hittas ej, avbryter")
            pass  # Om filen inte finns, meddela användaren 

        # Lägg till den nya highscore-posten
        new_score = {"name": player_name, "attempts": self.attempts, "size": self.size}
        highscores.append(new_score)

        # Sortera highscore-poster efter antal försök och brädstorlek
        # Om flera personer samma antal försök, sortera  baserat på brädets storlek, negativt tecken så att största brädstorleken först
        highscores.sort(key=lambda x: (x["attempts"], -x["size"])) # attempts ger att lägst antal försök hamnar högre upp

        # Skriv tillbaka hela listan till filen
        with open(highscore_file, "w") as file:
            for score in highscores:
                file.write(f"{score['name']},{score['attempts']},{score['size']}\n")

        # läser in data från filen, sorterar och formaterar för visning i dialogruta
        self.display_highscores(highscore_file)

    # Visar highscore-listan
    def display_highscores(self, highscore_file):
        highscores = []
        try:
            with open(highscore_file, "r") as file:
                for line in file:
                    name, attempts, size = line.strip().split(",")
                    highscores.append({"name": name, "attempts": int(attempts), "size": int(size)})
        except FileNotFoundError:
            print("Highscore filen hittas ej, avbryter")
            pass  # Om filen inte hittas, meddela användaren

        # Skapa texten för att visa highscore-listan
        highscore_text = "\n".join(
            [f"{i+1}. {entry['name']} - {entry['attempts']} försök, {entry['size']}x{entry['size']} bräde" for i, entry in enumerate(highscores)] # formaterar highscore listan
        )

        messagebox.showinfo("Highscores", highscore_text) # Visa lista i dialogruta

    # Fråga användaren om storlek
def ask_size():
    size = simpledialog.askinteger(
        "Välj storlek",
        "Ange storlek på brädet (2-6, endast jämna tal):",
        minvalue = 2,
        maxvalue = 6,
    )

    if size is None:
        messagebox.showwarning("Fel", "Ange en storlek")
        return ask_size()
    elif size % 2 != 0:
        messagebox.showerror("Fel", "Endast jämna tal är tillåtna")
        return ask_size()
    else: # kör programmet
        root = tk.Tk() # skapar huvudfönstret
        root.title("Memory Game") # titel på huvudfönstret
        root.geometry("770x600") # storleken på brädan (huvudfönstret)
        game = MemoryGameGUI(root, size=size) # anropar konstruktor
        root.mainloop() # startar programmet

ask_size() # anropar funktionen för att den ska sättas igång