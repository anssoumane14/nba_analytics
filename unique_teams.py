import pandas as pd

df_rs = pd.read_csv("flat_table/flat_rs_player.csv", encoding="utf-8-sig")

if "TEAM" in df_rs.columns:
    teams = df_rs["TEAM"].dropna().astype(str).unique()
elif "TM" in df_rs.columns:
    teams = df_rs["TM"].dropna().astype(str).unique()
else:
    raise ValueError("❌ Impossible de trouver la colonne TEAM ou TM")

teams = sorted(teams)

print("📑 Distinct team abbreviations in RS dataset:")
for t in teams:
    print(t)
"""
📑 Distinct team abbreviations in RS dataset:
2TM
3TM
4TM
5TM
ATL
BOS
BRK
BUF
CHA
CHH
CHI
CHO
CLE
DAL
DEN
DET
GSW
HOU
IND
KCK
LAC
LAL
MEM
MIA
MIL
MIN
NJN
NOH
NOJ
NOK
NOP
NYK
NYN
OKC
ORL
PHI
PHO
POR
SAC
SAS
SDC
SEA
TOR
UTA
VAN
WAS
WSB

"""