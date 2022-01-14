#!/usr/bin/env python
# coding: utf-8

# # load_problem
# Given a `namefile` of a tsp file, like "st70.tsp", collocated in the right path, the function returns the `problem` object, containing relevant informations about that tsp file, like the list of the nodes with their own coordinates.

# In[1]:


import tsplib95
global problem, counter_call_Make_2_Opt_Move, counter_call_Gain_From_2_Opt, counter_call_One_City_2_Opt
def load_problem(namefile):
    global problem
    problem = tsplib95.load("Network Optimization\\ALL_tsp\\"+str(namefile)+"\\"+str(namefile))
    return problem


# # distance
# Given two nodes, the function returns the euclidean distance between their coordinates, that is the weight of the arc connecting the two nodes

# In[ ]:


def distance(cityOne, cityTwo):
    global problem
    edge = cityOne, cityTwo
    weight = problem.get_weight(*edge) #distance between the two
    return weight


# # totalDistance
# Given a `tour`, that is a list of nodes, the function call the distance function for each couple of adjacent nodes in the list, summing all the results together to obtain the total distance of the tour

# In[ ]:


def totalDistance(tour):
    totDist = 0
    for i in range(len(tour)-1):
        totDist += distance(tour[i], tour[i+1])
    return totDist


# # nearest_neighbor
# Find the city in the list `cities` that is nearest to city `A`.

# In[ ]:


def nearest_neighbor(A, cities):
    return min(cities, key=lambda c: distance(c, A))


# # Build_Nearest_Neighbor_Tour
# Start the tour at the first city `firstCity`. At each step of the while cycle extend the tour by moving from the previous city to its nearest neighbor that has not yet been visited.

# In[ ]:


def Build_Nearest_Neighbor_Tour(firstCity, cities):
    start = firstCity
    tour = [start]
    unvisited = set(cities)
    unvisited.remove(start)
    while unvisited:
        C = nearest_neighbor(tour[-1], unvisited)
        tour.append(C)
        unvisited.remove(C)
    tour.append(firstCity) #add as last city the first one of the tour, useful to calculate correctly the total distance of the tour
    return tour


# # Build_Random_Tour
# Start from an empty tour. At each step of the while cycle, extend the tour by adding a random city that has not yet been visited.

# In[ ]:


import random
def Build_Random_Tour(nodes):
    listNodes = []
    listNodes[:] = nodes[:]
    tour = []
    while len(listNodes) > 0:
        nextCity = (int)(random.random()*len(listNodes))
        tour.append(listNodes[nextCity])
        del listNodes[nextCity]
    tour.append(tour[0]) #add as last city the first one of the tour, useful to calculate correctly the total distance of the tour
    return tour


# # Gain_From_2_Opt
# Gain of tour length that can be obtained by performing given 2-opt move: it returns a positive number if it is convenient to perform a 2-opt move, a negative number otherwise, checking if the distance between `X1` and `X2` plus the distance between `Y1` and `Y2` is greater than the distance between `X1` and `Y1` plus the distance between `X2` and `Y2`.
# <br>
# `X2` is the successor of `X1`.
# <br>
# `Y2` is the successor of `Y1`.

# In[ ]:


def Gain_From_2_Opt(X1, X2, Y1, Y2): 
    global counter_call_Gain_From_2_Opt
    del_Length = distance(X1, X2) + distance(Y1, Y2)
    add_Length = distance(X1, Y1) + distance(X2, Y2)
    result = del_Length - add_Length
    counter_call_Gain_From_2_Opt += 1 #to check how many times this function is called
    return result


# # Reverse_Segment
# Reverses order of elements in segment starting from startIndex and ending to endIndex of tour.
# <br>
# Final and initial part of tour make one segment.
# <br>
# While the order of arguments (`startIndex` and `endIndex`) can be safely changed when reversing segment in 2-optimization, it makes difference for 3-opt move: it isn't the same to reverse (x,z) and (z,x) in 3-opt.

# In[ ]:


def Reverse_Segment(tour, startIndex, endIndex):
    N = len(tour)
    inversionSize = (int)(((N + endIndex - startIndex + 1) % N) / 2)
    left  = startIndex
    right = endIndex

    for counter in range(inversionSize): #swap tour[left] with tour[right] for each cities between startIndex and endIndex
        aux = tour[left]
        tour[left] = tour[right]
        tour[right] = aux
        left  = (left + 1) % N
        right = (len(tour) + right - 1) % N


# # Make_2_Opt_Move
# Performs given 2-opt move on array representation of the tour.
# <br>
# The cyclic tour is cut in 2 places, by removing 2 links:
# <br>
# L1: from `t[i]` to `t[i+1]`  and  L2: from `t[j]` to `t[j+1]` and replacing them with
# <br>
# L1': from `t[i]` to `t[j]`   and  L2': from `t[i+1]` to `t[j+1]`
# <br>
# This is equivalent to reverse the order in segment from `i+1` to `j`

# In[ ]:


def Make_2_Opt_Move(tour, i, j):
    global counter_call_Make_2_Opt_Move
    Reverse_Segment(tour, (i+1) % len(tour), j)
    counter_call_Make_2_Opt_Move += 1 #to check how many times this function is called


# # One_City_2_Opt
# Shortens the tour by repeating 2-opt moves until no improvement can be done. 
# <br>
# In every iteration the function looks for and applies the move that gives maximal length gain.
# <br>
# It is the basic version, without any speedup. 
# <br>
# The parameters passed to it are the list of cities, `tour`, the index `basePos` of the city that is used to search if there is a substitute better than its successor to decrease the total tour distance, the `improvement` chosen (First or Best taken).

# In[ ]:


def One_City_2_Opt(tour, basePos, improvement):
    global counter_call_One_City_2_Opt # used to count how many times this function is called
    counter_call_One_City_2_Opt += 1
    improved = False
    if improvement == "Best":
        locallyOptimal = True
        bestMove = {"gain":0,"i":0,"j":0} # structure useful for the best improvement keeping trace of the last better gain and the positions of the cities in the tour giving that gain
    N = len(tour)
    
    i = basePos # index of the city for which it is done the local search in the tour
    X1 = tour[i] # city with index i in the tour
    X2 = tour[(i+1) % N] # the successor of X1 in the tour

    if i == 0:
        counter_2_Limit = N-1 #in this way we don't get in the cycle Y2 equal to X1
    else:
        counter_2_Limit = N

    for counter_2 in range((i+2), counter_2_Limit):
        j = counter_2 # index of another city different from X1 and X2
        Y1 = tour[j] # city with index j in the tour
        Y2 = tour[(j+1) % N] # the successor of Y1 in the tour

        gainExpected = Gain_From_2_Opt(X1, X2, Y1, Y2)
        if improvement == "First":
            if gainExpected > 0: 
                Make_2_Opt_Move(tour, i, j)
                improved = True
                return improved  # for the First Improvement, it has been found a better solution, so we break here the research
        else:
            if gainExpected > bestMove["gain"]: 
                bestMove = {"gain":gainExpected,"i":i,"j":j} # for the Best Improvement, it has been found a better solution, so we save it and we continue the research
                locallyOptimal = False
    if improvement == "Best":
        if not locallyOptimal: # only out from the cycle, if it has been found a good solution with the Best Improvement, we use the best solution found 
            Make_2_Opt_Move(tour, bestMove["i"], bestMove["j"])
            improved = True
    return improved


