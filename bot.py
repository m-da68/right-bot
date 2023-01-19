import vk_api, json, time, pymysql, random, wikipedia
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from datetime import datetime, timedelta
import logging as logging1
from transliterate import translit

token = ""
token_mobile = ""

vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, 210984954)
vk = vk_session.get_api()

vk_session_mobile = vk_api.VkApi(token=token_mobile)
vk_mobile = vk_session_mobile.get_api()

settings = dict(one_time=False, inline=True)
buffer_money_user = None
buffer_marry_user = None
buffer_mute_user = None

wikipedia.set_lang("RU")

logging = logging1.getLogger()
logging.setLevel(logging1.DEBUG)
handler = logging1.FileHandler('logs.txt', 'w', 'utf-8')
handler.setFormatter(logging1.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s', '%Y-%m-%d %H:%M:%S'))
logging.addHandler(handler)

def get_user(pattern: str) -> int:
    if "[id" in pattern:
        return int(pattern.split("|")[0].replace("[id", ""))
    if "vk.com/" in pattern:
        domen = pattern.split("/")[-1]
        return vk.utils.resolveScreenName(screen_name=domen)["object_id"]

def get_name(id, name_case="nom", do_logger=None):
    result = vk.users.get(user_ids=id, name_case=name_case)[0]
    if do_logger == None:
        name = "[id{0}|{1} {2}]".format(str(id), result["first_name"], result["last_name"])
    else:
        name = "{1} {2} (id{0})".format(str(id), translit(result["first_name"], language_code='ru', reversed=True), translit(result["last_name"], language_code='ru', reversed=True))
    return name

def do_account_user(user):
    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
    count = cur.rowcount
    db.close()
    if count > 0:
        return True
    else:
        return False

def do_account_muted(user):
    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute("SELECT * FROM `mutes` WHERE `vk_id`='{0}'".format(str(user)))
    count = cur.rowcount
    db.close()
    if count > 0:
        return True
    else:
        return False
    
def do_account_baned(user):
    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute("SELECT * FROM `bans` WHERE `vk_id`='{0}'".format(str(user)))
    count = cur.rowcount
    db.close()
    if count > 0:
        return True
    else:
        return False

def do_user_admin(user):
    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
    try:
        result = cur.fetchall()[0]
        if result["role"] == "admin":
            return True
        if result["role"] == "owner":
            return True
        else:
            return False
    except:
        return False

def do_user_owner(user):
    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
    try:
        result = cur.fetchall()[0]
        if result["role"] == "owner":
            return True
        else:
            return False
    except:
        return False

def add_money(const, user):
    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
    money = cur.fetchall()[0]["money"]
    db.close()

    money += const

    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute("UPDATE `users` SET `money` = '{0}' WHERE `vk_id`='{1}'".format(str(money), str(user)))
    db.close()

def minus_money(const, user):
    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
    money = cur.fetchall()[0]["money"]
    db.close()

    money -= const

    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute("UPDATE `users` SET `money` = '{0}' WHERE `vk_id`='{1}'".format(str(money), str(user)))
    db.close()

def get_user_money(user):
    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
    money = cur.fetchall()[0]["money"]
    db.close()
    return money

def set_sex_text(user, male, female):
    result = vk.users.get(user_ids=user, fields="sex")[0]

    if result["sex"] == 2:
        return male
    if result["sex"] == 1:
        return female

def get_randomphoto_album(album_id):
    album_vk = vk_mobile.photos.get(owner_id=-210419741, album_id=album_id)
    if album_vk["items"] != []:
        photo_item = random.choice(album_vk["items"])
        return "photo{0}_{1}".format(str(photo_item["owner_id"]), str(photo_item["id"]))
    else:
        return None

def do_marry_user(user):
    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
    result = cur.fetchall()[0]
    if result["marry"] != None:
        return True
    else:
        return False

def sender(peer_id, text, attachment=None, keyboard=None, template=None):
    return vk.messages.send(peer_id=peer_id, message=str(text), attachment=attachment, keyboard=keyboard, template=template, random_id=0)

for event in longpoll.listen():
    try:
        if event.type == VkBotEventType.MESSAGE_EVENT:
            peer_id = id = event.obj.peer_id
            type = event.object.payload.get('type')
            user = event.object.user_id

            if type == "strapon_yes":
                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                cur = db.cursor()
                cur.execute("UPDATE `users` SET `sex_mode` = '1' WHERE `vk_id`='{0}'".format(str(user)))
                db.close()
                vk.messages.sendMessageEventAnswer(event_id=event.object.event_id, user_id=event.object.user_id, peer_id=event.object.peer_id, event_data=json.dumps({"type": "show_snackbar", "text": "Вы успешно изменили состояние опции Страпон"}))
                
            if type == "strapon_no":
                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                cur = db.cursor()
                cur.execute("UPDATE `users` SET `sex_mode` = NULL WHERE `vk_id`='{0}'".format(str(user)))
                db.close()
                vk.messages.sendMessageEventAnswer(event_id=event.object.event_id, user_id=event.object.user_id, peer_id=event.object.peer_id, event_data=json.dumps({"type": "show_snackbar", "text": "Вы успешно изменили состояние опции Страпон"}))
                
            if type == "money_plus_10":
                if do_user_owner(user):
                    if buffer_money_user != None:
                        add_money(10, buffer_money_user)
                        sender(id, "На счет {0} зачислено 10 монет<br>Баланс: {1}".format(get_name(buffer_money_user, "gen"), str(get_user_money(buffer_money_user))))
                    else:
                        vk.messages.sendMessageEventAnswer(event_id=event.object.event_id, user_id=event.object.user_id, peer_id=event.object.peer_id, event_data=json.dumps({"type": "show_snackbar", "text": "Не удалось выполнить это автоматически, используйте команду Деньги+ @айди Кол-во_денег"}))
            if type == "money_plus_100":
                if do_user_owner(user):
                    if buffer_money_user != None:
                        add_money(100, buffer_money_user)
                        sender(id, "На счет {0} зачислено 100 монет<br>Баланс: {1}".format(get_name(buffer_money_user, "gen"), str(get_user_money(buffer_money_user))))
                    else:
                        vk.messages.sendMessageEventAnswer(event_id=event.object.event_id, user_id=event.object.user_id, peer_id=event.object.peer_id, event_data=json.dumps({"type": "show_snackbar", "text": "Не удалось выполнить это автоматически, используйте команду Деньги+ @айди Кол-во_денег"}))

            if type == "money_minus_10":
                if do_user_owner(user):
                    if buffer_money_user != None:
                        minus_money(10, buffer_money_user)
                        sender(id, "Со счета {0} списано 10 монет<br>Баланс: {1}".format(get_name(buffer_money_user, "gen"), str(get_user_money(buffer_money_user))))
                    else:
                        vk.messages.sendMessageEventAnswer(event_id=event.object.event_id, user_id=event.object.user_id, peer_id=event.object.peer_id, event_data=json.dumps({"type": "show_snackbar", "text": "Не удалось выполнить это автоматически, используйте команду Деньги- @айди Кол-во_денег"}))
            if type == "money_minus_100":
                if do_user_owner(user):
                    if buffer_money_user != None:
                        minus_money(100, buffer_money_user)
                        sender(id, "Со счета {0} списано 100 монет<br>Баланс: {1}".format(get_name(buffer_money_user, "gen"), str(get_user_money(buffer_money_user))))
                    else:
                        vk.messages.sendMessageEventAnswer(event_id=event.object.event_id, user_id=event.object.user_id, peer_id=event.object.peer_id, event_data=json.dumps({"type": "show_snackbar", "text": "Не удалось выполнить это автоматически, используйте команду Деньги- @айди Кол-во_денег"}))

            if type == "money_0":
                if do_user_owner(user):
                    if buffer_money_user != None:
                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                        cur = db.cursor()
                        cur.execute("UPDATE `users` SET `money` = '0' WHERE `vk_id`='{0}'".format(str(buffer_money_user)))
                        db.close()
                        sender(id, "Счет {0} был обнулен<br>Баланс: {1}".format(get_name(buffer_money_user, "gen"), str(get_user_money(buffer_money_user))))
                    else:
                        vk.messages.sendMessageEventAnswer(event_id=event.object.event_id, user_id=event.object.user_id, peer_id=event.object.peer_id, event_data=json.dumps({"type": "show_snackbar", "text": "Не удалось выполнить это автоматически, используйте команду Деньги0 @айди"}))
                    
            if type == "money_share":
                sender(id, "Для того, чтобы поделиться средствами напишите<br>Деньги перевод @айди [сумма]")
            
            if type == "money_add":
                sender(id, "За каждые 10 сообщений на ваш счет начисляется 5 монет<br>Так же вы можите пополнить внутренний счет за реальные деньги<br>Писать разработчику ({0})".format(get_name(400484262)))
            
            if type == "mute_time_5":
                if do_user_admin(user):
                    time = datetime.now() + timedelta(minutes=5)
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("INSERT INTO `mutes`(`vk_id`, `datetime`) VALUES ('{0}', '{1}')".format(str(buffer_mute_user), str(time)))
                    db.close()
                    
                    sender(id, "{0}, вы были замучены на 5 минут".format(get_name(buffer_mute_user)))
                    logging.info("User {0} was muted (5min) by moderator {1}".format(get_name(buffer_mute_user, "nom", True), get_name(user, "nom", True)))
                
            if type == "mute_time_10":
                if do_user_admin(user):
                    time = datetime.now() + timedelta(minutes=10)
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("INSERT INTO `mutes`(`vk_id`, `datetime`) VALUES ('{0}', '{1}')".format(str(buffer_mute_user), str(time)))
                    db.close()
                    
                    sender(id, "{0}, вы были замучены на 10 минут".format(get_name(buffer_mute_user)))
                    logging.info("User {0} was muted (10min) by moderator {1}".format(get_name(buffer_mute_user, "nom", True), get_name(user, "nom", True)))
                
            if type == "mute_time_30":
                if do_user_admin(user):
                    time = datetime.now() + timedelta(minutes=30)
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("INSERT INTO `mutes`(`vk_id`, `datetime`) VALUES ('{0}', '{1}')".format(str(buffer_mute_user), str(time)))
                    db.close()
                    
                    sender(id, "{0}, вы были замучены на 30 минут".format(get_name(buffer_mute_user)))
                    logging.info("User {0} was muted (30min) by moderator {1}".format(get_name(buffer_mute_user, "nom", True), get_name(user, "nom", True)))
            
            if type == "mute_time_1":
                if do_user_admin(user):
                    time = datetime.now() + timedelta(minutes=60)
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("INSERT INTO `mutes`(`vk_id`, `datetime`) VALUES ('{0}', '{1}')".format(str(buffer_mute_user), str(time)))
                    db.close()
                    
                    sender(id, "{0}, вы были замучены на 1 час".format(get_name(buffer_mute_user)))
                    logging.info("User {0} was muted (1hour) by moderator {1}".format(get_name(buffer_mute_user, "nom", True), get_name(user, "nom", True)))

            if type == "console_sql":
                if event.obj.user_id == 400484262:
                    sender(id, "Сервер mySQL сопряжен с консолью")
                    logging.debug("Connect to mysql server")
                    for event in longpoll.listen():
                        if event.type == VkBotEventType.MESSAGE_NEW:
                            if event.obj.from_id == 400484262:
                                if event.obj.text.lower() == "break":
                                    break
                                else:
                                    peer_id = id = event.obj["peer_id"]
                                    sql = event.obj.text.lower().replace("'", "\'")
                                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                    cur = db.cursor()
                                    try:
                                        cur.execute(sql)
                                        sender(id, "SQL query was executed successfully<br>"+str(cur.fetchall()))
                                        db.close()
                                        logging.debug("SQL query was executed successfully: {0} => {1}".format(sql, str(cur.fetchall())))
                                        break
                                    except Exception as e:
                                        sender(id, f"Ошибка: {e}")
                                        logging.exception(f"ERROR SQL {e}")
                                        break

            if type == "marry_add_yes":
                if buffer_marry_user == user:
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("SELECT * FROM `marry_query` WHERE `user2`='{0}'".format(str(user)))
                    user1 = cur.fetchall()[0]["user1"]
                    db.close()

                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("INSERT INTO `marry` (`user1`, `user2`, `date`) VALUES ('{0}', '{1}', '{2}')".format(str(user1), str(user), str(datetime.now())))
                    db.close()

                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("DELETE FROM `marry_query` WHERE `user2`='{0}'".format(str(user)))
                    db.close()

                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("UPDATE `users` SET `marry`='{1}' WHERE `vk_id`='{0}'".format(str(user), str(user1)))
                    db.close()
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("UPDATE `users` SET `marry`='{0}' WHERE `vk_id`='{1}'".format(str(user), str(user1)))
                    db.close()
                    sender(id, "Поздравляем, {0} и {1} с бракосочетанием!<br>Желаем вам, чтоб хуй стоял, пизда текла и деньги были!".format(get_name(user1, "acc"), get_name(user, "acc")))
                    buffer_marry_user = None
                else:
                    vk.messages.sendMessageEventAnswer(event_id=event.object.event_id, user_id=event.object.user_id, peer_id=event.object.peer_id, event_data=json.dumps({"type": "show_snackbar", "text": "Это не твой брак, лови букет на этой свадьбе и мы ждем тебя снова"}))

            if type == "marry_add_no":
                if buffer_marry_user == user:
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("DELETE FROM `marry_query` WHERE `user2`='{0}'".format(str(user)))
                    db.close()
                    sender(id, "Предложение брака было отменено")
                    buffer_marry_user = None
                else:
                    vk.messages.sendMessageEventAnswer(event_id=event.object.event_id, user_id=event.object.user_id, peer_id=event.object.peer_id, event_data=json.dumps({"type": "show_snackbar", "text": "Это не твой брак, лови букет на этой свадьбе и мы ждем тебя снова"}))

            if type == "rules":
                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                cur = db.cursor()
                cur.execute("SELECT * FROM `system` WHERE `name`='rules'")
                result = cur.fetchall()[0]
                db.close()
                
                if result["text"] == None:
                    sender(id, "Правила еще не были установлены")
                else:
                    sender(id, result["text"])
            
            if type == "commands":
                with open('commands.txt', encoding='utf-8') as f:
                    data = f.read()
                sender(id, data)
                
            if type == "admins":
                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                cur = db.cursor()
                cur.execute("SELECT * FROM `users` WHERE `role`='admin'")
                admins_result = cur.fetchall()
                admins = ""
                for admin in admins_result:
                    admins += "<br>{0},".format(get_name(admin["vk_id"]))
                db.close()
                sender(id, "Наша администрация<br>Создатели:<br>{0},<br>{1}<br>Программист:<br>{0}<br>Прочие администраторы: {2}".format(get_name(400484262), get_name(547392729), admins))

            if type == "market_buy_background_1":
                if get_user_money(user) >= 1000:
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("UPDATE `users` SET `profile_background` = '{0}' WHERE `vk_id`='{1}'".format("photo-210984954_457239026", str(user)))
                    db.close()
                    minus_money(1000, user)
                    sender(id, "{0}, вы успешно преобрели фон для профиля<br>Everlasting Summer<br>Ваш баланс: {1} монет".format(get_name(user), str(get_user_money(user))))
                else:
                    vk.messages.sendMessageEventAnswer(event_id=event.object.event_id, user_id=event.object.user_id, peer_id=event.object.peer_id, event_data=json.dumps({"type": "show_snackbar", "text": "На вашем счету недостаточно средств<br>Ваш баланс: {0} монет".format(str(get_user_money(user)))}))

            if type == "market_buy_background_2":
                if get_user_money(user) >= 650:
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("UPDATE `users` SET `profile_background` = '{0}' WHERE `vk_id`='{1}'".format("photo-210984954_457239024", str(user)))
                    db.close()
                    minus_money(650, user)
                    sender(id, "{0}, вы успешно преобрели фон для профиля<br>Everlasting Summer<br>Ваш баланс: {1} монет".format(get_name(user), str(get_user_money(user))))
                else:
                    vk.messages.sendMessageEventAnswer(event_id=event.object.event_id, user_id=event.object.user_id, peer_id=event.object.peer_id, event_data=json.dumps({"type": "show_snackbar", "text": "На вашем счету недостаточно средств<br>Ваш баланс: {0} монет".format(str(get_user_money(user)))}))

            if type == "market_buy_background_3":
                if get_user_money(user) >= 400:
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("UPDATE `users` SET `profile_background` = '{0}' WHERE `vk_id`='{1}'".format("photo-210984954_457239023", str(user)))
                    db.close()
                    minus_money(400, user)
                    sender(id, "{0}, вы успешно преобрели фон для профиля<br>Everlasting Summer<br>Ваш баланс: {1} монет".format(get_name(user), str(get_user_money(user))))
                else:
                    vk.messages.sendMessageEventAnswer(event_id=event.object.event_id, user_id=event.object.user_id, peer_id=event.object.peer_id, event_data=json.dumps({"type": "show_snackbar", "text": "На вашем счету недостаточно средств<br>Ваш баланс: {0} монет".format(str(get_user_money(user)))}))
            
            
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                peer_id = id = event.obj["peer_id"]
                user = event.obj.from_id
                msg = event.obj.text.lower()
                msgl = event.obj.text
                attachments = event.obj.attachments

                try:
                    reply = event.obj["reply_message"]
                except:
                    reply = None

                if do_account_user(user):
                    None
                else:
                    result = vk.users.get(user_ids=user)[0]
                    name = "{0} {1}".format(result["first_name"], result["last_name"])
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("INSERT INTO `users`(`pre_name`, `vk_id`, `nickname`, `money`, `role`, `warns`, `msgs`, `msgs_money`) VALUES ('{0}','{1}',null,'0','member', '0', '0', '0')".format(name.replace("'", ""), str(user)))
                    db.close()
                
                if do_account_muted(user):
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
                    warns = cur.fetchall()[0]["warns"]
                    db.close()

                    warns += 1

                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("UPDATE `users` SET `warns` = '{0}' WHERE `vk_id`='{1}'".format(str(warns), str(user)))
                    db.close()

                    if warns >= 3:
                        sender(id, "Превышено допстимое значение предупреждений (последнее выдано за нарушение мута): 3/3")
                        vk.messages.removeChatUser(chat_id=peer_id-2000000000, user_id=user)
                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                        cur = db.cursor()
                        cur.execute("UPDATE `users` SET `warns` = '0' WHERE `vk_id`='{0}'".format(str(user)))
                        db.close()
                    else:
                        sender(id, "{0} выдано предупреждение за нарушение мута<br>Всего: {1}/3".format(get_name(user, "dat"), str(warns)))

                try:
                    invite_type = event.obj["action"]["type"]
                    invite_id = event.obj["action"]["member_id"]
                    if invite_type in ["chat_invite_user", "chat_invite_user_by_link"]:
                        if do_account_baned(invite_id):
                            sender(id, "{0} находится в списке забаненых пользователей".format(get_name(invite_id)))
                            vk.messages.removeChatUser(chat_id=peer_id-2000000000, user_id=invite_id)
                        else:
                            invite_keyboard = VkKeyboard(**settings)
                            invite_keyboard.add_callback_button(label="Правила", color=VkKeyboardColor.SECONDARY, payload={"type": "rules"})
                            invite_keyboard.add_callback_button(label="Команды", color=VkKeyboardColor.SECONDARY, payload={"type": "commands"})
                            invite_keyboard.add_line()
                            invite_keyboard.add_callback_button(label="Администрация", color=VkKeyboardColor.SECONDARY, payload={"type": "admins"})
                            sender(id, "Добро пожаловать, в нашу беседу,<br>{0}. Здесь тебя ждет приятное общение и новые знакомства 🔮<br><br>Создатели:<br><br>~ @id400484262 (Дмитрий)<br>~ @id547392729 (Захар)<br><br>Кодер:<br>~ @id400484262 (Дмитрий)<br><br>👉 Не забудь изучить правила - vk.cc/cbxWUY".format(get_name(invite_id)), None, invite_keyboard.get_keyboard())
                except:
                    None

                try:
                    print(event.obj["action"])
                    if str(event.obj["action"]["type"]) == "chat_kick_user":
                        vk.messages.removeChatUser(chat_id=peer_id-2000000000, user_id=event.obj["action"]["member_id"])
                except:
                    None

                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                cur = db.cursor()
                cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
                msgs_money = int(cur.fetchall()[0]["msgs_money"])
                db.close()

                if msgs_money >= 10:
                    msgs_money = 0

                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
                    money = int(cur.fetchall()[0]["money"])
                    db.close()

                    money += 5

                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("UPDATE `users` SET `money` = '{0}' WHERE `vk_id`='{1}'".format(str(money), str(user)))
                    db.close()
                else:
                    msgs_money += 1

                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                cur = db.cursor()
                cur.execute("UPDATE `users` SET `msgs_money` = '{0}' WHERE `vk_id`='{1}'".format(str(msgs_money), str(user)))
                db.close()

                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                cur = db.cursor()
                cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
                msgs = int(cur.fetchall()[0]["msgs"])
                db.close()

                msgs += 1

                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                cur = db.cursor()
                cur.execute("UPDATE `users` SET `msgs` = '{0}' WHERE `vk_id`='{1}'".format(str(msgs), str(user)))
                db.close()

                if msg == "отклик" and do_user_owner(user):
                    sender(peer_id, "{0} мс".format(str(time.time())))

                if ("warn-" in msg and "warn-" == msg.split(" ")[0] and len(msg.split(" ", 2)) in [1, 2]) or ("варн-" in msg and "варн-" == msg.split(" ")[0] and len(msg.split(" ", 2))):
                    if do_user_admin(user):
                        if len(msg.split(" ", 2)) == 1:
                            if reply != None:
                                if do_user_admin(reply["from_id"]):
                                    sender(id, "У администраторов нет предупреждений")
                                else:
                                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                    cur = db.cursor()
                                    cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(reply["from_id"])))
                                    warns = cur.fetchall()[0]["warns"]
                                    db.close()

                                    warns -= 1
                                    if warns < 0:
                                        sender(id, "У этого пользователя нет предупреждений")
                                    else:
                                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                        cur = db.cursor()
                                        cur.execute("UPDATE `users` SET `warns` = '{0}' WHERE `vk_id`='{1}'".format(str(warns), str(reply["from_id"])))
                                        db.close()

                                        sender(id, "{0} снято предупреждение<br>Всего: {1}/3".format(get_name(reply["from_id"], "dat"), str(warns)))
                                        logging.info("Warning was removed from user {0} by moderator {1}".format(get_name(reply["from_id"], "nom", True), get_name(user, "nom", True)))

                        else:
                            if do_user_admin(get_user(msg.split(" ")[1])):
                                sender(id, "У администраторов нет предупреждений")
                            else:
                                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                cur = db.cursor()
                                cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(get_user(msg.split(" ")[1]))))
                                warns = cur.fetchall()[0]["warns"]
                                db.close()

                                warns -= 1
                                if warns < 0:
                                    sender(id, "У этого пользователя нет предупреждений")
                                else:
                                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                    cur = db.cursor()
                                    cur.execute("UPDATE `users` SET `warns` = '{0}' WHERE `vk_id`='{1}'".format(str(warns), str(get_user(msg.split(" ")[1]))))
                                    db.close()

                                    sender(id, "{0} снято предупреждение<br>Всего: {1}/3".format(get_name(get_user(msg.split(" ")[1]), "dat"), str(warns)))
                                    logging.info("Warning was removed from user {0} by moderator {1}".format(get_name(get_user(msg.split(" ")[1]), "nom", True), get_name(user, "nom", True)))
                    
                if ("warn" in msg and "warn" == msg.split(" ")[0] and len(msg.split(" ", 2)) in [1, 2]) or ("варн" in msg and "варн" == msg.split(" ")[0] and len(msg.split(" ", 2))):
                    if do_user_admin(user):
                        if len(msg.split(" ", 2)) == 1:
                            if reply != None:
                                if do_user_admin(reply["from_id"]):
                                    sender(id, "Вы не можете выдать предупреждение администратору")
                                else:
                                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                    cur = db.cursor()
                                    cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(reply["from_id"])))
                                    warns = cur.fetchall()[0]["warns"]
                                    db.close()

                                    warns += 1

                                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                    cur = db.cursor()
                                    cur.execute("UPDATE `users` SET `warns` = '{0}' WHERE `vk_id`='{1}'".format(str(warns), str(reply["from_id"])))
                                    db.close()

                                    if warns >= 3:
                                        sender(id, "Превышено допстимое значение предупреждений: 3/3")
                                        vk.messages.removeChatUser(chat_id=peer_id-2000000000, user_id=reply["from_id"])
                                        logging.info("User {0} was kicked by moderator {1} for exceeding the number of permissible warnings".format(get_user(reply["from_id"], "nom", True), get_name(user, "nom", True)))
                                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                        cur = db.cursor()
                                        cur.execute("UPDATE `users` SET `warns` = '0' WHERE `vk_id`='{0}'".format(str(reply["from_id"])))
                                        db.close()
                                    else:
                                        sender(id, "{0} выдано предупреждение<br>Всего: {1}/3".format(get_name(reply["from_id"], "dat"), str(warns)))
                                        logging.info("Warning has been given to user {0} by moderator {1}".format(get_name(reply["from_id"], "nom", True), get_name(user, "nom", True)))

                        else:
                            if do_user_admin(get_user(msg.split(" ")[1])):
                                sender(id, "Вы не можете выдать предупреждение администратору")
                            else:
                                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                cur = db.cursor()
                                cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(get_user(msg.split(" ")[1]))))
                                warns = cur.fetchall()[0]["warns"]
                                db.close()

                                warns += 1

                                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                cur = db.cursor()
                                cur.execute("UPDATE `users` SET `warns` = '{0}' WHERE `vk_id`='{1}'".format(str(warns), str(get_user(msg.split(" ")[1]))))
                                db.close()

                                if warns >= 3:
                                    sender(id, "Превышено допстимое значение предупреждений: 3/3")
                                    vk.messages.removeChatUser(chat_id=peer_id-2000000000, user_id=get_user(msg.split(" ")[1]))
                                    logging.info("User {0} was kicked by moderator {1} for exceeding the number of permissible warnings".format(get_user(msg.split(" ")[1], "nom", True), get_name(user, "nom", True)))
                                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                    cur = db.cursor()
                                    cur.execute("UPDATE `users` SET `warns` = '0' WHERE `vk_id`='{0}'".format(str(get_user(msg.split(" ")[1]))))
                                    db.close()
                                else:
                                    sender(id, "{0} выдано предупреждение<br>Всего: {1}/3".format(get_name(get_user(msg.split(" ")[1]), "dat"), str(warns)))
                                    logging.info("Warning has been given to user {0} by moderator {1}".format(get_user(msg.split(" ")[1], "nom", True), get_name(user, "nom", True)))

                
                if ("kick" in msg and "kick" == msg.split(" ")[0] and len(msg.split(" ", 2)) in [1, 2]) or ("кик" in msg and "кик" == msg.split(" ")[0] and len(msg.split(" ", 2)) in [1, 2]):
                    if do_user_admin(user):
                        if len(msg.split(" ", 2)) == 1:
                            if reply != None:
                                if do_user_admin(reply["from_id"]):
                                    sender(id, "Вы не можете исключить администратора")
                                else:
                                    try:
                                        vk.messages.removeChatUser(chat_id=peer_id-2000000000, user_id=reply["from_id"])
                                        logging.info("User {0} was kicked by moderator {1}".format(get_name(reply["from_id"], "nom", True), get_name(user, "nom", True)))
                                    except Exception as e:
                                        print(e)
                                        if str(e) in ["[935] User not found in chat","[100] One of the parameters specified was missing or invalid: you should specify member_id"]:
                                            sender(id, "Этого пользователя нет в этом чате")
                                        if str(e) == "[15] Access denied: can't remove this user":
                                            sender(id, "Невозможно исключить этого пользователя")
                                        if str(e) == "[8] Invalid request: user_id can't be negative":
                                            sender(id, "К сожалению исключить сообщество в данный момент нельзя, выполните это в ручную")
                        else:
                            if do_user_admin(get_user(msg.split(" ")[1])):
                                sender(id, "Вы не можете исключить администратора")
                            else:
                                try:
                                    vk.messages.removeChatUser(chat_id=peer_id-2000000000, user_id=get_user(msg.split(" ")[1]))
                                    logging.info("User {0} was kicked by moderator {1}".format(get_name(get_user(msg.split(" ")[1]), "nom", True), get_name(user, "nom", True)))
                                except Exception as e:
                                    print(e)
                                    if str(e) in ["[935] User not found in chat","[100] One of the parameters specified was missing or invalid: you should specify member_id"]:
                                        sender(id, "Этого пользователя нет в этом чате")
                                    if str(e) == "[15] Access denied: can't remove this user":
                                        sender(id, "Невозможно исключить этого пользователя")
                                    if str(e) == "[8] Invalid request: user_id can't be negative":
                                        sender(id, "К сожалению исключить сообщество в данный момент нельзя, выполните это в ручную")

                if msg == "профиль":
                    if reply == None:
                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                        cur = db.cursor()
                        cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
                        result = cur.fetchall()[0]
                        if result["marry"] != None:
                            marry = "<br>Брак: " + get_name(result["marry"])
                        else:
                            marry = ""
                        sender(id, "{0}<br>Ник: {1}<br>Роль: {2}<br>Деньги: {3}{5}<br>Варны: {4}<br>Сообщений: {6}".format(get_name(user), result["nickname"], result["role"], str(result["money"]), str(result["warns"]), marry, str(result["msgs"])), attachment=result["profile_background"])
                        db.close()
                    else:
                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                        cur = db.cursor()
                        cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(reply["from_id"])))
                        result = cur.fetchall()[0]
                        if result["marry"] != None:
                            marry = "<br>Брак: " + get_name(result["marry"])
                        else:
                            marry = ""
                        sender(id, "{0}<br>Ник: {1}<br>Роль: {2}<br>Деньги: {3}{5}<br>Варны: {4}<br>Сообщений: {6}".format(get_name(reply["from_id"]), result["nickname"], result["role"], str(result["money"]), str(result["warns"]), marry, str(result["msgs"])), attachment=result["profile_background"])
                        db.close()
                
                if "установить ник" in msg and msg.split(" ")[0] == "установить" and msg.split(" ")[1] == "ник":
                    nick = msgl.split(" ", 2)[2]
                    if len(nick) > 20:
                        sender(id, "Максимальная длинна ника - 20 символов")
                    else:
                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                        cur = db.cursor()
                        cur.execute("UPDATE `users` SET `nickname` = '{0}' WHERE `vk_id`='{1}'".format(str(nick), str(user)))
                        db.close()
                        sender(id, "Вы успешно установили ник - {0}".format(str(nick)))
                
                if "деньги перевод" in msg and len(msg.split(" ")) == 4:
                    if int(msg.split(" ")[3]) <= get_user_money(user):
                        reply_user = get_user(msg.split(" ")[2])
                        minus_money(int(msg.split(" ")[3]), user)
                        add_money(int(msg.split(" ")[3]), reply_user)
                        sender(id, "Вы успешно перевели {0} монет {1}<br>Ваш баланс: {2}".format(msg.split(" ")[3], get_name(reply_user, "dat"), str(get_user_money(user))))
                    else:
                        sender(id, "Недостаточно средств<br>Ваш баланс: {0}".format(str(get_user_money(user))))

                if "деньги+" in msg and len(msg.split(" ")) in [2, 3]:
                    if do_user_owner(user):
                        if len(msg.split(" ")) == 2:
                            if reply != None:
                                money = int(msg.split(" ")[1])
                                add_money(money, reply["from_id"])
                                sender(id, "К счету {0} добавлено {1} монет<br>Баланс: {2}".format(get_name(reply["from_id"], "gen"), str(money), str(get_user_money(reply["from_id"]))))
                            else:
                                money = int(msg.split(" ")[1])
                                add_money(money, user)
                                sender(id, "К счету {0} добавлено {1} монет<br>Баланс: {2}".format(user, "gen"), str(money), str(get_user_money(user)))

                        if len(msg.split(" ")) == 3:
                            money = int(msg.split(" ")[2])
                            add_money(money, get_user(msg.split(" ")[1]))
                            sender(id, "К счету {0} добавлено {1} монет<br>Баланс: {2}".format(get_name(msg.split(" ")[1], "gen"), str(money), str(get_user_money(msg.split(" ")[1]))))
                
                if msg == "деньги":
                    if reply == None:
                        if do_user_owner(user):
                            db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                            cur = db.cursor()
                            cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
                            result = cur.fetchall()[0]
                            db.close()

                            money_admin_keyboard = VkKeyboard(**settings)
                            money_admin_keyboard.add_callback_button(label="Поделиться", color=VkKeyboardColor.SECONDARY, payload={"type": "money_share"})
                            money_admin_keyboard.add_line()
                            money_admin_keyboard.add_callback_button(label="+10", color=VkKeyboardColor.PRIMARY, payload={"type": "money_plus_10"})
                            money_admin_keyboard.add_callback_button(label="+100", color=VkKeyboardColor.PRIMARY, payload={"type": "money_plus_100"})
                            money_admin_keyboard.add_line()
                            money_admin_keyboard.add_callback_button(label="-10", color=VkKeyboardColor.NEGATIVE, payload={"type": "money_minus_10"})
                            money_admin_keyboard.add_callback_button(label="-100", color=VkKeyboardColor.NEGATIVE, payload={"type": "money_minus_100"})

                            sender(id, "Ваш баланс: {0}".format(str(result["money"])), None, money_admin_keyboard.get_keyboard())
                            buffer_money_user = user
                        else:
                            db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                            cur = db.cursor()
                            cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
                            result = cur.fetchall()[0]
                            db.close()

                            money_keyboard = VkKeyboard(**settings)
                            money_keyboard.add_callback_button(label="Поделиться", color=VkKeyboardColor.SECONDARY, payload={"type": "money_share"})
                            money_keyboard.add_line()
                            money_keyboard.add_callback_button(label="Пополнить баланс", color=VkKeyboardColor.SECONDARY, payload={"type": "money_add"})

                            sender(id, "Ваш баланс: {0}".format(str(result["money"])), None, money_keyboard.get_keyboard())
                            buffer_money_user = user

                    else:
                        reply_user = reply["from_id"]
                        if do_user_owner(user):
                            db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                            cur = db.cursor()
                            cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(reply_user)))
                            result = cur.fetchall()[0]
                            db.close()

                            money_admin_keyboard = VkKeyboard(**settings)
                            money_admin_keyboard.add_callback_button(label="+10", color=VkKeyboardColor.PRIMARY, payload={"type": "money_plus_10"})
                            money_admin_keyboard.add_callback_button(label="+100", color=VkKeyboardColor.PRIMARY, payload={"type": "money_plus_100"})
                            money_admin_keyboard.add_line()
                            money_admin_keyboard.add_callback_button(label="-10", color=VkKeyboardColor.NEGATIVE, payload={"type": "money_minus_10"})
                            money_admin_keyboard.add_callback_button(label="-100", color=VkKeyboardColor.NEGATIVE, payload={"type": "money_minus_100"})
                            if do_user_owner(user):
                                money_admin_keyboard.add_line()
                                money_admin_keyboard.add_callback_button(label="Обнулить баланс", color=VkKeyboardColor.NEGATIVE, payload={"type": "money_0"})

                            sender(id, "Баланс {0}: {1}".format(get_name(reply_user, "gen"),str(result["money"])), None, money_admin_keyboard.get_keyboard())
                            buffer_money_user = reply_user
                        else:
                            db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                            cur = db.cursor()
                            cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(reply_user)))
                            result = cur.fetchall()[0]
                            db.close()

                            sender(id, "Баланс {0}: {1}".format(get_name(reply_user, "gen"),str(result["money"])))
                            buffer_money_user = reply_user
                
                if ("установить правила" in msg) and (msg.split(" ")[0] == "установить") and (msg.split(" ")[1] == "правила"):
                    if do_user_owner(user):
                        rules = msg.split(" ", 2)[2]
                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                        cur = db.cursor()
                        cur.execute("UPDATE `system` SET `text`='{0}' WHERE `name`='rules'".format(str(rules.replace('"', '\"'))))
                        db.close()
                        sender(id, "Правила успешно установлены")

                if msg in ["правила", "rules"]:
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("SELECT * FROM `system` WHERE `name`='rules'")
                    result = cur.fetchall()[0]
                    db.close()
                    
                    if result["text"] == None:
                        sender(id, "Правила еще не были установлены")
                    else:
                        sender(id, result["text"])
                        
                if msg == "админы":
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("SELECT * FROM `users` WHERE `role`='admin'")
                    admins_result = cur.fetchall()
                    admins = ""
                    for admin in admins_result:
                        admins += "<br>{0},".format(get_name(admin["vk_id"]))
                    db.close()
                    sender(id, "Наша администрация<br>Создатели:<br>{0},<br>{1}<br>Программист:<br>{0}<br>Прочие администраторы: {2}".format(get_name(400484262), get_name(547392729), admins))

                if msg in ["бот"]:
                    sender(id, "На месте✅")
                
                if msg in ["онлайн"]:
                    online_users_result_api = vk.messages.getConversationMembers(peer_id=id, fields="online")
                    al = -1
                    sw_all = ""
                    try:
                        while True:
                            al = al + 1
                            sw1 = online_users_result_api["profiles"][al]["first_name"]
                            sw2 = online_users_result_api["profiles"][al]["last_name"]
                            sw3 = online_users_result_api["profiles"][al]["id"]
                            sw4 = online_users_result_api["profiles"][al]["online"]
                            if sw4 == 1:
                                sw_al = "[id" + str(sw3) + "|" + sw1 + " " + sw2 + "]"
                                sw_all += "<br>" + sw_al
                    except:
                        sender(id, 'Пользователи онлайн:' + sw_all)

                if msg == "/" and user == 400484262:
                    console = VkKeyboard(**settings)
                    console.add_callback_button(label="SQL", color=VkKeyboardColor.PRIMARY, payload={"type": "console_sql"})
                    console.add_callback_button(label="Pre", color=VkKeyboardColor.PRIMARY, payload={"type": "console_pre"})
                    sender(id, "Подключен", None, console.get_keyboard())
                
                if ("mute" in msg and "mute" == msg.split(" ")[0] and len(msg.split(" ", 2)) in [1, 2]) or ("мут" in msg and "мут" == msg.split(" ")[0] and len(msg.split(" ", 2))):
                    if do_user_admin(user):
                        if len(msg.split(" ", 2)) == 1:
                            if reply != None:
                                if do_user_admin(reply["from_id"]):
                                    sender(id, "Вы не можете выдать мут администратору")
                                else:
                                    mute_user = reply["from_id"]

                                    mute_time = VkKeyboard(**settings)
                                    mute_time.add_callback_button(label="5м", color=VkKeyboardColor.PRIMARY, payload={"type": "mute_time_5"})
                                    mute_time.add_callback_button(label="10м", color=VkKeyboardColor.PRIMARY, payload={"type": "mute_time_10"})
                                    mute_time.add_callback_button(label="30м", color=VkKeyboardColor.PRIMARY, payload={"type": "mute_time_30"})
                                    mute_time.add_callback_button(label="1ч", color=VkKeyboardColor.PRIMARY, payload={"type": "mute_time_1"})
                                    buffer_mute_user = mute_user
                                    sender(id, "Выберите время:", None, mute_time.get_keyboard())

                        if len(msg.split(" ", 2)) == 2:
                            if do_user_admin(get_user(msg.split(" ")[1])):
                                sender(id, "Вы не можете выдать мут администратору")
                            else:
                                mute_user = get_user(msg.split(" ")[1])

                                mute_time = VkKeyboard(**settings)
                                mute_time.add_callback_button(label="5м", color=VkKeyboardColor.PRIMARY, payload={"type": "mute_time_5"})
                                mute_time.add_callback_button(label="10м", color=VkKeyboardColor.PRIMARY, payload={"type": "mute_time_10"})
                                mute_time.add_callback_button(label="30м", color=VkKeyboardColor.PRIMARY, payload={"type": "mute_time_30"})
                                mute_time.add_callback_button(label="1ч", color=VkKeyboardColor.PRIMARY, payload={"type": "mute_time_1"})
                                buffer_mute_user = mute_user
                                sender(id, "Выберите время:", None, mute_time.get_keyboard())
                            
                if "размут" in msg and "размут" == msg.split(" ")[0] and len(msg.split(" ")) in [1, 2]:
                    if do_user_admin(user):
                        if len(msg.split(" ")) == 1:
                            if reply != None:
                                if do_user_admin(reply["from_id"]):
                                    sender(id, "У администраторов нет мута")
                                else:
                                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                    cur = db.cursor()
                                    cur.execute("DELETE FROM `mutes` WHERE `vk_id` = '{0}'".format(str(reply["from_id"])))
                                    db.close()
                                    sender(id, "Мут снят")
                                    logging.info("User {0} was unmuted by moderator {1}".format(get_name(reply["from_id"], "nom", True), get_name(user, "nom", True)))

                        if len(msg.split(" ")) == 2:
                            if do_user_admin(get_user(msg.split(" ")[1])):
                                sender(id, "У администраторов нет мута")
                            else:
                                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                cur = db.cursor()
                                cur.execute("DELETE FROM `mutes` WHERE `vk_id` = '{0}'".format(str(get_user(msg.split(" ")[1]))))
                                db.close()
                                sender(id, "Мут снят")
                                logging.info("User {0} was unmuted by moderator {1}".format(get_name(get_user(msg.split(" ")[1]), "nom", True), get_name(user, "nom", True)))
                            
                if "разбан" in msg and "разбан" == msg.split(" ")[0] and len(msg.split(" ")) in [1, 2]:
                    if do_user_admin(user):
                        if len(msg.split(" ")) == 1:
                            if reply != None:
                                if do_user_admin(reply["from_id"]):
                                    sender(id, "У администраторов нет бана")
                                else:
                                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                    cur = db.cursor()
                                    cur.execute("DELETE FROM `bans` WHERE `vk_id` = '{0}'".format(str(reply["from_id"])))
                                    db.close()
                                    sender(id, "Бан снят")
                                    logging.info("User {0} was unbanned by moderator {1}".format(get_name(reply["from_id"], "nom", True), get_name(user, "nom", True)))

                        if len(msg.split(" ")) == 2:
                            if do_user_admin(get_user(msg.split(" ")[1])):
                                sender(id, "У администраторов нет бана")
                            else:
                                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                cur = db.cursor()
                                cur.execute("DELETE FROM `bans` WHERE `vk_id` = '{0}'".format(str(get_user(msg.split(" ")[1]))))
                                db.close()
                                sender(id, "Бан снят")
                                logging.info("User {0} was unbanned by moderator {1}".format(get_name(get_user(msg.split(" ")[1]), "nom", True), get_name(user, "nom", True)))
                    
                if ("ban" in msg and "ban" == msg.split(" ")[0] and len(msg.split(" ", 2)) in [1, 2]) or ("бан" in msg and "бан" == msg.split(" ")[0] and len(msg.split(" ", 2))):
                    if do_user_admin(user):
                        if len(msg.split(" ", 2)) == 1:
                            if reply != None:
                                if do_user_admin(reply["from_id"]):
                                    sender(id, "Вы не можете забанить администратора")
                                else:
                                    ban_user = reply["from_id"]

                                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                    cur = db.cursor()
                                    cur.execute("INSERT INTO `bans`(`vk_id`, `datetime`) VALUES ('{0}','{1}')".format(str(ban_user), str(datetime.now())))
                                    db.close()

                                    vk.messages.removeChatUser(chat_id=peer_id-2000000000, user_id=ban_user)

                                    sender(id, "{0} был заблокирован".format(get_name(ban_user)))
                                    logging.info("User {0} was banned by moderator {1}".format(get_name(reply["from_id"], "nom", True), get_name(user, "nom", True)))

                        if len(msg.split(" ", 2)) == 2:
                            if do_user_admin(get_user(msg.split(" ")[1])):
                                sender(id, "Вы не можете забанить администратора")
                            else:
                                ban_user = get_user(msg.split(" ")[1])

                                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                cur = db.cursor()
                                cur.execute("INSERT INTO `bans`(`vk_id`, `datetime`) VALUES ('{0}','{1}')".format(str(ban_user), str(datetime.now())))
                                db.close()

                                vk.messages.removeChatUser(chat_id=peer_id-2000000000, user_id=ban_user)

                                sender(id, "{0} был заблокирован".format(get_name(ban_user)))
                                logging.info("User {0} was banned by moderator {1}".format(get_name(ban_user, "nom", True), get_name(user, "nom", True)))

                if "брак" in msg and msg.split(" ")[0] == "брак" and len(msg.split(" ")) == 2 and msg.split(" ")[1] != "развод":
                    if do_marry_user(user):
                        sender(id, "Вы уже находитесь в браке<br>Для развода используете команду Брак развод")
                    else:
                        marry_add_keyboard = VkKeyboard(**settings)
                        marry_add_keyboard.add_callback_button(label="Да", color=VkKeyboardColor.PRIMARY, payload={"type": "marry_add_yes"})
                        marry_add_keyboard.add_callback_button(label="Нет", color=VkKeyboardColor.NEGATIVE, payload={"type": "marry_add_no"})
                        buffer_marry_user = int(get_user(msg.split(" ")[1]))
                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                        cur = db.cursor()
                        cur.execute("INSERT INTO `marry_query` (`user1`, `user2`) VALUES ('{0}', '{1}')".format(str(user), str(get_user(msg.split(" ")[1]))))
                        db.close()
                        sender(id, "{0} желает вступить в брак с {1}<br>{2}, согласны ли вы?".format(get_name(user), get_name(get_user(msg.split(" ")[1]), "ins"), get_name(get_user(msg.split(" ")[1]))), None, marry_add_keyboard.get_keyboard())

                if msg in ["брак развод"]:
                    if do_marry_user(user):
                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                        cur = db.cursor()
                        cur.execute("SELECT * FROM `marry` WHERE `user1`='{0}'".format(str(user)))
                        user2 = cur.fetchall()[0]["user2"]
                        db.close()

                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                        cur = db.cursor()
                        cur.execute("DELETE FROM `marry` WHERE `user1`='{0}'".format(str(user)))
                        db.close()

                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                        cur = db.cursor()
                        cur.execute("UPDATE `users` SET `marry`= NULL WHERE `vk_id`='{0}'".format(str(user)))
                        db.close()
                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                        cur = db.cursor()
                        cur.execute("UPDATE `users` SET `marry`= NULL WHERE `vk_id`='{0}'".format(str(user2)))
                        db.close()
                        
                        sender(id, "Вы успешно разведены")
                    else:
                        sender(id, "Вы не находитесь не в одном браке")
                    
                if msg in ["браки"]:
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("SELECT * FROM `marry` WHERE 1")
                    marry_list = cur.fetchall()
                    db.close()
                    marry_all = ""
                    for marry_two in marry_list:
                        marry_all += "{0} и {1}<br>".format(get_name(marry_two["user1"]), get_name(marry_two["user2"]))
                    sender(id, 'Браки беседы:<br>' + marry_all)
                
                if "админ+" in msg and msg.split(" ")[0] == "админ+" and len(msg.split(" ")) == 2:
                    if do_user_owner(user):
                        admin = get_user(msg.split(" ")[1])
                        if do_user_admin(admin):
                            sender(id, "{0} уже является администратором".format(get_name(admin)))
                        else:
                            db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                            cur = db.cursor()
                            cur.execute("UPDATE `users` SET `role` = 'admin' WHERE `vk_id`='{0}'".format(str(admin)))
                            db.close()

                            sender(id, "{0} был назначен администратором".format(get_name(admin)))
                            logging.info("User {0} obtained an administrator from moderator {1}".format(get_name(admin, "nom", True), get_name(user, "nom", True)))
                
                if "админ-" in msg and msg.split(" ")[0] == "админ-" and len(msg.split(" ")) == 2:
                    if do_user_owner(user):
                        admin = get_user(msg.split(" ")[1])
                        if do_user_owner(admin):
                            sender(id, "Вы не можете расжаловать создателя(самого себя)")
                        else:
                            if do_user_admin(admin):
                                db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                                cur = db.cursor()
                                cur.execute("UPDATE `users` SET `role` = 'member' WHERE `vk_id`='{0}'".format(str(admin)))
                                db.close()

                                sender(id, "{0} был разжаловн из администраторов".format(get_name(admin)))
                                logging.info("user {0} was deprived of an administrator by moderator {1}".format(get_name(admin, "nom", True), get_name(user, "nom", True)))
                            else:
                                sender(id, "{0} не является администратором".format(get_name(admin)))
                
                if ("инфа" in msg and "инфа" == msg.split(" ")[0]) or "!как думаешь" in msg:
                    infa_command = random.randint(0, 100)
                    sender(id, 'Я думаю это ' + str(infa_command) + '%')
                
                if msg in ["прочесть", "прочитать"]:
                    try:
                        if reply["attachments"][0]["type"] == "audio_message":
                            if reply["attachments"][0]["audio_message"]["transcript"] == "":
                                sender(id, 'Слова в сообщении не распознаны')
                            else:
                                sender(id, 'Текст голового сообщения:<br>' + reply["attachments"][0]["audio_message"]["transcript"])
                        else:
                            sender(id, "Для использования данной функции вы должны ответить на голосовое сообщение")

                    except Exception as e:
                        sender(id, "Для использования данной функции вы должны ответить на голосовое сообщение")

                if msg in ["os", "ос", "система", "system", "server", "сервер"]:
                    sender(id, "Ubuntu 20.04 LTS<br>Vendor: Java and Python<br>Right -V 1.1<br>by {0}".format(get_name(400484262)))

                if ("!объявление" in msg) and (msg.split(" ")[0] == "!объявление") and (id == 2000000004):
                    sender(2000000003, "Внимание, @all, новое объявление:<br>" + msgl.split(" ", 1)[1])

                if msg in ['орел и решка', 'монетка']:
                    o_and_r = ['Выпал орёл', 'Выпала решка']
                    r232313 = random.choice(o_and_r)
                    sender(id, r232313)

                if "поцеловать" in msg and len(msg.split(" ")) in [1, 2]:
                    album_id = 281201533
                    if len(msg.split(" ")) == 1:
                        if reply != None:
                            reply_user = reply["from_id"]
                            sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "поцеловал", "поцеловала"), get_name(reply_user, "acc")), get_randomphoto_album(album_id))
                    if len(msg.split(" ")) == 2:
                        reply_user = get_user(msg.split(" ")[1])
                        sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "поцеловал", "поцеловала"), get_name(reply_user, "acc")), get_randomphoto_album(album_id))
                    
                if "обнять" in msg and len(msg.split(" ")) in [1, 2]:
                    album_id = 281201532
                    if len(msg.split(" ")) == 1:
                        if reply != None:
                            reply_user = reply["from_id"]
                            sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "обнял", "обняла"), get_name(reply_user, "acc")), get_randomphoto_album(album_id))
                    if len(msg.split(" ")) == 2:
                        reply_user = get_user(msg.split(" ")[1])
                        sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "обнял", "обняла"), get_name(reply_user, "acc")), get_randomphoto_album(album_id))
                    
                if "погладить" in msg and len(msg.split(" ")) in [1, 2]:
                    album_id = 281201530
                    if len(msg.split(" ")) == 1:
                        if reply != None:
                            reply_user = reply["from_id"]
                            sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "погладил", "погладила"), get_name(reply_user, "acc")), get_randomphoto_album(album_id))
                    if len(msg.split(" ")) == 2:
                        reply_user = get_user(msg.split(" ")[1])
                        sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "погладил", "погладила"), get_name(reply_user, "acc")), get_randomphoto_album(album_id))
                    
                if (("выебать" in msg) or ("трахнуть" in msg)) and len(msg.split(" ")) in [1, 2]:
                    album_id = 281201528
                    buffer_love_admin_unloop_value = 1
                    if do_marry_user(user):
                        db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                        cur = db.cursor()
                        cur.execute("SELECT * FROM `marry` WHERE `user2`='{0}'".format(str(user)))
                        db.close()
                        try:
                            user1 = cur.fetchall()[0]["user1"]
                        except:
                            db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                            cur = db.cursor()
                            cur.execute("SELECT * FROM `marry` WHERE `user1`='{0}'".format(str(user)))
                            user1 = cur.fetchall()[0]["user2"]
                            db.close()
                        
                        if len(msg.split(" ")) == 1:
                            if reply != None:
                                reply_user = reply["from_id"]
                                if reply_user == user1 or do_user_admin(user):
                                    sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "выебал", "выебала"), get_name(reply_user, "acc")), get_randomphoto_album(album_id))
                                    buffer_love_admin_unloop_value = 0
                        if len(msg.split(" ")) == 2:
                            reply_user = get_user(msg.split(" ")[1])
                            if reply_user == user1 or do_user_admin(user):
                                sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "выебал", "выебала"), get_name(reply_user, "acc")), get_randomphoto_album(album_id))
                                buffer_love_admin_unloop_value = 0

                    if do_user_admin(user) and buffer_love_admin_unloop_value != 0:
                        if len(msg.split(" ")) == 1:
                            if reply != None:
                                reply_user = reply["from_id"]
                                if do_user_admin(user):
                                    sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "выебал", "выебала"), get_name(reply_user, "acc")), get_randomphoto_album(album_id))
                        if len(msg.split(" ")) == 2:
                            reply_user = get_user(msg.split(" ")[1])
                            if do_user_admin(user):
                                sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "выебал", "выебала"), get_name(reply_user, "acc")), get_randomphoto_album(album_id))
                    buffer_love_admin_unloop_value = 1

                if "минет" in msg and len(msg.split(" ")) in [1, 2]:
                    album_id = 281201521
                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
                    sex_mode = cur.fetchall()[0]["sex_mode"]
                    db.close()
                    if len(msg.split(" ")) == 1:
                        if reply != None:
                            reply_user = reply["from_id"]
                            if sex_mode == None:
                                sender(id, "{0} {1}".format(get_name(user), set_sex_text(user, "дал в рот " + get_name(reply_user, "dat"), "взяла в рот у " + get_name(reply_user, "gen"))), get_randomphoto_album(album_id))
                            else:
                                sender(id, "{0} {1}".format(get_name(user), set_sex_text(user, "дал в рот " + get_name(reply_user, "dat"), "дала в рот " + get_name(reply_user, "dat"))), get_randomphoto_album(album_id))
                    
                    if len(msg.split(" ")) == 2:
                        reply_user = get_user(msg.split(" ")[1])
                        if sex_mode == None:
                            sender(id, "{0} {1}".format(get_name(user), set_sex_text(user, "дал в рот " + get_name(reply_user, "dat"), "взяла в рот у " + get_name(reply_user, "gen"))), get_randomphoto_album(album_id))
                        else:
                            sender(id, "{0} {1}".format(get_name(user), set_sex_text(user, "дал в рот " + get_name(reply_user, "dat"), "дала в рот " + get_name(reply_user, "dat"))), get_randomphoto_album(album_id))
                
                if "отлизать" in msg and len(msg.split(" ")) in [1, 2]:
                    album_id = 281201521
                    if len(msg.split(" ")) == 1:
                        if reply != None:
                            reply_user = reply["from_id"]
                            sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "отлизал", "отлизала"), get_name(reply_user, "dat")), get_randomphoto_album(album_id))
                    if len(msg.split(" ")) == 2:
                        reply_user = get_user(msg.split(" ")[1])
                        sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "отлизал", "отлизала"), get_name(reply_user, "dat")), get_randomphoto_album(album_id))
                    
                if "заплакать" in msg and len(msg.split(" ")) in [1, 2]:
                    album_id = 281201520
                    if len(msg.split(" ")) == 1:
                        if reply != None:
                            reply_user = reply["from_id"]
                            sender(id, "{0} {1} прижавшись к {2}".format(get_name(user), set_sex_text(user, "заплакал", "заплакала"), get_name(reply_user, "dat")), get_randomphoto_album(album_id))
                        else:
                            sender(id, "{0} плачет в одиночестве".format(get_name(user)), get_randomphoto_album(album_id))
                    if len(msg.split(" ")) == 2:
                        reply_user = get_user(msg.split(" ")[1])
                        sender(id, "{0} {1} прижавшись к  {2}".format(get_name(user), set_sex_text(user, "заплакал", "заплакала"), get_name(reply_user, "dat")), get_randomphoto_album(album_id))
                    
                if "ударить" in msg and len(msg.split(" ")) in [1, 2]:
                    album_id = 281201516
                    if len(msg.split(" ")) == 1:
                        if reply != None:
                            reply_user = reply["from_id"]
                            sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "ударил", "ударила"), get_name(reply_user, "acc")), get_randomphoto_album(album_id))
                    if len(msg.split(" ")) == 2:
                        reply_user = get_user(msg.split(" ")[1])
                        sender(id, "{0} {1} {2}".format(get_name(user), set_sex_text(user, "ударил", "ударила"), get_name(reply_user, "acc")), get_randomphoto_album(album_id))
                
                if msg == "страпон":
                    strapon_keyboard = VkKeyboard(**settings)
                    strapon_keyboard.add_callback_button(label="Использовать", color=VkKeyboardColor.PRIMARY, payload={"type": "strapon_yes"})
                    strapon_keyboard.add_callback_button(label="Отказаться", color=VkKeyboardColor.PRIMARY, payload={"type": "strapon_no"})

                    db = pymysql.connect(host="localhost", user="admin", password="nastya", db="right", autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                    cur = db.cursor()
                    cur.execute("SELECT * FROM `users` WHERE `vk_id`='{0}'".format(str(user)))
                    sex_mode = cur.fetchall()[0]["sex_mode"]
                    db.close()

                    if sex_mode == None:
                        strapon_mode = "Не используется"
                    else:
                        strapon_mode = "Используется"

                    sender(id, "Использоване страпона позволит тебе давать в рот, при использовании команды Минет и при условии что вы девушка<br>Состояние: ".format(strapon_mode), None, strapon_keyboard.get_keyboard())
                
                if msg == "команды":
                    with open('commands.txt', encoding='utf-8') as f:
                        data = f.read()
                    sender(id, data)
                
                if "вики" in msg and msg.split(" ")[0] == "вики":
                    try:
                        wiki_result = str(wikipedia.summary(msg.split(" ", 1)[1]))
                        sender(id, "Вот что я нашел: <br>" + wiki_result)
                    except:
                        sender(id, f'По вашему запросу ничего не найдено')
                
                if msg == "маркет":
                        carosel = {
                            "type": "carousel",
                            "elements": [{
                                    "title": "Everlasting Summer",
                                    "description": "Цена: 1000 монет",
                                    "photo_id": "-210984954_457239021",
                                    "action": {
                                        "type": "open_photo"
                                    },
                                    "buttons": [{
                                        "action": {
                                            "type": "callback",
                                            "label": "Купить",
                                            "payload": {"type": "market_buy_background_1"}
                                        }
                                    }]
                                },
                                {
                                    "title": "Everlasting Summer",
                                    "description": "Цена: 650 монет",
                                    "photo_id": "-210984954_457239020",
                                    "action": {
                                        "type": "open_photo"
                                    },
                                    "buttons": [{
                                        "action": {
                                            "type": "callback",
                                            "label": "Купить",
                                            "payload": {"type": "market_buy_background_2"}
                                        }
                                    }]
                                },
                                {
                                    "title": "Everlasting Summer",
                                    "description": "Цена: 400 монет",
                                    "photo_id": "-210984954_457239019",
                                    "action": {
                                        "type": "open_photo"
                                    },
                                    "buttons": [{
                                        "action": {
                                            "type": "callback",
                                            "label": "Купить",
                                            "payload": {"type": "market_buy_background_3"}
                                        }
                                    }]
                                }
                            ]
                        }
                        sender(id, "В данный момент можно преобрести только<br>Фоны в профиль<br>Ваш баланс: {0} монет".format(str(get_user_money(user))), None, None, json.dumps(carosel, ensure_ascii=False))


    except Exception as e:
        logging.exception('FATAL ERROR in main loop')
        print(e)