## main.py 
import simpy
from DHT import DHT
from MessageLogger import MessageLogger 

def main():
    env = simpy.Environment()
    dht = DHT("", env)

    dht.run_simulation(until_time=250)

    # Affichage de l'état final de la DHT
    print(dht)


if __name__ == "__main__":
    main()
