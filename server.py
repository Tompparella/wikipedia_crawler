#   Tommi Kunnari
#   17.4.2021
#   Wikipedia Crawler
#   Made as a final project for a university course on Distributed Systems.

from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
from datetime import date, datetime
import xml.etree.ElementTree as ET
import os
import wikipedia
import copy
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal
import sys

#server = SimpleXMLRPCServer(('127.0.0.1', 5000), logRequests=True, allow_none=True)
port = 5000
address = '127.0.0.1'

# Reference to the threaded server is taken from a suggestion made by the course assistant from https://stackoverflow.com/questions/53621682/multi-threaded-xml-rpc-python3-7-1
class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class Article:
    def __init__(self, title, prev):
        self.title = title
        self.prev = prev

class Loop:
    def __init__(self, loop, visited):
        self.loop = loop
        self.visited = visited



def get_articles(article_list):                                         # Finds the initial articles based on user input.
    print("{}: Searching wikipedia for '{}' and '{}'...".format(get_time(), article_list[0], article_list[1]))
    try:
        results = []
        for i in article_list:
            results.append(wikipedia.search(i))
        print("{}: Successfully searched wikipedia!".format(get_time()))
        return results
    except Exception as e:
        print("{}: An error has occurred while searching wikipedia: {}".format(get_time(), e))
        return e



def find_shortest_path(start,end):                                      # An RPC function that initializes the breadth-first-algorithm function.
    visited = []                    
    queue = []                 
    first = Article(start, [])
    visited.append(start)
    queue.append(first)
    loop = Loop(True, visited)
    print("\n{} --- Commencing a search on articles '{}' and '{}'...\n".format(get_time(),start,end))
    path = get_path(queue,end,True,loop)
    return path



def get_path(queue, end, threading, loop):                               # This my take on a threaded breadth-first-search algorithm. Due to wikipedias' connectedness, this is the best approach I could figure to querueing paths between articles.
    while loop.loop:                                                     # Reference for the initial algorithm taken from https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/ but highly modified to fit the needs for the program.
        try:
            curr = queue.pop(0)                                     
            #print("Path:", curr.prev, curr.title)
        except Exception as e:
            #print("{} --- Pop Error: {}".format(get_time(), e))
            pass
        try:                                                            # First call checks initial links for matches. If a match is not found, create threads for each initial link (to highly improve performance) to continue the loop.
            page = wikipedia.page(title=curr.title, auto_suggest=False) # Does not create any more threads after this, because of restrictions on concurrent requests given by wikipedia.
            links = page.links                                          # Ends all threads after finding one path, this being the shortest one. Has the chance of finding more than one path, but
            if (end in links):                                          # returns only one for consistent output.
                #print("Path found!")       
                loop.loop = False                                       # The function stores the boolean that determines the loop in an object. Since python normally only gives a reference to an objects' value, we
                curr.prev.append(curr.title)                            # can sort of use this as a trigger for all threads to end at the same time when finding a path in one thread.
                curr.prev.append(end)                                   #
                return curr.prev                                        # In a nutshell:
                                                                        # A thread finds a correct path -> object's boolean is changed to false -> all threads recieve a reference to the object's value, which is now false -> All threads finish.
            for i in links:
                if i not in loop.visited:
                    loop.visited.append(i)
                    n_prev = copy.deepcopy(curr.prev)
                    n_prev.append(curr.title)
                    a = Article(i, n_prev)
                    queue.append(a)
        except Exception as e:                                          # Exceptions only print an error, since wikipedia has a lot of dead links which throw errors. We can simply ignore these.
            print("{} --- Error: {}".format(get_time(), e))
            #loop.visited.append(curr.title)
            pass

        if threading:                                           # Start threads if parent function.
            threading = False
            executor = ThreadPoolExecutor()
            results = {executor.submit(get_path, [i],end, False, loop): i for i in queue}  

            return_path = []
            for f in as_completed(results):
                result = f.result()
                if result != None:                              # Empty returns are ignored. Assigns only the first found path as the result. Others are discarded, but still printed in server.
                    if return_path == []:
                        return_path = result
                    print("\n***********************************************\n{}\nResult:\n{}\n***********************************************\n".format(get_time(), result))
            print("\n************************************************\n     Process completed, threads joined.\n***********************************************\n")
            if return_path != []:
                return return_path
            else:
                return Exception



def get_time():                                                 # A helper function that gets current server time and foramts it.
    today = date.today().strftime("%d/%m/%Y")
    time = datetime.now().strftime("%H:%M:%S")
    timestamp = "[{} - {}]".format(today, time)
    return timestamp



def run_server(host=address, port=port):                        # Starts the server and handles request concurrency.
    server_addr = (host, port)
    server = SimpleThreadedXMLRPCServer(server_addr)

    server.register_function(get_articles)
    server.register_function(find_shortest_path)

    print('Server started!\nListening on {} port {}'.format(host, port))
    server.serve_forever()



def signal_handler(signal, frame):                              # Handles interruptions.
    print('{}: Quitting server'.format(get_time()))
    sys.exit(0)



signal.signal(signal.SIGINT, signal_handler)



if __name__ == '__main__':                                      # Starts the server on startup.
    run_server()

