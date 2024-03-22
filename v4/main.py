## main.py 
import simpy
from DHT import DHT
from MessageLogger import MessageLogger 

def main():
    env = simpy.Environment()
    dht = DHT("", env)

    # Lancement de la simulation pour une durée de 100 unités de temps (à ajuster selon vos besoins)
    dht.run_simulation(until_time=100)

    # Affichage de l'état de la DHT
    print(dht)
    

if __name__ == "__main__":
    main()