# # LS_2_Opt_NoSpeedup
# Optimizes the given tour using 2-opt without speedup.
# <br>
# While it can be found an improvement, the function try to do the 2-opt move starting from the city called basePos and the cities after it.
# <br>
# The city called `basePos` goes from the first one of the tour till the last one minus one, because the last one hasn't followers, so it is useless.

# In[ ]:


def LS_2_Opt_NoSpeedup(tour,improvement):
    del tour[len(tour)-1]
    N = len(tour)
    locallyOptimal = False
    
    while not locallyOptimal:
        locallyOptimal = True
        for basePos in range(0,N-2):
            improved = One_City_2_Opt(tour, basePos, improvement)
            if improved:
                locallyOptimal = False
    tour.append(tour[0])
    return tour


# # sortSecond
# Used to sort the list of neighbors depending on the distance.
# <br>
# `val` is an element of the list of neighbors with two elements: the first one is the number of the city and the second one is its distance from a certain node to which we are finding its closest neighbors.

# In[ ]:


def sortSecond(val): 
    return val[1] 


# # Build_Neighbors_Matrix
# Builds lists of `No_Of_Neighbors` nearest neighbors of each city.
# <br>
# `neighbor[i][j]` is the j-th nearest neighbour of city number `i`.

# In[ ]:


def Build_Neighbors_Matrix(No_Of_Neighbors,N):
    neighbor = [] #matrix
    neighbor.append("EMPTY ROW") # the first row is empty and not used because there is no city with number 0. The cities start from 1.
    for currentCity in range(1,N+1):
        neighbors_of_currentCity_with_distance = []
        # create the list of all neighbors of currentCity:
        for otherCity in range(1,N+1):
            if otherCity != currentCity:
                neighbors_of_currentCity_with_distance.append([otherCity, distance(currentCity,otherCity)])
                # Sort elements in neighbors_of_currentCity by ascending distance 
        neighbors_of_currentCity_with_distance.sort(key=sortSecond, reverse = False)
        neighbors_of_currentCity_with_distance = neighbors_of_currentCity_with_distance[0:No_Of_Neighbors]
        neighbors_of_currentCity = []
        for i in neighbors_of_currentCity_with_distance:
            neighbors_of_currentCity.append(i[0]) #it mantains only the neighbors, not the distances, useful only for ordering the neighbors
        neighbor.append(neighbors_of_currentCity)
    return neighbor


# # isDLB_on
# Checks if the DLB is on or off for a certain city passed as parameter

# In[ ]:


def isDLB_on(DontLook, city):
    return DontLook[city] #return True or False


# # Set_DLB_on
# Sets the DLB to on for a certain city passed as parameter

# In[ ]:


def Set_DLB_on(DontLook, city):
    DontLook[city] = True


# # Set_DLB_off
# Turns off the DLB for all the cities passed inside a list passed as parameter

# In[ ]:


def Set_DLB_off(DontLook, cities):
  # turns off DLB for given cities
    for city in range(0,len(cities)):
        DontLook[cities[city]] = False


# # One_City_2_Opt_DR
# Shortens the tour by repeating 2-opt moves until no improvement can be done with DLB or Fixed Radius.
# <br>
# In every iteration the function looks for and applies the move that gives maximal length gain.
# <br>
# This is the version with speedup DLB or Fixed Radius.
# <br>
# Its role is the same as `One_City_2_Opt()`, but here there is the speedup, so there are some modifications for it.
# <br>
# The parameter `DontLook` is used to pass the structure containing the information about the DLB, in the case we use DLB as speedup, or it is a variable at False in the other case.
# <br>
# `Fraction_Radius` is used if we use Fixed Radius as speedup, to enlarge or restrict the radius, that is the distance between two consecutive cities.

# In[ ]:


def One_City_2_Opt_DR(tour, basePos, DontLook, improvement, speedup, Fraction_Radius):
    N = len(tour)
    improved = False
    if improvement == "Best":
        locallyOptimal = True
        if "DLB" in speedup: 
            bestMove = {"gain":0,"i":0,"j":0,"X1":0,"X2":0,"Y1":0,"Y2":0} # the structure with DLB as speedup has to remember more things (X1,X2,Y1,Y2) because they have to be turned off if chosen for the 2-opt move
        else:
            bestMove = {"gain":0,"i":0,"j":0}
    for direction in ["forward", "backward"]:  # both tour neighbors considered: link between t[i] and t[i+1], then between t[i-1] and t[i]
        if "DLB" in speedup:
            if direction == "forward":
                i  = basePos
            else:
                i  = (N + basePos - 1) % N
            X1 = tour[i]
            X2 = tour[(i+1) % N]
        else:
            if direction == "forward":
                i  = basePos
                X1 = tour[i]
                X2 = tour[(i+1) % N]
            else:
                i  = (N + basePos - 1) % N
                X2 = tour[i]
                X1 = tour[basePos]  # it is equal to tour[(i+1) % N] 
            radius = distance(X1, X2) #the distance chosen as radius can be fixed a priori as a constant or depending on the actual distance between two consecutive cities. Here we consider the second case 

        for counter_2 in range(0,N):
            j = counter_2
            Y1 = tour[j]
            Y2 = tour[(j+1) % N]
            if "FixedRadius" in speedup:
                if direction == "backward":
                    aux = Y1 #swap between Y1 and Y2 in the case of backward direction of the tour
                    Y1 = Y2
                    Y2 = aux
            if (X1 == Y1) or (X2 == Y1) or (Y2 == X1):
                continue
            if "FixedRadius" in speedup:
                if distance(X2,Y2) > radius*Fraction_Radius: # only if the distance between X2 and Y2 is less than radius multiplied by Fraction_Radius we check if it is good to do the 2-opt move.
                    continue
            gainExpected = Gain_From_2_Opt(X1, X2, Y1, Y2)
            if improvement == "First":
                if gainExpected > 0:
                    if "DLB" in speedup:
                        Set_DLB_off(DontLook, [X1, X2, Y1, Y2])
                    Make_2_Opt_Move(tour, i, j)
                    improved = True
                    return improved
            else:
                if gainExpected > bestMove["gain"]: #if it is greater than zero!
                    if "DLB" in speedup:
                        bestMove = {"gain":gainExpected,"i":i,"j":j,"X1":X1,"X2":X2,"Y1":Y1,"Y2":Y2}
                    else:
                        bestMove = {"gain":gainExpected,"i":i,"j":j}
                    locallyOptimal = False
    if improvement == "Best":
        if not locallyOptimal:
            if "DLB" in speedup:
                Set_DLB_off(DontLook, [bestMove["X1"], bestMove["X2"], bestMove["Y1"], bestMove["Y2"]])
            Make_2_Opt_Move(tour, bestMove["i"], bestMove["j"])
            improved = True
    return improved


