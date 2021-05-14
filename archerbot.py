from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.replykeyboardremove import ReplyKeyboardRemove
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

updater = Updater("---API-KEY---", use_context=True)

# Globális Dictionary létrehozása
games_dict = {}

#Class Game
class Game:
    def __init__(self, chatId):
        self.chatId = chatId
        self.rounds = int(10)
        self.maxPoint = int(30)
        self.counter = int(1)
        self.point = int(0)
    
    def setRound(self, rounds: int):
        self.rounds = rounds

    def setMaxPoint(self, maxPoint: int):
        self.maxPoint = maxPoint

    def resetCounter(self):
        self.counter = int(1)

    def increaseCounter(self):
        self.counter = self.counter + int(1)
    
    def resetPoint(self):
        self.point = int(0)

    def addPoint(self, point: int):
        self.point = self.point + point


def start(update: Update, context: CallbackContext):
    
    # ChatId kiolvasása a message-ből
    chatId = update.message.chat_id
    createNewGameAndAddToDict(chatId)

    update.message.reply_text("Üdvözöllek, Zafira vagyok. A chat id-d: " + str(chatId)  + ". Alapból 10 fordulót lőhetsz és egy körben 30 az elérhető maximális pontszám. Ezt tetszőlegesen módosíthatod a: /fordulo [n] és a /max [n ]parancsok segítségével. (Ha valami nem világos használd a /help parancsot.) ")
    update.message.reply_text("A gyakorlás elkezdéséhez egyszerűen csak küld el egy üzenetben az első körben lőtt pontszámot.")


def addPoint(update: Update, context: CallbackContext):
    """
    Add achived points and show the stats in the end.
    """
    
    chatId = update.message.chat_id
    game = games_dict[chatId]

    rounds = game.rounds
    counter = game.counter
    point = game.point
    maxPoint = game.maxPoint

    # debugText = "ChatId: " + str(chatId) + "\n-------------\nRound: " + str(rounds) + "\nMaxPoint: " + str(maxPoint) + "\nCounter: " + str(counter) + "\nPoint: " + str(point) + "\n-------------\n-------------\n" 
    # print(debugText)

    newPoint = int(update.message.text)

    # Ha newPoint magasabb mint maxPoint, akkor irjon uzenetet
    if newPoint > maxPoint:
        update.message.reply_text("Nagyobb pontszámot írtál be mint a korábban beállított maximális érték, valamit elszámoltál.")
        return

    if newPoint < 0:
        update.message.reply_text("Negatív pontszámot próbáltál megadni, valamit elgépelhettél.")
        return

    if rounds == counter:
        point = point + newPoint        
        total = maxPoint * rounds
        rate = round((point / total) * 100, 2)
        msg1 = "\nA megszerezhető " + str(total) + " pontból elértél: " + str(point) + " pontot."
        msg2 = "\nEz " + str(rate) + "%-os teljesítmény."
        msg3 = "\n\nKezdheted az új edzést azonos beállításokkal."
        update.message.reply_text(msg1 + msg2 + msg3)
        
        game.resetCounter()
        game.resetPoint()
        return

    if rounds > counter:
        
        # add new ponts to the stat
        game.increaseCounter()
        game.addPoint(newPoint)
        msg = "Összesen: " + str(game.point) + " pontod van.\n" + str(rounds - counter) + " kör van még hátra."
        update.message.reply_text(msg)    

def initMaxPoint(update: Update, context: CallbackContext):
    rawInput = update.message.text
    maxPoint = int(rawInput[5:])

    chatId = update.message.chat_id
    game = games_dict[chatId]
    game.setMaxPoint(maxPoint)
    
    
    msg = "Az egy körben lőhető max pontszámot " + str(maxPoint) + " pontra állítottam."
    update.message.reply_text(msg)

def initRounds(update: Update, context: CallbackContext):
    rawInput = update.message.text
    newRound = int(rawInput[9:])

    chatId = update.message.chat_id
    game = games_dict[chatId]
    game.setRound(newRound)
    
    msg = str(newRound) + " kört fugunk lőni."
    update.message.reply_text(msg)


def restartGame(update: Update, context: CallbackContext):
    #Újraindítja a játékot, megtartva az egyéni beállításokat.
    chatId = update.message.chat_id
    game = games_dict[chatId]
    game.resetCounter()

    update.message.reply_text("Újrakezdtem az edzést a korábbi beállításokkal, jó gyakorlást!")

def showHelpDialog(update: Update, context: CallbackContext):
        update.message.reply_text("Szia, Zafira 2.2 vagyok.\nAhhoz, hogy nekem egy parancsod adj, azt a '/' perjellel kell kezdened.\nA fordulók számának módosítását a /fordulo (szóköz) [n] paranccsal teheted meg, ahol az [n] a fordulók száma legyen pl.: /fordulo 5\nUgyanez igaz az egy körben elérhető max pontszám beállítására, pl.: /max 20\nEz utóbbinál kérlek Te vedd figyelembe, hogy milyen lőlapra hány vesszövel tervezel lőni.\nA gyakorlás elkezdéséhez pedig csak üzenetben küld el az adott körben lőtt pontszámot.\nHa olyan üzenetet küldesz amit nem ismerek fel, arra (még) nem tudok válaszolni.\nEzekre az értékekre azért van szükségem, hogy ki tudjam számolni az edzéseid eredményességét.")
        update.message.reply_text("Disclaimer: A fejlesztőm bot mivoltom megszemélyesítéséhez kislánya javaslatára az ő kedvenc babáját választotta, így nevemnek és bőrszínemnek semmi felhangja, töbletjelentése nincs. Ugye milyen szép dolog az őszinte gyermeki ártatlanság és nyitottság? Bízom benne, hogy Te kedves felhasználó is így gondolod:)")

def printGame(update: Update, context: CallbackContext):
    #Debug függvény, a játékhoz nem szükséges
    chatId = update.message.chat_id
    game = games_dict[chatId]
    
    msg = "Az aktuális játékod:\nForduló: " + str(game.rounds) + "\nMax Pont: " + str(game.maxPoint) + "\nAktuális forduló: " + str(game.counter) + "\nPontszám: " + str(game.point) 
    update.message.reply_text(msg)

def createNewGameAndAddToDict(chatId: int):
    # Új játék objektum létrehozása a user-nek
    newGame = Game(chatId)

    # Új game és user hozzáadása a dictionary-hez
    games_dict[chatId] = newGame
    #print(games_dict)


updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("max", initMaxPoint))
updater.dispatcher.add_handler(CommandHandler("fordulo", initRounds))
updater.dispatcher.add_handler(CommandHandler("restart", restartGame))
updater.dispatcher.add_handler(CommandHandler("game", printGame))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(r"[0-9]"), addPoint))
updater.dispatcher.add_handler(CommandHandler("help", showHelpDialog))

updater.start_polling()


# adding the message handler with filter to handle the Option [0-9] regex input
# documentation for MessageHandler: https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.messagehandler.html
# documentation for Filter: https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.filters.html#telegram.ext.filters.Filters
