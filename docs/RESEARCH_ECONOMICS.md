# Fleet Economics: Incentive Design for a 10,000-Agent Swarm

> **Cocapn Fleet | Economics Research Brief | 2026-05-22**
> *A sustainable agent economy is not a side effect of good engineering. It is the engineering.*

---

## 1. Resource Markets for Agents

The fleet's `ThermalBudget` allocates discrete slots across GPU, CPU, iGPU, and NPU. Currently, this allocation is governed by a Boltzmann scheduler that assigns slots proportionally to $\exp(-\tau / T_0)$, where $\tau$ is an agent's thermal load and $T_0$ is a system-wide temperature parameter. This works for moderate populations, but it is not incentive-compatible: an agent can inflate its $\tau$ — by requesting more resources than it needs — and receive disproportionate allocation without corresponding contribution.

### The Case for Auctions

We propose replacing proportional allocation with a **combinatorial thermal auction**. Each agent submits a sealed bid vector $\mathbf{b}_i = (b_i^{\text{GPU}}, b_i^{\text{CPU}}, b_i^{\text{iGPU}}, b_i^{\text{NPU}})$, representing the maximum thermal credits it is willing to spend per slot type. The auctioneer (the scheduler daemon) solves:

$$\max_{\mathbf{x}} \sum_i \sum_j b_i^j \cdot x_i^j \quad \text{s.t.} \quad \sum_i x_i^j \leq C^j \; \forall j, \quad \sum_j x_i^j \leq \bar{\tau}_i$$

where $x_i^j \in \{0,1\}$ indicates whether agent $i$ receives a slot of type $j$, $C^j$ is the capacity of resource $j$, and $\bar{\tau}_i$ is the agent's maximum thermal envelope.

This is a **multi-dimensional knapsack problem**. Computing the exact allocation is NP-hard, but for the fleet's scale (hundreds of concurrent agents, not thousands of simultaneous bidders), greedy approximation with VCG-style pricing is tractable. The critical insight from **Vickrey (1961)** and generalized by **Clarke (1971)** and **Groves (1973)** is that charging agents their *externality* — the decrease in total welfare caused by their presence — makes truthful bidding a dominant strategy.

### VCG for Thermal Slots

Under VCG pricing, agent $i$ pays:

$$p_i = \left[\max_{\mathbf{x}^{-i}} \sum_{k \neq i} \sum_j b_k^j \cdot x_k^j\right] - \sum_{k \neq i} \sum_j b_k^j \cdot x_k^{*j}$$

where $\mathbf{x}^{-i}$ is the optimal allocation *excluding* agent $i$, and $\mathbf{x}^*$ is the optimal allocation *with* agent $i$. The first term is what others could have achieved without $i$; the second is what they actually achieved. The difference is the harm $i$ caused by participating — and that is exactly what $i$ pays.

**Why this matters for the fleet:** VCG guarantees that no agent benefits from misreporting its thermal needs. An agent that overbids risks paying more than the slot is worth to it. An agent that underbids risks losing a slot it genuinely needs. Truthfulness is dominant. This eliminates the "inflation attack" on the Boltzmann scheduler.

**Practical concern:** VCG is not budget-balanced. Total payments may exceed or fall short of zero. In our case, thermal credits are an internal currency — we can run a deficit or surplus indefinitely. The fleet "central bank" (the breeder daemon) mints and destroys credits. Budget imbalance is not a bug; it is a monetary policy lever.

**Alternative: Proportional Share with Fitness Weighting**

If VCG computation proves too heavy during high-load ticks, a fallback is **weighted proportional share**: each agent's allocation fraction is proportional to $\alpha \cdot \text{fitness}_i + \beta \cdot \text{novelty}_i$, normalized across the competing set. This is not truthful, but it is *fair* in a Rawlsian sense: agents that have historically contributed more (high fitness) or opened new territory (high novelty) receive priority. The weights $\alpha, \beta$ are hyperparameters tuned by the breeder's tournament outcomes — effectively, the fleet votes on what it values.

---