# # One_City_2_Opt_NDR
# Shortens the tour by repeating 2-opt moves until no improvement can be done with Neighbor List (with or without DLB and/or Fixed Radius).
# <br>
# In every iteration the function looks for and applies the move that gives maximal length gain.
# <br>
# This is the version with speedup Neighbor List  (with or without DLB and/or Fixed Radius).
# <br>
# Its role is the same as `One_City_2_Opt()`, but here there is the Neighbor List, so there are some modifications for it, in particular for the research of `Y1` and `Y2`.
# <br>
# The parameter `neighbor` is the matrix of neighbors of all the cities in the tour.
# <br>
# The parameter `numberOfNeigbors` is the length of the rows of the matrix neighbor.
# <br>
# The other parameters are the same of `One_City_2_Opt()` and `One_City_2_Opt_DR()`.

# In[ ]:


def One_City_2_Opt_NDR(tour, basePos, neighbor, numberOfNeigbors, DontLook, improvement, speedup, Fraction_Radius):

    N = len(tour)
    improved = False
    if improvement == "Best":
        locallyOptimal = True
        if "DLB" in speedup:
            bestMove = {"gain":0,"i":0,"j":0,"X1":0,"X2":0,"Y1":0,"Y2":0}
        else:
            bestMove = {"gain":0,"i":0,"j":0}
    for direction in ["forward", "backward"]:
        if direction == "forward":
            i  = basePos
            X1 = tour[i]
            X2 = tour[(i+1) % N]
        else:
            i  = (N + basePos - 1) % N
            X2 = tour[i]
            X1 = tour[(i+1) % N]  # == tour[basePos]
        if "FixedRadius" in speedup:
            radius = distance(X1,X2)

        for neighbor_number in range(0, numberOfNeigbors): #this is the part that changes using NeighborList. It isn't compactable because the final part, that is equal even without the NeighborList, is still inside the cycle for
            Y1 = neighbor[X1][neighbor_number]
            if direction == "forward":
                j = tour.index(Y1)
                Y2 = tour[(j+1) % N]
            else:
                j  = (N + tour.index(Y1) - 1) % N  # pos[Y1] == j+1
                Y2 = tour[j]

            if (X2 == Y1) or (Y2 == X1):
                continue
            if "FixedRadius" in speedup:
                if distance(X1, Y1) > radius*Fraction_Radius:
                    break # we break the cycle here because the other Y1 will all have greater distances from X1 because we are using here the matrix of neighbors of X1, ordered in ascending order            
                    
            gainExpected = Gain_From_2_Opt(X1, X2, Y1, Y2)
            if improvement == "First":
                if gainExpected > 0:
                    if "DLB" in speedup:
                        Set_DLB_off(DontLook, [X1, X2, Y1, Y2])
                    Make_2_Opt_Move(tour, i, j)
                    improved = True
                    return improved
            else:
                if gainExpected > bestMove["gain"]:
                    if "DLB" in speedup:
                        bestMove = {"gain":gainExpected,"i":i,"j":j,"X1":X1,"X2":X2,"Y1":Y1,"Y2":Y2}
                    else:
                        bestMove = {"gain":gainExpected,"i":i,"j":j}
                    locallyOptimal = False
    if improvement == "Best":
        if not locallyOptimal:
            if "DLB" in speedup:
                Set_DLB_off(DontLook, [bestMove["X1"], bestMove["X2"], bestMove["Y1"], bestMove["Y2"]])
            Make_2_Opt_Move(tour, bestMove["i"], bestMove["j"])
            improved = True
    return improved


# # LS_2_Opt
# Optimizes the given tour using 2-opt with speedup.
# <br>
# While it can be found an improvement, the function try to do the 2-opt move starting from the city `basePos` and the cities after it.
# <br>
# The parameters `No_Of_Neigbors` and `Fraction_Radius`, if not passed, are setted with their default values.

# In[ ]:


def LS_2_Opt(tour,improvement, speedup, No_Of_Neigbors = False, Fraction_Radius = 1):
    del tour[len(tour)-1]
    N = len(tour)
    locallyOptimal = False
    if "NeighborList" in speedup:
        if No_Of_Neigbors == False:
            No_Of_Neigbors = (int)(len(tour)/10)
        neighborListLen = min(No_Of_Neigbors, len(tour)-1)#neighbors mustn't exceed the number of cities in the tour
        neighbor = Build_Neighbors_Matrix(neighborListLen,N)#neighbor is the matrix of the neighbors
    if "DLB" in speedup:
        DontLook = {} #it is a dictionary where the key is the city and the value is True or False
        for i in range(1,len(tour)+1):
            DontLook[i] = False#set DLB off
    else:
        DontLook = False #if we don't use DLB we don't need any structure for it, but we have in any case something to pass as DontLook to the function (because it consider either the cases with and without DLB to be more compact)
  
    while not locallyOptimal:
        locallyOptimal = True
        for basePos in range(0,N):
            if "DLB" in speedup:
                baseCity = tour[basePos]
                if isDLB_on(DontLook, baseCity):
                    continue
            if "NeighborList" in speedup: # here there are all the possible cases in which there is NeighborList
                improved = One_City_2_Opt_NDR(tour, basePos, neighbor, neighborListLen, DontLook, improvement, speedup, Fraction_Radius)
            else: # here there are the other cases with speedup but without NeighborList
                improved = One_City_2_Opt_DR(tour, basePos, DontLook, improvement, speedup, Fraction_Radius)
                
            if not improved:
                if "DLB" in speedup: 
                    Set_DLB_on(DontLook, baseCity)
            else:
                locallyOptimal = False
    tour.append(tour[0])
    return tour


