#   Tommi Kunnari
#   17.4.2021
#   Wikipedia Crawler
#   Made as a final project for a university course on Distributed Systems.

from xmlrpc.client import ServerProxy
from datetime import date, datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys, signal

proxy = ServerProxy('http://localhost:5000')

def ui_loop():                                                                                    # This is the main UI-loop that takes user input.
    print("This program finds the shortest paths between two wikipedia articles.\nCtrl+C to quit\n")
    search1 = input("Enter article 1: ")
    search2 = input("Enter article 2: ")
    print("\nFetching articles based on input, please wait...")
    article_list = get_articles([search1,search2])

    if (article_list[0] == [] or article_list[1] == []):
        if article_list[0] == []:
            print("No articles found on '{}'.".format(search1))
        else:
            print("No articles found on '{}'.".format(search2))
        return

    print("\n1) ----- Entries on {}:\n{}\n\n2) ----- Entries on {}:\n{}\n".format(search1,article_list[0],search2,article_list[1]))
    print("Select the first article by index (starts from 0):")
    index1 = take_index(article_list[0])
    print("Select the second article by index (starts from 0):")
    index2 = take_index(article_list[1])
    
    article1 = article_list[0][index1]
    article2 = article_list[1][index2]
    print("You've chosen articles '{}' and '{}'. Find the shortest paths between these on wikipedia? (y/n):".format(article1, article2))
    while True:
        choice = input()
        if choice in ["y","Y"]:
            break
        elif choice in ["n", "N"]:
            print("\nProcedure aborted.\n")
            return
        else:
            print("Invalid choice.")
    find_shortest_path(article1, article2)



def take_index(articles):                                                      # A helper-function to ease taking user's desired article.
    while True:
            try:
                choice = int(input())
                articles[choice]
                return choice
            except:
                print("You gave an invalid index. The index has to be a round number (int) and be in range of the list. Try again.")



def find_shortest_path(a1,a2):                                              # Requests the server to start handling the search and provides user with transparency.
                                                                            # Also prints data referring to the seeked path.
    start = time.time()
    try:
        print("\nSearch in progres. This might take some time.\nPlease wait...\n")
        try:
            result = proxy.find_shortest_path(a1,a2)
            end = time.time()
            print("\n************************\nPath found!\n\nThis process required {} steps.\n\nTraversed articles: {}\n\nTime taken to complete: {} seconds\n************************\n".format(len(result)-1,result, end-start))
        except Exception as e:
            print("An error has occurred on the serverside: {}\nThis might be a disambiguation error, which means that either of given articles doesn't suffice.\nTry some other input.".format(e))
    except KeyboardInterrupt:
        print("Process interrupted.")
        exit(1)



def get_articles(article_list):                                             # Sends the server a request to find the initial articles.
    articles = proxy.get_articles(article_list)
    return articles


    
def get_time():                                                             # A helper function to get current system time and format it.
    today = date.today().strftime("%d/%m/%Y")
    time = datetime.now().strftime("%H:%M:%S")
    timestamp = "{} - {}".format(today, time)
    return timestamp



def signal_handler(signal, frame):                                          # Handles user interruptions.
    print('\n{}: Quitting client'.format(get_time()))
    sys.exit(0)



signal.signal(signal.SIGINT, signal_handler)



if __name__ == '__main__':                                                  # Starts the UI-loop on startup.
    print("Client started!\n")
    while(True):
        ui_loop()