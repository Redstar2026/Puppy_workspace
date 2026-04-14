"""
Generador de Dashboard Pricing SW11 vs SW10 · 2026
Datos jalados desde BigQuery tabla PGMB_PREMED_A0M1J1N
Generado por Code Puppy 🐶
"""

D_PAIS = """const D_PAIS = [
  {pais:"CR",sw:10,pgmb:.1123,mbmb:.7151,pg:.0553,mb:.7610,meta:.0364},
  {pais:"CR",sw:11,pgmb:.1080,mbmb:.7017,pg:.0502,mb:.7475,meta:.0366},
  {pais:"GT",sw:10,pgmb:.0754,mbmb:.7006,pg:.0320,mb:.7586,meta:.0357},
  {pais:"GT",sw:11,pgmb:.0828,mbmb:.7038,pg:.0428,mb:.7548,meta:.0351},
  {pais:"HN",sw:10,pgmb:.0704,mbmb:.7414,pg:.0683,mb:.7453,meta:.0495},
  {pais:"HN",sw:11,pgmb:.0693,mbmb:.7473,pg:.0680,mb:.7524,meta:.0496},
  {pais:"NI",sw:10,pgmb:.1079,mbmb:.8999,pg:.0867,mb:.9135,meta:.0471},
  {pais:"NI",sw:11,pgmb:.0989,mbmb:.8353,pg:.0822,mb:.8511,meta:.0467},
  {pais:"SV",sw:10,pgmb:.0869,mbmb:.8355,pg:.0687,mb:.8518,meta:.0451},
  {pais:"SV",sw:11,pgmb:.0871,mbmb:.8441,pg:.0722,mb:.8571,meta:.0447},
];"""

D_DIV = """const D_DIV = [
  {pais:"CR",div:"ABARROTES",sw:10,pgmb:.1043,mbmb:.8013,pg:.0650,mb:.8452,meta:.0327,peso:.2013},
  {pais:"CR",div:"ABARROTES",sw:11,pgmb:.0955,mbmb:.7790,pg:.0552,mb:.8228,meta:.0327,peso:.2125},
  {pais:"CR",div:"CONSUMO",sw:10,pgmb:.1104,mbmb:.7896,pg:.0687,mb:.8351,meta:.0366,peso:.0989},
  {pais:"CR",div:"CONSUMO",sw:11,pgmb:.1000,mbmb:.7696,pg:.0554,mb:.8133,meta:.0368,peso:.1012},
  {pais:"CR",div:"FARMACIA",sw:10,pgmb:.0641,mbmb:.3551,pg:.0347,mb:.4216,meta:.0235,peso:.0088},
  {pais:"CR",div:"FARMACIA",sw:11,pgmb:.0489,mbmb:.3493,pg:.0197,mb:.4222,meta:.0235,peso:.0089},
  {pais:"CR",div:"FRUTAS Y VEGETALES",sw:10,pgmb:.1798,mbmb:.7393,pg:.0498,mb:.8595,meta:.0604,peso:.0422},
  {pais:"CR",div:"FRUTAS Y VEGETALES",sw:11,pgmb:.2027,mbmb:.8319,pg:.0759,mb:.9061,meta:.0607,peso:.0424},
  {pais:"CR",div:"MG Y TEXTIL",sw:10,pgmb:.0668,mbmb:.6305,pg:.0026,mb:.7025,meta:.0200,peso:.0007},
  {pais:"CR",div:"MG Y TEXTIL",sw:11,pgmb:.0751,mbmb:.6235,pg:.0109,mb:.6942,meta:.0200,peso:.0007},
  {pais:"CR",div:"PROTEINAS/INDUSTRIAL",sw:10,pgmb:.1060,mbmb:.7457,pg:.0261,mb:.8334,meta:.0381,peso:.0966},
  {pais:"CR",div:"PROTEINAS/INDUSTRIAL",sw:11,pgmb:.1081,mbmb:.7397,pg:.0256,mb:.8289,meta:.0386,peso:.0976},
  {pais:"GT",div:"ABARROTES",sw:10,pgmb:.0683,mbmb:.7006,pg:.0290,mb:.7531,meta:.0329,peso:.1387},
  {pais:"GT",div:"ABARROTES",sw:11,pgmb:.0696,mbmb:.6918,pg:.0384,mb:.7335,meta:.0321,peso:.1449},
  {pais:"GT",div:"CONSUMO",sw:10,pgmb:.0962,mbmb:.6804,pg:.0500,mb:.7340,meta:.0382,peso:.0702},
  {pais:"GT",div:"CONSUMO",sw:11,pgmb:.0811,mbmb:.6630,pg:.0395,mb:.7115,meta:.0383,peso:.0703},
  {pais:"GT",div:"FARMACIA",sw:10,pgmb:.0592,mbmb:.8625,pg:.0421,mb:.8919,meta:.0332,peso:.0025},
  {pais:"GT",div:"FARMACIA",sw:11,pgmb:.0370,mbmb:.8362,pg:.0193,mb:.8720,meta:.0331,peso:.0025},
  {pais:"GT",div:"FRUTAS Y VEGETALES",sw:10,pgmb:.0577,mbmb:.7134,pg:.0203,mb:.7994,meta:.0459,peso:.0289},
  {pais:"GT",div:"FRUTAS Y VEGETALES",sw:11,pgmb:.1274,mbmb:.8776,pg:.0741,mb:.9171,meta:.0459,peso:.0287},
  {pais:"GT",div:"MG Y TEXTIL",sw:10,pgmb:.0412,mbmb:.4506,pg:-.0168,mb:.5798,meta:.0200,peso:.0002},
  {pais:"GT",div:"MG Y TEXTIL",sw:11,pgmb:.0574,mbmb:.4552,pg:-.0093,mb:.5863,meta:.0200,peso:.0002},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",sw:10,pgmb:.0766,mbmb:.6947,pg:.0246,mb:.7678,meta:.0357,peso:.0675},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",sw:11,pgmb:.0954,mbmb:.7685,pg:.0434,mb:.8235,meta:.0346,peso:.0686},
  {pais:"HN",div:"ABARROTES",sw:10,pgmb:.0719,mbmb:.7782,pg:.0703,mb:.7814,meta:.0480,peso:.0728},
  {pais:"HN",div:"ABARROTES",sw:11,pgmb:.0777,mbmb:.7941,pg:.0775,mb:.7967,meta:.0481,peso:.0744},
  {pais:"HN",div:"CONSUMO",sw:10,pgmb:.0760,mbmb:.7603,pg:.0734,mb:.7622,meta:.0545,peso:.0328},
  {pais:"HN",div:"CONSUMO",sw:11,pgmb:.0713,mbmb:.7583,pg:.0689,mb:.7593,meta:.0547,peso:.0326},
  {pais:"HN",div:"FARMACIA",sw:10,pgmb:.0643,mbmb:.7881,pg:.0571,mb:.7963,meta:.0544,peso:.0013},
  {pais:"HN",div:"FARMACIA",sw:11,pgmb:.0409,mbmb:.7830,pg:.0314,mb:.7986,meta:.0544,peso:.0013},
  {pais:"HN",div:"FRUTAS Y VEGETALES",sw:10,pgmb:.0805,mbmb:.8394,pg:.0752,mb:.8511,meta:.0520,peso:.0100},
  {pais:"HN",div:"FRUTAS Y VEGETALES",sw:11,pgmb:.0618,mbmb:.8145,pg:.0565,mb:.8291,meta:.0519,peso:.0100},
  {pais:"HN",div:"MG Y TEXTIL",sw:10,pgmb:.0854,mbmb:.4540,pg:-.0266,mb:.5792,meta:.0200,peso:.0000},
  {pais:"HN",div:"MG Y TEXTIL",sw:11,pgmb:.0670,mbmb:.4351,pg:-.0307,mb:.6004,meta:.0200,peso:.0000},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",sw:10,pgmb:.0607,mbmb:.6358,pg:.0587,mb:.6451,meta:.0478,peso:.0390},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",sw:11,pgmb:.0545,mbmb:.6506,pg:.0533,mb:.6587,meta:.0478,peso:.0390},
  {pais:"NI",div:"ABARROTES",sw:10,pgmb:.1138,mbmb:.9037,pg:.0930,mb:.9189,meta:.0407,peso:.0500},
  {pais:"NI",div:"ABARROTES",sw:11,pgmb:.0949,mbmb:.8272,pg:.0803,mb:.8401,meta:.0397,peso:.0661},
  {pais:"NI",div:"CONSUMO",sw:10,pgmb:.1118,mbmb:.9255,pg:.0925,mb:.9404,meta:.0458,peso:.0222},
  {pais:"NI",div:"CONSUMO",sw:11,pgmb:.1092,mbmb:.8256,pg:.0941,mb:.8449,meta:.0467,peso:.0290},
  {pais:"NI",div:"FARMACIA",sw:10,pgmb:.0824,mbmb:.8135,pg:.0733,mb:.8236,meta:.0540,peso:.0011},
  {pais:"NI",div:"FARMACIA",sw:11,pgmb:.0733,mbmb:.8247,pg:.0712,mb:.8354,meta:.0543,peso:.0014},
  {pais:"NI",div:"FRUTAS Y VEGETALES",sw:10,pgmb:.1520,mbmb:.9291,pg:.1384,mb:.9350,meta:.1027,peso:.0121},
  {pais:"NI",div:"FRUTAS Y VEGETALES",sw:11,pgmb:.1556,mbmb:.9470,pg:.1414,mb:.9512,meta:.1027,peso:.0098},
  {pais:"NI",div:"MG Y TEXTIL",sw:10,pgmb:.1263,mbmb:.6393,pg:.0716,mb:.7191,meta:.0200,peso:.0000},
  {pais:"NI",div:"MG Y TEXTIL",sw:11,pgmb:.1568,mbmb:.6685,pg:.1079,mb:.7694,meta:.0200,peso:.0000},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",sw:10,pgmb:.0691,mbmb:.9191,pg:.0407,mb:.9255,meta:.0519,peso:.0229},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",sw:11,pgmb:.0791,mbmb:.8629,pg:.0541,mb:.8786,meta:.0520,peso:.0279},
  {pais:"SV",div:"ABARROTES",sw:10,pgmb:.0970,mbmb:.8358,pg:.0722,mb:.8496,meta:.0427,peso:.0517},
  {pais:"SV",div:"ABARROTES",sw:11,pgmb:.0981,mbmb:.8426,pg:.0793,mb:.8519,meta:.0424,peso:.0533},
  {pais:"SV",div:"CONSUMO",sw:10,pgmb:.1289,mbmb:.8400,pg:.1045,mb:.8620,meta:.0518,peso:.0223},
  {pais:"SV",div:"CONSUMO",sw:11,pgmb:.1269,mbmb:.8507,pg:.1044,mb:.8651,meta:.0513,peso:.0224},
  {pais:"SV",div:"FARMACIA",sw:10,pgmb:.0745,mbmb:.9435,pg:.0702,mb:.9566,meta:.0323,peso:.0014},
  {pais:"SV",div:"FARMACIA",sw:11,pgmb:.0110,mbmb:.8798,pg:.0068,mb:.9099,meta:.0323,peso:.0014},
  {pais:"SV",div:"FRUTAS Y VEGETALES",sw:10,pgmb:.0472,mbmb:.6354,pg:.0475,mb:.6439,meta:.0499,peso:.0118},
  {pais:"SV",div:"FRUTAS Y VEGETALES",sw:11,pgmb:.0414,mbmb:.7281,pg:.0437,mb:.7304,meta:.0499,peso:.0118},
  {pais:"SV",div:"MG Y TEXTIL",sw:10,pgmb:.0504,mbmb:.5897,pg:-.0452,mb:.6450,meta:.0200,peso:.0001},
  {pais:"SV",div:"MG Y TEXTIL",sw:11,pgmb:.0818,mbmb:.5905,pg:-.0036,mb:.6781,meta:.0200,peso:.0001},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",sw:10,pgmb:.0584,mbmb:.8666,pg:.0479,mb:.8762,meta:.0428,peso:.0341},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",sw:11,pgmb:.0623,mbmb:.9099,pg:.0525,mb:.9183,meta:.0425,peso:.0336},
];"""

