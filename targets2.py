import emcli
import login

mytargets = emcli.get_targets \
    (targets='oraoem1%:%;oms12c1_%_oraoem1:%oracle%') \
    .out()['data']

for targ in mytargets:
    print('Target: ' + targ['Target Name'])
