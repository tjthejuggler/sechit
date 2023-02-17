

#DOESN't TELL TEAMMATES

# import random

# def assign_roles(num_players):
#     if num_players < 5 or num_players > 10:
#         raise ValueError("Invalid number of players.")
#     elif num_players < 7:
#         roles = ['Liberal'] * (num_players - 2) + ['Hitler', 'Fascist']
#     elif num_players < 9:
#         roles = ['Liberal'] * (num_players - 3) + ['Hitler', 'Fascist', 'Fascist']
#     else:
#         roles = ['Liberal'] * (num_players - 4) + ['Hitler', 'Fascist', 'Fascist', 'Fascist']
#     random.shuffle(roles)
#     return roles

# num_players = int(input("Enter the number of players: "))
# roles = assign_roles(num_players)
# seen_roles = set()

# for i in range(num_players):
#     input(f"Press any key to reveal your role: ")
#     if i > 0:
#         print("Previous roles:")
#         for j in range(i):
#             if j not in seen_roles:
#                 print(f"Player {j+1}: Hidden")
#         print("-------------")
#     print(f"Your role: {roles[i]}")
#     seen_roles.add(i)
#     input("Press any key to hide your role.")
#     print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

#TELLS TEAMMATES, BUT NOT HITLER IN 5 AND 6, AND NOT THE OTHER FASCISTS

# import random

# def assign_roles(num_players):
#     if num_players < 5 or num_players > 10:
#         raise ValueError("Invalid number of players.")
#     elif num_players < 7:
#         roles = ['Liberal'] * (num_players - 2) + ['Hitler', 'Fascist']
#     elif num_players < 9:
#         roles = ['Liberal'] * (num_players - 3) + ['Hitler', 'Fascist', 'Fascist']
#     else:
#         roles = ['Liberal'] * (num_players - 4) + ['Hitler', 'Fascist', 'Fascist', 'Fascist']
#     random.shuffle(roles)
#     return roles

# num_players = int(input("Enter the number of players: "))
# roles = assign_roles(num_players)
# seen_roles = set()

# for i in range(num_players):
#     input(f"Press any key to reveal your role: ")
#     if i > 0:
#         print("Previous roles:")
#         for j in range(i):
#             if j not in seen_roles:
#                 print(f"Player {j+1}: Hidden")
#         print("-------------")
#     if roles[i] == "Fascist":
#         fascist_indices = [j+1 for j, role in enumerate(roles) if role == "Fascist" and j != i]
#         if len(fascist_indices) == 1 and num_players < 7:
#             print(f"Your teammate is: Player {fascist_indices[0]}")
#         else:
#             print(f"Your teammates are: Players {', '.join(str(index) for index in fascist_indices)}")
#         hitler_index = next(j+1 for j, role in enumerate(roles) if role == "Hitler")
#         print(f"Hitler is: Player {hitler_index}")
#     print(f"Your role: {roles[i]}")
#     seen_roles.add(i)
#     input("Press any key to hide your role.")
#     print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")




import random

def assign_roles(num_players):
    if num_players < 5 or num_players > 10:
        raise ValueError("Invalid number of players.")
    elif num_players < 7:
        roles = ['Liberal'] * (num_players - 2) + ['Hitler', 'Fascist']
    elif num_players < 9:
        roles = ['Liberal'] * (num_players - 3) + ['Hitler', 'Fascist', 'Fascist']
    else:
        roles = ['Liberal'] * (num_players - 4) + ['Hitler', 'Fascist', 'Fascist', 'Fascist']
    random.shuffle(roles)
    return roles

num_players = int(input("Enter the number of players: "))
roles = assign_roles(num_players)
seen_roles = set()

for i in range(num_players):
    input(f"Player "+str(i+1)+": Press any key to reveal your role: ")
    if i > 0:
        print("Previous roles:")
        for j in range(i):
            if j not in seen_roles:
                print(f"Player {j+1}: Hidden")
        print("-------------")
    if roles[i] == "Fascist":
        fascist_indices = [j+1 for j, role in enumerate(roles) if role == "Fascist" and j != i]
        #if len(fascist_indices) == 1 and num_players < 7:
        hitler_index = next(j+1 for j, role in enumerate(roles) if role == "Hitler")
        if num_players < 7:           
            print(f"Hitler is: Player {hitler_index}")
        else:
            print(f"Your team mates are: Players {', '.join(str(index) for index in fascist_indices)} and Hitler is: Player {hitler_index}")
    elif roles[i] == "Hitler":
        fascist_index = next(j+1 for j, role in enumerate(roles) if role == "Fascist")
        if num_players < 7:
            print(f"Your team mate is: Player {fascist_index}")
    print(f"Your role: {roles[i]}")
    seen_roles.add(i)
    input("Press any key to hide your role.")
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")