D_ITEMS = """const D_ITEMS = [
  {pais:"CR",div:"PROTEINAS/INDUSTRIAL",cat:"EGGS - D93",item:75006091,desc:"HUEVO GALLINA MARRON KG",marca:"MARKETSIDE",pgmb:-.0047,mbmb:.2927,pg:-.2503,meta:.0288,peso:.0090,desv:.0335},
  {pais:"CR",div:"FRUTAS Y VEGETALES",cat:"FRUIT D94",item:70149316,desc:"BANANO SELECCION ESPECIAL KILO",marca:"HORTIFRUTI",pgmb:.0123,mbmb:1.0,pg:.0123,meta:.0725,peso:.0057,desv:.0602},
  {pais:"CR",div:"CONSUMO",cat:"PAPER TOWELS D04",item:70067855,desc:"TOALLA SULI COCINA 60HD 3 ROLL",marca:"SULI",pgmb:.1887,mbmb:.8333,pg:.0926,meta:.0300,peso:.0045,desv:.1587},
  {pais:"CR",div:"PROTEINAS/INDUSTRIAL",cat:"MILK D90",item:9001750,desc:"LECH LIQ DOS P HOMOG 2PORC 3785ML",marca:"DOS PINOS",pgmb:.0659,mbmb:1.0,pg:.0241,meta:.0458,peso:.0043,desv:.0202},
  {pais:"CR",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:9401764,desc:"CEBOLLA KG 2DA CALIDAD",marca:"HORTIFRUTI",pgmb:.1317,mbmb:.7692,pg:.0363,meta:.0600,peso:.0036,desv:.0717},
  {pais:"CR",div:"CONSUMO",cat:"TOILET TISSUE D04",item:70478347,desc:"PH SULI 1P 4R 1000 HOJAS 629GR",marca:"SULI",pgmb:.1780,mbmb:.5556,pg:.0226,meta:.0300,peso:.0031,desv:.1480},
  {pais:"CR",div:"CONSUMO",cat:"BLEACH D13",item:75167226,desc:"CLORO SULI BT 3785 ML GALON",marca:"SULI",pgmb:.1389,mbmb:.7333,pg:-.0031,meta:.0325,peso:.0028,desv:.1064},
  {pais:"CR",div:"ABARROTES",cat:"BEVERAGES D95",item:9522120,desc:"COCA COLA ORIGINAL PE 3000ML",marca:"COCA-COLA",pgmb:.0130,mbmb:.7273,pg:-.0045,meta:.0444,peso:.0027,desv:.0314},
  {pais:"CR",div:"ABARROTES",cat:"RICE D92",item:75242122,desc:"ARROZ SABEMAS GRANO ENTERO 1500GR",marca:"SABEMAS",pgmb:.2052,mbmb:.7143,pg:.0894,meta:.0218,peso:.0027,desv:.1834},
  {pais:"CR",div:"PROTEINAS/INDUSTRIAL",cat:"POULTRY D93",item:70011346,desc:"PECHUGA ENTERA DE POLLO KG",marca:"DON CRISTOBAL",pgmb:.1266,mbmb:1.0,pg:.0647,meta:.0559,peso:.0026,desv:.0706},
  {pais:"CR",div:"ABARROTES",cat:"SUGAR D92",item:9211753,desc:"AZUCAR DONA M REG BCO 1000 GR",marca:"DONA MARIA",pgmb:.0505,mbmb:.9259,pg:.0144,meta:.0197,peso:.0026,desv:.0308},
  {pais:"CR",div:"PROTEINAS/INDUSTRIAL",cat:"PORK D93",item:75375013,desc:"CHULETA ECONOMICA DE CERDO 1 KG",marca:"DON CRISTOBAL",pgmb:.2296,mbmb:.8571,pg:.0944,meta:.0429,peso:.0024,desv:.1866},
  {pais:"CR",div:"ABARROTES",cat:"COFFEE D92",item:70392159,desc:"CAFE LEYENDA MOLIDO 1000 GR",marca:"LEYENDA",pgmb:.1496,mbmb:1.0,pg:.1477,meta:.0713,peso:.0023,desv:.0783},
  {pais:"CR",div:"PROTEINAS/INDUSTRIAL",cat:"PORK D93",item:75375016,desc:"POSTA DE CERDO 1 KG",marca:"DON CRISTOBAL",pgmb:.1351,mbmb:.7805,pg:.0400,meta:.0395,peso:.0022,desv:.0956},
  {pais:"CR",div:"ABARROTES",cat:"BUTTER D92",item:70478386,desc:"MARGAR NUMAR CAJ 500 GR",marca:"NUMAR",pgmb:.0744,mbmb:.9697,pg:.0056,meta:.0672,peso:.0021,desv:.0071},
  {pais:"CR",div:"CONSUMO",cat:"ORAL CARE D02",item:70393628,desc:"CREMA DENT COLGATE CALC 50ML",marca:"COLGATE",pgmb:.0610,mbmb:.8333,pg:-.0223,meta:.0319,peso:.0021,desv:.0291},
  {pais:"CR",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:75121113,desc:"CHILE DULCE EA",marca:"HORTIFRUTI",pgmb:.4396,mbmb:1.0,pg:.2943,meta:.0600,peso:.0020,desv:.3796},
  {pais:"CR",div:"ABARROTES",cat:"BEANS D92",item:70000614,desc:"FRIJOL ROJO INDIANA 3000GR",marca:"INDIANA",pgmb:.0962,mbmb:1.0,pg:.0752,meta:.0604,peso:.0020,desv:.0358},
  {pais:"CR",div:"PROTEINAS/INDUSTRIAL",cat:"POULTRY D93",item:70011208,desc:"MUSLO POLLO FRESCO NACIONAL KG",marca:"DON CRISTOBAL",pgmb:.2267,mbmb:.9143,pg:.0681,meta:.0600,peso:.0019,desv:.1667},
  {pais:"CR",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:9402359,desc:"ZANAHORIA KG PRIMERA CALIDAD",marca:"HORTIFRUTI",pgmb:.3662,mbmb:.9512,pg:.0977,meta:.0561,peso:.0019,desv:.3102},
  {pais:"CR",div:"ABARROTES",cat:"SUGAR D92",item:70643818,desc:"AZUCAR DONA MARIA BLANCA 2000GR",marca:"DONA MARIA",pgmb:.0473,mbmb:.9697,pg:.0186,meta:.0196,peso:.0018,desv:.0277},
  {pais:"CR",div:"ABARROTES",cat:"SALT D92",item:75023226,desc:"SAL SOL CON FLUOR 500GR",marca:"SAL SOL",pgmb:.1211,mbmb:.6364,pg:-.0187,meta:.0387,peso:.0017,desv:.0824},
  {pais:"CR",div:"ABARROTES",cat:"SOUPS D92",item:70023456,desc:"CONSOME MAGGI POLLO 50 GR",marca:"MAGGI",pgmb:.0963,mbmb:.5455,pg:.0112,meta:.0685,peso:.0017,desv:.0277},
  {pais:"CR",div:"ABARROTES",cat:"SUGAR D92",item:70240507,desc:"AZUCAR SULI BLANCA 2000GR",marca:"SULI",pgmb:.0621,mbmb:.9500,pg:.0235,meta:.0212,peso:.0017,desv:.0409},
  {pais:"CR",div:"ABARROTES",cat:"MILK D95",item:75260389,desc:"LECHE SULI SEMIDESCREMADA UHT 3000ML",marca:"SULI",pgmb:.1070,mbmb:.6111,pg:-.0172,meta:.0200,peso:.0017,desv:.0870},
  {pais:"CR",div:"ABARROTES",cat:"BEANS D92",item:70634791,desc:"FRIJOL NEGRO INDIANA 1800 GR",marca:"INDIANA",pgmb:.1068,mbmb:1.0,pg:.1068,meta:.0588,peso:.0015,desv:.0480},
  {pais:"CR",div:"ABARROTES",cat:"SUGAR D92",item:70635167,desc:"AZUCAR DONA MARIA BLANCA 5000GR",marca:"DONA MARIA",pgmb:.0083,mbmb:.8485,pg:.0041,meta:.0195,peso:.0015,desv:.0111},
  {pais:"CR",div:"PROTEINAS/INDUSTRIAL",cat:"SEAFOOD D83",item:75381756,desc:"MIX MARISCOS 454 G",marca:"DELIMAR",pgmb:.1438,mbmb:1.0,pg:.1438,meta:.0288,peso:.0015,desv:.1150},
  {pais:"CR",div:"ABARROTES",cat:"WATER D95",item:75305183,desc:"40PACK AGUA PURIFICADA 20000ML",marca:"GREAT VALUE",pgmb:.0120,mbmb:.5455,pg:.0120,meta:.0559,peso:.0014,desv:.0438},
  {pais:"CR",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:75268253,desc:"TOMATE GRANEL KG",marca:"HORTIFRUTI",pgmb:.2009,mbmb:.7692,pg:.1097,meta:.0600,peso:.0014,desv:.1409},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",cat:"POULTRY D93",item:9328392,desc:"PIERNA CON CUADRIL POLLO IMPORTADA LB",marca:"DON CRISTOBAL",pgmb:.1219,mbmb:1.0,pg:.0498,meta:.0400,peso:.0033,desv:.0819},
  {pais:"GT",div:"CONSUMO",cat:"PAPER TOWELS D04",item:70009797,desc:"TOALLA DE PAPEL SULI BLANCA 3R 60H",marca:"SULI",pgmb:.1580,mbmb:1.0,pg:.1027,meta:.0309,peso:.0026,desv:.1271},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",cat:"PREPARED FOOD D39",item:70141864,desc:"POLLO ENTERO ROSTIZADO SABOR TEJANO",marca:"SIN MARCA",pgmb:.1166,mbmb:1.0,pg:.0588,meta:.0299,peso:.0018,desv:.0867},
  {pais:"GT",div:"CONSUMO",cat:"TOILET TISSUE D04",item:70168538,desc:"PAPEL HIGIENICO SULI 1000 HOJAS 6R",marca:"SULI",pgmb:.2082,mbmb:1.0,pg:.0652,meta:.0322,peso:.0017,desv:.1761},
  {pais:"GT",div:"FRUTAS Y VEGETALES",cat:"FRUIT D94",item:70359083,desc:"BANANO LIBRA",marca:"HORTIFRUTI",pgmb:.0861,mbmb:1.0,pg:.0802,meta:.0502,peso:.0017,desv:.0359},
  {pais:"GT",div:"ABARROTES",cat:"OILS D92",item:70464817,desc:"ACEITE SULI VEGETAL CON SOYA 800ML",marca:"SULI",pgmb:.1160,mbmb:1.0,pg:.0371,meta:.0223,peso:.0017,desv:.0937},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",cat:"PORK D93",item:70594694,desc:"CHULETA DE CERDO IMPORTADA MK LIBRA",marca:"MARKETSIDE",pgmb:.1286,mbmb:.9333,pg:.0286,meta:.0500,peso:.0017,desv:.0786},
  {pais:"GT",div:"ABARROTES",cat:"SUGAR D92",item:70629703,desc:"AZUCAR CANA REAL 2500 GR",marca:"CANA REAL",pgmb:.0417,mbmb:1.0,pg:.0125,meta:.0194,peso:.0017,desv:.0223},
  {pais:"GT",div:"ABARROTES",cat:"SUGAR D92",item:70635775,desc:"AZUCAR MORENA DE CANA 2000 GR",marca:"LOS TULIPANES",pgmb:.0392,mbmb:1.0,pg:.0116,meta:.0188,peso:.0016,desv:.0204},
  {pais:"GT",div:"CONSUMO",cat:"NAPKINS D04",item:70199459,desc:"SERVILLETA CUADRADA SULI 100G",marca:"SULI",pgmb:.2205,mbmb:1.0,pg:.0370,meta:.0304,peso:.0013,desv:.1900},
  {pais:"GT",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:9437779,desc:"TOMATE DE COCINA LIBRA",marca:"HORTIFRUTI",pgmb:.1694,mbmb:1.0,pg:.0945,meta:.0315,peso:.0013,desv:.1378},
  {pais:"GT",div:"FRUTAS Y VEGETALES",cat:"FRUIT D94",item:70496112,desc:"MANZANAS GALA HORTIFRUTI BOLSA",marca:"HORTIFRUTI",pgmb:.0527,mbmb:.9333,pg:.0423,meta:.0460,peso:.0013,desv:.0067},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",cat:"COLD CUTS D97",item:70431896,desc:"JAMON TOLEDO FAMILIAR 400 G",marca:"TOLEDO",pgmb:.2128,mbmb:1.0,pg:.1461,meta:.0492,peso:.0013,desv:.1636},
  {pais:"GT",div:"ABARROTES",cat:"MILK D95",item:70477012,desc:"FORMULA LACTEA NUTRILETY 946ML",marca:"LALA",pgmb:.0658,mbmb:1.0,pg:.0296,meta:.0443,peso:.0012,desv:.0215},
  {pais:"GT",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:75194894,desc:"TOMATE DE COCINA EN RED LIBRA",marca:"SIN MARCA",pgmb:.1964,mbmb:1.0,pg:.1199,meta:.0315,peso:.0012,desv:.1650},
  {pais:"GT",div:"ABARROTES",cat:"JUICES D95",item:70255321,desc:"JUGO DE LA GRANJA DE NARANJA 3400ML",marca:"DE LA GRANJA",pgmb:.0491,mbmb:1.0,pg:.0364,meta:.0442,peso:.0010,desv:.0049},
  {pais:"GT",div:"FRUTAS Y VEGETALES",cat:"FRUIT D94",item:9426145,desc:"MELON CANTALOUPE UNIDAD",marca:"HORTIFRUTI",pgmb:.2527,mbmb:.8000,pg:.1854,meta:.0536,peso:.0010,desv:.1991},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",cat:"COLD CUTS D97",item:9712390,desc:"SALCHICHA BREMEN 20 U",marca:"BREMEN",pgmb:-.0554,mbmb:.0000,pg:-.0285,meta:.0694,peso:.0010,desv:.1248},
  {pais:"GT",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:70222683,desc:"AJO HF IMPORTADO RED 3 UNIDADES",marca:"HORTIFRUTI",pgmb:.0501,mbmb:.9000,pg:.0510,meta:.0326,peso:.0010,desv:.0175},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",cat:"BAKERY D98",item:75218809,desc:"MAGDALENA NARANJA SULI AMB UND",marca:"SULI",pgmb:.3705,mbmb:1.0,pg:.0627,meta:.0300,peso:.0010,desv:.3405},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",cat:"EGGS D93",item:70691065,desc:"HUEVO SULI BLANCO MEDIANO 30 U",marca:"SULI",pgmb:.1775,mbmb:.8182,pg:.0170,meta:.0294,peso:.0010,desv:.1481},
  {pais:"GT",div:"ABARROTES",cat:"SEAFOOD D92",item:70085197,desc:"ATUN CALVO EN AGUA 3PK 426GR",marca:"CALVO",pgmb:-.0719,mbmb:.8462,pg:-.0749,meta:.0380,peso:.0010,desv:.1099},
  {pais:"GT",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:9425739,desc:"CEBOLLA BLANCA LIBRA",marca:"HORTIFRUTI",pgmb:.1505,mbmb:1.0,pg:.1150,meta:.0309,peso:.0009,desv:.1196},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",cat:"EGGS D93",item:9322484,desc:"HUEVO SULI BLANCO MEDIANO 30 U",marca:"SULI",pgmb:.1834,mbmb:1.0,pg:.0237,meta:.0300,peso:.0009,desv:.1534},
  {pais:"GT",div:"CONSUMO",cat:"NAPKINS D04",item:412229,desc:"SERVILLETA NUBE BLANCA 500UN",marca:"NUBE BLANCA",pgmb:.0623,mbmb:.6923,pg:.0584,meta:.0202,peso:.0009,desv:.0421},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",cat:"COLD CUTS D97",item:70147251,desc:"SALCHICHA PREMIER AHUMADA 54 U",marca:"PREMIER",pgmb:.1896,mbmb:.8529,pg:.0899,meta:.0207,peso:.0009,desv:.1690},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",cat:"EGGS D93",item:70004884,desc:"HUEVO SULI BLANCO MEDIANO 30 U",marca:"SULI",pgmb:.1550,mbmb:.7273,pg:-.0109,meta:.0300,peso:.0009,desv:.1250},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",cat:"PREPARED FOOD D39",item:70243838,desc:"POLLO ENTERO ROSTIZADO SABOR PIBIL",marca:"OM",pgmb:.1133,mbmb:1.0,pg:.0697,meta:.0239,peso:.0009,desv:.0894},
  {pais:"GT",div:"ABARROTES",cat:"SAUCES D92",item:9222135,desc:"SALSA NATURAS DE TOMATE RANCHERA 90GR",marca:"NATURAS",pgmb:.1008,mbmb:.8462,pg:.0554,meta:.0492,peso:.0009,desv:.0516},
  {pais:"GT",div:"PROTEINAS/INDUSTRIAL",cat:"BEEF D93",item:9313986,desc:"CARNE MOLIDA RES ESPECIAL 85C 15G LB",marca:"GRANEL",pgmb:.1088,mbmb:.7000,pg:.0294,meta:.0438,peso:.0009,desv:.0649},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",cat:"POULTRY D93",item:70285061,desc:"PECHUGA C ALAS MARKETSIDE FRESCO LB",marca:"MARKETSIDE",pgmb:.1101,mbmb:1.0,pg:.1083,meta:.0525,peso:.0016,desv:.0577},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",cat:"POULTRY D93",item:70285048,desc:"POLLO ENTERO MARKETSIDE FRESCO LB",marca:"MARKETSIDE",pgmb:.1317,mbmb:1.0,pg:.1313,meta:.0530,peso:.0014,desv:.0787},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",cat:"POULTRY D93",item:70285062,desc:"PIERNA C MUSLO MARKETSIDE FRESCO LB",marca:"MARKETSIDE",pgmb:.2690,mbmb:1.0,pg:.2695,meta:.0527,peso:.0013,desv:.2163},
  {pais:"HN",div:"ABARROTES",cat:"SNACKS D92",item:70588799,desc:"ZAMBOS YUMMIES PLATANO PICOSITAS 140GR",marca:"YUMMIES",pgmb:-.0120,mbmb:.7692,pg:-.0158,meta:.0485,peso:.0012,desv:.0605},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",cat:"EGGS D93",item:70279428,desc:"HUEVO SULI DE 30 UNIDADES",marca:"SULI",pgmb:.0071,mbmb:.8750,pg:.0074,meta:.0482,peso:.0011,desv:.0411},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",cat:"PORK D93",item:70446119,desc:"CHULETA CERDO IMP PROG CONG GRANEL LB",marca:"PROGCARNE",pgmb:.0204,mbmb:.8125,pg:.0240,meta:.0480,peso:.0010,desv:.0276},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",cat:"POULTRY D93",item:70285065,desc:"PECHUGA DESHUESA MARKETSIDE FRES LB",marca:"MARKETSIDE",pgmb:.0699,mbmb:1.0,pg:.0486,meta:.0451,peso:.0009,desv:.0248},
  {pais:"HN",div:"ABARROTES",cat:"BEVERAGES D95",item:9585071,desc:"BEBIDA COCA COLA GASEOSA 500 ML",marca:"COCA-COLA",pgmb:-.0147,mbmb:.0000,pg:-.0147,meta:.0532,peso:.0009,desv:.0679},
  {pais:"HN",div:"ABARROTES",cat:"MILK D95",item:70547855,desc:"LECHE LEYDE ENTERA UHT 900ML",marca:"LEYDE",pgmb:.1019,mbmb:1.0,pg:.1052,meta:.0535,peso:.0008,desv:.0484},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",cat:"PREPARED FOOD D39",item:75352471,desc:"POLLO ROSTIZADO TRADICIONAL UNIDAD",marca:"REY",pgmb:.0072,mbmb:.8182,pg:.0070,meta:.0215,peso:.0008,desv:.0142},
  {pais:"HN",div:"ABARROTES",cat:"MILK D95",item:9589628,desc:"LECHE SULA UHT DESLACTOSADA 1000ML",marca:"SULA",pgmb:.0477,mbmb:1.0,pg:.0481,meta:.0412,peso:.0008,desv:.0065},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",cat:"EGGS D93",item:70279040,desc:"HUEVO SULI 15 UNIDADES",marca:"SULI",pgmb:.0076,mbmb:.7000,pg:.0078,meta:.0500,peso:.0008,desv:.0424},
  {pais:"HN",div:"ABARROTES",cat:"SAUCES D92",item:70160327,desc:"PASTA TOMATE NATURAS TRADICIONAL 90GR",marca:"NATURAS",pgmb:.1397,mbmb:.8462,pg:.1403,meta:.0383,peso:.0007,desv:.1014},
  {pais:"HN",div:"ABARROTES",cat:"JUICES D95",item:70078968,desc:"JUGO SPORT VARIED 6 PACK 236ML",marca:"QUANTY",pgmb:.1767,mbmb:1.0,pg:.1767,meta:.0577,peso:.0007,desv:.1190},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",cat:"POULTRY D93",item:70285317,desc:"PATAS DE POLLO SULI FRESCO LB",marca:"MARKETSIDE",pgmb:.0399,mbmb:1.0,pg:.0386,meta:.0700,peso:.0007,desv:.0301},
  {pais:"HN",div:"ABARROTES",cat:"RICE D92",item:9246754,desc:"ARROZ BLANCO PROGRESO 1750GR",marca:"PROGRESSO",pgmb:-.0031,mbmb:.8462,pg:-.0075,meta:.0428,peso:.0006,desv:.0459},
  {pais:"HN",div:"ABARROTES",cat:"MILK D95",item:9575418,desc:"LECHE UHT ENTERA SULA 1000ML",marca:"SULA",pgmb:.0392,mbmb:1.0,pg:.0393,meta:.0418,peso:.0006,desv:.0025},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",cat:"PORK D93",item:70446238,desc:"COSTILLA CERDO TROZO PROG FRESC LB",marca:"PROGCARNE",pgmb:.0318,mbmb:1.0,pg:.0303,meta:.0481,peso:.0006,desv:.0163},
  {pais:"HN",div:"ABARROTES",cat:"BEVERAGES D95",item:70671132,desc:"BEBIDA COCA COLA GASEOSA 500 ML",marca:"COCA-COLA",pgmb:-.0152,mbmb:.0000,pg:-.0152,meta:.0589,peso:.0006,desv:.0741},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",cat:"CHEESE D90",item:70502047,desc:"QUESO CREMA DOS PINOS AMERICA 650GR",marca:"DOS PINOS",pgmb:.0313,mbmb:.7500,pg:.0300,meta:.0325,peso:.0006,desv:.0012},
  {pais:"HN",div:"CONSUMO",cat:"BAGS D04",item:70536719,desc:"PAPEL ALUMINIO ELMIGO 25 FT 1EA",marca:"ELMIGO",pgmb:.1274,mbmb:1.0,pg:.1274,meta:.0371,peso:.0005,desv:.0902},
  {pais:"HN",div:"ABARROTES",cat:"WATER D95",item:75305179,desc:"40PACK AGUA PURIFICADA 20000ML",marca:"GREAT VALUE",pgmb:.1109,mbmb:1.0,pg:.1109,meta:.0661,peso:.0005,desv:.0448},
  {pais:"HN",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:70386826,desc:"CULANTRO CASTILLA MAZO",marca:"SIN MARCA",pgmb:.0192,mbmb:.6250,pg:.0184,meta:.0433,peso:.0005,desv:.0240},
  {pais:"HN",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:9432354,desc:"ZANAHORIA SUELTA LIBRA",marca:"HORTIFRUTI",pgmb:.0937,mbmb:.8125,pg:.0936,meta:.0379,peso:.0005,desv:.0558},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",cat:"BAKERY D98",item:70268000,desc:"2 PACK BAGUETTE BLANC",marca:"SIN MARCA",pgmb:.1289,mbmb:1.0,pg:.1289,meta:.0368,peso:.0005,desv:.0921},
  {pais:"HN",div:"ABARROTES",cat:"BEVERAGES D95",item:9551150,desc:"GASEOSA COCA COLA 4PACK 8000ML",marca:"COCA-COLA",pgmb:.1482,mbmb:1.0,pg:.1482,meta:.0332,peso:.0005,desv:.1150},
  {pais:"HN",div:"PROTEINAS/INDUSTRIAL",cat:"BREAD D81",item:70088162,desc:"PAN MOLDE BIMBO MONARCA 540GR",marca:"MONARCA",pgmb:.0170,mbmb:1.0,pg:.0170,meta:.0428,peso:.0005,desv:.0258},
  {pais:"HN",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:9431899,desc:"PLATANO MADURO LIBRA",marca:"HORTIFRUTI",pgmb:.0664,mbmb:1.0,pg:.0238,meta:.0351,peso:.0005,desv:.0313},
  {pais:"HN",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:70386875,desc:"TOMATE PERA SUELTO LIBRA",marca:"SIN MARCA",pgmb:.0097,mbmb:.7500,pg:.0104,meta:.0376,peso:.0005,desv:.0279},
  {pais:"HN",div:"ABARROTES",cat:"PASTA D92",item:9286550,desc:"PASTA ESPAGUETTI BRUNI 200 GR",marca:"BRUNI",pgmb:.0284,mbmb:.3846,pg:.0545,meta:.0373,peso:.0005,desv:.0089},
  {pais:"NI",div:"ABARROTES",cat:"MILK D95",item:70332014,desc:"BEBIDA LACTEA NUTRI LETY 1000 ML",marca:"NUTRI LETY",pgmb:.1135,mbmb:1.0,pg:.0872,meta:.0447,peso:.0037,desv:.0688},
  {pais:"NI",div:"ABARROTES",cat:"SUGAR D92",item:70437129,desc:"AZUCAR SULFITADA GRANEL 110 LB",marca:"SIN",pgmb:.0596,mbmb:.1250,pg:.0000,meta:.0199,peso:.0017,desv:.0397},
  {pais:"NI",div:"ABARROTES",cat:"RICE D92",item:70410231,desc:"ARROZ 80 20 GRANEL",marca:"HORTIFRUTI",pgmb:.1449,mbmb:1.0,pg:.1341,meta:.0333,peso:.0014,desv:.1116},
  {pais:"NI",div:"ABARROTES",cat:"CONDIMENTS D92",item:70204953,desc:"NATURAS KETCHUP DOYPACK 385GR",marca:"NATURAS",pgmb:.1083,mbmb:.7500,pg:.0679,meta:.0593,peso:.0012,desv:.0491},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",cat:"BEEF D93",item:70688368,desc:"POSTA DE GALLINA LB",marca:"GRANEL",pgmb:.1568,mbmb:1.0,pg:.0654,meta:.0549,peso:.0011,desv:.1019},
  {pais:"NI",div:"ABARROTES",cat:"SALT D92",item:9244856,desc:"SAL ATLANTIDA FINA MOLIDA 454GR",marca:"ATLANTIDA",pgmb:.0789,mbmb:1.0,pg:.0292,meta:.0306,peso:.0010,desv:.0482},
  {pais:"NI",div:"ABARROTES",cat:"SUGAR D92",item:9236946,desc:"AZUCAR MOTE ROSA SULFITADA 400GR",marca:"MONTE ROSA",pgmb:.0295,mbmb:1.0,pg:.0089,meta:.0197,peso:.0010,desv:.0098},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",cat:"PORK D93",item:70515320,desc:"POSTA DE CERDO LIBRA",marca:"GRANEL",pgmb:.0526,mbmb:1.0,pg:.0030,meta:.0484,peso:.0009,desv:.0042},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",cat:"BEEF D93",item:70688365,desc:"HIGADO DE RES LB",marca:"GRANEL",pgmb:.1617,mbmb:1.0,pg:.0389,meta:.0580,peso:.0009,desv:.1036},
  {pais:"NI",div:"ABARROTES",cat:"SOUPS D92",item:70491404,desc:"SOPA DE POLLO MAGGI FIDEOS 55 GR",marca:"MAGGI",pgmb:.1909,mbmb:1.0,pg:.1878,meta:.0545,peso:.0008,desv:.1364},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",cat:"BEEF D93",item:75370847,desc:"HUESO ROJO ESPECIAL LB",marca:"GRANEL",pgmb:.0772,mbmb:.8750,pg:.0277,meta:.0545,peso:.0008,desv:.0227},
  {pais:"NI",div:"ABARROTES",cat:"RICE D92",item:9236393,desc:"ARROZ EL FAISAN 96 4 400GR",marca:"EL FAISAN",pgmb:.0144,mbmb:.5000,pg:-.0188,meta:.0444,peso:.0007,desv:.0301},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",cat:"POULTRY D93",item:70515360,desc:"PECHUGA CONO IQF LB",marca:"GRANEL",pgmb:.0098,mbmb:.8333,pg:.0001,meta:.0700,peso:.0007,desv:.0602},
  {pais:"NI",div:"CONSUMO",cat:"ORAL CARE D02",item:277687,desc:"CREMA COLGATE DENTAL TRIPLE ACCION 150ML",marca:"COLGATE",pgmb:.3269,mbmb:1.0,pg:.2844,meta:.0693,peso:.0007,desv:.2576},
  {pais:"NI",div:"ABARROTES",cat:"SOUPS D92",item:75106679,desc:"MAGGI CONSOME POLLO 5UND 50GR",marca:"MAGGI",pgmb:.1437,mbmb:1.0,pg:.1412,meta:.0335,peso:.0007,desv:.1102},
  {pais:"NI",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:70494175,desc:"TOMATE CRIOLLO LIBRA",marca:"HORTIFRUTI",pgmb:.0854,mbmb:1.0,pg:.0574,meta:.0886,peso:.0007,desv:.0033},
  {pais:"NI",div:"ABARROTES",cat:"COOKIES D92",item:70049129,desc:"GALLETA GAMA WAFFLE VAINILLA 240GR",marca:"GAMA",pgmb:.1343,mbmb:.8750,pg:.1075,meta:.0593,peso:.0007,desv:.0749},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",cat:"BEEF D93",item:75370842,desc:"CARNE DE RES PARA ASAR LB",marca:"GRANEL",pgmb:.0992,mbmb:1.0,pg:.0896,meta:.0532,peso:.0006,desv:.0460},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",cat:"BEEF D93",item:70515333,desc:"CARNE MOLIDA 90 10 LB",marca:"GRANEL",pgmb:.0395,mbmb:1.0,pg:.0384,meta:.0554,peso:.0006,desv:.0158},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",cat:"POULTRY D93",item:70515369,desc:"PIERNA DE POLLO SOLA FRESCA LIBRA",marca:"GRANEL",pgmb:.0672,mbmb:1.0,pg:.0499,meta:.0687,peso:.0006,desv:.0015},
  {pais:"NI",div:"FRUTAS Y VEGETALES",cat:"FRUIT D94",item:9416121,desc:"BANANO MADURO NACIONAL UNIDAD",marca:"HORTIFRUTI",pgmb:.0611,mbmb:.8750,pg:.0462,meta:.0614,peso:.0006,desv:.0003},
  {pais:"NI",div:"ABARROTES",cat:"CEREAL D92",item:9229890,desc:"AVENA SASA MOLIDA 400GR",marca:"SASA",pgmb:.0747,mbmb:.0000,pg:-.1058,meta:.0593,peso:.0006,desv:.0154},
  {pais:"NI",div:"ABARROTES",cat:"CRACKERS D92",item:70690641,desc:"GALLETA GAMA CLUB MAX SALADA 306 GR",marca:"GAMA",pgmb:.0220,mbmb:.5000,pg:-.0217,meta:.0596,peso:.0006,desv:.0376},
  {pais:"NI",div:"ABARROTES",cat:"JUICES D95",item:9543806,desc:"HI C 6 PACK REFRESCO SURTIDO 250 ML",marca:"HI-C",pgmb:.0291,mbmb:.8750,pg:.0230,meta:.0565,peso:.0006,desv:.0274},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",cat:"PORK D93",item:70515322,desc:"TROZOS DE CERDO LB",marca:"GRANEL",pgmb:.0136,mbmb:1.0,pg:.0070,meta:.0471,peso:.0006,desv:.0335},
  {pais:"NI",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:9416093,desc:"CEBOLLA AMARILLA SUELTA LIBRA",marca:"HORTIFRUTI",pgmb:.1447,mbmb:.8750,pg:.1187,meta:.0886,peso:.0006,desv:.0561},
  {pais:"NI",div:"CONSUMO",cat:"SHAVING D02",item:70035550,desc:"RASURADORA GILLETTE DESECH PERMA SHARP",marca:"GILLETTE",pgmb:.1419,mbmb:1.0,pg:.0649,meta:.0496,peso:.0005,desv:.0923},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",cat:"BEEF D93",item:70291360,desc:"POSTA DE CORONA LIBRA",marca:"GRANEL",pgmb:.1295,mbmb:1.0,pg:.0688,meta:.0562,peso:.0005,desv:.0733},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",cat:"CHEESE D90",item:70496714,desc:"QUESO CREMA DOS PINOS AMERICA 650GR",marca:"DOS PINOS",pgmb:.1089,mbmb:1.0,pg:.1077,meta:.0523,peso:.0005,desv:.0566},
  {pais:"NI",div:"PROTEINAS/INDUSTRIAL",cat:"BREAD D81",item:70289061,desc:"PAN MOLDE BIMBO MONARCA 540GR",marca:"BIMBO",pgmb:.0526,mbmb:1.0,pg:.0502,meta:.0437,peso:.0005,desv:.0090},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",cat:"POULTRY D93",item:9329106,desc:"PECHUGA SIN ALA POLLO IND LB 454G",marca:"POLLO INDIO",pgmb:-.0650,mbmb:.0000,pg:-.0592,meta:.0520,peso:.0023,desv:.1170},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",cat:"PREPARED FOOD D39",item:70267215,desc:"POLLO ROSTIZADO UNIDAD",marca:"POLLO INDIO",pgmb:.2072,mbmb:1.0,pg:.2072,meta:.0614,peso:.0020,desv:.1458},
  {pais:"SV",div:"ABARROTES",cat:"OILS D92",item:70464845,desc:"ACEITE SULI VEGETAL BOLSA 750 ML",marca:"SULI",pgmb:.2436,mbmb:1.0,pg:.0898,meta:.0300,peso:.0017,desv:.2136},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",cat:"BEEF D93",item:70367193,desc:"CARNE MOLIDA SUPER ESPECIAL LB 454G",marca:"DON CRISTOBAL",pgmb:.1858,mbmb:1.0,pg:.1083,meta:.0407,peso:.0013,desv:.1451},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",cat:"BEEF D93",item:70366477,desc:"CARNE MOLIDA ESPECIAL LB 454G",marca:"DON CRISTOBAL",pgmb:.0340,mbmb:.7857,pg:.0177,meta:.0455,peso:.0012,desv:.0115},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",cat:"BAKERY D98",item:75177348,desc:"PAN TIPO BAGUETTE PRODUCCION CRIO",marca:"BADU",pgmb:.1772,mbmb:1.0,pg:.1579,meta:.0155,peso:.0011,desv:.1618},
  {pais:"SV",div:"ABARROTES",cat:"BEVERAGES D95",item:70075952,desc:"GASEOSA COCA COLA PET 3000ML",marca:"COCA-COLA",pgmb:.1432,mbmb:1.0,pg:.1274,meta:.0562,peso:.0010,desv:.0869},
  {pais:"SV",div:"FRUTAS Y VEGETALES",cat:"FRUIT D94",item:70032332,desc:"BANANO LB 454 G",marca:"SIN MARCA",pgmb:.0870,mbmb:1.0,pg:.0894,meta:.0593,peso:.0010,desv:.0277},
  {pais:"SV",div:"ABARROTES",cat:"BEVERAGES D95",item:9554419,desc:"GASEOSA COCA COLA LATA 355 ML",marca:"COCA-COLA",pgmb:.0609,mbmb:1.0,pg:.0159,meta:.0713,peso:.0010,desv:.0104},
  {pais:"SV",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:9422736,desc:"TOMATE DE COCINA LB 454 G",marca:"SIN MARCA",pgmb:-.0067,mbmb:.0000,pg:-.0045,meta:.0317,peso:.0009,desv:.0384},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",cat:"PORK D93",item:70674053,desc:"COSTILLA DE CERDO TIPO RIBBLETS LB",marca:"DON CRISTOBAL",pgmb:.0449,mbmb:1.0,pg:.0426,meta:.0500,peso:.0008,desv:.0051},
  {pais:"SV",div:"CONSUMO",cat:"PAPER TOWELS D04",item:70009800,desc:"TOALLA DE PAPEL SULI BLANCA 60H 3R",marca:"SULI",pgmb:.1546,mbmb:1.0,pg:.1546,meta:.0408,peso:.0008,desv:.1138},
  {pais:"SV",div:"FRUTAS Y VEGETALES",cat:"FRUIT D94",item:70031919,desc:"UVA VERDE IMPORTADA LB 454 G",marca:"SIN MARCA",pgmb:-.2060,mbmb:.0000,pg:-.2031,meta:.0584,peso:.0008,desv:.2643},
  {pais:"SV",div:"FRUTAS Y VEGETALES",cat:"FRUIT D94",item:70033341,desc:"UVA RED GLOBE LB 454 G",marca:"SIN MARCA",pgmb:-.0187,mbmb:.0000,pg:-.0119,meta:.0565,peso:.0007,desv:.0752},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",cat:"BEEF D93",item:75302038,desc:"CARNE PARA GUISAR TROCITOS LB 454G",marca:"SIN MARCA",pgmb:.0797,mbmb:1.0,pg:.0718,meta:.0360,peso:.0007,desv:.0438},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",cat:"POULTRY D93",item:9311389,desc:"MUSLO PIERNA DE POLLO INDIO LB 454G",marca:"POLLO INDIO",pgmb:.1253,mbmb:1.0,pg:.1256,meta:.0474,peso:.0007,desv:.0779},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",cat:"BEEF D93",item:70367113,desc:"HUESO DE RES CORRIENTE LB 454G",marca:"DON CRISTOBAL",pgmb:.0338,mbmb:.7857,pg:-.0494,meta:.0469,peso:.0006,desv:.0132},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",cat:"BEEF D93",item:70367285,desc:"COSTILLA ALTA DE RES LB 454G",marca:"DON CRISTOBAL",pgmb:.0590,mbmb:1.0,pg:.0532,meta:.0462,peso:.0006,desv:.0128},
  {pais:"SV",div:"ABARROTES",cat:"BEVERAGES D95",item:70099787,desc:"GASEOSA COCA COLA PET 1250ML",marca:"COCA-COLA",pgmb:.1652,mbmb:1.0,pg:.1510,meta:.0560,peso:.0006,desv:.1091},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",cat:"POULTRY D93",item:9329099,desc:"CARNE MOLIDA DE POLLO INDIO LB 454G",marca:"POLLO INDIO",pgmb:.0510,mbmb:1.0,pg:.0521,meta:.0797,peso:.0006,desv:.0288},
  {pais:"SV",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:70050938,desc:"PLATANO LB 454 G",marca:"SIN MARCA",pgmb:.0327,mbmb:1.0,pg:.0396,meta:.0310,peso:.0006,desv:.0016},
  {pais:"SV",div:"PROTEINAS/INDUSTRIAL",cat:"BEEF D93",item:70367026,desc:"POSTA NEGRA LB 454G",marca:"DON CRISTOBAL",pgmb:-.0934,mbmb:.0000,pg:-.0905,meta:.0466,peso:.0006,desv:.1400},
  {pais:"SV",div:"ABARROTES",cat:"CRACKERS D92",item:70281485,desc:"GALLETA GAMA CLUB MAX SALADA 306G",marca:"GAMMA",pgmb:.0448,mbmb:1.0,pg:.0262,meta:.0548,peso:.0006,desv:.0100},
  {pais:"SV",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:9422813,desc:"PAPA SOLOMA LB 454 G",marca:"SIN MARCA",pgmb:.1183,mbmb:1.0,pg:.1251,meta:.0344,peso:.0006,desv:.0840},
  {pais:"SV",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:70382326,desc:"CILANTRO EN MANOJOS UNIDAD",marca:"SIN MARCA",pgmb:.0214,mbmb:1.0,pg:.0236,meta:.0524,peso:.0006,desv:.0309},
  {pais:"SV",div:"FRUTAS Y VEGETALES",cat:"FRUIT D94",item:70034970,desc:"LIMON PERSICO UNIDAD",marca:"SIN MARCA",pgmb:.1130,mbmb:1.0,pg:.1130,meta:.0586,peso:.0005,desv:.0544},
  {pais:"SV",div:"FRUTAS Y VEGETALES",cat:"VEGETABLES D94",item:9448307,desc:"AGUACATE HASS UNIDAD",marca:"SIN MARCA",pgmb:.1662,mbmb:1.0,pg:.1779,meta:.0600,peso:.0005,desv:.1062},
  {pais:"SV",div:"ABARROTES",cat:"SUGAR D92",item:70194104,desc:"AZUCAR BLANCA DEL CANAL 500GR",marca:"DEL CANAL",pgmb:.0363,mbmb:1.0,pg:.0324,meta:.0337,peso:.0005,desv:.0026},
  {pais:"SV",div:"ABARROTES",cat:"SNACKS D92",item:70164326,desc:"MIX KITTY DE SNACKS 560GR",marca:"KITTY",pgmb:.2695,mbmb:1.0,pg:.2695,meta:.0356,peso:.0005,desv:.2339},
  {pais:"SV",div:"ABARROTES",cat:"WATER D95",item:75305182,desc:"AGUA PURIFICADA GREAT VALUE 500 ML",marca:"GREAT VALUE",pgmb:.2105,mbmb:1.0,pg:.1600,meta:.0300,peso:.0005,desv:.1805},
];"""

