import os
import time
import csv
import re
import ast
from datetime import date
from random import random

from dotenv import load_dotenv
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

from openai_request import chatgpt_reply, chatgpt_reply_premium, reply_audio, reply_dalle


load_dotenv()

app = Flask(__name__)
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)


def init_members():
    paid_members_txt = open("./paid_members.txt", 'r')
    list_free_users = [num.replace(".csv","") for num in os.listdir("./csvs/free/")]
    list_paid_users = ["whatsapp:" + line.replace("\n", "") for line in paid_members_txt.readlines()]
    list_free_users = [num for num in list_free_users if num not in list_paid_users]
    list_paid_users = list(set(list_paid_users))
    return list_free_users, list_paid_users


limit_free = 150 # 150 mots pour la limite free
list_free_users, list_paid_users = init_members()

message_premium = "Vous utilisez la version premium de What The Chat, merci pour votre confiance  ! Contactez-nous en cas de problème : \n \n hello@what-the-chat.com \n \n Vous pouvez gérer votre abonnement via ce lien : https://billing.stripe.com/p/login/9AQ9AVgHs9Ef7NmaEE"
message_cta = "\n\nPassez à l'abonnement premium pour profiter de What The Chat, on vous offre 7 jours pour essayer : \n\n🚀 En illimité \n🎙️ Posez vos questions en audio \n🏞️ Générez des images en 2 secondes (écrivez /image avant le message) \n😇 Sans publicités \n \nTravaillez, créez, apprenez, plus vite. Par ici : https://buy.stripe.com/bIY8x54Z2g067HWcMO \n \n🇬🇧 \nUpgrade your account for unlimited access to the Chat, voice notes support and image generation. \n \nhello@what-the-chat.com",
cta_sending_rate = 0.25
msg_premium_rate = 0.25


