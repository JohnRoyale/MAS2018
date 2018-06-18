Introduction
============

*The Ship* is a multiplayer videogame developed by Outerlight in 2006.
It is a type of murder mystery game (like cluedo), where multiple
players are on a cruise ship together. At the start of the game every
player is given a murder target which is another player on the cruise
ship. The targets are assigned in such a way that every player is both a
target and a murderer.\
When the game starts the players only know the last known location of
their target and do not know who has them as a target. The identity of
the target can be obtained by talking to them. In the videogame other
non playable characters (NPCs) are on this ship to make the players
blend in and players have to perform actions that leave them vulnerable
such as sleeping, eating, and showering. Also, the players are not
allowed to murder their targets while being observed by guards, cameras
or NPCs. The final goal for a player is to kill their target (and their
murderer) while avoiding getting killed themselves. Players have to be
smart and able to deduce who their target and murderer are to avoid
being murdered while successfully accomplishing their mission.\
For our project, we want to implement a multi-agent simulation based on
the premise of *The Ship*. Since the game is quite elaborate we propose
a simplified turn-based simulation, but the basic idea stays the same.
Like the game, our simulation has a set of agents where each agent has
to kill one of the other agents, while not getting killed themselves.
There are no NPCs and it is allowed to murder targets in front of
witnesses, and these events will expand the knowledge of the agents
involved. The agents will need to use logical reasoning to find out who
their murderer is. Besides this, the agents will also try to figure out
who targets who, such that they can figure out what the real world is.\

Setup
=====

Program
-------

Our implementation of *The Ship* will be simplified in a couple of
different ways. First of all the sandbox world of the game is simplified
to a number of connected rooms. The simulation environment will consist
of a graph containing 8 nodes, where each node represents a room in the
ship. Each agent can only see agents that are in the same room and every
agent is always in a room. The real-time component is changed to a more
turn-based component consisting of two different phases, namely a
movement phase and an action phase.

1.  **The movement phase:** Each agent will move to a different room,
    adjacent/connected to its current room.

2.  **The action phase:** Each agent will do one of the following
    actions: *do nothing*, *flee* or *kill agent*.

The actions are pretty self-explanatory. When a kill action is performed
against another agent, that agent becomes dead and is not able to move
around and gain knowledge anymore. The order of agent turns is
completely random each step of the model. This means that an agent can
be murdered, even though this agent knows who his murderer is and thus
wants to flee, but the murderer gets to move first. This randomization
has no effect on the knowledge of the target and murderer in this case.
There are some constraints on the model, which are as follows:

1.  Each agent has exactly one unique target, which is another agent.
    This means that each agent only is targeted by exactly one other
    agent as well.

2.  Two agents can never target each other. Note that, due to this
    constraint, a given model must at least have three agents.

3.  An agent that is in a room with their target, will always perform
    the *kill agent* action on their target.

4.  If an agent knows by whom they are targeted, and if they are
    currently in the same room as this agent, they will always perform
    the *flee* action.

5.  If none of the above rules apply, an agent will perform the *do
    nothing* action.