CSS = """
  :root {
    --blue-100:#0053e2;--blue-110:#0047c7;--blue-130:#0035a0;
    --spark-100:#ffc220;--spark-140:#995213;--spark-10:#fff8e7;
    --red-100:#ea1100;--green-100:#2a8703;
    --gray-10:#f5f5f5;--gray-50:#c5c5c5;--gray-100:#8c8c8c;--gray-160:#1d1d1d;
  }
  *{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',system-ui,sans-serif}
  body{background:#f5f5f5;color:#1d1d1d;min-height:100vh}
  header{background:#0053e2;color:#fff;padding:16px 24px;display:flex;align-items:center;gap:16px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,.2)}
  header .logo{font-size:22px;font-weight:900;letter-spacing:-1px}
  header .subtitle{font-size:13px;opacity:.85}
  header .badge{margin-left:auto;background:#ffc220;color:#1d1d1d;border-radius:20px;padding:4px 14px;font-size:12px;font-weight:700}
  .container{max-width:1400px;margin:0 auto;padding:20px 16px}
  .kpi-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:20px}
  .kpi{background:#fff;border-radius:10px;padding:16px;border-left:4px solid var(--blue-100);box-shadow:0 1px 4px rgba(0,0,0,.08)}
  .kpi .label{font-size:11px;color:#8c8c8c;text-transform:uppercase;font-weight:600;margin-bottom:4px}
  .kpi .value{font-size:24px;font-weight:800;color:#0053e2}
  .kpi .delta{font-size:12px;margin-top:4px;font-weight:600}
  .delta.up{color:#2a8703} .delta.down{color:#ea1100} .delta.flat{color:#8c8c8c}
  .tabs{display:flex;gap:4px;margin-bottom:16px;flex-wrap:wrap;background:#fff;border-radius:10px;padding:8px;box-shadow:0 1px 4px rgba(0,0,0,.08)}
  .tab{padding:8px 16px;border:none;border-radius:8px;cursor:pointer;font-size:13px;font-weight:600;background:transparent;color:#8c8c8c;transition:all .2s}
  .tab:hover{background:#f5f5f5;color:#1d1d1d}
  .tab.active{background:#0053e2;color:#fff}
  .section{display:none} .section.active{display:block}
  .card{background:#fff;border-radius:10px;padding:20px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:16px}
  .card h2{font-size:15px;font-weight:700;margin-bottom:14px;color:#1d1d1d;border-bottom:2px solid #0053e2;padding-bottom:8px}
  .chart-wrap{position:relative;height:280px}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
  @media(max-width:768px){.grid2{grid-template-columns:1fr}}
  table{width:100%;border-collapse:collapse;font-size:12px}
  th{background:#0053e2;color:#fff;padding:8px 10px;text-align:left;font-weight:600;position:sticky;top:0}
  td{padding:7px 10px;border-bottom:1px solid #f5f5f5}
  tr:hover td{background:#f5f5f5}
  tr:nth-child(even) td{background:#fafafa}
  .pill{display:inline-block;border-radius:12px;padding:2px 8px;font-size:11px;font-weight:700}
  .pill.g{background:#e6f5e0;color:#2a8703}
  .pill.r{background:#fde9e8;color:#ea1100}
  .pill.y{background:#fff8e7;color:#995213}
  .pill.b{background:#e8eeff;color:#0053e2}
  .alert-bar{background:#fff8e7;border:1px solid #ffc220;border-left:4px solid #ffc220;border-radius:6px;padding:10px 14px;margin-bottom:14px;font-size:13px;color:#995213}
  .section-label{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:#8c8c8c;margin-bottom:8px}
  select,input{padding:6px 10px;border:1px solid #c5c5c5;border-radius:6px;font-size:13px;outline:none}
  select:focus,input:focus{border-color:#0053e2;box-shadow:0 0 0 2px rgba(0,83,226,.2)}
  .btn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;border:none;transition:all .2s}
  .btn-primary{background:#0053e2;color:#fff}.btn-primary:hover{background:#0047c7}
  .btn-secondary{background:#fff;color:#1d1d1d;border:1.5px solid #c5c5c5}.btn-secondary:hover{background:#f5f5f5}
  .tbl-wrap{max-height:420px;overflow-y:auto;border-radius:8px;border:1px solid #f0f0f0}
  .filter-row{display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap;align-items:center}
"""

