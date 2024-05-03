"""To test the antena choosing function manually"""
go_on = True
ant_orientation = 0
while go_on:
    inp = input("→: ")
    if "END" in inp:
        go_on = False
    elif "AN" in inp:
        ant_orientation = float(inp[2:])
    else:
        ant = 0
        az = float(inp)
        """
        if divmod(divmod(az - ant_orientation, 360)[1] + 45, 90)[0] in (4,0) :     
            ant = 1
        elif divmod(divmod(az - ant_orientation, 360)[1] + 45, 90)[0] == 1:
            ant = 2
        elif divmod(divmod(az - ant_orientation, 360)[1] + 45, 90)[0] == 2:
            ant = 3
        elif divmod(divmod(az - ant_orientation, 360)[1] + 45, 90)[0] == 3:
            ant = 4
        """
        print(divmod(az - ant_orientation + 45, 90))
        """
        if divmod(az - ant_orientation + 45, 90)[0] in (4,0) :     
            ant = 1
        elif divmod(az - ant_orientation + 45, 90)[0] == 1:
            ant = 2
        elif divmod(az - ant_orientation + 45, 90)[0] == 2:
            ant = 3
        elif divmod(az - ant_orientation + 45, 90)[0] == 3:
            ant = 4
        """
        if divmod(divmod(az - ant_orientation, 360)[1] + 45/2, 45)[0] in (8,0) :     
            ant = 1
        elif divmod(divmod(az - ant_orientation, 360)[1] + 45/2, 45)[0] == 1:
            ant = 12
        elif divmod(divmod(az - ant_orientation, 360)[1] + 45/2, 45)[0] == 2:
            ant = 2
        elif divmod(divmod(az - ant_orientation, 360)[1] + 45/2, 45)[0] == 3:
            ant = 23
        elif divmod(divmod(az - ant_orientation, 360)[1] + 45/2, 45)[0] == 4:
            ant = 3
        elif divmod(divmod(az - ant_orientation, 360)[1] + 45/2, 45)[0] == 5:
            ant = 34
        elif divmod(divmod(az - ant_orientation, 360)[1] + 45/2, 45)[0] == 6:
            ant = 4
        elif divmod(divmod(az - ant_orientation, 360)[1] + 45/2, 45)[0] == 7:
            ant = 41

        
        print(ant, end="\n")