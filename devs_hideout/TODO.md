# Gesture 
- [X] (F) welcome/goodbye

- [ ] profiling / difficulty select ? 

- [X] (F) handshake (lower stiffness to let user shake, maybe?)

- [X] (A) victory animation

- [X] (A) defeat animation

- [ ] announce move (many variants):
    - [X] (A) point at tablet
    - [X] (F) air writing *(Not sure it's a good idea. Tried writing on an horizontal plane and out of the user's way, but found no way to make it elegant.)*
    - [ ] (D+) generic animation(s)
        - [X] (D) wait gesture, "it's not your turn" (hand in front) (gesture_turn_2)
        - [X] "you cannot do this move" gesture (shake head gesture)


- [X] waiting on the other player (impatience gestures)

- [X] thinking



# Logic/Reasoning

- [X] (D) basic proxemics w/ sonar A
- [X] profiling / difficulty select
- [X] Start --> Play --> new match/stop
- [ ] Qualcosa di migliore per la scelta della mossa (qualche paper utile da trovare)


# UI

- [X] (F) game board
- [X] profiling / difficulty select (select on tablet for extra multimodality)
- [X] grid coordinates
- [X] select move by touching/clicking grid cell
- [X] highlight tiles in a tris



# Led

- [X] (D) won
- [X] (D) lost
- [X] (A) thinking (circular animation for eyes?) 
- [X] (A) waiting 
- [X] red if losing
- [X] green if winning


# Sound

- [ ] (D) suono fine mossa 
- [X] (D) suono vittoria 
- [X] (D) suono sconfitta 
- [ ] suono pensare 
- [X] (D) suono selezione su tablet 


# Speech
Meglio da codice e non behaviour così interfacciamo con modim per lingua automatica

- [X] chiacchiere varie durante e tra le mosse
- [X] welcome / goodbye
- [ ] profiling / difficulty select


# Other interactions

- [X] touch hand (handshake)
- [ ] touch head


# Papers stuff

- [ ] Cambia soglie delle zone prossemiche in base all'età? (scritto nel report, ma mi pare che non lo facciamo ancora)
- [X] Salvare utenti
- [X] Regole di interazione del robot teatrale
    - [X] Utterance-first behavior **VERIFICARE IN REALE** [R1]
        - (l'interazione è sempre a due)
        - (pare già a posto, i behavior ci mettono un istante a partire)
    - [X] Se sollevi un braccio, aspetta a riabbassarlo **VERIFICARE IN REALE** [R5]
        - (pare già a posto, i behavior ci mettono un istante a terminare)
    - [X] Desincronizzare movimenti con ambo le braccia! [R6]
    - [X] Contrasta movimento di un braccio con l'altro [R7-8]
    - *R3-4 sono sull'eye contact, ma noi ancora non lo consideriamo minimamente*

# OFF-TOPIC: Old-compatible DOM classing

It seems classList is not supported on old browsers from 2011.
If Pepper turns out to use such an old browser, see this StackOverflow post:
https://stackoverflow.com/questions/6787383/how-to-add-remove-a-class-in-javascript