JS = """
// ====== HELPERS ======
const pct = v => (v*100).toFixed(2)+"%";
const bps = v => {const s=Math.round(v*10000); return (s>0?"▲ +":"▼ ")+Math.abs(s)+" bps"};
const bpsRaw = v => Math.round(v*10000);
const clr = v => v>=0?"#2a8703":"#ea1100";
const countries = ["CR","GT","HN","NI","SV"];
const W_COLORS = ["#0053e2","#ffc220","#2a8703","#ea1100","#6b21a8","#0891b2"];
function getPais(p,sw){return D_PAIS.find(d=>d.pais===p&&d.sw===sw)}
function getDivPais(p,sw){return D_DIV.filter(d=>d.pais===p&&d.sw===sw)}

// ====== TABS ======
function showTab(id){
  document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tab-'+id).classList.add('active');
  event.target.classList.add('active');
  if(id==='pais') renderPaisDetail();
  if(id==='outliers') renderOutliers();
  if(id==='descarga') renderDescarga();
  if(id==='base100') renderBase100();
  if(id==='desviacion') renderDesviacion();
  if(id==='division') renderDivision();
  if(id==='meta') renderMeta();
}

// ====== KPIs ======
function buildKPIs(){
  const row=document.getElementById('kpi-row');
  const data=[
    {label:"Pais que MAS cae en PG MB",value:"NI",delta:"-90 bps SW10 a SW11",down:true},
    {label:"Pais que MAS sube en PG MB",value:"GT",delta:"+74 bps SW10 a SW11",up:true},
    {label:"Mayor caida %MB MB",value:"NI",delta:"-646 bps SW10 a SW11",down:true},
    {label:"Caida critica en division",value:"SV FARMACIA",delta:"-635 bps SW10 a SW11",down:true},
    {label:"Item critico SW11",value:"UVA VERDE SV",delta:"PG MB: -20.6% | Desv: +26.4pp",down:true},
    {label:"Paises sobre META PG MB",value:"5/5",delta:"Todos sobre meta global",up:true},
  ];
  row.innerHTML=data.map(d=>`
    <div class="kpi">
      <div class="label">${d.label}</div>
      <div class="value">${d.value}</div>
      <div class="delta ${d.down?'down':d.up?'up':'flat'}">${d.delta}</div>
    </div>`).join('');
}

// ====== OVERVIEW CHARTS ======
function buildOverview(){
  buildKPIs();
  const labels=countries;
  const sw10pgmb=countries.map(c=>getPais(c,10).pgmb*100);
  const sw11pgmb=countries.map(c=>getPais(c,11).pgmb*100);
  const sw10mbmb=countries.map(c=>getPais(c,10).mbmb*100);
  const sw11mbmb=countries.map(c=>getPais(c,11).mbmb*100);

  new Chart(document.getElementById('chartPgmbPais'),{
    type:'bar',
    data:{labels,datasets:[
      {label:'SW10',data:sw10pgmb,backgroundColor:'rgba(0,83,226,.5)',borderColor:'#0053e2',borderWidth:2},
      {label:'SW11',data:sw11pgmb,backgroundColor:'rgba(255,194,32,.7)',borderColor:'#ffc220',borderWidth:2},
    ]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top'},
      tooltip:{callbacks:{label:ctx=>`${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)}%`}}},
      scales:{y:{ticks:{callback:v=>v+'%'},title:{display:true,text:'% PG MB'}}}}
  });

  new Chart(document.getElementById('chartMbmbPais'),{
    type:'bar',
    data:{labels,datasets:[
      {label:'SW10',data:sw10mbmb,backgroundColor:'rgba(42,135,3,.5)',borderColor:'#2a8703',borderWidth:2},
      {label:'SW11',data:sw11mbmb,backgroundColor:'rgba(234,17,0,.6)',borderColor:'#ea1100',borderWidth:2},
    ]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top'},
      tooltip:{callbacks:{label:ctx=>`${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)}%`}}},
      scales:{y:{min:60,ticks:{callback:v=>v+'%'},title:{display:true,text:'% MB MB'}}}}
  });

  const bpsData=countries.map(c=>bpsRaw(getPais(c,11).pgmb-getPais(c,10).pgmb));
  new Chart(document.getElementById('chartBps'),{
    type:'bar',
    data:{labels,datasets:[{
      label:'Delta BPS en % PG MB (SW11 - SW10)',
      data:bpsData,
      backgroundColor:bpsData.map(v=>v>=0?'rgba(42,135,3,.7)':'rgba(234,17,0,.7)'),
      borderColor:bpsData.map(v=>v>=0?'#2a8703':'#ea1100'),
      borderWidth:2
    }]},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{legend:{position:'top'},tooltip:{callbacks:{label:ctx=>`${ctx.parsed.y>0?'+':''}${ctx.parsed.y} BPS`}}},
      scales:{y:{ticks:{callback:v=>(v>0?'+':'')+v+' bps'},title:{display:true,text:'Delta BPS'}},
        x:{grid:{display:false}}}}
  });
}

// ====== PAIS DETAIL ======
let chartPaisDiv=null, chartDivDelta=null;
function renderPaisDetail(){
  const p=document.getElementById('selectPais').value;
  const sw10=getPais(p,10), sw11=getPais(p,11);
  const delta_pgmb=sw11.pgmb-sw10.pgmb, delta_mbmb=sw11.mbmb-sw10.mbmb;

  document.getElementById('paisKpis').innerHTML=`
    <table><thead><tr><th>Metrica</th><th>SW10</th><th>SW11</th><th>Delta BPS</th><th>META</th><th>vs Meta</th></tr></thead>
    <tbody>
      <tr><td><b>% PG MB</b></td><td>${pct(sw10.pgmb)}</td><td>${pct(sw11.pgmb)}</td>
          <td style="color:${clr(delta_pgmb)}">${bps(delta_pgmb)}</td><td>${pct(sw11.meta)}</td>
          <td><span class="pill ${sw11.pgmb>=sw11.meta?'g':'r'}">${sw11.pgmb>=sw11.meta?'Sobre':'Bajo'} meta</span></td></tr>
      <tr><td><b>% MB MB</b></td><td>${pct(sw10.mbmb)}</td><td>${pct(sw11.mbmb)}</td>
          <td style="color:${clr(delta_mbmb)}">${bps(delta_mbmb)}</td><td>-</td><td>-</td></tr>
      <tr><td><b>% PG</b></td><td>${pct(sw10.pg)}</td><td>${pct(sw11.pg)}</td>
          <td style="color:${clr(sw11.pg-sw10.pg)}">${bps(sw11.pg-sw10.pg)}</td><td>-</td><td>-</td></tr>
      <tr><td><b>% MB</b></td><td>${pct(sw10.mb)}</td><td>${pct(sw11.mb)}</td>
          <td style="color:${clr(sw11.mb-sw10.mb)}">${bps(sw11.mb-sw10.mb)}</td><td>-</td><td>-</td></tr>
    </tbody></table>`;

  const divs11=getDivPais(p,11);
  const divLabels=divs11.map(d=>d.div.length>12?d.div.substring(0,12)+'...':d.div);
  if(chartPaisDiv) chartPaisDiv.destroy();
  chartPaisDiv=new Chart(document.getElementById('chartPaisDivision'),{
    type:'bar',
    data:{labels:divLabels,datasets:[
      {label:'% PG MB SW11',data:divs11.map(d=>+(d.pgmb*100).toFixed(2)),backgroundColor:'rgba(0,83,226,.7)',borderColor:'#0053e2',borderWidth:2},
      {label:'META',data:divs11.map(d=>+(d.meta*100).toFixed(2)),type:'line',borderColor:'#ea1100',borderWidth:2,borderDash:[6,3],pointRadius:5,pointBackgroundColor:'#ea1100',fill:false},
    ]},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{tooltip:{callbacks:{label:ctx=>`${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)}%`}}},
      scales:{y:{ticks:{callback:v=>v+'%'}}}}
  });

  const divs10=getDivPais(p,10);
  const deltaDiv=divs11.map((d,i)=>+((d.pgmb-divs10[i].pgmb)*10000).toFixed(0));
  if(chartDivDelta) chartDivDelta.destroy();
  chartDivDelta=new Chart(document.getElementById('chartDivDelta'),{
    type:'bar',
    data:{labels:divLabels,datasets:[{
      label:'Delta BPS PG MB (SW11-SW10)',
      data:deltaDiv,
      backgroundColor:deltaDiv.map(v=>v>=0?'rgba(42,135,3,.7)':'rgba(234,17,0,.7)'),
      borderColor:deltaDiv.map(v=>v>=0?'#2a8703':'#ea1100'),borderWidth:2
    }]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{y:{ticks:{callback:v=>(v>0?'+':'')+v+' bps'}}}}
  });
}

// ====== DIVISION ======
let chartDivAll=null;
function renderDivision(){
  const allDivs=[...new Set(D_DIV.map(d=>d.div))];
  const ds=countries.map((c,i)=>{
    const vals=allDivs.map(div=>{
      const found=D_DIV.find(d=>d.pais===c&&d.div===div&&d.sw===11);
      return found?+(found.pgmb*100).toFixed(2):null;
    });
    return{label:c,data:vals,backgroundColor:W_COLORS[i]+'99',borderColor:W_COLORS[i],borderWidth:2};
  });
  if(chartDivAll) chartDivAll.destroy();
  chartDivAll=new Chart(document.getElementById('chartDivAll'),{
    type:'bar',
    data:{labels:allDivs.map(d=>d.length>14?d.substring(0,14)+'...':d),datasets:ds},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top'}},
      scales:{x:{stacked:false},y:{ticks:{callback:v=>v+'%'},title:{display:true,text:'% PG MB SW11'}}}}
  });

  const html=allDivs.map(div=>`
    <div style="margin-bottom:10px">
      <div class="section-label">${div}</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        ${countries.map(c=>{
          const d=D_DIV.find(x=>x.pais===c&&x.div===div&&x.sw===11);
          if(!d) return '';
          const ok=d.pgmb>=d.meta;
          return `<span class="pill ${ok?'g':'r'}" title="${pct(d.pgmb)} vs META ${pct(d.meta)}">${c} ${ok?'OK':'BAJO'}</span>`;
        }).join('')}
      </div>
    </div>`).join('');
  document.getElementById('semaforoDivision').innerHTML=html;
}

// ====== META ======
let chartMetaPais=null;
function renderMeta(){
  const labels=countries;
  const pgmb=countries.map(c=>+(getPais(c,11).pgmb*100).toFixed(2));
  const meta=countries.map(c=>+(getPais(c,11).meta*100).toFixed(2));
  const gap=countries.map((c,i)=>+((pgmb[i]-meta[i]).toFixed(2)));
  if(chartMetaPais) chartMetaPais.destroy();
  chartMetaPais=new Chart(document.getElementById('chartMetaPais'),{
    type:'bar',
    data:{labels,datasets:[
      {label:'% PG MB SW11',data:pgmb,backgroundColor:'rgba(0,83,226,.7)',borderColor:'#0053e2',borderWidth:2},
      {label:'META',data:meta,type:'line',borderColor:'#ea1100',borderWidth:3,borderDash:[6,3],fill:false,pointRadius:6,pointBackgroundColor:'#ea1100'},
      {label:'Gap vs Meta (pp)',data:gap,type:'line',borderColor:'#2a8703',borderWidth:2,fill:false,pointRadius:5,pointStyle:'triangle'},
    ]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{y:{ticks:{callback:v=>v+'%'}}}}
  });

  const allDivs=[...new Set(D_DIV.map(d=>d.div))];
  let tbl=`<div class="tbl-wrap"><table><thead><tr><th>Division</th>${countries.map(c=>`<th>${c}</th>`).join('')}</tr></thead><tbody>`;
  allDivs.forEach(div=>{
    tbl+=`<tr><td><b>${div}</b></td>`;
    countries.forEach(c=>{
      const d=D_DIV.find(x=>x.pais===c&&x.div===div&&x.sw===11);
      if(!d){tbl+='<td>-</td>';return;}
      const diff=+((d.pgmb-d.meta)*100).toFixed(2);
      const bg=diff>=0?`rgba(42,135,3,${Math.min(0.8,diff/10+.1)})`:`rgba(234,17,0,${Math.min(0.8,Math.abs(diff)/10+.1)})`;
      tbl+=`<td style="background:${bg};color:#fff;font-weight:700;text-align:center">${diff>0?'+':''}${diff}pp</td>`;
    });
    tbl+='</tr>';
  });
  tbl+='</tbody></table></div>';
  document.getElementById('heatmapDiv').innerHTML=tbl;
}

// ====== OUTLIERS ======
function buildOutlierTable(items){
  if(!items.length) return '<p style="padding:12px;color:#8c8c8c">Sin datos para el filtro seleccionado.</p>';
  return`<table>
    <thead><tr><th>#</th><th>Pais</th><th>Division</th><th>Categoria</th><th>Item</th><th>Descripcion</th><th>Marca</th>
      <th>% PG MB</th><th>% MB MB</th><th>META</th><th>Desv vs Meta</th><th>Peso MB</th></tr></thead>
    <tbody>${items.map((d,i)=>`<tr>
      <td>${i+1}</td><td><span class="pill b">${d.pais}</span></td><td>${d.div}</td><td>${d.cat}</td>
      <td>${d.item}</td><td style="max-width:180px">${d.desc}</td><td>${d.marca}</td>
      <td style="color:${d.pgmb>=0?'#2a8703':'#ea1100'};font-weight:700">${pct(d.pgmb)}</td>
      <td>${pct(d.mbmb)}</td><td>${pct(d.meta)}</td>
      <td style="color:${d.desv>0?'#ea1100':'#2a8703'};font-weight:700">${d.desv>0?'+':''}${pct(d.desv)}</td>
      <td>${(d.peso*100).toFixed(3)}%</td></tr>`).join('')}
    </tbody></table>`;
}
function renderOutliers(){
  const fp=document.getElementById('filterPaisOut').value;
  const fd=document.getElementById('filterDivOut').value;
  let items=D_ITEMS.filter(d=>(!fp||d.pais===fp)&&(!fd||d.div===fd));
  const allDivs=[...new Set(D_ITEMS.map(d=>d.div))];
  const selDiv=document.getElementById('filterDivOut');
  if(selDiv.options.length<=1){
    allDivs.forEach(dv=>{const o=document.createElement('option');o.value=dv;o.text=dv;selDiv.appendChild(o);});
  }
  const neg=items.filter(d=>d.pgmb<0).sort((a,b)=>a.pgmb-b.pgmb);
  const pos=items.filter(d=>d.pgmb>=0).sort((a,b)=>b.pgmb-a.pgmb);
  document.getElementById('tblNeg').innerHTML=buildOutlierTable(neg);
  document.getElementById('tblPos').innerHTML=buildOutlierTable(pos);
}
function resetOutFilters(){
  document.getElementById('filterPaisOut').value='';
  document.getElementById('filterDivOut').value='';
  renderOutliers();
}

// ====== DESCARGA ======
function renderDescarga(){
  const selDiv=document.getElementById('dlDiv');
  if(selDiv.options.length<=1){
    [...new Set(D_ITEMS.map(d=>d.div))].forEach(dv=>{const o=document.createElement('option');o.value=dv;o.text=dv;selDiv.appendChild(o);});
  }
  const fp=document.getElementById('dlPais').value;
  const fd=document.getElementById('dlDiv').value;
  let items=D_ITEMS.filter(d=>(!fp||d.pais===fp)&&(!fd||d.div===fd));
  document.getElementById('tblDescarga').innerHTML=buildOutlierTable(items);
}
function downloadCSV(){
  const fp=document.getElementById('dlPais').value||'TODOS';
  const fd=document.getElementById('dlDiv').value||'TODOS';
  let items=D_ITEMS.filter(d=>(!fp||fp==='TODOS'||d.pais===fp)&&(!fd||fd==='TODOS'||d.div===fd));
  const hdr='PAIS,DIVISION,CATEGORIA,ITEM_NBR,DESCRIPCION,MARCA,PCT_PGMB,PCT_MB_MB,PCT_PG,META_PG,PESO_MB,DESV_VS_META\\n';
  const rows=items.map(d=>[d.pais,d.div,d.cat,d.item,`"${d.desc}"`,d.marca,
    pct(d.pgmb),pct(d.mbmb),pct(d.pg),pct(d.meta),(d.peso*100).toFixed(4)+'%',pct(d.desv)].join(',')).join('\\n');
  const blob=new Blob([hdr+rows],{type:'text/csv'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download=`outliers_pricegap_${fp}_${fd}_SW11_2026.csv`;a.click();
}

// ====== BASE 100 ======
let chartB100=null;
function renderBase100(){
  const p=document.getElementById('b100Pais').value;
  const dv=document.getElementById('b100Div').value;
  const sel=document.getElementById('b100Div');
  if(sel.options.length<=1){
    [...new Set(D_ITEMS.map(d=>d.div))].forEach(d=>{const o=document.createElement('option');o.value=d;o.text=d;sel.appendChild(o);});
  }
  let items=D_ITEMS.filter(d=>d.pais===p&&(!dv||d.div===dv));
  items.sort((a,b)=>b.peso-a.peso);
  const totalPeso=items.reduce((s,d)=>s+d.peso,0);
  const base100=items.map(d=>({...d,pesoNorm:totalPeso>0?d.peso/totalPeso*100:0,contrib:totalPeso>0?(d.pgmb*d.peso/totalPeso*100):0}));
  const labels=base100.map(d=>d.item+'');
  const contribs=base100.map(d=>+d.contrib.toFixed(3));
  if(chartB100) chartB100.destroy();
  chartB100=new Chart(document.getElementById('chartBase100'),{
    type:'bar',
    data:{labels,datasets:[{
      label:'Contribucion al PG MB (Base 100)',
      data:contribs,
      backgroundColor:contribs.map(v=>v>=0?'rgba(42,135,3,.7)':'rgba(234,17,0,.7)'),
      borderColor:contribs.map(v=>v>=0?'#2a8703':'#ea1100'),borderWidth:2
    }]},
    options:{responsive:true,maintainAspectRatio:false,indexAxis:'y',
      plugins:{tooltip:{callbacks:{label:(ctx)=>{
        const it=base100[ctx.dataIndex];
        return[`Item: ${it.desc}`,`Contrib: ${ctx.parsed.x.toFixed(3)}`,`Peso norm: ${it.pesoNorm.toFixed(2)}/100`,`PG MB: ${pct(it.pgmb)}`];
      }}}},
      scales:{x:{ticks:{callback:v=>v.toFixed(2)},title:{display:true,text:'Contribucion (Peso x PG MB, normalizado a 100)'}}}}
  });
  let tbl=`<table><thead><tr><th>Item</th><th>Descripcion</th><th>% PG MB</th><th>Peso Norm /100</th><th>Contribucion Base 100</th><th>Impacto</th></tr></thead><tbody>`;
  base100.forEach(d=>{
    const imp=d.contrib>=0?'<span class="pill g">Sube PG</span>':'<span class="pill r">Baja PG</span>';
    tbl+=`<tr><td>${d.item}</td><td style="max-width:160px;font-size:11px">${d.desc}</td>
      <td style="color:${d.pgmb>=0?'#2a8703':'#ea1100'};font-weight:700">${pct(d.pgmb)}</td>
      <td>${d.pesoNorm.toFixed(2)}</td>
      <td style="color:${d.contrib>=0?'#2a8703':'#ea1100'};font-weight:700">${d.contrib>0?'+':''}${d.contrib.toFixed(3)}</td>
      <td>${imp}</td></tr>`;
  });
  tbl+='</tbody></table>';
  document.getElementById('tblBase100').innerHTML=`<div class="tbl-wrap">${tbl}</div>`;
}

// ====== DESVIACION META ======
let chartDesv=null;
function renderDesviacion(){
  const sorted=[...D_ITEMS].sort((a,b)=>b.desv-a.desv).slice(0,20);
  const labels=sorted.map(d=>d.item+'');
  const data=sorted.map(d=>+(d.desv*100).toFixed(2));
  if(chartDesv) chartDesv.destroy();
  chartDesv=new Chart(document.getElementById('chartDesviacion'),{
    type:'bar',
    data:{labels,datasets:[{
      label:'Desviacion vs META (pp)',
      data,
      backgroundColor:data.map(v=>v>5?'rgba(234,17,0,.8)':v>0?'rgba(255,194,32,.8)':'rgba(42,135,3,.7)'),
      borderColor:data.map(v=>v>5?'#ea1100':v>0?'#ffc220':'#2a8703'),borderWidth:2
    }]},
    options:{responsive:true,maintainAspectRatio:false,indexAxis:'y',
      plugins:{tooltip:{callbacks:{label:(ctx)=>{
        const it=sorted[ctx.dataIndex];
        return[`${it.desc}`,`Desv: ${ctx.parsed.x>0?'+':''}${ctx.parsed.x}pp`,`PG MB: ${pct(it.pgmb)}`,`META: ${pct(it.meta)}`];
      }}}},
      scales:{x:{ticks:{callback:v=>(v>0?'+':'')+v+'pp'},title:{display:true,text:'Desviacion vs Meta (positivo = debajo de meta)'}}}}
  });
  let tbl=`<table><thead><tr><th>Pais</th><th>Division</th><th>Item</th><th>Descripcion</th><th>% PG MB</th><th>META</th><th>Desv (pp)</th><th>Semaforo</th></tr></thead><tbody>`;
  sorted.forEach(d=>{
    const desv_pp=(d.desv*100);
    const sem=desv_pp>5?'<span class="pill r">Critico</span>':desv_pp>0?'<span class="pill y">Atencion</span>':'<span class="pill g">OK</span>';
    tbl+=`<tr><td><span class="pill b">${d.pais}</span></td><td>${d.div}</td><td>${d.item}</td>
      <td style="font-size:11px;max-width:160px">${d.desc}</td>
      <td style="color:${d.pgmb>=0?'#2a8703':'#ea1100'};font-weight:700">${pct(d.pgmb)}</td>
      <td>${pct(d.meta)}</td>
      <td style="color:${desv_pp>0?'#ea1100':'#2a8703'};font-weight:700">${desv_pp>0?'+':''}${desv_pp.toFixed(2)}pp</td>
      <td>${sem}</td></tr>`;
  });
  tbl+='</tbody></table>';
  document.getElementById('tblDesviacion').innerHTML=`<div class="tbl-wrap">${tbl}</div>`;
}

// ====== INIT ======
buildOverview();
window.addEventListener('load',()=>{
  [...new Set(D_ITEMS.map(d=>d.div))].forEach(d=>{
    const o=document.createElement('option');o.value=d;o.text=d;
    document.getElementById('dlDiv').appendChild(o);
  });
  renderOutliers();
});
"""

HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Competitividad Pricing | SW11 vs SW10 · 2026</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
{CSS}
</style>
</head>
<body>
<header>
  <div>
    <div class="logo">⭐ Walmart Pricing</div>
    <div class="subtitle">Analisis de Competitividad · Año 2026</div>
  </div>
  <div class="badge">SW11 vs SW10 · Centroamerica</div>
</header>

<div class="container">

<div class="tabs" role="tablist">
  <button class="tab active" onclick="showTab('overview')" role="tab">📊 General</button>
  <button class="tab" onclick="showTab('pais')" role="tab">🌎 Pais</button>
  <button class="tab" onclick="showTab('division')" role="tab">🏪 Division</button>
  <button class="tab" onclick="showTab('meta')" role="tab">🎯 Meta</button>
  <button class="tab" onclick="showTab('outliers')" role="tab">⚠️ Outliers Top30</button>
  <button class="tab" onclick="showTab('descarga')" role="tab">⬇️ Descargables</button>
  <button class="tab" onclick="showTab('base100')" role="tab">📐 Base 100</button>
  <button class="tab" onclick="showTab('desviacion')" role="tab">🔍 Desviacion Meta</button>
</div>

<!-- OVERVIEW -->
<div id="tab-overview" class="section active">
  <div class="alert-bar">⚠️ <strong>NI</strong> registra la mayor caida en %PG_MB (−90 bps) y caida severa en %MB_MB de −646 bps. <strong>SV FARMACIA</strong> colapso −635 bps. <strong>GT</strong> es el unico pais con mejora significativa (+74 bps).</div>
  <div class="kpi-row" id="kpi-row"></div>
  <div class="grid2">
    <div class="card">
      <h2>% PG MB por Pais · SW10 vs SW11</h2>
      <div class="chart-wrap"><canvas id="chartPgmbPais"></canvas></div>
    </div>
    <div class="card">
      <h2>% MB MB por Pais · SW10 vs SW11</h2>
      <div class="chart-wrap"><canvas id="chartMbmbPais"></canvas></div>
    </div>
  </div>
  <div class="card">
    <h2>Tendencia de Competitividad: SW10 → SW11 (BPS)</h2>
    <div class="chart-wrap"><canvas id="chartBps"></canvas></div>
  </div>