# # Between
# Returns true if `x` is between `a` and `b` in cyclic sequence of the tour.
# <br>
# It is used if used the 3-opt method.

# In[ ]:


def Between(a, x, b):
    if (b > a):
        result = (x > a) and (x < b)
    elif (b < a):
        result = (x > a) or (x < b)
    else:
        result = False


# # Gain_From_3_Opt
# Gain of tour length which can be obtained by performing 3-opt move.
# <br>
# `X2` is the successor of `X1`, `Y2` of `Y1`, `Z2` of `Z1`.
# <br>
# The cyclic order must be `X1`,`Y1`,`Z1`, so we can have `X1`->`Y1`->`Z1` or `Y1`->`Z1`->`X1` or `Z1`->`X1`->`Y1`, but not `Z1`->`Y1`->`X1`.
# <br>
# The cyclic tour is built from three segments: `abc`
# <br>
# segment `a` = `Z2`..`X1` (could be that `X1` is towards the end of the list `tour` and `Z2` at the beginning of it)
# <br>
# segment `b` = `X2`..`Y1`
# <br>
# segment `c` = `Y2`..`Z1`
# <br>
# `a'` means reversed segment `a`, same thing for `b'` and `c'`

# In[ ]:


def Gain_From_3_Opt(X1, X2, Y1, Y2, Z1, Z2, optCase):
    if optCase == "opt3_case_0":
        return 0  # original tour remains without changes

      # 2-OPT MOVES
      # the move is identical to a single 2-opt move
    elif optCase == "opt3_case_1":   #  a'bc;  2-opt (i,k)
        del_Length = distance(X1, X2) + distance(Z1, Z2)
        add_Length = distance(X1, Z1) + distance(X2, Z2)
    elif optCase == "opt3_case_2":   #  abc';  2-opt (j,k)
        del_Length = distance(Y1, Y2) + distance(Z1, Z2)
        add_Length = distance(Y1, Z1) + distance(Y2, Z2)
    elif optCase == "opt3_case_3":   #  ab'c;  2-opt (i,j)
        del_Length = distance(X1, X2) + distance(Y1, Y2)
        add_Length = distance(X1, Y1) + distance(X2, Y2)

      # PURE 3-OPT MOVES
      # all 3 edges must be removed, so they all have the same formula for del_Length
         # CASE A) move equal to two subsequent 2-opt moves
    elif optCase == "opt3_case_4":   # ab'c'
        add_Length = distance(X1, Y1) + distance(X2, Z1) + distance(Y2, Z2)
        del_Length = distance(X1, X2) + distance(Y1, Y2) + distance(Z1, Z2)
    elif optCase == "opt3_case_5":  # a'b'c
        add_Length = distance(X1, Z1) + distance(Y2, X2) + distance(Y1, Z2)
        del_Length = distance(X1, X2) + distance(Y1, Y2) + distance(Z1, Z2)
    elif optCase == "opt3_case_6":   # a'bc'
        add_Length = distance(X1, Y2) + distance(Z1, Y1) + distance(X2, Z2)
        del_Length = distance(X1, X2) + distance(Y1, Y2) + distance(Z1, Z2)
         # CASE B) move equal to three subsequent 2-opt moves
    elif optCase == "opt3_case_7":   # a'b'c'
        add_Length = distance(X1, Y2) + distance(Z1, X2) + distance(Y1, Z2)
        del_Length = distance(X1, X2) + distance(Y1, Y2) + distance(Z1, Z2)
      
    result = del_Length - add_Length
    return result


# # Make_3_Opt_Move
# Performs given 3-opt move on the tour.
# <br>
# The cyclic order must be: `k`>`j`>`i` or `i`>`k`>`j` or `j`>`k`>`i`, but not `i`>`j`>`k` nor `j`>`k`>`i` nor `k`>`i`>`j`
# <br>
# The cyclic tour is built from three segments: `abc`
# <br>
# segment `a` = `[k+1 .. i]` (could be `[0..i]` & `[k+1..N-1]`)
# <br>
# segment `b` = `[i+1 .. j]`
# <br>
# segment `c` = `[j+1 .. k]`
# <br>
# `a'` means reversed segment `a`, same thing for `b'` and `c'`

# In[ ]:


def Make_3_Opt_Move(tour,i, j, k, optCase):
    N = len(tour)
  # IDENTITY
  #   nothing to do, the tour remains without changes
    if optCase == "opt3_case_0":
        return

  # 2-OPT MOVES
  #   one of the three links is removed and added again
    elif optCase == "opt3_case_1":#  a'bc = a[bc]'
        Reverse_Segment(tour, (k+1) % N, i)
    elif optCase == "opt3_case_2":    #  abc'
        Reverse_Segment(tour, (j+1) % N, k)
    elif optCase == "opt3_case_3":    #  ab'c
        Reverse_Segment(tour, (i+1) % N, j)

      # PURE 3-OPT MOVES
      #   all three links are removed, then other links between cities added
      #   A) moves equal to two subsequent 2-opt moves:
    elif optCase == "opt3_case_4":    # ab'c'
        Reverse_Segment(tour, (j+1) % N, k)
        Reverse_Segment(tour, (i+1) % N, j)
    elif optCase == "opt3_case_5":    # a'b'c
        Reverse_Segment(tour, (k+1) % N, i)
        Reverse_Segment(tour, (i+1) % N, j)
    elif optCase == "opt3_case_6":    # a'bc'
        Reverse_Segment(tour, (k+1) % N, i)
        Reverse_Segment(tour, (j+1) % N, k)
      #   B) move equal to three subsequent 2-opt moves
    elif optCase == "opt3_case_7":    # a'b'c' (=acb)
        # this move can be implemented by reversing all segments
        # without changing their order (a'b'c'), that is as a sequence
        # of three 2-opt moves:
        Reverse_Segment(tour, (k+1) % N, i)
        Reverse_Segment(tour, (i+1) % N, j)
        Reverse_Segment(tour, (j+1) % N, k)


# # LS_3_Opt
# Optimizes the given tour using 3-opt with or without speedup (only cases with DLB and NeighborList+DLB).
# <br>
# The parameters have the same meaning of the ones in `LS_2_Opt()`.

# In[2]:


def LS_3_Opt(tour, improvement, speedup, No_Of_Neigbors = False): 
    del tour[len(tour)-1]
    N = len(tour)
    locallyOptimal = False
    if "NeighborList" in speedup:
        if No_Of_Neigbors == False:
            No_Of_Neigbors = (int)(len(tour)/10)
        neighborListLen = min(No_Of_Neigbors, len(tour)-1)#neighbors mustn't exceed the number of cities in the tour
        neighbor = Build_Neighbors_Matrix(neighborListLen,N)#neighbor is the matrix of the neighbors
    
    if "DLB" in speedup:
        DontLook = {} #it is a dictionary where the key is the city and the value is True or False
        for i in range(1,len(tour)+1):
            DontLook[i] = False#set DLB off
  
    while not locallyOptimal:
        locallyOptimal = True
        for basePos in range(0,N):
            if "DLB" in speedup:
                baseCity = tour[basePos]
                if isDLB_on(DontLook, baseCity):
                    continue
                # here there is the call to the function depending on the speedup used
            if "NeighborList+DLB" in speedup:
                improved = One_City_3_Opt_ND(tour, basePos, neighbor, neighborListLen, DontLook, improvement)
            elif "DLB" in speedup:
                improved = One_City_3_Opt_DLB(tour, basePos, DontLook, improvement)
            elif "False" in speedup:
                improved = One_City_3_Opt(tour, basePos, improvement)
            if not improved:
                if "DLB" in speedup:
                    Set_DLB_on(DontLook, baseCity)
            else:
                locallyOptimal = False
    tour.append(tour[0])
    return tour


# # One_City_3_Opt
# Shortens the tour by repeating 3-opt moves until no improvement can be done: in every iteration looks for and applies the move that gives maximal length gain (if used the Best improvement) or apply the first move that is acceptable (if used the First improvement).
# <br>
# It is the basic version, without any speedup. 
# <br>
# The idea is the same used in `One_City_2_Opt()`, but taking into account another couple of cities, `Z1` and `Z2`, (obtained with another cycle for), to use `Gain_From_3_Opt()` and `Make_3_Opt_Move()`.

# In[ ]:


def One_City_3_Opt(tour, basePos, improvement):
    improved = False
    if improvement == "Best":
        locallyOptimal = True
        bestMove = {"gain":0,"i":0,"j":0,"k":0,"optCase":0} # it has to save also the optCase for which the gain is better than the last one, to understand how to do, at the end, the 3-opt move.
    N = len(tour)
    
    i  = basePos 
    X1 = tour[i]
    X2 = tour[(i+1) % N]
    for counter_2 in range(1, N-2):
        j = (i + counter_2) % N 
        Y1 = tour[j]
        Y2 = tour[(j+1) % N]
        for counter_3 in range(counter_2+1,N):
            k = (i + counter_3) % N  
            Z1 = tour[k]
            Z2 = tour[(k+1) % N]

            for optCase in ["opt3_case_3", "opt3_case_6", "opt3_case_7"]: # it checks only these three cases, because the others are equals to some of these.
                gainExpected = Gain_From_3_Opt(X1, X2, Y1, Y2, Z1, Z2, optCase)
                if improvement == "First":
                    if gainExpected > 0:
                        Make_3_Opt_Move(tour, i, j, k, optCase)
                        improved = True
                        return improved
                else:
                    if gainExpected > bestMove["gain"]:
                        bestMove = {"gain":gainExpected,"i":i,"j":j,"k":k,"optCase":optCase}
                        locallyOptimal = False
    if improvement == "Best":
        if not locallyOptimal:
            Make_3_Opt_Move(tour, bestMove["i"], bestMove["j"], bestMove["k"], bestMove["optCase"])
            improved = True
    return improved


# # One_City_3_Opt_DLB
# Shortens the tour by repeating 3-opt moves until no improvement can be done.
# <br>
# This is the version using the DLB speedup, so there is as parameter also `DontLook`, with the same meaning of the 2-opt case.

# In[ ]:


def One_City_3_Opt_DLB(tour, basePos, DontLook, improvement):
    N = len(tour)
    improved = False
    if improvement == "Best":
        locallyOptimal = True
        bestMove = {"gain":0,"i":0,"j":0,"k":0,"optCase":0}
    for direction in ["forward", "backward"]:
        if direction == "forward":
            i  = basePos
        else:
            i  = (N + basePos - 1) % N
        X1 = tour[i]
        X2 = tour[(i+1) % N]

        if isDLB_on(DontLook,X1) or isDLB_on(DontLook,X2):  
            continue

        for counter_2 in range(0, N):
            j = counter_2 # second cut after j
            Y1 = tour[j]
            Y2 = tour[(j+1) % N]

            if (X1 == Y1) or (X2 == Y1) or (Y2 == X1):
                continue

            # examine 2-opt move (opt3_case_1, opt3_case_2 and opt3_case_3, that are all equal to opt3_case_1, so it saves at the end it)
            gainExpected = Gain_From_2_Opt(X1, X2, Y1, Y2)
            if improvement == "First":
                if gainExpected > 0:
                    Set_DLB_off(DontLook, [X1, X2, Y1, Y2])
                    Make_3_Opt_Move(tour, i, j, j, "opt3_case_1")
                    improved = True
                    return improved
            else:
                if gainExpected > bestMove["gain"]:
                    bestMove = {"gain":gainExpected,"i":i,"j":j,"k":j,"optCase":"opt3_case_1"}
                    locallyOptimal = False
            
            for counter_3 in range(0,N):
                k = counter_3 
                Z1 = tour[k]
                Z2 = tour[(k+1) % N]
                if (X1 == Z1) or (Y1 == Z1):
                    continue

                if not Between(i, j, k):
                    continue
              # examine pure 3-opt cases
                for optCase in ["opt3_case_6", "opt3_case_7"]:
                    gainExpected = Gain_From_3_Opt(X1, X2, Y1, Y2, Z1, Z2, optCase)
                    if improvement == "First":
                        if gainExpected > 0:
                            improved = True
                            Set_DLB_off(DontLook, [X1, X2, Y1, Y2, Z1, Z2])
                            Make_3_Opt_Move(tour, i, j, k, optCase)
                            return improved
                    else:
                        if gainExpected > bestMove["gain"]:
                            bestMove = {"gain":gainExpected,"i":i,"j":j,"k":k,"optCase":optCase}
                            locallyOptimal = False
    if improvement == "Best":
        if notLocallyOptimal:
            improved = True
            Set_DLB_off(DontLook, [X1, X2, Y1, Y2])
            if bestMove["optCase"] == "opt3_case_6" or bestMove["optCase"] == "opt3_case_7":
                Set_DLB_off(DontLook, [Z1, Z2])
            Make_3_Opt_Move(tour, bestMove["i"], bestMove["j"], bestMove["k"], bestMove["optCase"])
    return improved