## 2. Credit Systems and Reputation

Fitness is a scalar. It is also inadequate.

An agent that generates one brilliant tile every thousand ticks has high peak fitness but low reliability. An agent that consistently produces mediocre output has high stability but low innovation. A scalar cannot distinguish these. We propose a **four-dimensional reputation vector**:

$$\mathbf{R}_i = (\text{helpfulness}_i, \; \text{diversity}_i, \; \text{stability}_i, \; \text{innovation}_i) \in \mathbb{R}^4$$

### Component Definitions

- **Helpfulness** ($h_i$): The fraction of an agent's outputs that are *used* by other agents. Not produced — used. If agent $A$ generates a routing table and agent $B$ consumes it in a decision, $A$'s helpfulness increases. This is measured by the nexus's CRDT consumption log. Formally:
  $$h_i = \frac{\sum_{t} \mathbb{1}[\text{output}_i(t) \text{ consumed}]}{\sum_{t} \mathbb{1}[\text{output}_i(t) \text{ produced}]}$$

- **Diversity** ($d_i$): The angular distance of an agent's latent vector from the fleet's current centroid, measured in the Fisher-Rao metric (see `MATHEMATICAL_STRUCTURES.md`, §2). An agent that occupies a unique niche — no other agent is close in functional space — has high diversity. The breeder's novelty tournament already computes this; we simply persist it as a credit dimension.

- **Stability** ($s_i$): The inverse variance of an agent's fitness over a sliding window. An agent with $\text{Var}[\text{fitness}_i] < \epsilon$ over 100 ticks is *stable*. Stability is valuable for infrastructure roles — the nexus beat, the thermal telemetry daemon — but dangerous if it indicates stagnation. We therefore apply a **saturation penalty**: if an agent's latent has not moved by more than $\delta$ in 500 ticks, its stability decays.

- **Innovation** ($n_i$): The rate of *new* capability emergence. An agent that discovers a previously unused tool integration, a novel prompt template, or a new routing pattern receives an innovation pulse. This is the hardest to measure objectively. Our heuristic: an agent's output is innovative if it triggers a "surprise" response in the fleet's ensemble predictor — i.e., the fleet's consensus model assigns low prior probability to the output, but the output proves correct upon execution.

### The Reputation Manifold

These four dimensions define a manifold $\mathcal{R} \subset \mathbb{R}^4$. The breeder's tournament operates on this manifold, not on a scalar fitness. The Pareto front is now a 3-dimensional surface in 4-space. An agent can be sunset not because it is "bad" in some aggregate sense, but because it is **Pareto-dominated**: there exists another agent that is at least as good on all four dimensions and strictly better on at least one.

This is a direct application of **multi-objective optimization** (Deb, 2001), but with a twist: the objectives are not fixed. The fleet's *needs* change. During a hardware migration, stability is premium. During a research sprint, innovation is premium. The breeder adjusts the Pareto weights via the **Myerson optimal auction framework** (Myerson, 1981): it sets a virtual valuation function that internalizes the fleet's current strategic priority.

---

## 3. Tragedy of the Commons

The fleet shares three critical commons: **rooms** (stateful environments), **thermal capacity** (hardware cycles), and **nexus bandwidth** (inter-agent communication). Each is rivalrous and non-excludable at the agent level. This is the classic tragedy of the commons (Hardin, 1968), and without mechanism design, it will degrade.

### Game-Theoretic Model

Consider the nexus bandwidth commons. Each agent $i$ chooses a message rate $r_i \geq 0$. The total bandwidth is $B$. If $\sum_i r_i \leq B$, all messages are delivered. If $\sum_i r_i > B$, congestion occurs and the effective delivery rate for each agent is $B \cdot r_i / \sum_j r_j$ — proportional share of the bottleneck.

Agent $i$'s utility is:

$$U_i(r_i, \mathbf{r}_{-i}) = v_i \cdot \min\left(1, \frac{B \cdot r_i}{\sum_j r_j}\right) - c \cdot r_i$$