</div>

<!-- PAIS -->
<div id="tab-pais" class="section">
  <div class="filter-row">
    <div class="section-label">Pais:</div>
    <select id="selectPais" onchange="renderPaisDetail()">
      <option>CR</option><option>GT</option><option>HN</option><option>NI</option><option>SV</option>
    </select>
  </div>
  <div class="grid2">
    <div class="card">
      <h2>KPIs del Pais Seleccionado</h2>
      <div id="paisKpis"></div>
    </div>
    <div class="card">
      <h2>% PG MB vs META por Division (SW11)</h2>
      <div class="chart-wrap"><canvas id="chartPaisDivision"></canvas></div>
    </div>
  </div>
  <div class="card">
    <h2>Division mas Afectada (mayor caida SW10 → SW11 en % PG MB)</h2>
    <div class="chart-wrap"><canvas id="chartDivDelta"></canvas></div>
  </div>
</div>

<!-- DIVISION -->
<div id="tab-division" class="section">
  <div class="card">
    <h2>% PG MB por Division y Pais · SW11 (vs META)</h2>
    <div class="chart-wrap" style="height:340px"><canvas id="chartDivAll"></canvas></div>
  </div>
  <div class="card">
    <h2>Semaforo: Divisiones vs Meta por Pais (SW11)</h2>
    <div id="semaforoDivision"></div>
  </div>