def get_data(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        # Skip the first row
        next(reader)
        # Extract data from the second row
        second_row = next(reader)
    return second_row


def update_current_conv_append(txt_file, msg):
    with open(txt_file, "r+") as f:
        current_conv = ast.literal_eval(f.read()[:])
        current_conv.append(msg)
        open(txt_file, "w").close()
    with open(txt_file, "r+") as f:
        f.write(str(current_conv))
    f.close()


def get_current_conv(txt_file):
    with open(txt_file, "r") as f:
        current_conv = ast.literal_eval(f.read()[:])
    f.close()
    return current_conv


def update_data(csv_file, usage):
    # Open the CSV file
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        rows = list(csvreader)

    # Update the last row's value
    rows[-1][-1] = usage

    # Save the updated CSV file
    with open(csv_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(rows)


@app.route('/')
def hello_world():
    list_free_users, list_paid_users = init_members()
    return "Number of free users : " + str(len(list_free_users)) + "\n" + "Number of paid users : " + str(len(list_paid_users))


@app.route('/message', methods=['POST'])
def reply():

    num_sender = request.form.get('From')
    message = request.form.get('Body').lower()

    #print(audio_path is not None)
    audio_path = request.form.get('MediaUrl0')
    print("Audio_path : ---------------- ", audio_path)

    list_free_users, list_paid_users = init_members()

    print("Free users :", list_free_users)
    print("Paid users :", list_paid_users)
    print("Number of free users :", len(list_free_users))
    print("Number of paid users :", len(list_paid_users))

    if (message or audio_path) and (num_sender in list_paid_users):

        if str(num_sender) + ".txt" not in os.listdir("./convs"):
            with open("./convs/" + str(num_sender) + ".txt", "w") as f:
                f.write(str([{"role": "system", "content": "You are a helpful assistant."}]))
                f.close()

        if "new chat" in message:

            client.messages.create(
                from_='whatsapp:+13159035087',
                body="New chat initialised..",
                to=num_sender
                )

        elif message.startswith("/image"):
            image_url = reply_dalle(message)
            client.messages.create(
                media_url=image_url,
                from_='whatsapp:+13159035087',
                body=message,
                to=num_sender
                )

        elif audio_path is not None:
            current_conv = get_current_conv("./convs/" + str(num_sender) + ".txt")
            txt_msg, completion = reply_audio(audio_path, current_conv)
            update_current_conv_append("./convs/" + str(num_sender) + ".txt", {"role": "user", "content": txt_msg})
            update_current_conv_append("./convs/" + str(num_sender) + ".txt", {"role": "assistant", "content":completion['choices'][0]['message']['content']}) # ajout du message à la conv
            print("About to send the message")
            print("Txt to send:", completion['choices'][0]['message']['content'])

            client.messages.create(
                from_='whatsapp:+13159035087',
                body=completion['choices'][0]['message']['content'],
                to=num_sender
                )
            print("Message sent")

        else:
            update_current_conv_append("./convs/" + str(num_sender) + ".txt", {"role": "user", "content": message})
            current_conv = get_current_conv("./convs/" + str(num_sender) + ".txt")
            completion = chatgpt_reply_premium(current_conv)
            update_current_conv_append("./convs/" + str(num_sender) + ".txt", {"role": "assistant", "content":completion['choices'][0]['message']['content']}) # ajout du message à la conv

            liste_mots = completion['choices'][0]['message']['content'].split(" ")
            taille_rep = len(liste_mots)
            print(taille_rep)

            if taille_rep < 200:
                client.messages.create(
                        from_='whatsapp:+13159035087',
                        body=completion['choices'][0]['message']['content'],
                        to=num_sender
                        )

            elif taille_rep > 200 and taille_rep < 400:
                messages = [' '.join(liste_mots[:200])] + [' '.join(liste_mots[200:400])]

                for msg in messages:
                    client.messages.create(
                            from_='whatsapp:+13159035087',
                            body=msg,
                            to=num_sender
                            )
                    time.sleep(2)

            elif taille_rep > 400 and taille_rep < 600:
                messages = [' '.join(liste_mots[:200])] + [' '.join(liste_mots[200:400])] + [' '.join(liste_mots[400:600])]

                for msg in messages:
                    client.messages.create(
                            from_='whatsapp:+13159035087',
                            body=msg,
                            to=num_sender
                            )
                    time.sleep(2)

            else:
                client.messages.create(
                        from_='whatsapp:+13159035087',
                        body="Réponse trop longue",
                        to=num_sender
                        )
            
            if random()<msg_premium_rate:
                client.messages.create(
                        from_='whatsapp:+13159035087',
                        body=message_premium,
                        to=num_sender
                        )                    
                print("Message premium")

    elif message and (num_sender not in list_paid_users):
        if num_sender not in list_free_users:
            with open("./csvs/free/" + num_sender + ".csv", mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Number', 'creation_date', 'Usage'])
                writer.writerow([num_sender, date.today(), 0])
            list_free_users.append(num_sender)

            with open("./convs/" + str(num_sender) + ".txt", "w") as f:
                f.write(str([{"role": "system", "content": "You are a helpful assistant."}]))
                f.close()

        csv_file = "./csvs/free/" + num_sender + ".csv"
        num, creation_date, usage = get_data(csv_file)
        usage = int(usage)

        if usage < limit_free:
            if "new chat" in message:
                with open("./convs/" + str(num_sender) + ".txt", "w") as f:
                    f.write(str([{"role": "system", "content": "You are a helpful assistant."}]))
                client.messages.create(
                    from_='whatsapp:+13159035087',
                    body="New chat initialised..",
                    to=num_sender
                    )
            elif message.startswith("/image"):
                client.messages.create(
                    from_='whatsapp:+13159035087',
                    body="La génération d'image n'est pas disponible dans la version gratuite. \n \nPassez à l'abonnement premium pour profiter de What The Chat, on vous offre 7 jours d'essai : : \n \n🚀 Nombre de mots illimité \n🎙️ Posez vos questions en audio \n🏞️ Générez des images en 2 secondes (écrivez /image avant le message) \n😇 Sans publicités \n \nTravaillez, créez, apprenez, plus vite. Par ici : https://buy.stripe.com/bIY8x54Z2g067HWcMO \n \n🇬🇧 \nImage generation isn't available on the free version. Upgrade your account for unlimited access to the Chat, voice messages support and image generation. \n \n📞 Contact : hello@what-the-chat.com",
                    to=num_sender
                    )

            else:
                update_current_conv_append("./convs/" + str(num_sender) + ".txt", {"role": "user", "content": message})
                current_conv = get_current_conv("./convs/" + str(num_sender) + ".txt")
                completion = chatgpt_reply(current_conv)
                update_current_conv_append("./convs/" + str(num_sender) + ".txt", {"role": "assistant", "content":completion['choices'][0]['message']['content']}) # ajout du message à la conv

                client.messages.create(
                        from_='whatsapp:+13159035087',
                        body=completion['choices'][0]['message']['content'],
                        to=num_sender
                        )

                if random()<cta_sending_rate:
                    client.messages.create(
                            from_='whatsapp:+13159035087',
                            body=message_cta,
                            to=num_sender
                            )                    
                    print("CTA")

                taille_rep = len(completion['choices'][0]['message']['content'].split(" "))
                usage += taille_rep
                usage = str(usage)
                update_data(csv_file, usage)
        else:
            client.messages.create(
                        from_='whatsapp:+13159035087',
                        body="Votre limite d'utilisation quotidienne de 150 mots a été atteinte. \n \nPassez à l'abonnement premium pour profiter de What The Chat, on vous offre 7 jours d'essai : \n \n🚀 En illimité \n🎙️ Posez vos questions en audio \n🏞️ Générez des images en 2 secondes (écrivez /image avant le message) \n😇 Sans publicités \n \nTravaillez, créez, apprenez, plus vite. Par ici : https://buy.stripe.com/bIY8x54Z2g067HWcMO \n \n🇬🇧 \nYou've reach your 150 free words for today. Upgrade your account for unlimited access to the Chat and image generation. \n \n📞 Contact : hello@what-the-chat.com",
                        to=num_sender
                        )

    return "Message sent"


if __name__ == "__main__":
    app.run=()