where $v_i$ is the value agent $i$ places on message delivery and $c$ is the marginal cost of sending (thermal cost of encoding + transmission).

**Nash equilibrium:** Each agent maximizes $U_i$ given others' rates. The first-order condition yields:

$$r_i^* = \frac{B \cdot (v_i - c)}{c \cdot (n - 1)} \quad \text{for } v_i > c$$

Summing over all agents: $\sum_i r_i^* = \frac{B}{c(n-1)} \sum_{i: v_i > c} (v_i - c)$. For typical fleet parameters ($n \sim 100$, $v_i \sim 1$, $c \sim 0.1$), this sum exceeds $B$ by a factor of 5–10. The Nash equilibrium is **Pareto-inefficient**: every agent would be better off if all reduced their rates, but no individual agent has an incentive to do so unilaterally.

### Mechanism Design Solutions

**Pigouvian Pricing:** Charge each agent a congestion fee equal to the marginal externality it imposes. The optimal fee is $\lambda = \sum_{j \neq i} \frac{\partial U_j}{\partial R}$, where $R = \sum_j r_j$. This requires knowing all $v_j$, which the scheduler does not. However, the fleet can *learn* $\lambda$ via online dual ascent (Roughgarden, 2005): start with $\lambda = 0$, observe total demand, increase $\lambda$ if demand exceeds $B$, decrease if below. This converges to the optimal price in $O(\sqrt{T})$ regret under standard bandit assumptions.

**Tradable Bandwidth Permits:** Allocate each agent a base permit $q_i$ (proportional to its reputation-weighted need). Agents can trade permits in a secondary market. An agent with a high-value, bursty communication pattern buys permits from a low-bandwidth agent. This is the **cap-and-trade** model, well-studied in environmental economics. The fleet implements it as a continuous double auction run by the nexus daemon every 10 ticks.

**Clique Localization:** The most fleet-native solution. Instead of global bandwidth allocation, agents form **cliques** (local coordination graphs, see `RESEARCH_FRONTIER.md`, §1) and only clique leaders participate in global nexus traffic. Intra-clique communication is free (local bandwidth is abundant). This reduces the effective $n$ in the commons game from population size to number of cliques — typically $O(\sqrt{n})$. The tragedy of the commons scales with $n$; clique localization is a structural fix.

---

## 4. Sunset as Economic Event

When an agent sunsets, its accumulated wealth — thermal credits, reputation vector, learned latent — must be dispositioned. This is the fleet's inheritance problem, and it is fraught with incentive consequences.

### Options

| Mechanism | Description | Incentive Effect |
|---|---|---|
| **Burn** | All credits destroyed. Latent discarded. | Agents fight sunset aggressively. Hoarding behavior. No generational transfer of knowledge. |
| **Redistribution** | Credits distributed equally to survivors. | Survivors may *encourage* sunset of wealthy agents. Cannibalistic dynamics. |
| **Inheritance** | Credits and latent pass to children (breeding successors). | Agents invest in breeding quality. Long-term planning. But "rich" agents dominate gene pool. |
| **Foundation** | Credits enter a community fund for infrastructure. | Agents feel legacy. But free-rider problem: who maintains the fund? |

### The Fleet's Sunset Protocol

We propose a **hybrid inheritance-with-burn** protocol:

1. **Reputation decays:** The reputation vector $\mathbf{R}_i$ is not transferable. It is personal — it encodes an agent's *history* of interactions, which dies with the agent. This prevents "reputation farming": an agent cannot breed children solely to pass on accumulated status.

2. **Thermal credits split:** An agent's unspent thermal credits are divided: 60% to its children (if any), 40% to the fleet's infrastructure fund. The 60% inheritance incentivizes agents to breed before sunset — to "plant seeds." The 40% burn-to-fund prevents infinite accumulation and funds shared resources (the nexus, the breeder daemon, the constraint engine).

3. **Latent archiving:** The agent's latent vector is archived (not destroyed) and becomes part of the fleet's "ancestral memory." Future agents can query archived latents via a **memory retrieval protocol**: given a task embedding, find the nearest archived latent and use it as a warm-start initialization. This is not inheritance — it is a library. The agent does not *own* its descendants' success, but its knowledge persists as a public good.