</div>

<!-- META -->
<div id="tab-meta" class="section">
  <div class="card">
    <h2>% PG MB vs META por Pais (SW11)</h2>
    <div class="chart-wrap"><canvas id="chartMetaPais"></canvas></div>
  </div>
  <div class="card">
    <h2>Heatmap Division × Pais: Diferencia PG MB − META (SW11, en pp)</h2>
    <div id="heatmapDiv"></div>
  </div>
</div>

<!-- OUTLIERS -->
<div id="tab-outliers" class="section">
  <div class="filter-row">
    <div class="section-label">Filtrar Pais:</div>
    <select id="filterPaisOut" onchange="renderOutliers()">
      <option value="">Todos</option>
      <option>CR</option><option>GT</option><option>HN</option><option>NI</option><option>SV</option>
    </select>
    <div class="section-label">Filtrar Division:</div>
    <select id="filterDivOut" onchange="renderOutliers()"><option value="">Todas</option></select>
    <button class="btn btn-secondary" onclick="resetOutFilters()">↺ Reset</button>
  </div>
  <div class="card">
    <h2>⚠️ Outliers Negativos (PG MB &lt; 0%) · Primero por Peso</h2>
    <div class="tbl-wrap" id="tblNeg"></div>
  </div>
  <div class="card">
    <h2>🚀 Outliers Positivos (PG MB &gt; META) · Por Peso</h2>
    <div class="tbl-wrap" id="tblPos"></div>
  </div>
