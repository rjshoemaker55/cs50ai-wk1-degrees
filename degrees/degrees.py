import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


# def shortest_path(source, target):

#     # initialize a variable to hold the number of explored person_ids
#     num_explored = 0
#     # initialize a starting node with the source person_id as the state, no parent (first node) and no action (first node)
#     start = Node(state=source, parent=None, action=None)
#     # initializea  new frontier from the stack frontier
#     frontier = StackFrontier()
#     # add the starting node (state, parent, action) to the frontier
#     frontier.add(start)
#     # intialize a new set to hold the explored nodes
#     explored = set()

#     while(True):

#          """ 1. If the frontier is empty, all people have been explored and there is no solution"""
#         if frontier.empty():
#             return None

#         """ 2. Remove a node from the frontier """
#         node = frontier.remove()

#         # add the removed node to the explored set
#         explored.add(node.state)

#         # explore each person that has starred in movies with this person, pull out the movie_id and person_id for each
#         for movie_id, person_id in neighbors_for_person(node.state):
#             # if this person is not in the explored set or the frontier,
#             if (not frontier.contains_state(person_id) and person_id not in explored):
#                 """ 3. If the node is a goal state, return the solution """
#                 if person_id == target:
#                     # create a new node for this person, setting the state as the id, parent as the current node, and action as the movie_id (how they are connected)
#                     n = Node(state=person_id, parent=node, action=movie_id)
#                     # intialize a new actions list to store the actions that got us to the goal node
#                     actions = []
#                     # start reversing the actions to build a list of the actions that got us here
#                     # while there is a parent node for the current node,
#                     while(n.parent is not None):
#                         # append the current node to the actions list
#                         actions.append((n.action, n.state))
#                         # set the parent node to the current node, repeat the process
#                         n = n.parent
#                     # once we have build up the list, reverse it so it is in the correct order
#                     actions.reverse()
#                     # return the reversed actions list
#                     return actions

def shortest_path(source, target):
    num_explored = 0
    start = Node(state=source, parent=None, action=None)
    frontier = StackFrontier()
    frontier.add(start)
    explored = set()

    while True:
        if frontier.empty():
            return None

        node = frontier.remove()
        explored.add(node)

        for movie_id, person_id in neighbors_for_person(node.state):
            if (not frontier.contains_state(person_id) and person_id not in explored):
                if person_id == target:
                    n = Node(state=person_id, parent=node, action=movie_id)
                    actions = []

                    while (n.parent is not None):
                        actions.append((n.action, n.state))
                        n = n.parent
                    actions.reverse()
                    return actions


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