In the backend of our program, we use the Python multi-agent library
*Mesa* for agent-based modeling (<https://github.com/projectmesa/mesa>).
For building and updating the Kripke model, we use the *mlsolver*
library (<https://github.com/erohkohl/mlsolver>).

Epistemic logic model
---------------------

We want to model this version of the game using epistemic logic. Given a
set of $n$ agents $A = \{1, 2, ..., n\}$, formulae will be of the form
$t_{ij}$ with $i \neq j$ and $i, j \in A$, which stands for *i targets
j*. A Kripke model would consist of a world for every combination of
killer-target pairs. For example, for three agents and given the
constraints above, we would have two worlds: $w_1$, where we have the
formulae $\{t_{12}, t_{23}, t_{31}\}$ and $w_2$, where we have
$\{t_{13}, t_{21}, t_{32}\}$. In general, for $n$ agents, we would
initially have $(n-1)(n-2)$ different worlds. For simplicity, we omit
the $t$ part of the propositions in the actual implementation.\
During the simulation, the Kripke model will decrease in complexity as
agents reason about their and others' prospective killers by observing
the actions of the agents around them. There are a variety of ways in
which agents can gain knowledge during the game. At any time step, it's
possible for multiple agents to be present in the same room. This allows
for actions such as fleeing and killing, if the right persons meet in
the same place. However, the participants of the game know that
murderers always want to kill their target, and targets always want to
flee from their murderer, given that they know who their murderer is.
This allows for knowledge acquisition, followed by inference. Each agent
in the game contains a knowledge base, which contains propositions of
the form described above. At the start of the game, for each agent i,
knowledge base i only contains the proposition $ij$, where j is their
target. Therefore, the agents initially only know who they have to
murder and nothing else. After the action phase ends and before the
movement phase begins, each knowledge base is sent to the modal logic
solver, which we use to make adjustments to our Kripke model. The modal
logic solver will take the knowledge for each agent and use it to reduce
the amount of possible worlds and relations that an agent can still
access. Therefore, knowledge acquisition and then inference using the
new knowledge is the way in which the Kripke model becomes less complex.

As an example of inference, let us assume that two or more agents meet
in the same room. All agents choose to do nothing. The action phase is
now over and the movement phase begins, so each agent moves to a
different room. Each agent has observed that the other agents did not
murder anyone. Therefore, each agent now knows that the agents that were
just in the same room as it are not his killer, nor are they each others
killer. This knowledge is added to each participating agent of this
event, and this knowledge will then reduce the worlds that these agents
hold for possible. It's possible that because of previously acquired
knowledge, an agent is able to figure out who his murderer is because
only worlds are possible for this agent where his murderer is the same
agent.

Other events can lead to different knowledge acquisition. If three
agents are in a room, it's possible for an agent to witness the murder
of another agent. When this happens, the witnessing agent now knows that
the murderer is not his murderer. Another possible event happens when
once again, three agents meet in the same room. Now, an agent witnesses
a different agent flee. The witnessing agent now knows that the
remaining agent has to be the murderer of the fleeing agent, unless the
witness agent is also the murderer of the fleeing agent. However,
different knowledge is acquired when there are four or more agents in
the same room, with one agent fleeing. Now, the witnessing agent(s) do
not know from who the fleeing agent is fleeing from. In this case, an OR
formula is built up using the possible murderers and is added to the
witnessing agent(s) knowledge base(s). However, this situation can be
quite rare as a lot of agents need to be present in the same room.

At the end of every action phase, agents will try to figure out theirs
and others' murderers. This happens by checking all the worlds that the
agent still holds for possible, and then checking whether the murderer
is the same in all worlds. In this way, the agent can not only try to
figure out his own murderer, he may also uncover the murderers of other
agents, which in turn shorten the amount of possible agents that could
be his murderer. Eventually, it happens that multiple agents get killed
off while one or more agents survive. The game stops when only one agent
is still left, or until multiple agents are alive that are not each
other's target, so no more deaths can happen. It's still possible for
the agents to gain knowledge: two remaining agents might not know they
are not each other's target, so they could still meet in the same room
and discover this fact. However, since they are already safe from harm,
we don't consider it interesting anymore when no more murders can
happen.

In the next section, we show the results that we acquired from multiple
runs of our model. The game is very trivial if only 3 agents are
present, and computation time is too long when more than 6 agents are
used, so we only gather results from runs containing 4, 5 and 6 agents.
To show the complexity of the Kripke model, we show the initial amount
of possible worlds and relations present in the Kripke model in each
setting. we run each of the three settings (4, 5, and 6 agents) a total
of 5 times. We then take the average amount of relations that are left
after the game stops. We also count the average amount of agents
(collapsed agents) that only hold the true world for possible.

Results
=======

\centering
   agents   begin relations   worlds   collapsed agents   relations left   \% complexity reduction
  -------- ----------------- -------- ------------------ ---------------- -------------------------
     4            16            6             2                8.2                   51
     5            180           24            0                58.4                  32
     6           6144          160            0                1887                  31

  : Collapsed agents and relations left in the Kripke model, averaged
  over 5 runs for three different settings. The percentage of complexity
  reduction is also shown, which is the proportion of relations that
  have been removed from the Kripke model.[]{label="tab:results"}

The results of the model runs are summarized in Table
[\[tab:results\]](#tab:results){reference-type="ref"
reference="tab:results"}.

Discussion
==========

As we can see in the results, it seems that the amount that we are able
to reduce the complexity of the kripke model (which can get very large
very quickly) gets reduced as the number of agents increases. This makes
sense, as having more

\iffalse
Proposal
========

*The Ship* is a multiplayer videogame where all players are on a cruise
ship together. At the start of the game, each player receives the name
of their target, which is one of the other players. Each player has to
kill their target while avoiding getting killed themselves. Initially,
each player does not know whose target they are, which is something they
have to find out in order to increase their odds of survival.\
\
For our project, we want to implement a multi-agent simulation based on
the premise of *The Ship*. Like the game, our simulation has a set of
agents where each agent has to kill one of the other agents, while not
getting killed themselves. At the start of the simulation, each agent
only knows their own target. The simulation environment will consist of
a graph, where each node represents a room in the ship. Each agent can
only see agents that are in the same room. The simulation will be
turn-based, where each turn consists of two phases:

1.  **The movement phase:** Each agent will move to a different room,
    adjacent to its current room.

2.  **The action phase:** Each agent will do one of the following
    actions: *do nothing*, *flee* or *kill agent*.

To keep our model simple, we will have the following constraints which
are known by each agent:

-   Each agent has exactly one unique target, which is another agent.
    This means that each agent only is targeted by exactly one other
    agent as well.

-   Two agents can never target each other. Note that, due to this
    constraint, a given model must at least have three agents.

-   An agent that is in a room with their target, will always perform
    the *kill agent* action on their target.

-   If an agent knows by whom they are targeted, and if they are
    currently in the same room as this agent, they will always perform
    the *flee* action.

-   If none of the above rules apply, an agent will perform the *do
    nothing* action.

We want to model this version of the game using epistemic logic. Given a
set of $n$ agents $A = \{1, 2, ..., n\}$, formulae will be of the form
$t_{ij}$ with $i \neq j$ and $i, j \in A$, which stands for *i targets
j*. A Kripke model would consist of a world for every combination of
killer-target pairs. For example, for three agents and given the
constraints above, we would have two worlds: $w_1$, where we have the
formulae $\{k_{12}, k_{23}, k_{31}\}$ and $w_2$, where we have
$\{k_{13}, k_{21}, k_{32}\}$. In general, for $n$ agents, we would
initially have $(n-1)(n-2)$ different worlds.\
There is an additional game rule that will make the game a bit more
interesting, from an epistemic point of view. When an agent observes
someone murdering another agent, both the observer and the murderer know
this. To tie any loose ends, the murderer now also has to murder this
observer, as the murderer knows that the observer knows that the
murderer has murdered someone. In this situation, the observer knows
that the murderer knows that the observer saw the murder, which means
that the observer has another murderer to worry about (if his previous
murderer(s) is/are still alive).

During the simulation, the Kripke model will decrease in complexity as
agents reason about their prospective killers by observing the actions
of the agents around them. Eventually, every agent will know by whom
they are targeted[^1]. At this point, all uncertainty is gone and the
Kripke model will have collapsed to one state. This is where the
simulation ends.

[^1]: We will somewhat break suspension of disbelief by saying that if
    agent $i$ is killed by agent $j$, agent $i$ will know that they are
    $j$'s target, despite the fact that they are dead
