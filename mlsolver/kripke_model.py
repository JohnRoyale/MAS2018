""" Three wise men puzzle

Module contains data model for three wise men puzzle as Kripke strukture and agents announcements as modal logic
formulas
"""
from itertools import permutations
from mlsolver.kripke import KripkeStructure, World
from mlsolver.formula import Atom, And, Not, Or, Box_a, Box_star
from bisect import bisect_left


class WiseMenWithHat:
    """
    Class models the Kripke structure of the "Three wise men example.
    """

    knowledge_base = []

    def __init__(self):
        worlds = [
            World('RWW', {'1:R': True, '2:W': True, '3:W': True}),
            World('RRW', {'1:R': True, '2:R': True, '3:W': True}),
            World('RRR', {'1:R': True, '2:R': True, '3:R': True}),
            World('WRR', {'1:W': True, '2:R': True, '3:R': True}),

            World('WWR', {'1:W': True, '2:W': True, '3:R': True}),
            World('RWR', {'1:R': True, '2:W': True, '3:R': True}),
            World('WRW', {'1:W': True, '2:R': True, '3:W': True}),
            World('WWW', {'1:W': True, '2:W': True, '3:W': True}),
        ]

        relations = {
            '1': {('RWW', 'WWW'), ('RRW', 'WRW'), ('RWR', 'WWR'), ('WRR', 'RRR')},
            '2': {('RWR', 'RRR'), ('RWW', 'RRW'), ('WRR', 'WWR'), ('WWW', 'WRW')},
            '3': {('WWR', 'WWW'), ('RRR', 'RRW'), ('RWW', 'RWR'), ('WRW', 'WRR')}
        }

        relations.update(add_reflexive_edges(worlds, relations))
        relations.update(add_symmetric_edges(relations))

        self.ks = KripkeStructure(worlds, relations)

        # Wise man ONE does not know whether he wears a red hat or not
        self.knowledge_base.append(And(Not(Box_a('1', Atom('1:R'))), Not(Box_a('1', Not(Atom('1:R'))))))

        # This announcement implies that either second or third wise man wears a red hat.
        self.knowledge_base.append(Box_star(Or(Atom('2:R'), Atom('3:R'))))

        # Wise man TWO does not know whether he wears a red hat or not
        self.knowledge_base.append(And(Not(Box_a('2', Atom('2:R'))), Not(Box_a('2', Not(Atom('2:R'))))))

        # This announcement implies that third men has be the one, who wears a red hat
        self.knowledge_base.append(Box_a('3', Atom('3:R')))

class TheShipThreeAgents:
    """
    Class models the Kripke structure of the The Ship for three agents (somewhat trivial).
    """
    # The knowledge_base is as of yet unused for this class
    knowledge_base = []

    def __init__(self):
        # There are only two possible configurations of killer-targer pairs
        # Note that world 231, for example, stands for the world where 1 targets 2, 2 targets 3, 3 targets 1
        worlds = [
            World('231', {'t12': True, 't23': True, 't31': True}),
            World('312', {'t13': True, 't21': True, 't32': True}),
        ]
        # In the 3-agent case, from each world only the world itself is accessible for each agents
        relations = {
            '1': {('231','231'), ('312', '312')},
            '2': {('231','231'), ('312', '312')},
            '3': {('231','231'), ('312', '312')}
        }
        # Build the Kripke model and store it in ks
        self.ks = KripkeStructure(worlds, relations)