</div>

<!-- DESCARGA -->
<div id="tab-descarga" class="section">
  <div class="card">
    <h2>Descarga de Datos por Pais y Division</h2>
    <p style="font-size:13px;color:#8c8c8c;margin-bottom:14px">Selecciona pais y division para descargar el CSV de outliers en Price Gap.</p>
    <div class="filter-row">
      <select id="dlPais"><option value="">Todos los paises</option><option>CR</option><option>GT</option><option>HN</option><option>NI</option><option>SV</option></select>
      <select id="dlDiv"><option value="">Todas las divisiones</option></select>
      <button class="btn btn-primary" onclick="downloadCSV()">⬇️ Descargar CSV</button>
    </div>
    <div class="tbl-wrap" id="tblDescarga"></div>
  </div>
</div>

<!-- BASE 100 -->
<div id="tab-base100" class="section">
  <div class="filter-row">
    <div class="section-label">Pais:</div>
    <select id="b100Pais" onchange="renderBase100()">
      <option>CR</option><option>GT</option><option>HN</option><option>NI</option><option>SV</option>
    </select>
    <div class="section-label">Division:</div>
    <select id="b100Div" onchange="renderBase100()"><option value="">Todas</option></select>
  </div>
  <div class="card">
    <h2>📐 Contribucion al PG MB en Base 100 por Item (SW11)</h2>
    <p style="font-size:12px;color:#8c8c8c;margin-bottom:12px">Muestra que items arrastran mas la competitividad cuando se normaliza el peso total a 100.</p>
    <div class="chart-wrap" style="height:360px"><canvas id="chartBase100"></canvas></div>
  </div>
  <div class="card">
    <h2>Tabla de Contribucion Base 100</h2>
    <div class="tbl-wrap" id="tblBase100"></div>
  </div>
</div>

<!-- DESVIACION META -->
<div id="tab-desviacion" class="section">
  <div class="card">
    <h2>🔍 Items mas Desviados vs Meta en PG MB (SW11)</h2>
    <p style="font-size:12px;color:#8c8c8c;margin-bottom:12px">Desviacion = |PG_MB - META|. Mayor valor = mas alejado de meta.</p>
    <div class="chart-wrap" style="height:360px"><canvas id="chartDesviacion"></canvas></div>
  </div>
  <div class="card">
    <h2>Top Items con Mayor Desviacion vs Meta</h2>
    <div class="tbl-wrap" id="tblDesviacion"></div>
  </div>
</div>

</div><!-- /container -->

<script>
{D_PAIS}
{D_DIV}
{D_ITEMS}
{JS}
</script>
</body>
</html>"""

output_path = "pricing_dashboard_sw11.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"Dashboard generado: {output_path}")
print(f"Tamaño: {len(HTML):,} bytes")