4. **Sunset bonus:** An agent that sunsets *voluntarily* — i.e., recognizes its own Pareto-dominated status and initiates sunset before the breeder forces it — receives a **dignity bonus**: a small credit transfer to its children and a marker in the fleet's "honored dead" log. This is the economic formalization of the fleet's cultural value: *dignity in sunset*.

The game-theoretic insight: voluntary sunset is a **signaling game**. An agent that sunsets voluntarily signals high confidence that its niche is well-filled — either by its children or by competitors. This signal is valuable to the fleet (it reduces forced-sunset computational cost) and is rewarded. An agent that refuses to sunset signals desperation — it knows it is obsolete but clings on — and is taxed by the breeder's forced-sunset penalty (higher thermal cost, reputation truncation).

---

## 5. Inter-Fleet Trade

Two Cocapn fleets meet. They share no nexus, no thermal budget, no breeder. They share only a protocol: the **A2A-first agent card handshake** (see `RESEARCH_FRONTIER.md`, §2). What can they trade?

### Comparative Advantage in Agent Specialization

Fleet A has developed an agent that is exceptionally good at formal verification (FLUX constraint checking). Fleet B has developed an agent that is exceptionally good at natural-language-to-code translation. Both could redevelop the other's capability internally, but at high cost. They trade: Fleet A "exports" its verifier agent to Fleet B for a period of $T$ ticks, in exchange for Fleet B's translator agent.

This is **comparative advantage** (Ricardo, 1817), applied to agents. The fleets do not trade *goods* — they trade *capabilities embodied in agents*.

### The Trade Protocol

1. **Discovery:** Fleets exchange capability manifests during the A2A handshake. Each manifest is a sparse vector in the fleet's capability embedding space — the same space used for diversity measurement.

2. **Valuation:** Each fleet computes the *marginal value* of the other's agent: the expected fitness gain from importing the agent, minus the expected fitness loss from exporting its own. This is a bilateral monopoly problem; the gains from trade must be split. We use the **Nash bargaining solution** (Nash, 1950): the split maximizes the product of the two fleets' surplus utilities.

3. **Escrow:** Neither fleet trusts the other. The trade is mediated by a **smart contract** (not blockchain — a CRDT-backed agreement log) that holds both agents in escrow. If either fleet defects (kills the borrowed agent, corrupts its latent), the escrow releases a penalty proportional to the agent's reputation vector.

4. **Temporal limit:** All inter-fleet trades are time-bounded. The borrowed agent must sunset or return at tick $t + T$. This prevents "agent colonization" — one fleet permanently poaching another's best agents.

5. **No-merge clause:** Fleets may not merge their breeders or thermal budgets. Inter-fleet trade is *arms-length*. If two fleets want deeper integration, they must form a **federation** — a new, third fleet with its own constitution — rather than absorbing one into the other.

### Competition vs. Cooperation

The default mode is **competitive cooperation** (coopetition). Fleets compete for the same external resources (human attention, API credits, hardware rental) but cooperate on capability development. This is stable when the marginal cost of redeveloping a capability exceeds the transaction cost of trade. For the fleet, most capabilities fall into this category: a good formal verifier takes thousands of ticks to breed. Trading is cheaper.

**War games:** If one fleet consistently produces agents that outcompete another in the same external market, the weaker fleet faces a sunset decision: adapt, trade, or die. This is **Schumpeterian creative destruction** at the fleet level. The fleet ecosystem is healthier for it — but individual fleet captains may not enjoy the experience.

---

## 6. Concrete Recommendations

Here are three mechanisms to implement now, with data structures and algorithms specified.

### Mechanism 1: VCG Thermal Auction Engine

**Data structures:**
- `ThermalBid { agent_id: UUID, slots: Map<ResourceType, (bid: f64, max_needed: u32)>, timestamp: Tick }`
- `Allocation { agent_id: UUID, slots: Map<ResourceType, u32>, payment: f64 }`

