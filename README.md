# info833_dht

Pour tester la DHT, simplement exécuter le fichier <i>main.py</i> en modifiant si besoin le temps de simulation (paramètre <i>until_time</i> à la ligne 10), plus il est long plus il y aura de noeuds.  
  
Pour controler le nombre de noeuds rejoignant ou quittant la DHT, au cours de la simulation, se rendre dans le fichier DHT.py et changer les paramètres de schedule_join_random et schedule_leave_random dans la méthode run_simulation à la fin du fichier, comme ceci par exemple (là ce sont les paramètres par défaut) : 
  
    self.env.process(
        self.schedule_join_random(
            start_time = 10, 
            end_time = 180, 
            delay = [5, 10], 
            nb_nodes = 2
            )
        )

    self.env.process(
        self.schedule_leave_random(
            start_time = 20, 
            end_time = 170, 
            delay = [10, 20], 
            nb_nodes = 2
            )
        ) 

Voici un exemple de sortie (état final de la DHT) en exécutant la simulation sur 250 unités de temps :  

![alt text](/images/output_state_dht_1.png)  
![alt text](/images/output_state_dht_2.png)  
