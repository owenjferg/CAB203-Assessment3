
def isProbDist(P):
   '''Given a dictionary P with floats as values, returns True if P represents a probability distribution, otherwise False
   '''
   if any(p < 0 or p > 1 for p in P.values()):  # Are any of the values outside 0..1?
      return False
   return sum(P.values()) == 1                  # sum of probabilities must be 1.

# We need some help to determine the probability of events from the probability distribution over outcomes
def probEvent(P, E):
   '''Given a probability distribution P and a subset E of the possible outcomes (P.keys()), returns the probability of E'''
   return sum(P[x] for x in E)                  # sum of the probabilities of all outcomes in E

# some python magic!
def prob(P, *events):                           # the * here is called the splat operator.  
                                                # All arguments after P will be put into the events as a tuple.
   '''P is  probability distribution and all remaining arguments are events (subsets of the possible outcomes).  Returns the probability of all outcomes occuring simultaneously.  Called like so:
   
   prob(P, A, B, C)
   '''
   # events is the list of all arguments after P.  Find the intersection of them all
   E = P.keys() # this is largest possible event.  
   for F in events:              
      E = E & F                                 # keep doing intersection with all given events
                                                # E is now the interesection of all events
   return probEvent(P, E)                       # Get the probability of the intersection

def conditionalProbDistribution(P, C):
   '''Returns the probability _distribution_ P(x | C) conditioned on an event C, or None if P(C) = 0'''
   p = probEvent(P, C)
   if p == 0 : return None                      # Can't divide by zero, so conditional probability not defined
   return { x : px / p for x, px in P.items() } # Give a new distribution, conditioned on C

def conditionalProb(P, A, C):
   '''Returns the conditional probability P(A|C), or None if P(C) = 0''' 
   p = probEvent(P, C)                          
   if p == 0: return None                       # Can't divide by zero, so conditional probability not defined
   return probEvent(P, A & C) / p                    # formula for P(A | C)

def marginalLikelihood(prior, likelihood, E):
   '''Given a prior distribution over hypotheses prior, a likelihood function likelihood for outcomes based on hypotheses, and an event E, 
   retutrns the total liklihood of E'''
   # This is the sum over all H of P(E | H) * P(H)
   return sum(prob(likelihood[hypothesis], E) * probHypothesis for hypothesis, probHypothesis in prior.items() )

def posterior(prior, likelihood, E):
   '''Given a prior distribution over hypotheses prior, a likelihood function likelihood for outcomes based on hypotheses, and an event E, 
   retutrns posterior distributon on hypotheses, i.e. the new probability distribution after Bayesian update.'''
   # Computes the distribution of P(H | E) = P(E | H) * P(H) / P(E)
   return { hypothesis: prob(likelihood[hypothesis], E) * hypothesisProb / marginalLikelihood(prior, likelihood, E) 
         for hypothesis, hypothesisProb in prior.items() }

def utility(P, utilityFunction):
   '''Given a probability distribution P and a utility function utilityFunction, return the expected utility.'''
   # Computes the sum of u(x) * P(x)
   return sum(p * utilityFunction[x] for x, p in P.items())

def decide(P, utilityFunctions):
   '''Given a probability distribution P and a dictionary of choices, find the choice that gives the highest expected utility.
   The dictionary of choices should be in the form
   utilityFunctions = { choice1: utilFun1, choice2: utilFun2, }
   returns a pair (choice, utility) where choice is the optimal choice (a key in the above dictionary) and utility its expected utility.
   '''
   # Get the expected utility for each utility function
   utilities = { choice: utility(P, utilFun) for choice, utilFun in utilityFunctions.items() }
   # Find the utility function that gives the best expected utility
   bestChoice = max(utilities, key=utilities.get)
   # Return the best choice and what it achieves
   return bestChoice, utilities[bestChoice]


if __name__ == "__main__":
   # Probability distributions are dictionaries with outcomes as keys and probabilities as values
   P = {
      'heads': 0.25,
      'tails': 0.25,
      'edge': 0.50
   }
   print(isProbDist(P))
   notTails = {'heads', 'edge'}
   print("Probability of heads or edge: ", probEvent(P, notTails))
   notEdge = {'heads', 'tails'}
   notHeads = {'tails', 'edge'}
   print("P(heads)", prob(P, {'heads'}))
   print("P(notEdge, notTails): ", prob(P, notHeads, notEdge))
   print("P(heads | notEdge)", conditionalProb(P, {'heads'}, notEdge))
   print("P(heads | Edge)", conditionalProb(P, {'heads'}, {'edge'}))

   # Likelyhood functions map hypotheses to probability distributions.  We model them as 
   # a dictionary with hypotheses as keys and probability distributions as values

   L = {
      'biased': { 'heads': 0.7, 'tails': 0.3 },
      'unbiased': { 'heads': 0.5, 'tails': 0.5 }
   }

   # a prior distribution is a probability distribution on hypotheses
   prior = {
      'biased': 0.1,
      'unbiased': 0.9
   }

   # What is the probability of heads given the likelihood function and prior distribution on the coin?
   print("Prob heads for possibly biased coin:", marginalLikelihood(prior, L, {'heads'}))

   # Update model based on an event
   print("Prior distribution on hypotheses", prior)
   print("heads observed")
   print("Posterior distribution on hypotheses", posterior(prior, L, {'heads'}))

   # normative decision theory
   P = { 
      'A': 0.4,
      'B': 0.6
   }

   betA = {
      'A': 1.1,
      'B': -1
   }

   betB = {
      'A': -1,
      'B': 0.5
   }
   
   noBet = {
      'A': 0,
      'B': 0
   }
   print('Utility for betting on A', utility(P, betA))
   print('Utility for betting on B', utility(P, betB))
   print('Utility for not betting', utility(P, noBet))
   print('optimal choice', decide(P, {'betA': betA, 'betB': betB, 'noBet': noBet}))
   