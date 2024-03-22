import simpy
from DHT import DHT

def main():
    env = simpy.Environment()
    dht = DHT("", env)

    # Ajout de trois nœuds à la DHT
    dht.add_node()
    dht.add_node()
    dht.add_node()
    dht.add_node()
    dht.add_node()

    # Lancement de la simulation pour une durée de 100 unités de temps (à ajuster selon vos besoins)
    dht.run_simulation(until_time=200)

    # Affichage de l'état de la DHT
    print(dht)

if __name__ == "__main__":
    main()
