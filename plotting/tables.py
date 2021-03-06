from plotting.general import abbreviations, cost_cs


def uls_forces_table(name, cross_sections, all_uls=False):
    text = open(name + ".txt", 'w')
    text.write(r"\begin{tabular}{llcccc}" + "\n")
    text.write(r"\hline" + "\n")
    text.write(r"Segment & Limit state & Normal force & Moment-y & Moment-z & Demand/Capacity \\" + "\n")
    text.write(r" & & [MN]   & [MNm] & [MNm] & [-] \\ \hline" + "\n")
    for cs in cross_sections:
        name = cs.name
        length = len(cs.effects)
        if all_uls:
            text.write(r"\multirow{" + str(length + 1) + "}{*}{" + name + "}")
        else:
            text.write(r"\multirow{2}{*}{" + name + "}")

        dc_max = 0
        uls_max = ''
        for uls_type in cs.effects:
            p = cs.effects[uls_type]['Normal Force'][2] / 1000
            mz = cs.effects[uls_type]['Moment'][2] / 1000 if 'Moment' in cs.effects[uls_type] else 0
            my = cs.effects[uls_type]['Moment y'][2] / 1000 if 'Moment y' in cs.effects[uls_type] else 0
            d_c = cs.degree_of_compliance[uls_type]
            if d_c > dc_max:
                dc_max = d_c
                uls_max = uls_type
            if all_uls:
                text.write(" & " + uls_type.replace('_', ' ') + f" & {p:.1f} & {mz:.1f} & {my:.1f} & " + f"{d_c:.2f}" + r"\\" + "\n")

        if not all_uls:
            p = cs.effects[uls_max]['Normal Force'][2] / 1000
            my = cs.effects[uls_max]['Moment y'][2] / 1000 if 'Moment y' in cs.effects[uls_max] else 0
            mz = cs.effects[uls_max]['Moment'][2] / 1000 if 'Moment' in cs.effects[uls_max] else 0
            d_c = cs.degree_of_compliance[uls_max]
            text.write(" & " + uls_max.replace('_', ' ') + f" & {p:.1f} & {mz:.1f} & {my:.1f} & " + f"{d_c:.2f}" + r"\\" + "\n")

    text.write(r"\end{tabular}" + "\n")

    text.close()
    return


def dc_table(name, cross_sections, uls_types="", base_case=False):
    if not uls_types:
        uls_types = []
        for cs in cross_sections:
            for key in cs.degree_of_compliance.keys():
                if key not in uls_types:
                    uls_types.append(key)

    n = len(uls_types)
    text = open(name + ".txt", 'w')
    text.write(r"\begin{tabular}{l" + "c" * n)
    if base_case:
        text.write("cl")
    text.write("}" + "\n")
    text.write(r"\hline" + "\n")

    if base_case:
        text.write(r"Segment & \multicolumn{" + str(n + 1) + r"}{c}{Demand / Capacity} & \\" + "\n")
    else:
        text.write(r"Segment & \multicolumn{" + str(n) + r"}{c}{Demand / Capacity} \\" + "\n")

    for uls_type in uls_types:
        text.write(" & " + uls_type.replace('_', ' ').replace('Strength', 'S').replace('Tie ', '').replace('Cable ', ''))
    if base_case:
        text.write(r" & Base case & ")
    text.write(r"\\ \hline "+"\n")

    for cs in cross_sections:
        text.write(cs.name)
        dcs = []
        for uls_type in uls_types:
            if uls_type not in cs.degree_of_compliance:
                dc = 0
            else:
                dc = cs.degree_of_compliance[uls_type]
            dcs.append(dc)
        for dc in dcs:
            if dc == max(dcs):
                text.write(r" & \textbf{" + f"{dc:.2f}" + r"}")
            elif dc == 0:
                text.write(r" & - ")
            else:
                text.write(f" & {dc:.2f}")
        if base_case:
            text.write(r" & \textbf{" + f"{cs.dc_ref:.2f}" + r"} & (" + r")")
        text.write(r"\\ " + "\n")

    text.write(r"\hline" + "\n")
    text.write(r"\end{tabular}" + "\n")
    text.close()
    return