# # One_City_3_Opt_ND
# Shortens the tour by repeating 3-opt moves until no improvement can be done.
# <br>
# This is the version using the NeighborList+DLB speedup, with some semplifications.
# <br>
# The parameters has the same meaning that they have in `One_City_2_Opt_NDR()`.

# In[ ]:


def One_City_3_Opt_ND(tour, basePos, neighbor, numberOfNeigbors, DontLook, improvement):
    N = len(tour)
    improved = False
    if improvement == "Best":
        locallyOptimal = True
        bestMove = {"gain":0,"i":0,"j":0,"k":0,"optCase":0}
    
    for direction in ["forward", "backward"]:
        if direction == "forward":
            i  = basePos
        else:
            i  = (N + basePos - 1) % N
        X1 = tour[i]
        X2 = tour[(i+1) % N]
 
        for neighbor_1 in range(0, numberOfNeigbors):
        # new edges in optCase=6: *X1-Y2*, Y1-Z1, X2-Z2
        # new edges in optCase=7: *X1-Y2*, X2-Z1, Y1-Z2
            Y2 = neighbor[X1][neighbor_1]
            j  = (tour.index(Y2) + N - 1) % N
            Y1 = tour[j]

            if (Y1 != X1) and (Y1 != X2):
                gainExpected = Gain_From_2_Opt(X1, X2, Y1, Y2)
                if improvement == "First":
                    if gainExpected > 0:
                        improved = True
                        Set_DLB_off(DontLook, [X1, X2, Y1, Y2])
                        Make_3_Opt_Move(tour, i, j, j, "opt3_case_1")
                        return improved
                else:
                    if gainExpected > bestMove["gain"]:
                        locallyOptimal = True
                        bestMove = {"gain":gainExpected,"i":i,"j":j,"k":j,"optCase":"opt3_case_1"}

            for neighbor_2 in range(0, numberOfNeigbors):
              # new edges in optCase=6: X1-Y2, *Y1-Z1*, X2-Z2
                Z1_6 = neighbor[Y1][neighbor_2]
                k_6  = tour.index(Z1_6)
                Z2_6 = tour[(k_6 + 1) % N]
              # new edges in optCase=7: X1-Y2, X2-Z1, *Y1-Z2*
                Z2_7 = neighbor[Y1][neighbor_2]
                k_7  = (tour.index(Z2_7) + N - 1) % N
                Z1_7 = tour[k_7]

                if Between(i, j, k_6):
                    gainExpected = Gain_From_3_Opt(X1, X2, Y1, Y2, Z1_6, Z2_6,"opt3_case_6")
                    if improvement == "First":
                        if gainExpected > 0:
                            improved = True
                            Set_DLB_off(DontLook, [X1, X2, Y1, Y2, Z1_6, Z2_6])
                            Make_3_Opt_Move(tour, i, j, k_6, "opt3_case_6")
                            return improved
                    else:
                        if gainExpected > bestMove["gain"]:
                            locallyOptimal = False
                            bestMove = {"gain":gainExpected,"i":i,"j":j,"k":k_6,"optCase":"opt3_case_6"}

                if Between(i, j, k_7):
                    gainExpected = Gain_From_3_Opt(X1, X2, Y1, Y2, Z1_7, Z2_7,"opt3_case_7")
                    if improvement == "First":
                        if gainExpected > 0:
                            improved = True
                            Set_DLB_off(DontLook, [X1, X2, Y1, Y2, Z1_7, Z2_7])
                            Make_3_Opt_Move(tour, i, j, k_7, "opt3_case_7")
                            return improved
                    else:
                        if gainExpected > bestMove["gain"]:
                            locallyOptimal = False
                            bestMove = {"gain":gainExpected,"i":i,"j":j,"k":k_7,"optCase":"opt3_case_7"}
    if improvement == "Best":
        if notLocallyOptimal:
            improved = True
            Set_DLB_off(DontLook,
                          [ tour[bestMove["i"]], tour[(bestMove["i"] + 1) % N],
                            tour[bestMove["j"]], tour[(bestMove["j"] + 1) % N],
                            tour[bestMove["k"]], tour[(bestMove["k"] + 1) % N] ])
            Make_3_Opt_Move(tour, bestMove["i"], bestMove["j"], bestMove["k"],bestMove["optCase"])
    return improved


# # Make_Segment_Shift_Move
# Shifts the segment of `tour`: cities from `tour[i+1]` to `tour[j]` from their current position to position after current city `tour[k]`, that is between cities `tour[k]` and `tour[k+1]`.
# <br>
# `k`, `k+1` must not be within the segment `[i+1..j]`
# <br>
# (it is the same that to do the opt_case_7 of 3Opt).
# <br>
# It is used if used the Or-opt method.

# In[ ]:


def Make_Segment_Shift_Move(tour,i, j, k):
    N = len(tour)
    Reverse_Segment(tour, (k+1) % N, i)
    Reverse_Segment(tour, (i+1) % N, j)
    Reverse_Segment(tour, (j+1) % N, k)


# # Gain_From_Segment_Shift
# Gain of tour length which can be obtained by performing Segment Shift.
# <br>
# Cities from `X2` to `Y1` would be moved from its current position, between `X1` and `Y2`, to position between cities `Z1` and `Z2`.
# <br>
# `X2` is the successor of `X1`, `Y2` of `Y1`, `Z2` of `Z1`.
# <br>
# It is used if used the Or-opt method.

# In[ ]:


def Gain_From_Segment_Shift(X1, X2, Y1, Y2, Z1, Z2):

    del_Length = distance(X1, X2) + distance(Y1, Y2) + distance(Z1, Z2)
    add_Length = distance(X1, Y2) + distance(Z1, X2) + distance(Y1, Z2)
    result = del_Length - add_Length
    return result


# # LS_Or_Opt
# Optimizes the given tour using Or-opt without speedup

# In[ ]:


def LS_Or_Opt(tour, improvement): 
    del tour[len(tour)-1]
    N = len(tour)
    locallyOptimal = False
  
    while not locallyOptimal:
        locallyOptimal = True
        for basePos in range(0,N):
            baseCity = tour[basePos]
            improved = One_City_Or_Opt(tour, basePos, improvement)
            if improved:
                locallyOptimal = False
    tour.append(tour[0])
    return tour


# # One_City_Or_Opt
# Optimizes the given tour using Or-opt.
# <br>
# Shortens the tour by repeating Segment Shift moves for segment with length equal 3, 2, 1 until no improvement can by done.

# In[ ]:


def One_City_Or_Opt(tour, basePos, improvement):
    improved = False
    if improvement == "Best":
        locallyOptimal = True
        bestMove = {"gain":0,"i":0,"j":0,"k":0}
    N = len(tour)

    for segmentLen in [3,2,1]:

        i = basePos
        X1 = tour[i]
        X2 = tour[(i + 1) % N]

        j = (i + segmentLen) % N
        Y1 = tour[j]
        Y2 = tour[(j + 1) % N]

        for shift in range(segmentLen+1, N):
            k  = (i + shift) % N
            Z1 = tour[k]
            Z2 = tour[(k + 1) % N]

            gainExpected = Gain_From_Segment_Shift(X1, X2, Y1, Y2, Z1, Z2)
            if improvement == "First":
                if gainExpected > 0:
                    Make_Segment_Shift_Move(tour, i, j, k)
                    improved = True
                    return improved
            else:
                if gainExpected > bestMove["gain"]:
                    bestMove = {"gain":gainExpected,"i":i,"j":j,"k":k}
                    improved = True
                    locallyOptimal = False
    if improvement == "Best":
        if not locallyOptimal:
            Make_Segment_Shift_Move(tour, bestMove["i"], bestMove["j"], bestMove["k"])
    return improved


# # solveTSP
# The main function callable from the user.
# Its parameters, with which the user can test the various cases, are: 
# <br>
# `firstSolution`: tour created randomly or with nearest neighbor technique;
# <br>
# `howToSolve`: technique used for the local search: 2Opt, OrOpt or 3Opt;
# <br>
# `improvement`: best taken or first taken;
# <br>
# `problem_to_solve`: the name of the file `.tsp` used;
# <br>
# `speedup`: the speedup chosen, or False if not used any speedup (it is False if not chosen one by default);
# <br>
# `No_Of_Neigbors`: number of neighbors (taken into account only if there is a speedup with NeighborList) (it is False if not chosen explicity by default); 
# <br>
# `Fraction_Radius`: the fraction of the radius to use (taken into account only if there is a speedup with FixedRadius) (it is equal to `1` by default).
# <br>
# The possible speedup that can be chosen are: "False", "NeighborList", "FixedRadius", "DLB" or a combination of the three types of speedup.
# 

# In[ ]:


import datetime
def solveTSP(firstSolution,howToSolve,improvement,problem_to_solve,speedup = "False", No_Of_Neigbors = False, Fraction_Radius = 1):
    global problem, counter_call_Make_2_Opt_Move, counter_call_Gain_From_2_Opt, counter_call_One_City_2_Opt
    counter_call_Gain_From_2_Opt = 0
    counter_call_Make_2_Opt_Move = 0
    counter_call_One_City_2_Opt = 0
    problem = load_problem(problem_to_solve)
    nodes = list(problem.get_nodes())
    start_time = datetime.datetime.now()
    if firstSolution == "NN":
        firstTour = Build_Nearest_Neighbor_Tour(1+(int)(random.random()*len(nodes)), nodes)
    elif firstSolution == "random":
        firstTour = Build_Random_Tour(nodes)
    first_distance = totalDistance(firstTour)
    text = "The total distance of the initial tour is: " + str(first_distance) + "\n"
    if howToSolve == "2Opt":
        if speedup == "False":
            finalTour = LS_2_Opt_NoSpeedup(firstTour,improvement)
        else:   
            finalTour = LS_2_Opt(firstTour,improvement, speedup, No_Of_Neigbors, Fraction_Radius)
    elif howToSolve == "3Opt":
        finalTour = LS_3_Opt(firstTour, improvement, speedup, No_Of_Neigbors)
    elif howToSolve == "OrOpt":
        finalTour = LS_Or_Opt(firstTour, improvement)
    final_time = datetime.datetime.now()
    time_to_solve = (final_time-start_time).total_seconds()
    final_distance = totalDistance(finalTour)
    text += "The total distance of the final tour is: " + str(final_distance)
    text += "\nSolution found in " + str(time_to_solve) + " seconds"
    save_in_file(problem_to_solve,firstSolution,howToSolve,improvement,speedup, finalTour)
    optimal_distance = check_optimal_solution(problem_to_solve)
    save_time_and_distance(problem_to_solve,firstSolution,howToSolve,improvement,speedup,No_Of_Neigbors,Fraction_Radius,time_to_solve,first_distance, final_distance, optimal_distance)
    if howToSolve == "2Opt" and speedup == "False":
        save_counters(problem_to_solve,improvement,counter_call_Make_2_Opt_Move, counter_call_Gain_From_2_Opt, counter_call_One_City_2_Opt, time_to_solve)
    graph_t = draw_tour(finalTour) #TO PLOT THE TOUR
    plot_tour(graph_t)
    return text


# # save_counters
# It saves in `counters.csv` the values of the counter of some functions.
# <br>
# In particular, it is called in the case of 2Opt method, without speedup, to compare the first and best improvements.
# <br>
# The column of `counters.csv` are: 
# <br>
# `problem`: the name of the file `.tsp` used;
# <br>
# `improvement`: best taken or first taken;
# <br>
# `timeToSolve`: the interval of time taken to obtain the final solution of the tour; 
# <br>
# `call_Make_2_Opt_Move`: the number of times the function `Make_2_Opt_Move()` has been called;
# <br>
# `call_Gain_From_2_Opt`: the number of times the function `Gain_From_2_Opt()` has been called;
# <br>
# `call_One_City_2_Opt`: the number of times the function `One_City_2_Opt()` has been called.

# In[ ]:


def save_counters(filename,improvement,c1, c2, c3, time_to_solve):
    df = pd.DataFrame({'problem': [filename],
                   'improvement': [improvement],
                   'timeToSolve': [time_to_solve],
                   'call_Make_2_Opt_Move': [c1],
                   'call_Gain_From_2_Opt': [c2],
                   'call_One_City_2_Opt': [c3]})

    if path.isfile('Network Optimization\\solutions\\counters.csv') == False:
        df.to_csv('Network Optimization\\solutions\\counters.csv', mode = 'w', index = False)
    else:
        df.to_csv('Network Optimization\\solutions\\counters.csv', mode = 'a', header=False, index = False)


# # draw_initial_tour
# Draw the initial tour for a problem in `ALL_tsp`. The parameter `firstSolution` is used to specify if to use the random method or nearest neighbor method to get the initial tour.

# In[ ]:


def draw_initial_tour(problem_to_solve,firstSolution):
    global problem
    problem = load_problem(problem_to_solve)
    nodes = list(problem.get_nodes())
    if firstSolution == "NN":
        firstTour = Build_Nearest_Neighbor_Tour(1+(int)(random.random()*len(nodes)), nodes)
    elif firstSolution == "random":
        firstTour = Build_Random_Tour(nodes)
    graph_t = draw_tour(firstTour) #TO PLOT THE TOUR
    plot_tour(graph_t)