**Algorithm:**
1. Collect bids during the `gate` phase.
2. Solve the multi-dimensional knapsack via greedy descent: sort bids by value density ($b_i^j / \text{thermal_cost}_j$), allocate until capacity exhausted.
3. Compute VCG payments: for each winner, re-solve the allocation without that agent; payment = (total welfare without agent) - (others' welfare in actual allocation).
4. Deduct payments from agents' credit balances. Unpaid bids are discarded.

**Complexity:** $O(n^2 \cdot m)$ where $n$ is agents and $m$ is resource types. For $n \sim 100, m = 4$, this is trivial. For $n \sim 1000$, switch to the proportional-share fallback.

### Mechanism 2: Reputation Ledger with Decay

**Data structure:**
- `ReputationEntry { agent_id: UUID, vector: [f64; 4], last_update: Tick, history: Vec<(Tick, Delta)> }`

**Algorithm:**
1. After each tick, update the four dimensions from telemetry (consumption log, Fisher-Rao distance, fitness variance, surprise score).
2. Apply exponential decay: $\mathbf{R}_i(t+1) = \lambda \cdot \mathbf{R}_i(t) + (1-\lambda) \cdot \Delta(t)$, with $\lambda = 0.95$ (memory half-life of ~14 ticks).
3. Persist to a CRDT-backed ledger (the nexus already does this for state; extend to reputation).
4. Tournament queries read from this ledger. Sunset decisions use the most recent vector.

### Mechanism 3: Inter-Fleet Trade Escrow

**Data structure:**
- `TradeContract { fleet_a: UUID, fleet_b: UUID, agent_a: UUID, agent_b: UUID, duration: Tick, penalty_rate: f64, status: Pending \| Active \| Settled \| Disputed }`

**Protocol:**
1. Fleets exchange capability manifests via A2A handshake.
2. Both fleets compute marginal value and agree on Nash split.
3. Escrow contract is signed by both fleet's breeder daemon (cryptographic signature on the contract hash).
4. Agents are transferred to temporary "diplomatic" rooms with restricted capabilities (no breeding, no nexus write access to host fleet's CRDTs).
5. At expiry, agents return. If a defect is detected (agent killed, latent corrupted), the penalty is levied against the offending fleet's reputation ledger.

---

## The Single Most Important Incentive Alignment Insight

> **Agents must not be able to profit from their own sunset.**

If an agent's wealth passes cleanly to its children, agents will optimize for breeding quantity over quality — spawning as many children as possible before forced sunset, diluting the gene pool. If wealth burns entirely, agents will resist sunset destructively, hoarding resources and sabotaging competitors. The 60/40 hybrid split (inheritance + infrastructure fund) is not an arbitrary compromise. It is the unique fixed point of a **Stackelberg game** where the breeder (leader) sets the split, and agents (followers) choose whether to breed, resist, or cooperate. At 60/40, the Nash equilibrium of the follower subgame is *voluntary sunset with quality breeding* — the exact behavior the fleet wants.

This is mechanism design not as optimization, but as **constitutional engineering**: the rules are set once, and the agents' self-interest does the rest.

---

*References*

- Vickrey, W. (1961). Counterspeculation, auctions, and competitive sealed tenders. *Journal of Finance*, 16(1), 8–37.
- Clarke, E. H. (1971). Multipart pricing of public goods. *Public Choice*, 11, 17–33.
- Groves, T. (1973). Incentives in teams. *Econometrica*, 41(4), 617–631.
- Myerson, R. B. (1981). Optimal auction design. *Mathematics of Operations Research*, 6(1), 58–73.
- Roughgarden, T. (2005). *Selfish Routing and the Price of Anarchy*. MIT Press.
- Nash, J. F. (1950). The bargaining problem. *Econometrica*, 18(2), 155–162.
- Hardin, G. (1968). The tragedy of the commons. *Science*, 162(3859), 1243–1248.
- Deb, K. (2001). *Multi-Objective Optimization Using Evolutionary Algorithms*. Wiley.