def cost_table(name, cross_sections, anchorages):
    text = open(name + ".txt", 'w')
    text.write(r"\begin{tabular}{lcccccc}" + "\n")
    text.write(r"\hline" + "\n")
    text.write(r"Segment & Length & Weight & Unit cost & D/C$_{max}$ & D/C$_{ref}$ & Cost \\" + "\n")
    text.write(r" & [m] & [kg/m] & [\$/kg] & [-] & [-] & [\$ Mio.] \\ \hline" + "\n")

    costs = 50000
    for cs in cross_sections:
        name = cs.name
        length = cs.length
        unit_cost = cs.unit_cost
        unit_weight = cs.unit_weight
        dc_ref = cs.dc_ref
        dc_max = cs.dc_max
        cost = cs.cost
        costs += cost
        text.write(name + ' & ' + f"{length:.0f}" + ' & ' + f"{unit_weight:.0f}" + ' & ' + f"{unit_cost:.1f}")
        text.write(' & ' + f"{dc_max:.2f}" + ' & ' + f"{dc_ref:.2f}" + ' & ' + f"{cost / 10 ** 6:.2f}" + r" \\" + "\n")

    text.write(r"\arrayrulecolor{gray} \hline" + "\n")
    text.write("- Anchorages & " + str(anchorages[0]) + " ea & " + f"{anchorages[1]:.0f}" + ' kg/ea & ' + f"{anchorages[2]:.1f}")
    text.write(r" \$/kg & " + f"{dc_max:.2f}" + ' & ' + f"{dc_ref:.2f}" + ' & ' + f"{anchorages[3] / 10 ** 6:.2f}" + r" \\" + "\n")
    text.write(r"- Testing & - & - & 50000 \$ & - & - & 0.05 \\ \hline" + "\n")
    costs += anchorages[3]
    text.write("& & & & & & " + f"{costs / 10 ** 6:.2f}" + r" \\ \hhline{~~~~~~ =}" + "\n")
    text.write(r"\end{tabular}" + "\n")
    text.close()
    return


def small_cost_overview_table(name, bridges):
    text = open(name + ".txt", 'w')
    text.write(r"\begin{tabular}{lcccc}" + "\n")
    text.write(r"\hline" + "\n")
    text.write(r"Model & Arch cost & Tie cost & Hanger cost & Total cost \\" + "\n")
    text.write(r" & [\$ Mio.] & [\$ Mio.] & [\$ Mio.] & [\$ Mio.] \\ \hline" + "\n")

    for name in bridges:
        bridge = bridges[name]
        costs = bridge.costs
        text.write(name + " & " + f"{sum(costs[0:3]) / 10 ** 6:.2f}" + " & " + f"{sum(costs[3:6]) / 10 ** 6:.2f}")
        text.write(" & " + f"{sum(costs[6:9]) / 10 ** 6:.2f}" + " & " + f"{bridge.cost / 10 ** 6:.2f}" + r" \\ " + "\n")
    text.write(r"\hline" + "\n")
    text.write(r"\end{tabular}" + "\n")
    text.close()

    return


def big_cost_overview_table(name, bridges):
    text = open(name + ".txt", 'w')
    text.write(r"\begin{tabular}{lcccccccccc}" + "\n")
    text.write(r"\hline" + "\n")
    text.write(r"Model & Arch 1 & Arch 2 & Arch 3")
    text.write("& Tie 1 & Tie 2 & Tie 3")
    text.write(r"& Hangers & Anchorages & Testing & Total \\" + "\n")
    text.write(r" & [\$ Mio.]"*10+r"\\ \hline" + "\n")

    for name in bridges:
        bridge = bridges[name]
        costs = bridge.costs
        text.write(name)
        for i in range(9):
            text.write(" & " + f"{costs[i] / 10 ** 6:.2f}")
        text.write(" & " + f"{bridge.cost / 10 ** 6:.2f}" + r" \\ " + "\n")
    text.write(r"\hline" + "\n")
    text.write(r"\end{tabular}" + "\n")
    text.close()
    return


def dc_overview_table(name, bridges, show_lc=True, slice_cs=slice(0, 7)):
    text = open(name + ".txt", 'w')
    n = slice_cs.indices(100)[1]

    text.write(r"\begin{tabular}{l"+"c"*n+"}" + "\n")
    text.write(r"\hline" + "\n")
    text.write(r"Model & \multicolumn{" + str(n) + r"}{c}{Demand / Capacity} \\" + "\n")
    for cs in cost_cs[slice_cs]:
        text.write(" & " + cs)
    text.write(r" \\ \hline" + "\n")

    for name in bridges:
        bridge = bridges[name]
        text.write(name)
        for cs in bridge.cost_cross_sections[slice_cs]:
            if show_lc:
                text.write(" & " + f"{cs.dc_max:.2f}"+" ("+abbreviations[cs.dc_max_limit_state]+')')
            else:
                text.write(" & " + f"{cs.dc_max:.2f}")
        text.write(r" \\ " + "\n")
    text.write(r"\hline" + "\n")
    text.write(r"\end{tabular}" + "\n")
    text.close()
    return