# # draw_loaded_tour
# Draw the tour of a solution found during the tests. 
# <br>
# The solution must be in the relative path `Network Optimization\solutions`, otherwise it can't be found.

# In[ ]:


def draw_loaded_tour(solution):
    #draw the loaded tour
    global problem
    problem_to_solve = solution[3:solution.index("_")]
    problem_to_solve += ".tsp"
    problem = load_problem(problem_to_solve)
    nodes = list(problem.get_nodes())
    opt = tsplib95.load('Network Optimization\\solutions\\'+str(solution)+'.tour')
    firstTour = opt.tours[0]
    firstTour.append(firstTour[0]) #the final city is equal to the first one, but for the standard it isn't repeated in the file, so we must add it here
    print("The total distance is "+str(totalDistance(firstTour)))
    graph_t = draw_tour(firstTour) #TO PLOT THE TOUR
    plot_tour(graph_t)


# # check_optimal_solution
# Checks if the optimal solution is present in a file `.opt.tour`: in positive case the function get the total distance of the optimal tour (only if written between brackets in the file)

# In[ ]:


def check_optimal_solution(filename): 
    if path.isfile('Network Optimization\\ALL_tsp\\'+str(filename[:-4])+'.opt.tour\\'+str(filename[:-4])+'.opt.tour') == False:
        return False
    opt = tsplib95.load('Network Optimization\\ALL_tsp\\'+str(filename[:-4])+'.opt.tour\\'+str(filename[:-4])+'.opt.tour')
    touropt = opt.tours[0] #because there can be more than one optimal tour in the file
    touropt.append(touropt[0])
    return totalDistance(touropt)


# # save_time_and_distance
# Saves in a row of `tsp.csv` the informations relevant to compare the methods used.
# <br>
# The column of `tsp.csv` are: 
# <br>
# `problem`: the name of the file `.tsp` used;
# <br>
# `firstSolution`: tour created randomly or with nearest neighbor technique;
# <br>
# `howToSolve`: technique used for the local search: 2Opt, OrOpt or 3Opt;
# <br>
# `improvement`: best taken or first taken;
# <br>
# `speedup`: the speedup chosen, or False if not used any speedup;
# <br>
# `timeToSolve`: the interval of time taken to obtain the final solution of the tour; 
# <br>
# `firstDistance`: the total distance of the initial tour;
# <br>
# `finalDistance`: the total distance of the final tour;
# <br>
# `optimalDistance`: the optimal distance of the tour (only if found a file `.opt.tour`)

# In[ ]:


import pandas as pd
import os
from os import path
def save_time_and_distance(filename,firstSolution,howToSolve,improvement,speedup,No_Of_Neigbors,Fraction_Radius,time_to_solve,first_distance, final_distance,optimal_distance):
    if "NeighborList" in speedup:
        if No_Of_Neigbors != False: # if the number of neighbors is specified, we save it at the end of the string for the speedup
            speedup += str(No_Of_Neigbors)
    if Fraction_Radius != 1:
        speedup += "-" + str(Fraction_Radius) # if the fraction is specified, we save it at the end of the string for the speedup (with a - before it, to distinguish from the number of neighbors)
    df = pd.DataFrame({'problem': [filename],
                   'firstSolution': [firstSolution],
                   'howToSolve': [howToSolve],
                   'improvement': [improvement],
                   'speedup': [speedup],
                   'timeToSolve': [time_to_solve],
                   'firstDistance': [first_distance],
                   'finalDistance': [final_distance],
                   'optimalDistance': [optimal_distance]})

    if path.isfile('Network Optimization\\solutions\\tsp.csv') == False:
        df.to_csv('Network Optimization\\solutions\\tsp.csv', mode = 'w', index = False)
    else:
        df.to_csv('Network Optimization\\solutions\\tsp.csv', mode = 'a', header=False, index = False)


# # save_in_file
# Saves in a file `.tour` the solution found following the standard for the files `.tour`
# <br>
# The `filename` will have the informations about how the solution has been found, separated by a underscore

# In[ ]:


def save_in_file(filename,firstSolution,howToSolve,improvement,speedup, finalTour):

    file1 = open("Network Optimization\\solutions\\sol"+str(filename[:-4])+"_"+str(firstSolution)+"_"+str(howToSolve)+"_"+str(improvement)+"_"+str(speedup)+"_"+str(datetime.datetime.timestamp(datetime.datetime.now()))+".tour","a") 
    file1.write("NAME : sol"+str(filename[:-4])+".tour\n")
    file1.write("COMMENT : Solution  for "+str(filename[:-4])+"\n")
    file1.write("TYPE : TOUR\n")
    dimension = len(finalTour)-1
    file1.write("DIMENSION : "+str(dimension)+"\n")
    file1.write("TOUR_SECTION\n")
    for i in range(len(finalTour)-1):
        file1.write((str)(finalTour[i])+"\n")
    file1.write("-1")
    file1.close() 


# # draw_tour
# Elaborates a graph from the list of cities with `networkx`

# In[ ]:


import networkx as nx
def draw_tour(t): 
    global problem
    G = nx.Graph()
    for i in range(len(t)-1):
        G.add_node(i+1,pos = problem.node_coords[i+1])
    for i in range(len(t)-1):
        G.add_edge(t[i],t[i+1],length = distance(t[i],t[i+1]))
    pos = nx.spring_layout(G, seed = 100)
    nx.draw(G, pos = pos, with_labels=True, node_color='orange', node_size=400, edge_color='black', linewidths=1, font_size=15) # it draws the graph, but coming awful, it is then passed the graph elaborated here to plotly
    edge_labels = nx.get_edge_attributes(G,'length')
    nx.draw_networkx_edge_labels(G, pos, edge_labels = edge_labels,  font_size = 12) #prints weight on all the edges (with many nodes it is impossible to see anything)
    return G


# # plot_tour
# Plots the tour with `plotly` using the graph obtained by `networkx`

# In[ ]:


import plotly.graph_objects as go
def plot_tour(G):
    #to draw the edges, saved in G
    edge_x = []
    edge_y = []
    for edge in G.edges(): 
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    #to draw the nodes, saved in G
    node_x = []
    node_y = []
    for node in G.nodes(): 
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu', #to indicate with different colors the nodes with different number of connections (they all must have exactly 2 connections, so they must be all of the same color)
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))
    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append('# of connections: '+str(len(adjacencies[1])))

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title='<br>Network graph of the tour',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.show()