class TheShipNAgents:
    # The knowledge_base is as of yet unused for this class
    knowledge_base = []
    agents = []

    def __init__(self, n):
        self.build_agents(n)
        print("Agents: ", self.agents)
        worlds, propositions = self.build_worlds(n)
        print("Worlds:", worlds)

        kripke_worlds = []

        self.propositions = propositions
        print("Propositions:", propositions)
        print()

        # create World objects for the Kripke structure
        for world in worlds:
            kripke_worlds.append(World(world, worlds[world]))

        # initialize the agent world relations
        relations = {}
        for i in range(n):
            id = str(i)
            relations[id] = []
        for world in worlds:
            for i in range(n):
                id = str(i)
                # an agent only has an accessibility relation to a world where their target is the same
                # find the current agent's target
                formulas = worlds[world]
                for formula in formulas:
                    if(formula[0]) == str(i):
                        break
                # look for other worlds where the agent has the same target
                for other_world in worlds:
                    if(formula in worlds[other_world]):
                        relations[id].append((world,other_world))


        for r in relations:
            relations[r] = set(relations[r])
        print("Relations:")
        self.ks = KripkeStructure(kripke_worlds, relations)
        print(self.ks.relations)

    def build_agents(self, n):
        for i in range(n):
            self.agents.append(str(i))

    # if proposition is true for an agent in all worlds accessible
    # from the real world, add it to the agent's knowledge base
    def add_knowledge(self, agent, world, proposition):
        """
        f = Box_a(str(agent.unique_id), Atom(proposition))
        if(f.semantic(self.ks, world.name)):
            agent.kb.append(proposition)
        """

    def update_structure(self, agents):
        print("Updating kripke structure:")
        for agent in agents:
            print(agent, " kb: ", agent.kb)
            for formula in agent.kb:
                if (agent.kb[formula] == False):
                    f = Atom(formula)
                    self.ks = self.ks.solve_a(str(agent.unique_id), f)
                    agent.kb[formula] = True

        print("Worlds left:", self.ks.worlds)


    def build_worlds(self, n):
        worlds = []
        worlds_dict = {}
        targets = []
        target_count = [0] * len(self.agents)
        agent_pairs = []
        perms = permutations(self.agents, 2)
        #worlds = combinations(worlds, n)
        for p in perms:
            agent_pairs.append(''.join(list(p)))

        worlds = self.combine_agent_pairs(agent_pairs, worlds, targets, target_count, n)

        #for w in worlds:
            #print(w)

        for w in worlds:
            name = ''.join([char[-1] for char in w])
            worlds_dict[name] = {f: True for f in w}

        print("Total amount of worlds: ", len(worlds))

        return worlds_dict, agent_pairs

    def combine_agent_pairs(self, agent_pairs, worlds, targets, target_count, n):
        """
        This function recursively builds up all possible worlds.

        :param agent_pairs: the possible killer-target pairs that are still allowed
        :param worlds: the set of worlds that are already built
        :param targets: a set of killer-target pairs
        :param n: how many agents still need to be assigned a target
        :return: a list of all possible worlds
        """
        if n == 0:
            targets = sorted(targets)
            if targets not in worlds:
                worlds.append(targets)

            return worlds

        for pair in agent_pairs:
            idx = int(pair[1])
            target_count[idx] += 1

            worlds = self.combine_agent_pairs(self.update_agent_pairs(agent_pairs, pair, target_count[idx]), worlds, targets + [pair],
                                              target_count, n - 1)

        return worlds

    def update_agent_pairs(self, agent_pairs, a, count):
        if count > len(self.agents) / 2:
            return [c for c in agent_pairs if not (c[0] == a[0] or c[1] == a[1] or (c[0] == a[1] and c[1] == a[0]))]

        return [c for c in agent_pairs if not (c[0] == a[0] or (c[0] == a[1] and c[1] == a[0]))]

def add_symmetric_edges(relations):
    """Routine adds symmetric edges to Kripke frame
    """
    result = {}
    for agent, agents_relations in relations.items():
        result_agents = agents_relations.copy()
        for r in agents_relations:
            x, y = r[1], r[0]
            result_agents.add((x, y))
        result[agent] = result_agents
    return result


def add_reflexive_edges(worlds, relations):
    """Routine adds reflexive edges to Kripke frame
    """
    result = {}
    for agent, agents_relations in relations.items():
        result_agents = agents_relations.copy()
        for world in worlds:
            result_agents.add((world.name, world.name))
            result[agent] = result_agents
    return result
